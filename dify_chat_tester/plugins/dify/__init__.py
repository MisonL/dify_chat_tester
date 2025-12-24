"""Dify AI 供应商插件"""

from dify_chat_tester.config.loader import get_config


def _normalize_base_url(base_url: str) -> str:
    base_url = (base_url or "").strip()
    if not base_url:
        return ""
    if not base_url.startswith(("http://", "https://")):
        base_url = "https://" + base_url
    return base_url


def setup(manager):
    """插件入口：注册 Dify 供应商"""
    from .provider import DifyProvider

    config = get_config()

    # 读取配置
    cfg_base_url = _normalize_base_url(config.get_str("DIFY_BASE_URL", ""))
    cfg_api_key = config.get_str("DIFY_API_KEY", "").strip()
    cfg_app_id = config.get_str("DIFY_APP_ID", "").strip()

    # 如果配置完整，直接注册实例
    if cfg_base_url and cfg_api_key and cfg_app_id:
        provider = DifyProvider(
            base_url=cfg_base_url, api_key=cfg_api_key, app_id=cfg_app_id
        )
        manager.register_instance("dify", provider, "Dify")
    else:
        # 配置不完整，注册类（需要交互式设置）
        manager.register_provider("dify", DifyProvider, "Dify")
