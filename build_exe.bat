@echo off
title CrossAim Power v1.2.0 - Build EXE
py -m pip install -U pyinstaller
py -m pip install -r requirements.txt
if errorlevel 1 pause & exit /b 1

py make_icon.py
if errorlevel 1 pause & exit /b 1

pyinstaller --noconfirm --clean --windowed --onefile ^
  --name "CrossAim_Power" ^
  --icon "crossaim_power.ico" ^
  --add-data "crossaim_power.png;." ^
  --collect-all mss ^
  crossaim_power_v12.py

echo Finished. Check dist\CrossAim_Power.exe
pause
