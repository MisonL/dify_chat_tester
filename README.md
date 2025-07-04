<div align="center">
  <h1 style="font-size: 2.5em;">🚀 Dify 聊天客户端测试工具</h1>
</div>

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?logo=python" alt="Python版本">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="许可证">
</div>

## 📖 简介

这是一个用于测试 Dify 聊天客户端的 Python 工具，支持**实时会话模式**和**Excel批量询问模式**。它能够帮助用户方便地与 Dify 应用进行交互，并记录详细的对话或查询日志。

## ✨ 核心特性

### 🗣️ 双模式操作
- **会话模式**：进行实时多轮对话，支持上下文维护和重置
- **批量询问模式**：从 Excel 文件读取问题，批量发送到 Dify API，并将结果实时写入 Excel

### ⚙️ 智能配置
- 支持输入 Dify 基础 URL 或应用 URL，自动提取应用 ID
- API 密钥校验（必须以 `app-` 开头）
- 角色选择功能，适配不同应用场景

### 📊 完善日志
- **会话模式**：生成 `chat_log.xlsx` 记录详细对话信息
- **批量模式**：生成时间戳命名的日志文件，包含完整操作记录
- 原始 Excel 文件实时更新，防止数据丢失

### 🧩 用户友好设计
- 命令行交互界面
- 请求状态实时指示器
- Excel 合并单元格安全处理
- 批量模式支持列选择与新增列

## 🔑 获取 Dify API 密钥和应用 ID

1.  **登录控制台**：[https://cloud.dify.ai/](https://cloud.dify.ai/)
2.  **选择或创建应用**
3.  **进入应用设置** → **API 密钥** 部分
4.  **创建/查看 API 密钥**
5.  **应用 ID** 获取方式：
    - 应用概览页 URL：`https://cloud.dify.ai/app/{应用ID}/configuration`
    - 应用设置页面直接查看

## ⬇️ 安装

```bash
# 安装依赖
pip install requests openpyxl
```

## 🚦 使用指南

### 启动程序
```bash
python dify_chat_tester.py
```

### 配置步骤
1. 输入 Dify 基础 URL 或应用 URL（自动提取应用 ID）
2. 输入 Dify API 密钥（以 `app-` 开头）
3. 选择对话角色

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
- **内容**: 时间戳、角色、用户输入、Dify响应、状态、错误信息、对话轮次、对话ID

### 批量模式
- **详细日志**: `batch_query_log_YYYYMMDD_HHMMSS.xlsx`
- **原始文件**: 结果直接写入用户选择的列
- **内容**: 时间戳、角色、原始问题、响应、状态、错误信息、对话ID

## ⚠️ 注意事项

1. **API 要求**
   - 确保 Dify API 支持流式响应
   - API 密钥必须以 `app-` 开头

2. **配置扩展**
   - 角色列表可在代码中 `ROLES` 变量扩展
   - 私有化部署支持自定义 API 地址

3. **批量模式**
   - 确保 Excel 格式正确
   - 问题列内容不能为空
   - 程序自动跳过空问题
   - 实时保存防止数据丢失

4. **用户体验**
   - 请求时显示等待指示器
   - 收到响应或错误时自动停止
   - 安全处理 Excel 合并单元格

## 📜 许可证

- **许可证类型**: [MIT 许可证](LICENSE)
- **中文版本**: [查看中文版许可证](LICENSE-CN)

## 👤 作者

- **姓名**: Mison
- **邮箱**: 1360962086@qq.com
- **GitHub**: [MisonL](https://github.com/MisonL)