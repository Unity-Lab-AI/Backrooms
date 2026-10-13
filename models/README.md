# Unity's models

Every model behind "Unity Plays RimWorld": what each one does on stream, how it was made, where its file lives
and how the stream loads it. Each model has its own folder with a full README.

The weight files are git-ignored and stay on this PC: `*.gguf`, `*.pt`, `*.safetensors`, `*.onnx`. Only the
READMEs and small records (checksums, eval results, model identity) go to the remotes. Every trained file also
has a master copy on the USB drive under `D:\voice-lab\pod-results\<run>\`. If this folder is ever lost,
copy them back from there and run `python training/apply.py`.

## What runs during a stream

```
 Twitch chat / game events
          │
          ▼
  ┌────────────────┐   tool calls    ┌──────────────┐
  │  unity-brain   │ ──────────────▶ │  RimWorld    │  (RimBridge + RimPLC)
  │  thinks, plays │                 └──────────────┘
  └───────┬────────┘
          │ what to say
          ▼
  ┌────────────────┐  her wording   ┌──────────────┐   audio   ┌─────┐
  │  unity-local   │ ─────────────▶ │ unity-voice  │ ────────▶ │ OBS │ ──▶ Twitch
  │  writes lines  │                │  speaks it   │           └─────┘
  └────────────────┘                └──────────────┘
  realistic-vision  ──▶  her webcam pictures (on demand)
```

| Model | Its job on stream | Made by | File | Loaded as | GPU memory | Status |
|---|---|---|---|---|---|---|
| **unity-brain** | Plays the game (RimBridge tools, RimPLC), answers chat, reads screenshots, decides what to say | Us, 2026-10-12: LoRA on Qwen3.5-9B, 8,481 rows | `unity-brain/unity-brain.gguf` (5.3 GB) | Ollama `unity-brain` on :11434 | ~5.3 GB + context | **Live**, replaced the 10-10 brain |
| **unity-voice** | Her actual speaking voice: turns a line into audio with emotion, laughs included | Us, 2026-10-12: trained from scratch on 4,845 clips | `unity-voice/acoustic.pt` + `vocoder.pt` (165 MB) | `training/voice/serve.py` on :5123 | ~0.5 GB | **Accepted** ("smaples are perfect"); going live now |
| **unity-local** | Rewrites each line in her own words and personality before she speaks | Us, 2026-10-10: LoRA on Qwen3-8B | `training/models/unity-voice.Q4_K_M.gguf` (5.0 GB) | Ollama `unity-local` on :11435 | ~5 GB | **Live**: still writes her lines because it beat the new brain on line quality (98% vs 90%) |
| **realistic-vision v5.1** | Draws her webcam pictures, always img2img from her locked likeness | Third party (Stable Diffusion 1.5 fine-tune) | `~\Desktop\Unity 3D Equational Model\Unity 18+\models\realistic-vision-v51.safetensors` | `.claude/tools/unity-face-sd.py` | ≤ ~4 GB while drawing; system RAM otherwise | **Live** |
| unity-player | The old game player before the brain | Us, 2026-10-10: LoRA on Qwen3.6-35B | `training/models/unity-player.Q4_K_M.gguf` (21.7 GB) | Ollama `unity-player` | ran on the CPU | **Retired**, kept for rollback |
| Piper hfc_female | The old voice before her own | Third party (Piper TTS) | `...\Unity 18+\models\piper\en_US-hfc_female-medium.onnx` | `.claude/tools/unity-speak.py` | CPU | **Fallback** only, used if her own voice server is down |

The base models Ollama keeps for these (`qwen3.5:9b`, `qwen3:8b`, `qwen3.6:35b`, `dolphin3:8b`) are pulled from the
Ollama registry by `stream/services.py`. They are not stored here.

## The 16 GB budget (RTX 4070 Ti SUPER)

Brain (~5.3 GB + context) + line writer (~5 GB) + her voice (~0.5 GB) + webcam pictures (~4 GB while drawing) +
RimWorld + OBS all share one 16 GB card. The stress test measures the real peak with everything loaded at once
and decides whether anything has to move to the CPU or out of the GPU. Results go in this file when it has run.

## Rebuilding a model

- **Brain:** `training/BRAIN_PLAN.md` (data → pod → pull → `training/apply.py`). Full recipe in `unity-brain/README.md`.
- **Voice:** `training/voice/pod/LAUNCH_RUNBOOK.md` (script → on-pod recording → screening → training → pull).
  Full recipe in `unity-voice/README.md`.
- **Before any pod rental:** dry-run the exact start command on one cheap GPU first. The 2026-10-12 launch lost
  about $40-50 to Linux-only setup bugs that a dry run would have caught.
