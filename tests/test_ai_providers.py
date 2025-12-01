"""AI Providers 模块的单元测试。

测试 DifyProvider、OpenAIProvider 和 iFlowProvider 的基本功能。
"""

from unittest.mock import Mock, patch


from dify_chat_tester.ai_providers import DifyProvider, OpenAIProvider, iFlowProvider


class TestDifyProvider:
    """测试 DifyProvider 类"""

    def test_init(self):
        """测试初始化"""
        provider = DifyProvider(
            base_url="https://api.dify.ai/v1",
            api_key="app-test-key",
            app_id="test-app-id"
        )
        assert provider.base_url == "https://api.dify.ai/v1"
        assert provider.api_key == "app-test-key"
        assert provider.app_id == "test-app-id"

    def test_get_models(self):
        """测试获取模型列表"""
        provider = DifyProvider(
            base_url="https://api.dify.ai/v1",
            api_key="app-test-key",
            app_id="test-app-id"
        )
        models = provider.get_models()
        assert isinstance(models, list)
        assert len(models) == 1
        assert "Dify App" in models[0]

    @patch('requests.post')
    def test_send_message_blocking_success(self, mock_post):
        """测试非流式消息发送成功"""
        # Mock 响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {
            "answer": "测试回答",
            "conversation_id": "conv-123"
        }
        mock_post.return_value = mock_response

        provider = DifyProvider(
            base_url="https://api.dify.ai/v1",
            api_key="app-test-key",
            app_id="test-app-id"
        )

        response, success, error, conv_id = provider.send_message(
            message="测试问题",
            model="Dify App",
            role="测试角色",
            stream=False,
            show_indicator=False
        )

        assert success is True
        assert response == "测试回答"
        assert error is None
        assert conv_id == "conv-123"

    @patch('requests.post')
    def test_send_message_http_error(self, mock_post):
        """测试 HTTP 错误处理"""
        # Mock HTTP 错误
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response
        mock_post.return_value.raise_for_status.side_effect = Exception("HTTP 401")

        provider = DifyProvider(
            base_url="https://api.dify.ai/v1",
            api_key="invalid-key",
            app_id="test-app-id"
        )

        response, success, error, conv_id = provider.send_message(
            message="测试问题",
            model="Dify App",
            stream=False,
            show_indicator=False
        )

        assert success is False
        assert response == ""
        assert error is not None


class TestOpenAIProvider:
    """测试 OpenAIProvider 类"""

    def test_init(self):
        """测试初始化"""
        provider = OpenAIProvider(
            base_url="https://api.openai.com/v1",
            api_key="sk-test-key"
        )
        assert provider.base_url == "https://api.openai.com/v1"
        assert provider.api_key == "sk-test-key"

    def test_get_models(self):
        """测试获取模型列表"""
        provider = OpenAIProvider(
            base_url="https://api.openai.com/v1",
            api_key="sk-test-key"
        )
        models = provider.get_models()
        assert isinstance(models, list)
        assert len(models) > 0
        assert "gpt-4o" in models

    @patch('requests.post')
    def test_send_message_blocking_success(self, mock_post):
        """测试非流式消息发送成功"""
        # Mock 响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "测试回答"
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        provider = OpenAIProvider(
            base_url="https://api.openai.com/v1",
            api_key="sk-test-key"
        )

        response, success, error, conv_id = provider.send_message(
            message="测试问题",
            model="gpt-4o",
            role="测试角色",
            stream=False,
            show_indicator=False
        )

        assert success is True
        assert response == "测试回答"
        assert error is None


class TestiFlowProvider:
    """测试 iFlowProvider 类"""

    def test_init(self):
        """测试初始化"""
        provider = iFlowProvider(api_key="sk-test-key")
        assert provider.base_url == "https://apis.iflow.cn/v1"
        assert provider.api_key == "sk-test-key"

    def test_get_models(self):
        """测试获取模型列表"""
        provider = iFlowProvider(api_key="sk-test-key")
        models = provider.get_models()
        assert isinstance(models, list)
        assert len(models) > 0
        assert "qwen3-max" in models

    @patch('requests.post')
    def test_send_message_blocking_success(self, mock_post):
        """测试非流式消息发送成功"""
        # Mock 响应
        mock_response = Mock()
        mock_response.status_code = 200
        # Mock iter_lines to return empty iterator for stream mode
        mock_response.iter_lines.return_value = iter([])
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "测试回答"
                    },
                    "finish_reason": "stop"
                }
            ]
        }
        mock_post.return_value = mock_response

        provider = iFlowProvider(api_key="sk-test-key")

        response, success, error, conv_id = provider.send_message(
            message="测试问题",
            model="qwen3-max",
            role="测试角色",
            stream=False,
            show_indicator=False
        )

        assert success is True
        assert response == "测试回答"
        assert error is None
