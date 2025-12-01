"""Pytest 配置：将项目根目录加入 sys.path。

这样在未安装包的情况下也可以直接 `import dify_chat_tester`。
"""

import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
