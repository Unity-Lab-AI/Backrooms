# Gate-cycle and event audio delivery

Original assets-only delivery, 2026-10-06. All WAVs are 48 kHz, mono, signed 16-bit PCM.

| Cue | Seconds | Sample peak dBFS | RMS dBFS | Loop |
| --- | ---: | ---: | ---: | --- |
| RR_GateRampUp | 2.50 | -14.89 | -24.12 | no |
| RR_GateCalibrate | 0.60 | -18.79 | -37.32 | no |
| RR_GateActivate | 2.00 | -13.56 | -30.02 | no |
| RR_GateRampDown | 2.50 | -14.89 | -28.18 | no |
| RR_GateEmergency | 2.00 | -13.77 | -32.86 | no |
| RR_CutoffThrown | 0.45 | -15.92 | -33.20 | no |
| RR_SectionAssembled | 0.80 | -15.92 | -30.89 | no |
| RR_JournalFiled | 0.70 | -18.42 | -33.12 | no |
| RR_AnalysisComplete | 1.00 | -18.42 | -36.37 | no |
| RR_MarkerSet | 0.40 | -19.58 | -36.73 | no |
| RR_ContractPaid | 1.00 | -18.42 | -32.98 | no |
| RR_GateSpinLoop | 3.00 | -20.00 | -26.66 | yes |
| RR_GateOpenLoop | 4.00 | -23.74 | -28.96 | yes |

## Loop boundary measurements

The wrap is an ordinary sample transition of a periodic waveform, not a required zero-crossing. Values below are signed PCM16 sample differences.

| Loop | Step before wrap | Wrap step | Step after wrap | Nearby max absolute step | Wrap curvature | Nearby max curvature |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RR_GateSpinLoop | 39 | 39 | 38 | 51 | 1 | 5 |
| RR_GateOpenLoop | 19 | 18 | 18 | 22 | 1 | 1 |

## Authoring and delivery

- Masters: `assets/source/audio/`. Package copies: `Mod/Rimrooms - Async Industries/1.6/Sounds/Rimrooms/`.
- Reproduce with `python tools/assets/render-gate-cycle-audio.py --group all` (Python 3.10+, NumPy). `--group oneshots` and `--group loops` allow separate deliveries.
- The ramp-up accelerates and holds its final speed until a short anti-click release; it deliberately leaves tension unresolved. Ramp-down decelerates, then seats a final latch and decays to rest.
- Calibration is dry and quieter than activation. Filing uses synthetic paper friction and a latch; payment uses a receipt feed, paper pull and muted stamp, without a money jingle.
- One-shots have 3 ms onset/12 ms tail anti-click envelopes, not silence padding. WAV quantization can leave a few zero-valued endpoint samples; their counts are recorded.
- Both loops use exact integer-cycle oscillators and modulators plus Fourier-periodic filtered noise. The boundary step and curvature are checked against interior steps, not forced to zero or made by duplicating an endpoint.
- `audio-metrics.json` records complete PCM metrics, hashes, loop seam measurements and the preserved original four cue/master hashes.

## Integration handoff and limits

This delivery contains no SoundDefs, C# call sites or sustainer implementation. Claude owns those changes. In particular, loops are not playable through the current one-shot-only `RimroomsAudio.Usable` route; they need explicit start/stop handling for normal closure, emergency, destruction, map unload and reload mid-cycle.

No audio was played or evaluated in-game. Numerical sample-peak/RMS and loop continuity checks do not establish perceptual quality, game loudness, true peak, LUFS or release acceptance. Preserve existing text/pane signals; audio must not become the only way to understand a gate state.

No existing cue was re-rendered or modified. No music, room ambience, stereo sound or Quiet Pursuer audio was authored.
