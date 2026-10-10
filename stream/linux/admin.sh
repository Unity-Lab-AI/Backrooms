#!/usr/bin/env bash
# Open Unity mission control -- the local admin page: processes, colony, orders to the model, model chat.
cd "$(dirname "$0")/../.." || exit 1
python3 stream/services.py start >/dev/null 2>&1
xdg-open http://127.0.0.1:4318/ 2>/dev/null || open http://127.0.0.1:4318/ 2>/dev/null
