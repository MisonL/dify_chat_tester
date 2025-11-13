# -*- mode: python ; coding: utf-8 -*-
"""
AI 聊天客户端测试工具 - PyInstaller 打包配置文件
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 获取项目根目录
# 使用 sys.argv[0] 获取spec文件路径，避免 __file__ 未定义错误
spec_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
# 检查spec文件是否在项目根目录下
if os.path.basename(spec_dir) == 'build':
    # spec文件在build目录下
    project_root = os.path.abspath(os.path.join(spec_dir, '..'))
else:
    # spec文件在项目根目录下
    project_root = spec_dir

# 主程序文件
main_script = os.path.join(project_root, 'main.py')

# 获取发布目录
release_dir = os.path.join(project_root, 'release_windows')

# 收集数据文件
datas = [
    # 配置文件模板
    (os.path.join(project_root, 'config.env.example'), '.'),
    
    # Excel模板文件
    (path.join(project_root, 'dify_chat_tester_template.xlsx'), '.'),
    
    # README文件（如果存在）
    (path.join(project_root, 'README.md'), '.',) if os.path.exists(path.join(project_root, 'README.md')) else None,
    
    # 用户指南（如果存在）
    (path.join(project_root, '用户使用指南.md'), '.',) if os.path.exists(path.join(project_root, '用户使用指南.md')) else None,
]

# 过滤掉 None 值
datas = [d for d in datas if d is not None]

# 收集隐藏导入
hiddenimports = [
    'dify_chat_tester.ai_providers',
    'dify_chat_tester.config_loader',
    'dify_chat_tester.terminal_ui',
    'rich.console',
    'rich.panel',
    'rich.prompt',
    'rich.table',
    'rich.text',
    'rich.progress',
    'rich.spinner',
    'rich.live',
    'rich.align',
    'rich.box',
    'rich.style',
    'rich.theme',
    'rich.color',
    'rich.ansi',
    'rich.markup',
    'rich.pretty',
    'rich.tree',
    'rich.columns',
    'rich.rule',
    'requests',
    'requests.adapters',
    'requests.auth',
    'requests.exceptions',
    'requests.models',
    'requests.sessions',
    'requests.utils',
    'openpyxl',
    'openpyxl.workbook',
    'openpyxl.worksheet',
    'openpyxl.cell',
    'openpyxl.styles',
    'openpyxl.utils',
    'colorama',
    'colorama.ansi',
    'colorama.initialise',
    'colorama.win32',
    'datetime',
    'json',
    'os',
    'sys',
    'time',
    're',
    'urllib.parse',
    'threading',
    'uuid',
]

# 收集二进制文件
binaries = []

# 排除不需要的模块
excludes = [
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'tkinter',
    'PyQt5',
    'PyQt6',
    'PySide2',
    'PySide6',
    'IPython',
    'jupyter',
    'notebook',
]

a = Analysis(
    [main_script],
    pathex=[project_root],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# 移除不需要的二进制文件（Windows特定）
for exclude in ['api-ms-win-*.dll', 'ucrtbase.dll', 'msvcp*.dll', 'vcruntime*.dll']:
    a.binaries = [x for x in a.binaries if not x[0].startswith(exclude)]

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='dify_chat_tester',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    path=release_dir,  # 直接输出到 release_windows 目录
)