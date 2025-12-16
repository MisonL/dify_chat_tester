"""
供应商设置模块
负责处理不同AI供应商的初始化配置
"""

import sys

from dify_chat_tester.providers.base import get_provider
from dify_chat_tester.config.loader import get_config
from dify_chat_tester.cli.terminal import (
    console,
    input_api_key,
    print_api_key_confirmation,
    print_error,
    print_info,
    print_input_prompt,
)

_config = get_config()


def _is_interactive() -> bool:
    """判断当前环境是否为交互式终端。

    在非交互环境（如 pytest、重定向等）下，避免等待用户输入，
    直接使用配置中的预设值，以保证自动化执行不会被阻塞。
    """
    try:
        return sys.stdin is not None and sys.stdin.isatty()
    except Exception:
        return False


def _normalize_base_url(base_url: str) -> str:
    """规范化基础 URL：补全协议并去掉多余空格。"""
    base_url = (base_url or "").strip()
    if not base_url:
        return ""
    if not base_url.startswith(("http://", "https://")):
        base_url = "https://" + base_url
    return base_url


def setup_dify_provider():
    """设置 Dify AI 供应商

    优先从配置文件读取 Dify 相关配置；若缺失则回退到交互式输入。
    """
    # 1. 优先从配置读取
    cfg_base_url = _normalize_base_url(_config.get_str("DIFY_BASE_URL", ""))
    cfg_api_key = _config.get_str("DIFY_API_KEY", "").strip()
    cfg_app_id = _config.get_str("DIFY_APP_ID", "").strip()

    # 优先使用配置中已经提供的字段，缺失的再走交互
    base_url = cfg_base_url
    api_key = cfg_api_key
    app_id = cfg_app_id

    # 如果配置中已有值，允许用户在交互式环境下一键确认或重新输入；
    # 在非交互环境（如自动化测试）中则直接使用配置值，避免阻塞。
    if base_url and _is_interactive():
        confirm = (
            print_input_prompt(
                f"检测到配置文件中的 Dify API 基础 URL: {base_url}，是否直接使用？(Y/n)"
            )
            .strip()
            .lower()
        )
        if confirm not in ("", "y", "yes"):
            base_url = ""  # 清空以便后续走交互输入

    if api_key:
        if _is_interactive():
            print_info("检测到配置文件中的 Dify API 密钥。")
            # 复用统一的密钥确认逻辑，必要时允许用户选择重新输入
            if not print_api_key_confirmation(api_key):
                api_key = ""
        # 非交互环境下直接使用配置的密钥

    if app_id and _is_interactive():
        confirm = (
            print_input_prompt(
                f"检测到配置文件中的 Dify 应用 ID: {app_id}，是否直接使用？(Y/n)"
            )
            .strip()
            .lower()
        )
        if confirm not in ("", "y", "yes"):
            app_id = ""

    # 仅对缺失的字段进行交互式补全
    if not base_url:
        info_message = (
            "获取 Dify API 服务器地址：\n\n"
            "【情况一】使用官方 Dify Cloud 平台：\n"
            "1. 登录 Dify Cloud (https://cloud.dify.ai)\n"
            "2. 创建应用后，进入应用设置\n"
            "3. 在左侧菜单选择「API 访问」\n"
            "4. API 服务器地址通常为：https://api.dify.ai/v1\n\n"
            "【情况二】使用私有化部署的 Dify 平台：\n"
            "1. 登录您的私有 Dify 平台\n"
            "2. 进入平台工作流\n"
            "3. 在「访问API」页面的右上角找到「API服务器」\n"
            "4. 复制显示的 API 服务器地址"
        )
        print_info(info_message)
        console.print()

        while True:
            base_url_input = print_input_prompt(
                "请输入 Dify API 基础 URL (例如: https://api.dify.ai/v1)"
            ).strip()
            if not base_url_input:
                print_error("API 基础 URL 不能为空。")
                continue

            base_url = _normalize_base_url(base_url_input)
            break

    if not api_key:
        while True:
            print_info("请输入 Dify API 密钥（输入不会显示在屏幕上）")
            api_key_input = input_api_key("密钥: ").strip()
            if not api_key_input:
                print_error("API 密钥不能为空。")
                continue

            # 确认输入的密钥（显示部分）
            if not print_api_key_confirmation(api_key_input):
                continue
            api_key = api_key_input
            break

    if not app_id:
        app_id_info = (
            "获取 Dify 应用 ID：\n"
            "进入 Dify 平台对应的工作流页面，从浏览器地址栏获取 UUID 格式的应用 ID\n"
            "例如：https://your-dify-domain.com/app/【应用ID】/workflow"
        )
        print_info(app_id_info)
        console.print()

        while True:
            app_id_input = print_input_prompt("请输入 Dify 应用 ID").strip()
            if not app_id_input:
                print_error("应用 ID 不能为空。")
                continue
            app_id = app_id_input
            break

    return get_provider("dify", base_url=base_url, api_key=api_key, app_id=app_id)


