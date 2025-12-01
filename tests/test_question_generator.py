"""question_generator 模块的基础单元测试。"""

from dify_chat_tester.question_generator import (
    MAX_DOC_CHARS_PER_CALL,
    generate_questions_for_document,
    parse_questions_from_response,
)


def test_parse_questions_from_response_json_array():
    response = '["Q1?", "Q2?", "Q3?"]'
    questions = parse_questions_from_response(response)
    assert questions == ["Q1?", "Q2?", "Q3?"]


def test_parse_questions_from_response_embedded_json():
    response = "前面的话... [\"Q1\", \"Q2\"] 后面的说明"
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
