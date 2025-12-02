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

from dify_chat_tester.app_controller import AppController


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
    return parser.parse_args(argv)


def main():
    """主程序入口"""
    args = parse_args(sys.argv[1:])

    try:
        app = AppController()
        if args.mode == "question-generation":
            app.run_question_generation_cli(folder_path=args.folder)
        else:
            app.run()
        print("\n\n程序已退出。")
        sys.exit(0)
    except Exception as e:
        print(f"\n程序发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
