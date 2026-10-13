# models/

Unity's trained models, one folder each. Only the READMEs (and small metadata) are in git; the weight files
(`*.gguf`, `*.pt`, `*.safetensors`, ...) are git-ignored and live only on this machine. The master copies of
every run are on the USB drive under `D:oice-lab\pod-results\<run>\`; re-copy from there if this folder is lost.

| Folder | What it is | Used by |
|---|---|---|
| `unity-brain/` | Her one brain: Qwen3.5-9B + Unity LoRA, IQ4_XS GGUF | `training/apply.py` imports it into Ollama as `unity-brain`; `stream/services.py` runs it |
| `unity-voice/` | Her own voice: from-scratch acoustic model + vocoder (A2 low warm alto) | `training/voice/infer.py`, the stream's speech |
