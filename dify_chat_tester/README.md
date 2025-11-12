# dify_chat_tester 模块

AI供应商接口实现模块

## 模块结构

- `ai_providers.py` - AI供应商接口实现
- `config_loader.py` - 配置加载器
- `terminal_ui.py` - 终端界面美化

## AI供应商

### DifyProvider
Dify平台API接口实现

### OpenAIProvider  
OpenAI兼容接口实现

### iFlowProvider
iFlow平台API接口实现

## 配置加载器

从config.env文件加载配置参数，支持：
- 字符串、数字、布尔值
- 列表类型
- 默认值

## 终端UI

提供美化的终端界面：
- 彩色输出
- 进度指示器
- 交互式菜单
- 表格显示