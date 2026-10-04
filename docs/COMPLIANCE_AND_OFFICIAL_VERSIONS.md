# Compliance: RimWorld and Steam terms, and official versions only

**Binding owner requirement, 2026-09-28, verbatim:**

> make sure we are foillowing all rimworld and steam TOS and requirments when it comes to issues similar and the issue of factions and pawn heduffs and the like this mod has to be working with official versions

This file is the position, the **verification behind it**, and the rules that bind every def the mod adds from here on — starting with the faction layer, which must not be authored until these rules are read.

Verified at 0.5.6-dev against the actual package on disk. Where something cannot be established by inspection it is listed as an owner question rather than asserted.

---

## Why this matters before the faction work, not after

A `FactionDef` needs a faction icon and pawn kinds. The lazy way to get an icon is to copy a PNG out of the game's own folders into the mod package. **That single act would be redistribution of Ludeon's assets** — a licence violation, a Workshop takedown risk, and the kind of thing that is trivial to do by accident and expensive to undo after release.

The decision already recorded in [`GATE_0_DECISIONS.md`](GATE_0_DECISIONS.md) — factions reference **existing icon paths and existing `PawnKindDef`s by name** — is therefore not only a content-policy choice. It is the compliant choice, and it is now also a compliance rule.

## Verified position — re-run every checkpoint by `tools/check-compliance.py`

**This table used to be dated, and that was the defect.** It was verified at 0.5.6-dev, read as current for **thirty-six checkpoints**, and its own closing section said *"everything in the verified table is mechanically checkable, so it is re-run rather than trusted."* It was never re-run. Over those thirty-six checkpoints **three of its rows stopped being true**: the package went from 76 approved files to 89, the fourteen gameplay PNGs it enumerated were deleted at 0.12.22-dev, and it stated there were **zero** DLC references in package XML while the DLC-gated defs added since are exactly the supported way to write them.

A dated table of mechanical checks is the same defect as a dated count. So the table is now **executable**, and the queue row asked for precisely that: *"one compliance test, applied to all of them."*

```
python tools/check-compliance.py
```

Exit 0 passed, 1 failed, **2 skipped** — and two is not a pass. Three rules are delegated so that no rule has two owners that can disagree about it: hard dependencies and `loadAfter` to `check-register-compliance.py`, DLC gating and the five official package ids to `check-dlc-gating.py`, and what the package may contain to `tools/package-files.json`.

| Requirement | Status | How it was checked |
|---|---|---|
| Targets official RimWorld only | **Pass** — `supportedVersions` is `1.6` alone; `LoadFolders.xml` maps `v1.6` → `1.6` | `About/About.xml`, `LoadFolders.xml` |
| No required third-party mod | **Pass** — zero `modDependencies` as of 0.12.86-dev. `loadAfter` carries **294** entries, which is an ordering preference and not a requirement: a mod manager sorts by it and never demands it | `About.xml`: 0 matches for `modDependencies` / `incompatibleWith`; 294 `loadAfter` entries, of which 293 were hard dependencies until the stand-alone direction |
| No game or DLC asset redistributed | **Pass** — every non-XML file in the **89**-entry package is ours: **6** original `RR_Menu_*` images, `About/Preview.png`, `About/License.txt` and our own compiled assembly. The **14 historical gameplay PNGs this row used to enumerate were deleted at 0.12.22-dev**, replaced by paths read out of Core's own defs | `check-compliance.py`, from `tools/package-files.json` rather than a directory walk |
| No Core texture copied in under a new name | **Pass** — no `texPath` anywhere points at a non-`RR_` path | grep of every package XML for `texPath` excluding `RR_`: 0 results |
| No Core or DLC def overwritten or deleted | **Pass** — the operations in use are **16 × `PatchOperationAdd`, 10 × `PatchOperationConditional`, 1 × `PatchOperationFindMod`, 1 × `PatchOperationSequence`**. **There is no `PatchOperationReplace` and no `PatchOperationRemove` in the package**, and the checker fails the build if one arrives — a replace takes ownership of a def, so the last mod to load wins and every other mod touching it loses | `check-compliance.py` counts them every run |
| DLC content referenced from XML is gated | **Pass, and this row's old text was stale** — it claimed **zero** DLC references. There are now **six**, all of them `MayRequire`: two each for `Ludeon.RimWorld.Anomaly`, `Ludeon.RimWorld.Biotech` and `Ludeon.RimWorld.Odyssey`. `MayRequire` is the official mechanism and Core and the DLC use it nearly two thousand times in their own data, so the correct rule was never *no references* but *no ungated reference* | `check-dlc-gating.py`, which owns this rule |
| No DLC assembly referenced from code | **Pass, and this row's old text was stale** — it said one `ModsConfig` reference; there are **five**: `AnomalyActive`, `BiotechActive`, two `IsActive` for tracked optional mods, and one generic. **Every DLC type this package names lives in the official `Assembly-CSharp`** — there is no separate DLC assembly to reference, which is why the rule holds however many call sites there are. Each is a runtime question answered by the game itself | `check-dlc-gating.py`; enumerated fresh each checkpoint |
| Official game assemblies only, unmodified | **Pass** — **5** reference assemblies, all from the official install, hashes recomputed each checkpoint with no drift. **Zero parsed references now fails rather than passing**: the first version of the check read the wrong manifest key and reported *"0 assemblies, all from the official install"*, which is the exact false-pass shape this file exists to remove | `check-compliance.py` against `docs/implementation/evidence/*/reference-manifest.json`; **exit 2, skipped, when no manifest is present** |
| No game assembly patching | **Pass** — no Harmony, no detours, no reflection writes into game types; behaviour is added through Core's own `ThingComp`, `GameComponent`, `WorkGiver`, `JobDriver` and `Def` extension points. **Reflection is the loophole this now closes:** a `SetValue` into a game type is an assembly modification no dependency list would show | `check-compliance.py` refuses Harmony, MonoMod, a reflection write and a non-public field read |
| No game binary or data bundled | **Pass** — the package contains no game file of any kind | approved package list |
| No third-party mod code or asset copied | **Pass** — no mod source or asset is vendored. Noted specifically because **Stargates! (profile row 218) is GPL-3.0**: copying from it would force this mod to GPL. It is explicitly not a dependency and nothing is taken from it. **The check tests for assertion, not mention** — its first run flagged `ConnectedFoodAdapter.cs`, whose comment says Gastronomy's rights are unresolved *so its code must not be adapted*, which is the sentence the rule wants the code to contain | `check-compliance.py`, with a negator list documented as maintained rather than complete |
| Our own licence, stated | **Pass** — MIT, in `About/License.txt` | `check-compliance.py` reads the file and the licence name |
| No AI attribution in any shipped file | **Pass** — a standing project LAW, and the honest authorship position for a store page. **Nothing had ever checked the package for it**; only commits and documents were considered | `check-compliance.py` scans every shipped XML and text file |
| QA overlay not shipped | **Pass** — the rim api / RimBridgeServer overlay is not in the package and is not declared a dependency; it is a separate owner-attached QA tool | `check-compliance.py` |

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

**It is `tools/check-compliance.py`, and it runs in the standard sweep with the other twelve checkers.** That sentence is the whole of this section now, because the previous version of it described the checks in prose and asked to be trusted — which is how the table above went thirty-six checkpoints without being re-run while saying it was re-run rather than trusted.

The one thing the checker cannot answer is below, and it is not a check.
