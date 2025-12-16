"""CLI 模块 - 命令行界面"""

from dify_chat_tester.cli.app import run_app
from dify_chat_tester.cli.selectors import (
    select_folder_path,
    select_main_function,
    select_mode,
    select_model,
    select_role,
)
from dify_chat_tester.cli.terminal import (
    StreamDisplay,
    console,
    input_api_key,
    print_api_key_confirmation,
    print_error,
    print_info,
    print_input_prompt,
    print_success,
    print_warning,
)

__all__ = [
    "run_app",
    "console",
    "print_error",
    "print_info",
    "print_success",
    "print_warning",
    "print_input_prompt",
    "input_api_key",
    "print_api_key_confirmation",
    "StreamDisplay",
    "select_role",
    "select_model",
    "select_mode",
    "select_main_function",
    "select_folder_path",
]
