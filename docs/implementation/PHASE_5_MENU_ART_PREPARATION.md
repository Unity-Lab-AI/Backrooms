# Menu art preparation: facility and field survey

**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](../CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


**Status:** two original image candidates created during the wait for the first owner-launched 0.2.0 session. This is independent asset preparation for RR-UI/RR-STYLE, not Phase 5 completion, gameplay screenshots or an implemented slideshow. The current 61-file package is unchanged.

The [style brief](../research/VISUAL_AUDIO_STYLE_BRIEF.md#main-menu-background-slideshow) owns the slideshow requirements. The [menu extension audit](../research/MENU_BACKGROUND_EXTENSION_AUDIT.md) records the native-background and exact-profile integration questions. Every shipped scenario eventually needs its own image; only Async Industries currently has scenario source.

## Original candidates

- File: [RR_Menu_FacilityThreshold_v1.png](../../assets/source/menu/RR_Menu_FacilityThreshold_v1.png).
- Second file: [RR_Menu_FieldSurvey_v1.png](../../assets/source/menu/RR_Menu_FieldSurvey_v1.png), two field investigators using a recorder, physical evidence case and beacon in a repeated office suite. A distant silhouette suggests the bounded encounter; the doorway marker is an artistic motif, not a promised encoded mechanic.
- Scene: modest research facility, staffed machine gate, equipment case and an institutional corridor beyond the threshold. These depict the current scenario/gate/expedition feature set artistically.
- Built-in imagegen produced the original scene without input images, film frames, screenshots, copied logos or named characters. The prompt describes the project's own gate silhouette. Exact prompt, file hash and dimensions are in [menu art metadata](assets/menu-art-candidates.json).
- Visual inspection: the gate and crew occupy the right half; a low-detail dark region occupies the middle-left for native controls. The image contains no baked menu text. Perspective, cables and amber gate lighting are coherent enough for an initial candidate.
- The tool's actual native dimensions are recorded in metadata. Requested 3840×2160 was not delivered; do not label this a 4K master or a final export. No resize, crop or image edit was performed.

## Work still required

1. Finish the menu controller's source review and implementation with 30-second image dwell, two-second quiet crossfade, reduced-motion still image, disable setting and native fallback.
2. Choose final production export sizing based on actual results; preserve the original source and record any future edit/export.
3. Add further original images for implemented systems and every scenario when it ships. Do not imply unimplemented outpost, alternate-start or orbital content is playable.
4. Inspect the actual native menu overlay at supported resolutions/aspect ratios and UI scales, including the owner's 3840×2160 / scale 2 preference. Candidate visual inspection cannot establish control legibility or crop safety in game.
5. Exercise native background preferences, DLC hover images, missing-image fallback, reduced motion and the selected profile's menu-changing mods before advertising compatibility.

Both assets are kept in `assets/source/menu/` and are not in `tools/package-files.json`. No game or runtime presentation check was performed. The [controller source preparation](PHASE_5_MENU_CONTROLLER_SOURCE.md) records the native class/cast/lifecycle findings and remaining hover/crossfade question.
