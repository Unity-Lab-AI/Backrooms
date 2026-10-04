# Deeper Backrooms background artwork — 2026-10-04

**Status:** complete for six original images and local package integration. Earlier rejected candidates remain unshipped. Native presentation acceptance remains open.

## Owner direction

**Verbatim request:** "okay i think it fixed those slideart issues so check it  out again and review the existing slide art... we are going to make about 5-8 more but we want the backrooms psychologically disterbing rimworld esk like feel maybe some red splaters here or ther a few with backrooms like dark and creepy vibe currently sall the slideshow images are tame and all are homely showing the gate, what about "deeper into the backrooms Universe" a few with the pawns freaking out, there are many mental states in rimworld and everyone so rar  looks uneffected by the strange oddity that is the backrooms, so we need more of the stuff (events random) that the player can experience in the mod. so lets begin doing what we need to do to add more images for the game/mod to use as backgrounds on loading and menu screens where backdrops are already used. this is a wild game and even a wilder mod, so lets keep it all themed as such making the additional images for the Mod Rimrooms -Async Industries"

**Verbatim clarification:** "unsettling situuations not just archeteture"

**Verbatim correction:** "hold up those are too realism the current set need to match the style with are more arty"

**Verbatim stop:** "scrap those u just did"

**Verbatim resume:** "come on ur burtrning my tokens!!! make thew artworks for the Mod already"

**Verbatim pilot correction:** "hold up thats a duplicate of one we already have dont do that"

The [initial provenance record](../../../../outputs/menu-art-2026-10-04/prompts-and-provenance.json) preserves the rejected batch. A subsequent pilot using `RR_Menu_FieldSurvey_v2.png` as an input was rejected as duplicative and is also unshipped. The revised direction is entirely new scenes and compositions with simple painted figures, visible brushwork and unsettling situations matching the original set's style.

## Scope and baseline

