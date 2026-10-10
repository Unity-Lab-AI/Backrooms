# -*- coding: utf-8 -*-
"""Ledger, queue and research-doc updates for 0.12.36-dev. Six rows in one batch."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def sub(rel, old, new):
    path = os.path.join(REPO, rel)
    s = io.open(path, encoding="utf-8").read()
    assert old in s, "%s: anchor missing %r" % (rel, old[:80])
    assert s.count(old) == 1, "%s: anchor not unique %r" % (rel, old[:80])
    io.open(path, "w", encoding="utf-8", newline="").write(s.replace(old, new, 1))
    print("updated %s" % rel)


sub("CHANGELOG.md", u"## 0.12.35-dev", u"""## 0.12.36-dev - 2026-09-29 - roofs, snow, and reporting in

- **Colonists will cross a gate to build a roof or take one down**, wherever you paint the area. On a Backrooms coordinate there is nothing to do, because it is already solid rock overhead and taking a roof off in there was never allowed.
- **They will also cross to clear snow, sand and pollution**, which only matters at a registered site: a coordinate has no outside and never gets weather.
- **Crew who come back from a trip now owe the company a report**, and the company will not send anybody out again until they have given it. Take the report from the facilities pane; somebody else has to take it, and they have to be a decent enough talker.
- **Confirmed rather than changed: the ground around a gate is ordinary ground.** Mine it, wall it, roof it, put a bedroom there. Nothing about a gate looks at its neighbours, and the only reserved square is the one people stand on to walk through.