def setup_openai_provider():
    """设置 OpenAI 兼容接口供应商

    优先从配置文件读取 OPENAI_BASE_URL / OPENAI_API_KEY；
    若缺失则回退到交互式输入。
    """
    # 1. 优先从配置读取
    cfg_base_url = _normalize_base_url(_config.get_str("OPENAI_BASE_URL", ""))
    cfg_api_key = _config.get_str("OPENAI_API_KEY", "").strip()

    base_url = cfg_base_url
    api_key = cfg_api_key

    # 如果配置中已有值，允许用户在交互式环境下一键确认或重新输入；
    # 在非交互环境（如自动化测试）中则直接使用配置值。
    if base_url and _is_interactive():
        confirm = (
            print_input_prompt(
                f"检测到配置文件中的 OpenAI 兼容接口基础 URL: {base_url}，是否直接使用？(Y/n)"
            )
            .strip()
            .lower()
        )
        if confirm not in ("", "y", "yes"):
            base_url = ""

    if api_key and _is_interactive():
        print_info("检测到配置文件中的 OpenAI 兼容接口 API 密钥。")
        if not print_api_key_confirmation(api_key):
            api_key = ""

    # 对缺失的字段进行交互式补全
    if not base_url:
        while True:
            base_url_input = print_input_prompt(
                "请输入 OpenAI 兼容 API 基础 URL (例如: https://api.openai.com/v1 或自定义)"
            ).strip()
            if not base_url_input:
                print_error("API 基础 URL 不能为空。")
                continue

            base_url = _normalize_base_url(base_url_input)
            break  # URL 有效，跳出循环

    if not api_key:
        while True:
            print_info("请输入 API 密钥（输入不会显示在屏幕上）")
            api_key_input = input_api_key("密钥: ").strip()
            if not api_key_input:
                print_error("API 密钥不能为空。")
                continue

            # 确认输入的密钥（显示部分）
            if not print_api_key_confirmation(api_key_input):
                continue  # 用户选择不确认，重新输入
            api_key = api_key_input
            break  # 密钥有效且用户确认，跳出循环

    return get_provider("openai", base_url=base_url, api_key=api_key)


def setup_iflow_provider():
    """设置 iFlow AI 供应商

    优先从配置文件读取 IFLOW_API_KEY；若缺失则回退到交互式输入。
    """
    # 1. 优先从配置读取
    cfg_api_key = _config.get_str("IFLOW_API_KEY", "").strip()

    if cfg_api_key:
        api_key = cfg_api_key
        if _is_interactive():
            print_info("检测到配置文件中的 iFlow API 密钥。")
            if print_api_key_confirmation(api_key):
                return get_provider("iflow", api_key=api_key)
            # 用户不确认，则继续走交互式输入
        else:
            # 非交互环境下直接使用配置密钥
            return get_provider("iflow", api_key=api_key)

    # 2. 回退到交互式输入
    while True:
        print_info(
            "请输入 iFlow API 密钥（从 https://platform.iflow.cn/profile?tab=apiKey 获取）"
        )
        api_key = input_api_key("密钥: ").strip()
        if not api_key:
            print_error("API 密钥不能为空。")
            continue

        # 确认输入的密钥（显示部分）
        if not print_api_key_confirmation(api_key):
            continue  # 用户选择不确认，重新输入
        break  # 密钥有效且用户确认，跳出循环

    return get_provider("iflow", api_key=api_key)


# --- 插件系统集成 ---
from dify_chat_tester.providers.plugin_manager import PluginManager

_plugin_manager = PluginManager()
try:
    # 1. 加载内置插件
    _plugin_manager.load_plugins()
    
    # 2. 加载外部私有插件（如果配置了路径）
    external_plugins_path = _config.get_str("EXTERNAL_PLUGINS_PATH", "").strip()
    if external_plugins_path:
        _plugin_manager.load_external_plugins(external_plugins_path)
except Exception as e:
    # 插件加载不应影响主程序启动
    print_error(f"警告: 插件加载失败: {e}")

def setup_plugin_provider(provider_id: str):
    """设置插件提供的 AI 供应商
    
    Args:
        provider_id: 供应商唯一ID
        
    Returns:
        AIProvider: 初始化的供应商实例
    """
    plugin_config = _plugin_manager.plugin_configs.get(provider_id)
    if not plugin_config:
        return None
        
    # 如果注册的是实例，直接返回
    if plugin_config.get("type") == "instance":
        return plugin_config.get("instance")
        
    # 如果注册的是类，尝试实例化 (假设不需要参数，或插件在注册时已处理配置)
    if plugin_config.get("type") == "class":
        provider_cls = plugin_config.get("class")
        try:
            return provider_cls()
        except Exception as e:
            print_error(f"无法实例化插件供应商 {provider_id}: {e}")
            return None
            
    return None

def get_plugin_providers_config():
    """获取所有插件供应商的配置信息 (用于菜单显示)"""
    configs = {}
    for pid, pdata in _plugin_manager.plugin_configs.items():
        configs[str(len(configs) + 100)] = {  # 使用 100+ 的序号避免冲突
            "name": pdata["name"],
            "id": pid
        }
    return configs
    

def get_plugin_manager():
    """获取插件管理器实例"""
    return _plugin_manager
