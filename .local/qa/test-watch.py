#!/usr/bin/env python3
"""Watch the live game through RimBridge and journal everything new, so the owner just plays.

Owner direction, 2026-10-06, verbatim:

    "you are gooing toi monitor the rimbridge and do the work of checking off whats comes and
     passes as i cant read 100 tasks then game them out and tell you to check em constantly"

**The owner must never be asked to hold the list in their head.** So this runs unattended beside a
session, captures what the game says, and writes it to an append-only journal with a timestamp and a
game tick on every record. Nothing is lost between a thing happening and somebody getting round to
reading it, and the owner reports nothing.

## What it is allowed to do, and the line it does not cross

**Read-only, and enforced here rather than trusted.** `READ_ONLY` is the same fixed set the shipped
client `tools/qa/rimbridge_readonly.py` carries, and `call()` refuses any name outside it. No tool
is discovered, no argument comes from outside this file, and nothing is ever written to the game.

**It does discover the port, the token and the process**, which the shipped client deliberately
refuses to do -- that tool's whole premise is that the caller supplies them. This one is the
`.local/` scratch counterpart the owner already sanctioned for live inspection
(*"you can use the api mod you have that we installed last so u can see wtf rimworld is doing"*,
2026-09-30), and it reuses `bridge.py`'s own `endpoint` and `exchange` rather than copying them.

## Why it dedupes by content hash rather than by id

The schema of a letter or a message is the bridge's, not ours, and an id field that exists today may
not tomorrow. Hashing the record's canonical JSON needs no schema at all and cannot silently stop
deduping when a field is renamed -- it would over-report rather than under-report, which is the safe
direction for an evidence journal.

## Reconnecting is the normal case, not an error

A session ends, the owner reloads, RimWorld restarts. The watcher drops back to waiting and
re-reads the endpoint, because the port and token change per launch. **A stale endpoint in the log
is the trap**: `Player.log` keeps every line a session wrote, so the last pair in the file may
belong to a game that is gone. Liveness is proved by `rimbridge/ping` answering, never by the log
having a line in it.

Usage
-----
    python .local/qa/test-watch.py                 # watch until interrupted
    python .local/qa/test-watch.py --once          # a single sweep, for checking it works
    python .local/qa/test-watch.py --every 20      # seconds between sweeps (default 15)
    python .local/qa/test-watch.py --digest        # print what the journal already holds
"""
import argparse
import hashlib
import importlib.util
import io
import json
import os
import socket
import sys
import time
import uuid
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
EVIDENCE = os.path.join(HERE, "evidence")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_spec = importlib.util.spec_from_file_location("rr_bridge", os.path.join(HERE, "bridge.py"))
_bridge = importlib.util.module_from_spec(_spec)
sys.modules["rr_bridge"] = _bridge
_spec.loader.exec_module(_bridge)

# The shipped client's fixed set, repeated here so this file can refuse anything else without
# importing a module that insists on command-line arguments it has no reason to need.
#
# `logs` asks for warnings and worse. A sweep that pulled every log line would bury the one red
# error that matters under a thousand informational ones, and the point of this journal is that
# somebody can read it.
READ_ONLY = {
    "ping": ("rimbridge/ping", {}),
    "status": ("rimbridge/get_bridge_status", {}),
    "game": ("rimworld/get_game_info", {}),
    "mods": ("rimworld/get_mod_configuration_status", {}),
    "logs": ("rimbridge/list_logs", {"limit": 200, "minimumLevel": "warning", "afterSequence": 0}),
    "messages": ("rimworld/list_messages", {}),
    "alerts": ("rimworld/list_alerts", {}),
    "letters": ("rimworld/list_letters", {}),
    "colonists": ("rimworld/list_colonists", {}),
    "camera": ("rimworld/get_camera_state", {}),
    "selection": ("rimworld/get_selection_semantics", {}),
}

