# Native sound reuse

**Task:** existing-content replacement, RR-STYLE/RR-GATE/RR-THREAT/RR-UI. Source implemented on 2026-09-28; compilation and runtime observations are recorded separately in the [company build record](PHASE_3_BUILD_RECORD.md). Follow the [reuse policy](../CONTENT_REUSE_POLICY.md).

The existing `Audio/RimroomsAudio.cs` service now resolves company cue IDs to installed Core SoundDefs. It does not create SoundDefs, copy native clips, synthesize audio, or alter the provider. Existing game-state/map visibility guards, cue volume, gate/field mute controls, warning cap and exception isolation remain. Visual messages and durable activity/observation records remain authoritative.

| Company event | Existing Core Def | Presentation |
| --- | --- | --- |
| Opening power transition | `Power_OnSmall` | Native positional power click |
| Gate warning/emergency | `Message_ThreatSmall` | Native interface alert on camera |
| Field communication observation | `CommsWindow_Open` | Native communication interface cue |
| Spatial observation warning | `Message_NegativeEvent` | Native interface caution cue |

Provider: Core row 4, `Ludeon.RimWorld`. Installed XML inspected under `Data/Core/Defs/SoundDefs/World_Oneshots_Misc.xml` (Power_OnSmall) and `UI_Oneshots_Misc.xml` (remaining three). Native `Verse.Sound.SoundInfo.OnCamera(MaintenanceType)` and `InMap(TargetInfo,MaintenanceType)` signatures were read from the pinned Assembly-CSharp. The service checks actual resolved non-sustained definitions and matching sub-sound camera mode; if a provider patch makes a cue incompatible, it stays silent with one bounded diagnostic. No custom audio is used as fallback.

The former [sound definitions](historical-content/0.2.0/1.6/Defs/SoundDefs/RR_CompanyCues.xml) and four original WAVs are preserved under `historical-content/0.2.0/1.6/Sounds/Rimrooms/`, outside the loadable mod. Their entries were removed from the package allowlist. Earlier audio implementation/provenance reports describe the historical build only. Cue IDs in code are event keys now, not lookups of removed Rimrooms SoundDefs.

No campaign schema changes: these calls have no saved SoundDef fields or persistent sustainers. This is not a claim that the whole content-reuse migration is done. Actual playback, volume, remote-map suppression, mute and profile-patched sound behavior remain owner-launched acceptance work; no game or sound playback was started for this task.
