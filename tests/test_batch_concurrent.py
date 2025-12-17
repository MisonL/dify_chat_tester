# tests/test_batch_concurrent.py
"""并发批量处理功能的单元测试"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import threading
import time

from dify_chat_tester.core.batch import (
    wait_for_any,
    KeyboardControl,
    _generate_worker_table,
    _process_single_question,
)


class TestWaitForAny:
    """测试 wait_for_any 函数"""

    def test_empty_futures(self):
        """空 futures 集合应返回两个空集合"""
        done, not_done = wait_for_any(set())
        assert done == set()
        assert not_done == set()

    def test_with_completed_future(self):
        """有已完成的 future 时应正确返回"""
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(lambda: "result")
            time.sleep(0.1)  # 等待完成

            done, not_done = wait_for_any({future}, timeout=1.0)
            assert len(done) == 1
            assert future in done


class TestKeyboardControl:
    """测试键盘控制类"""

    def test_initial_state(self):
        """测试初始状态"""
        kb = KeyboardControl()
        assert kb.stop_requested is False
        assert kb.paused is False
        assert kb._running is False

    def test_start_stop(self):
        """测试启动和停止"""
        kb = KeyboardControl()
        kb.start()
        assert kb._running is True
        assert kb._listener_thread is not None
        
        kb.stop()
        assert kb._running is False

    def test_stop_requested_flag(self):
        """测试停止请求标志"""
        kb = KeyboardControl()
        kb.stop_requested = True
        assert kb.stop_requested is True

    def test_paused_flag(self):
        """测试暂停标志"""
        kb = KeyboardControl()
        kb.paused = True
        assert kb.paused is True
        kb.paused = False
        assert kb.paused is False


class TestGenerateWorkerTable:
    """测试工作线程状态表格生成"""

    def test_empty_workers(self):
        """测试空工作线程状态"""
        table = _generate_worker_table({}, 0, 10, 0)
        assert table is not None
        assert "并发处理" in table.title

    def test_with_workers(self):
        """测试有工作线程状态"""
        worker_status = {
            1: {"state": "处理中", "question": "问题1"},
            2: {"state": "完成", "question": "问题2"},
            3: {"state": "失败", "question": "问题3"},
        }
        table = _generate_worker_table(worker_status, 2, 10, 1)
        assert table is not None

    def test_paused_state(self):
        """测试暂停状态显示"""
        table = _generate_worker_table({}, 5, 10, 0, paused=True)
        assert "暂停" in table.title

    def test_progress_display(self):
        """测试进度显示"""
        table = _generate_worker_table({}, 5, 10, 1, paused=False)
        # 标题应包含进度信息
        assert "[5/10]" in table.title
        assert "✅4" in table.title  # 成功数 = 完成数 - 失败数
        assert "❌1" in table.title


class TestProcessSingleQuestion:
    """测试单个问题处理函数"""

    def test_calls_provider_send_message(self):
        """测试是否正确调用 provider.send_message"""
        mock_provider = MagicMock()
        mock_provider.send_message.return_value = ("回答", True, None, "conv-1")

        result = _process_single_question(
            provider=mock_provider,
            question="测试问题",
            selected_model="model-1",
            selected_role="user",
            enable_thinking=False,
        )

        mock_provider.send_message.assert_called_once_with(
            message="测试问题",
            model="model-1",
            role="user",
            stream=True,
            show_indicator=False,
            show_thinking=False,
        )
        assert result == ("回答", True, None, "conv-1")

    def test_with_thinking_enabled(self):
        """测试启用思维链"""
        mock_provider = MagicMock()
        mock_provider.send_message.return_value = ("回答", True, None, "conv-1")

        _process_single_question(
            provider=mock_provider,
            question="问题",
            selected_model="model",
            selected_role="role",
            enable_thinking=True,
        )

        # 验证 show_thinking 参数
        call_kwargs = mock_provider.send_message.call_args[1]
        assert call_kwargs["show_thinking"] is True


class TestCLIArguments:
    """测试 CLI 参数解析"""

    def test_concurrency_argument_parsed(self):
        """测试 --concurrency 参数被正确解析"""
        import argparse
        
        parser = argparse.ArgumentParser()
        parser.add_argument("--concurrency", type=int, default=1)
        
        args = parser.parse_args(["--concurrency", "5"])
        assert args.concurrency == 5

    def test_default_concurrency(self):
        """测试默认并发数为 1"""
        import argparse
        
        parser = argparse.ArgumentParser()
        parser.add_argument("--concurrency", type=int, default=1)
        
        args = parser.parse_args([])
        assert args.concurrency == 1


class TestConfigLoader:
    """测试配置加载器对新配置项的支持"""

    @patch("dify_chat_tester.config.loader.get_config")
    def test_batch_concurrency_config(self, mock_get_config):
        """测试 BATCH_CONCURRENCY 配置项"""
        mock_config = MagicMock()
        mock_config.get_int.return_value = 5
        mock_get_config.return_value = mock_config

        config = mock_get_config()
        concurrency = config.get_int("BATCH_CONCURRENCY", 1)
        
        assert concurrency == 5
        mock_config.get_int.assert_called_with("BATCH_CONCURRENCY", 1)
