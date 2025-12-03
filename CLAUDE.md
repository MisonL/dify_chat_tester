# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 常用开发命令

### 依赖管理
```bash
# 安装依赖（推荐使用 uv）
uv sync

# 使用 pip 安装
pip install requests openpyxl colorama rich
```

### 运行程序
```bash
# 交互式模式（默认）
uv run python main.py

# 直接进入 AI 生成测试提问点功能
uv run python main.py -- --mode question-generation

# 指定文档目录
uv run python main.py -- --mode question-generation --folder ./kb-docs
```

### 代码质量检查
```bash
# 代码格式检查
uv run ruff check .

# 自动修复代码格式问题
uv run ruff check --fix .

# 代码格式化
uv run black .
uv run isort .
```

### 测试
```bash
# 运行测试
uv run pytest
```

### 构建和打包
```bash
# macOS 打包
./build/build_macos.sh

# 使用 PyInstaller 手动打包
uv run pyinstaller dify_chat_tester.spec
```

## 项目架构

### 核心模块结构
- `main.py`: 主程序入口，简洁委托给 AppController
- `dify_chat_tester/`: 核心功能模块
  - `app_controller.py`: 应用控制器，管理主程序流程
  - `chat_manager.py`: 聊天管理器，处理实时对话模式
  - `batch_manager.py`: 批量管理器，处理 Excel 批量询问
  - `question_generator.py`: 问题生成器，AI 分析文档生成测试问题
  - `ai_providers.py`: AI 供应商实现（Dify、OpenAI、iFlow）
  - `config_loader.py`: 配置管理，从 .env.config 加载设置
  - `terminal_ui.py`: 终端界面，基于 Rich 的现代化 UI
  - `excel_utils.py`: Excel 工具，处理数据读写和格式化
  - `logging_utils.py`: 日志工具，支持轮转和权限自适应
  - `selectors.py`: 选择器，处理用户交互选择
  - `provider_setup.py`: 供应商设置，配置 API 连接

### 设计模式
- **控制器模式**: AppController 统一管理应用流程
- **策略模式**: ai_providers 中不同供应商使用统一接口
- **工厂模式**: config_loader 根据配置创建相应的供应商实例
- **单例模式**: config_loader 中的配置全局共享

### 数据流
1. **配置加载**: `.env.config` → config_loader → 各模块
2. **用户交互**: terminal_ui → selectors → app_controller
3. **AI 请求**: app_controller → ai_providers → 外部 API
4. **数据处理**: excel_utils ↔ Excel 文件
5. **日志记录**: logging_utils → 文件/控制台

### 关键特性
- **多 AI 供应商支持**: 通过 ai_providers 模块统一接口
- **实时对话**: chat_manager 维护对话上下文
- **批量处理**: batch_manager 支持 Excel 批量询问
- **智能问题生成**: question_generator 分析文档自动生成测试点
- **富文本界面**: terminal_ui 使用 Rich 提供现代化体验
- **配置驱动**: 通过 .env.config 灵活配置所有参数

## 配置管理

### 主配置文件
- `.env.config.example`: 配置模板
- `.env.config`: 实际配置文件（需要自行创建）

### 关键配置项
- `AI_PROVIDERS`: 支持的 AI 供应商配置
- `ROLES`: 可用角色列表
- `BATCH_REQUEST_INTERVAL`: 批量请求间隔
- `USE_RICH_UI`: 是否使用富文本界面
- `ENABLE_THINKING`: 是否显示 AI 思维链
- `SYSTEM_PROMPT`: AI 系统提示词（支持占位符）

## 运行模式

### 1. AI 问答测试
- **会话模式**: 实时多轮对话，支持命令控制
- **批量询问模式**: 从 Excel 读取问题，批量处理并保存结果

### 2. AI 生成测试提问点
- 分析指定目录下的 Markdown 文档
- 自动生成高质量测试问题
- 导出为 Excel 文件

## 与 Semantic Tester 协同

本项目可与 semantic_tester 配合使用形成完整测试闭环：
1. 使用 dify_chat_tester 生成测试问题
2. 批量询问 AI 获取回答
3. 使用 semantic_tester 进行语义比对评估

## 开发注意事项

- 代码使用 Python 3.7+ 兼容语法
- 依赖 uv 进行包管理，也支持 pip
- 使用 Rich 库提供现代化终端界面
- 支持中英文混合显示
- 配置文件使用 UTF-8 编码
- 日志文件支持轮转和权限自适应