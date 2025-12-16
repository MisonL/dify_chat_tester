"""Question Generator 模块的深度测试"""

from unittest.mock import MagicMock, patch

from dify_chat_tester.core.question import run_question_generation


class TestQuestionGeneratorExtended:
    """Question Generator 扩展测试"""

    @patch("dify_chat_tester.core.question.read_markdown_files")
    @patch("dify_chat_tester.core.question.generate_questions_for_document")
    @patch("dify_chat_tester.core.question.export_questions_to_excel")
    def test_run_question_generation_flow(self, mock_export, mock_generate, mock_read):
        """测试问题生成完整流程"""
        # Mock 读取文件
        mock_read.return_value = (["doc1.md"], {"doc1.md": "Content"})

        # Mock 生成问题
        mock_generate.return_value = ["Q1", "Q2"]

        # Mock 导出
        mock_export.return_value = True

        # 运行
        run_question_generation(MagicMock(), "user", "Dify", "model", "dummy_path")

        # 验证
        mock_read.assert_called_with("dummy_path")
        mock_generate.assert_called_once()
        mock_export.assert_called_once()

    @patch("dify_chat_tester.core.question.read_markdown_files")
    @patch("dify_chat_tester.core.question.print_error")
    def test_run_question_generation_no_files(self, mock_error, mock_read):
        """测试没有 Markdown 文件"""
        mock_read.return_value = ([], {})

        run_question_generation(MagicMock(), "user", "Dify", "model", "dummy_path")

        mock_error.assert_called_with("没有找到可处理的文档")
