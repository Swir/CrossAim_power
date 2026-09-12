# 🎯 CrossAim Power

**Adaptive crosshair overlay for Windows and FPS games.**

CrossAim Power is a lightweight customizable crosshair overlay with a smart color engine that reacts to the pixels around the center of the screen and chooses a highly visible reticle color.

![CrossAim Power](crossaim_power.png)

## 🆕 v1.1.0

- Responsive control panel — no more overlapping widgets when the window is made smaller
- Scrollable settings and editor panels
- Automatic horizontal/vertical layout switch below 760 px
- Resizable splitter between settings and the 32×32 editor
- Windows system-tray integration
- Optional **close to tray** and **start minimized**
- Adjustable adaptive-color reaction interval (16–100 ms)
- Live **OVERLAY ON/OFF** indicator
- Improved compact-window and high-DPI behavior

## ✨ Highlights

- 🎨 **Power Smart Contrast** — dynamic color selection based on the game background
- 🧠 **Multi-zone analysis** — checks multiple regions around the aiming point
- ⚫ Dark background → bright/white reticle
- ⚪ Bright background → dark/black reticle
- 🌈 Complementary color response for colored scenes
- 🛡️ Worst-zone contrast protection
- ✨ Automatic contrasting outline
- 🧊 Anti-flicker / color hysteresis
- 🧩 Built-in 32×32 pixel crosshair editor
- 🖱️ Optional RMB temporary hide
- ⌨️ `F8` global overlay toggle
- 🪟 Click-through transparent Windows overlay

## 🚀 Quick start

Download the newest Windows build from **Releases** and run `CrossAim_Power.exe`.

To run v1.1 from source:

```bash
py -m pip install -r requirements.txt
py crossaim_power_v11.py
```

## 🎮 CS2

For the most reliable overlay behavior use **Fullscreen Windowed / Borderless**.

CrossAim Power is a visual overlay. It does **not** read/write CS2 memory, inject DLLs, inspect player/entity data, automate aiming, control recoil, or automate shooting.

Third-party anti-cheat and tournament platform rules can differ. Always check the current rules of the platform where you play.

## ⌨️ Controls

| Control | Action |
|---|---|
| `F8` | Show / hide overlay |
| Hold `RMB` | Temporarily hide (optional) |
| Tray icon | Restore controls / toggle overlay / quit |

## 🧠 Adaptive modes

**Power Smart Contrast** is the recommended mode. It evaluates multiple surrounding zones and selects a stable high-contrast color.

Other modes include Adaptive Complement, Adaptive B/W and fixed colors.

## 📦 Requirements

- Windows 10 / 11
- Python 3.10+ when running from source
- PySide6
- MSS

## 🔐 Privacy

CrossAim Power runs locally. It does not require an account or cloud connection.

## 📄 License

MIT License — see [LICENSE](LICENSE).

---

Made by **Swir**.
