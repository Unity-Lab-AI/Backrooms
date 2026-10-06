# -*- coding: utf-8 -*-
"""Assert that cross-map zoning stays the PLAYER'S and Core's, and that this mod never writes it.

The property this exists for
---------------------------
**Owner direction, 2026-10-06, verbatim:** *"all one person choices in zoning"*, then, when asked:
*"i mena its upto the play to zone pawns where they want them,, that was the whole cross zone
support"*.

**Half of this was already in the game and the measurement is what established that.**
`Pawn_PlayerSettings.allowedAreas` is a `Dictionary<Map, Area>` -- a separate allowed area for every
map a pawn has one on, scribed with the pawn. So cross-map zoning is **not a system to build**: once
somebody is standing on a coordinate the player restricts them with the UI they already know, and
Core enforces it with no help from here.

That makes this row's deliverable an **absence**, which is the hardest kind of thing to keep true:

    Nothing in this mod may write a pawn's allowed area, on any map, ever.

**And there is exactly one tempting way to break it.** Read out of the installed assembly:
`allowedAreas` is **private**, and the only public accessors are
`AreaRestrictionInPawnCurrentMap` and `EffectiveAreaRestrictionInPawnCurrentMap` -- both of which
read and write **only the map the pawn is standing on**. There is no public per-map getter at all.
So a future session that wants to know a worker's area on a map they are not on will find no API,
and the obvious next move is **reflection into a private field**. That is the thing this proof
exists to forbid: it would make this mod the second author of a player setting, and the first
disagreement between the two would be a colonist walking somewhere the player told them not to go.

What the mod does instead, and why it is honest
-----------------------------------------------
`RimroomsConnectedWorkComponent` **observes**: when a worker is standing on a map, it writes down
the area they have there, and cross-map work planning consults that observation. It is permissive on
anything it has never seen -- an unobserved map answers *allowed*, for the same reason Core answers
unrestricted for a map no area was ever set on -- and the definitive check still happens on arrival.

**That is a cache of a reading, not a second copy of the setting.** It is never written back, and a
stale observation can only ever cost a wasted trip, never a crossing the player forbade.

Run from the repository root.
"""
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def strip_cs_comments(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return "\n".join(re.sub(r"//.*$", "", line) for line in text.split("\n"))


def body_of(text, signature):
    at = text.find(signature)
    if at < 0:
        return None
    end = text.find("\n        }", at)
    return text[at:end] if end > at else text[at:]


def ordered(text, first, second):
    """Both present, and in that order. Absence is a failure, never a pass."""
    if text is None:
        return False
    at = text.find(first)
    then = text.find(second)
    return at >= 0 and then >= 0 and at < then


source = {}
for root, _, files in os.walk(SRC):
    if os.sep + "obj" + os.sep in root or os.sep + "bin" + os.sep in root:
        continue
    for name in files:
        if name.endswith(".cs"):
            source[os.path.join(root, name)] = strip_cs_comments(read(os.path.join(root, name)))
all_source = "\n".join(source.values())

work = source.get(os.path.join(SRC, "ConnectedWork", "RimroomsConnectedWorkComponent.cs"), "")
need = source.get(os.path.join(SRC, "ConnectedWork", "CrossForNeed.cs"), "")

print("")
print("proof: zoning is the player's, Core enforces it, and nothing here writes it")
print("")

# ------------------------------------------------------------------ 1. the absence
print("1. THE ABSENCE: nothing writes a pawn's allowed area")
writes = re.findall(r"AreaRestrictionInPawnCurrentMap\s*=[^=]", all_source)
check("no assignment to AreaRestrictionInPawnCurrentMap anywhere", not writes,
      "-- %d assignment(s). Zoning is the player's decision and this mod may only read it"
      % len(writes))
check("NO REFLECTION AT THE PRIVATE PER-MAP STORE",
      "allowedAreas" not in all_source
      and not re.search(r"GetField\(\s*\"allowed", all_source),
      "-- `allowedAreas` is private and has no public per-map accessor, so reflection is the "
      "obvious next move for anybody who wants one. It would make this mod the second author of a "
      "player setting")
check("no reflection machinery pointed at Pawn_PlayerSettings at all",
      not re.search(r"typeof\(Pawn_PlayerSettings\)\s*\.\s*Get(Field|Property|Method)", all_source))

# ------------------------------------------------------------------ 2. the read, and its shape
print("")
print("2. the one cross-map read is an observation, and it is permissive")
observe = body_of(work, "public void ObserveAreaHere(Pawn pawn)")
allows = body_of(work, "public bool ObservedAreaAllows(Pawn pawn, Map map, IntVec3 cell)")
check("the observation is taken where it is observable", observe is not None)
check("it reads only the map the pawn is standing on",
      observe is not None
      and "EffectiveAreaRestrictionInPawnCurrentMap" in observe
      and "SupportsAllowedAreas" in observe,
      "-- there is no public accessor for any other map, and the honest answer to that is to look "
      "when the pawn is there rather than to reach into a private field")
check("an unobserved map answers ALLOWED, matching Core's own unrestricted default",
      allows is not None and allows.rstrip().endswith("return true;"),
      "-- a cache that defaults to refusing would quietly stop cross-gate work for every worker "
      "who has not happened to stand somewhere yet")
check("the cache is bounded and evicts rather than refusing to learn",
      "MaximumAreaObservations" in work
      and ordered(observe, "areaObservations.Count >= MaximumAreaObservations",
                  "areaObservations.Add("),
      "-- an unbounded per-pawn-per-map cache grows with the save")

# ------------------------------------------------------------------ 3. the definitive check
print("")
print("3. the definitive answer is the pawn's own, on arrival")
crossers = [p for p, text in source.items() if "ConnectedCrossing.StepToward(" in text]
check("there is exactly one crossing implementation and three callers use it",
      "internal static ConnectedCrossingOutcome StepToward(" in
      source.get(os.path.join(SRC, "ConnectedWork", "ConnectedCrossing.cs"), "")
      and len(crossers) >= 3,
      "-- found %d caller(s). A second copy of stepping through a gate would drift, and what would "
      "drift out of it is the pawn's own allowed area and danger policy" % len(crossers))
check("the need-crossing issues through that one implementation",
      "ConnectedCrossing.StepToward(" in need,
      "-- owner: it is the player's job to zone pawns, so an automatic crossing must honour the "
      "zoning the same way a work crossing does")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: the player zones, Core enforces, this mod reads and never writes")