Full record: [four area types, a debrief that gates the next trip, and two rows that were already true](docs/implementation/AREAS_AND_DEBRIEF_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.35-dev""")

sub("docs/FINALIZED.md", u"## Completed sessions", u"""## Session 2026-09-29 - roofs, snow, and reporting in (0.12.36-dev)

**Verbatim user quote:** *"get to it we are trying to finish the build so lets start doing shit correctly and efficiently and keep going iin batches of items completed so we have less work constantly pushing and all of that"*

### What shipped

**Six rows in one batch**, per the owner's direction to work in batches rather than publishing each item. Row 761 closes completely; 1215, 1235 and 1239 close together; 98 and 99 close by proof.

### Files touched

`src/.../ConnectedWork/Providers/RoofWorkProvider.cs` **new**, `src/.../Company/StaffDebrief.cs` **new**, `src/.../ConnectedWork/Providers/UpkeepProviders.cs`, `src/.../ConnectedWork/ConnectedDeploymentProvider.cs`, `src/.../ConnectedWork/WorkGiver_ConnectedDeployment.cs`, `src/.../Core/ConnectedWorkPriorities.cs`, `src/.../Company/RimroomsCampaignComponent.cs`, `src/.../Expedition/RimroomsExpeditionComponent.cs`, `src/.../UI/OperationsFacilities.cs`, `1.6/Defs/WorkGiverDefs/RR_ConnectedWork.xml`, four keyed files, `.local/register/proof-areas-and-debrief.py` **new**, `docs/implementation/AREAS_AND_DEBRIEF_IMPLEMENTATION.md` **new**, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj, `NOW.md`, `TODO.md`, `docs/research/ZONES_AND_AREAS_ACROSS_A_GATE.md`.

### Closure notes

- **THE AREA ROWS CARRIED THEIR OWN EXPIRY CONDITION AND IT HAD EXPIRED.** `ZONES_AND_AREAS_ACROSS_A_GATE.md` recorded all four as *not covered and correctly so*, with the reason written down - a coordinate is all thick rock, roof removal there is forbidden by the world rule, and it has no outside and therefore no weather - and *"revisit when the ordinary-map endpoint lands"* attached. **It landed at 0.6.9-dev.** A registered site is an ordinary world map that wants roofs, gets snow and can be polluted. **This is the value of writing the reason down instead of just the verdict.**
- **NOTHING CHANGES THE BACKROOMS RULE, AND THE PROOF ASSERTS THAT.** `BackroomsContainment` still empties `Area_NoRoof` on a coordinate every interval, so the roof family finds an empty area there and offers nobody a crossing. The rule keeps itself. The proof asserts the roof provider contains **no Backrooms exception of its own**, because a second check could drift from the one that actually enforces it - and a planted fault that adds one is caught.
- **ONE SPLIT DECIDED BY A NUMBER, AND IT IS THE INTERESTING PART.** Snow and pollution became routes on the **existing cleaning family** because `RR_ConnectedCleaningContinue` is 22, above `CleanClearSnow` (10) and `CleanClearPollution` (0). Roofs could **not** ride the finishing family: `RR_ConnectedConstructionFinishingContinue` is **82**, below `BuildRoofs` (100) and `RemoveRoofs` (90), so roof routes hung there would turn a committed worker around - the exact failure the two-giver split exists to prevent. Raising 82 would have lifted frame finishing over roof work too. So a third `Construction` family at 101/1, and the tuned numbers are untouched.
- **Almost nothing needed a presence substitute**, which is unusual in this layer: `areaManager.BuildRoof.TrueCount`, `NoRoof.ActiveCells`, `cell.Roofed(map)`, `WithinRangeOfRoofHolder(cell, map)`, `snowGrid.GetDepth`, `GetSandDepth`, `pollutionGrid.IsPolluted` all take the map explicitly and take no pawn. Two deliberate omissions: `ConnectedToRoofHolder` walks the roof grid and is left to arrival because the cheap radius check always agrees when it refuses; and `map.pollutionGrid == null` is the only gate the pollution route needs. **The snow test is Core's own OR of snow and sand depth** - making it an AND refuses real work, and that is a planted fault.
- **QUARANTINE CANNOT BE MEDICAL HERE, AND THAT IS A MEASUREMENT.** This package has **no `HediffDefs` folder at all**. So there is nothing of this mod's own to clear, inventing one is forbidden content, and it would duplicate Core's health system. Quarantine is therefore the other thing the word means: **you do not go back out until you have reported in.** That gives the debrief a consequence and invents nothing. **Debrief and quarantine are one mechanism**, which is why they were built together.
- **THE HOLD BITES ON DISPATCH, NOT ON TRAVERSAL, AND THAT WAS THE CAREFUL DECISION.** The first instinct was `PortalTraversalPolicy`, and it is wrong: traversal is the chokepoint a player walking one colonist through a door by hand passes through, and a company procedure has no business refusing that. What the company controls is whether it **dispatches**. The proof asserts `AwaitingDebrief` appears nowhere in `PortalTraversalPolicy`.
- **`Complete(run)` is the one place "they came home" was already established**, reached from `AllAtHeadquarters`, so nothing new detects a return. A stranded, aborted or abandoned trip raises nothing - those people either are not home or belong to a different procedure, and a stranded trip raising holds is a planted fault. Raising is idempotent per pawn so a reload cannot stack two holds; the list is capped at 64 dropping the oldest; a hold whose pawn is gone is dropped on load rather than blocking dispatch forever.
- **The debrief reuses the interview Social floor rather than inventing one.** `InterviewerSocialFloor` already drops when the branch completes `RR_Measurement_StatementDiscipline`; a second constant would be a second opinion about one capability, and inventing one is a planted fault. **Nobody debriefs themselves** - first refusal, and the only one that cannot be worked around by waiting. **No thought, no mood effect, no hediff**, because the staff-psychology rows ask that native social behaviour be preserved and the Social skill is read and never written.
- **ROW 98 IS PROVED, NOT BUILT.** Enumerated every reason a gate can stop working - **six**: the kill switch, power, the operator, two clocks, and the deliberate cutoff. **Not one reads an adjacent cell**, and nothing in the gate calls `CellsAdjacent`. The proof asserts the whole **set**, so a seventh reason cannot appear without this row being reconsidered. **My first count said five** - I forgot the cutoff, which the containment procedure now also uses. **Fifth time this session a count of mine was wrong and the code was fine.**
- **ROW 99'S PREMISE IS WRONG ABOUT THIS MOD.** The row says linked equipment constrains placement *"because a link has a reach"*. `GateEquipmentLinks` deliberately has **no distance check and no line-of-sight check** - owner direction was *"reach fare and through walls"*, and Core's `CompProperties_Facility` defaults (`maxDistance = 8f`, `requiresLOS = true`) were the opposite of what was asked for. Same map and same branch is the whole spatial rule. The real constraints are power-net membership and single ownership across gates.
- **A FAULT-PLANT RUN FAILED MID-WAY AND LEFT A PLANTED FAULT ON DISK.** `io.open(w)` truncates before writing, so a failed write is **not a no-op**. `OSError 22` hit a restore and the pane kept a planted fault. Found by grepping for the planted key, restored by hand, and the harness now **reads every write back and compares before continuing**. Recorded because a plant harness that can silently leave a fault in the tree is worse than no harness. One plant was also mine rather than a proof gap: it hid its evidence inside a `/* */` comment, which the proof strips - correctly, because a claim about behaviour must not be satisfiable by a comment.
- Build 0.12.36-dev, **188 C# files, 87 package files**, **0 warnings, 0 errors**, assembly identical across two clean rebuilds. Eleven checkers pass, **thirty-three** proofs exit zero, **25 of 25** planted faults caught. **No game was launched.**

---

## Completed sessions""")

sub("README.md", u"**Current development version: 0.12.35-dev.**",
    u"**Current development version: 0.12.36-dev.**")

print("ledger written for 0.12.36-dev")
