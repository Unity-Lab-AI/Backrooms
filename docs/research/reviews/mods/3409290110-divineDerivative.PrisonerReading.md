# RimWorld mod review: Prisoners Can Read

- Steam Workshop URL: https://steamcommunity.com/sharedfiles/filedetails/?id=3409290110
- Public source: https://github.com/divineDerivative/PrisonerReading
- Workshop ID: `3409290110`
- Package ID: `divineDerivative.PrisonerReading`
- Exact installed version/date: no version declared; reviewed 2026-09-27
- RimWorld build and DLC present: 1.6.4871 rev590; local supports 1.5–1.6; SHA-256 `74655884BC0FDD75E6D0A4A0AEF6FCBF3A10E48E4BA0A7DD8411EB586FA91D79`
- Load order: profile row 174; Harmony required and loaded before it
- Dependencies and incompatibilities stated by publisher: prisoners can read accessible books when a recreation need is supplied by another mod. Author discussion references DivineFramework, while the selected local `About.xml` lists only Harmony; treat that difference as unresolved.
- Source/package files reviewed: Workshop page, upstream repository/license, local metadata and related logs reported upstream

## Verified source facts

- The public repository lists MIT. The selected local build declares Harmony but not DivineFramework; do not invent a hard dependency from discussion references alone.
- Book reading is an optional recreation behavior and does not add Rimrooms interaction/API.

## Rimrooms integration decision

- **Provisional:** optional QoL/no direct integration planned.
- Related systems: `RR-STA`, `RR-COMPAT`; see the [feature map](../../../FEATURE_TRACEABILITY.md).
- Prisoner care and recreation must remain possible without books or this mod.

## Runtime evidence

- Runtime tests: pending; none run.
- Confirm the selected build's framework requirements and test book access/recreation with Prison Commons, TVForPrison and Prison Labor before advertising support.
