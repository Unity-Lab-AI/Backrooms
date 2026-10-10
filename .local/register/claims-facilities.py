# -*- coding: utf-8 -*-
"""The facilities proof is a model with no source claims, and it drifted silently.

`proof-facilities.py` mirrors `FacilityPlanner` in Python -- `MAX_ROOMS = 4`,
`ELIGIBLE_SHARE = 0.45`, with a comment saying it *"must mirror FacilityPlanner.EligibleShare
exactly"*. **Nothing checked that it did.** The C# moved to 6 and 0.6 and the proof kept passing,
asserting bounds of 2 to 4 against its own copy of a number the code no longer used.

`proof-coordinate-layout.py` already learned this lesson and wrote it down: *"Every modelled
formula is therefore paired with a source claim that the step still exists in the C#. The model
asserts the property; the source claim asserts the code still computes it. One without the other
is exactly the mention-versus-assertion defect this project keeps meeting."* This proof had the
model and none of the claims.

So the constants are brought into step **and read out of the source**, the depth gate's removal is
claimed, and the loot sweep is claimed -- every archetype holding something worth carrying out,
which is the owner's *"need loot inside of them too"*.
"""
import io
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-facilities.py")

# 1. The model is brought into step with the code it mirrors.
MODEL = [
    (u"MAX_ROOMS = 4", u"MAX_ROOMS = 6"),
    (u"ELIGIBLE_SHARE = 0.45  # must mirror FacilityPlanner.EligibleShare exactly",
     u"ELIGIBLE_SHARE = 0.6  # mirrors FacilityPlanner.EligibleShare -- CHECKED below, not assumed"),
]

# 2. And the claims that make the mirror honest, plus the two features.
CLAIMS = u'''
# --------------------------------------------------------------------------- source claims
# **THE MODEL ABOVE HAD NO SOURCE CLAIMS AND DRIFTED.** It carried `MAX_ROOMS = 4` and
# `ELIGIBLE_SHARE = 0.45` with a comment saying they must mirror the C# exactly, and nothing
# checked that they did -- so when the planner moved to 6 and 0.6 this proof kept passing while
# asserting bounds the code no longer used. `proof-coordinate-layout.py` already wrote the rule
# down: the model asserts the property, a source claim asserts the code still computes it, and
# one without the other is the mention-versus-assertion defect.
import io as _io
import os as _os

_REPO = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))


def _read(*parts):
    return _io.open(_os.path.join(_REPO, *parts), encoding="utf-8-sig").read()


facility_source = _read("src", "RimroomsAsyncIndustries", "Generation", "FacilityPlanner.cs")
archetype_source = _read("Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                         "RimroomsRoomArchetypeDefs", "RR_RoomArchetypes.xml")

_failures = []


def _claim(label, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", label, detail if not condition else ""))
    if not condition:
        _failures.append(label)


print("")
print("source claims -- the model above is only worth its agreement with these")

_claim("THE MODELLED BOUNDS ARE THE CODE'S BOUNDS",
       ("private const int MinRooms = %d;" % MIN_ROOMS) in facility_source
       and ("private const int MaxRooms = %d;" % MAX_ROOMS) in facility_source
       and ("private const float EligibleShare = %gf;" % ELIGIBLE_SHARE) in facility_source,
       "-- read out of FacilityPlanner.cs rather than trusted. This proof asserted 2-4 against "
       "its own copy while the code said 2-6, and passed")

# Owner: *"facilitys and buildings and neighboorhoods and complexes and shools and hospitals and
# military and storages need loot inside of them too"*. `Anchors` opened with
# `coordinate.Depth <= 1` and returned null, so a FIRST LEVEL HAD NO INSTITUTIONS AT ALL -- the
# fourth system found gated on the coordinate's own depth rather than on distance from the
# arrival.
_claim("INSTITUTIONS REACH A FIRST LEVEL",
       "if (coordinate == null || coordinate.Rooms == null) { return null; }" in facility_source
       and "coordinate.Depth <= 1) { return null; }" not in facility_source,
       "-- the global depth gate is GONE, not bypassed")

_claim("and the arrival still stays sparse, measured per room",
       "RoomArchetypeService.EffectiveDepth(coordinate, room, coordinate.Depth) <= 1"
       in facility_source,
       "-- the property the gate protected is kept and measured per room, by the SAME function "
       "the archetypes, the inhabitants, the events and the wall materials all read. A room the "
       "dressing treats as deep and the facility planner treats as shallow cannot exist")

# Owner: *"...need loot inside of them too"*. Four of the sixteen archetypes carried none.
_blocks = archetype_source.split("<RimroomsAsyncIndustries.Generation.RimroomsRoomArchetypeDef>")[1:]
_without = []
for _block in _blocks:
    _name = re.search(r"<defName>(.*?)</defName>", _block)
    if _name is None:
        continue
    if "<category>" not in _block:
        _without.append(_name.group(1))

_claim("EVERY ARCHETYPE HOLDS SOMETHING WORTH CARRYING OUT",
       len(_blocks) >= 16 and not _without,
       "-- %d archetype(s) carry no loot at all: %s. The office, the nursery, the gallery and the "
       "duplicate were the four" % (len(_without), ", ".join(_without) or "none"))

if _failures:
    print("")
    print("PROOF FAILED: %d source claim(s)" % len(_failures))
    raise SystemExit(1)
'''

text = io.open(PROOF, encoding="utf-8").read()
problems = []
for old, _ in MODEL:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:52]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in MODEL:
    text = text.replace(old, new, 1)

if u"import re" not in text:
    text = text.replace(u"import math", u"import math\nimport re", 1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text + CLAIMS)
print("the model is in step with the code, and four source claims now hold it there")
