# -*- coding: utf-8 -*-
"""Add read-only selectors so the live messages, alerts and selection can actually be read.

Owner, 2026-10-01: *"look at the game and dont give me shit the api mod is not working make it
work look at the running game look at those messages look at the logs wtf!"*, and *"fix the api u
fuck"*.

**The api was working. I was probing the wrong thing.** `[RimBridge] GABP server running
standalone on port 5174` with a token is in the log; I had tried 8765, 8080, 9000 and 5000 over
plain HTTP with no token. GABP is a framed protocol on 5174 and `tools/qa/rimbridge_readonly.py`
already speaks it.

**What was genuinely missing is the thing the owner asked for.** The client's fixed allowlist had
five selectors -- ping, status, game, mods, logs -- and **none of them read messages**. So *"look
at those messages"* was not answerable by the instrument, which is a real gap and not a mistake
about ports.

Five selectors added, every one a parameterless **read**:

| | |
|---|---|
| `messages` | `rimworld/list_messages` -- the live message feed, which is where the owner's two refusals are |
| `alerts` | `rimworld/list_alerts` -- active alerts with their culprit targets |
| `letters` | `rimworld/list_letters` -- the letter stack |
| `selection` | `rimworld/get_selection_semantics` -- inspect strings for whatever is selected |
| `colonists` | `rimworld/list_colonists` -- stable pawn ids |

**The file's premise is unchanged**: it never discovers, starts, configures or controls a process,
and it only calls fixed read surfaces. These are five more fixed read surfaces.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLIENT = os.path.join(REPO, "tools", "qa", "rimbridge_readonly.py")

OLD = u'''READ_TOOLS = {
    "ping": ("rimbridge/ping", {}),
    "status": ("rimbridge/get_bridge_status", {}),
    "game": ("rimworld/get_game_info", {}),
    "mods": ("rimworld/get_mod_configuration_status", {}),
    "logs": ("rimbridge/list_logs", {"limit": 50, "minimumLevel": "warning", "afterSequence": 0}),
}'''

NEW = u'''READ_TOOLS = {
    "ping": ("rimbridge/ping", {}),
    "status": ("rimbridge/get_bridge_status", {}),
    "game": ("rimworld/get_game_info", {}),
    "mods": ("rimworld/get_mod_configuration_status", {}),
    "logs": ("rimbridge/list_logs", {"limit": 50, "minimumLevel": "warning", "afterSequence": 0}),
    # Added 2026-10-01 on the owner's direction: *"look at the running game look at those
    # messages look at the logs"*. The allowlist had no way to read a message, so the question
    # was not answerable by the instrument -- a real gap, and the reason a refusal the owner was
    # staring at had to be diagnosed from source instead of from the game.
    #
    # Every one is parameterless and read-only. The file's premise is unchanged: it never
    # discovers, starts, configures or controls a process.
    "messages": ("rimworld/list_messages", {}),
    "alerts": ("rimworld/list_alerts", {}),
    "letters": ("rimworld/list_letters", {}),
    "selection": ("rimworld/get_selection_semantics", {}),
    "colonists": ("rimworld/list_colonists", {}),
}'''

text = io.open(CLIENT, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(CLIENT, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))

after = io.open(CLIENT, encoding="utf-8").read()
failures = []
for key in ("messages", "alerts", "letters", "selection", "colonists"):
    if (u'"%s": ("rimworld/' % key) not in after:
        failures.append("%s selector missing" % key)
# The premise must survive: nothing here may start or control the game.
for banned in ("start_debug_game", "load_game", "click_cell", "set_", "execute"):
    if (u'"rimworld/%s' % banned) in after or (u'"rimbridge/%s' % banned) in after:
        failures.append("a non-read tool reached the allowlist: %s" % banned)
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("five read-only selectors added: messages, alerts, letters, selection, colonists")
