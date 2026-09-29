# One tech tree, different starting points (0.9.8-dev)

**Baseline:** `e343c48` (0.9.7-dev, 158 C# files, 79 package files).

**This checkpoint — 0.9.8-dev:** **158 C# source files**, **79 approved package files**. Zero warnings, zero errors, `TreatWarningsAsErrors` on. Assembly SHA-256 `211687673EA54860637418F89D3EFE90436387EDB9BB8284AA84A09A19295B94`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The request

> *"fyi all starts have same tech tree just differnt starting researches finished based on scenerio"*

## Why this, and why now

The recorded order puts new-game playability after M2, and the existing scenario still grants `RR_FieldRecorder`, `RR_SurveyTag`, `RR_ReturnBeacon` and `RR_SealedEvidenceCase` — **legacy gear pending retirement**. Writing two more scenarios that grant the same gear would be building against content about to be removed, which is the exact thing the ordering exists to prevent.

This piece touches none of it. It is the **scenario contract the other two starts will need**, it is an explicit owner direction that was unbuilt, and it can be done in the right order.

## Taken literally, which changed the implementation

The tempting reading is *give each start a list of projects*. That would have made three lists somebody has to keep in agreement, and *"same tech tree"* would have been a convention rather than a fact.

So a start declares **only what begins finished**, and the tree is built from **every `RimroomsProjectDef` the game has loaded**. The tree is therefore identical for every start **by construction**: a scenario cannot declare a different one, because it never declares one at all.

Adding a project later reaches every start at once, and a scenario that forgot to list it **cannot exist**.

## What it replaced

A single hardcoded record:

```
var initialProject = new ProjectRecord { id = newId + ":project:gate_telemetry",
                                         researchDefName = "RR_GateTelemetry" };
```

A second project would have been invisible to every branch until somebody remembered to add it here, in the scenario, and in whatever else read it. That is the kind of thing that is found months later by a player asking why a research project never appears.

Today there is exactly one project def, so **this checkpoint changes no behaviour at all** — the branch still begins with one unfinished `RR_GateTelemetry`. What changed is that it is now derived rather than asserted.

## Two details that matter

**A project that begins finished is also marked insight-committed.** Otherwise the operations window would offer a "start" button on work that is already done — somebody ran this branch before you, and they paid for it.

**Ordinal sort before the list is built.** Def load order varies with the mod list, and two players starting the same scenario must get the same branch. This has been a live trap three times in this code base.

**A named project that no longer exists is reported and skipped, not fatal.** A player should not lose a new colony because a scenario named a project that a content update renamed.

## Not done, and named in `TODO.md`

- **The other two starts** — `furniture_knickknack_store` and `lone_survivor` — which need the field-gear replacement first so they are not written against retiring content.
- **The world tile the branch does not hold**, and the rest of new-game playability.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled **twice** from clean; identical SHA-256.
- All five checkers pass. The start XML parses.
- Compliance: **no new def, asset, patch operation or work type.** One def field, one request field, one method.

## For the post-completion test phase

Confirming a new Async Industries branch still begins with `RR_GateTelemetry` present and unfinished; that adding a second project def makes it appear in a new branch without any scenario edit; that a start listing a project as completed begins with it finished and with no "start" button offered; and that a start naming a project that does not exist logs a warning and begins anyway.
