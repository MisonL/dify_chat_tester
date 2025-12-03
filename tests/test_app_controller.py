"""AppController 模块的单元测试。"""

from unittest.mock import MagicMock, patch

import pytest

from dify_chat_tester.app_controller import AppController


class TestAppController:
    """测试 AppController 类"""

    @pytest.fixture
    def controller(self):
        """创建一个 AppController 实例，并 mock 必要的依赖"""
        with patch("dify_chat_tester.app_controller.get_config") as mock_get_config:
            mock_config = MagicMock()
            mock_config.get.return_value = "dify,openai"
            mock_config.get_str.return_value = "chat_log.xlsx"
            mock_config.get_list.return_value = ["role1", "role2"]
            mock_config.get_float.return_value = 1.0
            mock_config.get_bool.return_value = False
            mock_get_config.return_value = mock_config

            controller = AppController()
            return controller

    def test_init(self, controller):
        """测试初始化"""
        assert controller.chat_log_file_name == "chat_log.xlsx"
        assert controller.roles == ["role1", "role2"]
        assert controller.batch_request_interval == 1.0
        assert controller.batch_default_show_response is False

    @patch("dify_chat_tester.app_controller.setup_dify_provider")
    def test_setup_provider_dify(self, mock_setup, controller):
        """测试设置 Dify Provider"""
        mock_provider = MagicMock()
        mock_provider.get_models.return_value = ["Dify App"]
        mock_setup.return_value = mock_provider

        provider, models = controller._setup_provider("dify")

        assert provider == mock_provider
        assert models == ["Dify App"]
        mock_setup.assert_called_once()

    @patch("dify_chat_tester.app_controller.setup_openai_provider")
    def test_setup_provider_openai(self, mock_setup, controller):
        """测试设置 OpenAI Provider"""
        mock_provider = MagicMock()
        mock_provider.get_models.return_value = ["gpt-4o"]
        mock_setup.return_value = mock_provider

        controller.openai_models = ["default-model"]

        provider, models = controller._setup_provider("openai")

        assert provider == mock_provider
        assert "gpt-4o" in models
        assert "default-model" in models

    @patch("dify_chat_tester.app_controller.print_input_prompt")
    def test_select_provider(self, mock_input, controller):
        """测试选择 Provider"""
        controller.ai_providers = {
            "1": {"name": "Dify", "id": "dify"},
            "2": {"name": "OpenAI", "id": "openai"},
        }

        mock_input.return_value = "1"
        name, pid = controller._select_provider()
        assert name == "Dify"
        assert pid == "dify"

        mock_input.return_value = "2"
        name, pid = controller._select_provider()
        assert name == "OpenAI"
        assert pid == "openai"

    @patch("dify_chat_tester.app_controller.sys.exit")
    @patch("dify_chat_tester.app_controller.print_input_prompt")
    def test_select_provider_exit(self, mock_input, mock_exit, controller):
        """测试选择退出"""
        controller.ai_providers = {"1": {"name": "Dify", "id": "dify"}}
        mock_input.return_value = "0"
        # 让 sys.exit 抛出异常以打破循环
        mock_exit.side_effect = SystemExit(0)

        with pytest.raises(SystemExit):
            controller._select_provider()

        mock_exit.assert_called_with(0)

    @patch("dify_chat_tester.app_controller.run_question_generation")
    @patch("dify_chat_tester.app_controller.select_model")
    def test_run_question_generation_cli(
        self, mock_select_model, mock_run_gen, controller
    ):
        """测试 CLI 模式运行问题生成"""
        # Mock _select_provider
        controller._select_provider = MagicMock(return_value=("Dify", "dify"))

        # Mock _setup_provider
        mock_provider = MagicMock()
        controller._setup_provider = MagicMock(return_value=(mock_provider, ["model1"]))

        mock_select_model.return_value = "model1"

        # Run
        controller.run_question_generation_cli(folder_path="/test/path")

        # Verify
        mock_run_gen.assert_called_once()
        args, kwargs = mock_run_gen.call_args
        assert kwargs["provider"] == mock_provider
        assert kwargs["role"] == "user"
        assert kwargs["folder_path"] == "/test/path"


class TestAppControllerAdditional:
    """AppController 额外测试"""

    @pytest.fixture
    def controller(self):
        """创建测试用的 controller"""
        with patch("dify_chat_tester.app_controller.get_config") as mock_get_config:
            mock_config = MagicMock()
            mock_config.get.return_value = "dify,openai,iflow"
            mock_config.get_str.return_value = "chat_log.xlsx"
            mock_config.get_list.return_value = ["role1"]
            mock_config.get_float.return_value = 1.0
            mock_config.get_bool.return_value = False
            mock_get_config.return_value = mock_config

            controller = AppController()
            return controller

    @patch("dify_chat_tester.app_controller.setup_iflow_provider")
    def test_setup_provider_iflow(self, mock_setup, controller):
        """测试设置 iFlow Provider"""
        mock_provider = MagicMock()
        mock_provider.get_models.return_value = ["qwen3-max"]
        mock_setup.return_value = mock_provider

        controller.iflow_models = ["default-model"]

        provider, models = controller._setup_provider("iflow")

        assert provider == mock_provider
        assert "qwen3-max" in models

    @patch("dify_chat_tester.app_controller.setup_dify_provider")
    def test_setup_provider_dify_no_models(self, mock_setup, controller):
        """测试 Dify Provider 没有返回模型"""
        mock_provider = MagicMock()
        mock_provider.get_models.return_value = []
        mock_setup.return_value = mock_provider

        provider, models = controller._setup_provider("dify")

        assert provider == mock_provider
        assert isinstance(models, list)

    @patch("dify_chat_tester.app_controller.print_error")
    def test_setup_provider_unknown(self, mock_error, controller):
        """测试未知的 Provider"""
        provider, models = controller._setup_provider("unknown")

        assert provider is None
        assert models is None
        mock_error.assert_called_once()

    @patch("dify_chat_tester.app_controller.sys.exit")
    @patch("dify_chat_tester.app_controller.print_info")
    @patch("dify_chat_tester.app_controller.run_interactive_chat")
    def test_run_mode_interactive(
        self, mock_run_chat, mock_info, mock_exit, controller
    ):
        """测试运行会话模式"""
        mock_provider = MagicMock()

        result = controller._run_mode(
            "1", mock_provider, "role", "OpenAI", "model", "openai"
        )

        assert result == "continue"
        mock_run_chat.assert_called_once()

    @patch("dify_chat_tester.app_controller.sys.exit")
    @patch("dify_chat_tester.app_controller.print_info")
    @patch("dify_chat_tester.app_controller.run_batch_query")
    def test_run_mode_batch(self, mock_run_batch, mock_info, mock_exit, controller):
        """测试运行批量模式"""
        mock_provider = MagicMock()

        result = controller._run_mode(
            "2", mock_provider, "role", "Dify", "model", "dify"
        )

        assert result == "continue"
        mock_run_batch.assert_called_once()
