@echo off
title CrossAim Power
py -m pip install -r requirements.txt
py make_icon.py
py crossaim_power_v12.py
if errorlevel 1 pause
