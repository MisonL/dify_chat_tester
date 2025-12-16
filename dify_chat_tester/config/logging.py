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

import logging
import sys
from pathlib import Path

from loguru import logger

from dify_chat_tester.config.loader import get_config

_config = get_config()


class InterceptHandler(logging.Handler):
    """
    拦截标准 logging 库的日志并转发给 loguru
    这样像 requests, urllib3 等第三方库的日志也能统一管理
    """

    def emit(self, record):
        # 获取对应的 loguru 级别
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 查找调用者的帧，确保日志行号正确
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def _get_log_directory(log_dir: str) -> Path:
    """获取日志目录路径"""
    # 尝试获取程序所在目录
    if getattr(sys, "frozen", False):
        app_dir = Path(sys.executable).parent
    else:
        app_dir = Path.cwd()

    preferred_log_dir = app_dir / log_dir

    try:
        preferred_log_dir.mkdir(parents=True, exist_ok=True)
        # 测试写入权限
        test_file = preferred_log_dir / ".write_test"
        test_file.write_text("test")
        test_file.unlink()
        return preferred_log_dir
    except (OSError, PermissionError):
        home_dir = Path.home()
        fallback_log_dir = home_dir / ".dify_chat_tester" / log_dir
        fallback_log_dir.mkdir(parents=True, exist_ok=True)
        return fallback_log_dir


def get_logger(name: str = "dify_chat_tester"):
    """
    获取配置好的 loguru logger
    注意：loguru 是单例，name 参数主要用于 bind 上下文，
    但为了兼容标准 logging 的用法，我们返回原生的 loguru.logger
    或者根据需要返回 bind 后的 logger
    """

    # 防止重复配置
    if hasattr(sys, "_dify_loguru_configured"):
        return logger.bind(name=name)

    # 1. 移除 loguru 默认的 handler
    logger.remove()

    # 2. 读取配置
    level_str = _config.get_str("LOG_LEVEL", "INFO").upper()
    log_to_file = _config.get_bool("LOG_TO_FILE", True)

    # 3. 配置控制台输出 (stderr)
    logger.add(
        sys.stderr,
        level=level_str,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )

    # 4. 配置文件输出
    if log_to_file:
        log_dir_name = _config.get_str("LOG_DIR", "logs")
        file_name = _config.get_str("LOG_FILE_NAME", "dify_chat_tester.log")
        # 10MB 切割，保留 7 天，旧文件压缩为 zip
        max_bytes = "10 MB"
        retention = "7 days"

        try:
            actual_log_dir = _get_log_directory(log_dir_name)
            log_path = actual_log_dir / file_name

            # 主日志文件配置
            # filter=None 表示记录所有（除非被 level 过滤）
            # 但我们希望把特定的插件 debug 日志分流出去，不混在主日志里？
            # 策略：主日志包含所有 logger 的内容（作为全量备份），
            # 或者：主日志排除特定的 channel。
            # 这里我们保持简单：主日志记录所有标准输出。

            logger.add(
                str(log_path),
                level=level_str,
                rotation=max_bytes,
                retention=retention,
                compression="zip",
                encoding="utf-8",
                enqueue=True,  # 异步写入，线程安全
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            )

            # 记录日志位置
            logger.debug(f"主日志文件: {log_path}")

        except Exception as e:
            print(f"警告: 无法初始化文件日志: {e}", file=sys.stderr)

    # 5. 拦截标准 logging 库的日志
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # 标记已配置
    setattr(sys, "_dify_loguru_configured", True)

    return logger.bind(name=name)
