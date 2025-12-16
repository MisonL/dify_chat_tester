import importlib
import os
import pkgutil
from typing import Dict, List, Type

from dify_chat_tester.providers.base import AIProvider
from dify_chat_tester.config.logging import get_logger

logger = get_logger("dify_chat_tester.plugin_manager")


class PluginManager:
    """插件管理器，负责加载和管理插件"""

    def __init__(self):
        self.providers: Dict[str, Type[AIProvider]] = {}
        self.provider_instances: Dict[str, AIProvider] = {}
        self.plugin_configs: Dict[str, dict] = {}

    def load_plugins(self, plugins_package: str = "dify_chat_tester.plugins"):
        """
        动态加载内置插件
        
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
                            logger.debug(f"正在加载内置插件: {name}")
                            module.setup(self)
                        else:
                            logger.debug(f"跳过插件 {name}: 未找到 setup(manager) 函数")
                            
                    except Exception as e:
                        logger.error(f"加载插件 {name} 失败: {e}", exc_info=True)
                        
        except ImportError:
            logger.warning(f"无法导入插件包: {plugins_package}，可能目录不存在")
        except Exception as e:
            logger.error(f"插件加载过程发生错误: {e}", exc_info=True)

    def load_external_plugins(self, external_path: str):
        """
        从外部路径加载私有插件
        
        Args:
            external_path: 外部插件目录的绝对路径
        """
        import sys
        from pathlib import Path
        
        plugins_dir = Path(external_path)
        
        if not plugins_dir.exists():
            logger.debug(f"外部插件目录不存在: {external_path}")
            return
            
        if not plugins_dir.is_dir():
            logger.warning(f"外部插件路径不是目录: {external_path}")
            return

        logger.debug(f"正在从外部路径加载插件: {external_path}")
        
        # 将父目录添加到 sys.path 以便导入
        parent_dir = str(plugins_dir.parent)
        plugins_dir_name = plugins_dir.name
        
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
            path_added = True
        else:
            path_added = False

        try:
            # 遍历外部插件目录中的子目录
            for item in plugins_dir.iterdir():
                if item.is_dir() and (item / "__init__.py").exists():
                    plugin_name = item.name
                    module_name = f"{plugins_dir_name}.{plugin_name}"
                    
                    try:
                        # 动态导入插件模块
                        module = importlib.import_module(module_name)
                        
                        # 检查是否有 setup 函数
                        if hasattr(module, "setup") and callable(module.setup):
                            logger.info(f"正在加载外部插件: {plugin_name}")
                            module.setup(self)
                        else:
                            logger.debug(f"跳过外部插件 {plugin_name}: 未找到 setup(manager) 函数")
                            
                    except Exception as e:
                        logger.error(f"加载外部插件 {plugin_name} 失败: {e}", exc_info=True)
                        
        finally:
            # 清理 sys.path（可选，保持环境干净）
            if path_added:
                try:
                    sys.path.remove(parent_dir)
                except ValueError:
                    pass

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

    # --- 增强功能: 菜单与样式定制 ---

    def register_menu_item(self, menu_id: str, item: dict):
        """
        注册自定义菜单项
        
        Args:
            menu_id: 菜单ID, 例如 "main_function", "run_mode", "role_select"
            item: 菜单项配置, 例如:
                  {
                      "id": "my_custom_action",
                      "label": "执行我的自定义动作",
                      "callback": my_function,  # 可选，用于执行动作
                      "order": 100              # 可选，排序权重
                  }
        """
        if not hasattr(self, "_menu_registry"):
            self._menu_registry = {}
            
        if menu_id not in self._menu_registry:
            self._menu_registry[menu_id] = []
            
        # 验证必要字段
        if "label" not in item:
            logger.warning(f"注册菜单项失败: 缺少 label 字段 - {item}")
            return
            
        # 自动生成 ID
        if "id" not in item:
            item["id"] = f"plugin_item_{len(self._menu_registry[menu_id]) + 1}"
            
        self._menu_registry[menu_id].append(item)
        logger.debug(f"已注册插件菜单项 [{menu_id}]: {item['label']}")

    def get_menu_items(self, menu_id: str, default_items: List[dict] = None) -> List[dict]:
        """
        获取合并后的菜单项列表
        
        Args:
            menu_id: 菜单ID
            default_items: 默认菜单项列表 [ {"id": "1", "label": "..."} ]
            
        Returns:
            List[dict]: 合并后的菜单项列表
        """
        if not hasattr(self, "_menu_registry"):
            self._menu_registry = {}
            
        items = list(default_items) if default_items else []
        
        # 获取插件注册的项目
        plugin_items = self._menu_registry.get(menu_id, [])
        if plugin_items:
            # 排序: order 小的在前 (默认放在最后)
            plugin_items_sorted = sorted(plugin_items, key=lambda x: x.get("order", 999))
            
            # 这里简单策略：追加到默认列表后面
            # 如果需要更复杂的插入逻辑（比如插入到中间），需要在 item 中指定 position
            items.extend(plugin_items_sorted)
            
        return items

    def register_style_config(self, config: dict):
        """
        注册样式配置 (用于覆盖默认样式)
        
        Args:
            config: 样式配置字典, 例如 {"prompt_color": "green", "banner_style": "minimal"}
        """
        if not hasattr(self, "_style_config"):
            self._style_config = {}
            
        self._style_config.update(config)
        logger.debug(f"已更新插件样式配置: {config}")
        
    def get_style_config(self) -> dict:
        """获取当前样式配置"""
        if not hasattr(self, "_style_config"):
            self._style_config = {}
        return self._style_config
