"""OpenAI 兼容接口插件"""

from dify_chat_tester.config.loader import get_config
import sys


def _is_interactive() -> bool:
    try:
        return sys.stdin is not None and sys.stdin.isatty()
    except Exception:
        return False


def _normalize_base_url(base_url: str) -> str:
    base_url = (base_url or "").strip()
    if not base_url:
        return ""
    if not base_url.startswith(("http://", "https://")):
        base_url = "https://" + base_url
    return base_url


def setup(manager):
    """插件入口：注册 OpenAI 兼容接口供应商"""
    from .provider import OpenAIProvider
    
    config = get_config()
    
    # 读取配置
    cfg_base_url = _normalize_base_url(config.get_str("OPENAI_BASE_URL", ""))
    cfg_api_key = config.get_str("OPENAI_API_KEY", "").strip()
    
    # 如果配置完整，直接注册实例
    if cfg_base_url and cfg_api_key:
        provider = OpenAIProvider(base_url=cfg_base_url, api_key=cfg_api_key)
        manager.register_instance("openai", provider, "OpenAI 兼容接口")
    else:
        # 配置不完整，注册类
        manager.register_provider("openai", OpenAIProvider, "OpenAI 兼容接口")
