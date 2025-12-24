import threading
import time
from typing import Callable, List, Optional

from dify_chat_tester.providers.base import AIProvider


class DemoProvider(AIProvider):
    """示例供应商实现
    
    模拟各种复杂的 AI 交互场景，用于测试和演示。
    """

    def get_models(self) -> List[str]:
        return ["demo-fast", "demo-slow", "demo-reasoning", "demo-tools"]

    def select_model(self, available_models: List[str]) -> str:
        """【可选】 自动选择默认模型，跳过用户交互"""
        return "demo-reasoning"

    def select_role(self, available_roles: List[str]) -> str:
        """【可选】 自动选择默认角色，跳过用户交互"""
        return "help-desk"

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
        stream_callback: Optional[Callable[[str, str], None]] = None,
    ) -> tuple:
        """处理消息发送"""
        
        full_response = ""
        
        # 模拟不同模型的行为
        if model == "demo-reasoning":
            full_response = self._handle_reasoning_flow(message, stream, show_thinking, stream_callback)
        elif model == "demo-tools":
            full_response = self._handle_tool_flow(message, stream, stream_callback)
        else:
            full_response = f"收到消息: {message}\n当前模型: {model}\n当前角色: {role}"
            if stream and stream_callback:
                for char in full_response:
                    time.sleep(0.02)
                    stream_callback("text", full_response[:full_response.index(char)+1])

        return full_response, True, None, "demo-session-id"

    def _handle_reasoning_flow(self, message, stream, show_thinking, callback):
        """模拟带思考过程的响应"""
        response_text = "根据刚才的分析，答案是 42。"
        
        if stream and callback:
            # 1. 发送思考过程
            if show_thinking:
                thoughts = ["正在分析用户意图...", "检索知识库...", "验证数据准确性...", "生成最终回复..."]
                for thought in thoughts:
                    time.sleep(0.5)
                    callback("thinking", f"🤔 {thought}\n")
            
            # 2. 发送正文
            current_text = ""
            for char in response_text:
                time.sleep(0.05)
                current_text += char
                callback("text", current_text)
                
        return response_text

    def _handle_tool_flow(self, message, stream, callback):
        """模拟工具调用的响应"""
        response_text = "已为您查询到今日天气为晴朗，气温 25℃。"
        
        if stream and callback:
            # 1. 模拟工具调用开始
            time.sleep(0.5)
            callback("tool_call", "weather_api --city=Shenzhen")
            
            # 2. 模拟运行耗时
            time.sleep(1.5)
            
            # 3. 模拟工具返回结果
            callback("tool_result", "Status: 200 OK, Data: {temp: 25, condition: sunny}")
            
            # 4. 生成回复
            current_text = ""
            for char in response_text:
                time.sleep(0.05)
                current_text += char
                callback("text", current_text)
                
        return response_text
