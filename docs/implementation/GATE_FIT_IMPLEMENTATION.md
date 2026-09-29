# What a gate's size lets through (0.9.4-dev)

**Baseline:** `5c199d2` (0.9.3-dev, 156 C# files, 79 package files).

**This checkpoint — 0.9.4-dev:** **156 C# source files**, **79 approved package files**. Zero warnings, zero errors, `TreatWarningsAsErrors` on. Assembly SHA-256 `8B01DE3983F9E2AA05011B50F497BFCF4F37B548A60EB74ABAF2EB82D00B16A3`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The request

> *"i suppose the fallback is okay of building mulitple doors 1x1 to make the sizes needed to fit vehicals and the like and bigger creatures"*

Gate sizes landed in 0.9.2-dev. They did not yet stop anything, which made them decoration.

## What the code actually said, before anything was designed

**Animals could not cross a gate at all.** `EligibilityFailureKey` required `IsColonist`, so a muffalo was refused outright.

That meant "bigger creatures fit through a wider gate" **had no subject**: every colonist is body size 1.0 and would have fitted the narrowest gate there is. A body-size rule written on top of the existing eligibility would have been a rule that could never fire.

The owner was asked rather than guessed at, and chose: **any player-owned animal may cross, freely.**

## The rule that was widened, and the one that was not

These are two different rules and they have been kept apart:

| | Who | What it governs |
|---|---|---|
| `TravellerFailureKey` | colonists only, **unchanged** | traversal **in the course of company work** |
| `OrderedCrossingFailureKey` | colonists **and player animals** | crossing because **the player ordered it** |

Eleven connected-work adapters ask the first one before they will plan a job across a gate. Relaxing *that* would have made animals eligible to be scheduled into bills and hauling routes, which is not what was asked for and is not a thing animals do.

**The rule this does not weaken is the one that matters.** The chokepoint exists to stop the **far side** walking out, and the test for that is ownership. A Backrooms inhabitant is hostile or unfactioned and fails on `Faction != Faction.OfPlayer` exactly as it always did. `AutonomousNonPlayerTraversalPermitted` is still a constant false and `MayApproachThresholdForTraversal` still returns false for everything.

## The ladder, from Core's own numbers

| Opening | Admits up to | In practice |
|---|---|---|
| 1 wide | body size 1.2 | people, dogs, chickens, deer |
| 2 wide | body size 2.5 | muffalo, dromedary, donkey, warg, tiger |
| 3 wide or more | no limit | hippo, rhinoceros, elephant, thrumbo |

Proved offline against **all 113 races the installed game ships**: 73 fit a one-wide gate, 97 fit a two-wide, 113 fit three. Strictly widening at each step, a person always fits the narrowest gate, and the pack animals a branch would actually want are **genuinely blocked** by a 1×1 — which is what makes the wider sizes worth building rather than a number on a card.

The proof asserts each of those properties rather than printing them, so a future change to the thresholds that made every creature fit a 1×1, or made pack animals impossible anywhere, fails rather than passes quietly.

## Width belongs to the connection, not to an endpoint

Checked where the **connection** is known, because a connection has one width in both directions: the gate is the machine that forms the aperture and the doorway on the Backrooms side is just where you arrive.

Measuring each end separately would have been the obvious implementation and **would have been wrong**: a generated return threshold is always an ordinary one-cell door, so a pack animal could have walked in through a wide gate and then been unable to come home.

Ordered crossings are the only path a non-colonist can take, and a colonist fits the narrowest gate there is, so work-driven crossings need no second check.

## Not done, and named in `TODO.md`

- **Hostiles needing width** to follow a pawn through, which belongs with the incursion work.
- **The adjacent-door-run fallback** for 1×3 and 2×3 without Doors Expanded.
- Vehicles as such: there is no vehicle in Core, so "vehicles" is served here by body size, and a vehicle mod's pawn would be measured the same way as anything else.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled **twice** from clean; identical SHA-256.
- **All five checkers pass.**
- `.local/register/proof-fit.py`: the ladder proved strictly widening across all 113 installed races, with a person always admitted and pack animals genuinely excluded from a 1×1.
- Compliance: **no new def, asset, patch operation or work type.** One keyed string added, two corrected because they claimed colonists only.

## For the post-completion test phase

Confirming a muffalo is refused at a 1×1 gate with a message naming the reason and accepted at a 1×2; that a colonist crosses any gate; that a Backrooms creature still cannot cross under any circumstances; that an animal crossing and returning both work on the same connection; that a downed or panicking animal is refused; and that cross-gate *work* is still colonists only and never schedules an animal.
