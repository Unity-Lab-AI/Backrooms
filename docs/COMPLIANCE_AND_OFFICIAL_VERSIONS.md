# Compliance: RimWorld and Steam terms, and official versions only

**Binding owner requirement, 2026-09-28, verbatim:**

> make sure we are foillowing all rimworld and steam TOS and requirments when it comes to issues similar and the issue of factions and pawn heduffs and the like this mod has to be working with official versions

This file is the position, the **verification behind it**, and the rules that bind every def the mod adds from here on — starting with the faction layer, which must not be authored until these rules are read.

Verified at 0.5.6-dev against the actual package on disk. Where something cannot be established by inspection it is listed as an owner question rather than asserted.

---

## Why this matters before the faction work, not after

A `FactionDef` needs a faction icon and pawn kinds. The lazy way to get an icon is to copy a PNG out of the game's own folders into the mod package. **That single act would be redistribution of Ludeon's assets** — a licence violation, a Workshop takedown risk, and the kind of thing that is trivial to do by accident and expensive to undo after release.

The decision already recorded in [`GATE_0_DECISIONS.md`](GATE_0_DECISIONS.md) — factions reference **existing icon paths and existing `PawnKindDef`s by name** — is therefore not only a content-policy choice. It is the compliant choice, and it is now also a compliance rule.

## Verified position at 0.5.6-dev

Each row was checked against the package and source, not recalled.

| Requirement | Status | How it was checked |
|---|---|---|
| Targets official RimWorld only | **Pass** — `supportedVersions` is `1.6` alone; `LoadFolders.xml` maps `v1.6` → `1.6` | `About/About.xml`, `LoadFolders.xml` |
| No required third-party mod | **Pass** — zero `modDependencies`, `loadAfter` is `Ludeon.RimWorld` only | grep of `About.xml`: 0 matches for `modDependencies` / `incompatibleWith` |
| No game or DLC asset redistributed | **Pass** — all 18 non-XML package files are ours: 14 historical `RR_` gameplay PNGs, 2 original `RR_Menu_*` images, `About/Preview.png`, `About/License.txt`, plus our own compiled assembly | enumerated the 76-entry approved package list; every texture is `RR_`-prefixed |
| No Core texture copied in under a new name | **Pass** — no `texPath` anywhere points at a non-`RR_` path | grep of every package XML for `texPath` excluding `RR_`: 0 results |
| No Core or DLC def overwritten or deleted | **Pass** — the only patch operations used anywhere are 4 × `PatchOperationAdd`, 2 × `PatchOperationConditional`, 1 × `PatchOperationSequence`. **There is no `PatchOperationReplace` and no `PatchOperationRemove` in the package.** | grep of all package XML for `Class="Patch*"` |
| No DLC content required or referenced from XML | **Pass** — zero references to Royalty, Ideology, Biotech, Anomaly or Odyssey in any package XML | grep across `1.6/` |
| No DLC assembly referenced from code | **Pass** — the single DLC-adjacent code path is `pawn.Ideo` in `ConstructionFinishingProvider`, and it is null-guarded. `Ideo` is a type in the official `Assembly-CSharp`, present with or without Ideology; without the DLC `pawn.Ideo` is simply null | grep of all C# for `ModsConfig.` / `.Ideo` / `*Active`: 1 result |
| Official game assemblies only, unmodified | **Pass** — 5 reference assemblies, all from the official install, hashes recomputed each checkpoint with no drift | `docs/implementation/evidence/*/reference-manifest.json` |
| No game assembly patching | **Pass** — no Harmony, no detours, no reflection writes into game types; behaviour is added through Core's own `ThingComp`, `GameComponent`, `WorkGiver`, `JobDriver` and `Def` extension points | audited in [`DEPENDENCIES_AND_CAPABILITY_MATCHING.md`](implementation/DEPENDENCIES_AND_CAPABILITY_MATCHING.md) |
| No game binary or data bundled | **Pass** — the package contains no game file of any kind | approved package list |
| No third-party mod code or asset copied | **Pass** — no mod source or asset is vendored. Noted specifically because **Stargates! (profile row 218) is GPL-3.0**: copying from it would force this mod to GPL. It is explicitly not a dependency and nothing is taken from it | dependency audit, per-mod review rows |
| Our own licence, stated | **Pass** — MIT, in `About/License.txt` | file present in the package |
| QA overlay not shipped | **Pass** — the rim api / RimBridgeServer overlay is not in the package and is not declared a dependency; it is a separate owner-attached QA tool | approved package list; `research/RIMBRIDGE_TEST_HARNESS.md` |

