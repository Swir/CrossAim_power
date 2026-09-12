@echo off
title CrossAim Power
py -m pip install -r requirements.txt
py make_icon.py
py crossaim_power.py
if errorlevel 1 pause