# **`maps` IS GONE FROM THIS LIST BECAUSE THE TOOL DOES NOT EXIST.** The live bridge answers
# `rimworld/list_maps` with *"Tool 'rimworld/list_maps' not found"*, and the first real session
# recorded that failure **fifty times**. It is still named in `tools/qa/rimbridge_readonly.py`'s
# own `READ_TOOLS`, which is a separate correction to make there rather than silently here.
# `get_game_info` already reports `mapCount`, which is what the selector was wanted for.

# Swept every time, in this order. `ping` first so a dead bridge costs one call instead of eleven.
SWEEP = ("ping", "game", "letters", "messages", "alerts", "logs", "colonists")

# These answer a question about *now* rather than about something that happened, so journaling every
# sweep of them would be noise. Collected once per connection instead.
ONCE_PER_SESSION = ("status", "mods")

# Sets whose members are events worth keeping one record each. Anything else is a state snapshot.
EVENTFUL = ("letters", "messages", "alerts", "logs")

# **NEVER JOURNALLED, ONLY READ, AND THE FIRST SESSION IS WHY.** It produced **263 records for one
# genuinely new game event.** `ping` carries a timestamp, `game` carries a tick and `colonists`
# carries fresh operation ids, so each differs on every sweep and the change-detector dutifully
# wrote all three down forty-nine times each. **A journal nobody can read is the same failure as a
# note nobody believes** -- the one real letter was buried under two hundred records of nothing
# happening.
#
# They are still *called*: `ping` proves the bridge is alive and `game` supplies the tick stamped on
# every other record. They simply stop being evidence of their own.
NEVER_JOURNALLED = ("ping", "game", "colonists")

# A payload that says there is no game is the **absence** of evidence, not evidence. Eleven of the
# first session's records were `"No game is currently loaded"` from the menu, which is exactly the
# kind of thing that makes somebody stop reading a journal.
NO_GAME = "no game is currently loaded"


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def journal_path():
    if not os.path.isdir(EVIDENCE):
        os.makedirs(EVIDENCE)
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    return os.path.join(EVIDENCE, "watch-%s.jsonl" % day)


# **THE FIELDS THAT MAKE EVERY SWEEP LOOK NEW.** A letter carries `ageTicks` and `alpha` that move
# every tick; a log entry carries a unique `EntryId` and `Sequence` per occurrence; every payload
# carries an `operation` block with a fresh id and timestamps.
#
# ## HASHING THE WHOLE PAYLOAD WAS WRONG, AND THE FIRST SESSION PROVED IT
#
# This file argued that a content hash "needs no schema at all and cannot silently stop deduping",
# and that over-reporting was "the safe direction for an evidence journal". **The second claim is
# what failed.** The same letter -- *"Branch authorization received"* -- was journalled **three
# times**, and five log messages were journalled **two hundred times** because each occurrence
# carried its own EntryId. Over-reporting does not merely cost space: it buries the one event that
# mattered, which is the same failure as not recording it.
#
# So a little schema knowledge is used after all, as a **removal** list rather than a keep list: a
# field named here is dropped before hashing, and anything the bridge adds later is still included
# by default. A renamed volatile field goes back to over-reporting rather than to silence.
# **AND THE FIRST FIX OF THIS LIST WAS INCOMPLETE, WHICH THE MEASUREMENT CAUGHT.** Stripping
# `EntryId` and `Sequence` fixed the letters -- three records became one -- and left the logs at
# **two hundred**, because a log entry also carries `TimestampUtc`, `FirstSeenAtUtc` and the whole
# bridge operation-id family, each unique per request. Five distinct error messages were being
# recorded a hundred and twenty-one times each. Found by diffing two records that shared a Message
# and printing the fields that differed, rather than by guessing at a second field.
VOLATILE = frozenset((
    "operation", "ageTicks", "alpha", "startingFrame", "startingTick", "expired",
    "EntryId", "Sequence", "timestamp", "StartedAtUtc", "CompletedAtUtc", "DurationMs",
    "TimestampUtc", "FirstSeenAtUtc", "RepeatCount",
    "OperationId", "ParentOperationId", "RootOperationId", "CapabilityId",
    "ScriptCall", "ScriptStatementId", "ScriptStepId",
))


