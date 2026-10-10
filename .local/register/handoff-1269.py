# -*- coding: utf-8 -*-
"""NOW.md handoff for 0.12.69-dev, written for the session after a compaction."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOW = os.path.join(REPO, "docs", "NOW.md")

OLD = u"## DO THIS FIRST — READ THE **FIRST** RED LINE, NOT THE LOUDEST ONE"

NEW = u"""## DO THIS FIRST — THE PACKAGE ID CHANGED, AND EIGHT CHECKPOINTS SHIPPED UNVERIFIED

**State: `0.12.69-dev`, staged, hash-verified, ten refs, porcelain 0.** Nothing is half-finished
and nothing is waiting on a decision.

### THE ONE THING THAT WILL CONFUSE EVERYTHING IF MISSED

**The packageId is `Rimrooms.AsyncIndustries` now.** It was `UnityLabAI.RimroomsAsyncIndustries`
until 0.12.68-dev. Owner direction: *"take the Unity Lab AI and the Unity AI Lab out of all
refrences and nameing but we will keep the repos as is for now"*, chosen at the fork as
`Rimrooms.AsyncIndustries` with the sweep covering the shipped package and the live documentation.

Consequences that are easy to trip over:

* **RimWorld sees a different mod.** The old RimSort entry is gone and a new one appears. Any save
  made before 0.12.68-dev will not find this package.
* **The staging guard refuses a folder whose packageId differs** — that is what stops it
  overwriting another mod. If it throws *"Existing folder belongs to another package"*, check the
  staged `About.xml`, and only remove the folder once you have confirmed it is our own build.
* **Dated records keep the old id on purpose.** `docs/FINALIZED.md` and
  `docs/implementation/evidence/` are receipts of what was true when written. `docs/TODO.md` keeps
  the lab's name too, because the owner's own words quote it and LAW #0 puts those in verbatim.
* **`.claude/`, the git remotes and the org are untouched**, by the owner's choice.

### WHAT IS UNVERIFIED, AND IT IS A LOT

**Thirteen launches, and the last one the owner reported on was 0.12.67-dev.** Everything since is
built, measured at the desk, and **never run**:

| Checkpoint | What has not been seen in a game |
|---|---|
| 0.12.68-dev | the braided maze, the raised graph ceiling, the new packageId |
| 0.12.69-dev | institutions on a first level, complexes up to six rooms, loot in all sixteen archetypes |

**A NEW START IS REQUIRED.** Every one of those lands on newly generated levels, and the owner has
been starting fresh each launch anyway.

### THE INSTRUMENT IS NOW THE FIRST THING TO RUN

```
python tools/check-planner-layouts.py     # checker 14: runs the planner for real
python tools/check-plant-residue.py       # checker 15: refuses while a fault is planted
```

**Checker 14 is the only one that runs code rather than reading it**, and it is what found every
generation defect in the last four checkpoints. It reports, per depth: refusals, room count,
widest span, back-to-back pairs, margin pressure, shaped-room share, rock share, **fallbacks**,
and **institutions**. Read the whole line; each column exists because something hid in it.

**Checker 15 exists because a plant suite left a deliberate fault in the source tree three
times.** `finally` handles an exception and does nothing for a killed process, so the suites write
a sentinel naming the file before they mutate it. **If you interrupt a plant sweep, run checker 15
and restore what it names.**

### THE TRAPS, AND EVERY ONE OF THEM BIT THIS SESSION

* **The machinery is not the behaviour — SEVEN times.** A claim asserting that a constant,
  a method or a variable *exists* passes while the branch that uses it is gone. `MakeHall`,
  `VariedRoomSpan`, `SpawnPillarLamps`, the margin fallback, the corridor lamps, `DiscoveryIdFor`,
  the gate toggle's refusal branch. **Assert the call site and the condition, never the
  definition.**
* **Claim scoping — FORTY instances.** A string that appears twice, or appears in a comment
  explaining its own removal. `PlaceWall(map, cell, wallDef, wallStuff)` occurs in two methods;
  `RR_GateTelemetry` occurs in the comment beside the list it was deleted from. **Scope to a
  method body, or count.**
* **An absence claim cannot read raw source.** `proof-coordinate-layout.py` keeps a comment-free
  `code()` view; `proof-generation-batch.py` strips comments.
* **A model with no source claim drifts silently.** `proof-facilities.py` carried
  `MAX_ROOMS = 4` with a comment saying it must mirror the C# exactly, and nothing checked —
  the code moved to 6 and the proof kept passing. **Every mirrored constant needs a claim that
  reads it out of the source.**
* **An anchored span is a delete.** A fix script rebuilt a proof as `text[:start] + new +
  text[end:]` and removed two claims written four minutes earlier.
* **Use the Write tool.** A bash heredoc has mangled an escape **eleven** times; the format-string
  anchors in the probe defeated it twice more this session.

### AND THE DEFECT SHAPE BEHIND ALMOST EVERYTHING

**Seven systems this week were built, correct, and switched off by a condition meant for something
else.** The archetypes, the inhabitants, the events, the shapes, the facilities — all gated on
`coordinate.Depth <= 1`. `NaturalFrontierService.Discover` had **zero callers**. A discovered gate
could never be entered because `IsLiveGate` wanted a player mark. The Backrooms could not go
deeper than two levels because a derived id outgrew a 128-character limit. Every candidate layout
was refused because `MaxRoomSpan` said 34 while the hall was 80. Every maze was refused because
the graph ceiling allowed one loop.

**So the question to ask of any feature the owner says is missing is not "is it written" but "can
it run, and is it reached".** The probe answers the first. A caller search answers the second.

### WHAT THE NEXT LAUNCH HAS TO SETTLE

1. **Refresh local mods in RimSort** — the mod has a new id and will appear as a new entry
2. **A fresh start**, any scenario; the corporate start is now playable for the first time
3. **Is it a maze** — branches, loops, dead ends, no single snaking line
4. **Institutions**: a school, a ward, an armoury, a storage complex, up to six rooms each, with
   loot in them
5. **The gate**: blue, glowing, Stargate FX, a pawn crossing; the door toggle on an ordinary door
   at the headquarters
6. **Ways onward**: blue dead-end doors offering *"Walk through"*, one world exit and one deeper
   per level, and **depth 2 reachable for the first time**

### STANDING CONSTRAINTS, UNCHANGED

* **Only the owner launches RimWorld, through RimSort.** Never alter the active mod list. Killing
  `RimWorldWin64.exe` is allowed only when staging requires it and a stage was asked for.
* **No Claude or AI attribution** in commits, PR bodies, code comments, docs or shipped artefacts.
* **Never force-push.** The cascade is **TEN refs** and the read-back is the only receipt.
* **Existing content only** — no new gameplay ThingDefs, benches, items, textures or audio.
* **Nothing is deferred.** Never add a row to `DEFERRED.md`.
* **Ask, do not flag.** *"dopnt flag shit!!! ask me then and there"*.
* **The mod register is guidance, not law**, and the check must still be stated in the record.
* **Do not stop until the owner says stop or the build is complete.**

"""

text = io.open(NOW, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(NOW, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW + OLD, 1))
print("NOW.md handoff written for the session after a compaction")
