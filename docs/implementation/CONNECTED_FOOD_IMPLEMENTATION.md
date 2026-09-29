# Food across a gate, and the family that is deliberately not built (0.6.0-dev)

**Baseline:** `a449e40` (0.5.9-dev, 104 C# files, 76 package files).

**This checkpoint — 0.6.0-dev:** **106 C# source files**, **76 approved package files** (unchanged — four work giver defs and five keyed strings added to files that already existed), zero warnings and zero errors with `TreatWarningsAsErrors` enabled, SDK 9.0.308, Release/net472. Assembly SHA-256 `E5663D70D2BB1F7EC7553DE05286D4C4EFE63237248E10234029D72019FEF2AE`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. Evidence: [`evidence/connected-food-2026-09-29/`](evidence/connected-food-2026-09-29/).

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The food item was three things, and one of them is a decision not to build

Handled as one register item with all its related work, per the owner's rule.

| Part | Shape | Outcome |
|---|---|---|
| Food carried across a gate to people with none | carry — eighth adapter | **Built.** `ConnectedFoodAdapter`. |
| Patient feeding across a gate | deployment — fourth provider | **Built.** `FeedingProvider`. |
| A hungry pawn crossing a gate to eat | a *need*, not work | **Decided against.** Reasons below. |

## Why a hungry pawn does not walk through a gate to eat

This is a decision, not a deferral, and it is recorded so it is not quietly reversed:

1. **Eating is a need, not work.** Core's `JobGiver_GetFood` is a `ThinkNode_JobGiver` in the think tree, not a `WorkGiver`. Every family in this mod rides Core's own `JobGiver_Work` through ordinary work givers. Reaching a need would mean patching Core's **think tree** — the most conflict-prone thing to touch across a 294-mod profile, and squarely against this project's standing method of using Core's own extension points rather than rewriting its behaviour.
2. **A laboratory gate can close mid-journey.** The duration ladder makes an opening finite until high tech. Sending a *starving* pawn on a multi-map walk risks stranding it on the far side with no food and no way back. That is strictly worse than being hungry at home, and the failure mode is a dead colonist rather than a wasted walk.
3. **The logistical answer solves the actual problem.** If people are over there, food should be over there. That is what shipped, and it carries none of that risk.

This is the first time a family has been closed by deciding a piece of it should not exist. Saying so plainly is better than leaving an open row that implies it is merely unfinished.

## The carry half: a narrow trigger, on purpose

The trigger is **"there are hungry people of ours on that map, and nothing there they will eat."** Not "somewhere else is better storage for this meal", which is all ordinary hauling ever asks.

That narrowness is the whole value. Storage hauling would never move food to a map that has no better storage for it, so without this family a colonist on the far side of a gate can starve beside an empty larder while the pantry at home is full.

### What Core decides, and this family does not

- `map.mapPawns.SpawnedHungryPawns` is Core's own map-explicit hungry-pawn list, the same one `WorkGiver_FeedPatient` uses for its potential work.
- `Pawn.WillEat(ThingDef)` **with no getter** decides whether a given eater would touch a given food at all — ideology, royal title, teetotalling and race food rules included. Never reimplemented and never overridden. With no getter it is purely a fact about the eater and the def, so it is fair to ask about a map nobody is standing on.
- Nutrition, meal quality, rot and preference ordering stay entirely Core's. This family decides *that food should be there*, never *what anybody eats*.

### Two guards that are specific to food

**Only our own people and our guests.** A wild animal or a hostile being hungry on the far side of a gate is not a logistics problem, and hauling meals to it would be feeding the Backrooms. The eater must be player-faction or player-hosted.

**The last meal never leaves a map.** `SafeToTakeFrom` refuses to take food from a map that has hungry people of ours unless something else there would still feed them. Without this the family would cheerfully move starvation from one side of a gate to the other and call it work — a bug that would look like correct behaviour in every individual trip.

### Deliberately *not* refused on arrival when they are no longer hungry

Every other carry family closes as "already supplied" if the need evaporated mid-trip. Food does not, because food **keeps**, and a map with people on it will be hungry again shortly. Setting the meals down in storage there is the right outcome either way, so only a genuinely absent storage destination ends the trip.

## The feeding half, and the one extra thing it needs

Core's `WorkGiver_FeedPatient.HasJobOnThing` is — like tending — almost entirely patient-side, which is why this fitted the deployment shape:

| Rule | Reads | Asked remotely? |
|---|---|---|
| `map.mapPawns.SpawnedHungryPawns` | Core's own map-explicit accessor | yes |
| `FeedPatientUtility.IsHungry` | the patient's own food need vs its own threshold | yes |
| `FeedPatientUtility.ShouldBeFed` | posture, bed, faction or host faction, `EatsFood`, slaughter designation, `ShouldSeekMedicalRest` | yes |
| `WardenFeedUtility.ShouldBeFed` | excludes prisoners, fed by wardens through a different route | yes |
| `DevelopmentalStage.Baby()` | the patient | yes |
| `pawn.CanReserve(patient)` | the feeder's map | **no — arrival only** |
| `FoodUtility.TryFindBestFoodSourceFor` | the **getter's** map | **no — arrival only** |

**The extra requirement: food must already be on that map.** A feeder is useless with nothing to feed with, and unlike research or construction there is no partial-credit version — Core's feeding giver simply finds no food source and does nothing. Sending somebody across a gate to stand beside a hungry patient and an empty larder would be the parked-worker case for real, so edible-food presence is part of the candidate test rather than left to hope.

That also makes the two halves cooperate rather than overlap: the carry family gets food there, and only then is a feeder worth sending.

## What the prep work supplied, including one corrected assumption

Per the standing rule, the food rows were read from their existing reviews first — and one of them **corrected an assumption I had going in**.

| Row | Mod | What its review actually establishes | Effect |
|---|---|---|---|
| **125** | Meals On Wheels | **Not** meal delivery, despite the name: colonists may take meals **from animals or other pawns** when other food is unavailable. A food-*sourcing* convenience. Its disposition explicitly warns not to rely on it for expedition or outpost ration accounting. | No overlap with this family, and its warning is another reason the family exists rather than leaning on the mod. |
| **269** | Gastronomy | Restaurant, waiter and register layer requiring Cash Register. **Rights unresolved** — Workshop text refers to GPL while the continuation repository declares CC BY-NC-ND — so its code and art must not be adapted. | No adapter, by both disposition and licence. Company meals must work without it, and they do: this family moves food and never touches dining or service. |
| **195** | RimFridge | Refrigerated storage | Already reached as an ordinary haul destination through `IHaulDestination`; nothing special needed. |
| **229** | Tradable Meals | Trade only | No interaction. |
| **93 / 48** | Food Poisoning Stack Fix / Bed Rest For Food Poisoning | Act on hediffs after eating | No food-logistics interaction. |

Also closed by this: two of the rows listed in `DEFERRED.md` under optional work-behaviour providers — **125 Meals On Wheels** and **269 Gastronomy** — were explicitly awaiting their own review before the food family could be claimed. Both are now reviewed with a recorded outcome, which was part of this item rather than a new one.

## Priorities

| Giver | Work type | Priority | Why there |
|---|---|---|---|
| `RR_ConnectedFoodContinue` | Hauling | **14** | Food outranks every other carry on both halves, because it is the one that keeps people alive: above medicine's 13, construction's 12, bills' 11. Still under Core's `HaulGeneral` (15), because food already on this side being put away properly still comes first. |
| `RR_ConnectedFood` | Hauling | **10** | Above medicine's 9, construction's 8, bills' 7. |
| `RR_ConnectedFeedingContinue` | Doctor | **82** | Above Core's `DoctorFeedHumanlikes` (80) so a feeder partway to a gate is not turned around, and below tending (100) and emergency tending (110), which must always win over feeding. |
| `RR_ConnectedFeeding` | Doctor | **4** | Below every Core doctor giver, **and below the cross-gate tending start at 5**: a patient who needs treatment is more urgent than one who needs a meal. |

Twenty cross-gate numbers now, all player settings, tunable live.

## Saved state

**None added.** The food adapter records the eater in the intent's existing `finalTarget` field and reuses `RecordResolvedCellForTarget`; the feeding provider adds nothing. A 0.5.9-dev save loads unchanged.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors, `TreatWarningsAsErrors` on.
- Determinism: `obj/` and `bin/` deleted and the project fully recompiled **twice**; identical assembly SHA-256 both times.
- All 58 package XML files parse; every `RR_` key referenced from source resolves with 0 missing; every `giverClass` resolves to a real class.
- Compliance checks pass: zero destructive patch operations, no `texPath` outside `RR_`, no ungated DLC id, no `modDependencies`, no non-original package asset.
- 76 approved package files, 0 missing. Reference assemblies recomputed, no drift. No attribution strings.
- One shipped XML comment containing a thinking-out-loud stumble was caught and corrected before publishing.

## Not done, and named

- **A hungry pawn crossing a gate to eat** — decided against, above. Not an open gap.
- **Prisoner feeding** goes through `WardenFeedUtility` and a warden route this family deliberately excludes, exactly as Core excludes it from `WorkGiver_FeedPatient`. It belongs with prisoner and guest care, which is already its own row.
- **Animal feeding** at troughs and `DoctorFeedAnimals` beyond the patient case is not covered; animals in beds are.
- Next: **rest**, then the remaining families. Then the 1990s period and the universe factions.

## For the post-completion test phase

Opening a gate with colonists on the far side and no food there, and confirming meals are carried across; confirming nothing crosses while there is already something there those people would eat; confirming food is **not** taken from a side that would then have nothing for its own hungry people; confirming a teetotaller is never brought alcohol and an ideology-restricted eater never brought forbidden food; confirming a hungry wild animal or hostile on the far side attracts nothing; confirming a hungry patient in a bed attracts a feeder **only** once there is food on that map; confirming a local emergency patient outranks a cross-gate feeding trip; confirming a pawn that stops being hungry mid-carry results in the food being stored rather than the trip failing; and — with rows 125, 269, 195 and 229 active — confirming each behaves as its review predicts and that removing all of them changes nothing about either half.
