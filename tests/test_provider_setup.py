"""Provider Setup 模块的单元测试。"""

from unittest.mock import MagicMock, patch

from dify_chat_tester.provider_setup import (
    setup_dify_provider,
    setup_iflow_provider,
    setup_openai_provider,
)


@patch("dify_chat_tester.provider_setup.get_provider")
@patch("dify_chat_tester.provider_setup._config")
def test_setup_dify_provider_from_config(mock_config, mock_get_provider):
    """测试从配置设置 Dify Provider"""
    # Mock config
    mock_config.get_str.side_effect = lambda k, d: {
        "DIFY_BASE_URL": "https://api.dify.ai",
        "DIFY_API_KEY": "dify-key",
        "DIFY_APP_ID": "app-id"
    }.get(k, d)
    
    setup_dify_provider()
    
    mock_get_provider.assert_called_with(
        "dify",
        base_url="https://api.dify.ai",
        api_key="dify-key",
        app_id="app-id"
    )


@patch("dify_chat_tester.provider_setup.get_provider")
@patch("dify_chat_tester.provider_setup._config")
@patch("dify_chat_tester.provider_setup.print_input_prompt")
@patch("dify_chat_tester.provider_setup.input_api_key")
@patch("dify_chat_tester.provider_setup.print_api_key_confirmation")
def test_setup_dify_provider_interactive(
    mock_confirm, mock_input_key, mock_input_prompt, mock_config, mock_get_provider
):
    """测试交互式设置 Dify Provider"""
    # Config returns empty
    mock_config.get_str.return_value = ""
    
    # Mock inputs
    mock_input_prompt.side_effect = ["https://api.dify.ai/v1", "app-id"]
    mock_input_key.return_value = "dify-key"
    mock_confirm.return_value = True
    
    setup_dify_provider()
    
    mock_get_provider.assert_called_with(
        "dify",
        base_url="https://api.dify.ai/v1",
        api_key="dify-key",
        app_id="app-id"
    )


@patch("dify_chat_tester.provider_setup.get_provider")
@patch("dify_chat_tester.provider_setup._config")
def test_setup_openai_provider_from_config(mock_config, mock_get_provider):
    """测试从配置设置 OpenAI Provider"""
    mock_config.get_str.side_effect = lambda k, d: {
        "OPENAI_BASE_URL": "https://api.openai.com",
        "OPENAI_API_KEY": "openai-key"
    }.get(k, d)
    
    setup_openai_provider()
    
    mock_get_provider.assert_called_with(
        "openai",
        base_url="https://api.openai.com",
        api_key="openai-key"
    )


@patch("dify_chat_tester.provider_setup.get_provider")
@patch("dify_chat_tester.provider_setup._config")
def test_setup_iflow_provider_from_config(mock_config, mock_get_provider):
    """测试从配置设置 iFlow Provider"""
    mock_config.get_str.side_effect = lambda k, d: {
        "IFLOW_API_KEY": "iflow-key"
    }.get(k, d)
    
    setup_iflow_provider()
    
    mock_get_provider.assert_called_with(
        "iflow",
        api_key="iflow-key"
    )


def test_normalize_base_url():
    """测试 URL 规范化"""
    from dify_chat_tester.provider_setup import _normalize_base_url
    
    # 正常 URL
    assert _normalize_base_url("https://api.example.com") == "https://api.example.com"
    
    # 没有协议的 URL
    assert _normalize_base_url("api.example.com") == "https://api.example.com"
    
    # 带空格的 URL
    assert _normalize_base_url("  https://api.example.com  ") == "https://api.example.com"
    
    # 空 URL
    assert _normalize_base_url("") == ""
    assert _normalize_base_url(None) == ""


@patch("dify_chat_tester.provider_setup.get_provider")
@patch("dify_chat_tester.provider_setup._config")
@patch("dify_chat_tester.provider_setup.print_api_key_confirmation")
@patch("dify_chat_tester.provider_setup.input_api_key")
@patch("dify_chat_tester.provider_setup.print_input_prompt")
def test_setup_openai_provider_interactive(
    mock_input, mock_input_key, mock_confirm, mock_config, mock_get_provider
):
    """测试交互式设置 OpenAI Provider"""
    # Config 为空，触发交互式输入
    mock_config.get_str.return_value = ""
    
    # Mock 用户输入
    mock_input.return_value = "https://api.openai.com/v1"
    mock_input_key.return_value = "sk-test-key"
    mock_confirm.return_value = True
    
    setup_openai_provider()
    
    mock_get_provider.assert_called_with(
        "openai",
        base_url="https://api.openai.com/v1",
        api_key="sk-test-key"
    )


@patch("dify_chat_tester.provider_setup.get_provider")
@patch("dify_chat_tester.provider_setup._config")
@patch("dify_chat_tester.provider_setup.print_api_key_confirmation")
@patch("dify_chat_tester.provider_setup.input_api_key")
def test_setup_iflow_provider_interactive(
    mock_input_key, mock_confirm, mock_config, mock_get_provider
):
    """测试交互式设置 iFlow Provider"""
    # Config 为空
    mock_config.get_str.return_value = ""
    
    # Mock 用户输入
    mock_input_key.return_value = "iflow-test-key"
    mock_confirm.return_value = True
    
    setup_iflow_provider()
    
    mock_get_provider.assert_called_with(
        "iflow",
        api_key="iflow-test-key"
    )

