# Phase 2: quiet gate and radio audio source review

**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](../CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


**Task assigned and source review completed 2026-09-28.** Scope is read-only Core source inspection and this report only. Features: RR-STYLE, RR-GATE, RR-EXP. Read the [visual/audio brief](../research/VISUAL_AUDIO_STYLE_BRIEF.md#audio-direction), [accessibility brief](../research/CONTENT_ACCESSIBILITY_BRIEF.md#accessibility-requirements) and [Phase 2 task](PHASE_2_VERTICAL_SLICE_TASK.md). The lead owns audio implementation and assets. No code or assets were changed in this assignment; no game/audio playback, build or tests.

Pinned source is profile row 4, `Ludeon.RimWorld`, `Assembly-CSharp.dll` SHA-256 `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`, inspected with local ILSpy 9.1.0.7988. Decompiled output remains ignored under `.local/inspection-audio/`. This report summarizes original findings, not copied Core code or assets.

## Supported Core route

Use native `SoundDef` one-shots for short, original cues. No Harmony, DLC dependency, external audio process or custom Unity audio player is needed. The existing `Core.RimroomsMod` is the correct owner for one shared `ModSettings` subclass; audio preferences are user settings, not campaign or expedition state.

| API | Exact inspected signature or field |
| --- | --- |
| Native one-shot | `Verse.Sound.SoundStarter.PlayOneShot(this SoundDef soundDef, SoundInfo info)` returns `void`. |
| On-camera convenience | `PlayOneShotOnCamera(this SoundDef soundDef, Map onlyThisMap = null)` returns `void`. |
| Map sound info | `SoundInfo.InMap(TargetInfo maker, MaintenanceType maint = MaintenanceType.None)`. |
| On-camera info | `SoundInfo.OnCamera(MaintenanceType maint = MaintenanceType.None)`. |
| Per-call volume/pitch | Public `SoundInfo.volumeFactor` and `pitchFactor` floats. The two factory methods initialize both to 1. |
| Positional target | `TargetInfo(Thing thing)` or `TargetInfo(IntVec3 cell, Map map, bool allowNullMap = false)`. A Thing target resolves its current held map. |
| Native settings | `Mod.GetSettings<T>() where T : ModSettings, new()`; one settings type per Mod instance. |
| Settings UI | `Mod.SettingsCategory()` returns string; `Mod.DoSettingsWindowContents(UnityEngine.Rect inRect)` returns void. |
| Settings persistence | `ModSettings.ExposeData()` is virtual; `ModSettings.Write()` and virtual `Mod.WriteSettings()` use the native settings path keyed by mod folder and Mod class name. |

`PlayOneShot` returns early off the Unity main thread. It rejects sustained SoundDefs, respects native sound slots and routes each subsound through the native one-shot manager. It does not return an acknowledgement that the player heard a cue. Audio must never determine action success, crew transfer, danger state or payment.

## Map position and view behavior

For a gate cue, use `SoundInfo.InMap(new TargetInfo(gate.Position, gate.Map))` or an actual spawned gate Thing. Check the gate/map/cell still exist first. Apply the clamped Rimrooms multiplier to `info.volumeFactor`, then call the native one-shot. Do not construct `default(SoundInfo)`: its zero pitch is rejected by `SampleOneShot.TryMakeAndPlay`.

A positional subsound has `onCamera=false`, uses the maker's shifted cell position, native distance range and spatial blend 1. `SoundDefHelper.CorrectContextNow` rejects a non-null source map when it is not the selected current map or when the world view is selected. `MapOnly` also requires a playing game and map view. Normal positional cues therefore do not intentionally play across unrelated maps.

For a radio acknowledgement that should be audible on the relevant viewed map independent of camera distance, use a dedicated `onCamera=true` subsound. There are two safe call routes:

- `PlayOneShotOnCamera(relevantMap)` applies the native current-map/`DrawingMap` filter. It uses default SoundInfo volume and does not accept a per-call volume argument.
- To apply the Rimrooms volume multiplier, explicitly check `Find.CurrentMap == relevantMap`, `WorldRendererUtility.DrawingMap` and a playing game, construct `SoundInfo.OnCamera()`, set `volumeFactor`, and call `PlayOneShot`. The factory itself has no source map; omitting the explicit guard would lose the map-specific restriction.

Keep maker mode and subsound `onCamera` consistent. The on-camera convenience call logs an error when the Def has no on-camera subsound. A sound with positional subsounds must use `MapOnly` according to native `SoundDef.ConfigErrors`. Do not set `testPlay` or `forcedPlayOnCamera` to bypass ordinary behavior.

## Volume and native controls

The inspected pipeline computes the subsound's randomized `volumeRange / 100`, then multiplies per-call `volumeFactor`, mapped parameters and a native context multiplier before sanitizing volume. Native master volume remains `AudioListener.volume`, assigned from `PrefsData.volumeMaster`.

| Sound configuration | Native preference behavior |
| --- | --- |
| Ordinary nonambient `MapOnly` or `WorldOnly` cue | `Prefs.VolumeGame`. |
| Ordinary `Any` context, including standard UI examples | `Prefs.VolumeUI`. |
| Ambience | Native ambient parameter mappings have a separate route; not needed for this bounded one-shot pass. |
| Any cue | Native master volume still applies. |

An on-camera subsound is not automatically a UI-volume sound: context determines that branch. For gate and in-world radio cues that should follow game volume, use `MapOnly` even if the radio subsound is on-camera. For a native button confirmation, preserve the standard UI route.

Use an additional Rimrooms multiplier in 0..1 and explicit mute/quiet options. Validate/clamp loaded settings, including non-finite values. Skip the call when muted rather than spawning inaudible one-shots. Do not multiply native preferences a second time or change `Prefs`/`AudioListener` from the mod. `muteWhenPaused` and `gameSpeedRange` are available subsound fields; their actual pause/speed experience needs owner-launched acceptance. Native positional sounds can additionally receive vacuum damping; no separate DLC-specific audio logic is needed here.

## SoundDef and asset bindings

Relevant public fields are:

- `SoundDef.sustain` (false for these cues), `context`, `maxVoices`, `maxSimultaneous`, `slot`, and `subSounds`.
- `SubSoundDef.onCamera`, `volumeRange`, `pitchRange`, `distRange`, `muteWhenPaused`, `gameSpeedRange`, `startDelayRange` and `grains`.
- `AudioGrain_Clip.clipPath`; resolution uses `ContentFinder<AudioClip>.Get(clipPath)`. Missing clips log an error and leave no resolved grain.

Use original clips and unique extensionless paths, for example a proposed `Rimrooms/Gate/RR_GateOpen` clip path with the exported asset under the package's `1.6/Sounds/` tree. No such path is claimed implemented by this review. Follow the existing brief's WAV master/export, edge-fade, peak/loudness and provenance requirements; actual asset loading and loudness remain unverified until the owner launch.

Set conservative voice/simultaneous caps, but do not mistake those native caps for an event cooldown. `maxVoices` is not a reliable on-camera repetition limiter according to the inspected field contract; a sound slot only applies to on-camera sounds. Emit a cue once for a real state transition or successful unique action, never every tick, draw or UI refresh. Existing saved action/run IDs should prevent load/retry replay; the audio preference itself need not be part of the campaign save. Ordinary sounds must not be emitted from `ExposeData` or map initialization merely because saved state is active.

## Existing local Core examples

These are verified installed Def/API examples, not proposed files to redistribute. A Core Def may be referenced at runtime if a temporary native fallback is desired; original Rimrooms cues remain the asset goal.

| Local Core XML and Def | Useful source fact |
| --- | --- |
| `Data/Core/Defs/SoundDefs/World_Oneshots_Misc.xml`: `Power_OnSmall`, `Power_OffSmall` | MapOnly, maxSimultaneous 1, folder grains, volume 10 in the pinned XML. |
| `Data/Core/Defs/SoundDefs/Interact_Oneshots_Misc.xml`: `FlickSwitch` | MapOnly, maxSimultaneous 1, clip grain and restrained native volume range. |
| `Data/Core/Defs/SoundDefs/UI_Oneshots_Misc.xml`: `CommsWindow_Open`, `CommsWindow_Close` | On-camera clip grains, maxSimultaneous 1 and volume 19; default Any context. |
| Same UI XML: `Tick_Tiny`, `Tick_Low`, `Tick_High`, `Click`, `ClickReject` | Existing on-camera UI cues; not gate ambience or proof of appropriate loudness. |

Avoid mixing an automatic native `Messages` sound and an added radio cue blindly; the lead must check the chosen message route so one event does not unintentionally produce two acknowledgements. Missing optional cue content should leave the existing persistent text/status intact and not block a gate action.

## Suggested implementation boundary

Implement only brief gate/open/return and radio acknowledgements for actual first-slice actions. Keep original cue production, settings UI and a small main-thread playback helper separate from gate/expedition state mutation. Preserve existing persistent logs, icon/text state and warnings at zero audio. Add no background loops, sustainer lifecycle or menu audio in this pass without a new bounded source/task record.

The helper can safely decline when disabled, the Def/clip is unavailable, the source map is not viewed or the source Thing is invalid. The gameplay action remains committed according to its existing service result. Log missing configuration once rather than on every tick. This recommendation is an original implementation proposal, not a copied Core method or tested result.

## Reproduction and remaining acceptance

```powershell
$rrAudioManaged = 'C:/Program Files (x86)/Steam/steamapps/common/RimWorld/RimWorldWin64_Data/Managed'
& .local/tools/ilspycmd.exe --version
Get-FileHash -Algorithm SHA256 -LiteralPath "$rrAudioManaged/Assembly-CSharp.dll"
& .local/tools/ilspycmd.exe -t Verse.Sound.SoundStarter -r $rrAudioManaged -o .local/inspection-audio "$rrAudioManaged/Assembly-CSharp.dll"
```

Additional exact inspected types: `Verse.SoundDef`, `Verse.Sound.SoundInfo`, `Verse.Sound.SubSoundDef`, `Verse.Sound.Sample`, `Verse.Sound.SampleOneShot`, `Verse.SoundDefHelper`, `Verse.Sound.AudioGrain_Clip`, `Verse.TargetInfo`, `Verse.PrefsData`, and `Verse.ModSettings`. `Verse.Mod` is already inspected in `.local/inspection-agent/Verse.Mod.cs`. The actual source review had no missing-type blocker. It did not play any audio or launch RimWorld.

Future owner-launched acceptance must cover: muted completion with persistent warnings; settings save/reload; native master/game/UI volume interaction; paused/fast-speed behavior; gate versus destination/world/menu views; no cue replay on save/load/retry; no overlapping cue spam; missing clip fallback; audible level and edge-click review; full-profile audio settings interaction. Asset loading, subjective mix and those behaviors remain unverified.
