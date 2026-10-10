@echo off
REM Stop every stream service. RimWorld is left alone.
cd /d "%~dp0..\.."
python .local\qa\services.py stop
echo.
pause
