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
| Generator | **The original SD1.5 image gen only** (`.claude/tools/unity-face-sd.py`, Realistic Vision): every frame is img2img over ONE reference picture, strength 0.7. **Never SDXL, never inpaint/cut-out compositing** (owner: *"its fucked just cookie cutting images together"*). SDXL is GONE (owner 2026-10-13: *"GET RID OF THE SDXL SHIT WE DONT NEED"*): `unity-face-sdxl.py`, RealVisXL and the SDXL IP-Adapter weights deleted (~8 GB) |
| Reference (her room, side view) | `.claude/.studio-images/unity-reference.png` = `.claude/likeness/unity-scene-home4.png` (owner: *"home $ is a yes"*): side view at her desk in a cozy girl's room, hips/stomach/knees in frame |
| **Room locked** | Each frame is painted whole; outside her zone the picked room's own pixels come back. Her zone = her + chair in the reference **plus her cut out of the new frame** (owner: *"the gilr is like half there half gohosted"* -- fixed), so she is solid wherever she moves. Owner: *"the home-live images whhere perfect"* |
| Girl | the girl in `.claude/.studio-images/cam-1791666443672.png` (`likeness/unity-likeness-original-cam.png`): long dark hair with pink-purple streaks, blunt bangs, choker, **bright pink cat-ear headset, no hats**. Light identity touch only (IP-Adapter Plus Face SD1.5, scale 0.3) -- her face is NOT locked: head, gaze, expression move |
| Every frame | `compose()`: gaze FIRST (owner: *"she has differnt gaze focal points mainly to her off screen screen"* -- side profile to her screen off frame left ~65%, a camera glance ~15%, phone/food/keyboard/eyes closed/thinking the rest; non-camera frames block eye contact and use a lighter face touch), then the outfit -- the full range (owner: *"the rull randge of clothing from blanket to sweater to eating pizza all of it"*): bikini/string/halter tops, sweater, cardigan, hoodies, flannel, tank, sports bra, pajama cami, mesh crop, blanket; pajama shorts/joggers; skirts half the time; slim (owner: *"just dont use chunkey"*) -- then props from her line, a random dynamic action, the mood. Strength 0.75 (0.82 off camera). Proofs: `home-range-4.png` (owner: *"okay those all work"*) |
| **Her own scene / viewer asks** | **SET IN STONE** (owner: *"perfect!!!! build that into everything its ready set what u just did in stone with all the dynamic needs we want for twitch viewer suggeted inputs and contorl"*). Two ways in: (1) her `webcam` tool's `scene`; (2) **every Twitch viewer line she answers** -- `stream-host.py` sends their words as the scene with her reply as the caption and her emotion as the mood (one viewer frame per 45 s). Both go to `scene_words()` in the face service: her loaded brain (`AUTOPILOT_MODEL` from `services.py`) rewrites it into what the camera sees -- no lists, no fallbacks (owner: *"no fallbacks!"*); nudity asks refused (tools.py + face service). Prompt: ask, gaze mix, `SHE` (same girl, 24-year-old white adult -- *"20-25"*, *"white not asian raced"*), clothes. Proof: `viewer-asks-9.png` |
| Wiring | `unity-cam.py` sends the mood; `persona-studio.cjs` now forwards her line as `caption` to the face service |
| Proof sheets | DELETED with every generated Unity/scene picture (owner: *"clear out all those Unity aND SCENE PICS WE GENERATED IN TOTALITY"*); only `unity-reference.png`, `cam-1791666443672.png` and the three likeness files stay. Nothing else is needed: every frame is painted fresh from those |

### Voice
- **Emotions come only from the model** (her `say`/`reply_chat` emotion+act; the stream host's writer returns `[emotion] line`); no guessing. `[laughter]` reaches her own voice, never chat. `!` is spoken as `.` (the voice has no `!` phoneme; every `!` line was silent before).
- **Owner verdict: monotone.** Diagnosis: the 4,845 source clips carried emotion as labels only (one intensity, one pace, Cosy told to stay restrained), all of it stream/colony talk, template-authored (161 lines share an opening). **unity-voice-v2 pipeline, in order -- every step resumable, nothing trains until the owner says "start":**
  1. `expressive_rerender.py` (RUNNING, Cosy venv, GPU, ~6 h): the 3,170 emotional clips re-performed in the A2 voice with the owner-approved pilot recipe (*"i reviewed all expressive-pilot-2026-10-13 they are good to go"*), real intensity 0.25/0.55/0.85 and pace labels, kept only if CAM++ says HER, else the original clip stays; neutral A2 clips untouched -> `D:/voice-lab/dataset-v2-expressive-2026-10-13/`.
  2. `build_offgame_corpus.py` (RUNNING, her brain, ~2-3 h): ~1,500 NEW lines that are not RimWorld (owner: *"we want her to say more than just rimworld"*, *"nothing should ever repeat"*, *"we dont want her remmebring repitiions"*) -- life topics x 9 emotions x 7 acts, stream-clean, no game words, NO 5 words in a row shared with any other line old or new, phonemes within the live vocabulary -> `training/voice/OFFGAME_CORPUS.jsonl`.
  3. `offgame_render.py` (after 1 finishes; Cosy, GPU, ~3.5 h): those lines in her voice, same recipe, a line that is not her is dropped -> `D:/voice-lab/dataset-v2-offgame-2026-10-13/`.
  4. `expressive_screen.py` (CPU, ~2 h, can overlap 3): the pod's speech-recognition screen (faster-whisper base int8, same flags, same 10% rescue, 0.15 s edge trim) on every re-performed clip; a flagged clip falls back to its original recording so all 4,845 lines stay and the vocabulary equals the live voice's; a flagged off-game line is dropped -> `D:/voice-lab/dataset-v2-screened-2026-10-13/` + `screen-report.json` (every fallback listed to listen to).
  5. `local_multipass.ps1` (owner's "start"): passes offgame -> screen -> feats (CPU ~45 min) -> prosody (from the LIVE acoustic model, 30k steps, ~2 h) -> GTA mels -> vocoder polish (warm start from the live 120k weights, fresh discriminator 2k steps alone, 20k joint, batch 16, ~2 h) -> A/B (8 lines live vs new, `D:/voice-lab/unity-voice-v2-2026-10-13/ab/`) -> package **`models/unity-voice-v2/`** (owner: *"this vocie model will be ...-v2 and a folder in model also ...-v2"*). `models/unity-voice/` is never touched; switching the stream to v2 (services.py) is a separate step after the owner listens.
  Guards relaxed on purpose (same voice, same phonemes, new dataset id): `local_prosody_retrain.py` dataset check, `train_vocoder.py --warm-generator` identity (records both). Estimated: training can start ~10-11 h after 2026-10-13 05:30, v2 done ~4.5 h later. The stream cannot run during any GPU step. D: ("Transporter") is the USB voice-lab drive; everything above lives there.
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
