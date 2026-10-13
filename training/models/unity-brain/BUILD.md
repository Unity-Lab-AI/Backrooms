# unity-brain: how it was built

The usable model is `models/unity-brain/`; this folder holds its build records and the stream's apply stamps.

**What for:** the single model that plays RimWorld through the RimBridge tools, runs RimPLC, answers Twitch chat,
writes catch-ups and reads screenshots (text + image input; the vision part is Qwen3.5-9B's own, untrained).

**How it was built (2026-10-12, RunPod 1x H100, ~5.5 h):**
- Base `Qwen/Qwen3.5-9B`, bf16 LoRA r=32 on attention, linear-attention and MLP projections (Unsloth),
  2 epochs, lr 1e-4, effective batch 16 (8 x 2), sequence 24,576, 1,062 steps, final train loss 0.397.
- Data: `training/data/brain/train.jsonl`, 8,481 rows, digest `7d2cac95...`: play, RimPLC usage, every tool,
  the If-Only-I-Had-A-Brain life story (admin, advice, banter, boundaries, hard moments, pacing, Q&A, reactions,
  setup, stream running), fortress and 100 real game screenshots with the game's own state.
- Code: `training/pod/train.py` + `run.sh` at commit `4932071`; merged, converted to GGUF, imatrix-calibrated on
  her own conversations, quantized to Q4_K_M and IQ4_XS; the eval picked **IQ4_XS**.
- Files: `models/unity-brain/unity-brain.gguf` (5.3 GB, sha256 in `unity-brain.gguf.sha256` here), `lora/` (the 306 MB adapter, for
  re-merging), `brain-eval.json`, `quant.txt`.

**Held-out eval (249 episodes never trained on):**
right tool overall 82% -- life story 100% in all ten categories, play 96%, RimPLC 92%,
rare-tools coverage set 53% (the known weak spot: more examples per rare tool next round).
Spoken lines: 90% pass, 97% distinct -- below today's line model (98%), so today's model keeps writing her
stream lines (`brain-voice.ok` is not written) and the brain does everything else.

**To use:** `python training/apply.py` (reads the expected sha256 and stamps here, loads `models/unity-brain/unity-brain.gguf`) (checks the sha256, imports into Ollama on :11434 as `unity-brain`).
