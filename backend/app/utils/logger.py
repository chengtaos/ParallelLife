"""日志工具"""

import logging
import sys

_loggers = {}


def setup_logger(name: str = 'parallel-life', level: int = logging.DEBUG) -> logging.Logger:
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(
            '[%(asctime)s] [%(name)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    _loggers[name] = logger
    return logger


def get_logger(name: str = 'parallel-life') -> logging.Logger:
    if name in _loggers:
        return _loggers[name]
    return setup_logger(name)
