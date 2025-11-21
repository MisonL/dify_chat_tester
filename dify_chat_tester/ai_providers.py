"""
AI 供应商接口实现

支持多种AI供应商：
- Dify
- OpenAI 兼容接口
- iFlow

作者：Mison
邮箱：1360962086@qq.com
仓库：https://github.com/MisonL/dify_chat_tester
许可证：MIT
"""

import json
import sys
import threading
import time
from abc import ABC, abstractmethod
from typing import List, Optional

import requests

# 导入配置加载器
try:
    from dify_chat_tester.config_loader import get_config

    config = get_config()
except ImportError:
    # 如果没有配置加载器，使用默认配置
    config = None


class AIProvider(ABC):
    """AI 供应商抽象基类"""

    @abstractmethod
    def get_models(self) -> List[str]:
        """获取可用的模型列表"""
        pass

    @abstractmethod
    def send_message(
        self,
        message: str,
        model: str,
        role: str = "员工",
        history: Optional[List[dict]] = None,  # 新增：用于传递对话历史
        conversation_id: Optional[str] = None,  # 保留：用于Dify
        stream: bool = True,
        show_indicator: bool = True,
    ) -> tuple:
        """
        发送消息到 AI 供应商

        Args:
            message: 用户消息
            model: 模型名称
            role: 角色（所有供应商都支持，传递方式不同）
            conversation_id: 对话ID（用于多轮对话）
            stream: 是否使用流式响应
            show_indicator: 是否显示等待指示器

        Returns:
            tuple: (response_text, success, error_message, new_conversation_id)
        """
        pass

    # 等待指示器配置（可调整）
    # 从配置中获取，如果失败则使用默认值
    if config:
        WAITING_INDICATORS = config.get_list(
            "WAITING_INDICATORS", default=["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
        )
        WAITING_TEXT = config.get_str("WAITING_TEXT", "正在思考")
        WAITING_DELAY = config.get_float("WAITING_DELAY", 0.1)
    else:
        WAITING_INDICATORS = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
        WAITING_TEXT = "正在思考"
        WAITING_DELAY = 0.1

    def show_waiting_indicator(self, stop_event: threading.Event):
        """显示等待状态指示器"""
        indicators = self.WAITING_INDICATORS
        idx = 0
        # 使用固定长度的字符串来避免截断
        while not stop_event.is_set():
            # 构建完整的等待信息，确保长度一致
            waiting_text = f"AI: {self.WAITING_TEXT} {indicators[idx]}"
            # 添加足够的空格来覆盖之前的文本
            padding = " " * (50 - len(waiting_text))
            sys.stdout.write(f"\r{waiting_text}{padding}")
            sys.stdout.flush()
            idx = (idx + 1) % len(indicators)
            time.sleep(self.WAITING_DELAY)
        # 清除整行
        sys.stdout.write("\r" + " " * 50 + "\r")
        sys.stdout.flush()


class DifyProvider(AIProvider):
    """Dify AI 供应商实现"""

    def __init__(self, base_url: str, api_key: str, app_id: str):
        # 保留用户输入的原始 URL，让服务器自己处理重定向
        self.base_url = base_url
        self.api_key = api_key
        self.app_id = app_id

    def get_models(self) -> List[str]:
        """Dify 不支持模型列表，使用应用 ID"""
        return ["Dify App (使用应用 ID)"]

    def send_message(
        self,
        message: str,
        model: str,
        role: str = "员工",
        history: Optional[List[dict]] = None,  # 新增：匹配基类签名
        conversation_id: Optional[str] = None,
        stream: bool = True,
        show_indicator: bool = True,
    ) -> tuple:
        """发送消息到 Dify API"""
        # base_url 已经包含了完整的 API 基础路径（包括 /v1）
        # 根据 Dify 官方文档，标准端点是：{base_url}/chat-messages
        # 应用 ID 不是在 URL 中，而是通过其他方式传递
        
        # 确保 base_url 不以 / 结尾，避免双斜杠
        base_url = self.base_url.rstrip('/')
        
        # 构建标准 URL
        url = f"{base_url}/chat-messages"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "inputs": {"role": role, "app_id": self.app_id},
            "query": message,
            "response_mode": "streaming" if stream else "blocking",
            "user": "chat_tester",
        }

        if conversation_id:
            payload["conversation_id"] = conversation_id

        stop_event = threading.Event()
        waiting_thread = None
        first_char_printed = False
        new_conversation_id = None
        last_error = None # Initialize last_error here

        try:
            # 启动等待动画（如果需要）
            if show_indicator:
                waiting_thread = threading.Thread(
                    target=self.show_waiting_indicator, args=(stop_event,)
                )
                waiting_thread.daemon = True
                waiting_thread.start()

            response = requests.post(
                url,
                headers=headers,
                json=payload,
                stream=stream,
                timeout=30,
                allow_redirects=False,
            )

            # 检查是否需要重定向
            if response.status_code in [301, 302, 307, 308]:
                redirect_url = response.headers.get("Location")
                if redirect_url:
                    response = requests.post(
                        redirect_url,
                        headers=headers,
                        json=payload,
                        stream=stream,
                        timeout=30,
                        allow_redirects=False,
                    )
                else:
                    raise requests.exceptions.RequestException(
                        "重定向响应但缺少 Location 头"
                    )

            response.raise_for_status()



        except requests.exceptions.HTTPError as e:
            if show_indicator:
                stop_event.set()
                if waiting_thread is not None:
                    waiting_thread.join(timeout=0.5)
            error_msg = f"{last_error or str(e)}"
            if show_indicator:
                print(f"\r错误: {error_msg}", file=sys.stderr)
            return "", False, error_msg, None
        except Exception as e:
            if show_indicator:
                stop_event.set()
                if waiting_thread is not None:
                    waiting_thread.join(timeout=0.5)
            error_msg = f"请求错误: {str(e)}"
            if show_indicator:
                print(f"\r错误: {error_msg}", file=sys.stderr)
            return "", False, error_msg, None
        finally:
            if show_indicator:
                stop_event.set()
            if waiting_thread is not None and waiting_thread.is_alive():
                waiting_thread.join(timeout=0.5)

        if stream:
            full_response = ""
            # 使用 iter_lines 进行真正的流式处理
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    
                    # 检查是否是 HTML 响应（可能是错误页面）
                    if decoded_line.startswith("<!DOCTYPE") or decoded_line.startswith("<html"):
                        raise ValueError(
                            f"收到 HTML 响应而非 JSON: {decoded_line[:100]}"
                        )
                    
                    if decoded_line.startswith("data:"):
                        try:
                            data = json.loads(decoded_line[5:])
                            
                            # 获取事件类型
                            event = data.get("event")
                            
                            # 处理错误事件
                            if event == "error":
                                if show_indicator:
                                    stop_event.set()
                                    if waiting_thread is not None:
                                        waiting_thread.join(timeout=0.5)
                                error_msg = data.get("message", "未知错误")
                                print(f"\n错误: {error_msg}", file=sys.stderr)
                                return "", False, error_msg, None
                            
                            # 处理消息事件
                            elif event == "message":
                                if "conversation_id" in data:
                                    new_conversation_id = data["conversation_id"]

                                if "answer" in data:
                                    if show_indicator and not first_char_printed:
                                        stop_event.set()
                                        if waiting_thread is not None:
                                            waiting_thread.join(timeout=0.5)
                                        sys.stdout.write("Dify: ")
                                        sys.stdout.flush()
                                        first_char_printed = True

                                    # 实时输出内容
                                    if show_indicator:
                                        print(data["answer"], end="", flush=True)
                                    full_response += data["answer"]
                            
                            # 处理消息结束事件
                            elif event == "message_end":
                                # 消息结束，可以在这里处理元数据
                                if "conversation_id" in data:
                                    new_conversation_id = data["conversation_id"]
                                # 流式响应正常结束
                                break
                            
                            # 忽略其他事件（workflow_started, workflow_finished, ping 等）
                            
                        except json.JSONDecodeError:
                            continue
            if show_indicator:
                print()
            return full_response, True, None, new_conversation_id
        else:
            # 检查响应内容类型
            content_type = response.headers.get("content-type", "").lower()
            if "text/html" in content_type:
                # 如果返回 HTML，可能是错误页面
                html_content = response.text[:200]
                return "", False, f"收到 HTML 响应而非 JSON: {html_content}", None

            try:
                data = response.json()
            except json.JSONDecodeError:
                # 如果不是 JSON，可能是其他错误
                text_content = response.text[:200]
                return "", False, f"响应不是有效 JSON: {text_content}", None

            if show_indicator:
                stop_event.set()
                if waiting_thread is not None:
                    waiting_thread.join(timeout=0.5)

            if "conversation_id" in data:
                new_conversation_id = data["conversation_id"]

            if "answer" in data:
                if show_indicator:
                    print("Dify:", data["answer"])
                return data["answer"], True, None, new_conversation_id
            elif "error" in data:
                error_msg = data.get("error", "未知错误")
                if show_indicator:
                    print(f"错误: {error_msg}", file=sys.stderr)
                return "", False, error_msg, None
            else:
                return "", False, "未知响应格式", None


