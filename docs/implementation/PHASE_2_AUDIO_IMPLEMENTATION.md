# Phase 2: quiet company cues implementation

**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](../CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


**Task assigned and implementation handed to the lead 2026-09-28.** Features RR-STYLE, RR-GATE and RR-EXP; Core profile row 4 (`Ludeon.RimWorld`) only. Inputs: [pinned audio source review](PHASE_2_AUDIO_SOURCE_REVIEW.md), [style brief](../research/VISUAL_AUDIO_STYLE_BRIEF.md#audio-direction), [accessibility requirements](../research/CONTENT_ACCESSIBILITY_BRIEF.md#accessibility-requirements), and the lead's [original audio manifest](assets/phase2-original-audio.json). Compilation is owned by the lead; no playback/runtime result is claimed here.

Exclusive scope: new `Audio/RimroomsAudio.cs`, new `Core/RimroomsSettings.cs`, edits to `Core/RimroomsMod.cs`, new package `Defs/SoundDefs/RR_CompanyCues.xml`, and this report. User preferences are owned by native ModSettings, not campaign saves. Cue calls are optional presentation; missing assets/settings or playback exceptions must not block gameplay. Lead owns original WAVs, call sites, keyed text, package allowlist/provenance and compilation. No playback, tests, game launch or build is authorized to this agent.

## Implemented files and route

| File | Behavior |
| --- | --- |
| [RimroomsAudio.cs](../../src/RimroomsAsyncIndustries/Audio/RimroomsAudio.cs) | Optional positional native one-shots with source/view/Def/settings checks and bounded diagnostic warnings. |
| [RimroomsSettings.cs](../../src/RimroomsAsyncIndustries/Core/RimroomsSettings.cs) | Native user-only gate/field mute preferences and normalized 0..1 cue volume. |
| [RimroomsMod.cs](../../src/RimroomsAsyncIndustries/Core/RimroomsMod.cs) | Loads one settings class, exposes native mod-settings UI, normalizes before native write. Package title/identity are unchanged. |
| [RR_CompanyCues.xml](historical-content/0.2.0/1.6/Defs/SoundDefs/RR_CompanyCues.xml) | Four original positional MapOnly SoundDefs bound to the lead-rendered WAVs. |

Public call:

```csharp
RimroomsAsyncIndustries.Audio.RimroomsAudio.Play(string defName, Map map, IntVec3 cell, bool field);
```

`field=false` selects the gate mute preference; `field=true` selects the field/radio mute preference. All four cues are positional in this pass; no on-camera variant, loop, sustainer or external player was introduced. Call only at actual committed transitions/actions. The helper has no action receipt or repeat timer and does not decide whether an action happened; the owning gate/expedition/threat service retains that responsibility.

The helper returns quietly unless the main thread is in a playing game, the map is live/registered/current, map view is drawn and the cell is valid. It requires loaded settings, positive effective volume, a defined non-sustained MapOnly SoundDef and positional subsounds with positive resolved duration. A missing resolved clip therefore avoids repeated native missing-grain playback attempts. For valid content it constructs `SoundInfo.InMap(new TargetInfo(cell, map))`, applies only the user multiplier and calls native `PlayOneShot`.

Any presentation exception is caught inside `Play`; warnings are themselves guarded. At most **eight distinct warning keys** are retained and logged per application session. Invalid/off-view source maps and intentional mute produce no warnings. There is no retry queue, deferred sound, saved playback object or gameplay mutation. A skipped cue leaves the caller's action/result untouched.

## Cues and production source

| SoundDef and WAV stem | Native Def volume | Intended caller category |
| --- | --- | --- |
| `RR_GatePowerRise` | 35 | Gate, `field=false`. |
| `RR_GateWarning` | 50 | Gate, `field=false`. |
| `RR_FieldRadio` | 35 | Field/radio, `field=true`. |
| `RR_SpatialTell` | 35 | Field/distortion, `field=true`. |

Each uses one `AudioGrain_Clip`, extensionless `Rimrooms/<stem>`, pitch 1, distance range 12..55, `maxVoices=1` and `maxSimultaneous=1`. These initial mix/distance settings are balance defaults, not measured acceptance. Native `volumeRange` is divided by 100 before the additional user factor. Native game volume and master volume remain in control; the mod does not write `Prefs` or `AudioListener`.

The lead's [original render source](../../tools/assets/render-phase2-audio.py) and [manifest](assets/phase2-original-audio.json) own provenance, hashes and production metrics. The manifest records original mono 48 kHz/16-bit exports, short durations, measured sample peak/RMS and **no playback review**. RMS is not LUFS or true peak. This agent neither regenerated nor played the files. Final audibility, balance, clipping/click perception and accessibility remain runtime/asset acceptance work.

## Settings and localization

Native settings fields are `MuteGateCues=false`, `MuteFieldCues=false`, `CueVolume=0.5f`. `EffectiveCueVolume` rejects NaN/infinity to 0.5 and clamps finite out-of-range values. Settings normalize before Scribe saving, after post-load, after initial retrieval and before native `WriteSettings`. These preferences are local user settings; no campaign schema/version changes were made.

The native settings screen has separate gate and field/radio checkboxes plus a volume slider and text explaining persistent warnings. The lead owns these keys:

- `RR_Settings_AudioTitle`
- `RR_Settings_AudioDescription`
- `RR_Settings_AudioUnavailable`
- `RR_Settings_MuteGateCues`
- `RR_Settings_MuteFieldCues`
- `RR_Settings_CueVolume` with percentage argument `{0}`.

Settings category remains the proper mod title `Rimrooms - Async Industries`. The extra source inspection `Verse.Listing_Standard` confirmed `Begin(Rect)`, `End()`, `Label(TaggedString, float=-1, string=null)`, `CheckboxLabeled(string, ref bool, string=null, float=0, float=1)`, and `Slider(float,float,float)`. It remains ignored in `.local/inspection-audio/`; no native UI source was copied.

## Integration and acceptance still required

The lead integrates call sites, keys, package allowlist and provenance, and records compilation in the [build record](PHASE_2_BUILD_RECORD.md). Call sites must preserve existing text/status, prevent action-retry/load replay and avoid an accidental duplicate native Messages sound. Muting these cues does not itself mute unrelated Core sounds.

Lead integration is present: normal/recovery opening events play the power-rise cue; countdown and emergency-entry transitions play the gate warning; displaced-route/loop events use the spatial cue; entity sighting/contact and route-aid placement use the field radio cue. Those messages use native `MessageTypeDefOf.SilentInput` to avoid a second native acknowledgement sound. The installed `Core/Defs/Misc/MessageTypeDefs/MessageTypeDef.xml` declares that message type with no sound. Existing state/receipt guards and persistent activity entries remain authoritative; audio never advances an action. No sound was played during asset generation or compilation.

After an owner-launched disposable session through RimSort, record:

1. Four Defs resolve their intended original WAVs without load errors; short positional playback respects map and camera distance.
2. Gate and field mutes operate independently; 0, default 0.5 and 1 volumes work; native master/game controls still apply.
3. Native settings save/reload and invalid loaded values recover safely; current text/slider layout remains readable at supported UI scale.
4. HQ/destination/world-view changes do not produce off-map cues or delayed replay; no cue on repeated UI draws, save/load or duplicate action retries.
5. Missing cue content or failed playback leaves gate/crew/evidence state and persistent warning text intact.
6. The complete first expedition remains understandable with all audio muted; subjective volume, fades and repeated-event density receive actual listening review.

None of those cases was executed by this agent. Gate 2 and broader profile/co-op compatibility remain pending.
