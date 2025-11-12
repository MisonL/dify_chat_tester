<div align="center">
  <h1 style="font-size: 2.5em;">🚀 AI 聊天客户端测试工具</h1>
  <p style="font-size: 1.2em; color: #666;">支持 Dify、OpenAI 兼容接口、iFlow 的多 AI 供应商测试工具</p>
</div>

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?logo=python" alt="Python版本">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="许可证">
</div>

## 📖 简介

这是一个用于测试多种 AI 聊天客户端的 Python 工具，支持**实时会话模式**和**Excel批量询问模式**。它能够帮助用户方便地与不同 AI 供应商进行交互，并记录详细的对话或查询日志。

### 🌟 支持的 AI 供应商

| 供应商 | 说明 | 特点 |
|--------|------|------|
| **Dify** | 专业的 LLM 应用开发平台 | 强大的应用开发能力，支持私有化部署 |
| **OpenAI 兼容接口** | 适配任何 OpenAI 格式的 API | 通用性强，支持多种 OpenAI 格式服务 |
| **iFlow** | 集成多种模型的 AI 平台 | 内置 qwen3-max、kimi-k2-0905、glm-4.6、deepseek-v3.2 等模型 |

## ✨ 核心特性

### 🗣️ 双模式操作
- **会话模式**：进行实时多轮对话，支持上下文维护和重置
- **批量询问模式**：从 Excel 文件读取问题，批量发送到 AI 供应商，并将结果实时写入 Excel

### 🌍 多 AI 供应商支持
- **Dify**：专业的 LLM 应用开发平台，支持私有化部署
- **OpenAI 兼容接口**：通用性强，适配任何 OpenAI 格式的服务
- **iFlow**：集成多种主流模型，简化配置流程

### ⚙️ 智能配置
- **Dify**：支持输入基础 URL 或应用 URL，自动提取应用 ID
- **OpenAI 兼容**：支持自定义基础 URL，灵活配置
- **iFlow**：预设基础 URL，简化配置流程
- 统一的 API 密钥校验和角色选择功能

### 📊 完善日志
- **会话模式**：生成 `chat_log.xlsx` 记录详细对话信息
- **批量模式**：生成时间戳命名的日志文件，包含完整操作记录
- 原始 Excel 文件实时更新，防止数据丢失

### 🧩 用户友好设计
- 命令行交互界面
- 请求状态实时指示器
- Excel 合并单元格安全处理
- 批量模式支持列选择与新增列

## 🔑 配置说明

