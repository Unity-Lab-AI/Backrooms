# Gate cycle asset delivery — 2026-10-06

## Request and authority

> you might check if u have work from claude to do: \ASSET_REQUESTS.md and todo :

The [asset brief](../ASSET_REQUESTS.md) is the authoring contract. This task continues the owner's **assets-only** scope; the full-mod goal remains paused in this chat. Feature IDs: RR-STYLE and RR-GATE. The existing [authored rotation handoff](AUTHORED_ROTATION_PIPELINE.md) remains the installed baseline evidence.

Baseline: branch `feature/bug-testing`, HEAD `eeda0b3`, version `0.13.0-dev`; the earlier rotation wave staged 164 files and recorded assembly SHA256 `519A9F36EE9CE5FC653DE77A54E31E026DA72A6C869340E703C8973C47F16D6D`. These are baseline identifiers, not a receipt for this delivery. Existing uncommitted artwork and the continuing build agent's work are preserved.

## Scope and file ownership

| Owner | Files and output | Scope |
| --- | --- | --- |
| Audio agent | `tools/assets/render-gate-cycle-audio.py`, `assets/source/audio/`, new WAVs under package `1.6/Sounds/Rimrooms/`, delivery metrics under `outputs/gate-cycle-assets-2026-10-06/audio/` | Eleven original one-shots first, then two periodic loops; preserve existing four clips |
| Animation agent | New gate-animation helper if required, new charge/activation masters under `assets/source/phase2/`, new PNGs under package `1.6/Textures/Things/Building/Rimrooms/Gates/`, animation provenance/previews under `outputs/gate-cycle-assets-2026-10-06/` | One shared energy overlay: eight looping charge frames, six nonloop activation frames, 256 square, transparent |
| Lead | Package allowlist, this task record, bounded TODO/archive entry, asset brief delivery links | Verify delivered paths/format/provenance and provide the integration handoff |
| Continuing build agent | SoundDefs, cue call sites, sustainer lifecycle, aura state, animation renderer | Outside this asset-authoring task |

## Preserved behavior and remaining integration

No saved fields, Def IDs, native door behaviors, provider bindings, C# state machines or playback preferences change here. Existing equipment facings, gate frames, journal views, menu assets and the four current audio cues remain intact. No natural-gate frames, Quiet Pursuer, music, ambience, stereo clips or per-footprint animation variants are produced.

WAVs must be 48 kHz, mono, signed 16-bit PCM, without silence padding; one-shots may use short anti-click edges. Ramp-up ends unresolved, while ramp-down descends and resolves. Loop wrap continuity must be measured, not inferred from duration.

PNG frames must be 256 x 256 RGBA energy only, no structure and no opaque background, using one coordinate registration for all footprints and facings. Charge wraps; activation ends and must not wrap. Fixed tint/aura state selection is code-owned, and no new state palette is approved here.

The new files do not play or animate merely by existing. At the starting inspection, `RimroomsAudio.Usable` rejected sustained sounds; the continuing build agent owns explicit start/stop handling for close, cancellation, destruction, map unload and save/reload. One-shots require SoundDefs and event bindings. Animation frames require frame-index selection, scaling and lifecycle. Missing new assets must preserve the current native rendering and existing cue behavior. Concurrent implementation may satisfy parts of this contract; this asset record does not audit or close that code work.

**Additional binding guard verified at the starting source inspection:** `RimroomsAudio.Play` called `ResolveNativeCue` before looking up a company SoundDef. Its switch accepted only the four existing cue IDs. Adding new SoundDefs alone therefore left all thirteen new names refused. The continuing build agent must reconcile cue admission as well as SoundDefs and event call sites; no new fallback mapping is approved or written by this asset task. SoundDef `clipPath` values should be `Rimrooms/<exact WAV basename>` without the extension. These are starting facts; inspect the current source because concurrent integration work began during this delivery.

The package checks permit allowlisted files without consumers. At the initial two-family delivery, the texture checker could report fourteen unused PNGs; unused WAVs were not flagged by the package checker. Preserve genuine missing-consumer reports until bindings exist; do not manufacture references or weaken the checks to make delivery look implemented. The catalog reads live source/Defs, so its count changes as the continuing build agent integrates the files.

## Delivered audio

All thirteen original WAVs now exist as byte-identical master/package pairs. They are **48,000 Hz, one channel, signed 16-bit PCM**. Authorship uses seeded, filtered noise, mathematical motor oscillators and damped mechanical/paper envelopes; no third-party recording was used. Reproduction: `python tools/assets/render-gate-cycle-audio.py --group all` (Python 3.10+ and NumPy). The generator preserves the four older WAVs and their source hashes.

