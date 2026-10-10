#!/bin/sh
# Wait until every named crew member has empty hands, draft them so no new haul starts, then dispatch.
cd "$(dirname "$0")/../.."
for i in $(seq 1 20); do
  busy=0
  for p in "$@"; do
    python .local/qa/bridge.py call rimworld/select_pawn "{\"pawnName\":\"$p\"}" >/dev/null
    if python .local/qa/bridge.py call rimworld/get_selected_pawn_inventory_state '{}' | grep -A1 '"carriedThing"' | grep -q defName; then busy=1; fi
  done
  if [ $busy -eq 0 ]; then
    for p in "$@"; do python .local/qa/bridge.py call rimworld/set_draft "{\"pawnName\":\"$p\",\"drafted\":true}" >/dev/null; done
    python .local/qa/bridge.py call rimworld/open_main_tab '{"mainTabId":"RR_Operations"}' >/dev/null
    python .local/qa/click-label.py Expedition >/dev/null
    python .local/qa/click-label.py "Approach gate and dispatch to selected coordinate"
    python .local/qa/bridge.py call rimworld/close_main_tab '{}' >/dev/null
    python .local/qa/bridge.py call rimworld/list_messages '{}' | grep -o '"text": *"[^"]*"' | tail -1
    exit 0
  fi
  python .local/qa/bridge.py call rimworld/play_for '{"durationMs":1500,"speed":"Normal"}' >/dev/null
done
echo "never empty-handed"
