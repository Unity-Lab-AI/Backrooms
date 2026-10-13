# NOW — the handoff

**ONE RECORD. Owner direction, 2026-10-02, verbatim:** *"and the now.md needs to be completedy deleted, then written current. The NOW .md is a temp read file not a history of all work ever done.. its a one time record only ever holding one record"*

| Ledger | Grain |
|--------|-------|
| `docs/ROADMAP.md` / `docs/TODO.md` / `docs/DECOMPOSED.md` | major / minor / smallest work |
| `docs/TEST.md` | test phase, `[T]` rows |
| **`docs/NOW.md`** (this file) | **the handoff — one record** |
| `docs/FINALIZED.md` | permanent archive, append-only |

---

## LIVE NOW (2026-10-13 ~04:55 UTC): full handoff -- read this first after a compaction

**No pods, no volumes, RunPod spend $0.** Both trainings finished 2026-10-12, were pulled to the USB drive,
verified (checksums) and deleted with the owner's go (*"last check make sure we are ready, then do it"*).

### What is live on this PC now
| Piece | Where | State |
|---|---|---|
| **Brain** `unity-brain` (Qwen3.5-9B + LoRA, IQ4_XS, 5.3 GB) | `models/unity-brain/` (weights git-ignored; master copy `D:\voice-lab\pod-results\brain-2026-10-12\`) | Applied to Ollama :11434 by `training/apply.py` (sha-checked, reads `models/unity-brain`). Plays the game AND writes her lines (owner chose *"Brain writes lines too"*, `training/models/unity-brain/brain-voice-owner.json`). `models/unity-brain/` is a standalone package: gguf + vision gguf + portable `Modelfile` + usage README; build records + apply stamps in `training/models/unity-brain/`. Eval: life 100%, play 96%, RimPLC 92%, rare tools 53% (weak spot), overall tool 82% |
| **Her own voice** (acoustic.pt + vocoder.pt, 165 MB) | `models/unity-voice/` (master `D:\voice-lab\pod-results\voice-2026-10-12\out\models\f8bb6cd3...`) | Accepted: owner *"smaples are perfect"* -> `training/voice/receipts/trained-voice-acceptance-2026-10-12.json` (bound to file hashes). Standalone package (weights + run code + `unity_voice.py` loader + usage README; build notes in `training/voice/receipts/unity-voice-2026-10-12/`). Served by `models/unity-voice/serve.py` :5123 = the `voice` service in `stream/services.py`; `unity-speak.py` posts every line with the brain's emotion/act. **No fallback voice** (owner: fallbacks are against the laws; Piper retired). Pace **1.0** (`UNITY_VOICE_LENGTH_SCALE`; owner: 1.2 was *"1/5th too slow"*) |
| Line writer `unity-local`, player `unity-player`, Piper | `training/models/`, Ollama | Installed for manual rollback only, not loaded |
| **Launchers** | `windows/start.bat`, `Stream Start.cmd`, Desktop `Unity Plays RimWorld.cmd` | All run `stream/services.py start` -> new brain + own voice (`UNITY_OWN_VOICE=1`) |
| **16 GB budget** | `.local/qa/vram-stress.py`; results in `models/README.md` | Brain + voice + webcam peak **11.3 GB** (5.1 GB free, no game/OBS). Two LLMs peaked 15.9 GB -> rejected. Every brain call must use 32K ctx (the stream pins it) or Ollama reloads at ~14 GB |
| **RimPLC** (new 1.7 layout, built 0 warnings, `rimplc-check` valid) | Game `Mods/RimPLC` + `BridgeTools/RimPLC` | Staged + deployed 2026-10-13 (old copy in `.local/staging-backup/`). Own repos: GitHub `G-Fourteen/RimPLC`, Forgejo `GFourteen/RimPLC`; owner: keep both copies in sync. Wiki live: `g-fourteen.github.io/Rimrooms-AsyncIndustries/rimplc.html` |
| **Twitch** (live channel; Playwright over CDP :9333 on the stream's Twitch window, profile `.local/twitch-profile`) | `docs/TWITCH_PANELS.md`, `docs/twitch-panels/` | New bio (both mods); social link "Report a bug" -> "RimPLC mod & wiki" (owner choice, cap 5); 4 RimPLC link panels + "RimPLC: colony logic mod" panel. Verified on the public About page |

Gate: `training/voice/VOICE_QUALITY_GATE.json` -- trained_voice_acceptance passes; **local_playback_acceptance** is the last
deploy check (owner hears her through OBS during the rehearsal).

### RimWorld 1.7 unstable (owner 2026-10-13: "we are temporarilly on a unstable version")
| Piece | State |
|---|---|
| Game | **1.7.4976 rev1043** (Waylith). Exe `RimWorld.exe`, window class `GLFW30`, log now `<LocalLow>/.../Logs/Player.log` with a timestamp prefix on every line |
| Mods | All **297** active (`ModsConfig.xml`; copy `ModsConfig.full-1.7-2026-10-13.xml`). Rimrooms 1.7 layout staged (old 1.6 copy in `.local/staging-backup/`). Map Preview loads through its 1.6 folder |
| Bridge | `.local/qa/bridge.py` reads both log formats/locations (Unity, admin, gates, eyes all go through it); `tools/qa/rimbridge_readonly.py` too |
| Stream | `services.py` finds `RimWorld.exe`; OBS scene `Untitled.json` points game video + audio at the 1.7 window (backup `.pre-rw17`); `obs-setup.py` picks the right one |
| GO | The switch closes debug/log windows, Unity says the 1.7-beta line over the main menu for 15 s, GO text with "crash landed" -> **Crashlanded** (else the company start), world seed **Earth / Earth2 / Earth(n)** (`.local/qa/_earth_seed.count`, absent = Earth) |
| New game | Driver: Cassandra Classic / Community builder / reload anytime, pollution 0, 30%, factions = all peaceful + Pirate (only red) + cannibal + nudist tribes, 300x300 Spring. **Map pick** (`MapVariantPicker.cs`): 60 Map Preview seeds per batch, up to 5 batches; qualifies when the main mountain touches east AND west edges and is 30%+ of the map with a nook dug into it; commits + reads back the seed. Live: 60/60 in 10 s, 22 qualified, #2 chosen (48%), owner: *"looks good"* |
| Build | 1.6 references are gone after the update: built against **Krafs.Rimworld.Ref 1.6.4871** (`docs/BUILDING.md`), DLL copied by hand to repo + game |
| Prompt | `.local/autopilot/prompt.md` THE GAME VERSION: temporary 1.7 beta, 296 other mods, never touch debug windows |

### First live run on 1.7, 2026-10-13 (~22:15-22:52 local) -- what broke and what is fixed
Owner stopped it (*"okay shut it all down she had major bugs in the game need fresh start and new streeam"*), then
updated the GPU driver with everything loaded and is **restarting the PC**. Everything was shut down cleanly first;
the 1-minute monitor cron is cancelled (session-only, gone with the session anyway).

| Problem seen live | Cause | Fix (committed) |
|---|---|---|
| Red X pawns/items | stream launched RimWorld from `common\Rimworld` (lowercase w); 1.7 then missed 485 Core textures | `services.py` RW_DIR uses the real casing `common\RimWorld` (+3 tools). Launched that way: 0 missing |
| She barely talked; brain HTTP 500s | webcam SD on the GPU + game + OBS overflowed 16 GB; every brain call timed out | webcam model on the **CPU** (`unity-face-sd.py`, ~2 min a frame, 20 steps); `UNITY_FACE_DEVICE=cuda` puts it back |
| Talked about storage 10x, never built it | play loop hung: her requests carried `use_mlock`/`num_thread` (load-time options) -> Ollama tried a 2nd copy, load failed, turns hung; the talk was the filler voice | options removed from `autopilot.py` |
| Turns 60-260 s | the 1.7 game renders flat out and starves the GPU (a 14K-token turn took 127 s; idle it is ~6 s) | **owner set NVIDIA Max Frame Rate 30 for RimWorld.exe** (persists) |
| NUM_PARALLEL=2 | Ollama: "model architecture does not currently support parallel requests" (qwen35) | reverted |
| Talking over herself / 3-4 chat rows at once | every speaker posted chat when its line was READY | one voice lock + chat row posted by `unity-speak.py` when the line starts playing (rows landed 8-26 s apart) |
| Two feeds heard | the stream Twitch window played the broadcast back | that window launches `--mute-audio`; **MUTE** button in the studio window header (local only) |
| Too fast | -- | `models/unity-voice/pace.txt` read before every line: **1.2** (1.0 natural, higher slower) |

Not fixed / still open: the host voice's stream filter rejects many lines ("nothing the model wrote passed");
RimPLC Twitch panels are live (owner's paste just stopped short). Map pick worked live (Earth2: #1, 39% E-W + nook).

### Next, in order
1. **After the PC restart** (owner 2026-10-13: *"it telling me to restart my PC.. so write now.md and be done"*):
   check the NVIDIA frame cap survived the driver update (Manage 3D settings -> RimWorld.exe -> Max Frame Rate 30).
2. `start.bat`, GO with "fresh crash landed colony, new stream" -> world seed **Earth3**. Start the 1-minute monitor
   again: play stall >3 min, repeated talk with no matching TOOL, silence >30 s, chat bursts, Ollama 500/499 or >60 s,
   DOWN services, "No textures found", GPU >15.5 GB / >95 %.
3. Owner hears her through OBS -> record **local_playback_acceptance** in his words.
4. Later: tighten the host filter; more rare-tool examples (53%); voice resume (only a step-25,000 full vocoder survives).

### Gotchas learned 2026-10-12/13
- `.local/qa/` holds a file that shadows Python's `inspect`: run Playwright scripts from `%TEMP%`, not `.local/qa`.
- Twitch panel add: `.create-panel button` -> "Add a Text or Image Panel" -> `input[type=file]` -> crop dialog **Done** -> fill title/link/alt/textarea -> Submit (greys out when saved).
- RunPod S3 is slow and resets big downloads; sync folders by name, skip teacher models (re-downloadable).
- A voice code change re-keys the run namespace; `VOICE_RESUME_RUN_ID` resumes a finished namespace when only the source digest differs.
- Python heredocs with Windows paths break on `\u`; use the Write/Edit tools for text with backslashes.
- Never leave RimWorld running after a test: it holds ~6 GB of GPU and the owner cannot start the stream (owner: *"u left the game open a 6G on gpu i cant run that yet"*).
- start-scenario must stop at every page after the scenario page; pressing through the tile page beat the map picker once.
- On 1.7 the scenario page repeats the selected scenario's title beside Back; only the list row may be clicked.
- Never ask Ollama for load-time options (use_mlock, num_thread...) that differ from the loaded brain: it loads a second copy, fails on 16 GB, and the caller hangs.
- Ollama's live log is `.local/qa/_svc_ollama.log` (not %LOCALAPPDATA%/Ollama/server.log) once the stream starts it.
- 1.7 writes the game log to `<LocalLow>/.../Logs/Player.log`; line 8 shows the launch path (check the casing).

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
| Branches | **Merged and cascaded** (2026-10-12): `feature/voice-pod-ready` merged into `feature/bug-testing`; PRs #33/#34; GitHub and Forgejo (`Main`/`Develop`) match locally at `8f2748bd` / `6b6dafe4` / `7672b94a`. Voice manifest `2afe1740…` (now `81fda2b3…` after the GPU-pegging + speed changes, uncommitted) | |
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

## RimWorld 1.7 package work — 2026-10-12

The owner requested Rimrooms and RimPLC game-version target 1.7, the unchanged-style preview label RIMWORLD 1.7, all supporting docs/wiki, and a standalone RimPLC repository at https://git.unityailab.com/GFourteen/RimPLC with a possible GitHub mirror. Read [the migration record](implementation/RIMWORLD_1_7_MIGRATION.md) and its evidence folder for this bounded task.

Both packages now map game 1.6/1.7 to their existing shared content; the own mod releases stay Rimrooms 0.13.0-dev and RimPLC 0.1.0. Local compile/reference evidence still uses installed RimWorld 1.6.4871; 1.7 runtime is not verified. The game Mods/profile/session is not switched or staged by this task. Earlier claims above that the repository/package/game copy all match describe the pre-migration checkpoint.

The preview edit is saved in Mod/Rimrooms - Async Industries/About/Preview.png, with prior image/prompt under outputs/preview-touchup-2026-10-12. Rimrooms, RimPLC core and its optional bridge each compiled against 1.6 with zero warnings/errors. The 200-file Rimrooms ZIP is refreshed, and the clean complete local public package/wiki is outputs/rimrooms-1.7-distribution-2026-10-12-v2 (288 files). The wiki renderer produced 17 pages; current docs and old evidence are version-separated. Rimrooms' existing remote/site was not published by this task.

The standalone RimPLC export excludes voice/brain training, the work ledger and provider assemblies. After automatic approval review initially rejected conditional public creation, the owner explicitly approved: "Yes — create public GitHub and publish to both". GitHub https://github.com/G-Fourteen/RimPLC was created, and both it and https://git.unityailab.com/GFourteen/RimPLC now hold main at bcfb3b713235a885927984efdcb53a09a9b725e6, read back in tool output. The standalone export contains 33 reviewed files with code, core/optional-companion DLLs, guide, schemas and license. The completed bounded milestone is archived in FINALIZED.md; actual 1.7 runtime remains unverified. Working-source changes from this task remain available here for the lead to integrate; no parent branch was checked out or source cascade run during the model jobs.

This mod task does not change the active voice/brain sources, training manifests, models, pod launch/stop controls or current job monitoring. Preserve the live training continuation above.

## RimPLC branding artwork — 2026-10-12

Owner request: "and we need some proper RimPLC images mad for it not menu and load screens tho".
Two original images are complete: `RimPLC/About/Preview.png` (1672×941, RIMWORLD 1.7, no development version) and `RimPLC/About/RimPLC_Badge.png` (1254×1254, true RGBA transparency). The badge is branding, not a newly wired game control. Exact prompts, source masters and hash/alpha observations are under `assets/source/rimplc/`; read its README for the bounded delivery record.

The RimPLC package manifests/export allowlist include both files. Workspace/standalone READMEs and the public wiki guide show/link the artwork. The refreshed standalone export has 35 files, with the existing source snapshot unchanged. The artwork checkpoint is staged for publication to the two approved RimPLC `main` repositories; the subsequent remote read-back in tool output is the publication receipt. The parent source branch/cascade, game Mods/profile, Rimrooms menu/load art, current training/voice/brain files and pods are untouched by this task. RimWorld 1.7 runtime remains unverified.

## Current content-folder correction — 2026-10-12

Owner: "might need to fix that all around the backrooms folder" / "i doont want my 1.7 saying 1.6".
Read [CONTENT_FOLDER_1_7_LAYOUT.md](implementation/CONTENT_FOLDER_1_7_LAYOUT.md) before the earlier October 12 migration section: its shared physical `1.6/` decision is superseded. Current folders are `Mod/Rimrooms - Async Industries/1.7/` and `RimPLC/1.7/`; both game-version loaders select that single folder. Current scripts, build destinations, package lists/manifests and docs/wiki use `1.7/`. Dated source/build/play observations and explicitly retained backups remain historical.

All 196 Rimrooms and three RimPLC moved content files retain identical bytes. All three projects compiled with zero warnings/errors; the game references are still installed 1.6.4871, with 1.7 runtime acceptance pending. The 200-file Rimrooms ZIP and both local distribution exports are refreshed: Rimrooms 288 files, RimPLC 35. Old RimPLC export/receipt were preserved in `.local/export/RimPLC-before-1-7-2026-10-12*`; existing Git history was retained in the new default export.

The bounded standalone distribution checkpoints are prepared for the approved remote publication; subsequent tool read-backs are the receipt. Parent source changes remain here for the lead to integrate: no parent branch checkout/cascade, game staging/profile/save/session change, training/model edit or pod action occurs in this layout task. Preserve the live training continuation above.

The prepared standalone layout commits are RimPLC `3d1bd3d18ade24fac55886b6f10b70815ce3b758` and Rimrooms `29f33ec10450728783934cf71b7860abd37dbc06`. Git's staged-file bytes match all 35/288 reviewed export files respectively; no `1.6/` content folder remains in either index. Existing CRLF payload bytes are preserved; whitespace inspection uses Git's `cr-at-eol` recognition alongside its normal whitespace checks. The subsequent push/read-back output owns the remote receipt.