| Cue | Seconds | Behavior authored |
| --- | --- | --- |
| `RR_GateRampUp` | 2.50 | Rev rises from 42 Hz toward 135 Hz and ends at speed, unresolved |
| `RR_GateCalibrate` | 0.60 | Quiet dry detent and relay; repeated quarter beats |
| `RR_GateActivate` | 2.00 | Pressure release and settling motor |
| `RR_GateRampDown` | 2.50 | Deceleration, final latch and decay to silence |
| `RR_GateEmergency` | 2.00 | Uneven failing motor and mechanical impacts, distinct from the existing warning |
| `RR_CutoffThrown` | 0.45 | Heavy switch and latch |
| `RR_SectionAssembled` | 0.80 | Fastening and securing strikes |
| `RR_JournalFiled` | 0.70 | Paper friction and archive latch |
| `RR_AnalysisComplete` | 1.00 | Quiet instrument verification |
| `RR_MarkerSet` | 0.40 | Small switch and indicator tick |
| `RR_ContractPaid` | 1.00 | Receipt-feed mechanism; no jackpot melody |
| `RR_GateSpinLoop` | 3.00 | Periodic low motor and pulse |
| `RR_GateOpenLoop` | 4.00 | Quieter periodic open-gate presence |

[Audio metrics](../../outputs/gate-cycle-assets-2026-10-06/audio/audio-metrics.json) and [master provenance](../../assets/source/audio/gate-cycle-provenance-2026-10-06.json) record file hashes, PCM format, sample peaks/RMS, clipping count, tiny anti-click edges and loop boundaries. No sample clips; the leading/trailing zero runs are at most 217 samples (4.52 milliseconds), not silence padding. Both loops use integer-cycle oscillators/modulators and periodic inverse-DFT noise, with no duplicated endpoint or silent seam. Spin's seam steps are 39, 39, 38 PCM units; live's are 19, 18, 18, with one-unit curvature at each wrap. Live RMS is -28.96 dBFS versus spin's -26.66 dBFS. These are numerical asset measurements, not listening or in-game mixing acceptance.

## Delivered animation

The following shared sequences now exist under `assets/source/phase2/` (masters) and package `1.6/Textures/Things/Building/Rimrooms/Gates/` (finished frames):

- **`RR_GateCharge_01.png` through `RR_GateCharge_08.png`:** eight-frame looping charge sequence.
- **`RR_GateActivation_01.png` through `RR_GateActivation_06.png`:** six-frame nonlooping activation burst. This chosen basename distinguishes the images from the `RR_GateActivate.wav` audio cue; it is part of the integration contract.

Each finished frame is **256 x 256 RGBA**. Source masters are 444 square for charge and 512 square for activation. The built-in image generator authored two coherent transparent sheets, with targeted edits to remove broad ribbons/background washes. [Exact prompts and tool output paths](../../outputs/gate-cycle-assets-2026-10-06/animation-provenance.json) are preserved alongside the accepted source sheets. [Frame/master manifest](../../outputs/gate-cycle-assets-2026-10-06/animation-manifest.json) records hashes and alpha metrics. Reproduction from the accepted sheets: `python tools/assets/package-gate-animation.py --family RR_GateCharge --apply` and `python tools/assets/package-gate-animation.py --family RR_GateActivation --apply` (Pillow and NumPy). The live-loop extension made an explicit family mandatory for writing so a one-family update cannot inadvertently rewrite the earlier frames; default/report mode writes nothing.

All cells use fixed registration and one uniform size conversion; individual frames are not independently fitted or recentered. Source alpha is retained and RGB beneath zero alpha is cleared after resizing. The charge aperture stays clear; activation has two brief thin inward branches while the central 16-pixel square remains fully transparent in every frame. No hardware, opaque portal surface, aura disk or natural-door graphics were added.

Lead inspection used the [charge contact sheet](../../outputs/gate-cycle-assets-2026-10-06/RR_GateCharge-contact.png) and [activation contact sheet](../../outputs/gate-cycle-assets-2026-10-06/RR_GateActivation-contact.png). [The animation inspection record](../../outputs/gate-cycle-assets-2026-10-06/animation-review.json) compares every charge transition: 8 to 1 has mean premultiplied RGBA difference 0.020036 versus 0.024448–0.030006 for ordinary steps. This is coherent electrical flicker, **not mathematically interpolated travel of one identical filament**. Activation peaks at frame 3 and decays to two sparks in frame 6; stop drawing afterward. The outside-package APNG previews use 110 ms per charge frame and 70 ms per burst frame solely as inspection aids; runtime cadence and state-driven opacity remain the build agent's choice and acceptance work.

## Evidence and closure

**Asset authoring and package registration complete:** thirteen WAVs and fourteen PNGs, with matching source masters, explicit descriptions and provenance. At the asset-registration snapshot, the repository package had **191 allowlisted files**, verified by `Get-RimroomsPackageManifest`; this was a file/hash/XML inspection, not a new compilation or staging receipt. [Package manifest](../../outputs/gate-cycle-assets-2026-10-06/package-manifest.json) and [delivery manifest](../../outputs/gate-cycle-assets-2026-10-06/delivery-manifest.json) are saved outside the mod. Subsequent concurrent integration files are outside that snapshot and must be included in the continuing build agent's complete package receipt.

