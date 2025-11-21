#!/usr/bin/env python3
"""
AI 聊天客户端测试工具 - 主程序入口

作者：Mison
邮箱：1360962086@qq.com
仓库：https://github.com/MisonL/dify_chat_tester
许可证：MIT
"""

import sys
from dify_chat_tester.app_controller import AppController

def main():
    """主程序入口"""
    try:
        app = AppController()
        app.run()
    except KeyboardInterrupt:
        print("\n\n程序已退出。")
        sys.exit(0)
    except Exception as e:
        print(f"\n程序发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()