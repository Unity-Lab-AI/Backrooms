# Authored rotation and journal artwork pipeline

## Task and scope

Owner requests, verbatim:

> hold up the assets folder has assets did you make those? do we need to make the missing ones with all the work claudse did

> gate size variants too right and any other things we need like journal and such and converting into game world

Owner's journal choice, verbatim:

> Paper field journal with matching closed, open and upright views (Recommended)

Feature IDs: RR-STYLE, RR-GATE, RR-RES and RR-EVD. Source baseline: commit `b1ee3d6`, package version `0.13.0-dev`. The original inventory/tooling task has expanded into original equipment facings, paper-journal graphics and footprint-specific cosmetic gate frames. Concurrent workflow edits are preserved; this record does not close the master TODO or any runtime gate.

Inputs: [content policy](../CONTENT_REUSE_POLICY.md), [original-content implementation](ORIGINAL_CONTENT_IMPLEMENTATION.md), [regression containment](../REGRESSION_CONTAINMENT.md), [feature map](../FEATURE_TRACEABILITY.md), [original art provenance](assets/phase2-original-art.json) and [audio provenance](assets/phase2-original-audio.json). The October 6 policy reversal governs original gameplay art; earlier retirement records remain historical evidence.

Applicable provider reviews remain row 53 Big Little Mod Patch for bench work, row 49 Better Electronics for power, and row 148 No Quests Without Comms for the console and independent company objectives. Native doors retain the boundaries of rows 77, 185, 201, 252, 265 and 273. No provider art or source is copied, no door Def is cloned, and this artwork does not change gate physics, route ownership or native access permissions.

## Current equipment inventory

All thirteen original Phase 2 PNG masters and four WAV masters remain preserved. The six formerly fixed-facing buildings now have their twelve authored north/back and east/side masters, eighteen derived north/east/south package frames, `Graphic_Multi` and rotation enabled. Existing unsuffixed masters supply the south/front view; RimWorld mirrors west from east.

| Object | Existing north/back master | Existing east/side master | Derived package folder |
| --- | --- | --- | --- |
| Gate console | `assets/source/phase2/RR_GateConsole_north.png` | `assets/source/phase2/RR_GateConsole_east.png` | `1.6/Textures/Things/Building/Rimrooms/` |
| Utility generator | `assets/source/phase2/RR_UtilityGenerator_north.png` | `assets/source/phase2/RR_UtilityGenerator_east.png` | same |
| Analysis bench | `assets/source/phase2/RR_FieldAnalysisBench_north.png` | `assets/source/phase2/RR_FieldAnalysisBench_east.png` | same |
| Field recorder | `assets/source/phase2/RR_FieldRecorder_north.png` | `assets/source/phase2/RR_FieldRecorder_east.png` | `1.6/Textures/Things/Item/Rimrooms/` |
| Evidence case | `assets/source/phase2/RR_SealedEvidenceCase_north.png` | `assets/source/phase2/RR_SealedEvidenceCase_east.png` | same |
| Survey tag | `assets/source/phase2/RR_SurveyTag_north.png` | `assets/source/phase2/RR_SurveyTag_east.png` | same |

Source-to-facing mappings, prompts, inspected references and native image metadata are recorded in [building rotation provenance](../../assets/source/phase2/building-rotation-provenance-2026-10-06.json) and [field-kit rotation provenance](../../assets/source/phase2/kit-rotation-provenance-2026-10-06.json). Those records also name presentation limitations; authored rear/side views are not a gameplay acceptance claim.

The original fixed-facing package PNGs are preserved outside the mod in [the fixed-facing archive](historical-content/fixed-facing-equipment-2026-10-06/). Source masters are unchanged. Object mass, footprint, power, storage/facility components and native interaction offsets are retained. The bench remains 2x1 and turns to 1x2; its east output is fitted to the swapped footprint.

The [initial cutter report](evidence/authored-rotations-2026-10-06/cutter-report.txt) is **historical**: it observed twelve missing drawings before generation and wrote nothing. Earlier text counted fourteen across seven buildings by including `RR_MachineGate`; [GateArt.cs](../../src/RimroomsAsyncIndustries/Gate/GateArt.cs) uses that image only as a flat designation icon. The cutter classifies it as an icon, so it contributes no building-rotation gap. New world gate frames are a separate asset family below.

