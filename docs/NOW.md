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

_(none — no work currently in motion. The 2026-09-28 Claude Code workflow handoff closed; see `docs/FINALIZED.md` session 2026-09-28.)_

**Verbatim user request:** _(when work is active, paste their exact words here)_

**Started:** _(ISO timestamp when the task became active)_

**Goal:** _(one-sentence statement of what "done" looks like)_

**Files touched so far:** _(running list, updated as edits happen)_

**Verification plan:** _(how we'll confirm the task is actually done — compile against pinned references, read output, manual review; the owner alone launches RimWorld through RimSort)_

**Blockers / open questions:** _(anything waiting on user input or external system)_

---

## Next up (from the cascade)

The next unblocked minor task is the first resume step from the connected-colony checkpoint, recorded in `docs/TODO.md` under the pending section. Read `docs/implementation/CONNECTED_COLONY_CHECKPOINT.md` and `docs/implementation/CONNECTED_CROSSING_IMPLEMENTATION.md` before touching `src/RimroomsAsyncIndustries/Portals/`.

Two owner questions are still open from the previous build agent and gate later scenario work (they do not block the portal work):

- Inside start: configurable party versus strictly lone start.
- Inside start: first reliable exit reveals a fixed discovered surface destination, or the player chooses a settlement.

The previous agent proceeded under the provisional assumption "configurable solo/group, automatic Backrooms entry and a fixed discovered surface destination" (see `docs/SCENARIO_SETUP_AND_PORTAL_NETWORK.md`). A third open item is the opening-duration clarification noted in `docs/GATE_0_DECISIONS.md`.

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
