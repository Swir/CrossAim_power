# CrossAim Power v1.3.1

## Smart Game Mode
- Detects supported foreground game executables, including CS2
- Uses a faster watchdog only while a known game is active
- Uses a slower desktop watchdog outside games to reduce unnecessary work

## Overlay recovery
- F9 performs a hard TOPMOST recovery without taking focus
- Game activation / Alt+Tab triggers a short 0 / 120 / 300 ms recovery sequence
- Display configuration changes trigger automatic re-centering and re-assertion
- Existing v1.3 Win32 TOPMOST watchdog remains active

## Diagnostics
- Optional compatibility log at `%APPDATA%\CrossAim_Power\diagnostics.log`
- Writes only meaningful state changes
- Automatically trims large logs
- UI button copies the diagnostics path

## Existing features retained
- Power Smart Contrast adaptive color
- Multi-zone screen analysis
- Responsive compact UI
- Reticle presets and 32×32 editor
- Multi-monitor support
- System tray
- Permanent Made by Swir + GitHub footer

## Fullscreen note
True Exclusive Fullscreen may bypass normal desktop overlays.
For CS2, Fullscreen Windowed / Borderless remains the recommended display mode.

Made by **Swir**
GitHub: https://github.com/Swir
