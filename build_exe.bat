@echo off
title CrossAim Power - Build EXE
echo Installing build dependencies...
py -m pip install -U pyinstaller
py -m pip install -r requirements.txt
if errorlevel 1 pause & exit /b 1

echo.
echo Preparing CrossAim Power icon...
py make_icon.py
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
