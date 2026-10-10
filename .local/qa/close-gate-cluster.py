# -*- coding: utf-8 -*-
"""Close the stranded-crew cluster and the gate-capacity cluster. Measured, then guarded."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

GUARD = ("`proof-gate-capacity-and-release.py` **40 of 40** with "
         "`plant-gate-capacity-and-release.py` **29 of 29**")

CLOSED = [
 ('- [ ] **"turning off a company gate with pawns inside doesnt lose control of those pawns"**',
  'CLOSED 0.12.95-dev ON MEASUREMENT — **it holds, and it was already guarded.** Closing a '
  'connection does **not** remove the coordinate map: `DeinitAndRemoveMap` is called from exactly '
  'one place in the entire mod, `CoordinateRelease`, which is a **player action**. So the crew '
  'stays spawned, player-faction and under the player’s own control on a loaded map. '
  '**And the feared route out of the player’s hands does not exist:** `proof-world-exit.py` '
  'asserts our source reaches `PassToWorld` in at most one place, that the world exit never calls '
  'it, that **no gate source** calls it and that **no traversal** calls it. The one place is an '
  '*applicant release* — a candidate who declined or expired, guarded by `everArrived`, '
  '`registered`, `Spawned` and `Faction != null`, so it can only ever pass a pawn who was never a '
  'colonist. **Nothing in this mod can take a colonist from the player.**'),

 ('- [ ] **"they have to survive till a reconnection is made"**',
  'CLOSED 0.12.95-dev ON MEASUREMENT. **The map stays loaded, so the player plays them** — food, '
  'warmth, injury and whatever is down there are ordinary RimWorld, which is exactly what the row '
  'asks for. The release guard is what makes it true rather than incidental: `RR_Release_CrewInside` '
  'refuses to let a place go while **anybody the player owns** is standing in it, and it is '
  'deliberately wider than colonists — the source says *"not only colonists: ... a prisoner, a '
  'guest or an animal"*, and asserts `IsPrisonerOfColony` alongside `Faction.OfPlayer`. '
  '**Nothing here is on a clock**, per `CAMPAIGN_CHART.md` §1.1: a stranded crew is somewhere '
  'hard, not on a countdown.'),

 ('- [ ] **"so they can escape"**',
  'CLOSED 0.12.95-dev ON MEASUREMENT. The ways out all exist and all belong to the player: '
  'reconnecting the gate from the near side, a natural doorway found from inside, or — when the '
  'branch is already holding its five maps — walking out into the world as a **caravan**, which is '
  'the one path that reaches `PassToWorld` and does so **only from a player’s click**, into a '
  'caravan they still own. `proof-world-exit.py` asserts the leave routine has **exactly one '
  'caller** and that the caller is a player command. Nothing automatic can reach it: no tick, no '
  'work giver, no incident.'),

 ('- [ ] **What to verify before writing anything:**',
  'VERIFIED 0.12.95-dev, AND THE FEARED DEFECT DOES NOT EXIST. The row said *"the name is the '
  'thing to check"* and it was right to be suspicious of it — but the answer is clean. '
  '`Company/LostPawnRegister.cs` exists, `ExposeLostPawns()` is called from '
  '`RimroomsCampaignComponent`, and **it stores names, not pawns**: `NoteLostPawn(string)`, '
  '`LostPawnNames()`, `TakeLostPawnName()`, read by `AnomalyEventService` as flavour. It was never '
  'a control-removal mechanism, so it was never the hazard the row described. '
  '**And the real hazard is instrumented.** The row named three forbidden routes — a closing gate, '
  'an expiring window, any traversal — and `proof-world-exit.py` asserts each of them never '
  'reaches the world pawn pool. Checked rather than assumed, which is the whole point of the row.'),

 ('- [ ] **"option 1"** - natural portals reach **through depth 3**, then stop.',
  'CLOSED 0.12.95-dev — **SUPERSEDED BY THE OWNER’S OWN LATER DIRECTION, and the source records '
  'it.** This row holds the 2026-09-29 answer. `NaturalFrontierService` says in its own words: '
  '**raised from 3 to 6 at 0.12.49-dev, owner direction 2026-09-30**, *"alongside the map budget '
  'that makes a deeper chain affordable"*, because *"the original three bands were chosen when a '
  'level was 60x60 and two doors wide"*. '
  '**Everything else the row asks for is built and now asserted:** the cap is a constant at 6, it '
  '**refuses** rather than quietly minting a shallower place (`RR_Frontier_BeyondNaturalReach`) — '
  'because *"a doorway that led somewhere other than where it should would be a quieter and worse '
  'lie"* — and it is checked **after** the way home, so the deepest band is not a trap. It bounds '
  'the free doorways only: a gate the player built reaches whatever it has earned, per *"this is '
  'all open eneded they can play how they choose"*. ' + GUARD + '.'),

 ('- [ ] **"and gates need to be able to set up a max of three of them',
  'CLOSED 0.12.95-dev — **both halves of the correction are built, and neither had a single proof '
  'on it until now.** '
  '**The cap is on GATES, not addresses**, exactly as the owner re-stated it: *"not three address '
  'per gate!!! up to three differnt operational gates that can call any address"*. '
  '`NativeGateBinding.MaximumOperationalGates = 3`, and `OperationalGateCount()` walks **every '
  'loaded map** filtered to the branch — because *operational* is a property of the branch, and '
  'counting one map would silently grant three more per map. A gate does not count itself and an '
  'undesignated door does not count. The arithmetic is the owner’s: three gates plus the colony is '
  'four of five, leaving one spare for a doorway somebody walks through without planning to. '
  '**And the random address option exists**, which is the half of the direction easiest to miss: '
  '`PortalRandomDial` with a gizmo on the gate. **Dialling creates an address, not a map** — '
  'nothing is generated until somebody crosses, so dialling is free and the open-map budget is '
  'only spent when a place is actually opened. The depth is **derived from the branch seed, never '
  'from `Rand`**, so dial twice and get the same place, reload and it is still there. ' + GUARD +
  '.'),

 ('- [ ] **"dont let them go more than 5 remember the games mechanics and limits built in',
  'CLOSED 0.12.95-dev ON MEASUREMENT, **including the clause that is easiest to skip** — *"but per '
  'scerio styled"*. `Portals/OpenMapBudget` carries the owner’s sentence verbatim in its own '
  'documentation and states *"A scenario may override the budget, which is per scerio styled"*, so '
  'the budget is a scenario-level thing rather than a hard-coded number. '
  'The warning is a real keyed line in the owner’s own words — `RR_Frontier_TooManyGatesHeld`: '
  '*"This gate is blocked: your company is holding open too many gates"* — and the budget reads '
  'the **player’s** `MaxNumberOfPlayerSettlements` rather than arguing with it, with the stricter '
  'of ours and theirs winning. A Backrooms level costs as much to hold open as a colony, which is '
  'the reasoning the row asks to be respected. Already asserted by `proof-coordinate-layout.py`.'),

 ('- [ ] **"how do they turn them off to use the machine gates for more controll and aiming deeper?"**',
  'CLOSED 0.12.95-dev — **built, and the row’s own list of requirements is met item by item.** The '
  'row said it was *"deliberately NOT half-built"* and named what it needed: a save-schema field on '
  '`CoordinateRecord`, and an Operations held-places list with Release. '
  '**Both ship.** `releasedByPlayer` is scribed as `rr_releasedByPlayer` in `CampaignRecords`, and '
  '`UI/OperationsHeldPlaces.cs` is the list: it shows what is held against the budget, asks '
  '`CoordinateRelease.RefusalFor` rather than deciding for itself, says how many items would be '
  '**left behind** before anything happens, and **shows a refusal as the row’s own state rather '
  'than a disabled button** — because a greyed-out button says no without saying why. '
  '**And there are two ways to turn a doorway off, not one.** `PortalBoardUp` boards a natural '
  'doorway up as **real work**: 25 wood checked against what is actually on the map, a 420-tick '
  'job a pawn walks to, `PlaceBehind` naming where it led *before* it is closed — because a '
  'doorway sealed without knowing that would make the place behind it unreachable for ever. '
  '**The teardown order is the whole safety and it is asserted:** doors are told what they led to '
  'before the edges go, and the edges go before the map does. ' + GUARD + ', including a plant '
  'that reverses that order — which breaks **nothing visible**, returns the budget correctly, and '
  'quietly orphans a place for ever.'),
]

text = io.open(TODO, encoding="utf-8").read()
problems = 0
for anchor, evidence in CLOSED:
    found = text.count(anchor)
    if found != 1:
        print("ANCHOR NOT UNIQUE (%d): %s" % (found, anchor[:85]))
        problems += 1
        continue
    at = text.index(anchor)
    line_end = text.index(NL, at)
    row = "- [x] " + text[at:line_end][len("- [ ] "):]
    text = text[:at] + row + " — **" + evidence + "**" + text[line_end:]
if problems:
    print("%d row(s) not touched; nothing written" % problems)
    sys.exit(1)
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text)
print("closed %d rows" % len(CLOSED))
