# 全功能示例插件 (Demo Plugin)

这是一个展示 `dify_chat_tester` 插件系统所有能力的示例插件。

## 功能特性

- **自动配置**: 演示 `select_model` 和 `select_role` 钩子，实现零配置启动。
- **多模型模拟**: 提供 `demo-reasoning` (思维链) 和 `demo-tools` (工具调用) 等模拟模型。
- **流式交互**: 完整支持流式文本输出。
- **高级 UI**: 演示如何触发思维链 (Reasoning) 显示和工具调用 (Tool Calls) 状态栏。

## 使用方法

1. 将本目录 `demo_plugin` 复制到 `external_plugins/` 目录中。
   ```bash
   cp -r examples/demo_plugin external_plugins/
   ```
2. 运行主程序，即可在供应商列表中看到 "Dify 示例全功能插件"。

## 模拟场景

- 选择 **demo-reasoning** 模型：你可以看到 AI 的思考过程（Thinking）。
- 选择 **demo-tools** 模型：你可以看到 AI 调用天气 API 的模拟动画和结果。
