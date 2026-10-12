# NOW — the handoff

**ONE RECORD. Owner direction, 2026-10-02, verbatim:** *"and the now.md needs to be completedy deleted, then written current. The NOW .md is a temp read file not a history of all work ever done.. its a one time record only ever holding one record"*

| Ledger | Grain |
|--------|-------|
| `docs/ROADMAP.md` / `docs/TODO.md` / `docs/DECOMPOSED.md` | major / minor / smallest work |
| `docs/TEST.md` | test phase, `[T]` rows |
| **`docs/NOW.md`** (this file) | **the handoff — one record** |
| `docs/FINALIZED.md` | permanent archive, append-only |

---

## The record, 2026-10-12: Unity's own voice + her brain, three pods, waiting on the local voice test

Owner, verbatim: *"update the now.md and what else in the voice work of the todo iss still open work is it all basicly done but waiting on the mini model vocie test before we run all 3 pods together to all accuretly build the shell and voice model to work together"*

**Nothing is rented. No pod exists. Training only runs locally (the mini voice test) on the owner's go.** Standing orders: *"NO POD RENT UNTIL I SAY!"*, *"let me know before u start a training"*.

### The plan: three pods
Owner: *"voice need two pod s remembre one is feeding into the other so 1>1=vocvie model, 1=lora shell"*, *"we dont want one lagging the other and we dont want it taking forever"*.

1. **Voice clip pod** (`VOICE_ROLE=generate`, multi-GPU, recording workers per GPU sized from measured VRAM: 12 on an 80 GB card)
   - Records the approved 5,000-line script with the A2 teachers (Qwen3-TTS + CosyVoice3).
   - Screens every clip with ASR, slows any clip faster than 3.3 words/s (owner: *"Slow to about 3.3 w/s (Recommended)"*; pitch kept, never below 0.80x, never sped up), writes `gen/READY` to the shared network volume, and stops itself.
2. **Voice training pod** (`VOICE_ROLE=train`, H100, same volume)
   - Launched together with the clip pod.
   - Installs while the clips are made, waits for `gen/READY`, then trains the acoustic model + vocoder from scratch (frame budget and vocoder batch scale with VRAM; unchanged on an 80 GB H100).
3. **Brain pod** (separate volume and budget)
   - Retrains the `unity-brain` LoRA shell on `training/data/brain/train.jsonl` (per-step batch 8/4/2 picked by the preflight, effective batch 16).

GPU pegging (owner: *make sure we are peggin these GPUS pod when we do it*): every pod logs GPU util every 30 s; `gpu-util-summary.json` (mean/min util %) comes home with each pull (`out/` for voice, `gguf/` for brain).

Everything comes home to the owner's USB drive **`D:\voice-lab\pod-results\<run>\`** via `pull_results_s3.ps1`:
- all clips (kept and screened-out), receipts, screen report, models, samples, logs, cost and state
- it verifies every file before any volume is deleted

Owner: *"why would i make them if they are only therei while its rented"*, *"make sure it sends home the data information and anxulliray details and info we need to monitor and do checks"*.

