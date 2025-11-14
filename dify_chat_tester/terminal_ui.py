"""
终端界面美化模块
提供颜色、进度条、动画等美化功能
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich import box
import colorama
import sys

# 初始化 colorama（Windows 兼容）
colorama.init(autoreset=True)

# 设置控制台窗口标题（Windows）
if sys.platform == 'win32':
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleTitleW("dify_chat_tester - AI聊天测试工具")
    except:
        pass

# 创建全局控制台对象
console = Console()

# 自定义颜色主题
class Colors:
    """自定义颜色方案"""
    BACKGROUND = "#000000"  # 黑色背景
    PRIMARY = "#61dafb"    # React蓝
    SUCCESS = "#4ade80"    # 绿色
    WARNING = "#fbbf24"    # 黄色
    ERROR = "#f87171"      # 红色
    INFO = "#60a5fa"       # 信息蓝
    ACCENT = "#c084fc"     # 紫色
    TEXT = "#f3f4f6"       # 主文本色
    MUTED = "#9ca3af"      # 次要文本色

# 图标定义
class Icons:
    """Unicode 图标"""
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    LOADING = "⏳"
    SPARKLES = "✨"
    TARGET = "🎯"
    GEAR = "⚙️"
    DIAMOND = "💎"
    CRYSTAL = "🔮"
    RAINBOW = "🌈"
    NEON = "💫"
    GLITCH = "🌠"
    TECH = "🔧"
    CODE = "💻"
    DATA = "📊"
    FIRE = "🔥"
    USER = "👤" # main.py is using this

def print_success(message: str):
    """打印成功信息"""
    success_text = Text()
    success_text.append(f"✅ {message}", style=f"bold {Colors.SUCCESS}")
    
    success_panel = Panel(
        success_text,
        border_style=Colors.SUCCESS,
        box=box.ROUNDED,
        padding=(0, 1)
    )
    console.print(success_panel)

def print_error(message: str):
    """打印错误信息"""
    error_text = Text()
    error_text.append(f"❌ {message}", style=f"bold {Colors.ERROR}")
    
    error_panel = Panel(
        error_text,
        border_style=Colors.ERROR,
        box=box.ROUNDED,
        padding=(0, 1)
    )
    console.print(error_panel)

def print_warning(message: str):
    """打印警告信息"""
    warning_text = Text()
    warning_text.append(f"⚠️ {message}", style=f"bold {Colors.WARNING}")
    
    warning_panel = Panel(
        warning_text,
        border_style=Colors.WARNING,
        box=box.ROUNDED,
        padding=(0, 1)
    )
    console.print(warning_panel)

def print_info(message: str):
    """打印信息"""
    info_text = Text()
    info_text.append(f"ℹ️ {message}", style=f"bold {Colors.INFO}")
    
    info_panel = Panel(
        info_text,
        border_style=Colors.INFO,
        box=box.ROUNDED,
        padding=(0, 1)
    )
    console.print(info_panel)

def print_input_prompt(message: str) -> str:
    """打印输入提示（美化的）"""
    # 使用标准输入以避免退格键问题
    text = Text()
    text.append(f"{Icons.GEAR} ", style=f"bold {Colors.ACCENT}")
    text.append(message, style=Colors.TEXT)
    text.append(": ", style=Colors.ACCENT)
    
    # 打印提示符但不换行
    console.print(text, end="")
    
    # 使用标准 input 函数获取输入
    try:
        return input().strip()
    except EOFError:
        return ""
    except KeyboardInterrupt:
        # 重新抛出中断异常，让程序退出
        print()  # 换行
        raise

def input_api_key(prompt: str) -> str:
    """安全地输入 API 密钥（不回显密钥内容）"""
    import getpass
    text = Text()
    text.append(f"{Icons.GEAR} ", style="bold yellow")
    text.append(prompt, style="bold white")
    # 不添加冒号，让 getpass 自动处理
    
    # 打印提示符但不换行
    console.print(text, end="")
    
    # 使用 getpass 获取密码
    try:
        return getpass.getpass("")
    except EOFError:
        return ""
    except KeyboardInterrupt:
        # 重新抛出中断异常，让程序退出
        print()  # 换行
        raise

def create_provider_menu(providers: dict) -> str:
    """创建 AI 供应商选择菜单"""
    console.print("🤖", style="bold bright_cyan", end="")
    console.print(" AI 供应商选择", style="bold white")
    console.print()

    for key, provider in providers.items():
        console.print(f"  {key}. {provider['name']}", style="bold white")

    # 使用 Text 对象来创建提示符（修复重复冒号）
    prompt_text = Text()
    prompt_text.append("⚙️ ", style="bold yellow")
    prompt_text.append("请选择供应商 [1-", style="bold white")
    prompt_text.append(f"{len(providers)}", style="bold cyan")
    prompt_text.append("]", style="bold yellow")
    return Prompt.ask(prompt_text, choices=list(providers.keys()))

def print_statistics(total: int, success: int, failed: int, duration: float):
    """打印统计信息"""
    # 统计数据
    success_rate = (success / total * 100) if total > 0 else 0
    failed_rate = (failed / total * 100) if total > 0 else 0
    avg_time = duration / total if total > 0 else 0
    
    # 统计信息内容
    stats_text = Text()
    stats_text.append("📈 数量统计\n", style="bold yellow")
    stats_text.append(f"  • 总处理数量: {total}\n", style="white")
    stats_text.append(f"  • 成功数量: {success} ({success_rate:.1f}%)\n", style="bold green")
    stats_text.append(f"  • 失败数量: {failed} ({failed_rate:.1f}%)\n\n", style="bold red")
    
    stats_text.append("⏱️  时间统计\n", style="bold yellow")
    stats_text.append(f"  • 总用时长: {duration:.2f} 秒\n", style="white")
    stats_text.append(f"  • 平均用时: {avg_time:.2f} 秒/问题\n", style="white")
    stats_text.append(f"  • 处理速度: {total/duration:.1f} 问题/秒" if duration > 0 else "  • 处理速度: 0", style="white")
    
    # 统计面板
    stats_panel = Panel(
        stats_text,
        title="[bold]📊 批量询问统计[/bold]",
        border_style="bright_magenta",
        box=box.DOUBLE,
        padding=(1, 2)
    )
    console.print(stats_panel)
    console.print()

def print_welcome():
    """打印欢迎信息 - 简洁版"""
    console.print()
    
    # 简洁标题
    title = Text()
    title.append("🤖 ", style="bright_cyan")
    title.append("dify_chat_tester", style="bold bright_cyan")
    title.append(" - AI聊天测试工具", style="bright_white")
    
    # 居中显示标题
    console.print(title, justify="center")
    console.print()
    
    # 简单分隔线
    console.print("─" * 50, style="dim")
    console.print()

def print_api_key_confirmation(hidden_key: str) -> bool:
    """打印 API 密钥确认"""
    key_text = Text()
    key_text.append("🔑 已输入密钥:\n", style="bold green")
    key_text.append(f"  {hidden_key}", style="bold cyan")
    
    key_panel = Panel(
        key_text,
        title="[bold]🔐 API 密钥确认[/bold]",
        border_style="green",
        box=box.ROUNDED,
        padding=(1, 2)
    )
    console.print(key_panel)
    return Confirm.ask("[bold]是否正确？[/bold]", default=True)

def print_file_list(files: list):
    """打印文件列表"""
    if not files:
        warning_text = Text()
        warning_text.append("⚠️ 当前目录没有找到 Excel 文件", style="bold orange_red1")
        warning_panel = Panel(
            warning_text,
            title="[bold]📁 文件列表[/bold]",
            border_style="orange_red1",
            box=box.ROUNDED,
            padding=(1, 2)
        )
        console.print(warning_panel)
        return

    # 表格内容
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("序号", style="cyan", justify="center", width=8)
    table.add_column("文件名", style="white")

    for i, file_name in enumerate(files, 1):
        table.add_row(f"[{i}]", file_name)
    
    file_panel = Panel(
        table,
        title="[bold]📁 当前目录下的 Excel 文件[/bold]",
        border_style="bright_cyan",
        box=box.ROUNDED,
        padding=(1, 2)
    )
    console.print(file_panel)
    console.print()

def print_column_list(columns: list):
    """打印列名列表"""
    # 表格内容
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("序号", style="cyan", justify="center", width=8)
    table.add_column("列名", style="white")

    for i, col_name in enumerate(columns, 1):
        table.add_row(f"[{i}]", str(col_name))
    
    column_panel = Panel(
        table,
        title="[bold]📋 Excel 文件中的列名[/bold]",
        border_style="bright_green",
        box=box.ROUNDED,
        padding=(1, 2)
    )
    console.print(column_panel)
    console.print()

def select_column_by_index(columns: list, prompt_msg: str) -> int:
    """让用户通过序号选择列"""
    print_column_list(columns)
    while True:
        try:
            choice = print_input_prompt(prompt_msg)
            col_index = int(choice) - 1
            if 0 <= col_index < len(columns):
                selected_col = columns[col_index]
                print_success(f"已选择列: {selected_col}")
                return col_index
            else:
                print_error(f"无效的序号！请输入 1-{len(columns)} 之间的数字。")
        except ValueError:
            print_error("请输入有效的数字！")
        except KeyboardInterrupt:
            print_warning("用户取消操作，程序退出。")
            sys.exit(0)