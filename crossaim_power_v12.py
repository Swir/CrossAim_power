import sys
import json
from pathlib import Path

import crossaim_power as core
import crossaim_power_v11 as v11
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QComboBox, QFrame, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel
)

VERSION = "1.2.0"


class CrossAimPowerV12(v11.ResponsiveMain):
    def __init__(self):
        core.APP_VERSION = VERSION
        self._selected_monitor = 0
        super().__init__()
        self.setWindowTitle(f"CrossAim Power {VERSION}")
        self._update_color_chip()

    def build_ui(self):
        super().build_ui()

        # Left settings panel created by v1.1.
        left_scroll = self.splitter.widget(0)
        left_container = left_scroll.widget()
        left = left_container.layout()

        # Insert before the existing stretch spacer.
        insert_at = max(0, left.count() - 1)

        profile_group = QGroupBox("Reticle presets")
        pg = QGridLayout(profile_group)
        self.profile_combo = QComboBox()
        self.profile_combo.addItems([
            "Custom",
            "CS2 Tiny Dot",
            "Precision Cross",
            "Ring + Dot",
            "Classic Cross",
            "High Visibility",
        ])
        self.profile_combo.currentTextChanged.connect(self.apply_reticle_profile)
        pg.addWidget(QLabel("Preset"), 0, 0)
        pg.addWidget(self.profile_combo, 0, 1)
        left.insertWidget(insert_at, profile_group)
        insert_at += 1

        display_group = QGroupBox("Display")
        dg = QGridLayout(display_group)
        self.monitor_combo = QComboBox()
        self.refresh_monitor_list()
        self.monitor_combo.currentIndexChanged.connect(self.change_monitor)
        dg.addWidget(QLabel("Monitor"), 0, 0)
        dg.addWidget(self.monitor_combo, 0, 1)
        left.insertWidget(insert_at, display_group)
        insert_at += 1

        live_group = QGroupBox("Live adaptive color")
        lg = QGridLayout(live_group)
        self.aim_color_chip = QLabel("AIM")
        self.aim_color_chip.setAlignment(Qt.AlignCenter)
        self.aim_color_chip.setMinimumHeight(38)
        self.aim_color_hex = QLabel("#FFFFFF")
        self.aim_color_hex.setObjectName("status")
        lg.addWidget(QLabel("Current reticle color"), 0, 0, 1, 2)
        lg.addWidget(self.aim_color_chip, 1, 0)
        lg.addWidget(self.aim_color_hex, 1, 1)
        left.insertWidget(insert_at, live_group)

        # Permanent author footer below the responsive splitter.
        outer = self.centralWidget().layout()
        footer = QFrame()
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(8, 3, 8, 1)
        footer_layout.addStretch(1)
        self.author_footer = QLabel(
            'Made by <b>Swir</b> • '
            '<a href="https://github.com/Swir">GitHub: github.com/Swir</a> • '
            '<a href="https://github.com/Swir/CrossAim_power">CrossAim Power</a>'
        )
        self.author_footer.setOpenExternalLinks(True)
        self.author_footer.setTextInteractionFlags(Qt.TextBrowserInteraction)
        footer_layout.addWidget(self.author_footer)
        footer_layout.addStretch(1)
        outer.addWidget(footer)

        self.author_footer.setStyleSheet(
            "color:#74849b;font-size:9pt;"
        )

    def refresh_monitor_list(self):
        self.monitor_combo.blockSignals(True)
        self.monitor_combo.clear()
        for index, screen in enumerate(QApplication.screens()):
            g = screen.geometry()
            self.monitor_combo.addItem(
                f"{index + 1}: {screen.name()} — {g.width()}×{g.height()}", index
            )
        if self.monitor_combo.count():
            self.monitor_combo.setCurrentIndex(
                min(self._selected_monitor, self.monitor_combo.count() - 1)
            )
        self.monitor_combo.blockSignals(False)

    def selected_screen(self):
        screens = QApplication.screens()
        if not screens:
            return QApplication.primaryScreen()
        index = self.monitor_combo.currentIndex() if hasattr(self, "monitor_combo") else 0
        index = max(0, min(index, len(screens) - 1))
        return screens[index]

    def change_monitor(self, index):
        self._selected_monitor = max(0, index)
        self._center_overlay()

    def _center_overlay(self):
        screen = self.selected_screen()
        if not screen:
            return
        g = screen.geometry()
        self.ov.move(
            g.x() + g.width() // 2 - self.ov.width() // 2,
            g.y() + g.height() // 2 - self.ov.height() // 2,
        )

    def apply_reticle_profile(self, name):
        profiles = {
            "CS2 Tiny Dot": ("Dot", 1, 100),
            "Precision Cross": ("Cross + Dot", 1, 100),
            "Ring + Dot": ("Circle + Dot", 1, 100),
            "Classic Cross": ("Cross", 2, 100),
            "High Visibility": ("Cross + Dot", 3, 100),
        }
        if name == "Custom" or name not in profiles:
            return
        shape_name, scale, opacity = profiles[name]
        self.editor.set_matrix(core.shape(shape_name))
        self.scale.setValue(scale)
        self.opacity.setValue(opacity)

    def _update_color_chip(self):
        if not hasattr(self, "aim_color_chip"):
            return
        color = self.ov.color
        text = "#000000" if color.lightness() > 140 else "#FFFFFF"
        self.aim_color_chip.setStyleSheet(
            f"background:{color.name()};color:{text};"
            "border:1px solid #4b5b72;border-radius:6px;font-weight:800;"
        )
        self.aim_color_hex.setText(color.name().upper())

    def tick_color(self):
        super().tick_color()
        self._update_color_chip()

    def toggle(self):
        super().toggle()
        if self.enabled:
            self._center_overlay()
        self._update_color_chip()

    def save(self):
        data = {
            "matrix": self.editor.matrix,
            "scale": self.scale.value(),
            "opacity": self.opacity.value(),
            "outline": self.outline.isChecked(),
            "mode": self.mode.currentText(),
            "sample": self.sample.value(),
            "smooth": self.smooth.value(),
            "refresh_ms": self.refresh_ms.value(),
            "rmb": self.rmb.isChecked(),
            "start_hidden": self.start_hidden.isChecked(),
            "close_to_tray": self.close_to_tray.isChecked(),
            "reticle_profile": self.profile_combo.currentText() if hasattr(self, "profile_combo") else "Custom",
            "monitor_index": self.monitor_combo.currentIndex() if hasattr(self, "monitor_combo") else 0,
            "window": {"x": self.x(), "y": self.y(), "w": self.width(), "h": self.height()},
            "splitter_sizes": self.splitter.sizes(),
        }
        self.settings.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def load(self):
        try:
            data = json.loads(self.settings.read_text(encoding="utf-8"))
            self.editor.matrix = data.get("matrix", self.editor.matrix)
            self.scale.setValue(data.get("scale", 2))
            self.opacity.setValue(data.get("opacity", 100))
            self.outline.setChecked(data.get("outline", True))
            self.mode.setCurrentText(data.get("mode", "Power Smart Contrast"))
            self.sample.setValue(data.get("sample", 21))
            self.smooth.setValue(data.get("smooth", 50))
            self.refresh_ms.setValue(data.get("refresh_ms", 35))
            self.rmb.setChecked(data.get("rmb", True))
            self.start_hidden.setChecked(data.get("start_hidden", False))
            self.close_to_tray.setChecked(data.get("close_to_tray", True))

            if hasattr(self, "profile_combo"):
                profile = data.get("reticle_profile", "Custom")
                if self.profile_combo.findText(profile) >= 0:
                    self.profile_combo.blockSignals(True)
                    self.profile_combo.setCurrentText(profile)
                    self.profile_combo.blockSignals(False)

            if hasattr(self, "monitor_combo"):
                index = int(data.get("monitor_index", 0))
                index = max(0, min(index, self.monitor_combo.count() - 1))
                self.monitor_combo.setCurrentIndex(index)
                self._selected_monitor = index

            window = data.get("window", {})
            if window:
                self.resize(max(640, int(window.get("w", 1080))), max(520, int(window.get("h", 760))))
                self.move(int(window.get("x", self.x())), int(window.get("y", self.y())))

            sizes = data.get("splitter_sizes")
            if isinstance(sizes, list) and len(sizes) == 2:
                self.splitter.setSizes([max(100, int(sizes[0])), max(100, int(sizes[1]))])

            self.sync()
            self._center_overlay()
            self._update_color_chip()
        except Exception:
            self.sync()
            self._update_color_chip()


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

    window = CrossAimPowerV12()
    window.show()
    if window.start_hidden.isChecked():
        QTimer.singleShot(0, window.hide)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