`python tools/check-register-compliance.py` passed with matching masters for all 79 gameplay assets and complete existing directional sets. `python tools/build-asset-page.py --apply` regenerated [the catalog](../wiki/assets.md): 44 drawings, 17 sounds and zero missing descriptions. The first snapshot had **27 assets awaiting consumers**. On the subsequent catalog check, `RR_GateCycleCues.xml` and a ramp-up call site had appeared from work outside this task; the catalog's unused count fell to **14 animation frames**, making the earlier generated page stale. The page was regenerated from those current files. This identifies concurrent SoundDef work, not a playback or complete integration result; no runtime acceptance is inferred. The unbound entries remain honestly reported. Audio PCM/master identity and PNG dimensions/alpha were inspected independently in the delivery manifest. Existing art and audio remained byte-identical to [the starting snapshot](../../outputs/gate-cycle-assets-2026-10-06/preserved-package-baseline.json). A separate `RR_GateRecipes.xml` hash changed during the pass; this task did not edit it and preserved the current file. Its before/after hashes are recorded without attributing the change to any editor or process.

No C#, SoundDef, saved-field, compiled DLL or gameplay integration change belongs to this delivery. **These new assets were not copied to RimSort's installed mod or published.** The earlier 164-file installed result remains the historical staging receipt. The new files, manifests and reproduction tools are ready for the continuing build agent to wire, then include in its next complete build/stage checkpoint. The five existing code TODO rows remain open; the bounded asset-authoring row may close with this record.

Owner-launched listening, in-game mixing, animation pacing/readability, reduced-motion/disable behavior, native-door visibility and sustained-sound lifecycle remain acceptance work. No game, audio preview playback, profile change, runtime test or remote publication is performed by this task.

## Active portal extension

> what about active portal ones. should you do those to and write an ote to claude in todo

**Delivered:** the third shared eight-frame sequence, `RR_GateOpen_01.png` through `RR_GateOpen_08.png`, for a company machine portal's live state. Masters are in `assets/source/phase2/`; finished frames are in package `1.6/Textures/Things/Building/Rimrooms/Gates/`. One calmer **256-square RGBA** energy loop serves all footprints/facings and retains the clear aperture. Natural doors remain native and unframed. No new aura art, hardware or portal fill is included.

The earlier fourteen animation frames and thirteen WAVs are preserved. [The owner's TODO note](../TODO.md#active-portal-artwork-and-code-handoff-2026-10-06) asks the continuing build agent to switch from activation to this loop while live, stop on closure/unload/destruction, reconcile on reload, retain native doors/pawns/fog guards and honor visual disable/reduced-motion behavior. This task writes only artwork and its package/provenance records; no state or renderer implementation is claimed.

Lead inspection used [the live-loop contact sheet](../../outputs/gate-cycle-assets-2026-10-06/RR_GateOpen-contact.png). It holds two soft corner filaments with much less variation and lower alpha energy than charge (894–920 versus 1169–1453). The 8-to-1 mean premultiplied difference is 0.003163, within ordinary steps 0.001617–0.005331. The central 64-pixel square has at most 1/255 alpha residue, the central 16-pixel square is transparent, and zero-alpha pixels have zero RGB. This is a subtle authored idle shimmer; cadence over native doors still needs runtime review. The outside-package APNG uses 300 ms per frame solely for inspection.

[Live-loop provenance and exact prompts](../../outputs/gate-cycle-assets-2026-10-06/gate-open-provenance.json), [frame/master manifest](../../outputs/gate-cycle-assets-2026-10-06/gate-open-manifest.json), [inspection record](../../outputs/gate-cycle-assets-2026-10-06/gate-open-review.json) and [delivery checks](../../outputs/gate-cycle-assets-2026-10-06/gate-open-delivery-manifest.json) preserve the evidence separately from the original two-family receipt. Reproduce only this family with `python tools/assets/package-gate-animation.py --family RR_GateOpen --apply`. The earlier 27 new assets are hash-identical to [their pre-extension snapshot](../../outputs/gate-cycle-assets-2026-10-06/pre-open-extension-assets.json). All eight new filenames have matching masters, explicit package entries and catalog descriptions. **Total authored in this request chain: 13 sounds and 22 animation PNGs.** No new staging or publication is performed; code integration stays with the continuing build agent.

Final asset inspection: register compliance passed for all **87 gameplay assets with matching masters**. The regenerated catalog listed **52 drawings and 17 sounds, zero missing descriptions and zero missing static consumers** after further concurrent source integration. These final counts supersede the earlier unused-asset snapshots for catalog purposes; a named source/Def consumer still does not prove playback, animation or runtime acceptance. The live-loop asset row was archived verbatim with `.local/qa/backup-20261006-090411`; independent archive verification passed. The explicit note to Claude remains open in `TODO.md`. No continuing build-agent code row was closed by this art task.
