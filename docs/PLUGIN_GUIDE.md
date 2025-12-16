# 插件开发指南

`dify_chat_tester` 支持通过插件系统扩展 AI 供应商，无需修改核心代码。

## 1. 插件结构

所有插件应放置在 `dify_chat_tester/plugins/` 目录下。

```bash
dify_chat_tester/plugins/
├── my_plugin/           # 你的插件目录
│   ├── __init__.py      # 入口文件（主要）
│   ├── provider.py      # 供应商实现代码
│   └── requirements.txt # 可选，第三方依赖
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

```python
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
```

## 3. 加载外部插件

### 3.1 文件夹形式

将插件放在 `external_plugins/` 目录下：

```bash
external_plugins/
└── my_custom_plugin/
    ├── __init__.py
    └── provider.py
```

### 3.2 ZIP 压缩包形式

程序支持直接加载 `.zip` 格式的插件包：

```bash
external_plugins/
└── my_plugin_v1.0.0.zip
```

程序启动时会自动解压并加载。

在 `.env.config` 中配置路径：

```ini
EXTERNAL_PLUGINS_PATH=/path/to/external_plugins
```

## 4. 版本管理

在 `__init__.py` 中定义版本号，程序加载时会显示：

```python
"""我的插件"""

__version__ = "1.0.0"

def setup(manager):
    ...
```

运行时显示：`正在加载外部插件: my_plugin v1.0.0`

## 5. 第三方依赖管理

如果插件依赖第三方库，请在插件目录下创建 `requirements.txt`：

```txt
some-package>=1.0.0
another-package
```

程序加载时会自动检测：

- **源码模式**：询问是否使用 `uv` 自动安装
- **打包模式**：提示用户手动安装

## 6. 插件打包

使用打包脚本生成可分发的插件包：

```bash
./build/build_plugin.sh <plugin_name>  # 打包单个
./build/build_plugin.sh all            # 打包所有
```

## 7. 发布插件

使用发布脚本创建 Release 并推送通知：

```bash
./build/publish_plugin.sh <plugin_name>  # 发布单个
./build/publish_plugin.sh all            # 发布所有

# 可选参数
--skip-release    # 跳过 GitLab Release
--skip-wechat     # 跳过企微通知
```

## 8. 示例

## 8. 示例

请参考 `external_plugins` 目录下的示例插件。
