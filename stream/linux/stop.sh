#!/usr/bin/env bash
# Stop every stream service. RimWorld is left alone.
cd "$(dirname "$0")/../.." || exit 1
exec python3 stream/services.py stop
