@echo off
title CrossAim Power v1.3.0
py -m pip install -r requirements.txt
py make_icon.py
py crossaim_power_v13.py
if errorlevel 1 pause
