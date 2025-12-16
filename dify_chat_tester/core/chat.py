"""
聊天管理模块
负责处理交互式聊天模式的功能
"""

from datetime import datetime

from dify_chat_tester.config.loader import get_config
from dify_chat_tester.utils.excel import init_excel_log, log_to_excel
from dify_chat_tester.cli.terminal import (
    Icons,
    console,
    print_error,
    print_input_prompt,
    print_success,
)

# 每多少轮对话保存一次聊天日志
SAVE_EVERY_N_ROUNDS = 5


def run_interactive_chat(
    provider,
    selected_role: str,
    provider_name: str,
    selected_model: str,
    chat_log_file_name: str,
    provider_id: str = None,
):
    """运行会话模式"""
    # 获取配置
    config = get_config()
    enable_thinking = config.get_enable_thinking()

    # 初始化 Excel
    chat_headers = [
        "时间戳",
        "角色",
        "用户输入",
        f"{provider_name}响应",
        "是否成功",
        "错误信息",
        "对话轮次",
        "对话ID",
    ]
    workbook, worksheet = init_excel_log(chat_log_file_name, chat_headers)

    print_success(f"已选择角色: {selected_role}")
    print_success(f"已选择模型: {selected_model}")
    if enable_thinking:
        console.print(f"{Icons.INFO} 思维链显示已开启", style="bright_green")
    console.print()
    console.print(f"{Icons.INFO} 命令说明:", style="bold cyan")
    console.print(f"  {Icons.USER} 输入 '/help' 查看命令说明", style="white")
    console.print(f"  {Icons.USER} 输入 '/exit' 或 '/quit' 返回模式选择", style="white")
    console.print(
        f"  {Icons.USER} 输入 '/new' 开启新的对话（重置上下文）", style="white"
    )
    console.print()

    # 多轮对话支持
    conversation_id = None  # 对话ID，用于维护Dify的多轮对话上下文
    history = []  # 对话历史，用于维护OpenAI/iFlow的多轮对话上下文
    conversation_round = 0  # 对话轮次计数器

    # 聊天循环
    while True:
        user_input = print_input_prompt(f"{Icons.USER} 你")
        user_input = user_input.strip()

        # 处理帮助命令
        if user_input == "/help":
            console.print()
            console.print(f"{Icons.INFO} 可用命令:", style="bold cyan")
            console.print(
                f"  {Icons.USER} 直接输入内容：向 {provider_name} 提问", style="white"
            )
            console.print("  /help  查看命令说明", style="white")
            console.print("  /new   开启新对话（重置上下文）", style="white")
            console.print("  /exit 或 /quit 返回模式选择", style="white")
            console.print()
            continue

        # 处理退出命令 - 返回运行模式选择
        if user_input.lower() in ["/exit", "/quit"]:
            # 关闭工作簿（日志已实时保存）
            try:
                workbook.close()
            except Exception:
                pass  # 静默处理错误
            return  # 直接返回，不显示任何消息

        # 处理开启新对话命令
        if user_input == "/new":
            conversation_id = None
            history = []  # 清空历史
            conversation_round = 0
            console.print()
            print_success("已开启新对话（上下文已重置）")
            console.print()
            continue

        conversation_round += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 根据供应商类型调用 send_message
        is_dify = (provider_id == "dify") if provider_id else (provider_name == "Dify")

        if is_dify:
            response, success, error, new_conversation_id = provider.send_message(
                message=user_input,
                model=selected_model,
                role=selected_role,
                conversation_id=conversation_id,
                stream=True,
                show_indicator=True,
                show_thinking=enable_thinking,
            )
            # 更新Dify的对话ID
            if new_conversation_id:
                conversation_id = new_conversation_id
        else:  # OpenAI 或 iFlow
            response, success, error, _ = provider.send_message(
                message=user_input,
                model=selected_model,
                role=selected_role,
                history=history,  # 传入历史
                stream=True,
                show_indicator=True,
                show_thinking=enable_thinking,
            )
            # 更新OpenAI/iFlow的对话历史
            if success:
                history.append({"role": "user", "content": user_input})
                history.append({"role": "assistant", "content": response})
                # 保持历史在合理长度内（例如，最多20条消息，即10轮对话）
                if len(history) > 20:
                    history = history[-20:]

        # 记录到 Excel
        log_to_excel(
            worksheet,
            [
                timestamp,
                selected_role,
                user_input,
                response,
                success,
                error,
                conversation_round,
                conversation_id or "",  # 确保传递字符串（None时用空字符串）
            ],
        )

        # 按轮次批量保存日志，减少 IO 频率
        if conversation_round % SAVE_EVERY_N_ROUNDS == 0:
            try:
                workbook.save(chat_log_file_name)
            except PermissionError:
                print_error(
                    f"警告：无法保存日志文件 '{chat_log_file_name}'。请确保文件未被其他程序打开。"
                )
            except Exception as e:
                print_error(f"警告：保存日志时出错：{e}")

    # 注意：循环通过 /exit 或 /quit 返回调用方，此处不再额外处理
