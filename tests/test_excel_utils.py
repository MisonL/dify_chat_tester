"""excel_utils 模块的基础单元测试。"""

from dify_chat_tester.excel_utils import clean_excel_text, init_excel_log, log_to_excel


def test_clean_excel_text_removes_illegal_chars():
    # 包含合法和非法控制字符的字符串
    text = "Hello\x00World\x07\nNext Line\x1fEnd"
    cleaned = clean_excel_text(text)
    # 非法字符应被移除，但换行保留
    assert "\x00" not in cleaned
    assert "\x07" not in cleaned
    assert "\x1f" not in cleaned
    assert "Hello" in cleaned and "World" in cleaned
    assert "Next Line" in cleaned


def test_log_to_excel_appends_cleaned_row(tmp_path):
    file_path = tmp_path / "log.xlsx"

    # 初始化日志文件
    workbook, worksheet = init_excel_log(str(file_path), ["col1", "col2"])

    # 写入一行包含非法字符的数据
    row = ["val\x00ue1", "val\x07ue2"]
    log_to_excel(worksheet, row)

    # 保存并重新加载，验证内容被清理
    workbook.save(str(file_path))

    from openpyxl import load_workbook

    wb2 = load_workbook(str(file_path))
    ws2 = wb2.active

    # 第一行是表头，第二行才是我们写入的数据
    values = [cell.value for cell in ws2[2]]
    assert values == ["value1", "value2"]
