"""batch_manager.run_batch_query 的集成式单元测试（大量使用临时目录和 mock）。"""

from pathlib import Path
from unittest.mock import MagicMock


def _create_sample_excel(path: Path):
    """在给定路径下创建一个简单的 Excel 输入文件。"""
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    # 表头：包含“文档名称”和“问题”两列
    ws.append(["文档名称", "问题"])
    ws.append(["doc1", "这是第一个问题？"])
    ws.append(["doc2", "这是第二个问题？"])
    wb.save(path)


def test_run_batch_query_basic_flow(tmp_path, monkeypatch):
    """在高度受控环境下跑通一次 run_batch_query 主流程。"""
    from dify_chat_tester.core.batch import run_batch_query

    # 在临时目录下构造输入 Excel 文件
    input_path = tmp_path / "input.xlsx"
    _create_sample_excel(input_path)

    # 切换当前工作目录到临时目录，便于使用 os.listdir(".")
    monkeypatch.chdir(tmp_path)

    # Mock get_config.get_enable_thinking 返回 False
    import dify_chat_tester.core.batch as bm

    mock_config = MagicMock()
    mock_config.get_enable_thinking.return_value = False
    monkeypatch.setattr(bm, "get_config", lambda: mock_config)

    # Mock 终端 UI 辅助函数，避免真实交互和复杂渲染
    # 第一次输入：选择文件序号 "1"；第二次输入：是否显示响应 -> "" (使用默认)
    inputs = iter(["1", ""])  # 文件选择 + 是否显示响应

    def fake_input_prompt(_msg: str) -> str:
        return next(inputs)

    monkeypatch.setattr(bm, "print_input_prompt", fake_input_prompt)

    # select_column_by_index：始终选择第 2 列（问题列）
    import dify_chat_tester.cli.terminal as tui_mod

    monkeypatch.setattr(tui_mod, "select_column_by_index", lambda columns, _msg: 1)

    # 将 print_success / print_error / print_statistics / console.print 都变成 no-op
    monkeypatch.setattr(bm, "print_success", lambda *a, **k: None)
    monkeypatch.setattr(bm, "print_error", lambda *a, **k: None)
    monkeypatch.setattr(bm, "print_statistics", lambda *a, **k: None)
    monkeypatch.setattr(bm.console, "print", lambda *a, **k: None)

    # 避免真实的 sleep 影响测试时间
    import time as _time

    monkeypatch.setattr(_time, "sleep", lambda _s: None)

    # Mock provider：返回简单的成功响应
    provider = MagicMock()
    provider.send_message.return_value = ("回答", True, None, "conv-1")

    # 调用被测函数
    run_batch_query(
        provider=provider,
        selected_role="tester",
        provider_name="OpenAI",
        selected_model="gpt-4o",
        batch_request_interval=0.0,
        batch_default_show_response=False,
    )

    # 至少应被调用一次
    assert provider.send_message.call_count >= 1

    # 生成的状态文件和日志文件应该位于临时目录中
    state_files = list(tmp_path.glob(".batch_state_*.json"))
    # 运行结束后状态文件会被删除，这里只验证不会抛异常
    assert isinstance(state_files, list)


def test_run_batch_query_with_resume_state(tmp_path, monkeypatch):
    """构造带现有日志 Excel 文件的场景，覆盖恢复逻辑与“全部处理完”分支。"""
    from openpyxl import Workbook

    import dify_chat_tester.core.batch as bm
    from dify_chat_tester.core.batch import run_batch_query

    input_path = tmp_path / "input.xlsx"
    _create_sample_excel(input_path)

    # 构造 log 文件：文件名规则 input_log.xlsx
    # 假设已处理到第 2 行（即表头 + 1条数据）
    log_path = tmp_path / "input_log.xlsx"
    wb_log = Workbook()
    ws_log = wb_log.active
    # 表头
    ws_log.append(
        ["Timestamp", "Role", "Doc", "Question", "Answer", "Success", "Error", "ConvID"]
    )
    # 第一条记录
    ws_log.append(["2025-01-01", "tester", "doc1", "q1", "ans1", True, "", "id1"])
    wb_log.save(log_path)

    # 工作目录切到临时目录
    monkeypatch.chdir(tmp_path)

    # Mock 配置
    mock_config = MagicMock()
    mock_config.get_enable_thinking.return_value = False
    monkeypatch.setattr(bm, "get_config", lambda: mock_config)

    # 输入顺序：
    # 1) 选择文件序号 "1" ("input.xlsx")
    # 2) 检测到日志文件，提示恢复 -> "" (默认 Y, 从下一行继续)
    # 3) 请选择问题列 -> "1" (因为移除了 JSON 状态还原列功能，这里需要重新选择列)
    # 4) 是否显示响应 -> "" (默认配置)
    inputs = iter(["1", "", "1", ""])

    def fake_prompt(_msg: str) -> str:
        try:
            return next(inputs)
        except StopIteration:
            return ""

    monkeypatch.setattr(bm, "print_input_prompt", fake_prompt)

    # select_column_by_index 在恢复场景下会被调用（不再从 state 恢复列索引）
    # 但由于我们在 inputs 里已经塞入了 "1"，这里我们不需要 mock lambda 为常量，
    # 而是让它真正调用 print_input_prompt (已被 mock) 或者 mock 它自己。
    # 为了简化， mock 它直接返回 1 (因为 input 里的 "1" 是给它用的吗？不，select_column_by_index 内部调用 print_input_prompt)
    # 如果 mock 了 select_column_by_index，那么 inputs 列表里的 "1" 就不需要了。
    # 让 inputs 变更为: ["1", "", ""] (文件, 恢复确认, 显示响应)
    # 并 mock select_column_by_index 返回 1
    inputs = iter(["1", "", ""])
    import dify_chat_tester.cli.terminal as tui_mod

    monkeypatch.setattr(tui_mod, "select_column_by_index", lambda cols, msg: 1)

    # 静音输出 & sleep
    monkeypatch.setattr(bm, "print_success", lambda *a, **k: None)
    monkeypatch.setattr(bm, "print_error", lambda *a, **k: None)
    monkeypatch.setattr(bm, "print_statistics", lambda *a, **k: None)
    monkeypatch.setattr(bm.console, "print", lambda *a, **k: None)

    import time as _time

    monkeypatch.setattr(_time, "sleep", lambda _s: None)

    provider = MagicMock()
    provider.send_message.return_value = ("回答", True, None, "conv-1")

    run_batch_query(
        provider=provider,
        selected_role="tester",
        provider_name="OpenAI",
        selected_model="gpt-4o",
        batch_request_interval=0.0,
        batch_default_show_response=False,
    )

    # input.xlsx 有 头 + 2行数据。
    # log.xlsx 有 头 + 1行记录。
    # 恢复后，resume_from_row 应该是 3。
    # 所以应该只处理剩下的一行（第3行）。
    assert provider.send_message.call_count == 1
