#!/usr/bin/env python3
"""
AI 聊天客户端测试工具 - 主程序入口

作者：Mison
邮箱：1360962086@qq.com
仓库：https://github.com/MisonL/dify_chat_tester
许可证：MIT
"""

import argparse
import sys

from dify_chat_tester.cli.app import AppController


def parse_args(argv: list[str]) -> argparse.Namespace:
    """解析命令行参数。

    支持两种模式：
    - interactive（默认）：完整交互式体验；
    - question-generation：直接进入“AI生成测试提问点”流程，可选指定文档文件夹路径。
    """
    parser = argparse.ArgumentParser(
        prog="dify_chat_tester",
        description="AI 聊天客户端测试工具",
    )
    parser.add_argument(
        "--mode",
        choices=["interactive", "question-generation"],
        default="interactive",
        help="运行模式：interactive 或 question-generation（默认：interactive）",
    )
    parser.add_argument(
        "--folder",
        type=str,
        default=None,
        help="当 mode=question-generation 时，指定文档文件夹路径；不指定则进入交互选择。",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=None,
        help="批量处理并发数（2-10 启用并发，1 或不指定为串行模式）",
    )
    parser.add_argument(
        "--enable-demo-plugin",
        action="store_true",
        help="开启示例插件 (Demo Plugin)，用于功能演示",
    )
    return parser.parse_args(argv)


def main():
    """主程序入口"""
    args = parse_args(sys.argv[1:])

    try:
        # 初始化插件系统
        # 0. 自动检查并补充插件依赖 (仅在源码 + uv 模式下生效)
        _auto_install_dependencies()

        from dify_chat_tester.providers.setup import init_plugin_manager

        init_plugin_manager(enable_demo=args.enable_demo_plugin)

        app = AppController()
        if args.mode == "question-generation":
            app.run_question_generation_cli(folder_path=args.folder)
        else:
            app.run(concurrency=args.concurrency)
        print("\n\n程序已退出。")
        sys.exit(0)
    except KeyboardInterrupt:
        # 优雅处理 Ctrl+C
        print("\n\n⚠️  用户取消操作，程序退出")
        sys.exit(0)
    except Exception as e:
        print(f"\n程序发生错误: {e}")
        sys.exit(1)


def _auto_install_dependencies(plugins_dir=None):
    """自动扫描插件目录并安装依赖

    Args:
        plugins_dir: 插件目录路径，如果不指定则使用默认的 external_plugins 目录
    """
    import shutil
    import subprocess
    from pathlib import Path

    # 1. 检测环境: 必须有 uv 且不是打包环境
    if getattr(sys, "frozen", False):
        return

    if not shutil.which("uv"):
        return

    # 2. 扫描依赖
    if plugins_dir is None:
        project_root = Path(__file__).parent
        plugins_dir = project_root / "external_plugins"
    else:
        plugins_dir = Path(plugins_dir)

    if not plugins_dir.exists():
        return

    deps_to_add = set()
    for item in plugins_dir.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            req_file = item / "requirements.txt"
            if req_file.exists():
                try:
                    with open(req_file, "r", encoding="utf-8") as f:
                        for line in f:
                            dep = line.strip()
                            if dep and not dep.startswith("#"):
                                deps_to_add.add(dep)
                except Exception:
                    pass

    if not deps_to_add:
        return

    # 3. 检查是否需要安装
    # 策略: 每次都运行 uv add，但通过 capture_output 隐藏输出，出错才报。
    # 考虑到用户体验，我们打印一行“正在检查插件依赖...”然后运行。

    print("📦 正在检查插件依赖...", end="", flush=True)
    try:
        # 使用 check=True, 捕获输出
        subprocess.run(
            ["uv", "add"] + list(deps_to_add),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print(" ✅")
    except subprocess.CalledProcessError:
        print(" ⚠️ (自动安装失败，将尝试继续)")


if __name__ == "__main__":
    main()
