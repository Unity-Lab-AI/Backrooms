# NOW — Current Focus Snapshot

**Single-focus tracker.** One thing in flight at a time. The "what is Unity actively working on right this moment" file. Distinct from the three-tier task ledger:

| File | Grain | Scope |
|------|-------|-------|
| `docs/ROADMAP.md` | MAJOR | High-level phases / milestones (multi-session, multi-PR) — layered onto the project's Stage 0–6 development roadmap |
| `docs/TODO.md` | MINOR | Day-to-day work queue (everything pending + in-progress) — the working slice of the master backlog in `docs/PREPRODUCTION_AND_IMPLEMENTATION_TODO.md` |
| `docs/DECOMPOSED.md` | DECOMPOSED | Smallest meaningful execution unit (one file edit, one command) |
| **`docs/NOW.md`** (this file) | **CURRENT** | **The ONE task currently in motion — the active context** |
| `docs/FINALIZED.md` | ARCHIVE | Permanent record of every completed task |

LAW #0 applies: every snapshot of the active task preserves the user's verbatim words from the request.

---

## Active

M1 connected colony portals. The intent/lease engine and the **storage-hauling** family shipped in 0.5.0-dev; 0.5.1-dev then closed **nine deferments** on the owner's direction not to park work the mod depends on, including the natural-gate discovery trigger, container delivery destinations, remote allowed-area preflight and the crossing receipt bound. Branch `feature/connected-colony-portals`.

0.5.2-dev closed the **casualties and remains** family: our own downed people are carried home to a bed and our dead to a grave or storage, which was the owner-named capability no route reached. Capture stays a player order by design.

0.5.3-dev closed **construction supply** — real material carried through a gate into a real build site, blueprints included — and audited the mod's dependency position: it requires nothing but base Core, now verified rather than asserted. The capability-matching method is recorded as binding and dissolves the M2 "Core has no X" content blockers.

0.5.4-dev implemented four owner decisions: the laboratory duration ladder (first opening ~30 real minutes, multiplying per completed project, indefinite at the top while still requiring power, operator and energy every tick), confirmation that natural gates stay permanently open and untouched, one tech tree for every scenario, and a **player-named company** renameable through Core's own dialog. The two inside-start questions open since Gate 0 are also decided.

**Next, chosen by the owner:** **travel-to-work intents**, the new intent shape for work done at the far site with nothing carried. It completes construction *finishing* and unlocks every later "work over there" family. Then bills and unfinished work, research, tending across a gate, food and rest.

Owner direction on validation: **keep building, launch later.** No QA pass is scheduled yet; runtime acceptance rows stay open.

Steps 1–3 closed in 0.4.2-dev (addresses, legacy threshold repair, ordinary crossing job, session controls, emergency return, reconcile surface). The owner's gate traversal rule shipped in 0.4.3-dev on top of them: inhabitants and monstrosities stay in the Backrooms, enforced at one chokepoint. Record for both: `implementation/CONNECTED_TRAVEL_IMPLEMENTATION.md`.

Carried into step 4 and beyond: the adapters must honour `PortalTraversalPolicy` — a colonist may decide to cross to do a job, an inhabitant may never decide anything about a gate. The pacing half of the owner's rule (gradual bounded escalation) is specified and owned by step 5 in `DEFERRED.md`.

Standing constraints every further adapter inherits, established in 0.5.0-dev and recorded in `implementation/CONNECTED_WORK_IMPLEMENTATION.md`: an adapter's candidate half runs against an explicit `Map` and may never call a native `HasJob`/`JobOn` remotely, nor claim a pawn-specific or allowed-area result for a map the worker is not standing on; the definitive half runs only on arrival; a bounded search that ran out of budget is pending and never "no route"; every bounded scan uses a rotating window rather than a prefix, so no map, stockpile or object is starved when several gates are open; and each family registers two work givers, a high-priority one that only finishes committed trips and a low-priority one that only starts them.

**Verbatim user request:** "new feature branch for your work start on the todo weork making sure to properly finalize all completed work as i think gate 0 is still in the todo stuff but it should be finalized first and begin on any and all todo work to reach the goal of having a completed working mod in all regaurds as outlined in the many prep documentes build over 18 hours of work in gate 0"

**Started:** 2026-09-28T19:50 local

