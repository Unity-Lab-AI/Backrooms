# Unity's brain: one model for everything

One GPU model plays RimWorld through the tools, speaks the stream lines, answers Twitch chat, writes catch-ups, posts highlights, reads screenshots and routes picture requests to the picture tools. It replaces two models: today's 35B CPU player (`unity-player`) and the 8B voice (`unity-local`).

Nothing on RunPod has been created or called. This file is the plan plus the launch checklist. The owner approves the launch.

## 1. Base model: Qwen3.5-9B

Installed here: Ollama **0.40.2**. The Ollama library already ships `qwen3.5:9b` with text and image input, tools and a 256K context.

| Candidate (Oct 2026) | Vision | Tool calling | Q4 size | Fit on 16 GB beside RimWorld/OBS | LoRA + GGUF path | Verdict |
|---|---|---|---|---|---|---|
| **Qwen3.5-9B** (dense, hybrid gated-delta + full attention) | native (projector ~0.9 GB F16) | strong, same Qwen tool format our data already uses | Q4_K_M 5.7 GB, IQ4_XS ~5.0 GB | yes, ~7 GB with projector + 32K q8 KV | Unsloth supports the whole Qwen3.5 family in bf16 LoRA (vision, text, RL); llama.cpp converts it (Unsloth publishes GGUF + mmproj). Our pipeline already trained and applied the same architecture family (qwen3.6 35B, `RENDERER qwen3.5`) | **chosen** |
| Qwen3-VL-8B | yes | good | ~5 GB | yes | supported | an older generation; Qwen3.5-9B scores higher on vision (RealWorldQA 80.3) and agentic tasks |
| Gemma 4 12B | yes | yes | ~7.5 GB + projector | tight once RimWorld peaks | supported | different chat template, so every row would be re-rendered; no gain for the risk |
| Gemma 3 12B | yes | weak (no native tool tokens) | ~7 GB | tight | supported | tool calling is the job, so no |
| Ministral 3 14B | yes | yes | ~8.5 GB | no headroom for the image model | partial | too big |
| Qwen3.6 27B / 35B-A3B | yes | best | 17-22 GB | no (today's 35B runs on the CPU) | done before | too big for the GPU |

**Why Qwen3.5-9B:**
- It fits a 16 GB card at Q4 with room for RimWorld, OBS, the Twitch window and an on-demand image render.
- It is the same family and chat template as every row we already have, so nothing has to be re-rendered.
- Only 8 of its 32 layers keep a KV cache, so a long tool context is cheap.
- Unsloth recommends bf16 LoRA for Qwen3.5, not 4-bit QLoRA. bf16 needs ~22 GB, which any H100 has.

Known Ollama limitation: Unsloth's GGUFs keep vision in a separate mmproj that Ollama will not load as an import. `apply.py` avoids that the same way it did for the 35B. It takes Ollama's own `qwen3.5:9b` Modelfile, which keeps Ollama's projector blob, and swaps only the text weights for ours.

**Owner's compression ask** (*"back it off a touch ... we dont need spaceage"*): weights are stored at a moderate 4-bit quant, never below ~3.5 bits.
- The default is **IQ4_XS with an importance matrix** built from her own conversations (~4.25 bpw, ~0.7 GB smaller than Q4_K_M).
- The pod builds both IQ4_XS and Q4_K_M and scores each on the held-out voice and tool sets. It keeps IQ4_XS unless it scores more than 0.02 below Q4_K_M on either, in which case it keeps Q4_K_M.
- No exotic tricks: no 2-3 bit quants, no speculative decoding, no MTP.

## 2. VRAM budget (16 GB RTX 4070 Ti SUPER)

| Item | GB | Notes |
|---|---|---|
| Windows desktop + Twitch browser window | 1.5 | DWM plus one Chromium window |
| OBS (NVENC encode + scenes) | 2.0 | |
| RimWorld with 294 mods | 3.0 | textures; peaks on big maps |
| Brain weights, IQ4_XS (Q4_K_M: 5.7) | 5.0 | |
| Vision projector (F16) | 0.9 | loaded with the model |
| KV cache, 32K context at q8_0 | 0.6 | 8 full-attention layers x 4 KV heads x 256 dims |
| Ollama compute buffers | 0.6 | flash attention on |
| **Steady total** | **13.6** | Q4_K_M: 14.3 |
| Webcam/selfie render (SD 1.5, CPU-offloaded, on demand) | +1.0-2.2 while rendering | the pipeline lives in RAM, only the running block is on the GPU, and the cache is emptied after |

The steady state is under 15 GB. A render briefly peaks at 14.6-15.8 GB. If RimWorld runs hot, switch `unity-face-sd.py` from `enable_model_cpu_offload()` to `enable_sequential_cpu_offload()`. That keeps the render at ≤ 1 GB, at a few more seconds per picture. This is not changed yet because the rig is live. Today's stack already sits at ~15 GB with the 8B voice on the GPU, and the brain replaces that 8B.

Service settings, already written in `stream/services.py`, take effect at the next start:
- `OLLAMA_FLASH_ATTENTION=1`, `OLLAMA_KV_CACHE_TYPE=q8_0` on both Ollama servers.
- Once the brain is applied: player context `AUTOPILOT_NUM_CTX=32768`. Her longest training turn plus the 48-tool list is ~24K tokens.
- The autopilot moves from CPU to GPU (`--num-gpu 999`).
- When the brain's voice passed its eval, every voice caller uses the same model and context (`UNITY_VOICE_URL/LLM/NUM_CTX`). That means one resident model and no reload between the player and the voice. The 11435 server stays up but empty.

## 3. Data: `training/data/brain/`

Build: `python training/build_brain.py`. Check: `python training/check_brain.py`. Last run: **PASS, 0 failures**. The check covers:
- tool rows validated against the current schemas
- stream rules on every spoken line
- no stale habits
- no overlap between the eval sets and training
- no owner handle
- the manifest matches

| Kind | Rows | Source |
|---|---|---|
| play | 706 | player.jsonl. 40 truncated at a "once it stands" recital, 12 dropped (closing "After the kill" recital), 7 canned "we just landed and I am about to explore everything" greetings removed. Tools re-pointed at the current `tools.py` list (48 tools; `game_set` gained `map`) |
| knowledge | 2125 | knowledge_game / mods / code / walkthrough |
| voice | 638 | voice.jsonl + voice_stream.jsonl (stream lines, announce lines) |
| chat | 484 | the same files: greetings, chat replies, follows/subs |
| writeup | 150 | catch-ups built only from lines she already said in one episode |
| highlight | 45 | the game's own letters (watch logs), each a `snap` at the letter's cell plus a `say` |
| image | 220 | 160 selfie requests -> `reply_chat` + `webcam` (mood, caption); 60 free-form picture requests -> polite reply + `webcam` (see the gap below) |
| screen | 0 | none yet (see below) |
| **train total** | **4368** | ~11-12M tokens per epoch, including the tool list on tool rows |
| eval_voice (held out) | 63 | 1 in 20 voice/chat lines by hash, never trained on |
| eval_tools (held out) | 21 episodes | 1 in 33 play episodes, never trained on |

- Rows that contain any word from the owner's secret-words list are excluded (10 knowledge rows and 1 voice row hit an ordinary word on that list).
- The owner's orders text inside play prompts is kept verbatim. That is context, not her lines.

**Screenshots:** the 1,700 shots on disk have no answers, so none are used. `python training/collect_screens.py --shots 40` takes the game's own screenshot together with the game's own state at the same moment. It writes Q/A about what the screen always shows: the colonist bar, the letter stack, alerts, pause/speed, and downed or drafted pawns. All of it is read-only bridge calls. Run it, then rebuild. Each shot gives 5-8 rows, and `train.py` then sends them through the vision processor. The vision tower is never trained.

**Gap: "any image a user asks for".** `tools.py` has no free-form picture tool. `webcam` renders Unity and `snap` renders the map. The builder routes free-form requests to an `image` tool automatically once one exists in `tools.py` with a `prompt` (+ `viewer`) argument, for example wired to the persona-studio image endpoint. Until then she politely offers her cam instead.

**Thinking:** every row is trained no-think, which is how the autopilot runs. `plan` turns ask for deep thinking and may get slightly weaker. Unsloth suggests mixing reasoning rows to keep it. That is not done here.

## 4. Pipeline: `training/pod/`

| File | What it does |
|---|---|
| `bootstrap.sh` | Pod start command. Read-only HTTP on :8000 serves `/workspace/gguf` (GET only: no endpoint can start, extend, restart or spend). Refuses to run without `PRICE_PER_HOUR` or without `runpodctl` self-stop. **Hash-bound:** it verifies every file against `MANIFEST.json` and refuses unless the digest equals the `BRAIN_DIGEST` approved at launch. **Cost cap:** a watchdog stops the pod at 92% of `BUDGET_USD / PRICE_PER_HOUR`, counted from the first start and kept on the volume, so a restart never resets it. After success it serves for `KEEP_HOURS` (1 h) and stops itself. After a failure it serves for 15 min and stops. |
| `run.sh` | One shell. Stages, each one marked: setup (Unsloth, transformers 5, fast linear-attention kernels, llama.cpp CUDA sm_90) -> **preflight** (2 steps on the longest rows, proving memory before the paid hours) -> train + merge -> bf16 GGUF -> imatrix (her conversations) -> Q4_K_M + IQ4_XS -> eval -> keep the picked one as `unity-brain.gguf` + sha256. Any input change clears every marker, checkpoint and output. |
| `train.py` | bf16 LoRA r=32 on attention, linear-attention and MLP projections. Seq 24576, 2 epochs, lr 1e-4, bs 2 x ga 8. Checkpoint every 40 steps (resumes on restart). Loss on her turns only (weight-0 refused steps stay context). Screen rows go through the processor. |
| `eval.py` | llama-server per quant. Voice: the stream's exact prompt at temperature 0.9, two seeds, scored by `voice_score.py` (the stream's own filters, pass rate + distinct lines). Tools: the first 6 tool steps of each held-out episode, scoring the same tool with schema-valid arguments. Picks the quant (above). **Voice verdict:** the brain replaces today's voice only if its pass rate is >= today's and its distinct rate is no more than 0.02 lower. "Today's" comes from `baseline_voice.json`. With no baseline, today's voice stays. |
| `voice_score.py` | One scorer, used by both sides. |

