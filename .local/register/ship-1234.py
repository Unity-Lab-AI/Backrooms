# -*- coding: utf-8 -*-
"""Ledger for 0.12.34-dev: fifteen work givers, and a clamp overwriting the mod's own numbers."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def sub(rel, old, new):
    path = os.path.join(REPO, rel)
    s = io.open(path, encoding="utf-8").read()
    assert old in s, "%s: anchor missing %r" % (rel, old[:70])
    assert s.count(old) == 1, "%s: anchor not unique %r" % (rel, old[:70])
    io.open(path, "w", encoding="utf-8", newline="").write(s.replace(old, new, 1))
    print("updated %s" % rel)


sub("CHANGELOG.md", u"## 0.12.33-dev", u"""## 0.12.34-dev - 2026-09-29 - fifteen more reasons to walk through a gate

- **Colonists will now cross a gate to load and empty machines on the other side** - gene banks, growth vats, gene extractors, subcore scanners, mech chargers, waste containers, biosculpter pods, bioferrite harvesters and entity holding platforms. Everything the worker handles is already on the far side; nobody and nothing is ever carried through the gate into a machine.
- **Colonists will cross a gate to paint, and to strip paint.** Mark a floor or a wall on a coordinate and somebody will come and do it, provided there is dye over there. Marking nothing means nobody comes.
- **A travel priority you set is the priority that gets used.** Six of the mod's own shipped travel priorities were being quietly replaced with a lower number every time a game loaded, which could turn a worker around part way to a gate. Each family's slider now reaches its own shipped value.
- No expansion is required for any of this. With Biotech, Ideology or Anomaly missing, the machines simply are not there and nothing is offered.

