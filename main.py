#!/usr/bin/env python3
"""
dify_chat_tester - AI聊天测试工具
支持多个AI供应商的聊天客户端，包括Dify、OpenAI兼容接口和iFlow
"""

import sys
from dify_chat_tester.app_controller import AppController
from dify_chat_tester.terminal_ui import print_error, print_info


def main():
    """主程序入口"""
    try:
        # 创建应用控制器并运行
        controller = AppController()
        controller.run()
    except KeyboardInterrupt:
        print()
        print_info("用户中断操作，程序退出。")
        sys.exit(0)
    except Exception as e:
        print_error(f"程序发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()