The Quiet Pursuer master remains deliberately held under [decision 25](../GATE_0_DECISIONS.md#decision-log). No new creature presentation is introduced by this wave.

## Paper field journal

Seven original masters exist under [assets/source/journal](../../assets/source/journal/), with [prompts and provenance](../../assets/source/journal/provenance.json):

- `RR_CompanyJournal_Closed.png` for the ground sprite and UI icon.
- `RR_CompanyJournal_Open_north.png`, `_east.png`, `_south.png` for reading.
- `RR_CompanyJournal_Vertical_north.png`, `_east.png`, `_south.png` for upright presentation.

Each is converted to a 128-pixel package texture under `1.6/Textures/Things/Item/Rimrooms/Journal/`. The [journal Def](../../Mod/Rimrooms%20-%20Async%20Industries/1.6/Defs/ThingDefs_Items/RR_CompanyJournal.xml) uses matching closed, open and vertical paths; the latter two are `Graphic_Multi`. The previous cassette texture is retained in [the cassette archive](historical-content/journal-cassette-2026-10-06/RR_RouteRecording.png), and its original source master remains preserved.

`RR_RouteRecording`, `BookBase`, `RimroomsRecordBook`, `CompBook`, quality, native hauling, the evidence component and all saved keys remain intact. The recipe and description now identify a paper journal. [CompRouteEvidence.cs](../../src/RimroomsAsyncIndustries/Investigation/CompRouteEvidence.cs) checks the existing central `RimroomsMod.PackageId`, matching `About.xml`, instead of the obsolete package literal. This restores recognition of the company's own current Def while retaining the native textbook fallback and historical-carrier recovery shape. It does not add a retired-package metadata alias or establish old-save compatibility.

The journal increment compiled with zero warnings/errors and was staged as a 140-file package before equipment/gate-frame integration. That is an earlier bounded build result; the combined package needs a new successful manifest and staging receipt before launch.

## Gate sizes and cosmetic world frames

[GateFootprint.cs](../../src/RimroomsAsyncIndustries/Gate/GateFootprint.cs) supports 1x1, 1x2, 1x3 and 2x3, including their rotated equivalents. Native doors and bound adjacent door runs provide the apertures; [NativeGateBinding.cs](../../src/RimroomsAsyncIndustries/Gate/NativeGateBinding.cs) limits a branch to three operational gates. This is existing source behavior, not a new custom-door family.

The four-size frame family is implemented as twelve original north/east/south drawings under [assets/source/gates](../../assets/source/gates/) with [prompts, references and provenance](../../assets/source/gates/provenance2026-10-06.json). [The gate cutter](../../tools/cut-gate-frames.py) preflights all twelve masters, exact runtime consumers and transparent aperture centers before writing. It clears RGB hidden beneath alpha zero during conversion, crops the hardware and exports 128 pixels per cell to `1.6/Textures/Things/Building/Rimrooms/Gates/`. North/south use long-side by short-side dimensions; east swaps them. Masters remain untouched.

[GateWorldFrames.cs](../../src/RimroomsAsyncIndustries/Gate/GateWorldFrames.cs) adds `CompRimroomsGate.PostDraw`, drawing one cached, white cutout frame on a designated native door-run host. It uses `nativeBoundRotation`, the full `GateOccupiedRect` geometric center including even-cell footprints, and cardinal textures without a second mesh rotation. West mirrors east UVs. Every occupied cell must be revealed and on the current map. Missing cardinal sets, malformed aspect, unsupported footprint or an orientation that cannot match the frame retain native door rendering. Depth-aligned runs intentionally omit the trim; providers bypassing the base draw hook may also omit it. No run, route, collision, access, power or campaign save state is added.

`GateFramesEnabled` is an additive mod preference, default true, serialized as `rr_gateFramesEnabled` in [RimroomsSettings.cs](../../src/RimroomsAsyncIndustries/Core/RimroomsSettings.cs), with a localized checkbox in [RimroomsMod.cs](../../src/RimroomsAsyncIndustries/Core/RimroomsMod.cs) and `RR_NativeGate.xml`. It is independent of the existing aura and reduced-motion preferences. Native tint, aura and real door leaves remain. A frame is cosmetic and does not imply an active connection.

Pinned local Core source inspection: `Building_Door.DrawAt` calls `Comps_PostDraw`; `DoorPreDraw` can overwrite the live door rotation; multi-tile/supported doors reach the hook through their base calls; supported door tops use Blueprint altitude. The frame follows that layer plus `Altitudes.AltInc`. `MeshPool.GridPlane(size, flip)` supplies the physical rectangle and mirrored UVs. Appearance, occlusion and third-party provider behavior still require owner-launched observation.

## Implemented cutter and package behavior

- [The cutter](../../tools/cut-phase2-art.py) excludes interface icons from building rotations and counts absent authored views individually.
- Explicit `graphicData`, `openGraphic` and `verticalGraphic` class/path pairs activate authored `Graphic_Multi` output. Draft facings for a `Graphic_Single` remain outside the package.
- Each active facing is checked, decoded and fitted before package writes. Missing, unreadable or empty authored views cause refusal; no fake replacement is supplied.
- East building frames use the swapped rectangular footprint. The existing cutoff/beacon uniform derivation, fluorescent flat rotation and seamless carpet derivation are preserved.
- The provenance checker now accepts the exact facing master before the unsuffixed fallback used by uniform/flat derivatives. The journal's genuine directional masters therefore are not false orphans.
- [The package allowlist](../../tools/package-files.json) includes the new equipment and journal paths; obsolete fixed-facing/cassette package files are archived rather than deleted without evidence.
- The activated equipment/journal conversion has been exercised with real masters and wrote 36 textures before the gate-frame batch. This is a conversion observation, not a game result.

The parser covers explicit shipped XML graphics; inherited or runtime-patched graphics require separate review. Independent trimming/centering does not prove that sprites have identical apparent scale or origin across facings.

[Package integrity](../../tools/check-package-integrity.py) was updated because the first run treated the three genuine journal texture stems as undeclared Defs and reported directional/code textures as unnamed. The [initial result](evidence/authored-rotations-2026-10-06/package-check-before-scanner-update.txt) is preserved. Asset leaf values now undergo texture/audio validation separately from Def tokens; multi-facing XML requires all three cardinal files; literal/constant C# content lookups and the bounded gate-frame constructor table are recognized. This is bounded source inspection, not general C# data-flow analysis. An explicit `--rimsort-settings` option permits installed-copy comparison without altering sandbox or manager settings. Genuine missing Def, cardinal texture and clip references remain failures.

Final targeted checks passed: [package integrity and installed-copy comparison](evidence/authored-rotations-2026-10-06/package-check-output.txt), [register/provenance](evidence/authored-rotations-2026-10-06/register-check-output.txt), [keyed strings](evidence/authored-rotations-2026-10-06/keyed-check-output.txt) and [asset catalog agreement](evidence/authored-rotations-2026-10-06/asset-page-check-output.txt). The package contains 52 original gameplay assets, including four existing cues; all have masters and no gameplay texture exceeds 1024 pixels per axis. These results do not establish game rendering or profile compatibility.

## Completion evidence and acceptance still open

- [x] Correct the gate icon classification and historical absent-frame count.
- [x] Implement authored discovery, explicit activation and safe preflight.
- [x] Author and inspect twelve equipment views; preserve prompts and source-to-facing provenance.
- [x] Enable rotation on the six existing objects and convert eighteen package facings; preserve original fronts and archive superseded fixed-facing package output.
- [x] Author, bind and convert the seven paper-journal views; preserve Def/state identity and fix the current package guard.
- [x] Exercise equipment/journal conversion with real masters. The initial report remains historical evidence only.
- [x] Finish the four-size cosmetic gate-frame source/package integration, with actual renderer/cutter/settings paths and twelve converted package textures.
- [x] Save combined build and staging evidence under [the evidence folder](evidence/authored-rotations-2026-10-06/): [build output](evidence/authored-rotations-2026-10-06/build-output.txt), [gate conversion](evidence/authored-rotations-2026-10-06/gate-conversion-output.txt), [package manifest](evidence/authored-rotations-2026-10-06/package-manifest.json), [reference manifest](evidence/authored-rotations-2026-10-06/reference-manifest.json), [staging output](evidence/authored-rotations-2026-10-06/staging-output.txt) and [staging receipt](evidence/authored-rotations-2026-10-06/staging-receipt.json). The final combined build has zero warnings/errors and 164 approved files, all hash-checked after staging through the real RimSort settings. No game is launched or profile changed by those commands.
- [ ] Owner-launched acceptance: all four equipment facings at normal zoom; sprite scale/origin; console/bench interaction access; bench rectangular placement; storage/facility links; uninstall/minify/carry/reinstall; power and optional-provider behavior.
- [ ] Owner-launched journal acceptance: closed ground/icon appearance, all open/upright facings, native book reading, company issuance, field recording, physical custody, analysis and save/reload.
- [ ] Owner-launched gate acceptance: all four footprints/orientations, bound runs and native providers, native door animation/access, frame disable/fog behavior, arrival/return cells and unchanged physical crossings.

No in-game result or compatibility pass is recorded. The full mod objective and broader release/runtime acceptance remain open. No publication is performed by this artwork wave.
