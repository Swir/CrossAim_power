import sys
import json
from pathlib import Path

import crossaim_power as core
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QComboBox, QSlider, QSpinBox, QCheckBox, QGroupBox,
    QScrollArea, QSplitter, QSystemTrayIcon, QMenu, QFrame
)

VERSION = "1.1.0"


class ResponsiveMain(core.Main):
    def __init__(self):
        core.APP_VERSION = VERSION
        self._really_quit = False
        self._compact_layout = False
        super().__init__()
        self.setMinimumSize(640, 520)
        self.resize(1080, 760)
        self.setup_tray()
        self.setWindowTitle(f"CrossAim Power {VERSION}")
        self.adapt.setInterval(self.refresh_ms.value())

    def build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(8)

        header = QFrame()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 6, 10, 6)
        titles = QVBoxLayout()
        title = QLabel("CROSSAIM POWER")
        title.setObjectName("title")
        subtitle = QLabel("Adaptive multi-zone gaming reticle • responsive UI")
        subtitle.setObjectName("subtitle")
        titles.addWidget(title)
        titles.addWidget(subtitle)
        header_layout.addLayout(titles)
        header_layout.addStretch(1)
        self.overlay_state = QLabel("● OVERLAY ON")
        self.overlay_state.setObjectName("overlayOn")
        header_layout.addWidget(self.overlay_state)
        outer.addWidget(header)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(6)
        outer.addWidget(self.splitter, 1)

        left_container = QWidget()
        left = QVBoxLayout(left_container)
        left.setContentsMargins(4, 4, 8, 4)
        left.setSpacing(10)

        reticle_group = QGroupBox("Reticle")
        rg = QGridLayout(reticle_group)
        rg.setColumnStretch(1, 1)
        self.shapes = QComboBox()
        self.shapes.addItems(["Dot", "Cross", "Cross + Dot", "Circle", "Circle + Dot", "Tiny Ring", "Custom"])
        self.shapes.setCurrentText("Cross + Dot")
        self.shapes.currentTextChanged.connect(self.pick_shape)
        self.scale = QSpinBox()
        self.scale.setRange(1, 7)
        self.scale.setValue(2)
        self.scale.valueChanged.connect(self.sync)
        self.opacity = QSlider(Qt.Horizontal)
        self.opacity.setRange(20, 100)
        self.opacity.setValue(100)
        self.opacity.valueChanged.connect(self.sync)
        self.outline = QCheckBox("Auto contrast outline")
        self.outline.setChecked(True)
        self.outline.toggled.connect(self.sync)
        rg.addWidget(QLabel("Shape"), 0, 0)
        rg.addWidget(self.shapes, 0, 1)
        rg.addWidget(QLabel("Scale"), 1, 0)
        rg.addWidget(self.scale, 1, 1)
        rg.addWidget(QLabel("Opacity"), 2, 0)
        rg.addWidget(self.opacity, 2, 1)
        rg.addWidget(self.outline, 3, 0, 1, 2)
        left.addWidget(reticle_group)

        adaptive_group = QGroupBox("Adaptive color")
        ag = QGridLayout(adaptive_group)
        ag.setColumnStretch(1, 1)
        self.mode = QComboBox()
        self.mode.addItems(["Power Smart Contrast", "Adaptive Complement", "Adaptive B/W", "Fixed White", "Fixed Green", "Fixed Magenta"])
        self.sample = QSpinBox()
        self.sample.setRange(9, 61)
        self.sample.setSingleStep(2)
        self.sample.setValue(21)
        self.smooth = QSlider(Qt.Horizontal)
        self.smooth.setRange(0, 90)
        self.smooth.setValue(50)
        self.refresh_ms = QSpinBox()
        self.refresh_ms.setRange(16, 100)
        self.refresh_ms.setValue(35)
        self.refresh_ms.setSuffix(" ms")
        self.refresh_ms.valueChanged.connect(self._update_refresh_rate)
        self.status = QLabel("Waiting for pixels…")
        self.status.setWordWrap(True)
        self.status.setObjectName("status")
        ag.addWidget(QLabel("Mode"), 0, 0)
        ag.addWidget(self.mode, 0, 1)
        ag.addWidget(QLabel("Sample area"), 1, 0)
        ag.addWidget(self.sample, 1, 1)
        ag.addWidget(QLabel("Anti-flicker"), 2, 0)
        ag.addWidget(self.smooth, 2, 1)
        ag.addWidget(QLabel("Reaction rate"), 3, 0)
        ag.addWidget(self.refresh_ms, 3, 1)
        ag.addWidget(self.status, 4, 0, 1, 2)
        left.addWidget(adaptive_group)

        control_group = QGroupBox("Controls")
        controls = QVBoxLayout(control_group)
        self.rmb = QCheckBox("Hide while RMB is held")
        self.rmb.setChecked(True)
        self.start_hidden = QCheckBox("Start control window minimized")
        self.close_to_tray = QCheckBox("Close button minimizes to tray")
        self.close_to_tray.setChecked(True)
        controls.addWidget(self.rmb)
        controls.addWidget(self.start_hidden)
        controls.addWidget(self.close_to_tray)
        tips = QLabel("F8 = show/hide overlay\nRMB = temporary hide (optional)\nWhen the window becomes narrow, the UI stacks vertically.")
        tips.setObjectName("help")
        tips.setWordWrap(True)
        controls.addWidget(tips)
        left.addWidget(control_group)

        quick_group = QGroupBox("Quick actions")
        quick = QGridLayout(quick_group)
        center = QPushButton("Center overlay")
        center.clicked.connect(self._center_overlay)
        fast = QPushButton("Fast 16 ms")
        fast.clicked.connect(lambda: self.refresh_ms.setValue(16))
        balanced = QPushButton("Balanced 35 ms")
        balanced.clicked.connect(lambda: self.refresh_ms.setValue(35))
        smooth_button = QPushButton("Smooth 60 ms")
        smooth_button.clicked.connect(lambda: self.refresh_ms.setValue(60))
        quick.addWidget(center, 0, 0, 1, 2)
        quick.addWidget(fast, 1, 0)
        quick.addWidget(balanced, 1, 1)
        quick.addWidget(smooth_button, 2, 0, 1, 2)
        left.addWidget(quick_group)
        left.addStretch(1)

        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setFrameShape(QFrame.NoFrame)
        left_scroll.setWidget(left_container)
        left_scroll.setMinimumWidth(270)
        self.splitter.addWidget(left_scroll)

        right_container = QWidget()
        right = QVBoxLayout(right_container)
        right.setContentsMargins(8, 4, 4, 4)
        right.setSpacing(8)
        editor_title = QLabel("32 × 32 RETICLE EDITOR")
        editor_title.setObjectName("section")
        right.addWidget(editor_title)
        self.editor = core.PixelEditor()
        self.editor.setMinimumSize(280, 280)
        self.editor.changed.connect(self.editor_changed)
        right.addWidget(self.editor, 1)
        help_editor = QLabel("Left mouse = paint • Right mouse = erase")
        help_editor.setObjectName("help")
        right.addWidget(help_editor)
        buttons = QHBoxLayout()
        clear = QPushButton("Clear")
        clear.clicked.connect(lambda: self.editor.set_matrix(core.blank()))
        dot = QPushButton("Dot")
        dot.clicked.connect(lambda: self.editor.set_matrix(core.shape("Dot")))
        save = QPushButton("Save settings")
        save.clicked.connect(self.save)
        toggle = QPushButton("Show / Hide [F8]")
        toggle.clicked.connect(self.toggle)
        buttons.addWidget(clear)
        buttons.addWidget(dot)
        buttons.addStretch(1)
        buttons.addWidget(save)
        buttons.addWidget(toggle)
        right.addLayout(buttons)

        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setFrameShape(QFrame.NoFrame)
        right_scroll.setWidget(right_container)
        right_scroll.setMinimumWidth(300)
        self.splitter.addWidget(right_scroll)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)
        self.splitter.setSizes([350, 700])

        self.setStyleSheet("""
        QMainWindow,QWidget { background:#090e17; color:#e7eef8; font-family:'Segoe UI'; font-size:10pt; }
        QLabel#title { font-size:20pt; font-weight:800; color:#62dcff; }
        QLabel#subtitle,QLabel#help { color:#8492a8; font-size:9pt; }
        QLabel#section { color:#dff8ff; font-size:12pt; font-weight:700; }
        QLabel#status { color:#8ef5ac; font-family:Consolas; padding:4px; }
        QLabel#overlayOn { color:#71ff9a; font-weight:700; }
        QLabel#overlayOff { color:#ff7a8a; font-weight:700; }
        QGroupBox { border:1px solid #27344a; border-radius:9px; margin-top:12px; padding-top:12px; color:#9ce8ff; font-weight:700; }
        QGroupBox::title { subcontrol-origin:margin; left:10px; padding:0 5px; }
        QPushButton,QComboBox,QSpinBox { background:#121c2c; border:1px solid #334660; border-radius:6px; padding:6px; min-height:24px; }
        QPushButton:hover,QComboBox:focus,QSpinBox:focus { border-color:#5bd8ff; }
        QSlider::groove:horizontal { height:5px; background:#253149; border-radius:2px; }
        QSlider::handle:horizontal { background:#5bd8ff; width:14px; margin:-5px 0; border-radius:7px; }
        QScrollArea { border:none; }
        QSplitter::handle { background:#172133; }
        """)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not hasattr(self, "splitter"):
            return
        compact = self.width() < 760
        if compact != self._compact_layout:
            self._compact_layout = compact
            self.splitter.setOrientation(Qt.Vertical if compact else Qt.Horizontal)
            self.splitter.setSizes([360, 430] if compact else [350, 700])

    def _update_refresh_rate(self, value):
        if hasattr(self, "adapt"):
            self.adapt.setInterval(value)

    def _center_overlay(self):
        screen = QApplication.primaryScreen()
        if not screen:
            return
        g = screen.geometry()
        self.ov.move(g.x() + g.width() // 2 - self.ov.width() // 2, g.y() + g.height() // 2 - self.ov.height() // 2)

    def setup_tray(self):
        self.tray = None
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        icon_path = Path(__file__).with_name("crossaim_power.png")
        icon = QIcon(str(icon_path))
        self.tray = QSystemTrayIcon(icon, self)
        self.tray.setToolTip(f"CrossAim Power {VERSION}")
        menu = QMenu()
        show_action = QAction("Show CrossAim Power", self)
        show_action.triggered.connect(self._show_window)
        toggle_action = QAction("Toggle overlay", self)
        toggle_action.triggered.connect(self.toggle)
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self._quit_app)
        menu.addAction(show_action)
        menu.addAction(toggle_action)
        menu.addSeparator()
        menu.addAction(quit_action)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._tray_clicked)
        self.tray.show()

    def _tray_clicked(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self._show_window()

    def _show_window(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _quit_app(self):
        self._really_quit = True
        if self.tray:
            self.tray.hide()
        self.close()

    def toggle(self):
        super().toggle()
        if self.enabled:
            self.overlay_state.setText("● OVERLAY ON")
            self.overlay_state.setObjectName("overlayOn")
        else:
            self.overlay_state.setText("● OVERLAY OFF")
            self.overlay_state.setObjectName("overlayOff")
        self.overlay_state.style().unpolish(self.overlay_state)
        self.overlay_state.style().polish(self.overlay_state)

    def save(self):
        data = {"matrix": self.editor.matrix, "scale": self.scale.value(), "opacity": self.opacity.value(), "outline": self.outline.isChecked(), "mode": self.mode.currentText(), "sample": self.sample.value(), "smooth": self.smooth.value(), "refresh_ms": self.refresh_ms.value(), "rmb": self.rmb.isChecked(), "start_hidden": self.start_hidden.isChecked(), "close_to_tray": self.close_to_tray.isChecked()}
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
            self.sync()
        except Exception:
            self.sync()

    def closeEvent(self, event):
        self.save()
        if self._really_quit:
            self.ov.close()
            if self.sct:
                self.sct.close()
            event.accept()
            return
        if self.close_to_tray.isChecked() and self.tray:
            event.ignore()
            self.hide()
            self.tray.showMessage("CrossAim Power", "Control window minimized to tray. Overlay remains active.", QSystemTrayIcon.Information, 1800)
            return
        self.ov.close()
        if self.sct:
            self.sct.close()
        event.accept()


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
    window = ResponsiveMain()
    window.show()
    if window.start_hidden.isChecked():
        QTimer.singleShot(0, window.hide)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
