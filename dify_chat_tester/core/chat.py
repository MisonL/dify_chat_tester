"""
聊天管理模块
负责处理交互式聊天模式的功能
"""

from datetime import datetime

from dify_chat_tester.cli.terminal import (
    Icons,
    console,
    print_error,
    print_input_prompt,
    print_success,
)
from dify_chat_tester.config.loader import get_config
from dify_chat_tester.utils.excel import init_excel_log, log_to_excel

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
            console.print("  /help   查看命令说明", style="white")
            console.print("  /new    开启新对话（重置上下文）", style="white")
            console.print("  /export 导出当前对话记录", style="white")
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

        # 处理导出命令
        if user_input.startswith("/export"):
            try:
                import pyperclip
            except ImportError:
                pyperclip = None

            args = user_input.split()
            mode = "menu"
            if len(args) > 1:
                mode = args[1].lower()

            # 准备导出内容
            export_content = ""
            if not history and not conversation_id:
                # 如果没有历史变量（Dify模式且未自行维护history），尝试从 worksheet 读取本次会话
                # 注意：Dify模式下 history 变量目前是空的（除非在 else 分支更新了）。
                # 但我们在上一步修复中，并没有给 is_dify 的分支更新 history！
                # 只有非 Dify 模式才更新 history。
                # Dify 模式下我们只有 Excel 里的日志。
                # 这是一个问题。为了支持 Dify 模式导出，我们也应该在 is_dify 分支维护 history 列表，仅用于显示/导出。
                pass
            
            # 使用 history 列表生成文本
            if history:
                 export_content = f"# 对话记录 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n\n"
                 for msg in history:
                     role = msg.get("role", "unknown")
                     content = msg.get("content", "")
                     if role == "user":
                         export_content += f"**User**: {content}\n\n"
                     else:
                         export_content += f"**AI**: {content}\n\n"
            else:
                 # 如果 history 空，说明可能没记录（例如 Dify 模式）
                 # 我们需要修改下面的逻辑，让所有模式都记录 history
                 export_content = "暂无内存中的对话历史记录。"

            if mode == "menu":
                console.print()
                console.print(f"{Icons.INFO} 请选择导出方式:", style="bold cyan")
                console.print("  1. 剪切板 (Clipboard)", style="white")
                console.print("  2. Markdown 文件 (File)", style="white")
                console.print("  0. 取消", style="white")
                choice = print_input_prompt("请输入序号")
                if choice == "1":
                    mode = "clip"
                elif choice == "2":
                    mode = "file"
                else:
                    console.print("已取消")
                    continue
            
            if mode in ["clip", "clipboard"]:
                if pyperclip:
                    try:
                        pyperclip.copy(export_content)
                        print_success("对话记录已复制到剪切板！")
                    except Exception as e:
                        print_error(f"复制到剪切板失败: {e}")
                else:
                    print_error("未安装 pyperclip 库，无法使用剪切板功能。")
            
            elif mode in ["file", "md", "markdown"]:
                filename = f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                try:
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(export_content)
                    print_success(f"对话记录已导出到: {filename}")
                except Exception as e:
                    print_error(f"导出文件失败: {e}")
            else:
                print_error(f"未知的导出模式: {mode}")
            
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
            
            # 同时也更新本地历史记录，以便用于 /export 功能
            if success:
                history.append({"role": "user", "content": user_input})
                history.append({"role": "assistant", "content": response})
                # 保持历史在合理长度内
                if len(history) > 20:
                    history = history[-20:]
        else:  # OpenAI 或 iFlow 或 其他插件
            response, success, error, new_conversation_id = provider.send_message(
                message=user_input,
                model=selected_model,
                role=selected_role,
                history=history,  # 传入历史
                conversation_id=conversation_id, # ！！！统一传入 conversation_id
                stream=True,
                show_indicator=True,
                show_thinking=enable_thinking,
            )
            
            # ！！！统一更新对话ID（如果供应商返回了新的ID）
            if new_conversation_id:
                conversation_id = new_conversation_id
                
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
