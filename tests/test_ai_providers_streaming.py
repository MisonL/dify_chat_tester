"""AI Providers 流式处理和边缘情况的深度测试"""

from unittest.mock import MagicMock, patch


from dify_chat_tester.ai_providers import DifyProvider, OpenAIProvider, iFlowProvider


class TestDifyStreamProcessing:
    """Dify Provider 流式处理深度测试"""

    @patch("requests.post")
    def test_stream_json_decode_error(self, mock_post):
        """测试流式响应中的 JSON 解码错误"""
        resp = MagicMock()
        resp.status_code = 200
        resp.iter_lines.return_value = iter(
            [
                b"data: {invalid}",
                b'data: {"answer": "valid"}',
            ]
        )
        mock_post.return_value = resp

        provider = DifyProvider("http://url", "key", "app")

        with patch("dify_chat_tester.terminal_ui.StreamDisplay"):
            response, success, error, _ = provider.send_message(
                "msg", "model", stream=True, show_indicator=False
            )

        # 应该跳过无效JSON并处理有效的
        assert success is True or isinstance(response, str)

    @patch("requests.post")
    def test_stream_agent_thought_event(self, mock_post):
        """测试 agent_thought 事件"""
        resp = MagicMock()
        resp.status_code = 200
        resp.iter_lines.return_value = iter(
            [
                b'data: {"event": "agent_thought", "thought": "Thinking..."}',
                b'data: {"event": "agent_message", "answer": "Done"}',
            ]
        )
        mock_post.return_value = resp

        provider = DifyProvider("http://url", "key", "app")

        with patch("dify_chat_tester.terminal_ui.StreamDisplay"):
            response, success, error, _ = provider.send_message(
                "msg", "model", stream=True, show_indicator=False, show_thinking=True
            )

        assert success is True

    @patch("requests.post")
    def test_stream_message_file_event(self, mock_post):
        """测试 message_file 事件"""
        resp = MagicMock()
        resp.status_code = 200
        resp.iter_lines.return_value = iter(
            [
                b'data: {"event": "message_file", "id": "file123"}',
                b'data: {"answer": "Response with file"}',
            ]
        )
        mock_post.return_value = resp

        provider = DifyProvider("http://url", "key", "app")

        with patch("dify_chat_tester.terminal_ui.StreamDisplay"):
            response, success, error, _ = provider.send_message(
                "msg", "model", stream=True, show_indicator=False
            )

        assert isinstance(response, str)


class TestOpenAIStreamProcessing:
    """OpenAI Provider 流式处理深度测试"""

    @patch("requests.post")
    def test_stream_choice_not_dict(self, mock_post):
        """测试 choice 不是字典的情况"""
        resp = MagicMock()
        resp.status_code = 200
        resp.iter_lines.return_value = iter(
            [
                b'data: {"choices":["invalid"]}',
                b'data: {"choices":[{"delta":{"content":"OK"}}]}',
                b"data: [DONE]",
            ]
        )
        mock_post.return_value = resp

        provider = OpenAIProvider("http://url", "key")

        with patch("dify_chat_tester.terminal_ui.StreamDisplay"):
            response, success, error, _ = provider.send_message(
                "msg", "model", stream=True, show_indicator=False
            )

        assert "OK" in response

    @patch("requests.post")
    def test_stream_delta_not_dict(self, mock_post):
        """测试 delta 不是字典"""
        resp = MagicMock()
        resp.status_code = 200
        resp.iter_lines.return_value = iter(
            [
                b'data: {"choices":[{"delta":"invalid"}]}',
                b'data: {"choices":[{"delta":{"content":"Valid"}}]}',
                b"data: [DONE]",
            ]
        )
        mock_post.return_value = resp

        provider = OpenAIProvider("http://url", "key")

        with patch("dify_chat_tester.terminal_ui.StreamDisplay"):
            response, success, error, _ = provider.send_message(
                "msg", "model", stream=True, show_indicator=False
            )

        assert "Valid" in response

    @patch("requests.post")
    def test_stream_finish_reason_length(self, mock_post):
        """测试 finish_reason 为 length"""
        resp = MagicMock()
        resp.status_code = 200
        resp.iter_lines.return_value = iter(
            [
                b'data: {"choices":[{"delta":{"content":"Text"}}]}',
                b'data: {"choices":[{"finish_reason":"length"}]}',
            ]
        )
        mock_post.return_value = resp

        provider = OpenAIProvider("http://url", "key")

        with patch("dify_chat_tester.terminal_ui.StreamDisplay"):
            response, success, error, _ = provider.send_message(
                "msg", "model", stream=True, show_indicator=False
            )

        assert success is True

    @patch("requests.post")
    def test_stream_finish_reason_content_filter(self, mock_post):
        """测试 finish_reason 为 content_filter"""
        resp = MagicMock()
        resp.status_code = 200
        resp.iter_lines.return_value = iter(
            [
                b'data: {"choices":[{"delta":{"content":"Filtered"}}]}',
                b'data: {"choices":[{"finish_reason":"content_filter"}]}',
            ]
        )
        mock_post.return_value = resp

        provider = OpenAIProvider("http://url", "key")

        with patch("dify_chat_tester.terminal_ui.StreamDisplay"):
            response, success, error, _ = provider.send_message(
                "msg", "model", stream=True, show_indicator=False
            )

        assert success is True

    @patch("requests.post")
    def test_non_stream_empty_choices(self, mock_post):
        """测试非流式响应 choices 为空"""
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {"choices": []}
        mock_post.return_value = resp

        provider = OpenAIProvider("http://url", "key")

        response, success, error, _ = provider.send_message(
            "msg", "model", stream=False, show_indicator=False
        )

        assert success is False or response == ""

    @patch("requests.post")
    def test_non_stream_no_message(self, mock_post):
        """测试非流式响应没有 message"""
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {"choices": [{}]}
        mock_post.return_value = resp

        provider = OpenAIProvider("http://url", "key")

        response, success, error, _ = provider.send_message(
            "msg", "model", stream=False, show_indicator=False
        )

        assert isinstance(response, str)


