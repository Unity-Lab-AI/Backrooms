# Credits and distribution scope

**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


**Rimrooms - Async Industries — Operator.** Original project source is supplied under [MIT](../LICENSE). The original typographic package card uses the same project license, recorded separately in the [provenance register](research/provenance-register.csv). Its drawing script uses system Arial at render time; no font file is distributed.

RimWorld and its installed engine/game assemblies are supplied by Ludeon Studios and their respective owners. They are local build/runtime requirements and are not bundled. This project is a mod for RimWorld; no endorsement is implied.

Kane Pixels' series and the separate A24 feature inform the approved indirect story/style adaptation. See the [source register](SOURCE_REGISTER.md), [fan cliff notes](research/KANE_PIXELS_FAN_CLIFF_NOTES.md) and [feature note](research/reviews/a24-feature/feature-review.md). No film frames, footage, audio, dialogue or third-party mod assets are included in the foundation package. Their rights are separate from this repository's original-code license.

Build tooling uses Microsoft's .NET SDK and `Microsoft.NETFramework.ReferenceAssemblies.net472` 1.0.3 locally. Source inspection used [ILSpy 9.1](https://github.com/icsharpcode/ILSpy/releases/tag/v9.1) through [ilspycmd 9.1.0.7988](https://www.nuget.org/packages/ilspycmd/9.1.0.7988). These tools and their downloaded libraries are not copied into the mod. The [Core source review](implementation/PHASE_1_CORE_SOURCE_REVIEW.md) records the bounded inspection.

Other mods remain separately installed dependencies or optional compatibility targets. Credit their exact publisher/source in the linked per-mod review when an integration is implemented. Listing a mod in the 294-row register does not grant permission to distribute its files or claim that its authors support Rimrooms.
