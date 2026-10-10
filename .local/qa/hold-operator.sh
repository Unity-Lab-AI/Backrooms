#!/bin/sh
# Play N slices; after each, put Gee back on the console if he wandered. Stops on letters/modals via play.py.
n=$1; gate_x=$2; gate_z=$3
for i in $(seq 1 $n); do
  out=$(python .local/qa/play.py 1); echo "$out" | grep -v "^done"
  case "$out" in *STOP*) exit 0;; esac
  j=$(python .local/qa/bridge.py call rimworld/list_colonists '{}' | grep -oE '"(name|job)": "[^"]*"' | paste - - | tr '\n' ' ')
  case "$j" in *'"Gee"	"job": "RR_OperateGate"'*|*'"Gee"	"job": "Ingest"'*) ;; *) echo "restaff: $j" | cut -c1-200; m=$(python .local/qa/bridge.py call rimworld/play_for "{\"durationMs\":100}" | grep -oE "Map_[0-9]+" | head -1); [ "$m" != "Map_0" ] && { python .local/qa/hands.py 635 30 >/dev/null; python .local/qa/hands.py 635 30 >/dev/null; }; python .local/qa/door-gizmo.py $gate_x $gate_z "Staff gate console" >/dev/null;; esac
done
python .local/qa/bridge.py call rimworld/list_colonists '{}' | grep -oE '"(name|job)": "[^"]*"' | paste - - | tr '\n' ' '; echo