On the rig, `training/apply.py`:
- applies `training/models/unity-brain.gguf` as Ollama `unity-brain` (base `qwen3.5:9b`, sha256-checked)
- writes `models/brain-voice.ok` only when `brain-eval.json` says `voice_replaces_today: true`

`stream/services.py` then pulls `qwen3.5:9b` (only once a brain gguf is present) and sets the env above. The old player and voice shells stay for rollback.

## 5. Cost and time estimate

| Step | Time on 1x H100 80 GB |
|---|---|
| setup + llama.cpp CUDA build | 20-25 min |
| base download (18 GB) + preflight | 8-10 min |
| training, 2 epochs, ~23M tokens | 75-110 min |
| merge, bf16 GGUF, imatrix, 2 quants | 20-25 min |
| eval, 2 quants | 15-20 min |
| download window (KEEP_HOURS) | 60 min |
| **total** | **~3.3-4.2 h** |

At RunPod H100 prices of ~$2.0-3.0/h, that is about **$7-13**. The hard cap of $25 stops the pod at 0.92 x 25 / price: ~7.7 h at $3.00/h, ~11.5 h at $2.00/h. Volume disk (120 GB) bills a few cents an hour until it is deleted.

The older memory note says "~$1/hr". The owner's later choice was "Up to ~$25 (Recommended)" with H100-class. This plan follows the later choice.

