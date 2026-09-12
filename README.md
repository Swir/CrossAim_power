# 🎯 CrossAim Power

**Adaptive crosshair overlay for Windows and FPS games.**

CrossAim Power is a lightweight Windows overlay with a smart color engine that analyzes the pixels around the center of the screen and selects a highly visible reticle color.

![CrossAim Power](crossaim_power.svg)

## ✨ Highlights

- 🎨 **Power Smart Contrast** — dynamic high-contrast color selection
- 🧠 **Multi-zone analysis** — checks four surrounding zones plus the full sample ring
- ⚫ Dark backgrounds favor bright reticles
- ⚪ Bright backgrounds favor dark reticles
- 🌈 Complementary color response for colored scenes
- 🛡️ Worst-zone contrast scoring for mixed backgrounds
- ✨ Automatic contrasting outline
- 🧊 Anti-flicker color hysteresis
- 🧩 Built-in **32×32 pixel reticle editor**
- 🎯 Dot, Cross, Cross + Dot, Circle, Circle + Dot and Tiny Ring shapes
- 💾 Persistent local settings
- 🖱️ Optional RMB temporary hide
- ⌨️ `F8` global show/hide
- 🪟 Click-through transparent Windows overlay

## 🚀 Quick start

### Windows Release

Download the newest build from **Releases** and run:

`CrossAim_Power.exe`

### Run from source

Requires Python 3.10+ on Windows 10/11.

```bash
py -m pip install -r requirements.txt
py make_icon.py
py crossaim_power.py
```

Or launch `run.bat`.

## 🔨 Build EXE

Run:

```text
build_exe.bat
```

The build generates the Windows icon deterministically and creates:

```text
dist\CrossAim_Power.exe
```

## 🎮 CS2

For the most reliable overlay behavior use **Fullscreen Windowed / Borderless**.

CrossAim Power is designed as a visual overlay. It does **not** read/write CS2 memory, inject DLLs, inspect player/entity data, automate aiming, compensate recoil, or automate shooting.

Third-party anti-cheat and tournament platform rules can differ, so check the current rules for the platform where you play.

## ⌨️ Controls

| Control | Action |
|---|---|
| `F8` | Show / hide overlay |
| Hold `RMB` | Temporarily hide when enabled |
| Left mouse in editor | Draw pixels |
| Right mouse in editor | Erase pixels |

## 🧠 Color modes

- **Power Smart Contrast** — recommended multi-zone mode
- Adaptive Complement
- Adaptive B/W
- Fixed White
- Fixed Green
- Fixed Magenta

## 📦 Requirements

- Windows 10 / 11
- Python 3.10+ when running from source
- PySide6
- MSS
- Pillow (icon generation)

## 🔐 Privacy

CrossAim Power runs locally and does not require an account or cloud connection.

## 📄 License

MIT License — see [LICENSE](LICENSE).

---

Made by **Swir**.
