@echo off
REM Stop every one of them. RimWorld is left alone.
cd /d "%~dp0..\.."
python stream\services.py stop
echo.
pause
