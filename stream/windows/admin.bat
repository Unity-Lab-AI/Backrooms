@echo off
REM Open Unity mission control -- the local admin page: processes, colony, orders to the model, model chat.
REM Starts it first if it is not running, then opens the browser.
cd /d "%~dp0..\.."
python stream\services.py start >nul 2>&1
start "" http://127.0.0.1:4318/
