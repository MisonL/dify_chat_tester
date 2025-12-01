"""ConfigLoader 与 parse_ai_providers 的基础单元测试。"""

from dify_chat_tester.config_loader import ConfigLoader, parse_ai_providers


def test_parse_ai_providers_empty_returns_default():
    providers = parse_ai_providers("")
    # 默认应包含 3 个提供商，且 key 为 "1","2","3"
    assert set(providers.keys()) == {"1", "2", "3"}
    assert providers["1"]["id"] == "dify"
    assert providers["2"]["id"] == "openai"
    assert providers["3"]["id"] == "iflow"


def test_parse_ai_providers_custom_value_overrides_default():
    value = "1:Dify Cloud:dify;2:Custom OpenAI:openai-custom"
    providers = parse_ai_providers(value)
    assert set(providers.keys()) == {"1", "2"}
    assert providers["1"]["name"] == "Dify Cloud"
    assert providers["1"]["id"] == "dify"
    assert providers["2"]["name"] == "Custom OpenAI"
    assert providers["2"]["id"] == "openai-custom"


def test_config_loader_get_bool_and_get_list():
    # 直接构造一个 ConfigLoader 实例并注入配置字典，避免读写文件
    loader = ConfigLoader.__new__(ConfigLoader)  # type: ignore[call-arg]
    loader.env_file = "<memory>"  # 仅用于调试，无实际文件
    loader.config = {
        "FLAG_TRUE": "true",
        "FLAG_YES": "yes",
        "FLAG_FALSE": "false",
        "EMPTY_LIST": "",
        "LIST_VALUE": "a, b , c",
    }

    assert loader.get_bool("FLAG_TRUE") is True
    assert loader.get_bool("FLAG_YES") is True
    assert loader.get_bool("FLAG_FALSE") is False
    # 未配置时应返回默认值
    assert loader.get_bool("NOT_EXIST", default=True) is True

    # get_list: 空字符串返回默认值
    assert loader.get_list("EMPTY_LIST", default=[]) == []
    assert loader.get_list("LIST_VALUE") == ["a", "b", "c"]
    # 未配置时使用提供的默认列表
    assert loader.get_list("NOT_EXIST", default=["x"]) == ["x"]