class OpenAIProvider(AIProvider):
    """OpenAI 兼容 API 供应商实现"""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

        # 从配置中获取 OpenAI 模型列表
        if config:
            self.DEFAULT_MODELS = config.get_list(
                "OPENAI_MODELS",
                default=[
                    "gpt-4o",
                    "gpt-4o-mini",
                    "gpt-4-turbo",
                    "gpt-3.5-turbo",
                    "custom-model",
                ],
            )
        else:
            self.DEFAULT_MODELS = [
                "gpt-4o",
                "gpt-4o-mini",
                "gpt-4-turbo",
                "gpt-3.5-turbo",
                "custom-model",
            ]

    def get_models(self) -> List[str]:
        """获取 OpenAI 模型列表"""
        return self.DEFAULT_MODELS.copy()

    def send_message(
        self,
        message: str,
        model: str,
        role: str = "员工",
        history: Optional[List[dict]] = None,  # 新增：用于传递对话历史
        conversation_id: Optional[str] = None,  # 保留：匹配基类签名
        stream: bool = True,
        show_indicator: bool = True,
    ) -> tuple:
        """发送消息到 OpenAI 兼容 API"""
        # 检测 k2sonnet API，它不支持非流式模式
        is_k2sonnet = "k2sonnet.com" in self.base_url
        if is_k2sonnet and not stream:
            # k2sonnet 只支持流式模式，强制使用流式
            stream = True
        
        # 处理 base_url：如果已包含 /v1 路径，只添加 /chat/completions
        if self.base_url.endswith("/v1"):
            url = f"{self.base_url}/chat/completions"
        else:
            url = f"{self.base_url}/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # 准备消息
        messages = [
            {
                "role": "system",
                "content": f"你是一个AI助手。当前角色：{role}。请以专业、友好的方式回答问题。",
            }
        ]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": message})

        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,  # 标准 OpenAI API 使用布尔值
            "temperature": 0.7,
            "max_tokens": 2000,
        }

        stop_event = threading.Event()
        waiting_thread = None
        first_char_printed = False

        try:
            if show_indicator:
                waiting_thread = threading.Thread(
                    target=self.show_waiting_indicator, args=(stop_event,)
                )
                waiting_thread.daemon = True
                waiting_thread.start()

            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    stream=stream,
                    timeout=30,
                )
                response.raise_for_status()

            except requests.exceptions.Timeout:
                if show_indicator:
                    stop_event.set()
                    if waiting_thread is not None:
                        waiting_thread.join(timeout=0.5)
                return "", False, "请求超时", conversation_id
            except requests.exceptions.ConnectionError as e:
                if show_indicator:
                    stop_event.set()
                    if waiting_thread is not None:
                        waiting_thread.join(timeout=0.5)
                return "", False, f"连接错误: {str(e)}", conversation_id
            except Exception as e:
                if show_indicator:
                    stop_event.set()
                    if waiting_thread is not None:
                        waiting_thread.join(timeout=0.5)
                return "", False, f"请求错误: {str(e)}", conversation_id

            if stream:
                full_response = ""
                stream_success = False
                
                # 首先尝试标准流式处理
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode("utf-8")
                        # OpenAI 使用 "data: " (有空格)
                        if decoded_line.startswith("data: "):
                            # 检查流式结束标记
                            if decoded_line == "data: [DONE]":
                                stream_success = True
                                break
                            try:
                                data = json.loads(decoded_line[6:])

                                if "choices" in data and len(data["choices"]) > 0:
                                    choice = data["choices"][0]
                                    
                                    # 确保 choice 是字典
                                    if not isinstance(choice, dict):
                                        continue
                                    
                                    # 检查是否结束
                                    finish_reason = choice.get("finish_reason")
                                    if finish_reason in ["stop", "length", "content_filter", "tool_calls"]:
                                        # 流式响应自然结束
                                        stream_success = True
                                        break
                                    
                                    delta = choice.get("delta", {})
                                    if not isinstance(delta, dict):
                                        continue
                                    content = delta.get("content", "")
                                    
                                    if content:
                                        stream_success = True
                                        if show_indicator and not first_char_printed:
                                            stop_event.set()
                                            if waiting_thread is not None:
                                                waiting_thread.join(timeout=0.5)
                                            sys.stdout.write("OpenAI: ")
                                            sys.stdout.flush()
                                            first_char_printed = True

                                        # 只有在启用显示时才输出到终端（但 always flush for real-time output）
                                        if show_indicator:
                                            print(content, end="", flush=True)
                                        full_response += content
                            except json.JSONDecodeError:
                                continue
                
                # 如果流式处理失败或没有内容，尝试使用 iter_content 处理（类似 iFlow 的方式）
                if not stream_success or not full_response.strip():
                    # 重置响应
                    full_response = ""
                    raw_data = ""
                    for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                        if chunk:
                            raw_data += chunk
                    
                    # 按行分割处理
                    lines = raw_data.split('\n')
                    for line in lines:
                        if line.strip():
                            # 检查是否是 HTML 响应（可能是错误页面）
                            if line.startswith("<!DOCTYPE") or line.startswith("<html"):
                                raise ValueError(f"收到 HTML 响应而非 JSON: {line[:100]}")
                            
                            # 尝试不同的前缀格式
                            if line.startswith("data: "):
                                try:
                                    data_str = line[6:]  # 去掉 "data: "
                                    if data_str == "[DONE]":
                                        stream_success = True
                                        break
                                    data = json.loads(data_str)
                                    
                                    if "choices" in data and len(data["choices"]) > 0:
                                        choice = data["choices"][0]
                                        
                                        # 确保 choice 是字典
                                        if not isinstance(choice, dict):
                                            continue
                                        
                                        finish_reason = choice.get("finish_reason")
                                        if finish_reason in ["stop", "length", "content_filter", "tool_calls"]:
                                            stream_success = True
                                            break
                                        
                                        delta = choice.get("delta", {})
                                        if not isinstance(delta, dict):
                                            continue
                                        content = delta.get("content", "")
                                        
                                        if content:
                                            stream_success = True
                                            if show_indicator and not first_char_printed:
                                                stop_event.set()
                                                if waiting_thread is not None:
                                                    waiting_thread.join(timeout=0.5)
                                                sys.stdout.write("OpenAI: ")
                                                sys.stdout.flush()
                                                first_char_printed = True
                                            
                                            if show_indicator:
                                                print(content, end="", flush=True)
                                            full_response += content
                                except json.JSONDecodeError:
                                    continue
                            elif line.startswith("data:"):  # 没有空格的格式
                                try:
                                    data_str = line[5:]  # 去掉 "data:"
                                    data = json.loads(data_str)
                                    
                                    if "choices" in data and len(data["choices"]) > 0:
                                        choice = data["choices"][0]
                                        delta = choice.get("delta", {})
                                        content = delta.get("content", "")
                                        
                                        if content:
                                            stream_success = True
                                            if show_indicator and not first_char_printed:
                                                stop_event.set()
                                                if waiting_thread is not None:
                                                    waiting_thread.join(timeout=0.5)
                                                sys.stdout.write("OpenAI: ")
                                                sys.stdout.flush()
                                                first_char_printed = True
                                            
                                            if show_indicator:
                                                print(content, end="", flush=True)
                                            full_response += content
                                except json.JSONDecodeError:
                                    continue
                
                # 如果流式仍然失败，尝试回退到非流式
                if not stream_success or not full_response.strip():
                    # 重新发送非流式请求
                    # 标准 OpenAI API 设置 stream=False
                    payload["stream"] = False
                    try:
                        # 添加额外的调试信息
                        if show_indicator:
                            sys.stdout.write("\r尝试非流式请求...")
                            sys.stdout.flush()
                        
                        response = requests.post(
                            url, headers=headers, json=payload, stream=False, timeout=60
                        )
                        
                        # 检查响应状态
                        if response.status_code != 200:
                            error_text = response.text[:500] if response.text else f"状态码: {response.status_code}"
                            return "", False, f"非流式请求失败: {error_text}", None
                        
                        # 检查响应内容
                        if not response.content:
                            return "", False, "非流式请求返回空响应", None
                        
                        data = response.json()
                        
                        if "choices" in data and len(data["choices"]) > 0:
                            content = data["choices"][0].get("message", {}).get("content", "")
                            if content:
                                if show_indicator:
                                    stop_event.set()
                                    if waiting_thread is not None:
                                        waiting_thread.join(timeout=0.5)
                                    print("\nOpenAI:", content)
                                full_response = content
                            else:
                                return "", False, "响应格式异常：缺少内容", None
                        else:
                            # 提供更详细的错误信息
                            error_info = f"响应格式异常。收到的数据: {str(data)[:200]}"
                            return "", False, error_info, None
                    except requests.exceptions.Timeout:
                        return "", False, "非流式请求超时", None
                    except requests.exceptions.ConnectionError as e:
                        return "", False, f"非流式请求连接错误: {str(e)}", None
                    except json.JSONDecodeError as e:
                        # 尝试显示原始响应
                        raw_response = response.text[:500] if hasattr(response, 'text') else "无法读取响应"
                        return "", False, f"非流式响应JSON解析错误: {str(e)}。原始响应: {raw_response}", None
                    except Exception as e:
                        return "", False, f"非流式请求异常: {str(e)}", None

                if show_indicator:
                    print()

                # 对话历史由调用方管理，此处不再更新
                return full_response, True, None, conversation_id
            else:
                data = response.json()
                if show_indicator:
                    stop_event.set()
                    if waiting_thread is not None:
                        waiting_thread.join(timeout=0.5)

                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0]["message"]["content"]
                    if show_indicator:
                        print("OpenAI:", content)

                    # 对话历史由调用方管理，此处不再更新
                    return content, True, None, conversation_id
                else:
                    return "", False, "未知响应格式", None
        except requests.exceptions.HTTPError as e:
            if show_indicator:
                stop_event.set()
                if waiting_thread is not None:
                    waiting_thread.join(timeout=0.5)
            # 获取更详细的错误信息
            response_text = ""
            try:
                response_text = e.response.text
            except Exception:
                response_text = "无法读取响应内容"
            error_msg = f"HTTP错误 {e.response.status_code}: {response_text}"
            if show_indicator:
                print(f"\r错误: {error_msg}", file=sys.stderr)
            return "", False, error_msg, None
        except requests.exceptions.Timeout:
            if show_indicator:
                stop_event.set()
                if waiting_thread is not None:
                    waiting_thread.join(timeout=0.5)
            error_msg = "请求超时，请稍后重试"
            if show_indicator:
                print(f"\r错误: {error_msg}", file=sys.stderr)
            return "", False, error_msg, None
        except requests.exceptions.ConnectionError as e:
            if show_indicator:
                stop_event.set()
                if waiting_thread is not None:
                    waiting_thread.join(timeout=0.5)
            error_msg = f"连接错误: {str(e)}"
            if show_indicator:
                print(f"\r错误: {error_msg}", file=sys.stderr)
            return "", False, error_msg, None
        except Exception as e:
            if show_indicator:
                stop_event.set()
                if waiting_thread is not None:
                    waiting_thread.join(timeout=0.5)
            error_msg = f"请求错误: {str(e)}"
            if show_indicator:
                print(f"\r错误: {error_msg}", file=sys.stderr)
            return "", False, error_msg, None
        finally:
            if show_indicator:
                stop_event.set()
            if waiting_thread is not None and waiting_thread.is_alive():
                waiting_thread.join(timeout=0.5)


