# A way out of the Backrooms, and it comes up where you said (0.6.9-dev)

**Baseline:** `242597d` (0.6.8-dev, 117 C# files, 76 package files).

**This checkpoint — 0.6.9-dev:** **118 C# source files** (one new), **76 approved package files** (unchanged — one patch operation, fifteen keyed strings and one renamed key in files that already existed), zero warnings and zero errors with `TreatWarningsAsErrors` enabled, SDK 9.0.308, Release/net472. Assembly SHA-256 `33DBB4EF977C7539CAF4E5C066BA29DA437602B37CFC9FC5C101CBC4FCD38A8D`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. Evidence: [`evidence/emergence-2026-09-29/`](evidence/emergence-2026-09-29/).

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The half of the topology that was never built

The owner's direction has been open since 0.6.3-dev:

> *"and or pop out any where in the game world on a tile map"*

and later, in three worked examples:

> *"map>backrrooms>backrroms , map > backrooms > map > backrooms , and backrromms > map>backrooms>backrooms>map"*

The first of those already routed end to end. The other two both need the same missing piece: **a portal whose far side is an ordinary map**. Everything assumed the far endpoint was a branch-owned coordinate — `RegisterNaturalAddress` took a `CoordinateRecord`, and `DestinationService.EnsureSite` generated a Backrooms map for it.

This is that piece, in the bounded form the previous record named: the far side is an **ordinary map the branch already holds**.

## The player marks it, and that is not a detail

0.6.3-dev established the rule this inherits:

> **A door the player built is never a frontier.** Turning somebody's own wall door into a permanent way into the Backrooms would change an existing colony just by installing this mod.

Emergence runs the other direction — the way out arrives **at** the player's own map — so the same rule applies with more force, not less. `CompRimroomsEmergence` gives every Core `Door` and `Autodoor` one gizmo: *mark this as a way home*. Nothing else in the mod ever picks a door, and the network refuses to register an emergence edge whose near endpoint is not marked.

A mark is refused on a Backrooms map, because a way out cannot come up in the place it leads away from. The gizmo is not even offered there.

**Withdrawing a mark deliberately leaves an existing way out alone.** It says *"no more ways out here"*, not *"close the one that exists"* — a saved edge is evidence of a place somebody found, and deleting it silently would strand whatever depends on it.

## One orientation choice made most of this free

An emergence edge is recorded **anchor-first**: `First` is the marked door on the ordinary branch-owned map, `Second` is the doorway inside the coordinate.

That is the same orientation every other kind uses — branch-owned map on one side, coordinate on the other — and it means the checks the network already performs read correctly for this kind **with no special case at all**:

```csharp
if (!OwnsMap(campaign, edge.First.Map) || site == null || !site.LayoutReady || ...
```

`Availability` needed **no change**. `Register`'s site check on the second anchor needed **no change**. The uniqueness rule needed **no change** — one marked door hosts one way out, which is the existing non-laboratory rule and a clean fiction besides.

What the kind actually adds is one gate in `Register`: the near anchor must carry a designated `CompRimroomsEmergence` whose approach cell matches. That mirrors, line for line, the check laboratories already get on `CompRimroomsGate`.

`PortalConnectionKind.Emergence = 2` is **appended, never renumbered**, so saved values keep their meaning. The three places that tested "is this kind known" became one `KnownKind` helper rather than a condition repeated a fourth time.

## How a way out is found

A doorway inside the Backrooms that leads onward gets a **second, independent draw** deciding *deeper* or *out*:

- it uses a distinct seed key (`wayout:`) from the frontier draw, so which doorways lead onward and which of those lead out can never correlate;
- it is derived from the coordinate's own saved seed and the doorway's position, so the answer is stable across saves and revisits, like every other generated property;
- **one in three** ways onward leads out. Deliberately common: a way home is what makes the rest of the topology usable rather than a trap.

If no door is marked, the draw is moot and the doorway leads deeper instead — a fallback, not a refusal. The survey still finds something.

The question is asked **before** the coordinate is minted, because minting one and then not using it would leave a space nobody can reach recorded against the branch.

When several doors are marked, the one used is chosen by an ordinal sort of their load ids indexed by the same draw — deterministic, so a doorway does not come up somewhere different on a reload.

## Two defects found on the way, neither related to this feature

### A duplicated keyed string, with two different meanings

`RR_Gate_OperatorAway` was declared **twice in the same file**:

```xml
<RR_Gate_OperatorAway>Assigned operator away from the console: {0}</RR_Gate_OperatorAway>
...
<RR_Gate_OperatorAway>The assigned operator is not staffing the console.</RR_Gate_OperatorAway>
```

and used for two different things — a readout taking the operator's name as `{0}`, and a refusal with no argument. RimWorld resolves a duplicate by last-one-wins, so **one of the two messages was always wrong**: either a refusal rendering a literal `{0}`, or a readout that had lost the name it was meant to show. The refusal now has its own key, `RR_Gate_OperatorNotStaffing`, matching its own text.

### Nothing was checking for that

`tools/check-keyed-strings.py` now verifies three things: **no duplicate keys** anywhere; **every literal `RR_` reference resolves**; and **format arguments line up**, which is the specific mismatch the duplicate caused.

It resolves references against the mod's own declared defNames and against internal identifiers recognised by the *shape of the call site* — `ToilMaker.MakeToil`, `RimroomsAudio.Play`, an audio `case` label — rather than a maintained list of names. Same reasoning as the DLC gating check: a list of names rots exactly the way the thing it checks rots. Building it that way took three iterations, each one replacing a guess with something read from the data.

Current state: **1,114 keys, 0 duplicates, 136 defNames, 14 internal identifiers, 1,086 literal references all resolving, 0 argument mismatches.**

## Saved state

- `PortalConnectionKind.Emergence = 2` — an appended enum value in an existing saved field.
- `rr_emergenceDesignated` and `rr_emergenceBranchId` on the new comp, both defaulting to unmarked.

A 0.6.8-dev save loads unchanged: no existing edge has the new kind, and no door is marked until somebody marks one. The branch id is recorded at the moment of marking so a mark cannot be inherited by another company through a saved map.

`IsDesignated` re-derives every clause live rather than trusting the saved flag, so a door that was marked and then deconstructed, moved, or left behind by a different company stops being an anchor without anything having to notice and clear it.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors, `TreatWarningsAsErrors` on.
- Determinism: `obj/` and `bin/` deleted and the project fully recompiled **twice**; identical assembly SHA-256 both times.
- `tools/check-keyed-strings.py`: 0 duplicates, 0 unresolved references, 0 argument mismatches.
- `tools/check-dlc-gating.py`: 6,063 DLC-only defs indexed, 6 references, all gated.
- All 58 package XML files parse; every `RR_` key resolves; every Rimrooms `giverClass` resolves.
- Compliance: the new comp is added by a **`PatchOperationAdd`** on the same two Core door defs the gate comp already uses — additive, no destructive operation, no `modDependencies`, no non-original asset. 76 approved package files, 0 missing. Reference manifest recomputed, no drift. No attribution strings.

## Not done, and named

- **A world tile the branch does not hold.** The larger half of the direction, needing a new world object and a generated map. Unchanged from the previous record: it wants its own checkpoint.
- **`Area_BuildRoof`, `Area_NoRoof`, `Area_SnowOrSandClear`, `Area_PollutionClear` across a gate.** `ZONES_AND_AREAS_ACROSS_A_GATE.md` recorded these as a dependency of exactly this endpoint. **They are still open**: this checkpoint makes an ordinary map reachable *through* a gate, but the work families reach it the same way they reach any branch map, and those four area types have no cross-gate route yet. Now genuinely live rather than hypothetical.
- **A kill switch on the laboratory gate**, requested by the owner while this was in flight and recorded verbatim in `TODO.md`. Its own checkpoint.

## For the post-completion test phase

Marking a door on the colony and confirming the gizmo appears only on ordinary branch-owned maps and never inside the Backrooms; confirming an approach-blocked door is refused with a readable reason; surveying doorways in a coordinate with a way home marked and confirming roughly one in three leads out rather than deeper; confirming the same doorway always gives the same answer across save, reload and revisit; confirming that with **no** door marked every doorway leads deeper instead and nothing is refused; walking a colonist out through a discovered way and confirming they arrive at the marked door; confirming the Operations readout names it a *way out*; withdrawing a mark and confirming an existing way out still works while no new one comes up there; and loading a 0.6.8-dev save to confirm no edge changed and no door is marked.
