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
    from unittest.mock import MagicMock, patch

    from dify_chat_tester.terminal_ui import (
        print_error,
        print_info,
        print_success,
        print_warning,
        print_welcome,
    )

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
    from unittest.mock import MagicMock

    from dify_chat_tester.terminal_ui import print_input_prompt

    mock_console = MagicMock()
    monkeypatch.setattr("dify_chat_tester.terminal_ui.console", mock_console)

    # Mock builtins.input to accept optional argument
    monkeypatch.setattr("builtins.input", lambda prompt="": "user input")

    result = print_input_prompt("Prompt")
    assert result == "user input"
    mock_console.print.assert_called()


def test_stream_display(monkeypatch):
    """测试 StreamDisplay 类"""
    from unittest.mock import patch

    # 强制使用富文本 UI，以便覆盖 Live 分支
    import dify_chat_tester.terminal_ui as tui_mod
    from dify_chat_tester.terminal_ui import StreamDisplay

    monkeypatch.setattr(tui_mod, "USE_RICH_UI", True)

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


def test_input_api_key_simple_mode(monkeypatch):
    """测试不使用富文本 UI 时的 input_api_key"""
    import getpass
    from unittest.mock import MagicMock

    import dify_chat_tester.terminal_ui as tui_mod

    mock_console = MagicMock()
    monkeypatch.setattr(tui_mod, "console", mock_console)
    monkeypatch.setattr(tui_mod, "USE_RICH_UI", False)
    monkeypatch.setattr(getpass, "getpass", lambda prompt="": "secret-key")

    from dify_chat_tester.terminal_ui import input_api_key

    result = input_api_key("请输入 API 密钥: ")
    assert result == "secret-key"
    mock_console.print.assert_called()


def test_create_provider_menu(monkeypatch):
    """测试创建供应商选择菜单"""
    from unittest.mock import MagicMock

    import dify_chat_tester.terminal_ui as tui_mod

    mock_console = MagicMock()
    monkeypatch.setattr(tui_mod, "console", mock_console)

    # Mock Prompt.ask 直接返回第一个 key
    from dify_chat_tester.terminal_ui import Prompt, create_provider_menu

    monkeypatch.setattr(
        Prompt,
        "ask",
        lambda *args, **kwargs: list({"1": {"name": "Dify"}}.keys())[0],
    )

    providers = {"1": {"name": "Dify"}}
    choice = create_provider_menu(providers)
    assert choice == "1"


def test_print_statistics_simple_mode(monkeypatch):
    """测试纯文本模式下的统计输出"""
    from unittest.mock import MagicMock

    import dify_chat_tester.terminal_ui as tui_mod

    mock_console = MagicMock()
    monkeypatch.setattr(tui_mod, "console", mock_console)
    monkeypatch.setattr(tui_mod, "USE_RICH_UI", False)

    from dify_chat_tester.terminal_ui import print_statistics

    print_statistics(total=10, success=8, failed=2, duration=5.0)

    # 至少应打印几行统计信息
    assert mock_console.print.call_count >= 5


def test_print_file_and_column_list(monkeypatch):
    """测试文件列表和列名列表的打印（简单模式）"""
    from unittest.mock import MagicMock

    import dify_chat_tester.terminal_ui as tui_mod

    mock_console = MagicMock()
    monkeypatch.setattr(tui_mod, "console", mock_console)
    monkeypatch.setattr(tui_mod, "USE_RICH_UI", False)

    from dify_chat_tester.terminal_ui import print_column_list, print_file_list

    files = ["a.xlsx", "b.xlsx"]
    print_file_list(files)
    assert mock_console.print.call_count >= len(files)

    mock_console.print.reset_mock()

    cols = ["col1", "col2"]
    print_column_list(cols)
    assert mock_console.print.call_count >= len(cols)


def test_select_column_by_index(monkeypatch):
    """测试通过序号选择列的流程"""
    from unittest.mock import MagicMock

    import dify_chat_tester.terminal_ui as tui_mod

    mock_console = MagicMock()
    monkeypatch.setattr(tui_mod, "console", mock_console)
    monkeypatch.setattr(tui_mod, "USE_RICH_UI", False)

    # 让第一次输入无效，第二次输入有效
    inputs = iter(["0", "2"])

    def fake_prompt(_msg: str) -> str:
        return next(inputs)

    monkeypatch.setattr(tui_mod, "print_input_prompt", fake_prompt)

    from dify_chat_tester.terminal_ui import select_column_by_index

    cols = ["c1", "c2", "c3"]
    idx = select_column_by_index(cols, "请选择列")

    assert idx == 1
