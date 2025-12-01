"""针对批量模式和会话模式的基础单元测试。"""

from pathlib import Path

import openpyxl

import dify_chat_tester.batch_manager as batch_manager
import dify_chat_tester.chat_manager as chat_manager
import dify_chat_tester.terminal_ui as terminal_ui


class _FakeBatchProvider:
    """用于测试批量模式的假 Provider。"""

    def __init__(self):
        self.calls = 0
        self.base_url = "https://api.test"

    def send_message(self, message, model, role, **kwargs):  # type: ignore[unused-argument]
        self.calls += 1
        # 返回 (response_text, success, error_msg, conversation_id)
        return "answer", True, None, "cid-123"


def test_run_batch_query_processes_non_empty_rows(monkeypatch, tmp_path):
    """基础测试：确认非空问题会被处理并写入日志。"""
    # 在临时目录中创建一个简单的 Excel 输入文件
    monkeypatch.chdir(tmp_path)
    input_path = Path("questions.xlsx")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["问题"])  # 表头
    ws.append(["这是第一个问题"])
    ws.append([""])  # 空行，应被跳过
    wb.save(str(input_path))

    provider = _FakeBatchProvider()

    # 模拟用户输入：
    # 1. 选择第 1 个 Excel 文件
    # 2. 在是否显示回答时按回车（使用默认 Y）
    answers = iter(["1", ""])  # file index, display_response_choice

    monkeypatch.setattr(
        batch_manager,
        "print_input_prompt",
        lambda msg: next(answers),
        raising=False,
    )

    # 问题列固定为第 1 列
    # 直接在 terminal_ui 模块内覆盖 select_column_by_index，避免进入真正的交互逻辑
    def _fake_select_column_by_index(columns, prompt_msg):  # type: ignore[unused-argument]
        return 0

    monkeypatch.setattr(
        terminal_ui,
        "select_column_by_index",
        _fake_select_column_by_index,
        raising=False,
    )

    # 避免测试时真正等待
    monkeypatch.setattr(batch_manager.time, "sleep", lambda x: None, raising=False)

    batch_manager.run_batch_query(
        provider=provider,
        selected_role="user",
        provider_name="TestProvider",
        selected_model="test-model",
        batch_request_interval=0.0,
        batch_default_show_response=False,
    )

    # 只有一行非空问题，应至少被调用一次
    assert provider.calls >= 1

    # 应生成批量日志文件
    logs = list(tmp_path.glob("batch_query_log_*.xlsx"))
    assert logs, "未找到批量日志文件"


class _FakeChatProvider:
    """用于测试会话模式的假 Provider。"""

    def __init__(self):
        self.calls = 0

    def send_message(self, message, model, role, **kwargs):  # type: ignore[unused-argument]
        self.calls += 1
        # 返回 (response_text, success, error_msg, extra)
        return "mock-response", True, None, None


def test_run_interactive_chat_help_and_exit(monkeypatch, tmp_path):
    """输入 /help 后应仅显示帮助，不调用 Provider，然后 /exit 正常退出。"""
    provider = _FakeChatProvider()

    # 在临时目录中运行，确保日志文件不会写到项目根目录
    monkeypatch.chdir(tmp_path)

    inputs = iter(["/help", "/exit"])  # 先看帮助，再退出

    monkeypatch.setattr(
        chat_manager,
        "print_input_prompt",
        lambda msg: next(inputs),
        raising=False,
    )

    log_file = tmp_path / "chat_log.xlsx"

    chat_manager.run_interactive_chat(
        provider=provider,
        selected_role="user",
        provider_name="TestProvider",
        selected_model="test-model",
        chat_log_file_name=str(log_file),
    )

    # /help 只打印帮助，不应调用 Provider
    assert provider.calls == 0


def test_run_interactive_chat_single_message_and_exit(monkeypatch, tmp_path):
    """简单对话：发送一条消息后 /exit，应调用 Provider 一次并写入日志。"""
    provider = _FakeChatProvider()

    # 在临时目录中运行，确保日志文件写入到 tmp_path
    monkeypatch.chdir(tmp_path)

    inputs = iter(["你好", "/exit"])  # 一条普通消息，然后退出

    monkeypatch.setattr(
        chat_manager,
        "print_input_prompt",
        lambda msg: next(inputs),
        raising=False,
    )

    # 使用当前工作目录下的相对路径，避免 openpyxl 在不同工作目录下找不到文件
    log_file_name = "chat_log.xlsx"

    chat_manager.run_interactive_chat(
        provider=provider,
        selected_role="user",
        provider_name="TestProvider",
        selected_model="test-model",
        chat_log_file_name=log_file_name,
    )

    assert provider.calls == 1

    # 日志写入行为在 excel_utils 的单元测试中已经覆盖，这里只关注调用次数
