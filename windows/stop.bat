@echo off
REM One press. Kills every one of them by name first (llama-server, ollama, obs64, RimWorldWin64), then the
REM sweep, then prints the GPU to prove the memory came back. Never touches your browsers.
cd /d "%~dp0.."
python stream\services.py stop
echo.
pause
