@echo off
REM Start the whole stream: studio, webcam, Twitch chat, host voice, guards, cursor jobs, autopilot.
REM RimWorld is yours to launch -- this never touches the game.
cd /d "%~dp0..\.."
python .local\qa\services.py start
echo.
pause
