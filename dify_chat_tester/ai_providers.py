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
        """Dify 使用应用 ID，不支持模型列表"""
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
        # 根据 Dify 官方文档，私有化部署使用 /v1/chat-messages 路径
        # base_url 应该是域名，程序会自动添加 /v1 前缀

        # Ensure base_url ends with /v1
        if not self.base_url.endswith("/v1"):
            # If it ends with a slash, remove it before adding /v1
            if self.base_url.endswith("/"):
                self.base_url = self.base_url.rstrip("/") + "/v1"
            else:
                self.base_url += "/v1"

        url = f"{self.base_url}/chat-messages"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "inputs": {"role": role},
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
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8")
                    # 检查是否是 HTML 响应（可能是错误页面）
                    if decoded_line.startswith("<!DOCTYPE") or decoded_line.startswith(
                        "<html"
                    ):
                        raise Exception(
                            f"收到 HTML 响应而非 JSON: {decoded_line[:100]}"
                        )
                    if decoded_line.startswith("data:"):
                        try:
                            data = json.loads(decoded_line[5:])

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

                                # 只有在启用显示时才输出到终端（但 always flush for real-time output）
                                if show_indicator:
                                    print(data["answer"], end="", flush=True)
                                full_response += data["answer"]
                            elif "error" in data:
                                if show_indicator:
                                    stop_event.set()
                                    if waiting_thread is not None:
                                        waiting_thread.join(timeout=0.5)
                                error_msg = data.get("error", "未知错误")
                                print(f"\n错误: {error_msg}", file=sys.stderr)
                                return "", False, error_msg, None
                        except json.JSONDecodeError:
                            if show_indicator:
                                stop_event.set()
                                if waiting_thread is not None:
                                    waiting_thread.join(timeout=0.5)
                            return "", False, f"JSON解析错误: {decoded_line}", None
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
        # 处理 base_url：如果已包含 /v1 路径，只添加 /chat/completions
        if self.base_url.endswith("/v1"):
            url = f"{self.base_url}/chat/completions"
        else:
            url = f"{self.base_url}/v1/chat/completions"

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

            response = requests.post(
                url,
                headers=headers,
                json=payload,
                stream=stream,
                timeout=30,
                allow_redirects=False,
            )
            response.raise_for_status()

            if stream:
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode("utf-8")
                        if decoded_line.startswith("data: "):
                            if decoded_line == "data: [DONE]":
                                break
                            try:
                                data = json.loads(decoded_line[6:])

                                if "choices" in data and len(data["choices"]) > 0:
                                    delta = data["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        content = delta["content"]
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
            error_msg = f"HTTP错误: {e.response.status_code} - {e.response.text}"
            if show_indicator:
                print(f"\r错误: {error_msg}", file=sys.stderr)
            return "", False, error_msg, None
        except Exception as e:
            if show_indicator:
                stop_event.set()
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

            # 先尝试流式响应
            response = requests.post(
                url, headers=headers, json=payload, stream=True, timeout=30
            )
            response.raise_for_status()

            full_response = ""
            stream_success = False

            # 尝试流式解析
            try:
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode("utf-8")
                        if decoded_line.startswith("data: "):
                            if decoded_line == "data: [DONE]":
                                stream_success = True
                                break
                            try:
                                data = json.loads(decoded_line[6:])

                                if "choices" in data and len(data["choices"]) > 0:
                                    # 尝试多种可能的数据结构
                                    delta = data["choices"][0].get("delta", {})
                                    message_obj = data["choices"][0].get("message", {})

                                    content = ""
                                    if "content" in delta:
                                        content = delta["content"]
                                    elif "content" in message_obj:
                                        content = message_obj["content"]
                                    elif data["choices"][0].get("text"):
                                        content = data["choices"][0]["text"]

                                    if content:
                                        # 标记流式解析成功
                                        stream_success = True
                                        if show_indicator and not first_char_printed:
                                            stop_event.set()
                                            if waiting_thread is not None:
                                                waiting_thread.join(timeout=0.5)
                                            first_char_printed = True

                                        # 只有在启用显示时才输出到终端（但 always flush for real-time output）
                                        if show_indicator:
                                            print(content, end="", flush=True)
                                        full_response += content
                            except json.JSONDecodeError:
                                continue

                if show_indicator:
                    print()

            except (json.JSONDecodeError, requests.exceptions.RequestException):
                # 流式解析出错，保持 stream_success 为 False，尝试非流式
                pass

            # 如果流式解析失败，尝试非流式
            if not stream_success:
                try:
                    # 重新发送非流式请求
                    payload["stream"] = False
                    response = requests.post(
                        url, headers=headers, json=payload, stream=False, timeout=30
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
            return full_response, True, None, conversation_id

        except requests.exceptions.HTTPError as e:
            if show_indicator:
                stop_event.set()
            error_msg = f"HTTP错误: {e.response.status_code} - {e.response.text}"
            if show_indicator:
                print(f"\r错误: {error_msg}", file=sys.stderr)
            return "", False, error_msg, None
        except Exception as e:
            if show_indicator:
                stop_event.set()
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
