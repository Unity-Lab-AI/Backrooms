#!/bin/sh
# Print the stored power line off each battery's inspect pane. The bridge's selection reader throws
# on Core batteries, so this reads the pane's own label instead.
cd "$(dirname "$0")/../.."
for c in "143 146" "145 146" "143 150" "145 150"; do
  set -- $c
  python .local/qa/bridge.py call rimworld/clear_selection '{}' >/dev/null
  python .local/qa/bridge.py call rimworld/click_cell "{\"x\":$1,\"z\":$2,\"button\":\"left\"}" >/dev/null
  echo "($1,$2) $(python .local/qa/click-label.py --list 2>&1 | grep -o 'Stored: [0-9]* / [0-9]* Wd' | head -1)"
done
python .local/qa/bridge.py call rimworld/clear_selection '{}' >/dev/null
