"""简单日志工具

统一从配置中读取日志相关设置，并返回配置好的 logger。

配置项（来自 .env.config）：
- LOG_LEVEL: 日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL），默认 INFO
- LOG_TO_FILE: 是否写入文件（true/false），默认 true
- LOG_FILE_NAME: 日志文件名，默认 dify_chat_tester.log
- LOG_DIR: 日志目录，默认 logs
- LOG_MAX_BYTES: 单个日志文件最大字节数，默认 10485760 (10MB)
- LOG_BACKUP_COUNT: 保留的备份文件数量，默认 5
"""

from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dify_chat_tester.config_loader import get_config

_config = get_config()


def _parse_level(level_str: str) -> int:
    """将字符串形式的日志级别转换为 logging 级别。"""
    level_str = (level_str or "INFO").upper()
    return getattr(logging, level_str, logging.INFO)


def _get_log_directory(log_dir: str) -> Path:
    """
    获取日志目录路径，优先使用程序所在目录，否则使用用户主目录
    
    Args:
        log_dir: 日志目录名称
        
    Returns:
        Path: 日志目录的绝对路径
    """
    # 尝试获取程序所在目录
    if getattr(sys, 'frozen', False):
        # 打包后的程序
        app_dir = Path(sys.executable).parent
    else:
        # 开发环境
        app_dir = Path.cwd()
    
    # 首选：程序所在目录的logs文件夹
    preferred_log_dir = app_dir / log_dir
    
    # 测试是否有写入权限
    try:
        preferred_log_dir.mkdir(parents=True, exist_ok=True)
        # 尝试写入测试文件
        test_file = preferred_log_dir / '.write_test'
        test_file.write_text('test')
        test_file.unlink()
        return preferred_log_dir
    except (OSError, PermissionError):
        # 如果没有写入权限，使用用户主目录
        home_dir = Path.home()
        fallback_log_dir = home_dir / '.dify_chat_tester' / log_dir
        fallback_log_dir.mkdir(parents=True, exist_ok=True)
        return fallback_log_dir


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

    # 文件输出（默认启用，支持日志轮转）
    if _config.get_bool("LOG_TO_FILE", True):
        log_dir = _config.get_str("LOG_DIR", "logs")
        file_name = _config.get_str("LOG_FILE_NAME", "dify_chat_tester.log")
        max_bytes = _config.get_int("LOG_MAX_BYTES", 10 * 1024 * 1024)  # 10MB
        backup_count = _config.get_int("LOG_BACKUP_COUNT", 5)
        
        try:
            # 获取智能日志目录
            actual_log_dir = _get_log_directory(log_dir)
            log_path = actual_log_dir / file_name

            # 使用 RotatingFileHandler 实现日志轮转
            file_handler = RotatingFileHandler(
                log_path,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8"
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
            # 记录日志目录位置
            logger.info(f"日志目录: {actual_log_dir}")
        except Exception as e:
            # 文件日志失败时输出警告，但不影响主流程
            logger.warning(f"无法初始化文件日志: {e}")

    # 标记已配置
    setattr(logger, "_dify_configured", True)
    return logger
