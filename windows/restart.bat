@echo off
REM Restart everything EXCEPT the broadcast: OBS stays live on the BRB scene, so viewers never see a
REM network error. She asks Ready? again; GO switches the stream back to Live.
cd /d "%~dp0.."
python stream\services.py restart
echo.
pause
