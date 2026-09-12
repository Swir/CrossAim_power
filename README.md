# 🎯 CrossAim Power

**Adaptive crosshair overlay for Windows and FPS games.**

CrossAim Power is a lightweight customizable crosshair overlay with a smart color engine that reacts to the pixels around the center of the screen and chooses a highly visible reticle color.

![CrossAim Power](crossaim_power.png)

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
- 💾 Presets with JSON import/export
- 🎮 Per-game process profiles, including `cs2.exe`
- 🖱️ Optional RMB temporary hide
- ⌨️ `F8` global overlay toggle
- 🎯 Pixel-perfect X/Y positioning
- 🪟 Click-through transparent Windows overlay

## 🕹️ Built-in crosshairs

Dot • Cross • Cross + Dot • Circle • Circle + Dot • Tiny Ring • T • X • Custom

## 🚀 Quick start

### Option 1 — Release

Download the newest Windows build from **Releases** and run:

`CrossAim_Power.exe`

### Option 2 — Python

Requires Python 3.10+.

```bash
py -m pip install -r requirements.txt
py crossaim_power.py
```

Or simply launch:

```text
run.bat
```

## 🔨 Build Windows EXE

Run:

```text
build_exe.bat
```

The generated application will be:

```text
dist\CrossAim_Power.exe
```

## 🎮 CS2

For the most reliable overlay behavior use:

**Fullscreen Windowed / Borderless**

CrossAim Power is designed as a visual overlay. It does **not** read or write CS2 memory, inject DLLs, inspect player/entity data, automate aiming, control recoil, or automate shooting.

Third-party anti-cheat and tournament platform rules can differ. Always check the current rules of the platform where you play.

## ⌨️ Controls

| Control | Action |
|---|---|
| `F8` | Show / hide overlay |
| Hold `RMB` | Temporarily hide (optional) |
| `Ctrl + Alt + Arrow` | Move by 1 pixel |
| `Ctrl + Alt + Shift + Arrow` | Move by 10 pixels |

## 🧠 Adaptive modes

**Power Smart Contrast** is the recommended mode. It evaluates multiple surrounding zones and selects a stable high-contrast color.

Other modes:

- Adaptive Complement
- Adaptive B/W
- Adaptive Invert
- Fixed color

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