def stable(value):
    """`value` with volatile fields removed, recursively."""
    if isinstance(value, dict):
        return dict((k, stable(v)) for k, v in value.items() if k not in VOLATILE)
    if isinstance(value, list):
        return [stable(v) for v in value]
    return value


def digest_of(record):
    """A fingerprint of what an item *says*, not of when it was observed."""
    blob = json.dumps(stable(record), sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def seen_digests():
    """Every fingerprint already journalled today, so a restart does not re-report a session."""
    found = set()
    path = journal_path()
    if not os.path.isfile(path):
        return found
    with io.open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                found.add(json.loads(line).get("digest"))
            except ValueError:
                continue        # A half-written final line after a kill is not a reason to stop.
    found.discard(None)
    return found


def append(records):
    if not records:
        return
    with io.open(journal_path(), "a", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


def call(sock, buf, selector):
    """One allowlisted read. Refuses anything not in READ_ONLY, by name, before sending."""
    if selector not in READ_ONLY:
        raise SystemExit("refused: %r is not an allowlisted read-only selector" % selector)
    name, arguments = READ_ONLY[selector]
    return _bridge.exchange(sock, buf, "tools/call", {"name": name, "arguments": arguments})


def items_of(payload):
    """The list inside a bridge result, whatever the wrapper happens to be called."""
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return [payload]
    for key in ("letters", "messages", "alerts", "logs", "entries", "items", "results"):
        value = payload.get(key)
        if isinstance(value, list):
            return value
    # A dict with no list in it is one observation, not a collection of none.
    return [payload]


def tick_of(game):
    if isinstance(game, dict):
        for key in ("ticksGame", "ticks", "tickCount", "gameTicks"):
            if isinstance(game.get(key), int):
                return game[key]
        inner = game.get("game") if isinstance(game.get("game"), dict) else None
        if inner:
            return tick_of(inner)
    return None


def connect():
    """(socket, buffer) on a bridge that actually answers, or None.

    **Liveness is proved by the handshake, never by the log having a line in it.** `Player.log`
    keeps every line every session wrote, so the last port and token in it may belong to a game that
    has been closed for hours -- which is exactly what a connection-refused error looks like.
    """
    try:
        port, token = _bridge.endpoint()
    except SystemExit:
        return None
    try:
        sock = socket.create_connection(("127.0.0.1", port), timeout=_bridge.TIMEOUT)
    except OSError:
        return None
    sock.settimeout(_bridge.TIMEOUT)
    buf = bytearray()
    try:
        _bridge.exchange(sock, buf, "session/hello",
                         {"token": token, "bridgeVersion": "RimroomsTestWatch/1",
                          "platform": "windows", "launchId": str(uuid.uuid4())})
    except (SystemExit, OSError):
        sock.close()
        return None
    return sock, buf


def sweep(sock, buf, seen, selectors=SWEEP):
    """One pass. Returns (new records, a short human line per record)."""
    stamped = utc_now()
    game = None
    records = []
    lines = []
    for selector in selectors:
        try:
            payload = call(sock, buf, selector)
        except (SystemExit, OSError) as error:
            # One failing read must not end a session. It is journalled as a fault, because a
            # selector that stops answering mid-session is itself evidence.
            records.append({"at": stamped, "kind": "read-failed", "selector": selector,
                            "detail": str(error)[:300], "digest": digest_of([selector, str(error)])})
            continue
        if selector == "game":
            game = payload
        tick = tick_of(game)
        if selector in NEVER_JOURNALLED:
            continue
        if selector in EVENTFUL:
            for item in items_of(payload):
                if no_game(item):
                    continue
                mark = digest_of([selector, item])
                if mark in seen:
                    continue
                seen.add(mark)
                records.append({"at": stamped, "tick": tick, "kind": selector,
                                "item": item, "digest": mark})
                lines.append("%-9s %s" % (selector, summarise(item)))
        else:
            if no_game(payload):
                continue
            mark = digest_of([selector, payload])
            if mark in seen:
                continue
            seen.add(mark)
            records.append({"at": stamped, "tick": tick, "kind": selector,
                            "item": payload, "digest": mark})
            lines.append("%-9s changed" % selector)
    return records, lines


def no_game(item):
    """Whether a payload is the bridge saying there is nothing loaded to ask about.

    Matched on the message text rather than on `success`, because a `success: false` can also mean a
    real refusal worth keeping, and losing those would be the opposite mistake.
    """
    if not isinstance(item, dict):
        return False
    message = item.get("message")
    return isinstance(message, str) and NO_GAME in message.lower()


def summarise(item):
    """One readable line for a journalled item, without guessing at a schema."""
    if not isinstance(item, dict):
        return str(item)[:160]
    for key in ("label", "text", "message", "title", "name", "defName"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            extra = item.get("level") or item.get("type") or ""
            return ("[%s] " % extra if extra else "") + value.strip()[:150]
    return json.dumps(item, ensure_ascii=False, default=str)[:160]


def print_digest():
    path = journal_path()
    if not os.path.isfile(path):
        print("no journal for today at %s" % os.path.relpath(path, REPO))
        return 0
    counts = {}
    total = 0
    with io.open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except ValueError:
                continue
            counts[record.get("kind", "?")] = counts.get(record.get("kind", "?"), 0) + 1
            total += 1
    print("journal: %s" % os.path.relpath(path, REPO))
    print("records: %d" % total)
    for kind in sorted(counts, key=lambda k: -counts[k]):
        print("  %-12s %d" % (kind, counts[kind]))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--once", action="store_true", help="one sweep, then stop")
    parser.add_argument("--every", type=float, default=15.0,
                        help="seconds between sweeps while connected (default 15)")
    parser.add_argument("--digest", action="store_true", help="summarise today's journal and stop")
    args = parser.parse_args(argv)

    if args.digest:
        return print_digest()
    if not 2.0 <= args.every <= 600.0:
        parser.error("--every must be between 2 and 600 seconds")

    seen = seen_digests()
    print("test-watch: journal %s" % os.path.relpath(journal_path(), REPO))
    print("test-watch: %d record(s) already captured today" % len(seen))
    connection = None
    greeted = False
    try:
        while True:
            if connection is None:
                connection = connect()
                if connection is None:
                    if args.once:
                        print("test-watch: no live bridge. Launch the game and run this again.")
                        return 1
                    print("test-watch: waiting for a live bridge ...")
                    time.sleep(max(args.every, 10.0))
                    continue
                greeted = False
                print("test-watch: attached to a live bridge at %s" % utc_now())
            sock, buf = connection
            if not greeted:
                records, lines = sweep(sock, buf, seen, ONCE_PER_SESSION)
                append(records)
                greeted = True
            records, lines = sweep(sock, buf, seen)
            append(records)
            for line in lines:
                print("  %s" % line)
            # A ping that stops answering is how a closed game shows up here.
            if any(r.get("kind") == "read-failed" and r.get("selector") == "ping"
                   for r in records):
                print("test-watch: the bridge stopped answering; waiting for the next launch")
                try:
                    sock.close()
                except OSError:
                    pass
                connection = None
                continue
            if args.once:
                print("test-watch: one sweep done, %d new record(s)" % len(records))
                return 0
            time.sleep(args.every)
    except KeyboardInterrupt:
        print("")
        print("test-watch: stopped. Journal kept at %s"
              % os.path.relpath(journal_path(), REPO))
        return 0


if __name__ == "__main__":
    sys.exit(main())
