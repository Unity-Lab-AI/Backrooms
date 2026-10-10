
---

## 2026-09-29 — A way out of the Backrooms, and it comes up where you said (0.6.9-dev)

### Verbatim owner requests

> *"continue towards getting to the goal: a 100"*

> *"we also need to have the ability to use a switch so cutting power instantly closes the lab gate in emergencies.. idk think of cool shit in how all the equipment needs to connect and operate for a lab gate"*

The second arrived while this checkpoint was in flight. It is **recorded verbatim in `TODO.md` and not built here** — the emergence work was half-finished and compiling, and leaving it that way to start something else would have left an inconsistent tree. It is scoped to its own checkpoint.

### The half of the topology that was never built

- [x] **A portal whose far side is an ordinary map — BUILT.** Everything had assumed the far endpoint was a branch-owned coordinate: `RegisterNaturalAddress` took a `CoordinateRecord` and `DestinationService.EnsureSite` generated a Backrooms map for it. This is the bounded form the previous record named — the far side is an ordinary map the branch already holds — and it is what makes the owner's own examples `map > backrooms > map > backrooms` and `backrooms > map > backrooms > backrooms > map` route end to end. The first example already worked.
- [x] **`PortalConnectionKind.Emergence = 2`, appended and never renumbered**, so saved values keep their meaning. The three places that tested "is this kind known" became one `KnownKind` helper rather than a condition repeated a fourth time.

### One orientation choice made most of it free

- [x] **Recorded anchor-first**: `First` is the marked door on the ordinary branch-owned map, `Second` is the doorway inside the coordinate. That is the same orientation every other kind already uses — branch-owned map on one side, coordinate on the other — so `Availability` needed **no change**, `Register`'s site check on the second anchor needed **no change**, and the uniqueness rule needed **no change**. What the kind adds is a single gate in `Register`, mirroring line for line the check laboratories already get on `CompRimroomsGate`.

### The player marks it, and that is not a detail

- [x] **`CompRimroomsEmergence` on Core `Door` and `Autodoor`**, added by one `PatchOperationAdd` beside the existing gate comp, dormant until marked, two saved fields. This inherits 0.6.3-dev's rule with **more** force, because a way out arrives *at* the player's own map: *a door the player built is never quietly turned into a hole in the world.* Nothing in the mod ever picks a door, and the network refuses an emergence edge whose near endpoint is not marked.
- [x] **Marking is refused inside the Backrooms**, and the command is not even offered there — a way out cannot come up in the place it leads away from, which the containment rule already implies.
- [x] **Withdrawing a mark deliberately leaves an existing way out alone.** It means "no more ways out here", not "close the one that exists": a saved edge is evidence of a place somebody found, and deleting it silently would strand whatever depends on it.
- [x] **`IsDesignated` re-derives every clause live** rather than trusting the saved flag, so a door that was marked and then deconstructed, moved, or left behind by a different company stops being an anchor with nothing having to notice and clear it.

### How a way out is found

- [x] **A second, independent draw** decides deeper or out for a doorway that already leads onward. It uses a distinct seed key (`wayout:`) from the frontier draw so the two can never correlate, and derives from the coordinate's own saved seed and the doorway's position, so the answer is stable across saves and revisits like every other generated property.
- [x] **One in three ways onward leads out**, deliberately common: a way home is what makes the rest of the topology usable rather than a trap.
- [x] **With nothing marked the doorway leads deeper instead** — a fallback, not a refusal; the survey still finds something. The question is asked **before** the coordinate is minted, because minting one and then not using it would leave a space nobody can reach recorded against the branch.
- [x] **Several marked doors resolve deterministically** by an ordinal sort of their load ids indexed by the same draw, so a doorway does not come up somewhere different on a reload.

### Two defects found on the way, neither related to this feature

