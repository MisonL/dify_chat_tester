"""简单日志工具

统一从配置中读取日志相关设置，并返回配置好的 logger。

配置项（来自 config.env）：
- LOG_LEVEL: 日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL），默认 INFO
- LOG_TO_FILE: 是否写入文件（true/false），默认 false
- LOG_FILE_NAME: 日志文件名，默认 dify_chat_tester.log
"""

from __future__ import annotations

import logging
from pathlib import Path

from dify_chat_tester.config_loader import get_config


_config = get_config()


def _parse_level(level_str: str) -> int:
    """将字符串形式的日志级别转换为 logging 级别。"""
    level_str = (level_str or "INFO").upper()
    return getattr(logging, level_str, logging.INFO)


def get_logger(name: str = "dify_chat_tester") -> logging.Logger:
    """获取带统一配置的 logger。

    只在第一次调用时进行配置，后续重复调用直接复用同一个 logger。
    """
    logger = logging.getLogger(name)
    if getattr(logger, "_dify_configured", False):  # type: ignore[attr-defined]
        return logger

    level_str = _config.get_str("LOG_LEVEL", "INFO")
    log_level = _parse_level(level_str)
    logger.setLevel(log_level)

    # 不向上冒泡到 root，避免重复输出
    logger.propagate = False

    # 控制台输出
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # 文件输出（可选）
    if _config.get_bool("LOG_TO_FILE", False):
        file_name = _config.get_str("LOG_FILE_NAME", "dify_chat_tester.log")
        log_path = Path(file_name)
        try:
            # 确保目录存在（如果包含目录的话）
            if log_path.parent and not log_path.parent.exists():
                log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_path, encoding="utf-8")
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception:
            # 文件日志失败时不影响主流程，仅忽略
            pass

    # 标记已配置
    setattr(logger, "_dify_configured", True)
    return logger
