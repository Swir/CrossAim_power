@echo off
title CrossAim Power
py -m pip install -r requirements.txt
py crossaim_power.py
if errorlevel 1 pause
