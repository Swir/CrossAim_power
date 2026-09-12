@echo off
title CrossAim Power - Build EXE
echo Installing build dependencies...
py -m pip install -U pyinstaller PySide6 mss pillow
if errorlevel 1 pause & exit /b 1

echo.
echo Preparing Windows icon...
py -c "from PIL import Image; Image.open('crossaim_power.png').save('crossaim_power.ico', sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])"
if errorlevel 1 pause & exit /b 1

echo.
echo Building CrossAim Power...
pyinstaller --noconfirm --clean --windowed --onefile ^
  --name "CrossAim_Power" ^
  --icon "crossaim_power.ico" ^
  --add-data "crossaim_power.png;." ^
  --collect-all mss ^
  crossaim_power.py

echo.
echo Finished. Check dist\CrossAim_Power.exe
pause
