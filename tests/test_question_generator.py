"""question_generator 模块的基础单元测试。"""

from dify_chat_tester.core.question import (
    MAX_DOC_CHARS_PER_CALL,
    generate_questions_for_document,
    parse_questions_from_response,
)


def test_parse_questions_from_response_json_array():
    response = '["Q1?", "Q2?", "Q3?"]'
    questions = parse_questions_from_response(response)
    assert questions == ["Q1?", "Q2?", "Q3?"]


def test_parse_questions_from_response_embedded_json():
    response = '前面的话... ["Q1", "Q2"] 后面的说明'
    questions = parse_questions_from_response(response)
    assert questions == ["Q1", "Q2"]


def test_parse_questions_from_response_fallback_lines():
    # 使用较长的行文本，满足实现中对最小长度的过滤条件
    response = "- 这是第一个测试问题\n- 这是第二个测试问题 \n\n其他说明"
    questions = parse_questions_from_response(response)
    assert any("第一个测试问题" in q for q in questions)
    assert any("第二个测试问题" in q for q in questions)


class _FakeProvider:
    """用于测试 generate_questions_for_document 的假 Provider。"""

    def __init__(self, responses):
        # 每个分块对应一次 send_message 的返回值
        self._responses = list(responses)
        self.called = 0

    def send_message(self, message, model, role, stream, show_indicator):  # type: ignore[unused-argument]
        # 返回 (response_text, success, error_msg, conversation_id)
        idx = self.called
        self.called += 1
        return self._responses[idx], True, None, None


def test_generate_questions_for_document_splits_long_text_and_deduplicates(monkeypatch):
    # 构造一个长度略小于 MAX_DOC_CHARS_PER_CALL 的文本片段，
    # 两个片段拼接后应被分成 2 个分块。
    piece = "A" * (MAX_DOC_CHARS_PER_CALL - 10)
    document_content = piece + "\n" + piece

    # 两个分块各返回一部分问题，且有重复
    responses = [
        '["Q1", "Q2"]',
        '["Q2", "Q3"]',
    ]
    provider = _FakeProvider(responses)

    questions = generate_questions_for_document(
        provider=provider,
        model="test-model",
        role="user",
        document_name="doc.md",
        document_content=document_content,
    )

    # 应调用两次（对应两个分块）
    assert provider.called == 2
    # 去重且保持顺序
    assert questions == ["Q1", "Q2", "Q3"]


def test_generate_questions_for_document_handles_empty_content():
    provider = _FakeProvider([])
    questions = generate_questions_for_document(
        provider=provider,
        model="test-model",
        role="user",
        document_name="doc.md",
        document_content="",
    )
    assert questions == []

    assert questions == []


def test_read_markdown_files(tmp_path):
    """测试读取 Markdown 文件"""
    from dify_chat_tester.core.question import read_markdown_files

    # 创建测试文件
    d = tmp_path / "docs"
    d.mkdir()
    (d / "test1.md").write_text("内容1", encoding="utf-8")
    (d / "test2.md").write_text("内容2", encoding="utf-8")
    (d / "ignore.txt").write_text("忽略", encoding="utf-8")

    file_names, file_contents = read_markdown_files(str(d))

    assert len(file_names) == 2
    assert "test1.md" in file_names
    assert "test2.md" in file_names
    assert file_contents["test1.md"] == "内容1"
    assert file_contents["test2.md"] == "内容2"


def test_run_question_generation(tmp_path, monkeypatch):
    """测试问题生成主流程"""
    from unittest.mock import MagicMock, patch

    from dify_chat_tester.core.question import run_question_generation

    # 准备测试文件
    doc_dir = tmp_path / "docs"
    doc_dir.mkdir()
    (doc_dir / "test.md").write_text("测试文档内容", encoding="utf-8")

    # Mock Provider
    mock_provider = MagicMock()
    # 返回: (response, success, error, conv_id)
    mock_provider.send_message.return_value = ('["问题1", "问题2"]', True, None, None)

    # Mock UI functions
    monkeypatch.setattr("dify_chat_tester.core.question.print_info", lambda x: None)
    monkeypatch.setattr("dify_chat_tester.core.question.print_success", lambda x: None)
    monkeypatch.setattr("dify_chat_tester.core.question.print_error", lambda x: None)
    monkeypatch.setattr("dify_chat_tester.core.question.print_warning", lambda x: None)
    monkeypatch.setattr(
        "dify_chat_tester.core.question.console.print",
        lambda *args, **kwargs: None,
    )

    # Mock export_questions_to_excel to verify calls and avoid actual file I/O
    with patch(
        "dify_chat_tester.core.question.export_questions_to_excel"
    ) as mock_export:
        mock_export.return_value = True

        run_question_generation(
            provider=mock_provider,
            role="user",
            provider_name="TestProvider",
            selected_model="gpt-4o",
            folder_path=str(doc_dir),
        )

        # Verify export was called
        assert mock_export.called
        # Check arguments of the last call
        args, _ = mock_export.call_args
        questions_data, output_path = args

        assert len(questions_data) == 2
        assert questions_data[0] == ("test.md", "问题1")
        assert questions_data[1] == ("test.md", "问题2")
        assert output_path.startswith("question_generation_")
        assert output_path.endswith(".xlsx")
