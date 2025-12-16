"""
测试插件管理器模块
"""

import pytest
from unittest.mock import MagicMock, patch
import importlib
import sys


class TestPluginManager:
    """测试 PluginManager 类"""

    def test_plugin_manager_init(self):
        """测试插件管理器初始化"""
        from dify_chat_tester.providers.plugin_manager import PluginManager
        
        pm = PluginManager()
        
        assert pm.providers == {}
        assert pm.provider_instances == {}
        assert pm.plugin_configs == {}

    def test_register_instance(self):
        """测试注册供应商实例"""
        from dify_chat_tester.providers.plugin_manager import PluginManager
        from dify_chat_tester.providers.base import AIProvider
        
        pm = PluginManager()
        
        # 创建一个模拟的 AIProvider 实例
        mock_provider = MagicMock(spec=AIProvider)
        
        pm.register_instance("test_provider", mock_provider, "Test Provider")
        
        assert "test_provider" in pm.provider_instances
        assert pm.provider_instances["test_provider"] == mock_provider
        assert pm.plugin_configs["test_provider"]["name"] == "Test Provider"
        assert pm.plugin_configs["test_provider"]["type"] == "instance"

    def test_register_provider_class(self):
        """测试注册供应商类"""
        from dify_chat_tester.providers.plugin_manager import PluginManager
        from dify_chat_tester.providers.base import AIProvider, DifyProvider
        
        pm = PluginManager()
        
        pm.register_provider("dify_test", DifyProvider, "Dify Test")
        
        assert "dify_test" in pm.providers
        assert pm.providers["dify_test"] == DifyProvider
        assert pm.plugin_configs["dify_test"]["name"] == "Dify Test"
        assert pm.plugin_configs["dify_test"]["type"] == "class"

    def test_register_invalid_provider_class(self):
        """测试注册非 AIProvider 子类时失败"""
        from dify_chat_tester.providers.plugin_manager import PluginManager
        
        pm = PluginManager()
        
        # 尝试注册非 AIProvider 的类
        class NotAProvider:
            pass
        
        # 应该不会抛出异常，但不会注册成功
        pm.register_provider("invalid", NotAProvider, "Invalid")
        
        assert "invalid" not in pm.providers

    def test_get_provider_class(self):
        """测试获取供应商类"""
        from dify_chat_tester.providers.plugin_manager import PluginManager
        from dify_chat_tester.providers.base import DifyProvider
        
        pm = PluginManager()
        pm.register_provider("dify_test", DifyProvider, "Dify Test")
        
        result = pm.get_provider_class("dify_test")
        assert result == DifyProvider
        
        # 测试不存在的 ID
        result = pm.get_provider_class("nonexistent")
        assert result is None

    def test_load_plugins(self):
        """测试加载插件"""
        from dify_chat_tester.providers.plugin_manager import PluginManager
        
        pm = PluginManager()
        pm.load_plugins()
        
        # 应该加载内置插件
        assert len(pm.plugin_configs) >= 3  # dify, openai, iflow


class TestPluginIntegration:
    """集成测试：验证插件可以正确注册"""

    def test_builtin_plugins_loaded(self):
        """测试内置插件被正确加载"""
        from dify_chat_tester.providers.plugin_manager import PluginManager
        
        pm = PluginManager()
        pm.load_plugins()
        
        # 验证内置插件
        expected_plugins = ["dify", "openai", "iflow"]
        for plugin_id in expected_plugins:
            assert plugin_id in pm.plugin_configs, f"插件 {plugin_id} 未加载"


class TestPluginEnhancedFeatures:
    """测试插件增强功能（菜单、样式等）"""

    def test_menu_registration(self):
        """测试菜单项注册与获取"""
        from dify_chat_tester.providers.plugin_manager import PluginManager
        pm = PluginManager()
        
        # 1. 注册新菜单项
        pm.register_menu_item("main_function", {
            "id": "test_cmd",
            "label": "测试功能",
            "order": 10
        })
        
        # 2. 获取菜单项（无默认值）
        items = pm.get_menu_items("main_function")
        assert len(items) == 1
        assert items[0]["id"] == "test_cmd"
        
        # 3. 获取菜单项（有默认值）
        default_items = [{"id": "1", "label": "默认功能"}]
        items = pm.get_menu_items("main_function", default_items)
        assert len(items) == 2
        # 默认项在前
        assert items[0]["id"] == "1"
        assert items[1]["id"] == "test_cmd"

    def test_menu_sorting(self):
        """测试菜单项排序"""
        from dify_chat_tester.providers.plugin_manager import PluginManager
        pm = PluginManager()
        
        # 注册两个无序的项目
        pm.register_menu_item("nav", {"id": "item2", "label": "Item 2", "order": 20})
        pm.register_menu_item("nav", {"id": "item1", "label": "Item 1", "order": 10})
        
        items = pm.get_menu_items("nav")
        assert len(items) == 2
        assert items[0]["id"] == "item1"  # order 10
        assert items[1]["id"] == "item2"  # order 20

    def test_style_config(self):
        """测试样式配置注册"""
        from dify_chat_tester.providers.plugin_manager import PluginManager
        pm = PluginManager()
        
        # 初始状态为空
        assert pm.get_style_config() == {}
        
        # 注册配置
        pm.register_style_config({"color": "red"})
        assert pm.get_style_config()["color"] == "red"
        
        # 覆盖配置
        pm.register_style_config({"color": "blue", "font": "bold"})
        config = pm.get_style_config()
        assert config["color"] == "blue"
        assert config["font"] == "bold"
