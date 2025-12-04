"""chat_manager.run_interactive_chat 的基本流程测试。"""

from unittest.mock import MagicMock


def test_run_interactive_chat_basic_flow(tmp_path, monkeypatch):
    """跑通一次最简单的交互式聊天流程（含 /exit 提前退出）。"""
    # Mock get_config.get_enable_thinking -> False
    import dify_chat_tester.chat_manager as cm
    from dify_chat_tester.chat_manager import run_interactive_chat

    mock_config = MagicMock()
    mock_config.get_enable_thinking.return_value = False
    monkeypatch.setattr(cm, "get_config", lambda: mock_config)

    # Mock Excel 日志写入，避免真实 I/O
    from dify_chat_tester import excel_utils

    mock_wb = MagicMock()
    mock_ws = MagicMock()
    excel_utils.init_excel_log = MagicMock(return_value=(mock_wb, mock_ws))
    excel_utils.log_to_excel = MagicMock()

    # 用户输入：第一轮问一句话，第二轮输入 /exit 退出
    inputs = iter(["你好", "/exit"])

    def fake_prompt(_msg: str) -> str:
        return next(inputs)

    monkeypatch.setattr(cm, "print_input_prompt", fake_prompt)

    # 终端输出全部 mute 掉
    monkeypatch.setattr(cm, "print_success", lambda *a, **k: None)
    monkeypatch.setattr(cm, "print_error", lambda *a, **k: None)
    monkeypatch.setattr(cm.console, "print", lambda *a, **k: None)

    # provider.send_message 返回一次成功响应
    provider = MagicMock()
    provider.send_message.return_value = ("response", True, None, None)

    # chat_log_file_name 指向临时目录，避免污染仓库
    log_file = tmp_path / "chat_log.xlsx"

    run_interactive_chat(
        provider=provider,
        selected_role="tester",
        provider_name="OpenAI",
        selected_model="gpt-4o",
        chat_log_file_name=str(log_file),
        provider_id="openai",
    )

    # 至少调用了一次 AI
    assert provider.send_message.call_count >= 1


def test_run_interactive_chat_help_and_exit(tmp_path, monkeypatch):
    """覆盖 /help 分支，然后通过 /exit 退出。"""
    import dify_chat_tester.chat_manager as cm
    from dify_chat_tester import excel_utils
    from dify_chat_tester.chat_manager import run_interactive_chat

    # Mock 配置
    mock_config = MagicMock()
    mock_config.get_enable_thinking.return_value = False
    monkeypatch.setattr(cm, "get_config", lambda: mock_config)

    # Mock Excel 日志
    mock_wb = MagicMock()
    mock_ws = MagicMock()
    excel_utils.init_excel_log = MagicMock(return_value=(mock_wb, mock_ws))
    excel_utils.log_to_excel = MagicMock()

    # 输入：先 /help，再 /exit
    inputs = iter(["/help", "/exit"])

    def fake_prompt(_msg: str) -> str:
        return next(inputs)

    monkeypatch.setattr(cm, "print_input_prompt", fake_prompt)

    # 静音输出
    monkeypatch.setattr(cm, "print_success", lambda *a, **k: None)
    monkeypatch.setattr(cm, "print_error", lambda *a, **k: None)
    monkeypatch.setattr(cm.console, "print", lambda *a, **k: None)

    provider = MagicMock()
    provider.send_message.return_value = ("ignored", True, None, None)

    log_file = tmp_path / "chat_log_help.xlsx"

    run_interactive_chat(
        provider=provider,
        selected_role="tester",
        provider_name="OpenAI",
        selected_model="gpt-4o",
        chat_log_file_name=str(log_file),
        provider_id="openai",
    )

    # /help 分支不应调用 AI
    assert provider.send_message.call_count == 0


def test_run_interactive_chat_dify_with_new_and_history(tmp_path, monkeypatch):
    """覆盖 Dify 分支、/new 命令以及多轮对话逻辑。"""
    import dify_chat_tester.chat_manager as cm
    from dify_chat_tester import excel_utils
    from dify_chat_tester.chat_manager import run_interactive_chat

    mock_config = MagicMock()
    mock_config.get_enable_thinking.return_value = True
    monkeypatch.setattr(cm, "get_config", lambda: mock_config)

    mock_wb = MagicMock()
    mock_ws = MagicMock()
    excel_utils.init_excel_log = MagicMock(return_value=(mock_wb, mock_ws))
    excel_utils.log_to_excel = MagicMock()

    # 构造多轮输入：两轮对话，然后 /new，再一轮，然后 /exit
    inputs = iter(["你好", "再来一句", "/new", "重启后的问题", "/exit"])

    def fake_prompt(_msg: str) -> str:
        return next(inputs)

    monkeypatch.setattr(cm, "print_input_prompt", fake_prompt)

    # 静音输出
    monkeypatch.setattr(cm, "print_success", lambda *a, **k: None)
    monkeypatch.setattr(cm, "print_error", lambda *a, **k: None)
    monkeypatch.setattr(cm.console, "print", lambda *a, **k: None)

    # Dify provider：返回新的 conversation_id
    provider = MagicMock()
    provider.send_message.side_effect = [
        ("r1", True, None, "conv-1"),
        ("r2", True, None, "conv-1"),
        ("r3", True, None, "conv-2"),
    ]

    log_file = tmp_path / "chat_log_dify.xlsx"

    run_interactive_chat(
        provider=provider,
        selected_role="tester",
        provider_name="Dify",
        selected_model="app",
        chat_log_file_name=str(log_file),
        provider_id="dify",
    )

    # 三轮真正的对话
    assert provider.send_message.call_count == 3


def test_run_interactive_chat_save_error(tmp_path, monkeypatch):
    """强制 SAVE_EVERY_N_ROUNDS=1 并让 save 抛出异常，覆盖保存错误分支。"""
    import dify_chat_tester.chat_manager as cm
    from dify_chat_tester import excel_utils
    from dify_chat_tester.chat_manager import run_interactive_chat

    mock_config = MagicMock()
    mock_config.get_enable_thinking.return_value = False
    monkeypatch.setattr(cm, "get_config", lambda: mock_config)

    mock_wb = MagicMock()
    mock_ws = MagicMock()
    # save 抛出 PermissionError
    mock_wb.save.side_effect = PermissionError("no permission")
    excel_utils.init_excel_log = MagicMock(return_value=(mock_wb, mock_ws))
    excel_utils.log_to_excel = MagicMock()

    # 将 SAVE_EVERY_N_ROUNDS 设为 1，确保第一轮就尝试保存
    monkeypatch.setattr(cm, "SAVE_EVERY_N_ROUNDS", 1)

    inputs = iter(["你好", "/exit"])

    def fake_prompt(_msg: str) -> str:
        return next(inputs)

    monkeypatch.setattr(cm, "print_input_prompt", fake_prompt)

    monkeypatch.setattr(cm, "print_success", lambda *a, **k: None)
    monkeypatch.setattr(cm, "print_error", lambda *a, **k: None)
    monkeypatch.setattr(cm.console, "print", lambda *a, **k: None)

    provider = MagicMock()
    provider.send_message.return_value = ("resp", True, None, None)

    log_file = tmp_path / "chat_log_save_err.xlsx"

    run_interactive_chat(
        provider=provider,
        selected_role="tester",
        provider_name="OpenAI",
        selected_model="gpt-4o",
        chat_log_file_name=str(log_file),
        provider_id="openai",
    )

    assert provider.send_message.call_count == 1
