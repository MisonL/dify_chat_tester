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

供应商类必须继承自 `dify_chat_tester.providers.base.AIProvider` 并实现抽象方法。

````python
from dify_chat_tester.providers.base import AIProvider
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

### 4.2 加载外部插件

为了避免核心代码与特定业务逻辑耦合，建议将业务插件放在独立目录中，并通过环境变量加载。

将自定义插件放在项目目录外部或单独的 `external_plugins/` 目录中：

```bash
my_project/
├── dify_chat_tester/      # 核心代码
├── external_plugins/      # 外部插件 (可独立管理)
│   └── my_custom_plugin/
│       ├── __init__.py
│       └── provider.py
└── .env.config
````

在 `.env.config` 中配置路径：

```ini
EXTERNAL_PLUGINS_PATH=/path/to/external_plugins
```

**优势**：

- ✅ 完全隔离：私有代码与开源代码无历史交叉
- ✅ 部署灵活：不同环境可配置不同的插件路径

### 方案二：内置目录（仅限本地）

对于简单场景，也可以将插件放在 `dify_chat_tester/plugins/` 目录下。

`.gitignore` 已配置为忽略除内置插件外的所有目录，因此不会被提交到开源仓库。

## 4. 示例

请参考 `dify_chat_tester/plugins/dify/` 目录下的内置插件实现。
