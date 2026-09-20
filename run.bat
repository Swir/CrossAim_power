@echo off
title CrossAim Power v1.3.1
py -m pip install -r requirements.txt
py make_icon.py
py crossaim_power_v131.py
if errorlevel 1 pause
