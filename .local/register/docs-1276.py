# -*- coding: utf-8 -*-
"""Every document for 0.12.76-dev, in the same atomic commit as the code.

Docs before push, no patches. README version, CHANGELOG entry, FINALIZED record, TODO closure,
and the NOW.md handoff.

Written as a FILE: the prose is full of apostrophes, and the heredoc trap has been hit thirteen
times.
"""
import io
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

HASH = sys.argv[1] if len(sys.argv) > 1 else None
if not HASH or len(HASH) != 64:
    print("usage: docs-1276.py <assembly sha256 measured after the version bump>")
    raise SystemExit(1)

README = os.path.join(REPO, "README.md")
CHANGELOG = os.path.join(REPO, "CHANGELOG.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
TODO = os.path.join(REPO, "docs", "TODO.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

# ------------------------------------------------------------------ README
text = io.open(README, encoding="utf-8").read()
OLD = u"**Current development version: 0.12.75-dev.**"
NEW = u"**Current development version: 0.12.76-dev.**"
if text.count(OLD) != 1:
    print("README ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(README, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))
print("README version bumped")

# ------------------------------------------------------------------ CHANGELOG
entry = u"""# Changelog

## 0.12.76-dev - 2026-10-01 - the company clears the site, and the mod finally admits what it needs

- **If everyone at the laboratory goes down, The Company comes.** Not when they die - when they are
  all *down*. A squad arrives on all-access passes, and it does not leave anybody standing who was
  there. The dead are buried on the property where there is ground that will take a grave, and put
  in the fire where there is not. Damaged walls and fixtures come back to full repair. Every open
  connection is shut at the gate, and the gate is left commissioned. Three replacement staff land
  with supplies, on the ordinary wage, and **you never lose the game.**
- **It costs you everything on paper.** Every bearer bond anywhere on your maps is collected and
  credited nowhere, and up to 25,000,000 credits is drawn from the account as restocking the petty
  cash - whatever is there, and never below zero. The letter tells you the figures rather than
  saying the site has been secured.
- **This happens at the laboratory only.** The furniture store and the solo start keep the clean-up
  team they already had: five staff, and a trigger that waits for actual death.
- **The mod now declares what it needs, so your mod manager can tell you what is missing.** All five
  expansions and the 289 mods this build is authored against, each with a name and a link, and every
  one of them also declared as a load-order constraint - so a sorting manager puts this mod where it
  belongs on its own. It was previously declaring nothing at all and loading **197th of 296, with 99
  mods coming after it.**
- **Nothing from another mod is assumed.** Content is looked up by name and a missing one degrades
  what depends on it rather than throwing.
- **Reports get signed off now.** A second person reads a finished analysis and either stands behind
  it or returns it - the fourth of the four workflows, after analyse, compare and interview. The
  analyst cannot review their own work, and nothing can be signed off while two of your crew are
  still contradicting each other on the record.
- **Your people remember where they have been.** Field history is kept per person, and an operator
  who has personally walked an address brings the gate up faster on it. The crew panel says who is a
  novice, who is a veteran, and who knows this particular route.

Full record: [the company clears the site](docs/implementation/CLEAR_SQUAD_IMPLEMENTATION.md). No
gameplay, balance, performance or compatibility result is claimed.

"""
text = io.open(CHANGELOG, encoding="utf-8").read()
if not text.startswith(u"# Changelog\n"):
    print("CHANGELOG does not start as expected")
    raise SystemExit(1)
io.open(CHANGELOG, "w", encoding="utf-8", newline="").write(
    entry + text[len(u"# Changelog\n"):].lstrip(u"\n"))
print("CHANGELOG entry written")

# ------------------------------------------------------------------ FINALIZED
record = u"""
---

## Session 2026-10-01 - the clear squad, the hard dependencies, and the last two prep items (0.12.76-dev)

**Verbatim user quotes:** *"are u shure zero goon squad code is written weve gone over this before
by a different name"*; *"see thats WRONG the mod DOES HAVE HARD DEPENDANCIES SO GET IT RIGHT AND
MAKE SURE ITS LAYED OUT RIGHT FOR RIMSORT TO NOTICE AND ENFORCE"*; *"there are alot more
depeandacies than just the DLC we have alkinds of mods in the 274 mod list WE ARE USING ALL OF
THEM!!!!"*; *"6 row gap is dlcs"*; *"lets get it all done come on"*. And the settled fork from the
spec: *"the downed: No Witnesses"*.

**Files touched:** `Company/CompanyClearSquad.cs` (new), `Company/EvidenceReview.cs` (new),
`Company/StaffExposure.cs` (new), `Company/FacilityRelief.cs`, `Company/CampaignRecords.cs`,
`Company/RimroomsCampaignComponent.cs`, `Company/StaffDebrief.cs`, `Gate/GateSpinUp.cs`,
`ConnectedWork/Providers/UpkeepProviders.cs`, `UI/OperationsEvidence.cs`,
`UI/OperationsExpeditions.cs`, `UI/OperationsCrewPlanner.cs`, `About/About.xml`,
`Keyed/RR_Requests.xml`, `Keyed/RR_Investigation.xml`, `Keyed/RR_CrewPlanner.xml`,
`tools/check-register-compliance.py`, `tools/check-dlc-gating.py`, `proof-clear-squad.py` (new,
proof FORTY-SEVEN), `proof-review-exposure.py` (new, proof FORTY-EIGHT),
`proof-stranded-crew.py`, `plant-clearsquad.py` (new, suite EIGHTEEN),
`plant-review-exposure.py` (new, suite NINETEEN), `plant-dependencies.py` (new, suite
SEVENTEEN).

**Mod register.** Rows **4-9** are Core and the five expansions, and rows 5-9 carry stance
*Optional* with row 5 at firmness *Provisional*. **The owner has overruled all five into hard
dependencies**, which is the register being *"not law but guidance"* working exactly as the
owner's standing correction says. Row 77, *Doors Expanded*, is still patched through
`PatchOperationFindMod` and nothing about that changed.

### THE OWNER'S FIRST QUESTION FOUND TWO FALSE STATEMENTS IN MY OWN HANDOFF

*"are u shure zero goon squad code is written weve gone over this before by a different name"*. I
had written *"ZERO code written"* on the strength of `src/` being identical to 0.12.75-dev, which
proves only that **I** had not written any. It says nothing about what past-me built under another
name, and this repository has been caught by exactly that **nine times**.

| My claim | What was true |
|---|---|
| *"Nothing in the battery claims anything about `FacilityRelief`"* | **`proof-facility-relief.py` is proof FIVE**, and two of its claims contradicted the new direction outright |
| *"Core defs confirmed present: Grave, Sarcophagus, ElectricCrematorium, **Pyre**"* | **`Pyre` is Ideology**, not Core |

The Pyre error is the uglier one: the check was run against the **installed game** rather than
against **Core**, and for a Core-only mod that is the entire distinction. It read as a pass because
it answered the wrong question.

**And the third find was pure profit.** `ConnectedWork/Providers/UpkeepProviders.cs` already wraps
Core's `listerBuildingsRepairable.RepairableBuildings(faction)`. A second damaged-building scan was
deleted from the plan before it existed.

### THE SCOPING SAVED TWO PROOF CLAIMS THAT LOOKED LIKE CASUALTIES

`proof-facility-relief.py` asserts *the relief requisitions five roles* and *the living-staff scan
does not treat downed as dead*. Both read as doomed by the new direction -- until the owner's own
scoping resolved it: *"this only happens for the lab secnerio for now"*.

So the squad is a **separate path**, not an edit. The laboratory forks before the relief's trigger
is ever consulted; the Store and Solo/Group branches keep five staff and a death-only trigger.
**Both old claims still hold, untouched**, and the trigger comment that explained the old reasoning
is **scoped rather than deleted** -- it is still true about the path it guards.

Making it universal would have silently rewritten the bargain for two scenarios the owner excluded.
That is the defect shape this project keeps meeting: one rule, quietly applied where nobody asked.

### THE GRAVE DOES NOT FIT INDOORS, AND THAT WAS MEASURED

Core's `Grave` is **(1,2)** -- two cells -- and needs the **`Diggable`** affordance. **Ten** Core
terrains carry it. **Every constructed floor is excluded**: `Concrete`, `SterileTile`, `MetalTile`,
every stone tile, every carpet, every bridge.

**So a grave cannot be dug inside the facility at all.** Found by reading the game's data rather
than at runtime, which is the difference between a feature and a feature that never worked. Burial
goes to open ground -- the facility's unroofed breezeway and compound are exactly that -- and where
no ground will take one the corpse is destroyed, which is *"incenerate on propery"*. **No
crematorium is built**: a bill needs a worker and there is nobody alive to work it, so an unpowered
one would be scenery pretending to be a mechanism.

### THE DEPENDENCY WORK EXPOSED A DEFECT NOBODY WAS LOOKING FOR

`About.xml` declared **no dependencies at all** and a description reading *"Core only ... No
Harmony, no dependencies."* It now declares **294** -- five expansions and 289 mods, each with a
`displayName` and a `steamWorkshopUrl` -- plus **295 `loadAfter` entries**.

**And the load order was the real find.** The package sat at **position 197 of 296** in the owner's
live order, so **99 mods were loading after it**, and a patch cannot see a def from a mod that loads
later. `modDependencies` is what a manager reads to warn; `loadAfter` is what makes the order right,
and we had one entry.

Generated from the owner's own `ModsConfig.xml`, **read-only**. Every active mod resolved to an
installed folder and every non-expansion has a Workshop id. The cycle check read every active mod's
four load-order tags and **none names us**. **Never hand-edit the blocks; edit
`build-dependencies.py`.**

### TWO CHECKERS CARRIED THE OLD PREMISE, AND NEITHER WAS DEFECTIVE

`check-register-compliance.py` refused the whole thing: *"The package must load and run against
Core alone."* **The checker was not wrong; its premise was.** A prohibition became an **assertion**
rather than being deleted -- every declaration must carry a name, a way to obtain it and a matching
`loadAfter`; our own id, Core and duplicates are refused. **Seven planted faults, 7 of 7 caught.**

`check-dlc-gating.py`'s rule survives and matters **more**: `MayRequire` in XML is the same
graceful guard `GetNamedSilentFail` is in C#, which is the posture the owner chose. Only its stated
reason was stale. **A reason nobody believes is worse than no reason.**

### AND THE SIXTH INSTANCE OF AN INSTRUMENT READING ITS OWN PROSE WAS MINE

The fix script searched its result for the phrase it had removed -- and the replacement prose
*quotes* that phrase in the sentence retiring it. The write had landed; **the verification was the
defect.** Same shape as `check-compliance.py` flagging `PatchOperationReplace` inside the comment
explaining why a replace is wrong (0.12.46-dev) and `check-register-compliance.py` matching
`statBases` inside the comment saying it cannot be one (0.12.75-dev). The fix is the one both
checkers took: **assert against the live form, not the mention.**

A second instance of the same family turned up in the new claims: `"Pawn" not in register` is a
**substring test wearing a type test's clothes**, and it is false -- `NoteLostPawn`,
`TakeLostPawnName` and `lostPawnNames` all contain those letters. Duplicate-string trap, same as
0.12.75-dev's label claim.

### THE THREE PREP ITEMS THE OWNER ALSO ASKED FOR

**The stranded-crew verification.** `LostPawnRegister.cs` cannot remove player control **by
construction**: it holds a `List<string>`. But `proof-stranded-crew.py` had **eleven claims and not
one mentioned it**, so the guarantee rested on nobody ever adding a `Pawn` field to a file whose
name sounds exactly like somewhere a pawn would go. **Three claims make it permanent.**

**Review, the fourth workflow.** A second person signs a finished report off or returns it.
Recorded as **additive fields, never a sixth `EvidenceStatus`** -- `Analyzed` is terminal, eight
places compare against it, and the enum is saved by value. It ships with a **button**, a readout and
an objective line in the same checkpoint, because a service with no reachable caller is the defect
that accounted for four of five bond defects.

**Staff prior exposure.** `NoteReturnedFromField` already knew *this person came back from there*
and **threw it away** -- the fact lived as a transient debrief hold and was deleted on debrief.
Same shape as the contradictory-accounts defect: *a mechanism that existed and threw the
disagreement away*. Now kept per person by load id, never by reference, and **spent on the dial**:
an operator who has walked an address brings the gate up faster on it, applied **once** where the
branch's own familiarity compounds. The floor still holds, so a well-worn route is never free.

**210 C# files, 92 package files**, zero warnings, zero errors. Assembly SHA-256
`__HASH__`, measured after the version bump, reproduced by two clean rebuilds.
**Sixteen checkers pass, FORTY-EIGHT proofs hold, 27 of 27 and 20 of 20 and 7 of 7 planted faults
caught in the three new suites, 738 plant anchors findable.**
"""
record = record.replace(u"__HASH__", HASH)
text = io.open(FINAL, encoding="utf-8").read()
io.open(FINAL, "w", encoding="utf-8", newline="").write(text + record)
if record not in io.open(FINAL, encoding="utf-8").read():
    print("FINALIZED WRITE NOT VERIFIED")
    raise SystemExit(1)
print("FINALIZED written and verified")

# ------------------------------------------------------------------ TODO closures
todo = io.open(TODO, encoding="utf-8").read()
CLOSURES = [
    (u"## IN PROGRESS - the goon squad, and never losing the game - 2026-10-01 (0.12.76-dev)",
     u"## The goon squad, and never losing the game - 2026-10-01 (0.12.76-dev) - DONE"),
    (u"## IN PROGRESS - the hard dependencies, and RimSort enforcing them - 2026-10-01 (0.12.76-dev)",
     u"## The hard dependencies, and RimSort enforcing them - 2026-10-01 (0.12.76-dev) - DONE"),
]
problems = []
for old, _ in CLOSURES:
    if todo.count(old) != 1:
        problems.append("%d of %r" % (todo.count(old), old[:56]))
if problems:
    for problem in problems:
        print("TODO ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in CLOSURES:
    todo = todo.replace(old, new, 1)
    start = todo.index(new)
    end = todo.index(u"\n---", start)
    todo = todo[:start] + todo[start:end].replace(u"- [~] **", u"- [x] **") + todo[end:]
io.open(TODO, "w", encoding="utf-8", newline="").write(todo)
print("TODO closed for both batches, every description kept")

print("")
print("NOW.md is NOT touched by this script -- it is written after staging, per the owner's")
print("order of operations: STAGE then NOW.md then CASCADE.")
