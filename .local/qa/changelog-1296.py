# -*- coding: utf-8 -*-
"""Prepend the 0.12.96-dev entry. CHANGELOG.md has no BOM and must keep none."""
import io
import sys

NL = chr(10)
PATH = "CHANGELOG.md"
HEADING = "# Changelog"

ENTRY = NL.join([
"## 0.12.96-dev - 2026-10-05 - Ten rows that were built and unguarded, and the guarantee half proven",
"",
"- **OWNER DIRECTION:** *\"51 open... are those all doable? lets get to them lets start hoofing it..",
"  so remember get a bunch done berfore battery and stage and cascade\"*. Ten rows closed before the",
"  battery ran once, which is the cadence asked for.",
"- **THEY WERE NOT ALL DOABLE, AND THE COUNT WAS INFLATED.** Triaged honestly: roughly **24 are",
"  blocked on the owner, not on code** -- two starting-goods rows need a `Player.log`, performance",
"  and profile-collision rows need a launch, the domain needs buying, five Workshop rows need the",
"  owner's Steam session and two of those say *ask first*, and the balance rows say *\"no play behind",
"  them\"* in their own text. Roughly **12 are records or acceptance conditions wearing a checkbox**",
"  -- *\"the acceptance condition on the whole generator\"*, *\"This supersedes the earlier answer\"*,",
"  *\"The cost, stated plainly\"*. A condition cannot be completed, so it can never leave the queue,",
"  which is the inflation the owner already challenged once. That leaves about **15 genuinely",
"  buildable**, and ten of them closed here.",
"",
"### The stranded crew: already correct, and the feared defect never existed",
"",
"- **Owner, three directions:** *\"turning off a company gate with pawns inside doesnt lose control",
"  of those pawns they have to survive till a reconnection is made so they can escape\"*. The queue",
"  row warned that this was *\"the most consequential kind\"* of defect -- it takes colonists away",
"  from somebody -- and said *\"the name is the thing to check\"*.",
"- **Checked, and it holds.** `DeinitAndRemoveMap` is called from **exactly one place in the entire",
"  mod**, and that place is a player action. So closing a connection leaves the coordinate map",
"  loaded and the crew spawned, player-faction and under the player's own control.",
"- **`LostPawnRegister` stores NAMES, not pawns.** `NoteLostPawn(string)`, `LostPawnNames()`, read",
"  by the anomaly service as flavour. It was never a control-removal mechanism, so it was never the",
"  hazard the row described.",
"- **And the real hazard is instrumented.** `proof-world-exit.py` asserts our source reaches",
"  `PassToWorld` in at most one place, that the world exit never calls it, that **no gate source**",
"  calls it and **no traversal** calls it. The one place is an *applicant release* -- a candidate",
"  who declined or expired, guarded by `everArrived`, `registered`, `Spawned` and `Faction != null`",
"  -- so it can only ever pass a pawn who was never a colonist.",
"- **The release guard is wider than colonists, deliberately:** `RR_Release_CrewInside` refuses",
"  while anybody the player owns is standing there, and the source says why in its own words --",
"  *\"not only colonists: ... a prisoner, a guest or an animal\"*.",
"",
"### Four features that shipped with nothing guarding them",
"",
"- **Measured before building:** `MaximumOperationalGates` and `PortalBoardUp` had **zero** proofs",
"  between them, while `MaximumNaturalDepth` already had five. The work was never the features --",
"  they ship -- it was that nothing stopped them regressing.",
"- **Three operational gates, not three addresses**, exactly as the owner re-stated it inside their",
"  own message: *\"not three address per gate!!!\"*. The count walks **every loaded map** filtered to",
"  the branch, because *operational* is a property of the branch and counting one map would grant",
"  three more per map.",
"- **The random address option exists**, which is the half of that direction easiest to miss.",
"  **Dialling creates an address, not a map**, so it is free and the open-map budget is only spent",
"  when a place is actually opened; the depth is **derived from the branch seed, never `Rand`**, so",
"  dial twice and get the same place.",
"- **Boarding a doorway up is real work:** 25 wood checked against what is on the map, a 420-tick",
"  job, and `PlaceBehind` naming where it led *before* it closes -- because sealing a doorway",
"  without that makes the place behind it unreachable for ever.",
"- **The held-places list shows a refusal as the row's own state rather than a disabled button**,",
"  because a greyed-out button says no without saying why.",
"- **The depth row is stale and the source already says so:** *\"raised from 3 to 6 at 0.12.49-dev,",
"  owner direction 2026-09-30\"*, because *\"the original three bands were chosen when a level was",
"  60x60 and two doors wide\"*.",
"- New pair: `proof-gate-capacity-and-release.py` **40 of 40** with",
"  `plant-gate-capacity-and-release.py` **29 of 29**, including a plant that reverses the teardown",
"  order -- which breaks **nothing visible**, returns the budget correctly, and quietly orphans a",
"  place for ever.",
"",
"### The stand-alone guarantee: the half that was missing",
"",
"- **The queue row named it exactly:** *\"Removing a declaration does not make absence safe; it only",
"  stops advertising. What has to be proven, row by row, is that the Core-only path runs: every",
"  by-name `GetNamedSilentFail` lookup degrades rather than returning null into a dereference.\"*",
"- The checker proved the package only **names** safe things. It never proved the lookups degrade.",
"  **A silent-fail returning null is the designed outcome on a Core-only install; dereferencing it",
"  a line later is a NullReferenceException at the exact moment the guarantee is supposed to hold.**",
"- **Now checked, and the answer is clean: 152 silent-fail results, every one degrading** -- a",
"  `== null` guard, a `??` fallback or a `?.`. All three idioms, because C# has three and a rule",
"  that knows two cries wolf at the third.",
"- **The rule was wrong three times before it was right, and every narrowing was earned.** It first",
"  demanded every result be assigned or guarded and reported **65 findings, 56 of them innocent**:",
"  passing null as an argument and returning null are both safe, and the only real hazard is a",
"  member access on the result. Then a six-line guard window reported **9 more on correct code**,",
"  because `GenStep_BackroomsDestination` looks up **eleven** Core defs in a block and guards all",
"  eleven in one combined `if` about forty lines below the first -- a better shape than eleven",
"  separate guards, and a rule demanding adjacency was demanding worse code. Then two sites turned",
"  out safe through `??`.",
"- **Sixty-five false findings would have been a rule nobody believes**, which protects nothing.",
"  Proved able to refuse: a planted unguarded dereference fails it, and a plant removing `??` from",
"  the recogniser makes it report correct code. `plant-standalone-and-grants.py` **25 of 25**.",
"",
"### And four more claim-writing defects, every one caught by its plant",
"",
"- **The substring trap, four times in one session, so it is killed with a helper rather than case",
"  by case.** `\"WoodOnMap\" in text` stays true when a plant renames it `WoodOnMapUnused`; so does",
"  `PlaceBehind` against `PlaceBehindUnused`. `uses()` requires a word boundary, and after",
"  `WoodOnMap` in `WoodOnMapUnused` comes a word character, so there is none.",
"- **A definition keeps an identifier alive after its definition is renamed**, because the call",
"  site still names it -- so two claims now assert the **definition and a caller**.",
"- **Containment cannot tell one readout from two:** a plant blanked one of the two budget",
"  readouts and the claim passed. Counted now.",
"- **A plant written as a comment tests nothing**, because the proof strips comments deliberately.",
"  Second time this session.",
"- Build 0.12.96-dev, **232 C# files, 103 package files, 0 warnings, 0 errors**. Ten rows closed and",
"  archived with `VERBATIM TRANSFER CONFIRMED`; queue **41 open / 20 partial / 38 test / 0",
"  completed**. **No game was launched, and nothing here has been played.**",
"",
])

raw = io.open(PATH, "rb").read()
if raw.startswith(b"\xef\xbb\xbf"):
    print("CHANGELOG.md has a BOM and should not; refusing")
    sys.exit(1)
text = raw.decode("utf-8")
if "0.12.96-dev" in text:
    print("already present; nothing written")
    sys.exit(1)
rest = text[len(HEADING):].lstrip(NL)
io.open(PATH, "wb").write((HEADING + NL + NL + ENTRY + NL + rest).encode("utf-8"))
if io.open(PATH, "rb").read().startswith(b"\xef\xbb\xbf"):
    print("a BOM was added -- ABORT")
    sys.exit(1)
print("prepended %d lines; no BOM added" % ENTRY.count(NL))
