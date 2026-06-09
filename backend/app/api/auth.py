"""访问控制 - 密码门"""

import hashlib
import time
from flask import request, jsonify, Blueprint
from ..config import Config
from ..utils.logger import get_logger

auth_bp = Blueprint('auth', __name__)
logger = get_logger('parallel-life.api.auth')

# 内存中的活跃 token（服务重启即失效，足够简单）
_active_tokens = {}


def _make_token(password: str) -> str:
    raw = f"{password}:{Config.SECRET_KEY}:{int(time.time() // 3600)}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def verify_token(token: str) -> bool:
    if not Config.ACCESS_PASSWORD:
        return True  # 未设置密码时允许所有请求
    return token in _active_tokens


@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """密码验证，返回 token"""
    if not Config.ACCESS_PASSWORD:
        return jsonify({"success": True, "data": {"token": "", "message": "无需密码"}})

    data = request.get_json() or {}
    password = data.get('password', '')

    if password == Config.ACCESS_PASSWORD:
        token = _make_token(password)
        _active_tokens[token] = time.time()
        return jsonify({"success": True, "data": {"token": token}})

    return jsonify({"success": False, "error": "密码错误"}), 401


@auth_bp.route('/auth/check', methods=['GET'])
def check():
    """检查 token 是否有效"""
    token = request.headers.get('X-Auth-Token', '')
    if verify_token(token):
        return jsonify({"success": True, "data": {"valid": True}})
    return jsonify({"success": True, "data": {"valid": False}})
