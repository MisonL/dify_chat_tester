"""Selectors 模块的单元测试。

测试 select_model、select_role 等选择器函数。
"""

from unittest.mock import patch


from dify_chat_tester.selectors import select_model, select_role


class TestSelectModel:
    """测试 select_model 函数"""

    @patch('dify_chat_tester.selectors.print_input_prompt')
    def test_select_model_by_number(self, mock_input):
        """测试通过数字选择模型"""
        mock_input.return_value = "1"
        
        available_models = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
        result = select_model(available_models, "OpenAI")
        
        assert result == "gpt-4o"

    @patch('dify_chat_tester.selectors.print_input_prompt')
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

    @patch('dify_chat_tester.selectors.print_input_prompt')
    def test_select_custom_model(self, mock_input):
        """测试选择自定义模型"""
        # 先选择自定义模型选项，再输入模型名
        mock_input.side_effect = ["3", "my-custom-model"]
        
        available_models = ["gpt-4o", "gpt-4o-mini"]
        result = select_model(available_models, "OpenAI")
        
        assert result == "my-custom-model"


class TestSelectRole:
    """测试 select_role 函数"""

    @patch('dify_chat_tester.selectors.print_input_prompt')
    def test_select_role_by_number(self, mock_input):
        """测试通过数字选择角色"""
        mock_input.return_value = "1"
        
        available_roles = ["员工", "门店", "管理员"]
        result = select_role(available_roles)
        
        assert result == "员工"

    @patch('dify_chat_tester.selectors.print_input_prompt')
    def test_select_user_role(self, mock_input):
        """测试选择内置用户角色"""
        mock_input.return_value = "4"  # len(available_roles) + 1
        
        available_roles = ["员工", "门店", "管理员"]
        result = select_role(available_roles)
        
        assert result == "user"

    @patch('dify_chat_tester.selectors.print_input_prompt')
    def test_select_custom_role(self, mock_input):
        """测试选择自定义角色"""
        # 先选择自定义角色选项，再输入角色名
        mock_input.side_effect = ["5", "测试人员"]
        
        available_roles = ["员工", "门店", "管理员"]
        result = select_role(available_roles)
        
        assert result == "测试人员"

    @patch('dify_chat_tester.selectors.print_input_prompt')
    def test_select_role_by_name(self, mock_input):
        """测试直接输入角色名称"""
        mock_input.return_value = "产品经理"
        
        available_roles = ["员工", "门店"]
        result = select_role(available_roles)
        
        assert result == "产品经理"
