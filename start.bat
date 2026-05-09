@echo off
chcp 65001 >nul
title 小问悬浮窗
start /min pythonw "%~dp0copaw_floater.py"
exit
