import sys
import ctypes
import json
from ctypes import wintypes
from pathlib import Path

import crossaim_power as core
import crossaim_power_v12 as v12
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QGridLayout, QGroupBox, QLabel,
    QPushButton, QSpinBox
)

VERSION = "1.3.0"

GWL_EXSTYLE = -20
WS_EX_TOPMOST = 0x00000008
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_NOACTIVATE = 0x08000000

HWND_TOPMOST = -1
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040
SW_SHOWNOACTIVATE = 4

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.QueryFullProcessImageNameW.argtypes = [
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.LPWSTR,
    ctypes.POINTER(wintypes.DWORD),
]
kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]


class CrossAimPowerV13(v12.CrossAimPowerV12):
    def __init__(self):
        core.APP_VERSION = VERSION
        self._last_foreground_hwnd = 0
        self._last_foreground_exe = ""
        super().__init__()
        self.setWindowTitle(f"CrossAim Power {VERSION}")

        self.overlay_watchdog = QTimer(self)
        self.overlay_watchdog.timeout.connect(self.overlay_watchdog_tick)
        self.overlay_watchdog.start(self.watchdog_ms.value())

        self._force_topmost()
        self._update_compat_status("Overlay watchdog ready")

    def build_ui(self):
        super().build_ui()

        left_scroll = self.splitter.widget(0)
        left_container = left_scroll.widget()
        left = left_container.layout()
        insert_at = max(0, left.count() - 1)

        game_group = QGroupBox("Game visibility / compatibility")
        gg = QGridLayout(game_group)

        self.watchdog_enabled = QCheckBox(
            "Force overlay above the foreground game"
        )
        self.watchdog_enabled.setChecked(True)

        self.follow_game_monitor = QCheckBox(
            "Follow fullscreen game monitor"
        )
        self.follow_game_monitor.setChecked(True)

        self.watchdog_ms = QSpinBox()
        self.watchdog_ms.setRange(50, 1000)
        self.watchdog_ms.setValue(100)
        self.watchdog_ms.setSuffix(" ms")
        self.watchdog_ms.valueChanged.connect(
            self._watchdog_interval_changed
        )

        self.compat_status = QLabel("Overlay watchdog ready")
        self.compat_status.setWordWrap(True)
        self.compat_status.setObjectName("status")

        self.fullscreen_note = QLabel(
            "If a game uses true Exclusive Fullscreen, Windows can bypass "
            "normal desktop overlays. For CS2 use Fullscreen Windowed / "
            "Borderless when the overlay is not visible."
        )
        self.fullscreen_note.setWordWrap(True)
        self.fullscreen_note.setObjectName("help")

        test_btn = QPushButton("Re-assert overlay now")
        test_btn.clicked.connect(self._manual_overlay_reassert)

        gg.addWidget(self.watchdog_enabled, 0, 0, 1, 2)
        gg.addWidget(self.follow_game_monitor, 1, 0, 1, 2)
        gg.addWidget(QLabel("Topmost refresh"), 2, 0)
        gg.addWidget(self.watchdog_ms, 2, 1)
        gg.addWidget(test_btn, 3, 0, 1, 2)
        gg.addWidget(self.compat_status, 4, 0, 1, 2)
        gg.addWidget(self.fullscreen_note, 5, 0, 1, 2)

        left.insertWidget(insert_at, game_group)

    def _watchdog_interval_changed(self, value):
        if hasattr(self, "overlay_watchdog"):
            self.overlay_watchdog.setInterval(value)

    def _overlay_hwnd(self):
        try:
            return int(self.ov.winId())
        except Exception:
            return 0

    def _force_topmost(self):
        if not getattr(self, "enabled", False):
            return False
        if getattr(self, "hidden_rmb", False):
            return False

        hwnd = self._overlay_hwnd()
        if not hwnd:
            return False

        try:
            exstyle = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            wanted = (
                exstyle
                | WS_EX_TOPMOST
                | WS_EX_LAYERED
                | WS_EX_TRANSPARENT
                | WS_EX_TOOLWINDOW
                | WS_EX_NOACTIVATE
            )
            if wanted != exstyle:
                user32.SetWindowLongW(hwnd, GWL_EXSTYLE, wanted)

            user32.ShowWindow(hwnd, SW_SHOWNOACTIVATE)
            ok = user32.SetWindowPos(
                hwnd,
                HWND_TOPMOST,
                0,
                0,
                0,
                0,
                SWP_NOMOVE
                | SWP_NOSIZE
                | SWP_NOACTIVATE
                | SWP_SHOWWINDOW,
            )
            return bool(ok)
        except Exception:
            return False

    def _foreground_exe(self, hwnd):
        if not hwnd:
            return ""

        pid = wintypes.DWORD()
        try:
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if not pid.value:
                return ""

            process = kernel32.OpenProcess(
                PROCESS_QUERY_LIMITED_INFORMATION,
                False,
                pid.value,
            )
            if not process:
                return ""

            try:
                size = wintypes.DWORD(32768)
                buffer = ctypes.create_unicode_buffer(size.value)
                if kernel32.QueryFullProcessImageNameW(
                    process,
                    0,
                    buffer,
                    ctypes.byref(size),
                ):
                    return Path(buffer.value).name.lower()
            finally:
                kernel32.CloseHandle(process)
        except Exception:
            pass

        return ""

    def _foreground_state(self):
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return 0, "", False, -1

        rect = RECT()
        if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            return hwnd, self._foreground_exe(hwnd), False, -1

        cx = (rect.left + rect.right) // 2
        cy = (rect.top + rect.bottom) // 2
        screen = QApplication.screenAt(QPoint(cx, cy))
        if screen is None:
            return hwnd, self._foreground_exe(hwnd), False, -1

        screens = QApplication.screens()
        try:
            screen_index = screens.index(screen)
        except ValueError:
            screen_index = -1

        g = screen.geometry()
        tolerance = 3
        fullscreen_sized = (
            abs(rect.left - g.x()) <= tolerance
            and abs(rect.top - g.y()) <= tolerance
            and abs(rect.right - (g.x() + g.width())) <= tolerance
            and abs(rect.bottom - (g.y() + g.height())) <= tolerance
        )

        return (
            hwnd,
            self._foreground_exe(hwnd),
            fullscreen_sized,
            screen_index,
        )

    def _set_monitor_without_signal_loop(self, index):
        if not hasattr(self, "monitor_combo"):
            return
        if index < 0 or index >= self.monitor_combo.count():
            return
        if self.monitor_combo.currentIndex() == index:
            return

        self.monitor_combo.blockSignals(True)
        self.monitor_combo.setCurrentIndex(index)
        self.monitor_combo.blockSignals(False)
        self._selected_monitor = index
        self._center_overlay()

    def _update_compat_status(self, text):
        if hasattr(self, "compat_status"):
            self.compat_status.setText(text)

    def _manual_overlay_reassert(self):
        if not self.enabled:
            self.toggle()
            return

        self.ov.show()
        self._center_overlay()
        self.ov.raise_()
        ok = self._force_topmost()
        self._update_compat_status(
            "Manual TOPMOST refresh: OK"
            if ok
            else "Manual TOPMOST refresh failed"
        )

    def overlay_watchdog_tick(self):
        if not self.watchdog_enabled.isChecked():
            self._update_compat_status("Watchdog disabled")
            return

        if not self.enabled:
            self._update_compat_status(
                "Overlay is OFF — press F8 to enable"
            )
            return

        hwnd, exe, fullscreen_sized, screen_index = (
            self._foreground_state()
        )

        if (
            self.follow_game_monitor.isChecked()
            and fullscreen_sized
            and screen_index >= 0
        ):
            self._set_monitor_without_signal_loop(screen_index)

        foreground_changed = hwnd != self._last_foreground_hwnd
        if foreground_changed:
            self._last_foreground_hwnd = hwnd
            self._last_foreground_exe = exe
            try:
                self.ov.show()
                self.ov.raise_()
            except Exception:
                pass

        ok = self._force_topmost()

        label = exe or "unknown app"
        mode = (
            "fullscreen-sized"
            if fullscreen_sized
            else "windowed"
        )
        result = (
            "TOPMOST active"
            if ok
            else "TOPMOST refresh failed"
        )

        if fullscreen_sized:
            self._update_compat_status(
                f"Foreground: {label} • {mode} • {result}. "
                "If still invisible, use Fullscreen Windowed / Borderless."
            )
        else:
            self._update_compat_status(
                f"Foreground: {label} • {mode} • {result}"
            )

    def toggle(self):
        super().toggle()
        if self.enabled:
            QTimer.singleShot(0, self._manual_overlay_reassert)

    def load(self):
        super().load()
        try:
            data = json.loads(
                self.settings.read_text(encoding="utf-8")
            )
            if hasattr(self, "watchdog_enabled"):
                self.watchdog_enabled.setChecked(
                    data.get("watchdog_enabled", True)
                )
                self.follow_game_monitor.setChecked(
                    data.get("follow_game_monitor", True)
                )
                self.watchdog_ms.setValue(
                    int(data.get("watchdog_ms", 100))
                )
        except Exception:
            pass

    def save(self):
        super().save()
        try:
            data = json.loads(
                self.settings.read_text(encoding="utf-8")
            )
            if hasattr(self, "watchdog_enabled"):
                data["watchdog_enabled"] = (
                    self.watchdog_enabled.isChecked()
                )
                data["follow_game_monitor"] = (
                    self.follow_game_monitor.isChecked()
                )
                data["watchdog_ms"] = self.watchdog_ms.value()

            self.settings.write_text(
                json.dumps(data, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass


def main():
    if sys.platform != "win32":
        print("CrossAim Power requires Windows 10/11.")
        return 1

    try:
        core.ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass

    app = QApplication(sys.argv)
    app.setApplicationName("CrossAim Power")

    icon = Path(__file__).with_name("crossaim_power.png")
    if icon.exists():
        app.setWindowIcon(QIcon(str(icon)))

    window = CrossAimPowerV13()
    window.show()

    if window.start_hidden.isChecked():
        QTimer.singleShot(0, window.hide)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
