import sys
import json
import time
from datetime import datetime
from pathlib import Path

import crossaim_power as core
import crossaim_power_v13 as v13
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QGridLayout, QGroupBox, QLabel,
    QPushButton, QSpinBox
)

VERSION = "1.3.1"
VK_F9 = 0x78
HWND_NOTOPMOST = -2

KNOWN_GAMES = {
    "cs2.exe",
    "valorant-win64-shipping.exe",
    "fortniteclient-win64-shipping.exe",
    "r5apex.exe",
    "overwatch.exe",
    "overwatchlauncher.exe",
    "rainbowsix.exe",
    "rainbowsix_vulkan.exe",
    "cod.exe",
}


class CrossAimPowerV131(v13.CrossAimPowerV13):
    def __init__(self):
        core.APP_VERSION = VERSION
        self._f9_prev = False
        self._game_foreground_snapshot = 0
        self._last_diag_state = None
        self._last_hard_reassert = 0.0
        super().__init__()
        self.setWindowTitle(f"CrossAim Power {VERSION}")
        self._install_display_watchers()
        self._log_diag("CrossAim Power v1.3.1 started")
        self._update_game_status("Smart Game Mode ready")

    def build_ui(self):
        super().build_ui()

        left_scroll = self.splitter.widget(0)
        left_container = left_scroll.widget()
        left = left_container.layout()
        insert_at = max(0, left.count() - 1)

        stability_group = QGroupBox("Smart Game Mode v1.3.1")
        sg = QGridLayout(stability_group)

        self.smart_game_mode = QCheckBox(
            "Auto-detect supported foreground games"
        )
        self.smart_game_mode.setChecked(True)

        self.auto_hard_reassert = QCheckBox(
            "Hard re-assert after Alt+Tab / game activation"
        )
        self.auto_hard_reassert.setChecked(True)

        self.diagnostics_enabled = QCheckBox(
            "Write compatibility diagnostics log"
        )
        self.diagnostics_enabled.setChecked(True)

        self.game_watchdog_ms = QSpinBox()
        self.game_watchdog_ms.setRange(50, 500)
        self.game_watchdog_ms.setValue(75)
        self.game_watchdog_ms.setSuffix(" ms")

        self.desktop_watchdog_ms = QSpinBox()
        self.desktop_watchdog_ms.setRange(200, 2000)
        self.desktop_watchdog_ms.setValue(500)
        self.desktop_watchdog_ms.setSuffix(" ms")

        self.game_mode_status = QLabel("Smart Game Mode ready")
        self.game_mode_status.setWordWrap(True)
        self.game_mode_status.setObjectName("status")

        hard_btn = QPushButton("Hard re-assert overlay [F9]")
        hard_btn.clicked.connect(self._hard_reassert_overlay)

        copy_log_btn = QPushButton("Copy diagnostics path")
        copy_log_btn.clicked.connect(self._copy_diagnostics_path)

        sg.addWidget(self.smart_game_mode, 0, 0, 1, 2)
        sg.addWidget(self.auto_hard_reassert, 1, 0, 1, 2)
        sg.addWidget(self.diagnostics_enabled, 2, 0, 1, 2)
        sg.addWidget(QLabel("Game watchdog"), 3, 0)
        sg.addWidget(self.game_watchdog_ms, 3, 1)
        sg.addWidget(QLabel("Desktop watchdog"), 4, 0)
        sg.addWidget(self.desktop_watchdog_ms, 4, 1)
        sg.addWidget(hard_btn, 5, 0, 1, 2)
        sg.addWidget(copy_log_btn, 6, 0, 1, 2)
        sg.addWidget(self.game_mode_status, 7, 0, 1, 2)

        left.insertWidget(insert_at, stability_group)

    def _install_display_watchers(self):
        try:
            app = QApplication.instance()
            app.screenAdded.connect(self._screens_changed)
            app.screenRemoved.connect(self._screens_changed)
        except Exception:
            pass

    def _screens_changed(self, *args):
        try:
            if hasattr(self, "refresh_monitor_list"):
                self.refresh_monitor_list()
            QTimer.singleShot(100, self._hard_reassert_overlay)
            self._log_diag("Display configuration changed")
        except Exception:
            pass

    def _diag_path(self):
        return core.appdir() / "diagnostics.log"

    def _log_diag(self, message):
        if hasattr(self, "diagnostics_enabled") and not self.diagnostics_enabled.isChecked():
            return
        try:
            path = self._diag_path()
            if path.exists() and path.stat().st_size > 1024 * 1024:
                data = path.read_text(encoding="utf-8", errors="replace")
                path.write_text(data[-250000:], encoding="utf-8")
            stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with path.open("a", encoding="utf-8") as handle:
                handle.write(f"[{stamp}] {message}\n")
        except Exception:
            pass

    def _copy_diagnostics_path(self):
        try:
            QApplication.clipboard().setText(str(self._diag_path()))
            self._update_game_status("Diagnostics path copied to clipboard")
        except Exception:
            pass

    def _update_game_status(self, text):
        if hasattr(self, "game_mode_status"):
            self.game_mode_status.setText(text)

    def _is_known_game(self, exe):
        return bool(exe and exe.lower() in KNOWN_GAMES)

    def _hard_reassert_overlay(self):
        if not getattr(self, "enabled", False):
            return False
        if getattr(self, "hidden_rmb", False):
            return False

        hwnd = self._overlay_hwnd()
        if not hwnd:
            self._update_game_status("Hard re-assert failed: no overlay HWND")
            return False

        try:
            self.ov.show()
            self._center_overlay()

            # Reset the topmost state once, then immediately restore TOPMOST.
            # This is only used on game activation/manual F9 to avoid flicker.
            v13.user32.SetWindowPos(
                hwnd,
                HWND_NOTOPMOST,
                0, 0, 0, 0,
                v13.SWP_NOMOVE | v13.SWP_NOSIZE | v13.SWP_NOACTIVATE,
            )
            v13.user32.ShowWindow(hwnd, v13.SW_SHOWNOACTIVATE)
            ok = v13.user32.SetWindowPos(
                hwnd,
                v13.HWND_TOPMOST,
                0, 0, 0, 0,
                v13.SWP_NOMOVE
                | v13.SWP_NOSIZE
                | v13.SWP_NOACTIVATE
                | v13.SWP_SHOWWINDOW,
            )

            try:
                self.ov.raise_()
            except Exception:
                pass

            self._last_hard_reassert = time.monotonic()
            result = bool(ok)
            self._log_diag(
                f"Hard TOPMOST re-assert {'OK' if result else 'FAILED'}"
            )
            return result
        except Exception as exc:
            self._log_diag(f"Hard TOPMOST re-assert error: {exc}")
            return False

    def tick_keys(self):
        super().tick_keys()

        f9 = core.key_down(VK_F9)
        if f9 and not self._f9_prev:
            ok = self._hard_reassert_overlay()
            self._update_game_status(
                "F9 hard re-assert: OK" if ok else "F9 hard re-assert failed"
            )
        self._f9_prev = f9

    def overlay_watchdog_tick(self):
        hwnd, exe, fullscreen_sized, screen_index = self._foreground_state()
        known_game = self._is_known_game(exe)

        if self.smart_game_mode.isChecked():
            target_interval = (
                self.game_watchdog_ms.value()
                if known_game
                else self.desktop_watchdog_ms.value()
            )
            if self.overlay_watchdog.interval() != target_interval:
                self.overlay_watchdog.setInterval(target_interval)

        foreground_changed = hwnd != self._game_foreground_snapshot
        self._game_foreground_snapshot = hwnd

        if (
            known_game
            and foreground_changed
            and self.auto_hard_reassert.isChecked()
            and self.enabled
        ):
            # Schedule several no-focus re-asserts because some games reorder
            # windows more than once while Alt+Tab/display mode settles.
            QTimer.singleShot(0, self._hard_reassert_overlay)
            QTimer.singleShot(120, self._hard_reassert_overlay)
            QTimer.singleShot(300, self._hard_reassert_overlay)

        super().overlay_watchdog_tick()

        mode = "fullscreen-sized" if fullscreen_sized else "windowed"
        game_label = exe or "unknown app"

        if known_game:
            self._update_game_status(
                f"GAME MODE: {game_label} • {mode} • "
                f"watchdog {self.overlay_watchdog.interval()} ms • "
                "F9 = hard recovery"
            )
        else:
            self._update_game_status(
                f"Foreground: {game_label} • desktop mode • "
                f"watchdog {self.overlay_watchdog.interval()} ms"
            )

        diag_state = (
            game_label,
            mode,
            self.enabled,
            screen_index,
            self.overlay_watchdog.interval(),
        )
        if diag_state != self._last_diag_state:
            self._last_diag_state = diag_state
            self._log_diag(
                "Foreground="
                f"{game_label}; mode={mode}; overlay={self.enabled}; "
                f"screen={screen_index}; interval="
                f"{self.overlay_watchdog.interval()}ms"
            )

    def toggle(self):
        super().toggle()
        if self.enabled:
            QTimer.singleShot(50, self._hard_reassert_overlay)

    def load(self):
        super().load()
        try:
            data = json.loads(self.settings.read_text(encoding="utf-8"))
            if hasattr(self, "smart_game_mode"):
                self.smart_game_mode.setChecked(
                    data.get("smart_game_mode", True)
                )
                self.auto_hard_reassert.setChecked(
                    data.get("auto_hard_reassert", True)
                )
                self.diagnostics_enabled.setChecked(
                    data.get("diagnostics_enabled", True)
                )
                self.game_watchdog_ms.setValue(
                    int(data.get("game_watchdog_ms", 75))
                )
                self.desktop_watchdog_ms.setValue(
                    int(data.get("desktop_watchdog_ms", 500))
                )
        except Exception:
            pass

    def save(self):
        super().save()
        try:
            data = json.loads(self.settings.read_text(encoding="utf-8"))
            if hasattr(self, "smart_game_mode"):
                data["smart_game_mode"] = self.smart_game_mode.isChecked()
                data["auto_hard_reassert"] = (
                    self.auto_hard_reassert.isChecked()
                )
                data["diagnostics_enabled"] = (
                    self.diagnostics_enabled.isChecked()
                )
                data["game_watchdog_ms"] = self.game_watchdog_ms.value()
                data["desktop_watchdog_ms"] = (
                    self.desktop_watchdog_ms.value()
                )
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

    window = CrossAimPowerV131()
    window.show()

    if window.start_hidden.isChecked():
        QTimer.singleShot(0, window.hide)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
