# A researcher crosses a gate, and the deployment shape proves it generalises (0.5.8-dev)

**Baseline:** `3647f26` (0.5.7-dev, 101 C# files, 76 package files).

**This checkpoint — 0.5.8-dev:** **102 C# source files**, **76 approved package files** (unchanged — two work giver defs and three keyed strings added to files that already existed), zero warnings and zero errors with `TreatWarningsAsErrors` enabled, SDK 9.0.308, Release/net472. Assembly SHA-256 `46896D6F2D9A4F2D8A4DA526210CADD9DE2337F255F8E4675B28710213C9FC05`, reproduced by **two** full recompiles after deleting `obj/` and `bin/` — and now genuinely reproducible after the commit, because 0.5.7-dev removed the embedded git revision. Evidence: [`evidence/connected-research-2026-09-28/`](evidence/connected-research-2026-09-28/).

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## One new file. That is the point.

The sixth family, and the entire implementation is a single provider class plus two work giver defs, a settings row and three keyed strings.

**No new record. No new job driver. No new `JobDef`. No change to the engine.** The travel-to-work shape built in 0.5.5-dev took a second provider without being touched, which is the first real evidence that it was the right shape rather than a construction-specific convenience.

## What the owner's mod reminder changed

The owner interrupted mid-build with two instructions:

> remembre there are research mods you should always be checking mods too

> thats what the prep work was for

Both were right, and the second is the sharper one. The 294-row profile already has a per-mod review with verified source facts and a recorded disposition for every entry. Re-investigating from scratch wastes eighteen hours of preparation. **Reading the register first is now recorded as the standing method** in `TODO.md` and in the reading order in `NOW.md`.

Five profile rows turned out to matter, and each one was read rather than guessed at:

| Row | Mod | What the review establishes | Effect here |
|---|---|---|---|
| **279** | Research Whatever (`avilmask.ResearchWhatever`) | Auto-selects the cheapest available project at a bench when none is chosen | `GetProject()` may be null when a trip is planned and non-null by the time somebody arrives. **Harmless in that direction** — an optimistic miss just means no trip this pass, and planning retries on a cooldown. |
| **76** | Do Your F\*\*\*\*\*\* Research (`MD.PrioritizeResearch`) | A player float-menu prioritisation action, not a research system | Automatic work never sees it. No interaction. |
| **191** | ResearchTree Eheieh (`eheieh.researchtree`) | Presentation and planning layer only | No interaction. |
| **83** | Dubs Rimatomics | Keeps its **own** research table and its own research screen | That is **not** vanilla `ResearchManager` work. Because this provider matches Core exactly, a separate modded research system is neither claimed nor broken — it simply is not this family's work. |
| **39** | Anomaly Research Asteroid | Content: adds a site | No work-giver interaction. |

All five carry the same recorded disposition: **optional, no Rimrooms dependency, must work with the mod absent, do not copy code or assets.** This implementation satisfies all four by construction.

### The compatibility property of the deployment shape

This is the finding worth keeping. **Because a deployment never issues the work, whatever research giver is active on the destination map does it** — Core's `WorkGiver_Researcher`, or a mod's replacement.

So a profile that changes how research is *chosen* (Research Whatever), *prioritised* (row 76), *presented* (row 191), or that runs an entirely *separate* research system (Rimatomics) changes nothing here. The research family needed **no mod-specific adapter at all**, and that generalises to every future deployment provider. It is the strongest argument yet for the shape.

## The two validation halves, split by what each rule reads

`CanBeResearchedAt(bench, ignoreResearchBenchPowerStatus: false)` is fair to ask about a map nobody is standing on, and that was checked in the decompiled source rather than assumed. It reads:

- the bench's own `def` against `requiredResearchBuilding`;
- the bench's own `CompPowerTrader.PowerOn`;
- the bench's own linked facilities via `CompAffectedByFacilities.LinkedFacilitiesListForReading` and `IsFacilityActive`.

Every one is a fact about the bench and the map it stands on. It consults no pawn and never touches the worker's map.

| Rule | Where |
|---|---|
| a project is selected at all (`Find.ResearchManager.GetProject()`) | **global** — no map, so asked once |
| `CanBeResearchedAt` | candidate — bench and its own map |
| `IsForbidden(Faction.OfPlayer)` | candidate — the **faction** form, never the pawn form |
| `Position.Fogged(map)` | candidate — explicit map |
| observed allowed area at the interaction cell | candidate — from `ObservedAreaAllows` |
| `IsForbidden(pawn)` | **arrival only** |
| `CanReserve(bench)` | **arrival only** |
| `CanReserveSittableOrSpot(InteractionCell)` | **arrival only** |
| researching `HistoryEvent` | **arrival only** |

The forbidden check uses the faction overload remotely for the same reason as every other family: the pawn overload consults the pawn's allowed area *in its current map*, which is the wrong map.

### Why the history event is included

`new HistoryEvent(HistoryEventDefOf.Researching, pawn.Named(Doer)).Notify_PawnAboutToDo_Job()` is asked on arrival, matching Core, which calls it in exactly the same speculative position inside its own `HasJobOnThing`.

It is there for a concrete reason rather than completeness: an ideoligion that forbids researching would otherwise leave a deployed worker standing next to a bench it is never allowed to use, with the deployment held open because the provider believed work existed. Including the check means that case releases cleanly.

## Release: the bench, not the project

Noted at handoff and implemented as noted. Research progress is **global**, so "is there work here" is really two questions: is a project selected anywhere, and is there a usable bench *on this map*.

The deployment therefore ends when either goes away. It does **not** try to outlive a completed project in the hope that another is queued — if `GetProject()` is null there is genuinely nothing to research, and holding a worker on another map for that would be wrong. If a new project is selected while the worker is still standing there, no new deployment is needed at all: the anti-thrash rule already refuses to plan one for a worker on a map that has qualifying work, and Core's local giver simply carries on.

## Priorities

Core's `Research` work type: `130` Hack, `120` CreateXenogerm, `110` StudyArchotechStructures, `100` Research, `50` LongRangeScan, `50` GroundPenetratingScan.

| Giver | Priority | Why there |
|---|---|---|
| `RR_ConnectedResearchContinue` | **102** | Above ordinary research, so a researcher partway to a gate is not turned around by a bench freeing up at home. Below archotech study, xenogerm creation and hacking, which are more urgent or time-limited. |
| `RR_ConnectedResearch` | **40** | Below **every** Core research giver, including both scans. Crossing a gate to research only happens when there is nothing to research on this side. |

Both are player settings, tunable live, per the standing rule that nothing tunable is a constant. Twelve cross-gate numbers now.

## Saved state

**None added.** The deployment record already carries everything this provider needs, which is the same point as the single new file: a provider is data about a question, not new state. A 0.5.7-dev save loads unchanged.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors, `TreatWarningsAsErrors` on.
- Determinism: `obj/` and `bin/` deleted and the project fully recompiled **twice**; identical assembly SHA-256 both times.
- All 58 package XML files parse; every `RR_` key referenced from source resolves with 0 missing; every `giverClass` resolves to a real class.
- Compliance checks pass: zero destructive patch operations, no `texPath` outside `RR_`, no ungated DLC id, no `modDependencies`, no non-original package asset.
- 76 approved package files, 0 missing. Reference assemblies recomputed, no drift. No attribution strings.

## Not done, and named

- **A modded research system with its own work giver and its own bench type** (Rimatomics) is not supplied by this family and is not meant to be. If cross-gate Rimatomics research is ever wanted it is a separate provider with its own source review, and its review explicitly warns against building a Rimrooms dependency on its internals.
- **One risk recorded rather than guarded speculatively:** if a mod replaced the vanilla research giver with one whose eligibility is stricter than this provider's candidate test, a deployed worker could stand idle at a bench it cannot use. The one concrete instance found — an ideoligion forbidding research — is handled by the history-event check. No further machinery was added, because guarding an unverifiable hypothetical with untested code is worse than naming it. This belongs on the post-completion test list.
- Next: **tending across a gate** (needs medicine-as-cargo; surgery, prisoner and guest care, patient feeding and self-tend are each distinct native routes needing their own review), then **food**, **rest**, then the remaining families. Then the 1990s period and the universe factions.

## For the post-completion test phase

Opening a gate with a powered research bench on the far side and none on this side, and confirming a researcher crosses and works; confirming nobody crosses while a usable bench exists at home; unpowering the far bench and confirming the deployment releases and the worker is not walked home; completing the project with none queued and confirming release; confirming a colonist with Research switched off is never sent; confirming a bench requiring a facility is not treated as usable when that facility is missing or unpowered on its own map; and — with rows 279, 76, 191 and 83 active — confirming each behaves as its review predicts and that removing all of them changes nothing about this family.
