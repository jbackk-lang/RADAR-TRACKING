@echo off
cd /d "%~dp0"
python web_demo.py
if errorlevel 1 pause
