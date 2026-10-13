# NOW — the handoff

**ONE RECORD. Owner direction, 2026-10-02, verbatim:** *"and the now.md needs to be completedy deleted, then written current. The NOW .md is a temp read file not a history of all work ever done.. its a one time record only ever holding one record"*

| Ledger | Grain |
|--------|-------|
| `docs/ROADMAP.md` / `docs/TODO.md` / `docs/DECOMPOSED.md` | major / minor / smallest work |
| `docs/TEST.md` | test phase, `[T]` rows |
| **`docs/NOW.md`** (this file) | **the handoff — one record** |
| `docs/FINALIZED.md` | permanent archive, append-only |

---

## LIVE NOW (2026-10-13 ~03:40 local): stream DOWN, RimPLC rebuilt, Unity's webcam look locked, voice retrain prepared (not running)

**Nothing is running; the GPU is empty.** All work is committed on `feature/bug-testing`, not pushed. No pods, RunPod $0.
**Steam must be running before `start.bat`** (2026-10-13: without Steam the workshop mods, Harmony and RimBridgeServer did not load).

### Unity's webcam (owner-approved 2026-10-13) -- read `memory/project_unity_webcam_look.md` before touching it
| Piece | State |
|---|---|
| Generator | **The original SD1.5 image gen only** (`.claude/tools/unity-face-sd.py`, Realistic Vision): every frame is img2img over ONE reference picture, strength 0.7. **Never SDXL, never inpaint/cut-out compositing** (owner: *"its fucked just cookie cutting images together"*). `unity-face-sdxl.py` is in the repo but unused |
| Reference (her room, side view) | `.claude/.studio-images/unity-reference.png` = `.claude/likeness/unity-scene-home4.png` (owner: *"home $ is a yes"*): side view at her desk in a cozy girl's room, hips/stomach/knees in frame |
| **Room locked** | Each frame is painted whole; outside her zone the picked room's own pixels come back. Her zone = her + chair in the reference **plus her cut out of the new frame** (owner: *"the gilr is like half there half gohosted"* -- fixed), so she is solid wherever she moves. Owner: *"the home-live images whhere perfect"* |
| Girl | the girl in `.claude/.studio-images/cam-1791666443672.png` (`likeness/unity-likeness-original-cam.png`): long dark hair with pink-purple streaks, blunt bangs, choker, **bright pink cat-ear headset, no hats**. Light identity touch only (IP-Adapter Plus Face SD1.5, scale 0.3) -- her face is NOT locked: head, gaze, expression move |
| Every frame | `compose()`: gaze FIRST (owner: *"she has differnt gaze focal points mainly to her off screen screen"* -- side profile to her screen off frame left ~65%, a camera glance ~15%, phone/food/keyboard/eyes closed/thinking the rest; non-camera frames block eye contact and use a lighter face touch), then the outfit -- the full range (owner: *"the rull randge of clothing from blanket to sweater to eating pizza all of it"*): bikini/string/halter tops, sweater, cardigan, hoodies, flannel, tank, sports bra, pajama cami, mesh crop, blanket; pajama shorts/joggers; skirts half the time; slim (owner: *"just dont use chunkey"*) -- then props from her line, a random dynamic action, the mood. Strength 0.75 (0.82 off camera). Proofs: `home-range-4.png` (owner: *"okay those all work"*) |
| **Her own scene / viewer asks** | **SET IN STONE** (owner: *"perfect!!!! build that into everything its ready set what u just did in stone with all the dynamic needs we want for twitch viewer suggeted inputs and contorl"*). Two ways in: (1) her `webcam` tool's `scene`; (2) **every Twitch viewer line she answers** -- `stream-host.py` sends their words as the scene with her reply as the caption and her emotion as the mood (one viewer frame per 45 s). Both go to `scene_words()` in the face service: her loaded brain (`AUTOPILOT_MODEL` from `services.py`) rewrites it into what the camera sees -- no lists, no fallbacks (owner: *"no fallbacks!"*); nudity asks refused (tools.py + face service). Prompt: ask, gaze mix, `SHE` (same girl, 24-year-old white adult -- *"20-25"*, *"white not asian raced"*), clothes. Proof: `viewer-asks-9.png` |
| Wiring | `unity-cam.py` sends the mood; `persona-studio.cjs` now forwards her line as `caption` to the face service |
| Proof | `.claude/.studio-images/home-live.png` (8 live-path frames) |

### Voice
- **Emotions come only from the model** (her `say`/`reply_chat` emotion+act; the stream host's writer returns `[emotion] line`); no guessing. `[laughter]` reaches her own voice, never chat. `!` is spoken as `.` (the voice has no `!` phoneme; every `!` line was silent before).
- **Owner verdict: monotone.** Diagnosis: pitch/energy weighted 0.1 in training, emotions squashed to ~1.2 st. **The multi-pass re-train is prepared and NOT started** (owner: *"the prep for the vocie repase multipass run"*; never start without his "start"). One command, resumable, never writes `models/unity-voice/`: `powershell -ExecutionPolicy Bypass -File trainingoice\local_multipass.ps1` (`-Check` = verify only). Passes: (1) prosody fine-tune 3917 -> 30000 steps (~1.6 h at 4.4 steps/s); (2) GTA mels from the new acoustic model; (3) vocoder polish -- warm-started from the LIVE 120k vocoder's weights (it was saved weights-only; the only full checkpoint is step 25000), a fresh discriminator alone for 2000 steps, then 20000 joint steps on the new mels (`train_vocoder.py --warm-generator`); (4) A/B: the same 8 lines through live vs new, F0/accent metrics -> `D:oice-lab\local-retrain-2026-10-13b\` + `ab-report.json`. Nothing goes live until the owner listens. `-Check` PASSED 2026-10-13 04:13 (15.8 GB GPU free, 1.7 TB disk). Note: this PC re-prepared the text frontend (feature_id/frontend_id differ from the pod); the vocoder never sees text, the warm start records both identities. Close the game/Ollama/face service before the run.
- Voice test clips: `.local/qa/voice-session/` (her own choices), `.local/qa/voice-ab/` (accepted samples vs pace 1.0/1.2).

### RimPLC / her player (committed, not yet seen in a live game)
- Ladder rebuilt: 380 rungs / 16 families, a meta prompt per rung (`.local/autopilot/rung-prompts.json`), ~33 new game sensors + `set_host` remote I/O for stream readings, warnings/grouped Sensors tab/RimWorld alert column, unarmed colonist = critical. Record: `docs/RIMPLC_DESIGN.md` "Built status (2026-10-13)".
- 24 new mod commands (`build`, `build_room`, `equip`, `capture`, `zone_create`, `schedule`, `research`, ...), Crashlanded camp commands, situation prompt modules, 18k conversation cap.

### Next, in order
1. Webcam done and owner-approved; watch her first live frames (does she use `scene`?).
2. Voice: owner's prep, then the retrain only on his explicit "start".
3. Start: Steam, `start.bat`, GO "fresh crash landed colony, new stream" (Earth3); watch her opening, RimPLC alerts, her webcam.

### Gotchas (do not relearn)
- `.local/qa/` shadows Python's `inspect`: run torch/diffusers scripts from `%TEMP%`.
- Git Bash heredocs mangle `\b`, `\x00` and backslash paths: use the Write/Edit tools.
- Killing by command-line match kills the shell running the match: kill by port/PID.
- SD1.5 + IP-Adapter: no attention slicing; set a `feature_extractor`; re-run `enable_model_cpu_offload()` after `load_ip_adapter`.
- Never start a training run without the owner's explicit "start" for that run.
