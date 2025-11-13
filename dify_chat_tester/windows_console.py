"""
Windows 控制台支持模块
提供剪贴板粘贴和键盘输入增强功能
"""

import sys
import os

# Windows 平台特定设置
if sys.platform == 'win32':
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
                ENABLE_PROCESSED_INPUT = 0x0001
                ENABLE_LINE_INPUT = 0x0002
                ENABLE_ECHO_INPUT = 0x0004
                
                # 获取当前模式
                mode = wintypes.DWORD()
                if kernel32.GetConsoleMode(hStdin, ctypes.byref(mode)):
                    # 启用快速编辑模式（允许鼠标选择和粘贴）
                    new_mode = mode.value | ENABLE_QUICK_EDIT_MODE | ENABLE_EXTENDED_FLAGS
                    kernel32.SetConsoleMode(hStdin, new_mode)
                    return True
            return False
        
        # 在导入时自动启用
        enable_console_paste()
        
    except Exception:
        # 如果设置失败，静默忽略
        pass