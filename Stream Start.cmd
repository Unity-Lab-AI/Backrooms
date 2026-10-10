@echo off
REM One press: start the whole stream stack (studio, face, twitch, host, guards, cursor jobs, autopilot).
REM RimWorld itself is yours to launch -- this never touches the game.
cd /d "%~dp0"
python .local\qa\services.py start
echo.
pause
