"""API路由模块"""
from flask import Blueprint

profile_bp = Blueprint('profile', __name__)
decision_bp = Blueprint('decision', __name__)

from . import profile  # noqa: E402, F401
from . import decision  # noqa: E402, F401