### Where things are
| Piece | State | Where |
|---|---|---|
| Voice identity A2 + delivery | **Done.** Owner A/B: dry Cosy instruction, `!` spoken as `.`, everyday A2 take (sad/concerned/frustrated keep the soft take). Receipt binds the 10 heard clips | `training/voice/receipts/delivery-ab-2026-10-12.json`, `SOURCE_DELIVERY_POLICY.json` |
| Voice script, 5,000 lines | **Done, owner-approved** (*"script approved, next is a go"*). 420 laughter lines; all 5,000 route through the renderer | `training/voice/STREAM_CORPUS.jsonl` + `STREAM_EVENT_CORPUS.jsonl`; sources `.local/voice-lab/stream-script/` |
| Corpus approval (gate) | **Done** for the generated-on-pod corpus: script hashes + screen rule + at least 4,500 clips | `training/voice/receipts/corpus-acceptance-stream-script.json` |
| On-pod generation + two-pod split | **Built.** Proven locally on 26 + 200 lines; both teacher environments install and import on Linux (Docker) | branch `feature/voice-pod-ready`: `pod/start_template.sh`, `generate_on_pod.sh`, `auto_screen.py`, `requirements-teacher-*.txt`, `constraints-teacher.txt`, `pull_results_s3.ps1`, `upload_volume_s3.ps1`, `LAUNCH_RUNBOOK.md` |
| Pod safety rails | **Built.** Self-stop with credentials read back from PID 1; SSH-proof; refusal stops the pod; budget-bounded generation; resume keeps the first deadline; read-only progress on :8000 | same branch |
| **Local voice proof, run 1** | **Done.** 200 lines recorded, 198 kept, about 1 h of training (`D:\voice-lab\poc`). Owner: *"all words were reconizable"*, *"most we cut off starts and off pitch and robotic or speed up sounding"*. Measured: 30-45% too fast (3.1-4.6 vs 2.0-3.2 words/s), lead-in 0.03-0.2 s vs the teacher's random 0.03-1.0 s | `D:\voice-lab\poc\samples` |
| **Speed fix (3.3 w/s)** | **Built, not yet heard.** `auto_screen.py` slows kept clips toward 3.3 words/s (librosa phase vocoder, clamp 0.80-1.0); per-clip factor in `stretch.jsonl` + `screen-report.json`. On 20 run-2 clips: mean 4.11 -> 3.53 w/s, 13 reach 3.30, 7 hit the 0.80 clamp (4.5-5.6 -> 3.7-4.5). Before/after WAVs to listen to | `D:\voice-lab\poc\run2-slowed-3.3wps` |
| **Local voice proof, run 2** | **RUNNING.** Same recordings, every clip trimmed to 0.15 s edges (`pod/auto_screen.py`); acoustic done, vocoder about 50 min. Then A/B against run 1 with numbers | `D:\voice-lab\poc\run2` |
| Brain training data | **Done, `check_brain.py` PASS.** 6,462 rows: the original 4,468 + 1,994 "life" rows (hard moments incl. 26 crisis episodes with 988, advice, stream running, boundaries, Q&A, setup, banter, reactions). Every say/reply_chat call carries emotion + act. Fact-checked against the mod; stream-filter and secret-word clean | `training/data/brain/`, sources `training/brain-life/` |
| Live speech | **Done.** `say`/`reply_chat` take emotion + act. `[laughter]` never shown in chat but kept for the own voice (`UNITY_OWN_VOICE=1`). Links spoken *"unity ai lab dot com"* | `.local/autopilot/tools.py`, `guards.py` |
| Brain pod pipeline | **Built** (2026-10-12): pinned `BRAIN_SOURCE_COMMIT`, self-stop credentials from PID 1, own network volume, `training/pod/pull_brain_s3.ps1` brings the run home to D: (verified). Data digest `7d2cac95…` (pacing + admin + fortress + life story + every tool + PLC usage, 8,481 rows; 249-episode scored test set); launch steps in `training/BRAIN_PLAN.md` §7 | `training/pod/` |
| Branches | **Merged and cascaded** (2026-10-12): `feature/voice-pod-ready` merged into `feature/bug-testing`; PRs #33/#34; GitHub and Forgejo (`Main`/`Develop`) match locally at `8f2748bd` / `6b6dafe4` / `7672b94a`. Voice manifest `2afe1740…` (now `3e207e01…` after the GPU-pegging + speed changes, uncommitted) | |
| Speaking over herself | **Fixed in live code.** Owner: *"she need training on how not to over respond ... speaking over herself sending messages before the last finished"*. `say`/`reply_chat` now BLOCK until the line has played (`tools.py` `_speak`). Training: a `pacing` category (one line per turn, one combined answer to floods, deliberate silence); the first, script-built version was rejected (wrong answers paired to questions, canned thoughts) and is being rewritten by hand | `.local/autopilot/tools.py`, `training/brain-life/part-pacing.jsonl` |
| Big local data | Moved to the USB drive with junctions at the old paths; retired seed clips deleted | `D:\voice-lab\` |

### Still open before the three pods (in order)
1. **Voice proof run 2, then the owner listens** (trimmed edges). Laughter is still unconfirmed: ASR heard a laugh on 2 of 20 laughter lines. Owner on quality: *"if it help we can do multi pass and bigger pods"*. Pod plan: ~25x the data and far more training steps; progress samples every 30 min; a second resumed pass if needed.
1b. **Pacing set** (hand-written) finishes, then: assemble, rebuild `train.jsonl`, `check_brain.py` PASS, and record the new brain data digest.
2. ~~Brain pod pipeline~~: done (see table). Still optional: a delivery check in the brain eval (`training/pod/eval.py` scores tools and voice, not the emotion/act choice).
3. ~~Merge and cascade~~: done. Re-cascade after any further change.
4. **Gate:**
   - owner priced training authorization (`owner_training_authorization` + `training_allowed`)
   - engineering receipts for resume, budget/stop and free-running evaluation, using the mini test as evidence
5. **Pod shapes and prices, read live at launch:**
   - clip pod GPU type and count
   - voice training H100
   - brain H100
   - network volumes in an S3-API data center (US-MO-1 had H100 stock)
   - Owner's S3 keys are in `~/.aws/credentials` and work; AWS CLI v2 is installed.
6. **After training:**
   - swap her live voice to the own model (`unity-speak.py` -> `infer.py`, `UNITY_OWN_VOICE=1`)
   - live VRAM measurement on DumbAss with everything up (paper estimate: 18.8 GB of 16 while the old 8B voice-text model runs; ~13.3 GB + TTS with the brain writing the voice lines)

### Gotchas (do not relearn)
- Git Bash rewrites `/paths`, so use `MSYS_NO_PATHCONV=1`.
- Python on Windows writes CRLF, so write with `newline="\n"`; `grep $'\r'` lies here, check bytes in Python.
- Heredoc edits mangled `\b` into backspace bytes twice.
- A laughter line can never be labelled neutral (Cosy refuses neutral).
- The optimized batched Qwen renderer is broken; use the proven `make_dataset.py` renderer.
- RunPod deletes pods, so always use a network volume.
- No local branch checkout while a background job runs from the working tree.
- The game's Mods folder is not touched unless told.

### Other state
- Mod: the game copy, `Mod/`, the build manifest and both mod remotes (`51540ff`) all match the working 0.13.0-dev.
- RimBridgeServer must be re-enabled in RimSort before she can play on stream.
- Monitoring: a 20-min cron check-in runs in this session (session-only, expires in 7 days).
