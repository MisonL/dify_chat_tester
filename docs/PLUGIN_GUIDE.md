# 插件开发指南

`dify_chat_tester` 支持通过插件系统扩展 AI 供应商，无需修改核心代码。

## 1. 插件结构

所有插件应放置在 `dify_chat_tester/plugins/` 目录下。

```bash
dify_chat_tester/plugins/
├── my_plugin/           # 你的插件目录
│   ├── __init__.py      # 入口文件（主要）
│   └── provider.py      # 供应商实现代码
└── ...
```

## 2. 插件规范

每个插件必须在一个 Python 包（包含 `__init__.py` 的文件夹）中。

### 2.1 入口函数 `setup(manager)`

在 `__init__.py` 中，必须定义一个 `setup` 函数，接收 `PluginManager` 实例。

```python
from .provider import MyCustomProvider

def setup(manager):
    # 方式一：注册实例（推荐，适合需要复杂配置的场景）
    # 你可以在这里读取配置并实例化
    provider = MyCustomProvider()
    manager.register_instance("my_custom", provider, "我的自定义模型")

    # 方式二：注册类（适合无参构造的简单场景）
    # manager.register_provider("my_custom", MyCustomProvider, "我的自定义模型")
```

### 2.2 实现 AIProvider

供应商类必须继承自 `dify_chat_tester.ai_providers.AIProvider` 并实现抽象方法。

```python
from dify_chat_tester.ai_providers import AIProvider
from typing import List, Optional

class MyCustomProvider(AIProvider):
    def get_models(self) -> List[str]:
        return ["default-model"]

    def send_message(
        self,
        message: str,
        model: str,
        role: str = "员工",
        history: Optional[List[dict]] = None,
        conversation_id: Optional[str] = None,
        stream: bool = True,
        show_indicator: bool = True,
        show_thinking: bool = True,
    ) -> tuple:
        # 实现发送逻辑
        return "回复内容", True, None, None
```

## 3. 私有插件管理

对于公司内部的私有插件，`.gitignore` 已配置为忽略 `dify_chat_tester/plugins/` 下除 `__init__.py` 外的所有内容。

你可以在本地创建插件目录，它不会被提交到开源仓库。建议在内部 GitLab 仓库中维护这些插件代码，或者使用 git submodule。

## 4. 示例

请参考 `dify_chat_tester/plugins` 目录下的示例（如果有）。
