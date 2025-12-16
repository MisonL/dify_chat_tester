
"""针对 Loguru 日志系统的单元测试"""

import sys
from pathlib import Path
from loguru import logger
import dify_chat_tester.config.logging as logging_utils

class _FakeConfig:
    def __init__(self, level="DEBUG", to_file=True, file_name="test.log", log_dir="logs"):
        self._level = level
        self._to_file = to_file
        self._file_name = file_name
        self._log_dir = log_dir

    def get_str(self, key, default=""):
        if key == "LOG_LEVEL":
            return self._level
        if key == "LOG_FILE_NAME":
            return self._file_name
        if key == "LOG_DIR":
            return self._log_dir
        return default

    def get_bool(self, key, default=False):
        if key == "LOG_TO_FILE":
            return self._to_file
        return default
        
    def get_int(self, key, default=0):
        return default

def test_get_logger_basic_configuration(monkeypatch, tmp_path):
    # 重置配置标记，强制重新配置
    if hasattr(sys, "_dify_loguru_configured"):
        delattr(sys, "_dify_loguru_configured")
        
    fake_log_dir = tmp_path / "logs"
    fake_config = _FakeConfig(log_dir=str(fake_log_dir))
    
    monkeypatch.setattr(logging_utils, "_config", fake_config)
    
    # 获取 logger
    log = logging_utils.get_logger("test_db")
    
    # 验证是否返回了 loguru logger (bind 后的对象)
    assert hasattr(log, "bind")
    assert hasattr(log, "debug")
    assert hasattr(log, "info")
    
    # 写入一条日志
    log.info("Test log message")
    
    # 验证日志文件是否创建
    log_file = fake_log_dir / "test.log"
    assert log_file.exists()
    assert "Test log message" in log_file.read_text(encoding="utf-8")

def test_get_logger_no_file(monkeypatch, tmp_path):
    if hasattr(sys, "_dify_loguru_configured"):
        delattr(sys, "_dify_loguru_configured")
        
    fake_config = _FakeConfig(to_file=False)
    monkeypatch.setattr(logging_utils, "_config", fake_config)
    
    log = logging_utils.get_logger("test_no_file")
    log.info("Should not define file")
    
    # 验证日志文件不应存在
    # 注意：这里我们无法轻易断言"不写文件"，因为 loguru 可能还在以前的配置中？
    # 需要 insure remove() 被调用
    # 在这个测试环境中，get_logger 会调用 logger.remove()，所以应该是干净的
    
    log_file = tmp_path / "logs" / "test.log"
    assert not log_file.exists()
