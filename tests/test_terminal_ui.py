"""Terminal UI 模块的单元测试。

测试终端 UI 辅助函数，如 hide_api_key 等。
"""

from dify_chat_tester.terminal_ui import hide_api_key


class TestHideApiKey:
    """测试 hide_api_key 函数"""

    def test_hide_normal_key(self):
        """测试正常长度的密钥"""
        key = "sk-1234567890abcdef"
        result = hide_api_key(key)
        # 前4位 + 中间星号 + 后4位
        assert result == "sk-1" + "*" * (len(key) - 8) + "cdef"
        assert len(result) == len(key)

    def test_hide_short_key(self):
        """测试短密钥"""
        key = "short"
        result = hide_api_key(key)
        assert result == "*****"
        assert len(result) == len(key)

    def test_hide_long_key(self):
        """测试长密钥"""
        key = "app-very-long-api-key-here-for-testing-purposes"
        result = hide_api_key(key)
        # 应该只显示前4位和后4位
        assert result.startswith("app-")
        assert result.endswith("oses")
        assert "*" in result
        assert len(result) == len(key)

    def test_hide_empty_key(self):
        """测试空密钥"""
        key = ""
        result = hide_api_key(key)
        assert result == ""

    def test_hide_exactly_8_chars(self):
        """测试恰好8个字符的密钥"""
        key = "12345678"
        result = hide_api_key(key)
        # 8个字符或更少时，全部隐藏
        assert result == "********"
        assert result == "********"


def test_print_functions(monkeypatch):
    """测试各种打印函数"""
    from dify_chat_tester.terminal_ui import (
        print_error,
        print_info,
        print_success,
        print_warning,
        print_welcome,
    )
    from unittest.mock import MagicMock, patch
    
    mock_console = MagicMock()
    monkeypatch.setattr("dify_chat_tester.terminal_ui.console", mock_console)
    
    # Mock Panel to verify content
    with patch("dify_chat_tester.terminal_ui.Panel") as MockPanel:
        print_info("Info message")
        mock_console.print.assert_called()
        # Verify Panel was created
        assert MockPanel.called
        
        print_success("Success message")
        mock_console.print.assert_called()
        
        print_warning("Warning message")
        mock_console.print.assert_called()
        
        print_error("Error message")
        mock_console.print.assert_called()
        
        print_welcome()
        mock_console.print.assert_called()


def test_print_input_prompt(monkeypatch):
    """测试输入提示函数"""
    from dify_chat_tester.terminal_ui import print_input_prompt
    from unittest.mock import MagicMock
    
    mock_console = MagicMock()
    monkeypatch.setattr("dify_chat_tester.terminal_ui.console", mock_console)
    
    # Mock builtins.input to accept optional argument
    monkeypatch.setattr("builtins.input", lambda prompt="": "user input")
    
    result = print_input_prompt("Prompt")
    assert result == "user input"
    mock_console.print.assert_called()


def test_stream_display(monkeypatch):
    """测试 StreamDisplay 类"""
    from dify_chat_tester.terminal_ui import StreamDisplay
    from unittest.mock import MagicMock, patch
    
    # Mock Live from rich.live
    with patch("rich.live.Live") as MockLive:
        mock_live_instance = MockLive.return_value
        mock_live_instance.__enter__.return_value = mock_live_instance
        mock_live_instance.__exit__.return_value = None
        
        display = StreamDisplay(title="Test Stream")
        
        # Test start
        display.start()
        assert display.live is not None
        assert MockLive.called
        
        # Test update
        display.update("chunk1")
        assert display.content == "chunk1"
        mock_live_instance.refresh.assert_called()
        
        display.update("chunk2")
        assert display.content == "chunk1chunk2"
        
        # Test stop
        display.stop()
        assert display.live is None
        mock_live_instance.stop.assert_called()
