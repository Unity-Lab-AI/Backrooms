# unity-brain

Unity's brain: plays RimWorld through the RimBridge tools, runs RimPLC, answers Twitch chat, writes her spoken
lines and reads screenshots. Text and image input. Everything needed to run it is in this folder.

## What's here

| File | What it is |
|---|---|
| `unity-brain.gguf` | The language model (Qwen3.5-9B fine-tune, IQ4_XS, 5.3 GB) |
| `unity-brain-vision.gguf` | The image reader that lets it see screenshots (0.9 GB) |
| `Modelfile` | Tells Ollama how to load both, with the right chat format and sampling |

## Setup

Install [Ollama](https://ollama.com), then from this folder:

```
ollama create unity-brain -f Modelfile
```

## Use it

```
ollama run unity-brain "Say hi to chat."
```

From a program, Ollama's API on `http://127.0.0.1:11434`:

```
curl localhost:11434/api/chat -d "{\"model\": \"unity-brain\", \"stream\": false, \"options\": {\"num_ctx\": 32768}, \"messages\": [{\"role\": \"user\", \"content\": \"Say hi to chat.\"}]}"
```

- **Always send the same `num_ctx` (32768).** A request without it makes Ollama reload the model with a much
  bigger default context (~14 GB of GPU memory instead of ~6 GB).
- **GPU memory:** about 6 GB at 32K context; it fits a 16 GB card alongside a game and OBS.
- **Images:** add `"images": ["<base64 png>"]` to a message.
- **Tools:** pass the tool list in the request's `tools` field (Ollama's standard tool calling); it was trained
  on the RimBridge and RimPLC tool sets.