### Dify 配置
1. **登录控制台**：[https://cloud.dify.ai/](https://cloud.dify.ai/)
2. **选择或创建应用**
3. **进入应用设置** → **API 密钥** 部分
4. **创建/查看 API 密钥**
5. **应用 ID** 获取方式：
   - 应用概览页 URL：`https://cloud.dify.ai/app/{应用ID}/configuration`
   - 应用设置页面直接查看

### OpenAI 兼容接口配置
1. **基础 URL**：输入兼容 OpenAI Chat Completions API 的服务地址
   - 例如：`https://api.openai.com/v1`
   - 或私有化部署地址
2. **API 密钥**：从对应服务获取

### iFlow 配置
1. **API 密钥**：[从 iFlow 平台获取](https://platform.iflow.cn/profile?tab=apiKey)
2. **模型选择**：可选择 qwen3-max、kimi-k2-0905、glm-4.6、deepseek-v3.2

### 📁 配置文件

程序支持通过 `config.env` 文件进行统一配置管理：

1. **复制模板文件**：
   ```bash
   cp config.env.example config.env
   ```

2. **编辑配置文件**：
   - 角色列表：`ROLES=员工,门店,管理员`
   - 批量处理速度：`BATCH_REQUEST_INTERVAL=1.0`
   - 模型列表：`IFLOW_MODELS=qwen3-max,kimi-k2-0905`
   - 等待动画：`WAITING_INDICATORS=⣾,⣽,⣻,⢿`

3. **保存并重启程序**生效

**详细配置说明**：[查看配置说明文档](配置说明.md)

## ⬇️ 安装

### 使用 uv（推荐）

[uv](https://github.com/astral-sh/uv) 是现代化的 Python 包管理工具，比 pip 更快更高效。

```bash
# 安装 uv（如果尚未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 初始化项目（自动创建虚拟环境并安装依赖）
uv venv
uv add requests openpyxl

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows
```

### 使用 pip（备选）

```bash
# 安装依赖
pip install requests openpyxl
```

## 🚦 使用指南

### 启动程序

**使用 uv（推荐）**：
```bash
# 无需激活虚拟环境，直接运行
uv run python main.py
```

**使用虚拟环境**：
```bash
# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows

# 然后运行程序
python main.py
```

### 配置步骤
1. **选择 AI 供应商**（1-3）
   - Dify：专业的 LLM 应用开发平台
   - OpenAI 兼容接口：适配任何 OpenAI 格式的 API
   - iFlow：集成多种模型的 AI 平台

2. **根据供应商配置**
   - **Dify**：输入基础 URL/应用 URL、API 密钥、应用 ID
   - **OpenAI 兼容**：输入基础 URL、API 密钥
   - **iFlow**：输入 API 密钥

3. **选择模型**
   - **Dify**: 自动选择
   - **OpenAI 兼容**: 可选择预设模型或输入自定义模型名称（如 `gpt-4o`、`deepseek-r1` 等）
   - **iFlow**: 从预设模型中选择（`qwen3-max`、`kimi-k2-0905`、`glm-4.6`、`deepseek-v3.2`）

4. **选择对话角色**

5. **选择模式**
   - 会话模式：实时对话
   - 批量模式：Excel 批量处理

### 模式选择
| 模式 | 命令 | 功能 |
|------|------|------|
| **会话模式** (输入 `1`) | `exit` | 退出程序 |
|  | `/new` | 重置对话上下文 |
| **批量模式** (输入 `2`) | - | 处理 Excel 文件 |

### 批量模式流程
1. 选择 Excel 文件（自动列出当前目录）
2. 指定问题所在列（名称或序号）
3. 设置结果保存列（支持新增列）
4. 配置显示选项（是否显示回答内容）
5. 设置请求间隔时间（建议 ≥0.1秒）
6. 开始处理并查看统计报告

## 📝 日志说明

### 会话模式
- **文件**: `chat_log.xlsx`
- **内容**: 时间戳、角色、用户输入、AI供应商响应、状态、错误信息、对话轮次、对话ID

### 批量模式
- **详细日志**: `batch_query_log_YYYYMMDD_HHMMSS.xlsx`
- **原始文件**: 结果直接写入用户选择的列
- **内容**: 时间戳、角色、原始问题、AI供应商响应、状态、错误信息、对话ID

## ⚠️ 注意事项

1. **API 要求**
   - 确保 AI 供应商 API 支持流式响应
   - Dify API 密钥必须以 `app-` 开头
   - 其他供应商按各自要求配置

2. **兼容性说明**
   - **OpenAI 兼容接口**: 支持标准的 OpenAI Chat Completions API 格式
   - **MiniMax 兼容**: 如果你的 base URL 包含 `/v1`（如 `https://api.minimaxi.com/v1`），程序会自动适配正确的 API 路径
   - **自定义模型**: OpenAI 兼容接口支持输入任意模型名称，无需修改配置文件

3. **API 密钥安全**
   - 程序使用安全的密码输入方式，输入时不会显示密钥内容
   - 确认输入时仅显示密钥前4位和后4位，中间用星号保护
   - 例如：`sk-1234****89abcdef`
   - 密钥仅在内存中临时存储，不会写入日志或任何文件

3. **配置管理**
   - 所有可配置参数都在 `config.env` 文件中
   - 复制 `config.env.example` 为 `config.env` 即可开始配置
   - 配置文件已添加到 `.gitignore`，不会提交到代码仓库
   - 支持动态角色：在程序运行时可直接输入自定义角色名称

3. **批量模式**
   - 确保 Excel 格式正确
   - 问题列内容不能为空
   - 程序自动跳过空问题
   - 实时保存防止数据丢失

4. **用户体验**
   - 请求时显示等待指示器
   - 收到响应或错误时自动停止
   - 安全处理 Excel 合并单元格
   - 根据不同供应商显示不同的响应标识

5. **故障排除**
   - **iFlow 响应为空**：程序已修复 iFlow 的流式响应处理逻辑，并添加了非流式回退机制。如果仍有问题，程序会自动显示调试信息。
   - **API 错误**：检查 API 密钥是否有效，权限是否足够
   - **网络问题**：检查网络连接，确保能够访问对应服务

## 🔧 更新日志

### v2.1.0 (2025-11-10)
- ✨ **使用 uv 管理依赖** - 更快的包管理器和更简洁的项目结构
- ✨ 添加 `pyproject.toml` 配置文件
- 🔒 **增强 API 密钥安全性** - 输入时不显示密钥，确认时仅显示前4位和后4位
- 🧠 **支持自定义模型** - OpenAI 兼容接口支持用户输入任意模型名称
- 🔧 主程序重命名为 `main.py` - 更简洁的入口文件
- 📝 更新 README 文档，推荐使用 uv

### v2.0.0 (2025-11-07)
- ✨ 新增多 AI 供应商支持（Dify、OpenAI 兼容接口、iFlow）
- ✨ 添加了模型选择功能
- 🔧 修复了 iFlow 响应内容为空的问题
- 📝 更新了文档和使用说明
- 🎨 改进了用户交互流程

## 📜 许可证

- **许可证类型**: [MIT 许可证](LICENSE)
- **中文版本**: [查看中文版许可证](LICENSE-CN)

## 👤 作者

- **姓名**: Mison
- **邮箱**: 1360962086@qq.com
- **GitHub**: [MisonL](https://github.com/MisonL)