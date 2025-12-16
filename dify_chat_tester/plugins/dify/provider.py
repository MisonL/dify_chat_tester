"""Dify Provider - 引用核心模块实现"""

# 直接从核心模块导入，保持向后兼容
from dify_chat_tester.providers.base import DifyProvider

__all__ = ["DifyProvider"]