## 6. Readiness checklist (all must be ticked before the launch is approved)

- [x] Base chosen and justified (Qwen3.5-9B; IQ4_XS default, Q4_K_M fallback by eval)
- [x] Dataset built and `check_brain.py` PASS: 4368 train rows, 63 voice + 21 tool episodes held out, stale habits gone, clean, no owner handle
- [x] Pod scripts: one shell, hash-bound, preflight, checkpoints, cost cap, self-stop, GET-only server
- [x] `apply.py` / `services.py` updated (code only, nothing restarted)
- [ ] **Score today's voice**, between streams: `python training/eval_baseline.py` -> `baseline_voice.json`. Then rebuild + check again. Without it the brain cannot replace the voice.
- [ ] **Pull the base on the rig**, between streams, in the background: `ollama pull qwen3.5:9b` (6.6 GB). Confirm `ollama show qwen3.5:9b --modelfile` has a second `FROM` (the projector), the same as `qwen3.6:35b` does.
- [ ] Optional but recommended: `python training/collect_screens.py --shots 40` while the game runs, then rebuild (adds ~200-300 screen rows).
- [ ] Owner decision: add an `image` tool to `tools.py` for free-form pictures, or keep the cam-only answer.
- [ ] Commit and push `training/` (data/brain, pod, scripts) to the branch the pod clones (`feature/bug-testing`). Copy `digest` from `training/data/brain/MANIFEST.json`.
- [ ] RunPod pod settings to approve:
  - 1x H100 80 GB (SXM or PCIe)
  - a PyTorch **devel** image with CUDA >= 12.4 (nvcc is needed)
  - 40 GB container disk, 120 GB volume at `/workspace`
  - HTTP port 8000
  - start command runs `training/pod/bootstrap.sh` from the branch
  - env: `BRAIN_DIGEST=<digest>`, `PRICE_PER_HOUR=<price shown>`, `BUDGET_USD=25`, `KEEP_HOURS=1`
  - no other keys on the pod
- [ ] After DONE: download `unity-brain.gguf`, `unity-brain.gguf.sha256`, `brain-eval.json` and `quant.txt` from `https://<pod-id>-8000.proxy.runpod.net/` into `training/models/`. Delete the pod and its volume. The next `Stream Start` applies the model.
