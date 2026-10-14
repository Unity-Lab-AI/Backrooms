#!/bin/bash
# Wakes the session when a voice-pipeline job finishes or stalls. Exits (and so notifies) on the first event.
# usage: voice-watch.sh <progress-file> <report-file> <log-file> <label>
P="$1"; R="$2"; L="$3"; LABEL="$4"
last=-1; same=0
while true; do
  if [ -f "$R" ]; then echo "$LABEL FINISHED: $R"; exit 0; fi
  if grep -aqE "Traceback|pass failed|CUDA out of memory" "$L" 2>/dev/null && ! grep -aq "all passes done" "$L"; then
    tail -c 1500 "$L" | grep -av "it/s" | tail -12; echo "$LABEL ERROR (see $L)"; exit 2
  fi
  n=$(wc -l < "$P" 2>/dev/null || echo 0)
  if [ "$n" = "$last" ]; then same=$((same+1)); else same=0; last=$n; fi
  if [ $same -ge 10 ]; then echo "$LABEL STALLED at $n rows for 20 min (no new progress)"; exit 3; fi
  sleep 120
done
