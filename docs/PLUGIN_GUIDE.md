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

    # 方式三：注册主菜单项（v1.4.4 新增）
    # 允许插件在主程序菜单中注册自定义功能入口
    manager.register_menu_item(
        menu_id="main_function",
        item={
            "label": "我的插件功能",
            "order": 99,  # 排序权重，越小越靠前
            "callback": run_my_feature  # 点击后执行的函数，接收 controller 实例
        }
    )

def run_my_feature(controller):
    """插件自定义功能的入口函数"""
    from dify_chat_tester.cli.terminal import console
    console.print("[green]正在运行插件自定义功能...[/green]")
    # 你的业务逻辑...
```

### 2.2 实现 AIProvider

供应商类必须继承自 `dify_chat_tester.providers.base.AIProvider` 并实现抽象方法。

```python
from dify_chat_tester.providers.base import AIProvider
from typing import List, Optional, Callable

class MyCustomProvider(AIProvider):
    def get_models(self) -> List[str]:
        return ["default-model"]

    # 可选：重写模型选择逻辑（例如跳过交互直接返回）
    def select_model(self, available_models: List[str]) -> str:
        return "default-model"

    # 可选：重写角色选择逻辑
    def select_role(self, available_roles: List[str]) -> str:
        return "user"

    def send_message(
        self,
        message: str,
        model: str,
        role: str = "员工",
        history: Optional[List[dict]] = None,      # 对话历史
        conversation_id: Optional[str] = None,     # 会话 ID
        stream: bool = True,                       # 是否流式
        show_indicator: bool = True,               # 显示等待指示器
        show_thinking: bool = True,                # 显示思考过程
        stream_callback: Optional[Callable[[str, str], None]] = None, # 流式回调
    ) -> tuple:
        """
        实现发送逻辑

        stream_callback 使用说明:
        callback("text", "文本片段")      - 普通文本回复
        callback("thinking", "思考内容")  - 思维链/推理过程
        callback("tool_call", "工具名 参数") - 工具调用通知
        callback("tool_result", "结果")    - 工具执行结果
        """

        # 示例：简单的流式实现
        if stream_callback:
            stream_callback("thinking", "正在思考...\n")
            stream_callback("text", "这是回复内容")

        return "完整回复内容", True, None, "new-conversation-id"
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
同时也支持在主菜单中自动展示版本号，例如：`我的插件功能 (v1.0.0)`。

## 9. 高级特性 (v1.4.4+)

### 9.1 动态菜单 ID

主程序会自动为插件注册的菜单项分配唯一的数字 ID，开发者无需担心 ID 冲突问题。

### 9.2 带回调的菜单项

如上文所述，通过 `register_menu_item` 并提供 `callback` 函数，插件可以完全接管控制权，实现复杂的自定义交互流程（而不仅仅是作为 AI Provider）。

## 10. 依赖管理

插件通过 `requirements.txt` 声明依赖。

### 自动同步 (Zero-Config)

项目已内置自动依赖管理功能（仅源码模式生效）。
当程序启动时，会自动扫描所有 `external_plugins` 下的 `requirements.txt`，并调用 `uv add` 自动补全缺失的依赖。

**您只需：**

1. 将插件放入 `external_plugins` 目录。
2. 直接运行主程序 (`uv run main.py`)。
3. 程序会自动检测并安装依赖，无需手动操作。

_(注：打包后的程序不支持动态安装依赖，请确保打包前环境已同步)_

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
./build/build_plugins.sh <plugin_name>  # 打包单个
./build/build_plugins.sh all            # 打包所有
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

请参考以下示例：

- **全功能示例**：`external_plugins/demo_plugin` (展示所有高级特性)
  - 注意：此插件默认不加载，需使用 `--enable-demo-plugin` 参数开启：
    ```bash
    ./dify_chat_tester --enable-demo-plugin
    ```
