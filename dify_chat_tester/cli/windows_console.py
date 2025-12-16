"""
Windows 控制台增强支持模块
提供剪贴板粘贴和键盘输入增强功能
"""

import sys

# Windows 平台特定设置
if sys.platform == "win32":
    try:
        import ctypes
        from ctypes import wintypes

        def enable_console_paste():
            """启用Windows控制台的快速编辑模式，支持鼠标粘贴"""
            # 启用控制台模式
            kernel32 = ctypes.windll.kernel32

            # 获取标准输入句柄
            STD_INPUT_HANDLE = -10
            hStdin = kernel32.GetStdHandle(STD_INPUT_HANDLE)

            if hStdin and hStdin != -1:
                # 设置控制台模式以支持快速编辑和粘贴
                ENABLE_QUICK_EDIT_MODE = 0x0040
                ENABLE_EXTENDED_FLAGS = 0x0080
                ENABLE_LINE_INPUT = 0x0002
                ENABLE_VIRTUAL_TERMINAL_INPUT = 0x0200

                # 获取当前模式
                mode = wintypes.DWORD()
                if kernel32.GetConsoleMode(hStdin, ctypes.byref(mode)):
                    # 启用快速编辑模式（允许鼠标选择和粘贴）
                    # 同时保留必要的输入模式
                    new_mode = (
                        mode.value
                        | ENABLE_QUICK_EDIT_MODE
                        | ENABLE_EXTENDED_FLAGS
                        | ENABLE_VIRTUAL_TERMINAL_INPUT
                    )
                    # 移除可能干扰粘贴的标志
                    new_mode &= ~ENABLE_LINE_INPUT

                    if kernel32.SetConsoleMode(hStdin, new_mode):
                        # 尝试启用虚拟终端处理
                        hStdout = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
                        if hStdout and hStdout != -1:
                            out_mode = wintypes.DWORD()
                            if kernel32.GetConsoleMode(hStdout, ctypes.byref(out_mode)):
                                new_out_mode = (
                                    out_mode.value | 0x0004
                                )  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
                                kernel32.SetConsoleMode(hStdout, new_out_mode)
                        return True
            return False

        # 在导入时自动启用
        result = enable_console_paste()
        if not result:
            # 如果失败，尝试备用方法
            try:
                import subprocess

                subprocess.run(
                    ["cmd", "/c", "echo off"], shell=True, capture_output=True
                )
            except Exception:
                pass

    except Exception:
        # 如果设置失败，静默忽略
        pass
