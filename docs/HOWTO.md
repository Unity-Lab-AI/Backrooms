# HOWTO — Working on Rimrooms with the Claude Code workflow

This is the practical guide for anyone (human or build agent) opening this repository under the `.claude/` workflow. It explains how the two documentation layers fit together, what the daily ceremony is, how to build and stage the mod, and how work gets published. It does not replace the project contracts; it tells you where they are and in what order they win.

## 1. Two documentation layers, one project

**Layer A — project canon (pre-existing).** The design, research, source-review, implementation and evidence documents produced during pre-production and the first four build waves. Authority order when they conflict is defined in [`../AGENTS.md`](../AGENTS.md#authority-and-document-map): owner decisions in `GATE_0_DECISIONS.md` first, then the master backlog `PREPRODUCTION_AND_IMPLEMENTATION_TODO.md`, then the player/design contracts, then technical/integration contracts, then source facts. Required reading order for a fresh agent is in [`AI_BUILD_HANDOFF.md`](AI_BUILD_HANDOFF.md#required-reading-order).

**Layer B — workflow ledger (added 2026-09-28).** The files the `.claude/` template maintains every session:

| File | Role | Reads with |
|------|------|------------|
| [`ROADMAP.md`](ROADMAP.md) | MAJOR tier — milestone markers layered on the Stage 0–6 roadmap | master TODO phases |
| [`TODO.md`](TODO.md) | MINOR tier — the working queue: what is pending or in flight now | master TODO bounded subitems |
| [`DECOMPOSED.md`](DECOMPOSED.md) | DECOMPOSED tier — single-edit slices of the active minor task | the per-system implementation record |
| [`TEST.md`](TEST.md) | TEST tier (added 2026-10-06) — every row that cannot close without the game running. Nothing here is buildable by an agent | owner-launched acceptance |
| [`NOW.md`](NOW.md) | The one task in motion, verbatim request, files touched, blockers | — |
| [`FINALIZED.md`](FINALIZED.md) | Permanent archive of completed work; append-only | build records + evidence folders |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | As-built map of `src/`, the package, tools and save owners | `TECHNICAL_ARCHITECTURE.md` (the design target) |
| [`SKILL_TREE.md`](SKILL_TREE.md) | Capability inventory by domain, complexity, dependency and priority, with implementation status | `SYSTEMS_CATALOG.md`, `FEATURE_TRACEABILITY.md` |
| [`PUBLISHING.md`](PUBLISHING.md) | The exact, tested push + cascade procedure for both remotes and their differences | `AGENTS.md` publication cadence |
| ~~[`DEFERRED.md`](DEFERRED.md)~~ | **CLOSED.** Zero open rows, and no row may ever be added. Every row it held was migrated into `TODO.md`. Nothing in this project is deferred: build it, queue it, or ask | `TODO.md` |

**Which wins.** Scope, gates and evidence standards come from Layer A. "What is being worked on right now and in what order" comes from Layer B. When a minor task in `TODO.md` closes, tick the matching bounded subitem in the master TODO in the same change, name its evidence, and keep the broad parent item open if runtime acceptance is still pending. That rule already existed in [`REGRESSION_CONTAINMENT.md`](REGRESSION_CONTAINMENT.md); the ledger just makes the active slice visible.

## 2. Starting a session

```text
Windows:        .\.claude\start.bat
Linux / macOS:  ./.claude/start.sh
```

The launcher installs the persistent memory templates on first run, then starts Claude Code with `/unity then run /workflow`. Running plain `claude` in the repo root also works; the persona and workflow still load because `.claude/CLAUDE.md` auto-loads and the session hooks inject state. On `/workflow`, Claude reads `ROADMAP.md`, `TODO.md`, `DECOMPOSED.md`, `NOW.md`, `FINALIZED.md`, `ARCHITECTURE.md` and `SKILL_TREE.md` before doing anything, then resumes the cascade: current decomposed task → next decomposed → next minor → next major (major boundaries pause for the owner).

Useful commands once inside:

| Command | What it does |
|---------|--------------|
| `/workflow` | Re-run the pipeline: verbatim-words gate, timestamp, environment check, read the ledger, enter work mode |
| `/yolo` / `/sober` | Turn autonomous lead-dev mode on / off. YOLO works the cascade without asking at routine forks, still never launches the game, and ships a user test plan at every task closure |
| `/super-review` | Adversarial senior-engineer review of the current diff or a named file |
| `/unity-update` | Refresh the `.claude/` template from upstream; personal files and the memory folder are preserved |
| `rescan` (plain word) | Regenerate `ARCHITECTURE.md` and `SKILL_TREE.md` from a fresh source scan |

## 3. The ceremony every task follows

These are the workflow LAWs in `.claude/CONSTRAINTS.md`, restated as they apply here. They sit on top of the project rules in `AGENTS.md` and `CONTRIBUTING.md`; nothing here relaxes those.

1. **Verbatim words.** The owner's exact sentence goes into the `TODO.md` entry, the `FINALIZED.md` entry and any commit that references it. Never paraphrased, never collapsed. One task per item in a list. The previous build agent did not work under this rule, so older records paraphrase; new records must not.
2. **Add to TODO before work, archive to FINALIZED before removing.** Write the `FINALIZED.md` entry first, re-read it, then flip or remove the `TODO.md` status. Task descriptions are never deleted or rewritten; obsolete tasks move to a TOMBSTONES section with a reason.
3. **Read the whole file before editing it,** in 800-line chunks. No edits from a partial read.
4. **No tests.** Matches `CONTRIBUTING.md` ("Do not add/run tests without owner direction"). Verification is: compile against the pinned Core references, read the compiler output, inspect the package manifest, review neighbouring callers. Runtime behaviour is owner-launched acceptance only. **One scoped exception exists** — owner decision 20 (2026-09-29) authorises automated fixtures for the single Phase 6 row on deterministic room generation, gate transitions, ledger idempotency, transfer receipt IDs and schema migration, and defers all of it until after the owner's first launch. It covers that row alone and is not permission for a general test suite.
5. **Docs before push, atomically.** Every document that describes touched behaviour updates in the same commit as the code: the implementation record, the master TODO checkboxes, `TODO.md` / `FINALIZED.md`, `ARCHITECTURE.md` if structure changed, `CHANGELOG.md` and `About.xml` if the version changed, `README.md` if anything player-facing changed.
6. **Git Flow.** *(Branch names superseded on 2026-10-10: the integration branches are lowercase `develop` and `main`, reached by pull request; the capitalised `Main`/`Develop` were archived as `archive/*-do-not-use`; Forgejo is held since 2026-10-06. The rest of this item is kept as history.)* Work only on `feature/*` branches (currently `feature/connected-colony-portals`; `PUBLISHING.md` examples name the handoff branch, so substitute whichever branch you are on). Publication follows the project's existing cascade `feature/connected-colony-portals → Prep → Develop → Main`, run separately on the `forgejo` and `github` remotes, never force-pushed, with every resulting remote ref read back. Note the project's integration branches are capitalised (`Prep`, `Develop`, `Main`) while `.claude/project-config.json` names `main` / `develop`; the project cascade is the one that exists on the remotes.
7. **No task numbers or people's names in shipped files.** Source code, XML, launchers, `README.md` and anything under `Mod/` describe what the code does, never who asked. Workflow docs and commit messages may carry them.
8. **No AI attribution** in commits, PR bodies, comments or shipped artifacts.
9. **Cross-platform case insensitivity.** Never create two paths differing only by case; references match on-disk casing exactly.
10. **The `.claude/` folder is a proprietary workflow harness, and in this repository it IS tracked.** The owner opted in on 2026-09-28 after both remotes verified private (audit entry in `FINALIZED.md`). The owner's rule: the whole Backrooms folder always gets pushed, except obvious dependencies, node stuff, logs, temps, cache-like files and auto-generated configs that are not product-ship-worthy. Inside `.claude/` that means only the harness's session-state files and personal files (`settings.local.json`, `.env`, `user.json`, `user-context/`) stay ignored. The Layer 1 guard hook still re-checks every remote on each `.claude/`-touching git operation and blocks if anything turns public.

## 4. Project rules that never move

Straight from `AGENTS.md`, because a build agent forgets these at its peril:

- **Reuse first, and original content where the role needs it.** The existing-content-only rule was reversed in part on 2026-10-06 ([`CONTENT_REUSE_POLICY.md`](CONTENT_REUSE_POLICY.md)): the mod ships its own art, audio, items, benches and terrain again. Reuse is still the default and an original def is justified by a role nothing fills, never by wanting to attach a texture. **Never copy another package's assets** — that clause did not move. **And things rotate**: a `Graphic_Multi` of ours carries `_north`, `_east` and `_south` or the build fails.
- **Connected colony gates** supersede dispatch-only ordinary travel ([`CONNECTED_COLONY_PORTALS.md`](CONNECTED_COLONY_PORTALS.md)). Natural gates are permanently open. One local branch's labour and materials work across a live connection without crew manifests.
- *Superseded on 2026-10-06 by the owner's direction that the local player may launch and play ([`DECISIONS_CURRENT.md`](DECISIONS_CURRENT.md)); the owner's own saves are never overwritten. Kept as history:* **Only the owner launches RimWorld,** through RimSort, with the 295-entry product target. A build agent never starts the game, never edits the active mod list, never attaches RimBridgeServer outside the saved QA plan. A successful compile is compiler evidence only.
- **Regression containment** ([`REGRESSION_CONTAINMENT.md`](REGRESSION_CONTAINMENT.md)): every task records baseline commit, owned paths, affected callers and saved fields, deliberate changes, preserved behaviour, evidence, remaining runtime cases, and the master TODO update.
- **Save contracts.** Scribe keys start `rr_`, Def names and language keys start `RR_`, schema versions are explicit integers, and a written key is a contract that needs a migration before it changes ([`SAVE_MIGRATION_POLICY.md`](SAVE_MIGRATION_POLICY.md)).
- **Owner decisions D1–D9 and S1/B are fixed** unless the owner changes one and it is recorded in [`GATE_0_DECISIONS.md`](GATE_0_DECISIONS.md) and propagated. Do not revive an older proposal because it appears in a draft. **D1 changed on 2026-09-29:** public Steam Workshop is the first distribution target, replacing the private RimWorld Together prototype. D2–D9 and S1/B are unchanged.

## 5. How the previous agent laid out work, and how to keep doing it

Each build wave followed the same document rhythm, visible in `docs/implementation/`:

1. A **task record** (`PHASE_n_<AREA>_TASK.md` or `CONNECTED_COLONY_IMPLEMENTATION_TASK.md`) naming baseline commit, feature IDs, exclusive file scopes, regression obligations and the acceptance cases it will not run.
2. One or more **source reviews** (`*_SOURCE_REVIEW.md`, `CONNECTED_WORK_CORE_API.md`) pinning the exact Core/mod source inspected under `.local/inspection-*/` and separating verified facts from inferences.
3. An **implementation record** per system (`*_IMPLEMENTATION.md`) with saved keys, failure boundaries and explicit "not yet" limits.
4. A **build record / checkpoint** (`PHASE_n_BUILD_RECORD.md`, `CONNECTED_COLONY_CHECKPOINT.md`) with compiler output, source/package/reference manifests and a staging receipt saved under `evidence/<name>-<date>/`.
5. **Master TODO** bounded subitems ticked with their evidence link; broad parents left open.
6. Version bump in `About.xml` + `CHANGELOG.md`, then one **cascade publication** per remote.

Keep that rhythm. The workflow ledger adds the verbatim-quote discipline, the four-tier queue and the permanent archive on top of it; it does not replace the task-record pattern.

## 6. Build, package, stage

From the repository root in PowerShell (details and failure modes in [`BUILDING.md`](BUILDING.md)):

```powershell
./tools/build.ps1                # restore (locked), compile, package the allowlist
./tools/build.ps1 -NoRestore     # already-restored, unchanged project
./tools/stage-mod.ps1            # copy ONLY Mod/Rimrooms - Async Industries/ to RimSort's Local Mods
./tools/stage-mod.ps1 -UpdateExisting   # after inspecting an existing install; backs it up first
```

Requirements: .NET SDK 9.0.308 (via `global.json`), a locally installed RimWorld 1.6 whose Core DLL hash matches the pin, PowerShell. The build treats warnings as errors and refuses a changed Core pin. Output goes to `artifacts/build/` (manifests) and `Mod/Rimrooms - Async Industries/1.6/Assemblies/` (the DLL, gitignored). Package contents are governed by `tools/package-files.json`.

## 7. Publishing a milestone

Only after a substantive milestone is integrated and its evidence is saved (`AGENTS.md` publication cadence). Batch source, contracts, master TODO ticks, `TODO.md` / `FINALIZED.md`, build record and evidence into one commit on the feature branch. Then follow [`PUBLISHING.md`](PUBLISHING.md), starting with its 2026-10-10 supersession note (lowercase `feature/*` → `develop` → `main`, no mod-only repository, Forgejo held). *Historical procedure, superseded on 2026-10-10:* push the feature branch to `forgejo` and `github` by name, cascade `feature/connected-colony-portals → Prep → Develop → Main` on each remote by refspec (fast-forward only, no local integration branches, never force), read back all eight refs, and do not edit files after the push. Check `git config user.name` / `user.email` resolve to your own identity before committing.

## 8. Installed workflow reference docs

The template also dropped these reference files into `docs/` and the repo root; they document the Claude Code harness rather than the mod: `HOOKS.html` (hook event reference), `STATUSLINE.md`, `SPINNER-VERBS-SETUP.md`, `ADMIN-ONBOARDING.md`, plus `install-unity-globally.ps1` / `.sh` and `ForgejoUserSetup.ps1` at the root. Under the owner's whole-folder rule they are tracked alongside `.claude/`; they ship with the next milestone commit like everything else.
