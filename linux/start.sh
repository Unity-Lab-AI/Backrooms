#!/usr/bin/env bash
# One press. Brings up the whole rig: Ollama + both models (voice pre-warmed), OBS, the Twitch window, the
# studio, the webcam, chat, the host voice, the guards, the click queue, Unity the player, and the admin
# panel. Then she ASKS: "Are we starting the stream and the game? Tell me what you want tonight and hit GO."
# Nothing goes live and no game launches until you press GO in the panel.
cd "$(dirname "$0")/.." || exit 1
exec python3 stream/services.py start
