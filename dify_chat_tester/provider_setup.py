"""
供应商设置模块
负责处理不同AI供应商的初始化配置
"""

from dify_chat_tester.ai_providers import get_provider
from dify_chat_tester.config_loader import get_config
from dify_chat_tester.terminal_ui import (
    console,
    input_api_key,
    print_api_key_confirmation,
    print_error,
    print_info,
    print_input_prompt,
)

_config = get_config()


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

    if base_url:
        print_info("已从配置文件读取 Dify API 基础 URL，将直接使用。")

    if api_key:
        print_info("已从配置文件读取 Dify API 密钥，将直接使用。")

    if app_id:
        print_info("已从配置文件读取 Dify 应用 ID，将直接使用。")

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

    if base_url:
        print_info("已从配置文件读取 OpenAI 兼容接口基础 URL，将直接使用。")

    if api_key:
        print_info("已从配置文件读取 OpenAI 兼容接口 API 密钥，将直接使用。")

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
        print_info("已从配置文件读取 iFlow 配置，将直接使用。")
        return get_provider("iflow", api_key=cfg_api_key)

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
