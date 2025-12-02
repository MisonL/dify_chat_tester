"""Terminal UI 模块的单元测试。

测试终端 UI 辅助函数，如 hide_api_key 等。
"""

from dify_chat_tester.terminal_ui import hide_api_key


class TestHideApiKey:
    """测试 hide_api_key 函数"""

    def test_hide_normal_key(self):
        """测试正常长度的密钥"""
        key = "sk-1234567890abcdef"
        result = hide_api_key(key)
        # 前4位 + 中间星号 + 后4位
        assert result == "sk-1" + "*" * (len(key) - 8) + "cdef"
        assert len(result) == len(key)

    def test_hide_short_key(self):
        """测试短密钥"""
        key = "short"
        result = hide_api_key(key)
        assert result == "*****"
        assert len(result) == len(key)

    def test_hide_long_key(self):
        """测试长密钥"""
        key = "app-very-long-api-key-here-for-testing-purposes"
        result = hide_api_key(key)
        # 应该只显示前4位和后4位
        assert result.startswith("app-")
        assert result.endswith("oses")
        assert "*" in result
        assert len(result) == len(key)

    def test_hide_empty_key(self):
        """测试空密钥"""
        key = ""
        result = hide_api_key(key)
        assert result == ""

    def test_hide_exactly_8_chars(self):
        """测试恰好8个字符的密钥"""
        key = "12345678"
        result = hide_api_key(key)
        # 8个字符或更少时，全部隐藏
        assert result == "********"
