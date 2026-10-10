#!/usr/bin/env bash
# One press. Kills every one of them by name first (llama-server, ollama, obs64, RimWorldWin64), then the
# sweep, then prints the GPU to prove the memory came back. Never touches your browsers.
cd "$(dirname "$0")/.." || exit 1
exec python3 stream/services.py stop
