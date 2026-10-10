@echo off
REM Start the whole show: OBS, Twitch window, studio, webcam, chat, voice, guards, click queue,
REM the AI that plays, mission control and the local model API. RimWorld is yours to launch.
cd /d "%~dp0..\.."
python stream\services.py start
echo.
pause
