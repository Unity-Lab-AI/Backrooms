# First-site interior presentation

**2026-09-28 — RR-SPACE, RR-STYLE.** Original room arrangements and material treatment for the [first-slice room inventory](../FIRST_SLICE_CONTENT_INVENTORY.md), following the [visual/audio brief](../research/VISUAL_AUDIO_STYLE_BRIEF.md). Runtime presentation remains unobserved.

## Source route

Core row 4 (`Ludeon.RimWorld`), Assembly-CSharp SHA-256 `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`. Installed `Core/Defs/TerrainDefs/Terrain_Floors.xml` supplies the public `FloorBase` parent, ordinary flooring fields, `CarpetMaking` research and `BurnedCarpet` damage result. The new Def is authored for Rimrooms; no Core XML or texture is bundled.

Local ignored `.local/inspection-presentation/Verse.CompColorable.cs` confirms `SetColor(Color)` stores the native paint color, calls `Notify_ColorChanged`, and saves it through `PostExposeData`. The generator calls this public method only on newly generated wall instances with that component; it does not alter global wall definitions or repaint previously visited sites. A wall without the component retains its native appearance.

## Files and behavior

- [RR_LiminalFloors.xml](../../Mod/Rimrooms%20-%20Async%20Industries/1.6/Defs/TerrainDefs/RR_LiminalFloors.xml): original carpet material, four cloth, 650 construction work, ordinary flammability and cleaning cost. Native CarpetMaking permits reproducing it through Architect; generated site flooring does not require player research.
- [RoomContentBuilder.cs](../../src/RimroomsAsyncIndustries/Generation/RoomContentBuilder.cs): content version 2 uses carpet under institutional rooms, deterministic hard-floor stripes/insets, cooler service/utility surfaces, and muted room-wall paint. Readable landmarks and text distinguish room families without relying on the palette.
- [Interior art manifest](assets/phase2-interior-art.json) and [provenance register](../research/provenance-register.csv): original generated carpet PNG, exact prompt, master, package path and hash. Image output is preserved without pixel edits.

The generator changes only a newly committed site. Existing saved floors, furnishings, damage and player construction are retained. Flooring remains physical RimWorld terrain with ordinary construction/removal/fire behavior; it does not grant company money or evidence.

## Remaining acceptance

Check texture scale, edge repetition, floor/wall contrast, pawn visibility, labels, light and furniture placement at normal map zoom after the owner launches through RimSort. The generated material is development art; its requested small export size was not guaranteed by the image tool. Native-resolution output is retained until an approved export workflow supplies a reviewed smaller texture. No rendering, fire, removal, paint or accessibility behavior has been observed in game.
