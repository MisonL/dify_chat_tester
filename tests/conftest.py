# tests/conftest.py
"""pytest 配置和共享 fixtures"""

import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_provider():
    """创建模拟的 AI 提供商"""
    provider = MagicMock()
    provider.send_message.return_value = ("模拟回答", True, None, "conv-123")
    return provider


@pytest.fixture
def mock_console():
    """模拟 console 输出"""
    with patch("dify_chat_tester.core.batch.console") as mock:
        yield mock


@pytest.fixture
def mock_config():
    """模拟配置加载器"""
    config = MagicMock()
    config.get_int.return_value = 10
    config.get_bool.return_value = False
    config.get_enable_thinking.return_value = False
    return config
