"""logging_utils 模块的基础单元测试。"""

import logging

import dify_chat_tester.logging_utils as logging_utils


class _FakeConfig:
    def __init__(self, level="INFO", to_file=False, file_name="test.log"):
        self._level = level
        self._to_file = to_file
        self._file_name = file_name

    def get_str(self, key, default=""):
        if key == "LOG_LEVEL":
            return self._level
        if key == "LOG_FILE_NAME":
            return self._file_name
        return default

    def get_bool(self, key, default=False):
        if key == "LOG_TO_FILE":
            return self._to_file
        return default

    def get_int(self, key, default=0):
        return default


def test_get_logger_basic_configuration(monkeypatch, tmp_path):
    # 使用假配置，并将日志文件写到临时目录
    fake_log_path = tmp_path / "test.log"
    fake_config = _FakeConfig(level="DEBUG", to_file=True, file_name=str(fake_log_path))

    # 替换模块内部的 _config
    monkeypatch.setattr(logging_utils, "_config", fake_config, raising=False)

    logger = logging_utils.get_logger("dify_chat_tester.test")

    # 应该设置了正确的日志级别
    assert logger.level == logging.DEBUG

    # 再次获取同名 logger 不应重复配置 handler（_dify_configured 标记生效）
    logger2 = logging_utils.get_logger("dify_chat_tester.test")
    assert logger is logger2

    # 至少有一个 handler（流式），如果配置了写文件则会多一个
    assert len(logger.handlers) >= 1
