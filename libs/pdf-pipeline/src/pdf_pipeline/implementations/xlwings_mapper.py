import atexit
import os
import signal
import sys
import threading
import time
from pathlib import Path

from ..abstractions.excel_mapper import ExcelMapper

_live_apps: list = []
_live_pids: set[int] = set()
_live_apps_lock = threading.Lock()


def _is_pid_alive(pid: int) -> bool:
    if sys.platform == "win32":
        import ctypes
        kernel32 = ctypes.windll.kernel32
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        STILL_ACTIVE = 259
        handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            return False
        try:
            exit_code = ctypes.c_ulong()
            kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))
            return exit_code.value == STILL_ACTIVE
        finally:
            kernel32.CloseHandle(handle)
    else:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False


def _quit_app(app, timeout: float = 5.0) -> None:
    try:
        pid = app.pid
    except Exception:
        return
    try:
        app.quit()
    except Exception:
        pass
    deadline = time.time() + timeout
    while time.time() < deadline:
        if not _is_pid_alive(pid):
            return
        time.sleep(0.2)
    try:
        if sys.platform == "win32":
            os.kill(pid, signal.SIGTERM)
        else:
            os.kill(pid, signal.SIGKILL)
    except OSError:
        pass


def _cleanup_excel_apps():
    with _live_apps_lock:
        for app in _live_apps:
            try:
                app.quit()
            except Exception:
                pass
        _live_apps.clear()
        for pid in _live_pids:
            if _is_pid_alive(pid):
                try:
                    os.kill(pid, signal.SIGTERM)
                except OSError:
                    pass
        _live_pids.clear()


atexit.register(_cleanup_excel_apps)


class XlwingsMapper(ExcelMapper):
    """Generic Excel mapper using xlwings COM. Feature-specific subclasses
    override _get_column_mapping() and optionally _post_write()."""

    def write(self, records: list[dict], output_path: Path) -> Path:
        import xlwings as xw

        app = xw.App(visible=False, add_book=False)
        with _live_apps_lock:
            _live_apps.append(app)
            _live_pids.add(app.pid)
        try:
            wb = app.books.add()
            sheet = wb.sheets[0]

            if not records:
                wb.save(str(output_path))
                wb.close()
                _quit_app(app)
                return output_path

            headers = list(records[0].keys())
            sheet.range("A1").value = headers

            data = [[record.get(h) for h in headers] for record in records]
            sheet.range("A2").value = data

            output_path.parent.mkdir(parents=True, exist_ok=True)
            wb.save(str(output_path))
            wb.close()
        finally:
            pid = None
            try:
                pid = app.pid
            except Exception:
                pass
            _quit_app(app)
            with _live_apps_lock:
                if app in _live_apps:
                    _live_apps.remove(app)
                if pid:
                    _live_pids.discard(pid)

        return output_path
