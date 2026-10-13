# unity-voice: how it was built

The usable model is `models/unity-voice/`; this folder holds its publication record and checksums.

**What for:** Unity's own speaking voice on stream, replacing Piper. Emotion, intensity, pace and speech act are
inputs; recorded laughter and breath events are supported.

**How it was built (2026-10-12, RunPod 2x H100):**
- Script: 5,000 owner-approved lines (`training/voice/STREAM_CORPUS.jsonl` + events, 420 with laughter).
- Recorded on the pod by two teacher TTS models (Qwen3-TTS + CosyVoice3) steered to the approved A2 low warm
  alto; screened with speech recognition: **4,845 kept** (121 word mismatches, 22 long silences, 12 rushed dropped).
- Trained from scratch: acoustic model 20,000 steps (GPU 0) and HiFi-GAN-style vocoder 100,000 steps on real
  audio + 20,000 polishing steps on the acoustic model's own output (GPU 1). Best held-out vocoder error 0.189.
- Code `training/voice/` at commit `fd208ef0` (digest `5103180e...`), run id `f8bb6cd3...`, dataset `85b62deb...`.
- Files: `acoustic.pt`, `vocoder.pt`, `voice-meta.json` in `models/unity-voice/`; `SHA256SUMS` and `publication.json` here.

**Accepted:** owner on the final samples, 2026-10-12: *"smaples are perfect"* --
`training/voice/receipts/trained-voice-acceptance-2026-10-12.json` binds that to these exact file hashes.
Live pace: `UNITY_VOICE_LENGTH_SCALE` **1.0** (set by `stream/services.py`). The 1.2 stretch was for the too-fast
local test voice; on this voice the owner heard it as "1/5th too slow" (2026-10-13).

