"""
应用控制器模块
负责管理主程序流程和用户交互逻辑
"""

import sys

from dify_chat_tester import __author__, __email__, __version__

# 导入功能模块
from dify_chat_tester.batch_manager import run_batch_query
from dify_chat_tester.chat_manager import run_interactive_chat
from dify_chat_tester.config_loader import get_config, parse_ai_providers
from dify_chat_tester.provider_setup import (
    setup_dify_provider,
    setup_iflow_provider,
    setup_openai_provider,
)
from dify_chat_tester.question_generator import run_question_generation
from dify_chat_tester.selectors import (
    select_folder_path,
    select_main_function,
    select_mode,
    select_model,
    select_role,
)
from dify_chat_tester.terminal_ui import (
    Panel,
    Text,
    box,
    console,
    print_error,
    print_info,
    print_input_prompt,
    print_welcome,
)


class AppController:
    """应用控制器类"""

    def __init__(self):
        """初始化控制器"""
        self.config = get_config()
        self._load_config()

    def _load_config(self):
        """加载配置参数"""
        self.ai_providers = parse_ai_providers(self.config.get("AI_PROVIDERS", ""))
        self.chat_log_file_name = self.config.get_str(
            "CHAT_LOG_FILE_NAME", "chat_log.xlsx"
        )
        self.roles = self.config.get_list("ROLES", ",")
        self.iflow_models = self.config.get_list("IFLOW_MODELS", ",")
        self.openai_models = self.config.get_list("OPENAI_MODELS", ",")
        self.batch_request_interval = self.config.get_float(
            "BATCH_REQUEST_INTERVAL", 1.0
        )
        self.batch_default_show_response = self.config.get_bool(
            "BATCH_DEFAULT_SHOW_RESPONSE", False
        )

    def _print_header(self):
        """打印程序头部信息"""
        # 打印欢迎信息
        print_welcome()

        # 版本和作者信息面板
        info_text = Text()
        info_text.append("版本: ", style="bold yellow")
        info_text.append(f"v{__version__}\n", style="bold cyan")
        info_text.append("作者: ", style="bold yellow")
        info_text.append(f"{__author__}\n", style="bold cyan")
        info_text.append("许可证: ", style="bold yellow")
        info_text.append("MIT\n", style="bold cyan")
        info_text.append("邮箱: ", style="bold yellow")
        info_text.append(f"{__email__}\n", style="bold cyan")
        info_text.append("项目:\n", style="bold yellow")
        info_text.append(
            "https://github.com/MisonL/dify_chat_tester", style="bold cyan"
        )

        info_panel = Panel(
            info_text,
            box=box.ROUNDED,
            padding=(0, 1),
            border_style="bright_cyan",
            width=50,  # 与标题面板保持一致的宽度
            expand=False,  # 不扩展宽度
        )
        console.print(info_panel)
        console.print()

    def _select_provider(self):
        """选择AI供应商"""
        print_info("请选择AI供应商:")
        for provider_id, provider_info in self.ai_providers.items():
            print(f"  {provider_id}. {provider_info['name']}")
        print("  0. 退出程序")
        console.print()

        while True:
            provider_choice = print_input_prompt("请输入供应商序号")
            try:
                provider_num = str(provider_choice)
                if provider_num == "0":
                    print_info("感谢使用 dify_chat_tester，再见！")
                    sys.exit(0)
                elif provider_num in self.ai_providers:
                    provider_info = self.ai_providers[provider_num]
                    provider_name = provider_info["name"]
                    provider_id = provider_info["id"]
                    return provider_name, provider_id
                else:
                    print_error("无效的供应商序号")
            except ValueError:
                print_error("请输入有效的数字！")

    def _setup_provider(self, provider_id):
        """设置AI供应商"""
        if provider_id == "dify":
            provider = setup_dify_provider()
            # Dify 不需要选择模型，直接使用 API 返回的模型
            all_models = provider.get_models()
        elif provider_id == "openai":
            provider = setup_openai_provider()
            available_models = self.openai_models
            # 获取可用模型
            models = provider.get_models()
            if models:
                # 过滤掉 None 值并转换为字符串
                filtered_models = [str(model) for model in models if model is not None]
                if filtered_models:
                    # 合并预设模型和API返回的模型
                    all_models = list(dict.fromkeys(available_models + filtered_models))
                else:
                    all_models = available_models
            else:
                all_models = available_models
        elif provider_id == "iflow":
            provider = setup_iflow_provider()
            available_models = self.iflow_models
            # 获取可用模型
            models = provider.get_models()
            if models:
                # 过滤掉 None 值并转换为字符串
                filtered_models = [str(model) for model in models if model is not None]
                if filtered_models:
                    # 合并预设模型和API返回的模型
                    all_models = list(dict.fromkeys(available_models + filtered_models))
                else:
                    all_models = available_models
            else:
                all_models = available_models
        else:
            print_error("未知的供应商！")
            return None, None

        return provider, all_models

    def _run_mode(
        self,
        mode_choice,
        provider,
        selected_role,
        provider_name,
        selected_model,
        provider_id=None,
    ):
        """运行选择的模式"""
        if mode_choice == "1":
            # 会话模式
            console.print()
            print_info("已选择: 会话模式")
            run_interactive_chat(
                provider,
                selected_role,
                provider_name,
                selected_model,
                self.chat_log_file_name,
                provider_id=provider_id,
            )
            return "continue"  # 返回标志，表示继续选择模式
        elif mode_choice == "2":
            # 批量询问模式
            console.print()
            print_info("已选择: 批量询问模式")
            run_batch_query(
                provider,
                selected_role,
                provider_name,
                selected_model,
                self.batch_request_interval,
                self.batch_default_show_response,
            )
            return "continue"  # 返回标志，表示继续选择模式
        elif mode_choice == "3":
            # 退出程序
            print_info("感谢使用 dify_chat_tester，再见！")
            sys.exit(0)

    def _run_question_generation(
        self,
        provider,
        selected_role,
        provider_name,
        selected_model,
        folder_path: str | None = None,
    ):
        """运行问题生成功能

        Args:
            provider: AI 提供商实例
            selected_role: 角色名称
            provider_name: 提供商名称（用于展示）
            selected_model: 模型名称
            folder_path: 文档文件夹路径；
                - 为 None 时，进入交互式选择；
                - 非 None 时，直接使用指定路径。
        """
        console.print()
        print_info("已选择: AI生成测试提问点")

        # 选择文档文件夹路径（未指定时走交互）
        if not folder_path:
            folder_path = select_folder_path(default_path="./kb-docs")

        # 运行问题生成
        run_question_generation(
            provider=provider,
            role=selected_role,
            provider_name=provider_name,
            selected_model=selected_model,
            folder_path=folder_path,
        )

    def run_question_generation_cli(self, folder_path: str | None = None) -> None:
        """从命令行直接运行“AI生成测试提问点”流程。

        此模式下：
        - 仍然通过交互方式选择 Provider / 模型；
        - 角色固定为 "user"；
        - 若提供 folder_path，则直接使用该路径；否则仍然交互选择。"""
        # 打印头部信息
        self._print_header()

        # 选择 AI 供应商
        provider_name, provider_id = self._select_provider()

        # 设置供应商
        provider, available_models = self._setup_provider(provider_id)
        if not provider:
            print_error("供应商初始化失败，程序退出。")
            sys.exit(1)

        # 选择模型
        selected_model = select_model(available_models, provider_name)

        # 使用固定角色 "user"
        selected_role = "user"

        # 运行问题生成
        self._run_question_generation(
            provider=provider,
            selected_role=selected_role,
            provider_name=provider_name,
            selected_model=selected_model,
            folder_path=folder_path,
        )

    def run(self):
        """运行主程序循环"""
        # 打印头部信息
        self._print_header()

        # 主循环
        while True:
            # 选择主功能
            function_choice = select_main_function()

            # 如果选择退出
            if function_choice == "0":
                print_info("感谢使用 dify_chat_tester，再见！")
                sys.exit(0)

            # 选择AI供应商
            provider_name, provider_id = self._select_provider()

            # 设置供应商
            provider, available_models = self._setup_provider(provider_id)
            if not provider:
                continue

            # 选择模型
            selected_model = select_model(available_models, provider_name)

            # 根据主功能选择执行不同的流程
            if function_choice == "2":
                # AI生成测试提问点 - 使用默认角色 "user"
                selected_role = "user"
                self._run_question_generation(
                    provider=provider,
                    selected_role=selected_role,
                    provider_name=provider_name,
                    selected_model=selected_model,
                )
                console.print()
                print_welcome()
                continue

            # AI问答测试功能 - 需要选择角色
            selected_role = select_role(self.roles)

            # 内层循环：选择运行模式（AI问答测试）
            while True:
                # 选择运行模式
                mode_choice = select_mode()

                # 运行选择的模式
                result = self._run_mode(
                    mode_choice,
                    provider,
                    selected_role,
                    provider_name,
                    selected_model,
                    provider_id,
                )

                # 如果是退出命令，跳出内层循环
                if mode_choice == "3":
                    break

                # 如果是从会话或批量模式返回，继续选择模式
                if result == "continue":
                    console.print()
                    print_welcome()
