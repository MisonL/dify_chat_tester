"""Terminal UI 模块的扩展测试。"""

from unittest.mock import patch

import pytest

from dify_chat_tester.cli.terminal import (
    create_provider_menu,
    print_api_key_confirmation,
    print_column_list,
    print_file_list,
    print_statistics,
    print_welcome,
    select_column_by_index,
)


@pytest.fixture
def mock_console():
    with patch("dify_chat_tester.cli.terminal.console") as mock:
        yield mock


def test_print_statistics(mock_console):
    """测试打印统计信息"""
    print_statistics(total=10, success=8, failed=2, duration=5.5)
    mock_console.print.assert_called()


def test_print_file_list(mock_console):
    """测试打印文件列表"""
    files = ["file1.md", "file2.md"]
    print_file_list(files)
    mock_console.print.assert_called()


def test_print_column_list(mock_console):
    """测试打印列列表"""
    columns = ["A", "B", "C"]
    print_column_list(columns)
    mock_console.print.assert_called()


@patch("dify_chat_tester.cli.terminal.print_input_prompt")
def test_select_column_by_index(mock_input, mock_console):
    """测试选择列"""
    columns = ["A", "B", "C"]

    # 正常选择
    mock_input.return_value = "1"
    idx = select_column_by_index(columns, "选择列")
    assert idx == 0

    # 无效选择后有效选择
    mock_input.side_effect = ["4", "0", "2"]
    idx = select_column_by_index(columns, "选择列")
    assert idx == 1


@patch("dify_chat_tester.cli.terminal.Prompt.ask")
def test_create_provider_menu(mock_prompt_ask):
    """测试创建 Provider 菜单"""
    providers = {
        "1": {"name": "Dify", "id": "dify"},
        "2": {"name": "OpenAI", "id": "openai"},
    }
    mock_prompt_ask.return_value = "1"
    result = create_provider_menu(providers)
    assert result == "1"
    mock_prompt_ask.assert_called_once()


@patch("dify_chat_tester.cli.terminal.Confirm.ask")
def test_print_api_key_confirmation(mock_confirm_ask, mock_console):
    """测试 API Key 确认"""
    # 确认
    mock_confirm_ask.return_value = True
    assert print_api_key_confirmation("key") is True

    # 拒绝
    mock_confirm_ask.return_value = False
    assert print_api_key_confirmation("key") is False


def test_print_welcome(mock_console):
    """测试打印欢迎信息"""
    print_welcome()
    mock_console.print.assert_called()