- TODO: the bounded six-background addition in [the working queue](../../../TODO.md), under master TODO [Phase 5 presentation](../../../PREPRODUCTION_AND_IMPLEMENTATION_TODO.md#phase-5--complete-company-command-interface-and-polish). Feature IDs: **RR-UI / RR-STYLE**.
- Baseline: commit `0737357114606bed8a88046f956a7eb860085e5d`, **0.12.83-dev**. This record does not rebuild or replace the assembly. Concurrent unrelated planner/probe work stays with its existing owner.
- Contracts: [content-reuse exception](../../../CONTENT_REUSE_POLICY.md#menu-backgrounds-and-package-presentation), [menu art brief](../../../MENU_ART_BRIEF.md), [style brief](../../../research/VISUAL_AUDIO_STYLE_BRIEF.md#main-menu-background-slideshow), [accessibility brief](../../../research/CONTENT_ACCESSIBILITY_BRIEF.md), [regression containment](../../../REGRESSION_CONTAINMENT.md).
- Exact register relevance: row **4 / `Ludeon.RimWorld`** owns the native menu/window rendering surface. Row **203 / `Mlie.ShitRimworldSays`** is a loading-screen utility to retain in later profile acceptance, not an image provider or a new dependency. `register-query.py trace RR-UI` returned 24 rows and `trace RR-STYLE` 16 on this date; this art addition changes no provider adapter or dependency declaration and copies no provider assets.
- Exclusive art ownership: lead owns the six package PNGs and `outputs/menu-art-2026-10-04-revised/` prompts, image masters, hashes, previews and validation outputs. Documentation integration owns this record, `docs/MENU_ART_BRIEF.md`, `tools/package-files.json`, `docs/research/provenance-register.csv`, the new working-queue row and its eventual `docs/FINALIZED.md` archive. No C# or gameplay Def change is intended.

## Shared rendering path and preservation

`Presentation/RimroomsSlideArt.cs` owns the `UI/Menu` folder, required `RR_Menu_` prefix, ordinal ordering, cached discovery, cosmetic random selection and `FullScreenRect` crop calculation. `RimroomsMenuBackground` reads that shared list; `Dialog_RimroomsGenerationNotice` chooses one shared slide per notice. Additional PNGs in the same folder are discovered without adding a C# filename list. The manifest must list only files that actually exist.

The existing six assets are preserved: `CorridorEncounter`, `FacilityThreshold_v2`, `FieldSurvey_v2`, `IndustrialGateLogistics`, `LaboratoryOperations`, and `SilentRecovery`, all with the `RR_Menu_` prefix. Preserve 30-second dwell, two-second fade, random entry point, reduced-motion still, slideshow disable, native background fallback, DLC hover behavior and other renderer ownership.

The generation notice uses a centered **560-pixel-wide** text panel with variable height. Place the dramatic subject toward the right with calm space behind the left-third menu controls, while keeping the situation legible if the notice covers the center. `FullScreenRect` fills and crops; it does not letterbox. Static crop previews cannot establish actual native overlay readability.

This is an art-pool expansion for the surfaces already using it. The notice appears before Operations-origin generation. Core owns the subsequent long-event wait box, and the still-open tick/job-driven generation announcement work is not completed by adding images.

## Situation and source grounding

Use original painterly RimWorld-scale figures and ordinary institutional equipment; no borrowed game images, film frames, wider-community named entities or new gameplay assets. Show **people reacting to a situation**, with architecture serving the scene. Small blood splashes/trails and disturbing recovery imagery are owner-authorized; the palette and body language should carry the unease without graphic close-ups.

Current source contains `RR_Anomaly_LightsFail` / `RR_Anomaly_Blackout`, neutral `RR_Inhabitant_Echo`, survivors and dead-crew inhabitants, sealed mineable rooms and cinema/ward/service room archetypes. `RR_BackroomsPressure` supplies mood stages from **-1 to -10**, which coexist with RimWorld's ordinary emotional consequences. Paintings of panic, grief or shutdown are expressive depictions of that play context; they do not add or promise a new scripted mental-state event, hallucination system or monster. An echo remains a neutral familiar stranger, not an attacker. No scene should imply inhabitants cross an open gate by themselves.

## Integrated package outputs

All six files exist under `Mod/Rimrooms - Async Industries/1.6/Textures/UI/Menu/`, each **1672 × 941** at native generated resolution and copied byte-for-byte without transformations:

| Package file | Painted situation |
|---|---|
| `RR_Menu_PanicJunction.png` | An explorer hides beneath an overturned office desk while a companion tries to coax them out. |
| `RR_Menu_LightsOut.png` | Frightened crew members cling together around their only lamp after a maintenance-room blackout. |
| `RR_Menu_EmptyCinema.png` | A companion kneels beside a collapsed pawn in a cinema aisle; one distant figure remains seated. |
| `RR_Menu_FamiliarStranger.png` | A neutral echo of someone who should be at home confronts a shaken crew's expectations. |
| `RR_Menu_BreachedVault.png` | Mining opens a sealed room and reveals a disturbing discovery beyond the ore. |
| `RR_Menu_RedTrail.png` | A crew carries an injured companion through a deserted cafeteria, leaving small blood traces. |

`RR_Menu_MirroredWard.png` and `RR_Menu_BreakingPoint.png` belonged to the original eight-scene plan and are withdrawn, not missing package files. Six additions satisfy the requested 5–8 range. [Revised provenance](../../../../outputs/menu-art-2026-10-04-revised/prompts-and-provenance.json) records exact prompts, native dimensions and SHA-256 hashes. All final scenes were generated from text without reference images. The [verification record](../../../../outputs/menu-art-2026-10-04-revised/verification.json) records the unchanged original six.

## Acceptance and recovery

- Confirm every accepted PNG opens, record its actual dimensions/bytes/SHA-256, and visually inspect the images and menu/notice crop previews.
- Add existing accepted files to the package allowlist and append their original-generation provenance rows. Check package integrity and the existing menu-art static verifier; save actual outputs. These are package/source checks, not gameplay acceptance.
- Preserve the initial six files byte-for-byte. The addition changes no saved fields, IDs, pawn state, provider bindings, scenario choices, gameplay mechanics or dependency requirements. No save migration is needed.
- Recovery is to remove a rejected new slide from this batch and its allowlist entry together while retaining its source evidence; the unchanged native/missing-art fallbacks still belong to the renderer.
- Keep runtime checks open: actual menu and generation-notice readability at supported aspect ratios/resolutions/UI scales; DLC hover; reduced motion; disable/re-enable; native fallback; other menu-owner/profile behavior. Only owner-launched RimSort sessions establish those results.
- No game launch, active profile/settings modification, staging, version bump, commit or remote cascade is part of this one-task art batch. The standing publication cadence requires 10–12 archived work items.

## Result

Six final PNGs have package-allowlist and provenance CSV entries. Their dimensions and SHA-256 hashes independently match the lead's generation record; the original six are unchanged. The lead visually inspected all six new compositions. The initial realistic drafts and duplicative pilot remain rejected and unshipped.

Saved checks all exit **0**: [menu-art proof](../../../../outputs/menu-art-2026-10-04-revised/slide-proof.txt) confirms **12 slides** and the shared loader; [package integrity](../../../../outputs/menu-art-2026-10-04-revised/package-integrity.txt) confirms **98 package files / 12 textures**; [diff check](../../../../outputs/menu-art-2026-10-04-revised/diff-check.txt) reports no whitespace faults. [Verification](../../../../outputs/menu-art-2026-10-04-revised/verification.json) preserves hashes and original-six comparisons. No C# changes, build, game launch, staging, version bump or publication was performed for this art task.

This closes one bounded artwork/package task and moves its exact owner directions to `docs/FINALIZED.md`. Actual menu/notice overlays, crop/UI-scale/profile acceptance and the broad slideshow runtime rows remain open.
