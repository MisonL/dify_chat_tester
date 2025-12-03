"""ConfigLoader 与 parse_ai_providers 的基础单元测试。"""

import os
import tempfile


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

    assert loader.get_list("NOT_EXIST", default=["x"]) == ["x"]


def test_load_config_file_exists(tmp_path):
    """测试配置文件存在时的加载逻辑"""
    config_file = tmp_path / ".env.test"
    config_file.write_text("KEY=value\n# Comment\nINT_VAL=123", encoding="utf-8")

    loader = ConfigLoader(env_file=str(config_file.name))
    # Mock _get_config_file_path to return our temp file
    loader._get_config_file_path = lambda: str(config_file)
    loader.load_config()

    assert loader.get("KEY") == "value"
    assert loader.get_int("INT_VAL") == 123


def test_load_config_create_default(tmp_path, monkeypatch):
    """测试配置文件不存在时创建默认配置"""
    env_filename = ".env.new"
    loader = ConfigLoader(env_file=env_filename)

    # Mock _get_config_file_path to return path in tmp_path
    monkeypatch.setattr(
        loader, "_get_config_file_path", lambda: str(tmp_path / env_filename)
    )

    # Mock _create_default_config_file to verify it's called and make it write to tmp_path
    # We use _create_basic_config_file to actually create the file in tmp_path
    def mock_create_default():
        loader._create_basic_config_file(str(tmp_path))

    monkeypatch.setattr(loader, "_create_default_config_file", mock_create_default)

    # Ensure file doesn't exist
    assert not (tmp_path / env_filename).exists()

    # Run load_config
    loader.load_config()

    # Verify file was created
    assert (tmp_path / env_filename).exists()
    # Verify defaults were loaded
    assert loader.get("LOG_LEVEL") == "INFO"


def test_config_with_comments():
    """测试带注释的配置文件"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = os.path.join(tmpdir, ".env")
        with open(config_file, "w") as f:
            f.write("# Comment line\n")
            f.write("TEST_KEY=value\n")
            f.write("  # Another comment\n")
            f.write("ANOTHER_KEY=123\n")

        loader = ConfigLoader(env_file=config_file)
        loader.load_config()
        assert loader.get_str("TEST_KEY") == "value"
        assert loader.get_int("ANOTHER_KEY") == 123


def test_get_types():
    """测试各种类型的获取方法"""
    loader = ConfigLoader.__new__(ConfigLoader)
    loader.config = {
        "STR": " text ",
        "INT": "42",
        "FLOAT": "3.14",
        "BOOL_1": "true",
        "BOOL_2": "0",
    }

    # 修正：ConfigLoader.get_str 只是调用 get，没有 strip。
    # 但 _read_config_file 会 strip value。
    # 这里我们直接注入 dict，所以测试 get_str 的行为
    assert loader.get_str("STR") == " text "

    assert loader.get_int("INT") == 42
    assert loader.get_int("INVALID", default=10) == 10

    assert loader.get_float("FLOAT") == 3.14
    assert loader.get_float("INVALID", default=1.0) == 1.0

    assert loader.get_bool("BOOL_1") is True
    assert loader.get_bool("BOOL_2") is False


def test_get_enable_thinking(monkeypatch):
    """测试 get_enable_thinking 方法"""
    loader = ConfigLoader.__new__(ConfigLoader)
    loader.config = {"ENABLE_THINKING": "false"}

    # 1. 环境变量优先
    monkeypatch.setenv("ENABLE_THINKING", "true")
    assert loader.get_enable_thinking() is True

    # 2. 无环境变量，使用配置
    monkeypatch.delenv("ENABLE_THINKING", raising=False)
    assert loader.get_enable_thinking() is False

    # 3. 默认值
    loader.config = {}
    assert loader.get_enable_thinking() is True  # 默认为 True
