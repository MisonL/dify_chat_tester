import os
from unittest.mock import MagicMock, patch, mock_open
import pytest
from dify_chat_tester.core.chat import run_interactive_chat

def test_export_clipboard_command():
    """测试 /export clip 命令在 run_interactive_chat 中的执行"""
    
    mock_provider = MagicMock()
    # 模拟先发送一次消息，产生历史记录，然后导出，最后退出
    # 输入序列: "Hello" -> "/export clip" -> "/quit"
    user_inputs = ["Hello", "/export clip", "/quit"]
    
    # send_message 返回成功
    mock_provider.send_message.return_value = ("World", True, None, "cid")
    
    with patch("dify_chat_tester.core.chat.print_input_prompt", side_effect=user_inputs), \
         patch("dify_chat_tester.core.chat.init_excel_log", return_value=(MagicMock(), MagicMock())), \
         patch("pyperclip.copy") as mock_copy, \
         patch("dify_chat_tester.core.chat.get_config") as mock_conf:
         
        mock_conf.return_value.get_enable_thinking.return_value = False
        
        run_interactive_chat(mock_provider, "role", "Provider", "model", "log.xlsx")
        
        # 验证 send_message 被调用（产生历史）
        mock_provider.send_message.assert_called()
        
        # 验证 pyperclip.copy 被调用
        mock_copy.assert_called_once()
        args, _ = mock_copy.call_args
        content = args[0]
        assert "Hello" in content
        assert "World" in content

def test_export_markdown_command():
    """测试 /export md 命令"""
    mock_provider = MagicMock()
    user_inputs = ["Msg", "/export md", "/exit"]
    mock_provider.send_message.return_value = ("Reply", True, None, "cid")
    
    m_open = mock_open()
    
    with patch("dify_chat_tester.core.chat.print_input_prompt", side_effect=user_inputs), \
         patch("dify_chat_tester.core.chat.init_excel_log", return_value=(MagicMock(), MagicMock())), \
         patch("builtins.open", m_open), \
         patch("dify_chat_tester.core.chat.get_config"), \
         patch("os.getcwd", return_value="/tmp"):
            
        run_interactive_chat(mock_provider, "role", "Provider", "model", "log.xlsx")
        
        m_open.assert_called()
        handle = m_open()
        written = "".join(call.args[0] for call in handle.write.call_args_list)
        assert "Msg" in written
        assert "Reply" in written

def test_export_menu_interaction():
    """测试 /export 交互式菜单"""
    mock_provider = MagicMock()
    # 1. 发消息 -> 2. /export -> 3. 菜单选1(clip) -> 4. /quit
    # 注意 print_input_prompt 会被复用:
    # 1. 主循环: "Hello"
    # 2. 主循环: "/export"
    # 3. 导出内部: "1" (选择剪贴板)
    # 4. 主循环: "/quit"
    user_inputs = ["Hello", "/export", "1", "/quit"]
    mock_provider.send_message.return_value = ("Hi", True, None, "cid")
    
    with patch("dify_chat_tester.core.chat.print_input_prompt", side_effect=user_inputs), \
         patch("dify_chat_tester.core.chat.init_excel_log", return_value=(MagicMock(), MagicMock())), \
         patch("pyperclip.copy") as mock_copy, \
         patch("dify_chat_tester.core.chat.get_config"):
         
        run_interactive_chat(mock_provider, "role", "Provider", "model", "log.xlsx")
        
        mock_copy.assert_called_once()
        assert "Hello" in mock_copy.call_args[0][0]
