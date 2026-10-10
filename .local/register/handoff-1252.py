# -*- coding: utf-8 -*-
"""NOW.md handoff for 0.12.52-dev, written for a compaction.

Every anchor asserted before anything is written, one write at the end -- a replace that throws
part way loses the edits before it silently.

Measured rather than carried:

    branch       feature/bug-testing   (the cascade is TEN refs)
    published    1b16b6e  0.12.52-dev
    C# files     200
    package       91
    checkers      13
    proofs        41
    assembly     9D7DCDAF...ED7DF4, read from the live build after the determinism run
    launches     FIVE, eleven defects, all ours, no mod conflicts
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "docs", "NOW.md")

original = io.open(PATH, encoding="utf-8").read()

EDITS = [
    # ------------------------------------------------------------------ the heredoc rule
    (u"""**Use a FILE for any script with escapes or apostrophes, never a bash heredoc.** It mangled
`\\n` into real newlines **five times** in the 0.12.46-dev batch alone, each time producing a
Python syntax error in a proof or plant file that then had to be repaired. It is written down
here because writing it down has not yet been enough.""",
     u"""**Use a FILE for any script with escapes or apostrophes, never a bash heredoc.** It mangled
`\\n` into real newlines **five times** in the 0.12.46-dev batch, and then **three more times**
across 0.12.49 to 0.12.51 — once on a plain apostrophe in a closure script, twice on `\\\\s` inside
a regex. **Eight times in two days.** It is written down here because writing it down has not yet
been enough; the only thing that has worked is reaching for the Write tool first."""),

    # ------------------------------------------------------------------ the proof count
    (u"| Proofs | **FORTY** in `.local/register/proof-*.py`.",
     u"| Proofs | **FORTY-ONE** in `.local/register/proof-*.py`, and **THIRTEEN** plant suites in "
     u"`plant-*.py`. **Both are tracked in git now** — see *What the collaborator gets* — after "
     u"`.local/` was found to be hiding the entire verification suite from a clone."),

    # ------------------------------------------------------------------ the launch row
    (u"| Game launches | **FIVE, all by the owner on 2026-09-30.**",
     u"| Game launches | **FIVE, all by the owner on 2026-09-30, and a SIXTH is in flight right "
     u"now — reading its log is the first job of the next session.**"),

    # ------------------------------------------------------------------ the first instruction
    (u"## DO THIS FIRST — read the play-testing log, then launch again",
     u"""## DO THIS FIRST — READ THE LOG FROM THE SIXTH LAUNCH

**The owner is testing 0.12.52-dev right now and asked for exactly this:** *"you can check the
player.log on the other side of the compact to see if it works and our gates are working"*.

```
grep -n -i "rimrooms\\|Error in GenStep\\|Exception" \\
  "$USERPROFILE/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log"
```

**And the bridge, if the process is still up**, which answers in one call what the log only hints
at — see *The bridge is available now*. `.local/qa/bridge.py` is the scratch client:
`list`, `call <tool> '<json>'`, `scan <minx> <minz> <maxx> <maxz>`.

### What is actually verified, and what is not — be honest about this

The owner asked *"they work now right?"* and the answer given was **no, and I will not claim it**.
That split still holds and the next session must not quietly upgrade it:

| | |
|---|---|
| **Measured in the running game** | the Store's back-room **door exists** at (160, 161) carrying the emergence comp with `Mark as way home` enabled; Deconstruct and Uninstall both offered; a granite-block wall where the burn removed a Granite formation; `list_colonists` non-zero after the arrival fix |
| **Source-verified only, NEVER EXECUTED** | the light-count fix, the **entire 300x300 generator**, pillars, room shapes, corridor widths, the map budget, release, carry-a-doorway, and the material split. **Forty-one proofs check properties of code, not behaviour of a running game.** |

**Nothing from 0.12.48-dev onward has run once.** The coordinate generator in particular was
rewritten from a hard-coded 3x3 grid to a depth-driven one and has never executed.

**The one thing de-risked without a launch:** `CandidateIsSafe` was modelled against the new
layouts at **every depth across six seeds** — every room reachable, zero failures — so generation
should be *accepted* rather than refused with `RR_Generation_NoSafeCandidate`. That was the
likeliest silent killer. It is not proof that it runs.

### The two gates are completely different things, and only one should exist yet

**The natural gate** is the one to check first, and the chain that has to hold is:

