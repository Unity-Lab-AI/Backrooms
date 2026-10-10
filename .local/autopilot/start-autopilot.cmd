@echo off
rem Unity autopilot, LIVE. Start the stream stack first (Unity Plays RimWorld.cmd). See README.md.
cd /d "%~dp0..\..\"
python .local/autopilot/autopilot.py %*
