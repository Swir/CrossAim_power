# CrossAim Power v1.3.0

## Game visibility fix
- Native Win32 TOPMOST watchdog
- Re-applies click-through / no-activate / layered overlay styles
- Re-asserts the overlay when the foreground window changes
- Keeps the overlay above borderless/fullscreen-windowed games without stealing focus
- Detects fullscreen-sized foreground windows
- Automatically follows the monitor used by a fullscreen game when enabled
- Manual "Re-assert overlay now" recovery button
- Configurable watchdog interval from 50–1000 ms

## Fullscreen note
True Exclusive Fullscreen can bypass normal desktop overlays at the Windows compositor/display level.
For CS2, use Fullscreen Windowed / Borderless if the overlay is still hidden.

## Existing features retained
- Power Smart Contrast adaptive color
- Multi-zone screen analysis
- Anti-flicker
- Responsive compact UI
- Reticle presets and 32×32 editor
- Multi-monitor support
- System tray
- Permanent Made by Swir + GitHub footer

Made by Swir
GitHub: https://github.com/Swir
