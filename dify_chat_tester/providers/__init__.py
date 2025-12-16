"""Providers 模块 - AI 供应商"""
from dify_chat_tester.providers.base import (
    AIProvider,
    DifyProvider,
    OpenAIProvider,
    iFlowProvider,
    get_provider,
)
from dify_chat_tester.providers.setup import (
    setup_dify_provider,
    setup_openai_provider,
    setup_iflow_provider,
    setup_plugin_provider,
    get_plugin_providers_config,
)
from dify_chat_tester.providers.plugin_manager import PluginManager

__all__ = [
    "AIProvider",
    "DifyProvider",
    "OpenAIProvider",
    "iFlowProvider",
    "get_provider",
    "setup_dify_provider",
    "setup_openai_provider",
    "setup_iflow_provider",
    "setup_plugin_provider",
    "get_plugin_providers_config",
    "PluginManager",
]
