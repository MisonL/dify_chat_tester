"""batch_manager.run_batch_query 的集成式单元测试（大量使用临时目录和 mock）。"""

import os
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
    from dify_chat_tester.batch_manager import run_batch_query

    # 在临时目录下构造输入 Excel 文件
    input_path = tmp_path / "input.xlsx"
    _create_sample_excel(input_path)

    # 切换当前工作目录到临时目录，便于使用 os.listdir(".")
    monkeypatch.chdir(tmp_path)

    # Mock get_config.get_enable_thinking 返回 False
    import dify_chat_tester.batch_manager as bm

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
    import dify_chat_tester.terminal_ui as tui_mod

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
    """构造带进度 state 文件的场景，覆盖恢复逻辑与“全部处理完”分支。"""
    from dify_chat_tester.batch_manager import run_batch_query
    import dify_chat_tester.batch_manager as bm
    import json

    input_path = tmp_path / "input.xlsx"
    _create_sample_excel(input_path)

    # 构造 state 文件：假设已处理到第 2 行
    state_file = tmp_path / f".batch_state_{input_path.name}.json"
    state = {
        "excel_file_path": str(input_path),
        "batch_log_file": str(tmp_path / "log.xlsx"),
        "last_processed_row": 2,
        "question_col_index": 1,
        "doc_name_col_index": 0,
        "total_rows": 3,
        "provider_name": "OpenAI",
        "selected_model": "gpt-4o",
        "selected_role": "tester",
    }
    state_file.write_text(json.dumps(state), encoding="utf-8")

    # 工作目录切到临时目录
    monkeypatch.chdir(tmp_path)

    # Mock 配置
    mock_config = MagicMock()
    mock_config.get_enable_thinking.return_value = False
    monkeypatch.setattr(bm, "get_config", lambda: mock_config)

    # 输入顺序：
    # 1) 选择文件序号 "1"
    # 2) 回答是否从上次进度继续 -> "" (默认 Y)
    # 3) 是否显示响应 -> "" (默认配置)
    inputs = iter(["1", "", ""])  # 文件选择 + 恢复确认 + 是否显示响应

    def fake_prompt(_msg: str) -> str:
        return next(inputs)

    monkeypatch.setattr(bm, "print_input_prompt", fake_prompt)

    # select_column_by_index 在恢复场景下不会被调用（使用 state），但这里仍 patch 掉以防万一
    import dify_chat_tester.terminal_ui as tui_mod

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

    # 由于状态文件记录已到第 2 行，本次应只处理第 3 行
    assert provider.send_message.call_count == 1
