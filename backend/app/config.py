"""配置管理 — 从项目根目录 .env 加载"""

import os
from dotenv import load_dotenv

project_root_env = os.path.join(os.path.dirname(__file__), '../../.env')
if os.path.exists(project_root_env):
    load_dotenv(project_root_env, override=True)
else:
    load_dotenv(override=True)


class Config:
    """Flask配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'parallel-life-secret-key')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    JSON_AS_ASCII = False

    # LLM
    LLM_API_KEY = os.environ.get('LLM_API_KEY')
    LLM_BASE_URL = os.environ.get('LLM_BASE_URL', 'https://api.openai.com/v1')
    LLM_MODEL_NAME = os.environ.get('LLM_MODEL_NAME', 'gpt-4o-mini')

    # Zep
    ZEP_API_KEY = os.environ.get('ZEP_API_KEY')

    # Upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../uploads')
    PROFILES_DIR = os.path.join(UPLOAD_FOLDER, 'profiles')

    @classmethod
    def validate(cls) -> list[str]:
        errors: list[str] = []
        if not cls.LLM_API_KEY:
            errors.append("LLM_API_KEY 未配置")
        if not cls.ZEP_API_KEY:
            errors.append("ZEP_API_KEY 未配置")
        return errors
