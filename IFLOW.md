# Project Context for iFlow CLI

## Project Type
这是一个基于 Python 的 AI 聊天客户端测试工具，支持多个 AI 供应商。项目采用模块化架构，使用 uv 作为包管理器，支持中文界面和国际化。

## Directory Overview
项目结构如下：
- **根目录**: 包含主程序入口、配置文件和项目元数据
- **dify_chat_tester/**: 核心模块，包含 AI 供应商实现和工具函数
- **build/**: 构建脚本和打包配置
- **dist/**: 构建输出目录（通过 PyInstaller 打包）
- **配置文件**: 使用 config.env 进行运行时配置

## Key Files and Their Purpose

### Root Directory
- **main.py**: 主程序入口点，包含 CLI 接口和核心逻辑（简洁的入口，委托给 AppController）
- **pyproject.toml**: 项目元数据、依赖和构建配置
- **uv.toml**: uv 包管理器配置，使用阿里云 PyPI 镜像
- **config.env.example**: 运行时配置模板，包含详细的配置说明
- **README.md**: 项目文档，包含使用说明和功能介绍
- **用户使用指南.md**: 详细的中文用户指南（442 行）
- **dify_chat_tester_template.xlsx**: 批量测试模式的 Excel 模板
- **CHANGELOG.md**: 版本更新日志
- **LICENSE**: MIT 许可证
- **LICENSE-CN**: 中文许可证

### dify_chat_tester/ Module
- **app_controller.py**: 应用控制器，管理主程序流程和用户交互逻辑
- **ai_providers.py**: AI 供应商抽象基类和实现（Dify、OpenAI、iFlow）（681 行）
- **chat_manager.py**: 聊天管理器，处理交互式聊天模式功能
- **batch_manager.py**: 批量管理器，处理批量询问模式
- **provider_setup.py**: 供应商设置模块，处理不同 AI 供应商的初始化配置
- **selectors.py**: 选择器模块，处理用户选择逻辑（模型、角色、模式）
- **config_loader.py**: 配置管理系统，从 config.env 加载设置
- **terminal_ui.py**: 终端 UI 工具，使用 Rich 库提供美观的 CLI 界面
- **excel_utils.py**: Excel 操作工具，提供安全写入、初始化日志、清理非法字符等功能（109 行）
- **console_background.py**: 控制台背景设置模块（已禁用）
- **windows_console.py**: Windows 控制台增强支持，提供剪贴板粘贴功能（73 行）
- **__init__.py**: 模块初始化，定义版本和作者信息

### build/ Directory
- **build_macos.sh**: macOS 平台构建脚本
- **build_windows.bat**: Windows 平台构建脚本
- **create_release_zip.py**: 创建发布压缩包的脚本

## Supported AI Providers

### 1. Dify
- 专业的 LLM 应用开发平台
- 支持私有化部署
- API 密钥格式: `app-xxxxx`
- 特性: 应用 ID 提取、重定向处理、会话管理
- 注意: 不需要选择模型，直接使用应用 ID

### 2. OpenAI 兼容接口
- 通用适配器，支持任何 OpenAI 格式的 API
- 支持自定义基础 URL
- 支持自定义模型名称
- 特性: 对话历史管理、流式响应

### 3. iFlow
- 多模型 AI 平台
- 预配置基础 URL: `https://apis.iflow.cn/v1`
- 内置模型: qwen3-max, kimi-k2-0905, glm-4.6, deepseek-v3.2
- 特性: 流式响应自动回退到非流式

## Running the Application

### Prerequisites
- Python 3.7+
- uv 包管理器（推荐）

### Installation and Setup
```bash
# 安装依赖
uv sync

# 复制配置模板
cp config.env.example config.env

# 根据需要编辑配置
# （设置 AI 供应商密钥、角色等）
```

### Running the Program
```bash
# 使用 uv 运行（推荐）
uv run python main.py

# 或先激活虚拟环境
source .venv/bin/activate  # Linux/macOS
python main.py
```

### Testing
```bash
# 运行测试（如果已实现）
uv run pytest

# 代码质量检查
uv run ruff check .

# 代码格式化
uv run black .
uv run isort .
```

### Building
```bash
# macOS 构建
./build/build_macos.sh

# Windows 构建
./build/build_windows.bat

# 创建发布包
python build/create_release_zip.py
```

## Configuration

应用程序使用 `config.env` 进行配置。关键设置包括：

### 文件配置
- `CHAT_LOG_FILE_NAME`: 对话日志文件名（建议使用 .xlsx 扩展名）

### 角色配置
- `ROLES`: 可用角色列表（多个角色用英文逗号分隔）
- 示例: `员工,门店,管理员,客服,技术专家,产品经理`
- 内置选项: 用户(user) - 快速选择用户角色

### AI 供应商配置
- `AI_PROVIDERS`: 支持的 AI 供应商（格式：序号:名称:ID，多个用分号分隔）
- 示例: `1:Dify:dify;2:OpenAI 兼容接口:openai;3:iFlow:iflow`

### 批量询问配置
- `BATCH_REQUEST_INTERVAL`: 批量请求间隔时间（秒，建议范围：0.1-5.0）
- `BATCH_DEFAULT_SHOW_RESPONSE`: 是否默认显示回答内容（true/false）

### 模型配置
- `IFLOW_MODELS`: iFlow 可用模型列表
- `OPENAI_MODELS`: OpenAI 可用模型列表

### 等待指示器配置
- `WAITING_INDICATORS`: 等待动画字符
- `WAITING_TEXT`: 等待时的提示文字
- `WAITING_DELAY`: 动画更新延迟（秒）

## Usage Patterns

### Interactive Chat Mode
- 与 AI 进行实时对话
- 支持多轮对话
- 命令: `/exit` 或 `/quit` 返回模式选择, `/new` 重置上下文
- 特性: 退出时静默返回，无额外提示

### Batch Query Mode
- 从 Excel 文件处理问题
- 实时结果写入
- 带时间戳的详细日志
- 可配置的请求间隔

## Architecture

### Application Flow
1. **Main Entry** (`main.py`): 简洁的程序入口
2. **App Controller** (`app_controller.py`): 
   - 管理主程序循环
   - 处理供应商选择、设置
   - 内层循环处理运行模式选择
3. **Mode Managers**:
   - `chat_manager.py`: 处理会话模式
   - `batch_manager.py`: 处理批量模式
4. **Support Modules**:
   - `provider_setup.py`: 供应商初始化
   - `selectors.py`: 用户选择处理
   - `terminal_ui.py`: UI 组件

### Key Features
- 带指示器的流式响应
- 批量处理的 Excel 集成
- 多供应商支持
- Rich 终端 UI 体验
- Windows 控制台增强
- 跨平台兼容性
- 模块化的代码架构

## Development Conventions

### Code Style
- 使用 ruff 进行代码检查和格式化
- 使用 black 进行代码格式化
- 使用 isort 进行导入排序
- 使用 Optional 类型提示
- 抽象基类用于扩展性
- 流式操作的线程安全

### Error Handling
- 全面的异常处理
- API 问题的优雅回退
- 用户友好的错误消息
- 用于调试的详细日志

### Security
- 输入时隐藏 API 密钥（显示前几位和后几位，中间用*替代）
- 无硬编码凭据
- 使用 getpass 进行安全密码输入
- 配置文件已添加到 .gitignore

### Internationalization
- 支持中文界面
- 详细的中文文档
- 中文错误提示
- 中文配置说明

## Common Tasks

### Adding a New AI Provider
1. 在 `ai_providers.py` 中创建新的供应商类
2. 继承 `AIProvider` 抽象基类
3. 实现必需的方法: `get_models()` 和 `send_message()`
4. 在 `provider_setup.py` 中添加设置函数
5. 在 config.env 中更新供应商配置

### Modifying UI Elements
- 编辑 `terminal_ui.py` 进行 CLI 界面更改
- 使用 Rich 库进行样式和布局
- 图标和颜色在 Icons 类中定义

### Configuration Changes
- 编辑 `config.env.example` 设置新的默认值
- 更新 `config_loader.py` 支持新的配置类型
- 重启应用程序使更改生效

### Adding New Excel Features
- 编辑 `excel_utils.py` 添加新的 Excel 操作
- 使用 `write_cell_safely()` 处理合并单元格
- 使用 `clean_excel_text()` 清理非法字符

### Building and Distribution
- 使用 `build/` 目录中的脚本进行构建
- PyInstaller 用于创建独立可执行文件
- 支持 macOS 和 Windows 平台
- 创建发布压缩包便于分发

## Documentation

### User Documentation
- **README.md**: 项目概述和快速开始指南
- **用户使用指南.md**: 详细的中文用户指南，包含安装和配置步骤
- **config.env.example**: 详细的配置说明和示例

### Developer Documentation
- **IFLOW.md**: 项目上下文和架构说明（本文件）
- **代码内文档**: 详细的代码注释和文档字符串
- **类型提示**: 全面的类型注解提高代码可维护性

## Version Information

- **当前版本**: 1.0.0
- **Python 要求**: >=3.7
- **许可证**: MIT
- **作者**: Mison
- **邮箱**: 1360962086@qq.com
- **仓库**: https://github.com/MisonL/dify_chat_tester

## Dependencies

### Runtime Dependencies
- **requests**: HTTP 请求库
- **openpyxl**: Excel 文件操作
- **colorama**: 跨平台彩色终端输出
- **rich**: 现代化终端 UI 库

### Development Dependencies
- **pytest**: 测试框架
- **black**: 代码格式化工具
- **isort**: 导入排序工具
- **pyinstaller**: 可执行文件打包工具