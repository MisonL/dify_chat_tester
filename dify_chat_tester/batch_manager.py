"""
批量查询管理模块
负责处理批量询问模式的功能
"""

import os
import time
from datetime import datetime

import openpyxl

from dify_chat_tester.terminal_ui import (
    Panel,
    Text,
    box,
    console,
    print_error,
    print_file_list,
    print_input_prompt,
    print_statistics,
    print_success,
)
from dify_chat_tester.excel_utils import (
    init_excel_log,
    log_to_excel,
)

# 每多少条问题保存一次批量日志
SAVE_EVERY_N_QUERIES = 10


def run_batch_query(
    provider,
    selected_role: str,
    provider_name: str,
    selected_model: str,
    batch_request_interval: float,
    batch_default_show_response: bool,
):
    """运行批量询问模式"""
    console.print()

    # 模式信息面板
    mode_text = Text()
    mode_text.append("🤖 模型: ", style="bold yellow")
    mode_text.append(f"{selected_model}\n", style="bold cyan")
    mode_text.append("👤 角色: ", style="bold yellow")
    mode_text.append(f"{selected_role}\n", style="bold cyan")
    mode_text.append("💬 供应商: ", style="bold yellow")
    mode_text.append(f"{provider_name}", style="bold cyan")

    # Dify 不再需要显示应用 ID

    mode_panel = Panel(
        mode_text,
        title="[bold]📄 批量询问模式[/bold]",
        border_style="bright_magenta",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print(mode_panel)
    console.print()

    # 列出当前目录下的 Excel 文件
    excel_files = [f for f in os.listdir(".") if f.endswith(".xlsx") and os.path.isfile(f)]

    selected_excel_file = None
    while True:
        if excel_files:
            print_file_list(excel_files)
            file_input = print_input_prompt("请输入 Excel 文件序号或直接输入文件路径")

            try:
                file_index = int(file_input)
                if 1 <= file_index <= len(excel_files):
                    excel_file_path = excel_files[file_index - 1]
                else:
                    print(f"错误: 无效的文件序号 '{file_index}'。请重新输入。", file=console.file)
                    continue
            except ValueError:
                # 用户输入的是路径
                excel_file_path = file_input
        else:
            excel_file_path = print_input_prompt(
                "当前目录下没有找到 Excel 文件，请输入包含询问内容的 Excel 文件路径"
            )

        if not os.path.exists(excel_file_path):
            print(f"错误: 文件 '{excel_file_path}' 不存在。请重新输入。", file=console.file)
            continue

        try:
            batch_workbook = openpyxl.load_workbook(excel_file_path)
            batch_worksheet = batch_workbook.active
            if batch_worksheet is None:  # 确保工作表不为None
                print(f"错误: Excel 文件 '{excel_file_path}' 中没有活动工作表。请重新输入。", file=console.file)
                continue
            selected_excel_file = excel_file_path
            break  # 成功读取文件并获取工作表，跳出循环
        except Exception as e:
            print(
                f"错误: 无法读取 Excel 文件 '{excel_file_path}'。请确保文件格式正确且未被占用。错误信息: {e}。请重新输入。",
                file=console.file,
            )
            continue

    # 获取列名
    column_names = [cell.value for cell in batch_worksheet[1]]
    print_success(f"已选择文件: {selected_excel_file}")

    # 检查是否存在“文档名称”列（如果存在则复用）
    doc_name_col_index = None
    try:
        doc_name_col_index = column_names.index("文档名称")
    except ValueError:
        doc_name_col_index = None

    # 让用户通过序号选择问题列
    from dify_chat_tester.terminal_ui import select_column_by_index

    question_col_index = select_column_by_index(column_names, "请选择问题所在列的序号")

    # 注意：不再创建或使用回答列，所有结果只记录到日志文件

    # 询问是否显示每个问题的回答内容
    display_response_choice = print_input_prompt("是否在控制台显示每个问题的回答内容？ (Y/n)")
    show_batch_response = (
        (display_response_choice.lower() != "n") if display_response_choice else True
    )

    # 从配置中获取请求间隔时间（使用配置中的默认值）
    request_interval = batch_request_interval

    # 为批量模式设置 show_indicator（只有在用户选择显示响应时才启用）
    batch_show_indicator = show_batch_response

    # 详细日志文件，用于记录每次请求的详细信息
    output_file_name = f"batch_query_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    batch_log_headers = [
        "时间戳",
        "角色",
        "文档名称",
        "原始问题",
        f"{provider_name}响应",
        "是否成功",
        "错误信息",
        "对话ID",
    ]
    output_workbook, output_worksheet = init_excel_log(output_file_name, batch_log_headers)

    total_queries = 0
    successful_queries = 0
    failed_queries = 0
    # 自上次保存以来已处理的问题数量
    queries_since_last_save = 0
    start_time = time.time()

    total_rows = batch_worksheet.max_row - 1
    print(f"\n开始批量询问... (共 {total_rows} 行数据)")
    for row_idx in range(2, batch_worksheet.max_row + 1):  # 从第二行开始读取数据
        # 获取文档名称（如果输入表中存在对应列）
        doc_name = ""
        if doc_name_col_index is not None:
            doc_cell_value = batch_worksheet.cell(row=row_idx, column=doc_name_col_index + 1).value
            doc_name = str(doc_cell_value) if doc_cell_value is not None else ""

        question_cell_value = batch_worksheet.cell(row=row_idx, column=question_col_index + 1).value
        question = str(question_cell_value) if question_cell_value is not None else ""  # 确保转换为字符串

        if not question.strip():  # 检查问题是否为空或只包含空格
            print(f"警告: 第 {row_idx} 行问题为空，跳过。", file=console.file)
            failed_queries += 1  # 空问题也算作失败
            log_to_excel(
                output_worksheet,
                [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    selected_role,
                    doc_name,
                    question,  # 原始问题为空
                    "",
                    False,
                    "问题为空",
                    0,
                    "",
                ],
            )
            continue  # 跳过当前循环的剩余部分

        total_queries += 1  # 只有非空问题才计入总数

        # 计算进度
        current_progress = row_idx - 1
        pending_count = total_rows - current_progress
        progress_percent = (current_progress / total_rows) * 100

        # 美化问题显示（加粗和颜色）
        question_display = (
            f"[bold bright_magenta]处理进度 ({current_progress}/{total_rows} - {progress_percent:.1f}%) "
            f"| 待处理: {pending_count} | 问题:[/bold bright_magenta] "
            f"[bold yellow]{question[:50]}{'...' if len(question) > 50 else ''}[/bold yellow]"
        )
        console.print(f"\n{question_display}")

        response, success, error, conversation_id = provider.send_message(
            message=question,
            model=selected_model,
            role=selected_role,
            stream=True,
            show_indicator=batch_show_indicator,
        )

        if success:
            successful_queries += 1
            print(f"问题 (第 {total_queries} 个) 处理完成。")  # 简洁提示
        else:
            failed_queries += 1
            print(f"问题 (第 {total_queries} 个) 处理失败。错误: {error}")  # 简洁提示

        # 记录详细日志到新的Excel文件
        log_to_excel(
            output_worksheet,
            [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                selected_role,
                doc_name,
                question,
                response,
                success,
                error,
                conversation_id or "",
            ],
        )

        # 按批次保存日志，减少磁盘 IO
        queries_since_last_save += 1
        if queries_since_last_save >= SAVE_EVERY_N_QUERIES:
            try:
                output_workbook.save(output_file_name)
                queries_since_last_save = 0
            except PermissionError:
                print_error(f"警告：无法保存日志文件 '{output_file_name}'。请确保文件未被其他程序打开。")
            except Exception as e:
                print_error(f"警告：保存日志时出错：{e}")

        # 原始文件保持不变，只记录到日志文件

        time.sleep(request_interval)  # 间隔时间

    # 循环结束后做一次最终保存
    try:
        output_workbook.save(output_file_name)
    except PermissionError:
        print_error(f"警告：无法保存日志文件 '{output_file_name}'。请确保文件未被其他程序打开。")
    except Exception as e:
        print_error(f"警告：保存日志时出错：{e}")

    end_time = time.time()
    total_duration = end_time - start_time

    # 统计信息面板
    print_statistics(total_queries, successful_queries, failed_queries, total_duration)

    # 执行信息汇总面板
    summary_text = Text()
    summary_text.append("📁 文件信息\n", style="bold yellow")
    summary_text.append(f"  • 处理文件: {selected_excel_file}\n", style="white")
    summary_text.append(
        f"  • 问题列: {column_names[question_col_index]} (第{question_col_index+1}列)\n",
        style="white",
    )
    summary_text.append("  • 日志文件: 所有结果保存到独立日志文件\n\n", style="white")

    summary_text.append("🤖 模型配置\n", style="bold yellow")
    summary_text.append(f"  • AI 供应商: {provider_name}\n", style="white")
    summary_text.append(f"  • 选用模型: {selected_model}\n", style="white")
    summary_text.append(f"  • 角色设定: {selected_role}\n", style="white")

    # 添加 API 接口地址
    base_url = getattr(provider, "base_url", None)
    if base_url:
        summary_text.append(f"  • API 接口: {base_url}\n", style="white")

    # Dify 不再需要显示应用 ID

    summary_text.append("\n", style="white")

    success_rate = (successful_queries / total_queries * 100) if total_queries > 0 else 0
    summary_text.append("📊 执行统计\n", style="bold yellow")
    summary_text.append(f"  • 成功率: {success_rate:.1f}%\n", style="white")
    summary_text.append(f"  • 请求间隔: {batch_request_interval}秒\n", style="white")
    summary_text.append(f"  • 详细日志: {output_file_name}", style="white")

    summary_panel = Panel(
        summary_text,
        title="[bold]📋 执行信息汇总[/bold]",
        border_style="bright_magenta",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print()
    console.print(summary_panel)
    console.print()
