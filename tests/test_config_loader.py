import os
import pytest
from unittest.mock import patch
from dify_chat_tester.config.loader import ConfigLoader


class TestConfigLoader:
    @pytest.fixture
    def mock_env_content(self):
        return """
# Comment
KEY1=value1
INT_KEY=42
FLOAT_KEY=3.14
BOOL_KEY=true
LIST_KEY=a,b,c
MULTI_LINE_KEY=
\"\"\"
line1
line2
\"\"\"
"""

    def test_read_config_file(self, tmp_path, mock_env_content):
        mock_content = """
KEY1=value1
MULTI_LINE_KEY=\"\"\"
line1
line2
\"\"\"
"""
        env_file = tmp_path / ".env.test"
        env_file.write_text(mock_content)

        loader = ConfigLoader(env_file=str(env_file))
        assert loader.get("KEY1") == "value1"
        assert "line1\nline2" in loader.get("MULTI_LINE_KEY")

    def test_get_type_safe(self, tmp_path):
        content = """
INT_KEY=42
FLOAT_KEY=3.14
BOOL_KEY=true
LIST_KEY=a,b,c
"""
        env_file = tmp_path / ".env.test"
        env_file.write_text(content)
        loader = ConfigLoader(env_file=str(env_file))

        assert loader.get_int("INT_KEY") == 42
        assert loader.get_int("MISSING", 7) == 7
        assert loader.get_float("FLOAT_KEY") == 3.14
        assert loader.get_bool("BOOL_KEY") is True
        assert loader.get_list("LIST_KEY") == ["a", "b", "c"]

    def test_env_override(self, tmp_path):
        env_file = tmp_path / ".env.test"
        env_file.write_text("KEY=file_value")

        # Note: ConfigLoader usually reads from file into self.config
        # Environmental overrides are handled in specific methods like get_system_prompt
        # Here we test a method that supports override
        with patch.dict(os.environ, {"SYSTEM_PROMPT": "env_prompt"}):
            loader = ConfigLoader(env_file=str(env_file))
            assert loader.get_system_prompt() == "env_prompt"

    def test_default_config_creation(self, tmp_path):
        # Test that it creates a default file if it doesn't exist
        test_dir = tmp_path / "subdir"
        test_dir.mkdir()
        env_file = test_dir / ".env.config"

        with patch(
            "dify_chat_tester.config.loader.ConfigLoader._get_project_root"
        ) as mock_root:
            mock_root.return_value = str(test_dir)
            loader = ConfigLoader(env_file=".env.config")
            assert env_file.exists()
            # BATCH_REQUEST_INTERVAL is in _get_default_config_dict
            assert loader.get("BATCH_REQUEST_INTERVAL") == "1.0"

    def test_parse_ai_providers(self):
        from dify_chat_tester.config.loader import parse_ai_providers

        raw = "1:GPT:gpt-4;2:Claude:claude-3"
        providers = parse_ai_providers(raw)
        assert len(providers) == 2
        assert providers["1"]["name"] == "GPT"
        assert providers["2"]["id"] == "claude-3"
