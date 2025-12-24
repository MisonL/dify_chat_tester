"""全功能示例插件

展示插件系统的所有能力：
1. 自定义模型/角色选择钩子
2. 流式响应 (Text/Reasoning)
3. 工具调用状态展示
4. 模拟耗时任务与中断处理
"""

__version__ = "1.0.0"

from .provider import DemoProvider


def setup(manager):
    # 注册插件实例
    # 参数: (provider_id, provider_instance, display_name)
    manager.register_instance("demo_plugin", DemoProvider(), "Dify 示例全功能插件")
