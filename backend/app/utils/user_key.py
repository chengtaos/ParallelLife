"""用户身份隔离 - 从请求头提取 X-User-Key"""

from flask import request, has_request_context, g

DEFAULT_KEY = 'default'


def get_user_key() -> str:
    """获取当前请求的用户标识"""
    if has_request_context():
        key = request.headers.get('X-User-Key', '').strip()
        if key and key.startswith('uk_'):
            return key
    return DEFAULT_KEY
