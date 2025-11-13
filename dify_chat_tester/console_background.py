"""
Windows 控制台背景设置模块
提供控制台背景色设置功能
"""

import sys
import os

def set_console_background():
    """设置Windows控制台背景色"""
    if sys.platform == 'win32':
        try:
            # 方法1: 使用Windows Registry永久设置控制台颜色
            import winreg
            
            # 打开控制台注册表项
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r'Console',
                0,
                winreg.KEY_SET_VALUE
            )
            
            # 设置颜色表（16色）
            # 索引0-7是标准色，8-15是高亮色
            # 我们要修改背景色（索引0）为深灰色
            color_table = [
                0x00565656,  # 0: 黑色 -> 深灰色
                0x000000FF,  # 1: 蓝色
                0x0000FF00,  # 2: 绿色
                0x0000FFFF,  # 3: 青色
                0x00FF0000,  # 4: 红色
                0x00FF00FF,  # 5: 品红
                0x00FFFF00,  # 6: 黄色
                0x00FFFFFF,  # 7: 白色
                0x00808080,  # 8: 亮黑（灰）
                0x000000FF,  # 9: 亮蓝
                0x0000FF00,  # 10: 亮绿
                0x0000FFFF,  # 11: 亮青
                0x00FF0000,  # 12: 亮红
                0x00FF00FF,  # 13: 亮品红
                0x00FFFF00,  # 14: 亮黄
                0x00FFFFFF,  # 15: 亮白
            ]
            
            # 写入颜色表
            for i, color in enumerate(color_table):
                winreg.SetValueEx(key, f'ColorTable{i:02d}', 0, winreg.REG_DWORD, color)
            
            # 设置屏幕背景色和文字色
            # 属性位：背景色(高4位) + 前景色(低4位)
            # 背景色=0(深灰), 前景色=7(白色) -> 0x07
            winreg.SetValueEx(key, 'ScreenColors', 0, winreg.REG_DWORD, 0x07)
            
            winreg.CloseKey(key)
            
            # 清屏以应用新颜色
            os.system('cls')
            
        except Exception:
            # 如果注册表方法失败，使用PowerShell
            try:
                # 使用PowerShell设置当前窗口的背景色
                os.system('powershell -Command "$Host.UI.RawUI.BackgroundColor = 'Black'; Clear-Host"')
            except:
                # 最后的备用方案：使用ANSI转义序列
                print('\033[40m\033[37m', end='')  # 黑底白字
                os.system('cls')