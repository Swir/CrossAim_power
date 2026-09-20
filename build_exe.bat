@echo off
title CrossAim Power v1.3.1 - Build EXE
py -m pip install -U pyinstaller
py -m pip install -r requirements.txt
if errorlevel 1 pause & exit /b 1

py make_icon.py
if errorlevel 1 pause & exit /b 1

py -m py_compile crossaim_power.py crossaim_power_v11.py crossaim_power_v12.py crossaim_power_v13.py crossaim_power_v131.py
if errorlevel 1 pause & exit /b 1

pyinstaller --noconfirm --clean --windowed --onefile ^
  --name "CrossAim_Power" ^
  --icon "crossaim_power.ico" ^
  --add-data "crossaim_power.png;." ^
  --collect-all mss ^
  crossaim_power_v131.py

echo Finished. Check dist\CrossAim_Power.exe
pause