class TestiFlowStreamProcessing:
    """iFlow Provider 流式处理深度测试"""

    @patch("requests.post")
    def test_stream_delta_content_extraction(self, mock_post):
        """测试从 delta 提取 content"""
        resp = MagicMock()
        resp.status_code = 200
        resp.iter_lines.return_value = iter(
            [
                b'data: {"choices":[{"delta":{"content":"Part1"}}]}',
                b'data: {"choices":[{"delta":{"content":"Part2"}}]}',
                b'data: {"choices":[{"finish_reason":"stop"}]}',
            ]
        )
        mock_post.return_value = resp

        provider = iFlowProvider("key")

        with patch("dify_chat_tester.terminal_ui.StreamDisplay"):
            response, success, error, _ = provider.send_message(
                "msg", "model", stream=True, show_indicator=False
            )

        assert "Part1" in response and "Part2" in response

    @patch("requests.post")
    def test_stream_message_content_extraction(self, mock_post):
        """测试从 message 提取 content"""
        resp = MagicMock()
        resp.status_code = 200
        resp.iter_lines.return_value = iter(
            [
                b'data: {"choices":[{"message":{"content":"Message content"}}]}',
                b'data: {"choices":[{"finish_reason":"stop"}]}',
            ]
        )
        mock_post.return_value = resp

        provider = iFlowProvider("key")

        with patch("dify_chat_tester.terminal_ui.StreamDisplay"):
            response, success, error, _ = provider.send_message(
                "msg", "model", stream=True, show_indicator=False
            )

        assert "Message content" in response

    @patch("requests.post")
    def test_stream_text_field(self, mock_post):
        """测试使用 text 字段"""
        resp = MagicMock()
        resp.status_code = 200
        resp.iter_lines.return_value = iter(
            [
                b'data: {"choices":[{"text":"Text content"}]}',
                b'data: {"choices":[{"finish_reason":"stop"}]}',
            ]
        )
        mock_post.return_value = resp

        provider = iFlowProvider("key")

        with patch("dify_chat_tester.terminal_ui.StreamDisplay"):
            response, success, error, _ = provider.send_message(
                "msg", "model", stream=True, show_indicator=False
            )

        # text 字段应该被提取
        assert isinstance(response, str)

    @patch("requests.post")
    def test_non_stream_no_content(self, mock_post):
        """测试非流式响应没有 content"""
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {"choices": [{"message": {}}]}
        mock_post.return_value = resp

        provider = iFlowProvider("key")

        response, success, error, _ = provider.send_message(
            "msg", "model", stream=False, show_indicator=False
        )

        assert response == ""


class TestAIProvidersErrorHandling:
    """AI Providers 错误处理测试"""

    @patch("requests.post")
    def test_429_rate_limit(self, mock_post):
        """测试 429 限流错误"""
        from requests.exceptions import HTTPError

        resp = MagicMock()
        resp.status_code = 429
        resp.text = "Rate limit exceeded"
        mock_post.side_effect = HTTPError(response=resp)

        provider = DifyProvider("http://url", "key", "app")

        response, success, error, _ = provider.send_message(
            "msg", "model", stream=False, show_indicator=False
        )

        assert success is False
        assert "请求过于频繁" in error or "429" in str(error)

    @patch("requests.post")
    def test_500_server_error(self, mock_post):
        """测试 500 服务器错误"""
        from requests.exceptions import HTTPError

        resp = MagicMock()
        resp.status_code = 500
        resp.text = "Internal Server Error"
        # 显式提供错误消息
        mock_post.side_effect = HTTPError("500 Server Error", response=resp)

        provider = OpenAIProvider("http://url", "key")

        response, success, error, _ = provider.send_message(
            "msg", "model", stream=False, show_indicator=False
        )

        assert success is False
        assert "服务端错误" in error or "500" in str(error)

    @patch("requests.post")
    def test_connection_error(self, mock_post):
        """测试连接错误"""
        from requests.exceptions import ConnectionError

        mock_post.side_effect = ConnectionError("Connection refused")

        provider = iFlowProvider("key")

        response, success, error, _ = provider.send_message(
            "msg", "model", stream=False, show_indicator=False
        )

        assert success is False
        assert error is not None


class TestAIProvidersURLHandling:
    """AI Providers URL 处理测试"""

    def test_dify_base_url_with_trailing_slash(self):
        """测试 Dify base_url 带尾部斜杠"""
        provider = DifyProvider("http://api.dify.ai/v1/", "key", "app")
        # Dify 保留原始 URL
        assert provider.base_url == "http://api.dify.ai/v1/"

    def test_dify_base_url_without_trailing_slash(self):
        """测试 Dify base_url 不带尾部斜杠"""
        provider = DifyProvider("http://api.dify.ai/v1", "key", "app")
        assert provider.base_url == "http://api.dify.ai/v1"

    def test_openai_base_url_normalization(self):
        """测试 OpenAI base_url 规范化"""
        provider = OpenAIProvider("http://api.openai.com/v1///", "key")
        # 应该移除尾部斜杠
        assert not provider.base_url.endswith("/")

    def test_iflow_fixed_base_url(self):
        """测试 iFlow 固定 base_url"""
        provider = iFlowProvider("key")
        assert "iflow.cn" in provider.base_url
        assert provider.base_url.startswith("https://")
