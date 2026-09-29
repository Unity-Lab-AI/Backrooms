# Scenario and native room provider checkpoint

This checkpoint follows [the scoped task](PHASE_3_SCENARIO_GATE_REUSE_TASK.md) and the historical [0.3.0 company build](PHASE_3_BUILD_RECORD.md). Target package version: **0.3.1-dev**. It is a development milestone within the complete master TODO, not a completed campaign or compatibility claim.

## Scope and evidence

- [Company setup implementation](PHASE_3_SCENARIO_SETUP_IMPLEMENTATION.md): actual selected people and native editable supplies, followed by a final company review. Old physical setup and branch receipts remain readable. Company roles do not rewrite native work priorities.
- [Native-door migration review](NATIVE_GATE_MIGRATION_IMPACT.md) maps callers, saved fields and actual battery/control ownership. [Room provider replacement](PHASE_3_ROOM_PROVIDER_REUSE.md) remains planned; no Generation source changed in this checkpoint. It continues in the next implementation milestone.
- [Regression containment](../REGRESSION_CONTAINMENT.md) now requires baseline/caller/save-field review, evidence-based TODO closure and explicit preservation of existing behavior.
- The owner's publication clarification requires the entire current project-change batch in the milestone. Both remote cascades receive the same commit; final remote-ref verification is reported directly without leaving a new local-only publication receipt.

## Acceptance boundary

No RimWorld launch or gameplay test is performed. Native/Prepare Carefully navigation, edited relationships and equipment, count changes, partial arrival recovery, old saves, generated lighting/power, existing expedition/research/procurement behavior and full-profile compatibility require the later owner-launched RimSort session. Alternate store/inside starts, native portal door conversion, broader campaign systems and optional integrations remain open. The full mod goal remains active.

## Build result

`./tools/build.ps1 -NoRestore` succeeded with **zero warnings and errors**, .NET SDK 9.0.308, Release/net472 and the pinned Core references. **66 C# files**, **69 approved package files**. DLL SHA-256: `2589D21544392613C909C56C84036A696A4CB8E68BB3D3C24E0D81DC428E3382`.

- [Compiler output](evidence/phase3-scenario-provider-2026-09-28/build-output.txt), [source hashes](evidence/phase3-scenario-provider-2026-09-28/source-manifest.json), [package hashes](evidence/phase3-scenario-provider-2026-09-28/package-manifest.json), [reference manifest](evidence/phase3-scenario-provider-2026-09-28/reference-manifest.json).
- `./tools/stage-mod.ps1 -UpdateExisting` copied the package into the RimSort-discovered Local Mods directory and matched all 69 hashes. The previous installation was backed up; [staging receipt](evidence/phase3-scenario-provider-2026-09-28/staging-receipt.json). No game launch or profile change occurred.
- [Saved-reference audit](evidence/phase3-scenario-provider-2026-09-28/document-audit.json) checks local links/register agreement only; it is not gameplay or integration test evidence.

This evidence proves compilation and package identity only. It does not close gameplay or compatibility gates. All current source, documentation and saved evidence are included in the publication checkpoint; native room/gate implementation continues afterward.
