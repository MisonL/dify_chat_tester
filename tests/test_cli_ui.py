# Note: _format_duration is an internal function; we test it through print_statistics or direct import
from dify_chat_tester.cli.terminal import _format_duration
from dify_chat_tester.providers.base import _friendly_error_message


class TestFriendlyErrorMessageSafety:
    """测试友好错误信息转换 - 内容安全相关"""

    def test_inappropriate_content(self):
        """测试不当内容错误"""
        error_msg = "Error: Output data may contain inappropriate content"
        friendly = _friendly_error_message(error_msg)
        assert "敏感信息" in friendly
        assert "拒绝处理" in friendly

    def test_sensitive_content(self):
        """测试敏感内容错误"""
        error_msg = "Request rejected due to sensitive content policy"
        friendly = _friendly_error_message(error_msg)
        assert "敏感信息" in friendly

    def test_nsfw_content(self):
        """测试 NSFW 内容错误"""
        error_msg = "NSFW content detected"
        friendly = _friendly_error_message(error_msg)
        assert "敏感信息" in friendly


class TestDurationForamtting:
    """测试时间格式化"""

    def test_less_than_minute(self):
        """测试小于1分钟"""
        assert _format_duration(45.5) == "45.50 秒"

    def test_minutes(self):
        """测试分钟级"""
        # 2分30秒 = 150秒
        assert _format_duration(150.0) == "2 分 30 秒"

    def test_hours(self):
        """测试小时级"""
        # 1小时1分1秒 = 3661秒
        assert _format_duration(3661.0) == "1 小时 1 分 1 秒"

    def test_long_hours(self):
        """测试长小时"""
        # 10.758 小时 = 38729.52 秒
        # 38729 // 3600 = 10 小时
        # (38729 % 3600) // 60 = 2729 // 60 = 45 分
        # 2729 % 60 = 29 秒
        result = _format_duration(38729.52)
        assert "10 小时" in result
        assert "45 分" in result
