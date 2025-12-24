from unittest.mock import patch
from main import parse_args, _auto_install_dependencies


class TestMain:
    def test_parse_args_interactive(self):
        args = parse_args([])
        assert args.mode == "interactive"
        assert args.enable_demo_plugin is False

    def test_parse_args_question_gen(self):
        args = parse_args(["--mode", "question-generation", "--folder", "/fake/path"])
        assert args.mode == "question-generation"
        assert args.folder == "/fake/path"

    def test_parse_args_concurrency(self):
        args = parse_args(["--concurrency", "5"])
        assert args.concurrency == 5

    def test_auto_install_no_uv(self):
        with patch("shutil.which", return_value=None):
            # Should return safely
            _auto_install_dependencies()

    def test_auto_install_frozen(self):
        with patch("sys.frozen", True, create=True):
            # Should return safely
            _auto_install_dependencies()

    @patch("subprocess.run")
    def test_auto_install_execution(self, mock_run, tmp_path):
        plugin_dir = tmp_path / "plugins"
        plugin_dir.mkdir()
        p1 = plugin_dir / "p1"
        p1.mkdir()
        (p1 / "requirements.txt").write_text("pkg1\npkg2")

        with patch("shutil.which", return_value="/usr/bin/uv"):
            with patch("sys.frozen", False, create=True):
                # We need to capture stdout to avoid cluttering test output
                with patch("builtins.print"):
                    _auto_install_dependencies(plugins_dir=str(plugin_dir))

                    # Verify subprocess.run was called with uv add and the packages
                    mock_run.assert_called()
                    args = mock_run.call_args[0][0]
                    assert "uv" in args
                    assert "add" in args
                    assert "pkg1" in args
                    assert "pkg2" in args

    @patch("subprocess.run")
    def test_auto_install_failed_uv(self, mock_run, tmp_path):
        import subprocess

        mock_run.side_effect = subprocess.CalledProcessError(1, "uv")

        plugin_dir = tmp_path / "plugins"
        plugin_dir.mkdir()
        p1 = plugin_dir / "p1"
        p1.mkdir()
        (p1 / "requirements.txt").write_text("pkg1")

        with patch("shutil.which", return_value="/usr/bin/uv"):
            with patch("builtins.print") as mock_print:
                _auto_install_dependencies(plugins_dir=str(plugin_dir))
                # Should print warning instead of crashing
                mock_print.assert_any_call(" ⚠️ (自动安装失败，将尝试继续)")
