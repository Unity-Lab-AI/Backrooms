#!/usr/bin/env bash
# Open Unity mission control -- the local admin page: processes, colony, Ready?/GO, orders to the model,
# chat straight to her. Starts the rig first if it is not running, then opens the browser.
cd "$(dirname "$0")/.." || exit 1
python3 stream/services.py start >/dev/null 2>&1
xdg-open http://127.0.0.1:4318/ 2>/dev/null || open http://127.0.0.1:4318/ 2>/dev/null
