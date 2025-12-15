"""iFlow AI 供应商插件"""

from dify_chat_tester.config_loader import get_config


def setup(manager):
    """插件入口：注册 iFlow 供应商"""
    from .provider import iFlowProvider
    
    config = get_config()
    
    # 读取配置
    cfg_api_key = config.get_str("IFLOW_API_KEY", "").strip()
    
    # 如果配置完整，直接注册实例
    if cfg_api_key:
        provider = iFlowProvider(api_key=cfg_api_key)
        manager.register_instance("iflow", provider, "iFlow")
    else:
        # 配置不完整，注册类
        manager.register_provider("iflow", iFlowProvider, "iFlow")
