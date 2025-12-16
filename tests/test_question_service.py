"""QuestionService 模块的单元测试"""

from unittest.mock import MagicMock, patch

import pytest

from dify_chat_tester.services.question_service import QuestionService


class TestQuestionService:
    """测试 QuestionService 类"""

    @pytest.fixture
    def mock_provider(self):
        """创建模拟的 AI 供应商"""
        return MagicMock()

    @pytest.fixture
    def service(self, mock_provider):
        """创建 QuestionService 实例"""
        return QuestionService(
            provider=mock_provider,
            role="user",
            provider_name="TestProvider",
            model="test-model",
        )

    def test_init(self, service, mock_provider):
        """测试初始化"""
        assert service.provider == mock_provider
        assert service.role == "user"
        assert service.provider_name == "TestProvider"
        assert service.model == "test-model"

    @patch("dify_chat_tester.core.question.run_question_generation")
    @patch("dify_chat_tester.services.question_service.select_folder_path")
    def test_run_single_knowledge_generation_with_path(
        self, mock_select_folder, mock_run_gen, service
    ):
        """测试带路径的单一知识点生成"""
        service.run_single_knowledge_generation(folder_path="/test/path")

        mock_select_folder.assert_not_called()
        mock_run_gen.assert_called_once_with(
            provider=service.provider,
            role=service.role,
            provider_name=service.provider_name,
            selected_model=service.model,
            folder_path="/test/path",
        )

    @patch("dify_chat_tester.core.question.run_question_generation")
    @patch("dify_chat_tester.services.question_service.select_folder_path")
    def test_run_single_knowledge_generation_interactive(
        self, mock_select_folder, mock_run_gen, service
    ):
        """测试交互式单一知识点生成"""
        mock_select_folder.return_value = "/selected/path"

        service.run_single_knowledge_generation()

        mock_select_folder.assert_called_once_with(default_path="./kb-docs")
        mock_run_gen.assert_called_once()

    @patch("dify_chat_tester.core.question.run_cross_knowledge_generation")
    @patch("dify_chat_tester.services.question_service.select_folder_path")
    def test_run_cross_knowledge_generation_with_path(
        self, mock_select_folder, mock_run_cross, service
    ):
        """测试带路径的跨知识点生成"""
        service.run_cross_knowledge_generation(folder_path="/test/cross/path")

        mock_select_folder.assert_not_called()
        mock_run_cross.assert_called_once_with(
            provider=service.provider,
            role=service.role,
            provider_name=service.provider_name,
            selected_model=service.model,
            folder_path="/test/cross/path",
        )
