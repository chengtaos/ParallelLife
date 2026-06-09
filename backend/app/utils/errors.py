"""错误信息优化 — 将技术异常映射为用户友好的中文消息"""

import re
from .logger import get_logger

logger = get_logger('parallel-life.errors')


def friendly_error(exc: Exception) -> str:
    """将异常转换为用户友好的错误消息"""
    msg = str(exc)

    # LLM 相关
    if 'LLM_API_KEY' in msg or 'api_key' in msg.lower():
        return 'AI 服务配置错误，请检查 API Key 设置'
    if 'rate_limit' in msg.lower() or '429' in msg:
        return 'AI 服务请求过于频繁，请稍后重试'
    if 'timeout' in msg.lower() or 'timed out' in msg.lower():
        return 'AI 服务响应超时，请稍后重试'
    if 'context_length' in msg.lower() or 'token' in msg.lower():
        return '输入文本过长，请精简后重试'
    if 'invalid' in msg.lower() and 'json' in msg.lower():
        return 'AI 返回格式异常，请重试'

    # Zep 相关
    if 'ZEP_API_KEY' in msg or 'zep' in msg.lower():
        return '知识图谱服务配置错误，请检查 Zep Key 设置'
    if 'graph' in msg.lower() and ('not found' in msg.lower() or 'exist' in msg.lower()):
        return '知识图谱数据异常，请重建画像'

    # 文件/存储
    if 'no such file' in msg.lower() or 'not found' in msg.lower():
        return '数据文件缺失，画像可能已被删除'
    if 'permission' in msg.lower():
        return '文件权限不足，请检查磁盘权限'

    # 默认
    # 截取前 200 字符，去掉敏感路径信息
    clean = re.sub(r'[A-Z]:[\\/][^\s]*', '[路径]', msg)
    clean = clean[:200]
    logger.error(f"未分类的错误: {clean}")
    return f'操作失败（{clean}）'
