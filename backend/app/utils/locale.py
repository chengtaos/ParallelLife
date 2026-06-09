"""国际化工具（精简版）"""

import json
import os
import threading

_thread_local = threading.local()

_locales_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'locales')

with open(os.path.join(_locales_dir, 'languages.json'), 'r', encoding='utf-8') as f:
    _languages = json.load(f)

_translations = {}
for filename in os.listdir(_locales_dir):
    if filename.endswith('.json') and filename != 'languages.json':
        locale_name = filename[:-5]
        if locale_name in _languages:
            with open(os.path.join(_locales_dir, filename), 'r', encoding='utf-8') as f:
                _translations[locale_name] = json.load(f)


def set_locale(locale: str):
    _thread_local.locale = locale


def get_locale() -> str:
    from flask import request, has_request_context
    if has_request_context():
        raw = request.headers.get('Accept-Language', 'zh')
        return raw if raw in _translations else 'zh'
    return getattr(_thread_local, 'locale', 'zh')


def t(key: str, **kwargs) -> str:
    locale = get_locale()
    messages = _translations.get(locale, _translations.get('zh', {}))
    value = messages
    for part in key.split('.'):
        if isinstance(value, dict):
            value = value.get(part)
        else:
            return key
    if value is None:
        return key
    if kwargs:
        for k, v in kwargs.items():
            value = str(value).replace(f'{{{k}}}', str(v))
    return str(value)


def get_language_instruction() -> str:
    locale = get_locale()
    lang_config = _languages.get(locale, _languages.get('zh', {}))
    return lang_config.get('llmInstruction', '请使用中文回答。')
