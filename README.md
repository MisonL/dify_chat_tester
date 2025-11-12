# AI 聊天客户端测试工具

支持多AI供应商的聊天测试工具（Dify、OpenAI、iFlow）

## 功能特性

- 支持多种AI供应商（Dify、OpenAI、iFlow）
- 实时对话模式
- 批量询问模式
- 详细日志记录
- 美观的终端界面

## 安装

```bash
uv sync
```

## 使用

```bash
uv run python main.py
```

## 配置

复制 `config.env.example` 为 `config.env` 并编辑配置。

## 支持的AI供应商

### 1. Dify
- 专业的LLM应用开发平台
- 支持私有化部署
- API密钥格式：`app-xxxxx`

### 2. OpenAI 兼容接口
- 适配任何OpenAI格式的API
- 支持自定义基础URL
- 支持自定义模型名称

### 3. iFlow
- 集成多种模型的AI平台
- 预设基础URL：`https://apis.iflow.cn/v1`
- 内置模型：qwen3-max、kimi-k2-0905、glm-4.6、deepseek-v3.2

## 运行模式

### 会话模式
- 实时多轮对话
- 支持上下文维护
- 命令：`exit` 退出，`/new` 重置对话

### 批量询问模式
- 从Excel文件读取问题
- 批量发送到AI供应商
- 实时写入结果到Excel
- 生成详细日志文件

## 日志文件

- 会话模式：`chat_log.xlsx`
- 批量模式：`batch_query_log_YYYYMMDD_HHMMSS.xlsx`

## 许可证

MIT License

## 作者

Mison <1360962086@qq.com>