```
SoloGroupOpening.Open
  1. CreateDiscoveredCoordinate      mint the place
  2. DestinationService.EnsureSite   GENERATE THE 300x300 MAP   <- failed at launch 5
  3. CompRimroomsEmergence.Mark()    mark the Store's back door
  4. RegisterNaturalAddress          register the connection
```

Step 2 failed on the fifth launch for the light-count reason, so **steps 3 and 4 have never run.**
If the back-room door is still an ordinary steel door, step 2 failed again and the log names the
key. Look for `RR_Event_NaturalGateOpening`.

**The machine gate is NOT there and is not supposed to be.** Owner, verbatim: *"the store start
has a natural portal and to build a machanical one they need to contact the company and resaerch
whats needed"*. The Store ships `Battery`, `CommsConsole` and `WoodFiredGenerator` — **no Autodoor
and no TableMachining.** So the player must build a Machining Table and an Autodoor, designate
door/console/battery/bench on Operations' **Machine** pane, then run `RR_AssembleMachineGate`:
**100 Steel + 8 ComponentIndustrial, 6000 work, Crafting**, no research prerequisite on the recipe
itself. The setup page's readiness review already names the missing hardware.

### What the sixth launch should settle, in order

1. **does a coordinate generate at all** — the whole generator is unrun
2. **is the back-room door a natural gate** rather than a steel door
3. **level 0 reads as the yellow rooms** — wood walls, yellow carpet, coherent, everything matching
4. **one level in, the materials go wild** — two tables in one room in different stuffs, each room's
   walls a different material. This is the newest thing and the least like anything that has run
5. **no cave-in** when a wall or a pillar is deconstructed
6. **Operations → Places** lists the colony and any level, with the budget as `n/5`

---

