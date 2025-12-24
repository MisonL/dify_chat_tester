"""
Dify Chat Tester - AI 聊天客户端测试工具

支持多种 AI 供应商：Dify、OpenAI 兼容接口、iFlow

作者：Mison
邮箱：1360962086@qq.com
仓库：https://github.com/MisonL/dify_chat_tester
许可证：MIT
"""

from dify_chat_tester._version import __author__, __email__, __version__

# CLI
from dify_chat_tester.cli.app import run_app
from dify_chat_tester.cli.terminal import (
    console,
    print_error,
    print_info,
    print_success,
    print_warning,
)

# 向后兼容导出 - 保持旧的导入路径可用
# 配置
from dify_chat_tester.config.loader import ConfigLoader, get_config, parse_ai_providers
from dify_chat_tester.config.logging import get_logger

# 核心业务
from dify_chat_tester.core.batch import run_batch_query
from dify_chat_tester.core.chat import run_interactive_chat

# 供应商
from dify_chat_tester.providers.base import (
    AIProvider,
    DifyProvider,
    OpenAIProvider,
    get_provider,
    iFlowProvider,
)

# 工具
from dify_chat_tester.utils.excel import init_excel_log, log_to_excel
from dify_chat_tester.utils.exceptions import (
    ConfigError,
    DifyChatTesterError,
    NetworkError,
    ProviderError,
)

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    # 配置
    "get_config",
    "parse_ai_providers",
    "ConfigLoader",
    "get_logger",
    # CLI
    "run_app",
    "console",
    "print_error",
    "print_info",
    "print_success",
    "print_warning",
    # 核心
    "run_batch_query",
    "run_interactive_chat",
    # 供应商
    "AIProvider",
    "DifyProvider",
    "OpenAIProvider",
    "iFlowProvider",
    "get_provider",
    # 工具
    "init_excel_log",
    "log_to_excel",
    "DifyChatTesterError",
    "ConfigError",
    "ProviderError",
    "NetworkError",
]
