#!/usr/bin/env bash
# Restart everything EXCEPT the broadcast: OBS stays live on the BRB scene. GO switches back to Live.
cd "$(dirname "$0")/.." || exit 1
exec python3 stream/services.py restart