## The re-stage command and the old fifth-launch list"""),

    # ------------------------------------------------------------------ the lesson block
    (u"### The rules that come out of it",
     u"""### THE TRAP THAT NOW OUTRANKS EVERY OTHER ONE

**A claim satisfiable by something other than the thing it is about.** It has defeated a proof
claim **in every single checkpoint from 0.12.46 to 0.12.52**, and the plants caught all of them.
The full list, because the shape is only obvious once it is in a table:

| What the claim read | Why a plant walked past it |
|---|---|
| `"Prefs.MaxNumberOfPlayerSettlements" in budget` | the name is also in the **doc comment** above the code |
| `"RR_Frontier_TooManyGatesHeld" in keyed` | it is a **prefix** of `…HeldUnused` |
| `"MaximumFrontiersPerCoordinate" in frontier` | the **declaration** survived while the *use* was deleted |
| `"return false;" in parent` | that shape appears **four times** in the file |
| `"if (x == center.x …)" in planner` | a later feature added the **same line** to a second function, and the harness replaces only the first |
| `genstep.count("RockIntrusionCells") == 1` | a **comment** mentioning the name counted |
| `find(a) < find(b)` across a file | `SetRoof(cell, overheadRoof)` appears **twice**, so the wrong pair was compared |
| `"!receipt.IsTerminal" in crossing` | it appears **seven times** in that file |
| `"EnsureSite(campaign, coordinate, …)" in address` | the call appears **twice**; a presence test survived deleting one |
| `"connections.Remove(" ` | did not match a planted `connections.RemoveAll(` |
| `CoherentDepth >= 1` | a planted **99** passed — no upper bound |
| nothing asserted the **variant** reached the hash key | and that variant *is* the entire per-fixture feature |

**The rule, and it is cheap to follow:** scope a claim to the **method body**, the **exact tag**,
or the **call site** — and **count what should exist** rather than testing that something does. A
claim about code must never be satisfiable by a comment, a prefix, a declaration, or a duplicate.

**Twice this session the plant harness refused to run** because a new line made an old anchor
match twice. That is the harness working: it will not score a fault it never planted.

### The rules that come out of it"""),

    # ------------------------------------------------------------------ the register lesson
    (u"## The warning that matters most right now",
     u"""## THE REGISTER FOUND A LIVE DEFECT NOTHING IN OUR OWN CODE COULD HAVE

Owner instruction, 2026-09-30: *"make sure u are using prep and mod registry as needed"*. It paid
for itself in **one query**, and this is the strongest argument for the LAW that exists.

Register row **[188] Removable Mt.Rock Roof Patch** (Workshop `1541438898`) is **installed in this
profile** and patches:

```xml
<xpath>*/RoofDef[defName = "RoofRockThick"]/isThickRoof</xpath>
<value><isThickRoof>false</isThickRoof></value>
```

`RoofDef.VanishOnCollapse => !isThickRoof`. **So in this player's game Core's overhead mountain
vanishes on collapse and leaves open sky** — meaning invariant 13, *a Backrooms coordinate has no
outside*, **was already broken before any of this session's work**, and
`BackroomsContainment`'s claim that thick roof "never vanishes" was reasoning from unpatched Core.

The non-collapsing roof def added for the owner's *"backrooms can not and shall not have cave
ins"* direction repairs that breach as a side effect. And it is a second, independent reason
patching `RoofRockThick` would have been wrong: two mods editing one def at startup, load-order
dependent, and that mod asks to be loaded last.

**Also checked and clear:** [69] Craftable Mountains only *sets* `RoofDefOf.RoofRockThick` from
its own assembly; [63] Change map edge limit affects player map sizing and a coordinate is a fixed
size this mod creates; [128] MinifyEverything mutates `minifiedDef` on **defs, not instances**, so
every Core def the facility places is covered; [221] Stuff Mass Matters means a wider material set
changes hauling weight, which is native and correct.

## WHAT THE COLLABORATOR GETS

Owner direction: *"i need someone else to work on this in parrellel through git hub and i need to
make sure they have it all but the temp stuff i told you to git ignore"*.

**`.local/` was hiding the entire verification suite.** A clone could run the 13 checkers in
`tools/` and **none of the 41 proofs or 13 plant suites**. `.gitignore` now admits exactly two
globs and nothing else:

```
.local/*
!.local/register/
.local/register/*
!.local/register/proof-*.py
!.local/register/plant-*.py
```

Git will not descend into an ignored directory, so the parent has to be re-admitted a level at a
time — the same pattern as the existing `!.claude/bin/`. Still excluded: a 132 MB nuget cache,
19 MB of decompiler binaries, the per-subsystem inspections, the scratch bridge client, and the
hundreds of one-shot record scripts.

**A collaborator needs the same RimWorld install:** `tools/build.ps1` refuses to build unless the
Core assembly hashes to `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`.

## The warning that matters most right now"""),

    # ------------------------------------------------------------------ open questions
    (u"## Open owner questions — THERE ARE NONE",
     u"""## WHAT IS OPEN AFTER 0.12.52-dev

**Nothing in flight and nothing half-built.** Every decision the owner made this session is
implemented and verified at source level. What remains is **runtime acceptance**, which only a
launch can give.

One thing was explicitly deferred and then shipped the next checkpoint, so the pattern is worth
keeping: when a piece needs a save-schema change and a teardown order, say so and do it properly
next rather than half-building it. The Operations release list was that piece, and it is done.

**Owner decisions taken this session, all implemented:**

| Decision | Answer |
|---|---|
| level size | **300x300**, up from 60x60 |
| room count | **grand at level 0** — 6 halls of 80x80 with 144 pillars each — tightening to 42 rooms of 24 by depth 6 |
| families | threshold / office_copy / return_gallery **unique**; the other five repeat |
| onward gates | **4–6 per level**, one per 20 rooms; `MaximumNaturalDepth` **3 → 6** |
| saves | **fresh save**; the 60x60 path is dropped, `PlannerVersion` 3 |
| cave-ins | **never**, via a coordinate-only `RoofDef` with `canCollapse false`; Core's roof untouched |
| map budget | **`Prefs.MaxNumberOfPlayerSettlements`** (the player's own 1–5 slider), floor of 2, per-scenario override |
| natural gates | **deconstructable** (route lost) and **minifiable/movable** (route follows the door) |
| releasing a place | **Operations → Places**, with a Release button and a `releasedByPlayer` save flag |
| materials | **level 0 coherent and yellow**; deeper, **every type for all things**, per fixture |

## Open owner questions — THERE ARE NONE"""),
]

text = original
problems = []
for old, _ in EDITS:
    count = text.count(old)
    if count != 1:
        problems.append("%d occurrence(s) of %r" % (count, old[:70]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

for old, new in EDITS:
    text = text.replace(old, new, 1)

io.open(PATH, "w", encoding="utf-8", newline="").write(text)
print("NOW.md: %d edits applied in one write" % len(EDITS))