**Goal:** saved work intents and quantity leases exist, native destination job targets are revalidated at use, and the adapter families land one at a time with source evidence per route: storage hauling, construction supply and finish, bills, research, tend and rescue, food, rest, then the remaining families. Native priorities, schedules, allowed areas, locks, custody and actual inventory stay authoritative. A generic graph is not an adapter.

**Files touched so far (this branch):** `docs/DEFERRED.md`, `docs/TODO.md`, `docs/FINALIZED.md`, `docs/NOW.md`, `docs/DECOMPOSED.md`, `docs/ROADMAP.md`, `docs/ARCHITECTURE.md`, `docs/SKILL_TREE.md`, `docs/PREPRODUCTION_AND_IMPLEMENTATION_TODO.md`, `CHANGELOG.md`, `docs/implementation/CONNECTED_CROSSING_CALLER_REVIEW.md`, `docs/implementation/CONNECTED_TRAVEL_IMPLEMENTATION.md`, `docs/implementation/evidence/connected-travel-2026-09-28/`, `src/RimroomsAsyncIndustries/Portals/PortalAddressService.cs`, `PortalTravelService.cs`, `PortalCrossingService.cs`, `src/RimroomsAsyncIndustries/Generation/RimroomsDestinationMapParent.cs`, `src/RimroomsAsyncIndustries/Company/CampaignServices.cs`, `RimroomsCampaignComponent.cs`, `src/RimroomsAsyncIndustries/UI/OperationsPortalNetwork.cs`, `OperationsExpeditions.cs`, `Mod/.../1.6/Defs/JobDefs/RR_PortalJobs.xml`, `Mod/.../1.6/Languages/English/Keyed/RR_Portals.xml`, `tools/package-files.json`, `Mod/.../About/About.xml`, `src/.../RimroomsAsyncIndustries.csproj`

**Verification plan:** read every file in full before editing; `./tools/build.ps1` with zero warnings and errors; evidence folder per checkpoint with compiler output and source/package/reference manifests; no game launch, no RimSort change.

**Blockers / open questions:** none for step 4. The three owner questions (inside-start party size, first exit, opening duration) do not gate it and are tracked in `DEFERRED.md`.

---

## Next up (from the cascade)

Read before editing `src/RimroomsAsyncIndustries/Portals/` or adding an adapter: `implementation/CONNECTED_WORK_CORE_API.md` (the pinned Core job, reservation, carry, area and spawn behaviour every adapter depends on), `implementation/CONNECTED_WORK_PROFILE_BOUNDARIES.md` (which profile rows touch work, storage and hauling and how the design treats them), `implementation/CONNECTED_TRAVEL_IMPLEMENTATION.md` (what steps 1–3 actually built), and [`DEFERRED.md`](DEFERRED.md) (every deferment with its owner step — a step cannot close while it still owns an open row there).

After step 4: step 5 (optional providers, scenario openings, the natural-discovery trigger, procedural inhabitants), then step 6 (checkpoint and publish). Then M2 existing-content replacement, which shares its migration decision with the legacy threshold repair already built.

The three owner questions stay open and gate none of this: inside-start party size; inside-start first exit fixed versus chosen; opening duration. Provisional assumptions are recorded in `SCENARIO_SETUP_AND_PORTAL_NETWORK.md` and tracked in `DEFERRED.md`.

---

## How to use this file

1. **When starting a meaningful task** — populate the Active section with verbatim user request + goal + files
2. **During work** — update Files Touched + Verification Plan + Blockers as state shifts; this is a living snapshot
3. **When finishing** — append the closure to `docs/FINALIZED.md` (per FINALIZED-BEFORE-DELETE LAW), then reset the Active section back to _(none — no work currently in motion)_
4. **Never delete the Active section structure** — the placeholder lines stay; only the content shifts

The file always has exactly one Active section. When it says _(none)_, the bridge stream is idle and Unity is awaiting next direction.

---

## Why this file exists alongside TODO.md

`TODO.md` is the queue — everything pending + in-progress, grouped by section. It can hold dozens of `[~]` items if multiple parallel threads are open.

`NOW.md` is the lens — ONE task, all the context, no scroll. Useful when:
- Session resumes after compaction and you need the "where were we" anchor in 10 seconds, not 10 minutes
- The user asks "what are you doing right now" mid-task
- A pre-compact snapshot needs to capture exactly one current context (not the whole TODO queue)
- The harness hooks want a single-task pointer for the state-refresh banner

Read `NOW.md` first for "what's happening", then `TODO.md` for "what's queued", then `ROADMAP.md` for "where are we headed".