class iFlowProvider(AIProvider):
    """iFlow AI 供应商实现"""

    def __init__(self, api_key: str):
        self.base_url = "https://apis.iflow.cn/v1"
        self.api_key = api_key

        # 从配置中获取 iFlow 模型列表
        if config:
            self.DEFAULT_MODELS = config.get_list(
                "IFLOW_MODELS",
                default=["qwen3-max", "kimi-k2-0905", "glm-4.6", "deepseek-v3.2"],
            )
        else:
            self.DEFAULT_MODELS = [
                "qwen3-max",
                "kimi-k2-0905",
                "glm-4.6",
                "deepseek-v3.2",
            ]

    def get_models(self) -> List[str]:
        """获取 iFlow 模型列表"""
        return self.DEFAULT_MODELS.copy()

    def send_message(
        self,
        message: str,
        model: str,
        role: str = "员工",
        history: Optional[List[dict]] = None,  # 新增：用于传递对话历史
        conversation_id: Optional[str] = None,  # 保留：匹配基类签名
        stream: bool = True,
        show_indicator: bool = True,
    ) -> tuple:
        """发送消息到 iFlow API"""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # 准备消息
        messages = [
            {
                "role": "system",
                "content": f"你是一个AI助手。当前角色：{role}。请以专业、友好的方式回答问题。",
            }
        ]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": message})

        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "temperature": 0.7,
            "max_tokens": 2000,
        }

        stop_event = threading.Event()
        waiting_thread = None
        first_char_printed = False

        try:
            if show_indicator:
                waiting_thread = threading.Thread(
                    target=self.show_waiting_indicator, args=(stop_event,)
                )
                waiting_thread.daemon = True
                waiting_thread.start()

            # 先尝试流式响应，增加超时时间到 60 秒
            response = requests.post(
                url, headers=headers, json=payload, stream=True, timeout=60
            )
            
            # 检查响应状态
            if response.status_code != 200:
                error_msg = f"API返回错误状态码: {response.status_code}"
                try:
                    error_detail = response.text[:500]  # 限制错误信息长度
                    error_msg += f" - {error_detail}"
                except Exception:
                    pass
                return "", False, error_msg, None
                
            response.raise_for_status()

            full_response = ""
            stream_success = False
            has_lines = False
            line_count = 0

            # 尝试流式解析
            try:
                # 直接使用 iter_lines，让 requests 自动处理解压
                # 虽然可能不是完美的流式，但至少能正常工作
                for line in response.iter_lines():
                    if line:
                        has_lines = True
                        line_count += 1
                        decoded_line = line.decode("utf-8")
                        
                        if decoded_line.startswith("data:"):
                            try:
                                data = json.loads(decoded_line[5:])
                                
                                if "choices" in data and len(data["choices"]) > 0:
                                    choice = data["choices"][0]
                                    
                                    # 检查是否是结束标记
                                    finish_reason = choice.get("finish_reason")
                                    if finish_reason == "stop":
                                        stream_success = True
                                        break
                                    
                                    # 提取内容
                                    delta = choice.get("delta", {})
                                    message_obj = choice.get("message", {})
                                    
                                    content = ""
                                    if "content" in delta:
                                        content = delta["content"]
                                    elif "content" in message_obj:
                                        content = message_obj["content"]
                                    elif choice.get("text"):
                                        content = choice["text"]
                                    
                                    # 标记已收到有效的流式响应
                                    if "content" in delta or "content" in message_obj:
                                        stream_success = True
                                    
                                    # 实时显示内容
                                    if content:
                                        if show_indicator and not first_char_printed:
                                            stop_event.set()
                                            if waiting_thread is not None:
                                                waiting_thread.join(timeout=0.5)
                                        first_char_printed = True
                                        
                                        if show_indicator:
                                            print(content, end="", flush=True)
                                        full_response += content
                                        
                            except json.JSONDecodeError:
                                continue
                else:
                    # 非压缩响应，使用 iter_lines
                    for line in response.iter_lines():
                        if line:
                            has_lines = True
                            line_count += 1
                            decoded_line = line.decode("utf-8")
                            
                            if decoded_line.startswith("data:"):
                                try:
                                    data = json.loads(decoded_line[5:])
                                    
                                    if "choices" in data and len(data["choices"]) > 0:
                                        choice = data["choices"][0]
                                        
                                        # 检查是否是结束标记
                                        finish_reason = choice.get("finish_reason")
                                        if finish_reason == "stop":
                                            stream_success = True
                                            break
                                        
                                        # 提取内容
                                        delta = choice.get("delta", {})
                                        message_obj = choice.get("message", {})
                                        
                                        content = ""
                                        if "content" in delta:
                                            content = delta["content"]
                                        elif "content" in message_obj:
                                            content = message_obj["content"]
                                        elif choice.get("text"):
                                            content = choice["text"]
                                        
                                        # 标记已收到有效的流式响应
                                        if "content" in delta or "content" in message_obj:
                                            stream_success = True
                                        
                                        # 实时显示内容
                                        if content:
                                            if show_indicator and not first_char_printed:
                                                stop_event.set()
                                                if waiting_thread is not None:
                                                    waiting_thread.join(timeout=0.5)
                                            first_char_printed = True
                                            
                                            if show_indicator:
                                                print(content, end="", flush=True)
                                            full_response += content
                                            
                                except json.JSONDecodeError:
                                    continue

                # 如果收到了流式响应行但没有解析到内容，也认为是成功的
                if has_lines and not stream_success:
                    stream_success = True

                # 调试信息
                if not show_indicator and full_response:
                    # 在不显示模式下的调试信息
                    pass

                if show_indicator:
                    print()

            except (json.JSONDecodeError, requests.exceptions.RequestException):
                # 流式解析出错，保持 stream_success 为 False，尝试非流式
                pass

            # 如果流式解析失败，尝试非流式
            if not stream_success:
                try:
                    # 重新发送非流式请求
                    # 标准 OpenAI API 设置 stream=False
                    payload["stream"] = False
                    response = requests.post(
                        url, headers=headers, json=payload, stream=False, timeout=60
                    )
                    response.raise_for_status()
                    data = response.json()

                    if "choices" in data and len(data["choices"]) > 0:
                        content = (
                            data["choices"][0].get("message", {}).get("content", "")
                        )
                        if not content and "text" in data["choices"][0]:
                            content = data["choices"][0]["text"]

                        if content:
                            if show_indicator:
                                stop_event.set()
                                if waiting_thread is not None:
                                    waiting_thread.join(timeout=0.5)
                                print("iFlow:", content)
                            full_response = content
                        else:
                            return "", False, "响应格式异常", None
                    else:
                        return "", False, "响应格式异常", None
                except requests.exceptions.Timeout:
                    return "", False, "请求超时", None
                except Exception as e:
                    return "", False, f"非流式回退失败: {str(e)}", None

            # 对话历史由调用方管理，此处不再更新
            # 调试：确保返回的响应不为空
            if not full_response.strip() and stream_success:
                # 如果标记为成功但没有内容，返回一个默认响应
                full_response = "（收到空响应）"
            
            return full_response, True, None, conversation_id

        except requests.exceptions.HTTPError as e:
            if show_indicator:
                stop_event.set()
                if waiting_thread is not None:
                    waiting_thread.join(timeout=0.5)
            # 获取更详细的错误信息
            response_text = ""
            try:
                response_text = e.response.text
            except Exception:
                response_text = "无法读取响应内容"
            error_msg = f"HTTP错误 {e.response.status_code}: {response_text}"
            if show_indicator:
                print(f"\r错误: {error_msg}", file=sys.stderr)
            return "", False, error_msg, None
        except requests.exceptions.Timeout:
            if show_indicator:
                stop_event.set()
                if waiting_thread is not None:
                    waiting_thread.join(timeout=0.5)
            error_msg = "请求超时，请稍后重试"
            if show_indicator:
                print(f"\r错误: {error_msg}", file=sys.stderr)
            return "", False, error_msg, None
        except Exception as e:
            if show_indicator:
                stop_event.set()
                if waiting_thread is not None:
                    waiting_thread.join(timeout=0.5)
            error_msg = f"请求错误: {str(e)}"
            if show_indicator:
                print(f"\r错误: {error_msg}", file=sys.stderr)
            return "", False, error_msg, None
        finally:
            if show_indicator:
                stop_event.set()
            if waiting_thread is not None and waiting_thread.is_alive():
                waiting_thread.join(timeout=0.5)


def get_provider(provider_name: str, **kwargs) -> AIProvider:
    """
    获取 AI 供应商实例

    Args:
        provider_name: 供应商名称 ("dify", "openai", "iflow")
        **kwargs: 供应商初始化参数

    Returns:
        AIProvider 实例
    """
    providers = {"dify": DifyProvider, "openai": OpenAIProvider, "iflow": iFlowProvider}

    if provider_name not in providers:
        raise ValueError(f"不支持的 AI 供应商: {provider_name}")

    return providers[provider_name](**kwargs)
