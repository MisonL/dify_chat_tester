"""Batch Manager 模块的深度测试"""

import os
import tempfile
from unittest.mock import MagicMock, patch


from dify_chat_tester.batch_manager import run_batch_query


class TestBatchManagerExtended:
    """Batch Manager 扩展测试"""

    @patch("dify_chat_tester.terminal_ui.select_column_by_index")
    @patch("dify_chat_tester.batch_manager.get_config")
    @patch("dify_chat_tester.batch_manager.init_excel_log")
    @patch("dify_chat_tester.batch_manager.log_to_excel")
    @patch("dify_chat_tester.batch_manager.print_input_prompt")
    @patch("dify_chat_tester.batch_manager.print_file_list")
    def test_run_batch_query_flow(
        self,
        mock_print_list,
        mock_input,
        mock_log,
        mock_init_excel,
        mock_config,
        mock_select_col,
    ):
        """测试批量查询完整流程"""
        # Mock 配置
        mock_config.return_value.get_str.return_value = "batch_log.xlsx"

        # Mock 列选择
        mock_select_col.return_value = 0

        # Mock Excel 初始化
        mock_wb = MagicMock()
        mock_ws = MagicMock()
        mock_init_excel.return_value = (mock_wb, mock_ws)

        # Mock 文件列表
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建一个有效的 Excel 文件
            file_path = os.path.join(tmpdir, "questions.xlsx")
            import openpyxl

            wb = openpyxl.Workbook()
            ws = wb.active
            ws.append(["Question"])  # Header
            ws.append(["Q1"])
            ws.append(["Q2"])
            wb.save(file_path)
            wb.close()

            # Mock print_file_list (虽然这里不重要，因为我们直接输入路径)
            mock_print_list.return_value = [file_path]

            # Mock os.listdir 确保它不返回干扰项，或者我们直接走 else 分支
            # 但为了简单，我们假设 run_batch_query 可能会列出文件，也可能不列出
            # 关键是 input 的第一个值应该是 file_path

            # Mock 用户输入：
            # 1. 输入文件路径
            # 2. 确认开始 "y"
            # 3. 防止无限循环
            mock_input.side_effect = [file_path, "y", KeyboardInterrupt]

            # Mock Provider
            mock_provider = MagicMock()
            mock_provider.send_message.return_value = ("Answer", True, None, None)

            # 运行
            # 我们需要 patch os.listdir 吗？
            # 如果 os.listdir 返回空，会提示输入路径 -> file_path
            # 如果 os.listdir 返回文件，会提示输入序号或路径 -> file_path
            # 所以直接输入 file_path 是通用的

            run_batch_query(
                mock_provider,
                "user",
                "Dify",
                "model",
                batch_request_interval=0,
                batch_default_show_response=False,
            )

            # 验证
            assert mock_provider.send_message.call_count == 2
            assert mock_log.call_count == 2
            mock_wb.save.assert_called()

    @patch("dify_chat_tester.batch_manager.print_file_list")
    @patch("dify_chat_tester.batch_manager.print_input_prompt")
    def test_run_batch_query_no_files(self, mock_input, mock_print_list):
        """测试没有 Excel 文件的情况"""
        # 模拟 os.listdir 返回空（通过不创建任何文件，或者假设当前目录没有）
        # 实际上我们无法控制 os.listdir，除非 patch 它
        # 但如果 os.listdir 返回了文件，逻辑会不同

        # 让我们 patch os.listdir 确保它返回空
        with patch("os.listdir", return_value=[]):
            # 模拟用户输入无效路径，然后输入退出命令或者抛出异常中断循环
            # 这里我们让它抛出 KeyboardInterrupt 来模拟中断，或者输入一个不存在的文件然后 mock_print 报错

            # 为了简单，我们让它输入一个不存在的文件，然后再次循环...
            # 最好是抛出异常来结束循环
            mock_input.side_effect = KeyboardInterrupt

            try:
                run_batch_query(MagicMock(), "user", "Dify", "model", 0, False)
            except KeyboardInterrupt:
                pass

            # 验证是否提示了输入路径
            mock_input.assert_called()

    @patch("dify_chat_tester.batch_manager.print_file_list")
    @patch("dify_chat_tester.batch_manager.print_input_prompt")
    def test_run_batch_query_cancel_file_selection(self, mock_input, mock_print_list):
        """测试取消文件选择"""
        # 假设 os.listdir 返回文件
        with patch("os.listdir", return_value=["file1.xlsx", "file2.xlsx"]):
            with patch("os.path.isfile", return_value=True):
                mock_input.return_value = "0"  # 无效序号，或者我们想测试什么？
                # 代码逻辑：
                # file_index = int(file_input)
                # if 1 <= file_index <= len(excel_files): ...
                # else: print error ... continue

                # 如果输入 "0"，会报错并 continue
                # 如果输入非数字，会尝试作为路径

                # 我们想测试“取消”？代码里好像没有明确的取消选项，除了 Ctrl+C
                # 或者输入一个不存在的路径

                # 让我们模拟输入一个不存在的文件，然后中断
                mock_input.side_effect = ["non_existent.xlsx", KeyboardInterrupt]

                try:
                    run_batch_query(MagicMock(), "user", "Dify", "model", 0, False)
                except KeyboardInterrupt:
                    pass

                assert mock_input.call_count >= 1
