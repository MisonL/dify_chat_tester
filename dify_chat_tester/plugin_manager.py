import importlib
import os
import pkgutil
from typing import Dict, List, Type

from dify_chat_tester.ai_providers import AIProvider
from dify_chat_tester.logging_utils import get_logger

logger = get_logger("dify_chat_tester.plugin_manager")


class PluginManager:
    """插件管理器，负责加载和管理插件"""

    def __init__(self):
        self.providers: Dict[str, Type[AIProvider]] = {}
        self.provider_instances: Dict[str, AIProvider] = {}
        self.plugin_configs: Dict[str, dict] = {}

    def load_plugins(self, plugins_package: str = "dify_chat_tester.plugins"):
        """
        动态加载插件
        
        Args:
            plugins_package: 插件包的导入路径
        """
        try:
            # 导入插件包
            package = importlib.import_module(plugins_package)
            
            # 获取包的路径
            if not hasattr(package, "__path__"):
                logger.warning(f"插件包 {plugins_package} 没有 __path__ 属性，无法扫描子模块")
                return

            # 遍历包下的所有模块（子目录）
            for _, name, is_pkg in pkgutil.iter_modules(package.__path__):
                if is_pkg:  # 只加载子目录（包）类型的插件
                    full_name = f"{plugins_package}.{name}"
                    try:
                        module = importlib.import_module(full_name)
                        
                        # 检查是否有 setup 函数
                        if hasattr(module, "setup") and callable(module.setup):
                            logger.info(f"正在加载插件: {name}")
                            module.setup(self)
                        else:
                            logger.debug(f"跳过插件 {name}: 未找到 setup(manager) 函数")
                            
                    except Exception as e:
                        logger.error(f"加载插件 {name} 失败: {e}", exc_info=True)
                        
        except ImportError:
            logger.warning(f"无法导入插件包: {plugins_package}，可能目录不存在")
        except Exception as e:
            logger.error(f"插件加载过程发生错误: {e}", exc_info=True)

    def register_provider(self, provider_id: str, provider_cls: Type[AIProvider], name: str = None):
        """
        注册 AI 供应商类
        
        Args:
            provider_id: 供应商唯一ID
            provider_cls: 供应商类
            name: 供应商显示名称
        """
        if not issubclass(provider_cls, AIProvider):
            logger.error(f"注册失败: {provider_cls} 未继承 AIProvider")
            return

        self.providers[provider_id] = provider_cls
        self.plugin_configs[provider_id] = {
            "name": name or provider_id,
            "type": "class",
            "class": provider_cls
        }
        logger.info(f"已注册插件供应商类: {provider_id} ({name})")

    def register_instance(self, provider_id: str, instance: AIProvider, name: str = None):
        """
        注册 AI 供应商实例
        
        Args:
            provider_id: 供应商唯一ID
            instance: 供应商实例
            name: 供应商显示名称
        """
        if not isinstance(instance, AIProvider):
            logger.error(f"注册失败: {instance} 不是 AIProvider 的实例")
            return

        self.provider_instances[provider_id] = instance
        self.plugin_configs[provider_id] = {
            "name": name or provider_id,
            "type": "instance",
            "instance": instance
        }
        logger.info(f"已注册插件供应商实例: {provider_id} ({name})")

    def get_provider_class(self, provider_id: str) -> Type[AIProvider]:
        """获取指定ID的供应商类"""
        return self.providers.get(provider_id)
