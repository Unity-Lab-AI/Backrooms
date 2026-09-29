# Nothing is blocked on the owner: tunable priorities, a named test phase, and a verified compliance position (0.5.6-dev)

**Baseline:** `1dabefb` (0.5.5-dev, 99 C# files, 76 package files).

**This checkpoint — 0.5.6-dev:** **100 C# source files**, **76 approved package files** (unchanged — twelve keyed strings added to a file that already existed), zero warnings and zero errors with `TreatWarningsAsErrors` enabled, SDK 9.0.308, Release/net472. Evidence: [`evidence/tunable-priorities-2026-09-28/`](evidence/tunable-priorities-2026-09-28/).

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## What prompted this

The owner read a session report that ended with "still two owner-blocked rows" and pushed back:

> whats blocked by me nothing should ever be blocked by me use ask me question and make sure there is a write in option multile choice to select and fill out my own because not all your recommendations listed are the only options

The push-back was correct, and the fault was mine. Nothing in this project has ever been blocked on the owner. The standing instruction from the beginning was to keep building and launch later, and 0.4.2 through 0.5.5 were all built without waiting for anything. Labelling two rows "blocked on the owner" described a *closure* condition as if it were a *work* condition, and made the owner look like the bottleneck in their own project.

Four questions followed, each with a write-in option. All four are implemented here.

## 1. The `[!]` status is gone

`DEFERRED.md` and `TODO.md` no longer have a blocked-on-owner status at all. **28 rows in `TODO.md` and 2 in `DEFERRED.md`** were reclassified to `[T]`, and every "— blocked: owner …" suffix was rewritten. Both files now state, at the top, that no such status exists and that it must not be reintroduced.

`[T]` means: cannot be *closed* without the game running, gates no work, and is never a reason to stop building.

## 2. The post-completion test phase

The owner's answer to the launch-rule question carried a clarification that is more significant than the question:

> once again we should not be worriying about this as the mod is NOT completed yet only once we confirm everything in intirety with the mod and its workings with the game dlc, core, and mods is 100% do we ever test it(which i have to set up first, then u add the rim api mod, then we test(me running through the game asnd telling you the problems, LIVE fixes to the extent we can without a restart and reload of the mod)

Testing is not a pending activity that anything waits on. It is **one phase, after completion**, in a fixed order: the mod is complete at 100% including its behaviour with Core, the DLC and the mods → the owner sets up the environment → the rim api mod is added → the owner plays and reports, and fixes land live, without a mod restart and reload.

**Two consequences bind implementation now**, recorded in `DEFERRED.md` as rules rather than notes:

- **Prefer settings and data over constants.** Anything hardcoded is something that live session cannot fix. This is not a style preference; it is a direct consequence of how the only test session will work.
- **Never ask the owner to launch in order to continue building.** There is no such circumstance.

The launch rule itself is unchanged and was reaffirmed: only the owner launches RimWorld, through RimSort, and the agent never touches the active mod list.

## 3. Work-giver priorities became live settings

The balance-review row was closed by **removing the question instead of answering it**. All eight priorities across the four cross-gate families are now player settings.

| Family | Continue | Plan |
|---|---|---|
| Hauling through a gate | 95 | 14 |
| Casualties and the dead | 65 | 59 |
| Building material to a site | 12 | 8 |
| Travelling to finish a build | 82 | 5 |

Those remain the shipped defaults, in the XML, which stays the single source of truth for them — the code captures them at startup rather than duplicating them, so a default cannot drift out of step with a second copy.

### Applied live, with public API only, no Harmony

Three public surfaces make this work, each verified against decompiled Core rather than assumed:

- `WorkGiverDef.priorityInType` is a writable field.
- `WorkTypeDef.workGiversByPriority` is a public mutable `List<WorkGiverDef>`, built by Core's own `ResolveReferences` as that work type's givers `orderby d.priorityInType descending`.
- `Pawn_WorkSettings.Notify_UseWorkPrioritiesChanged()` is public and sets the `workGiversDirty` flag that rebuilds each pawn's cached giver order.

**The subtle one: Core's list is built with a LINQ `orderby`, which is a stable sort.** Givers sharing a priority keep their database order. `List.Sort` is *not* stable, so re-sorting with it would silently reshuffle equal-priority **native** givers — an unrelated change to vanilla behaviour, caused by touching a Rimrooms setting. `OrderByDescending` is stable, so that is what is used.

Applied at three moments: at startup once defs exist, on game load through `FinalizeInit` (because a loaded save's pawns did not exist at startup and each pawn caches its own order), and when the settings window closes. Not per slider frame — pushing values into defs re-sorts a work type and invalidates every pawn's cache, which belongs at the moment the player is finished, not mid-drag.

Pawn caches are invalidated for every pawn spawned on any map and every pawn in a caravan, which covers everyone who could be issued a job.

### The invariant is enforced, and explained

Starting a trip must stay below finishing one. If it did not, a worker standing on the far side with cargo in its hands could be handed a brand-new trip instead of completing the delivery, and the entire reason the giver pair exists collapses. So the plan value is clamped below the continue value — and when that clamp bites, the settings window **says so**, rather than a slider silently refusing to stay where it was dragged.

Overrides are keyed by giver defName, and a value equal to the shipped default is not stored at all. So a future family needs one row in a table and no settings migration, an untouched install saves nothing, and a later change to a shipped default is still picked up.

## 4. Compliance, verified rather than asserted

Mid-session the owner added a release requirement:

> make sure we are foillowing all rimworld and steam TOS and requirments when it comes to issues similar and the issue of factions and pawn heduffs and the like this mod has to be working with official versions

This landed at exactly the right moment, because the faction layer is the first thing that would have been tempted to violate it: a `FactionDef` needs an icon, and the easy way to get one is to copy a PNG out of the game's folders — which is redistribution of Ludeon's assets, trivial to do by accident and expensive to undo after release.

The full position, the verification behind each row, and the rules that now bind every def the mod adds are in [`../COMPLIANCE_AND_OFFICIAL_VERSIONS.md`](../COMPLIANCE_AND_OFFICIAL_VERSIONS.md). Checked against the package on disk, not recalled. Headlines:

- Targets official 1.6 only; **zero `modDependencies`**; `loadAfter` is `Ludeon.RimWorld` alone.
- **No game or DLC asset in the package.** All 18 non-XML files are ours, and no `texPath` anywhere points outside `RR_`.
- **Zero `PatchOperationReplace` and zero `PatchOperationRemove`** in the whole package — only 4 × `Add`, 2 × `Conditional`, 1 × `Sequence`. Nothing of Core's is overwritten or deleted.
- No DLC def referenced from any XML. The single DLC-adjacent code path is `pawn.Ideo`, null-guarded, and `Ideo` is a type in the official `Assembly-CSharp` so no DLC assembly is referenced.
- No Harmony, no assembly patching, no bundled game file, no shipped QA overlay. MIT licence, our own.
- GPL contamination specifically avoided: Stargates! (profile row 218) is GPL-3.0, is not a dependency, and nothing is taken from it.

**The confirmed mechanism for DLC-conditional content is `MayRequire="Ludeon.RimWorld.<Dlc>"`** with `MayRequireAnyOf` for alternatives — verified as the supported path by the fact that Core and the DLC use it 1,999 times in their own shipped data. The official ids are `Ludeon.RimWorld.Royalty`, `.Ideology`, `.Biotech`, `.Anomaly`, `.Odyssey`.

### Made self-enforcing

A document nobody re-reads is not a compliance position. The checkpoint verification now mechanically fails on: any destructive patch operation, any `texPath` outside `RR_`, any DLC package id not covered by `MayRequire`, any declared `modDependencies`, and any non-original-looking asset in the approved package list. It passes at 0.5.6-dev.

### Three owner questions, none blocking

Recorded in the compliance document: provenance of the three images intended to survive to release (note that the 14 gameplay PNGs **do not** survive M2, so questions about those are moot for the release package); the `<author>Operator</author>` field, which presumably becomes a real handle for publication; and a conscious confirmation of MIT before release, since MIT lets anyone redistribute and relicense derivatives.

## 5. Default behaviour at future forks

The owner chose: **ask immediately with multiple choice and a write-in, and keep building everything that does not depend on the answer.** That is now the recorded default. Also recorded: my four suggestions are never the whole option space, so the write-in is not decoration.

## Saved state

| Owner | Key | Rule |
|---|---|---|
| `RimroomsSettings` | `rr_connectedWorkPriorities` | Additive, in the mod's preferences file, not in a save. Absent from every earlier preferences file, loading correctly as "no overrides" and therefore as the shipped priorities. Keyed by giver defName so a family added later needs no migration. |

No campaign save state changed. A 0.5.5-dev save loads unchanged.

## Not done, and named

- **Bills and unfinished work** remains the next build, unchanged by this checkpoint.
- The faction and period layer follows the work families, now with compliance rules attached.
- The three compliance owner questions above, which are publication-time matters.

## For the post-completion test phase

The priority sliders are the first thing in this project designed specifically for that session: they let the feel of every cross-gate family be tuned while the game runs, with no rebuild and no mod reload. Every future tuning value should be held to the same test before it is written as a constant.
