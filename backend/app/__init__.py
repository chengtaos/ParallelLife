"""Parallel Life Backend - Flask应用工厂"""

import os
from flask import Flask, request
from flask_cors import CORS
from .config import Config
from .utils.logger import setup_logger, get_logger


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    if hasattr(app, 'json') and hasattr(app.json, 'ensure_ascii'):
        app.json.ensure_ascii = False

    logger = setup_logger('parallel-life')
    is_reloader = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
    debug_mode = app.config.get('DEBUG', False)
    should_log = not debug_mode or is_reloader

    if should_log:
        logger.info("=" * 50)
        logger.info("Parallel Life Backend 启动中...")
        logger.info("=" * 50)

    CORS(app, resources={r"/api/*": {"origins": "*", "allow_headers": ["Content-Type", "Accept-Language", "X-User-Key", "X-Auth-Token"]}})

    # 注册认证模块（在所有 API 之前）
    from .api.auth import auth_bp, verify_token
    app.register_blueprint(auth_bp, url_prefix='/api')

    # 访问控制中间件：拦截除 auth 和 health 之外的所有 /api/ 请求
    @app.before_request
    def check_auth():
        if request.path.startswith('/api/') \
           and not request.path.startswith('/api/auth') \
           and request.path != '/health':
            token = request.headers.get('X-Auth-Token', '')
            if not verify_token(token):
                from flask import jsonify
                return jsonify({"success": False, "error": "未授权访问"}), 401

    @app.before_request
    def log_request():
        req_logger = get_logger('parallel-life.request')
        req_logger.debug(f"请求: {request.method} {request.path}")

    @app.after_request
    def log_response(response):
        req_logger = get_logger('parallel-life.request')
        req_logger.debug(f"响应: {response.status_code}")
        return response

    from .api import profile_bp, decision_bp
    from .api.compare import compare_bp
    app.register_blueprint(profile_bp, url_prefix='/api/profile')
    app.register_blueprint(decision_bp, url_prefix='/api/decision')
    app.register_blueprint(compare_bp, url_prefix='/api/compare')

    @app.route('/health')
    def health():
        return {'status': 'ok', 'service': 'Parallel Life Backend'}

    if should_log:
        logger.info("Parallel Life Backend 启动完成")

    return app