Full record: [fifteen work givers, and a clamp that was overwriting the mod's own numbers](docs/implementation/MACHINE_LOADING_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.33-dev""")

sub("docs/FINALIZED.md", u"## Completed sessions", u"""## Session 2026-09-29 - fifteen work givers, and a clamp overwriting the mod's own numbers (0.12.34-dev)

**Verbatim user quote:** *"read now.md to continue the remaing 20 some items remaining and any anselary need work attributed make sure to use prep work docs and registar of mods to guide you"*

### What shipped

Row 1266 closed, and the painting half of the coverage row closed with it, because the coverage row named them in the same breath.

### Files touched

`src/.../ConnectedWork/Providers/MachineLoadingProvider.cs` **new**, `src/.../ConnectedWork/Providers/PaintingProvider.cs` **new**, `src/.../ConnectedWork/ConnectedDeploymentProvider.cs`, `src/.../ConnectedWork/WorkGiver_ConnectedDeployment.cs`, `src/.../Core/ConnectedWorkPriorities.cs`, `src/.../Core/RimroomsMod.cs`, `1.6/Defs/WorkGiverDefs/RR_ConnectedWork.xml`, `1.6/Languages/English/Keyed/RR_ConnectedWork.xml`, `1.6/Languages/English/Keyed/RR_Audio.xml`, `.local/register/proof-machine-loading.py` **new**, `docs/implementation/MACHINE_LOADING_IMPLEMENTATION.md` **new**, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj, `NOW.md`, `TODO.md`, `docs/research/WORK_TYPE_COVERAGE_AUDIT.md`.

### Closure notes

- **THE CUSTODY QUESTION WAS ALREADY ANSWERED BY CORE, and reading it is what took the time.** All eleven givers were decompiled. Every one refuses to act unless the thing it moves is already on the worker's map, and Core enforces it: `WorkGiver_CarryToBuilding.HasJobOnThing` returns false unless `selectedPawn.Map == pawn.Map`; `FindGeneBank` requires `targetContainer.Map == genepack.Map`; `WorkGiver_HaulToGrowthVat.CanHaulSelectedThing` requires `selectedThing.Map == pawn.Map`; `HaulMechsToCharger` draws candidates from `pawn.Map.mapPawns`; `EmptyWasteContainer` and `HaulToBiosculpterPod` search `pawn.Map`; `TakeEntityToHoldingPlatform` returns false unless `targetHolder.MapHeld == t.MapHeld`. **So the family is the ordinary deployment shape and the safest of them, not the riskiest: the worker crosses and everything it touches is already there.** Invariant 55 is never engaged because there is no transfer to govern. **Assuming it the other way is what kept the row open for twenty-seven checkpoints.**
- **NO EXPANSION BRANCH ANYWHERE, and that is the better design rather than a shortcut.** The obvious shape was three providers behind three `ModsConfig.XActive` gates. Every route degrades on its own instead: the `MayRequire` `ThingDefOf` fields are null without their expansion and each is null-checked, every other route matches a `ThingRequestGroup` or a comp and `ThingsInGroup` returns empty, and every class named lives in the always-present base assembly. **An absent expansion is an empty world, not a condition** - and it is strictly more capable, because the enterable route matches `Building_Enterable` rather than the three shipped buildings, so a modded enterable is covered with nothing naming it. `WorkGiver_CarryToBuilding` is itself an ungated abstract class; the Biotech skip lives on its subclasses because the *buildings* are Biotech, not because the shape is.
- **One Core answer could not be borrowed, and one that looked unusable could.** `GetClosestCharger` builds `TraverseParms.For(carrier)` and calls `carrier.CanReach`, so it is replaced by charger presence plus `CanPawnChargeCurrently`. But `Pawn.ThreatDisabled` reads the entity's own state and uses the passed searcher only for `attackDownedIfStarving` and a roamer comparison - **no map, no reservation** - so the capture route asks Core's question outright. Both were checked in source rather than assumed.
- **The painting givers were the quietest thing in the queue.** The coverage row's reason for staying `[~]` named three things and everyone remembered one. `Art` already had a family - `bill-work-art`, for sculpting - and a covered work type reads as finished. But a bill lives on a bench and paint lives on a **designation**, and `BillWorkProvider` returns false on a map with fifty painted-blue cells and no sculpting bench. **Nobody would ever have crossed for any of it.** All four are designation-driven, so nothing is inferred. Two conditions came out of Core: **paint needs dye and stripping paint does not**, and **a colour already applied is not work** (`terrainGrid.ColorAt` for a floor, `Building.PaintColorDef` for a building).
- **A DEFECT WAS FOUND WHILE WIRING, AND IT WAS LIVE ON EVERY GAME LOAD.** `ConnectedWorkPriorities.Effective` clamped every value against one shared `MaximumPriority = 130`, **including the shipped default**, and `Apply` writes Effective into `WorkGiverDef.priorityInType` while `FinalizeInit` calls `Apply` on every load. **Six of this mod's own authored priorities were being overwritten before a pawn ever ran.** Worst: `RR_ConnectedBasicWorkerContinue`, authored at **502** to sit one above Core's `Flick` (500), landing on **130** - below every local `BasicWorker` giver, so a worker part way to a gate to flick a switch was turned around by any switch at home. **That is precisely the failure the two-giver split exists to prevent, inside the code that exists to prevent it.** Also clamped: smithing bill work 222, art bill work 204, childcare 202, handling 152, and hauling upkeep 131 into a **tie** with `UnloadCarriers`. Fixed by making the ceiling **per giver** - `MaximumPriority` is now the floor of each slider's ceiling, never a cap - because a shipped number is authored against the native givers it must beat and is never a value the player is refused. The rejected alternative was one cap above the game's highest giver, `ChildcarerTeach` at **9999**, which would make every slider a 0-to-10000 drag.
- **MY OWN MEASUREMENT WAS WRONG AGAIN, and the standing warning is why it was caught.** The first scan for shipped priorities above the cap reported **six**; the pattern was `<WorkGiverDef>` and missed `<WorkGiverDef MayRequire="...">`, so it skipped `RR_ConnectedChildcareContinue` at 202. The real count before this checkpoint was **seven**, and eight after. The proof asserts the number so a new one cannot be added without the ceiling being considered.
- Build 0.12.34-dev, **182 C# files, 87 package files**, **0 warnings, 0 errors**, assembly identical across two clean rebuilds. Eleven checkers pass, **thirty-one** proofs exit zero, **18 of 18** planted faults caught. **No game was launched.**

---

## Completed sessions""")

sub("README.md", u"**Current development version: 0.12.33-dev.**",
    u"**Current development version: 0.12.34-dev.**")

print("ledger written for 0.12.34-dev")