## Rules that bind every def added from here on

These apply to the faction layer, to pawn hediffs, and — per the owner's *"and the like"* — to every def class the mod may add later: thoughts, traits, backstories, incidents, quests, world objects, research projects, precepts, anything.

1. **Add definitions. Never redistribute assets.** A new def is our own work and is fine. A copied PNG, WAV, or chunk of XML out of the game or another mod is not, whatever it is renamed to.
2. **Reference existing content by name and by path.** A `FactionDef` points its `pawnGroupMakers` at existing `PawnKindDef`s by defName and its icon at an existing texture path. A string that names Ludeon's asset is a reference; a copy of the file is redistribution. This distinction is the whole rule.
3. **Never `PatchOperationReplace` or `PatchOperationRemove` on a Core or DLC def.** Additive patches only, wrapped in `PatchOperationConditional` where the target may be absent. The package currently contains zero destructive operations and must stay that way — it also happens to be why load-order conflicts stay rare.
4. **Gate DLC-conditional content with `MayRequire`.** The official mechanism is `MayRequire="Ludeon.RimWorld.<Dlc>"` on a def or a list element, with `MayRequireAnyOf` for alternatives. Core and the DLC use it nearly two thousand times in their own data, so it is not a convention but the supported path. The official package ids are exactly `Ludeon.RimWorld.Royalty`, `Ludeon.RimWorld.Ideology`, `Ludeon.RimWorld.Biotech`, `Ludeon.RimWorld.Anomaly`, `Ludeon.RimWorld.Odyssey`. **Never make DLC content reachable without the DLC**, and never ship a DLC asset to a player who does not own it.
5. **A hediff, or anything attached to a pawn, must degrade to nothing.** A missing def is an unavailable effect, never an exception — the project already enforces `GetNamedSilentFail` everywhere. A pawn carrying our hediff must still load in a save where the mod is removed without corrupting the pawn; that is what the save-migration policy is for.
6. **No modified, patched or unofficial game build, ever.** The mod is developed and released against the official RimWorld and official DLC only. No bundled game file, no assembly rewriting, no dependence on a non-official install layout.
7. **Upload only what we own.** Workshop publication covers our own defs, code, text and original art. Nothing else goes in the archive.
8. **No AI attribution in any shipped artifact** — already a standing project LAW, and it is also the honest position for authorship on a store page.

## Owner questions — cannot be resolved by inspection

These are genuinely the owner's to answer, and none of them blocks further building.

1. **Provenance of the shipping images.** Three image files are intended to survive to release: `RR_Menu_FacilityThreshold_v2.png`, `RR_Menu_FieldSurvey_v2.png` and `About/Preview.png`. They are recorded as original work, not copied. Please confirm how they were produced and that you are content publishing them under your own name. Note that the **14 gameplay PNGs do not survive M2** — the existing-content replacement deletes them — so any question about those is moot for the release package.
2. **Author identity on the store page.** `About.xml` currently has `<author>Operator</author>`. For publication this presumably becomes your handle or the lab's name. Cosmetic, but it is the credited author of the work.
3. **Licence on release.** MIT is in the package now. Worth a conscious confirmation before publication, since MIT permits anyone to redistribute and relicense derivative builds of the mod's code.

## What this changes in the plan

- The faction rows that were in [`DEFERRED.md`](DEFERRED.md) carry rules 1–4 as authoring constraints, not just as content-policy notes. **`DEFERRED.md` is CLOSED** as of 0.7.x: it holds zero open rows, nothing is ever deferred, and no row may be added to it. Build it, queue it in `TODO.md`, or ask. Those rows were migrated to [`TODO.md`](TODO.md) and the constraints travelled with them.
- M4's DLC layers must use `MayRequire` and must be verified with each DLC absent, which the existing DLC matrix rows already require.
- M6's release rows gain the three owner questions above and a final pass over this table before any Workshop upload.

## Re-verification

Everything in the verified table is mechanically checkable, so it is re-run rather than trusted. The checks are: the approved package list for non-`RR_` assets, a grep of package XML for `Class="Patch"` operations and for `texPath` values outside `RR_`, a grep for DLC package ids in XML, and the reference manifest for assembly drift. Any future checkpoint that adds content re-runs them before publishing.
