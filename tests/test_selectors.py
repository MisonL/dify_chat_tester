"""Selectors 模块的单元测试。

测试 select_model、select_role 等选择器函数。
"""

from unittest.mock import patch

from dify_chat_tester.cli.selectors import (
    select_folder_path,
    select_main_function,
    select_mode,
    select_model,
    select_role,
)


class TestSelectModel:
    """测试 select_model 函数"""

    @patch("dify_chat_tester.cli.selectors.print_input_prompt")
    def test_select_model_by_number(self, mock_input):
        """测试通过数字选择模型"""
        mock_input.return_value = "1"

        available_models = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
        result = select_model(available_models, "OpenAI")

        assert result == "gpt-4o"

    @patch("dify_chat_tester.cli.selectors.print_input_prompt")
    def test_select_model_by_name(self, mock_input):
        """测试直接输入模型名称"""
        mock_input.return_value = "custom-model"

        available_models = ["gpt-4o", "gpt-4o-mini"]
        result = select_model(available_models, "OpenAI")

        assert result == "custom-model"

    def test_select_model_single_dify(self):
        """测试单个 Dify 模型自动选择"""
        available_models = ["Dify App (使用应用 ID)"]
        result = select_model(available_models, "Dify")

        assert result == "Dify App (使用应用 ID)"

    @patch("dify_chat_tester.cli.selectors.print_input_prompt")
    def test_select_custom_model(self, mock_input):
        """测试选择自定义模型"""
        # 先选择自定义模型选项，再输入模型名
        mock_input.side_effect = ["3", "my-custom-model"]

        available_models = ["gpt-4o", "gpt-4o-mini"]
        result = select_model(available_models, "OpenAI")

        assert result == "my-custom-model"


class TestSelectRole:
    """测试 select_role 函数"""

    @patch("dify_chat_tester.cli.selectors.print_input_prompt")
    def test_select_role_by_number(self, mock_input):
        """测试通过数字选择角色"""
        mock_input.return_value = "1"

        available_roles = ["员工", "门店", "管理员"]
        result = select_role(available_roles)

        assert result == "员工"

    @patch("dify_chat_tester.cli.selectors.print_input_prompt")
    def test_select_user_role(self, mock_input):
        """测试选择内置用户角色"""
        mock_input.return_value = "4"  # len(available_roles) + 1

        available_roles = ["员工", "门店", "管理员"]
        result = select_role(available_roles)

        assert result == "user"

    @patch("dify_chat_tester.cli.selectors.print_input_prompt")
    def test_select_custom_role(self, mock_input):
        """测试选择自定义角色"""
        # 先选择自定义角色选项，再输入角色名
        mock_input.side_effect = ["5", "测试人员"]

        available_roles = ["员工", "门店", "管理员"]
        result = select_role(available_roles)

        assert result == "测试人员"

    @patch("dify_chat_tester.cli.selectors.print_input_prompt")
    def test_select_role_by_name(self, mock_input):
        """测试直接输入角色名称"""
        mock_input.return_value = "产品经理"

        available_roles = ["员工", "门店"]
        result = select_role(available_roles)

        assert result == "产品经理"


class TestSelectMode:
    """测试 select_mode 函数"""

    @patch("dify_chat_tester.cli.selectors.print_input_prompt")
    def test_select_chat_mode(self, mock_input):
        mock_input.return_value = "1"
        result = select_mode()
        assert result == "1"

    @patch("dify_chat_tester.cli.selectors.print_input_prompt")
    def test_select_batch_mode(self, mock_input):
        mock_input.return_value = "2"
        result = select_mode()
        assert result == "2"

    @patch("dify_chat_tester.cli.selectors.print_input_prompt")
    def test_select_exit(self, mock_input):
        mock_input.return_value = "3"
        result = select_mode()
        assert result == "3"

    @patch("dify_chat_tester.cli.selectors.print_input_prompt")
    def test_invalid_retry(self, mock_input):
        mock_input.side_effect = ["invalid", "1"]
        result = select_mode()
        assert result == "1"


class TestSelectMainFunction:
    """测试 select_main_function 函数"""

    @patch("dify_chat_tester.cli.selectors.print_input_prompt")
    def test_select_chat_mode(self, mock_input):
        mock_input.return_value = "1"
        result = select_main_function()
        assert result == "1"

    @patch("dify_chat_tester.cli.selectors.print_input_prompt")
    def test_select_question_gen_mode(self, mock_input):
        mock_input.return_value = "2"
        result = select_main_function()
        assert result == "2"

    @patch("dify_chat_tester.cli.selectors.print_input_prompt")
    def test_select_exit(self, mock_input):
        mock_input.return_value = "0"
        result = select_main_function()
        assert result == "0"


class TestSelectFolderPath:
    """测试 select_folder_path 函数"""

    @patch("dify_chat_tester.cli.selectors.print_input_prompt")
    def test_select_default_path(self, mock_input):
        """测试选择默认路径"""
        mock_input.return_value = "1"
        result = select_folder_path("./default/path")
        assert result == "./default/path"

    @patch("dify_chat_tester.cli.selectors.print_input_prompt")
    def test_select_custom_path(self, mock_input):
        """测试输入自定义路径"""
        mock_input.side_effect = ["2", "/custom/path"]
        result = select_folder_path("./default/path")
        assert result == "/custom/path"

    @patch("dify_chat_tester.cli.selectors.print_input_prompt")
    @patch("pathlib.Path.iterdir")
    def test_select_existing_folder(self, mock_iterdir, mock_input):
        """测试选择当前目录下的文件夹"""
        from unittest.mock import MagicMock

        # 模拟 Path 对象
        mock_folder1 = MagicMock()
        mock_folder1.is_dir.return_value = True
        mock_folder1.name = "folder1"
        mock_folder1.__str__.return_value = "folder1"

        mock_folder2 = MagicMock()
        mock_folder2.is_dir.return_value = True
        mock_folder2.name = "folder2"
        mock_folder2.__str__.return_value = "folder2"

        mock_file1 = MagicMock()
        mock_file1.is_dir.return_value = False
        mock_file1.name = "file1"

        mock_iterdir.return_value = [mock_folder1, mock_file1, mock_folder2]

        # 选择列表中的第一个文件夹 (folder1)
        # 菜单项: 1.默认, 2.自定义, 3.folder1, 4.folder2
        mock_input.return_value = "3"

        result = select_folder_path("./default/path")
        # 注意：select_folder_path 返回的是 str(folder)
        assert result == "folder1"
