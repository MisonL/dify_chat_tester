"""与控制台平台相关的小模块测试：console_background 与 windows_console。"""


def test_set_console_background_noop():
    """console_background.set_console_background 应该是一个安全的空操作。"""
    from dify_chat_tester.console_background import set_console_background

    # 只要调用不抛异常即可
    set_console_background()


def test_windows_console_import_on_non_windows(monkeypatch):
    """在非 Windows 平台下导入 windows_console 不应抛异常。"""
    import importlib
    import sys

    # 强制当前平台为非 win32，确保 if 分支不执行
    monkeypatch.setattr(sys, "platform", "darwin")

    # 只验证导入行为，不要求执行 enable_console_paste
    import dify_chat_tester.windows_console  # noqa: F401

    # 再次导入以确保模块可重入
    importlib.reload(dify_chat_tester.windows_console)


def test_windows_console_win32_path_success(monkeypatch):
    """在模拟的 win32 环境下执行 enable_console_paste 成功路径。"""
    import importlib
    import sys
    import types

    monkeypatch.setattr(sys, "platform", "win32")

    fake_ctypes = types.SimpleNamespace()

    class DummyDWORD:
        def __init__(self, value: int = 0):
            self.value = value

    fake_wintypes = types.SimpleNamespace(DWORD=DummyDWORD)

    class DummyKernel32:
        def GetStdHandle(self, handle):  # noqa: ARG002
            return 1

        def GetConsoleMode(self, handle, mode_ptr):  # noqa: ARG002
            mode_ptr.value = 0
            return 1

        def SetConsoleMode(self, handle, mode):  # noqa: ARG002
            return 1

    fake_ctypes.wintypes = fake_wintypes
    fake_ctypes.windll = types.SimpleNamespace(kernel32=DummyKernel32())
    fake_ctypes.byref = lambda x: x

    monkeypatch.setitem(sys.modules, "ctypes", fake_ctypes)

    import dify_chat_tester.windows_console as win_mod

    importlib.reload(win_mod)


def test_windows_console_win32_path_failure(monkeypatch):
    """在 win32 模拟下让 enable_console_paste 返回 False，覆盖备用 subprocess 路径。"""
    import importlib
    import subprocess as real_subprocess
    import sys
    import types

    monkeypatch.setattr(sys, "platform", "win32")

    fake_ctypes = types.SimpleNamespace()

    class DummyDWORD:
        def __init__(self, value: int = 0):
            self.value = value

    fake_wintypes = types.SimpleNamespace(DWORD=DummyDWORD)

    class DummyKernel32:
        def GetStdHandle(self, handle):  # noqa: ARG002
            return 1

        def GetConsoleMode(self, handle, mode_ptr):  # noqa: ARG002
            mode_ptr.value = 0
            return 1

        def SetConsoleMode(self, handle, mode):  # noqa: ARG002
            # 模拟失败
            return 0

    fake_ctypes.wintypes = fake_wintypes
    fake_ctypes.windll = types.SimpleNamespace(kernel32=DummyKernel32())
    fake_ctypes.byref = lambda x: x

    monkeypatch.setitem(sys.modules, "ctypes", fake_ctypes)

    # 拦截 subprocess.run，防止真的执行命令
    import subprocess

    monkeypatch.setattr(
        subprocess, "run", lambda *a, **k: real_subprocess.CompletedProcess(a, 0)
    )

    import dify_chat_tester.windows_console as win_mod

    importlib.reload(win_mod)