- [x] **A keyed string declared twice in one file, with two different meanings.** `RR_Gate_OperatorAway` served both a readout taking the operator's name as `{0}` and a refusal with no argument. RimWorld resolves duplicates last-one-wins, so **one of the two messages was always wrong** — either a refusal rendering a literal `{0}`, or a readout that had lost the name it was meant to show. The refusal now has its own key, `RR_Gate_OperatorNotStaffing`, matching its own text.
- [x] **Nothing was checking for it, and now something does.** `tools/check-keyed-strings.py` verifies no duplicate keys anywhere, every literal `RR_` reference resolving, and format arguments lining up — the specific mismatch the duplicate caused. It resolves references against the mod's **own declared defNames** and against internal identifiers recognised by the **shape of the call site** (`ToilMaker.MakeToil`, `RimroomsAudio.Play`, an audio `case` label) rather than a maintained list, for the same reason the DLC gating check reads the game's data: a list of names rots exactly the way the thing it checks rots. **Three iterations to get there**, each replacing a guess of mine with something read from the data. Current state: 1,114 keys, 0 duplicates, 136 defNames, 14 internal identifiers, 1,086 references all resolving, 0 argument mismatches.

### What this makes live that was hypothetical

- [ ] **`Area_BuildRoof`, `Area_NoRoof`, `Area_SnowOrSandClear` and `Area_PollutionClear` across a gate.** `research/ZONES_AND_AREAS_ACROSS_A_GATE.md` recorded these as a dependency of exactly this endpoint, and they were correctly uncovered while the far side of a gate was always a coordinate with no outside and no removable roof. **An ordinary map is now reachable through a gate**, and a colony map genuinely gets snow, genuinely wants roofs built, and may be polluted. Now a real gap rather than a hypothetical one.

### Saved state

`PortalConnectionKind.Emergence = 2`, an appended value in an existing field; `rr_emergenceDesignated` and `rr_emergenceBranchId` on the new comp, both defaulting to unmarked. A 0.6.8-dev save loads unchanged: no existing edge carries the new kind and no door is marked until somebody marks one. The branch id is recorded at the moment of marking so a mark cannot be inherited by another company through a saved map.

### Documents updated in the same change

`implementation/CONNECTED_EMERGENCE_IMPLEMENTATION.md` (new record), `TODO.md` (two owner directions captured verbatim, including the kill switch), `DEFERRED.md` (a new section plus the area row promoted from hypothetical to live), `NOW.md` (queue item closed, a new ritual step for the keyed-string check), `CHANGELOG.md`, `About.xml`, the csproj.

### Build evidence

0.6.9-dev, SDK 9.0.308, Release/net472, zero warnings and zero errors with `TreatWarningsAsErrors` enabled. **118** C# source files (one new), **76** approved package files (unchanged; one patch operation, fifteen keyed strings and one renamed key added to existing files). Assembly SHA-256 `33DBB4EF977C7539CAF4E5C066BA29DA437602B37CFC9FC5C101CBC4FCD38A8D`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. Evidence folder `implementation/evidence/emergence-2026-09-29/`. All 58 packaged XML files parse; `check-keyed-strings.py` and `check-dlc-gating.py` both pass; `audit-gate0.py` PASS with zero errors; reference manifest recomputed with no drift; the new comp is added by an **additive** patch operation with no destructive operation anywhere; no attribution strings. Published via the cascade in `PUBLISHING.md`; refs read back in session output. No game launched, no test run, no RimSort profile touched.

### SESSION SUMMARY

Source files created: 1. Source files modified: 5. Package files modified: 4 (no new files). Tools created: 1. Docs updated: 6 (1 new).
Owner directions captured verbatim: 2, one of which is **recorded and deliberately not built** because a half-finished feature was in flight.
Network special cases needed for the new connection kind: **0** for `Availability`, the site check and the uniqueness rule, because of one orientation choice.
Defects found and fixed: 1 (a keyed string serving two different messages, so one was always wrong). Blind spots closed in the checking tools: 1.
Still open: a world tile the branch does not hold, the four area types now genuinely live, and the kill switch.
