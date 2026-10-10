#!/usr/bin/env bash
# Start the whole stream: studio, webcam, Twitch chat, host voice, guards, cursor jobs, autopilot.
# RimWorld is yours to launch -- this never touches the game.
cd "$(dirname "$0")/../.." || exit 1
exec python3 stream/services.py start
