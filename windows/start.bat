@echo off
REM One press. Brings up the whole rig: Ollama + both models (voice pre-warmed), OBS, the Twitch window,
REM the studio, the webcam, chat, the host voice, the guards, the click queue, Unity the player, and the
REM admin panel on screen. Then she ASKS: "Are we starting the stream and the game? Tell me what you want
REM tonight and hit GO." Nothing goes live and no game launches until you press GO in the panel.
cd /d "%~dp0.."
python stream\services.py start
echo.
pause
