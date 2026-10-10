@echo off
REM One press: stop every stream service. RimWorld is left alone.
cd /d "%~dp0"
python .local\qa\services.py stop
echo.
pause
