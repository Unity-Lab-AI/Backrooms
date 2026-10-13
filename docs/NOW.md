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
| **Room locked** | Owner: *"so the room is just going to change every time??? i already pioced the room"* -- at strength 0.7 the room was redrawn every frame. Fix in `unity-face-sd.py` (`her_zone()`): each frame is painted whole, then the picked room's own pixels are restored outside her zone (her + chair from the reference, widened ~70 px, feathered ~28 px) -- only she moves. **Built and compiled; the proof sheet (`home-live.png`) was still rendering at handoff -- check it shows one identical room** |
| Girl | the girl in `.claude/.studio-images/cam-1791666443672.png` (`likeness/unity-likeness-original-cam.png`): long dark hair with pink-purple streaks, blunt bangs, choker, **bright pink cat-ear headset, no hats**. Light identity touch only (IP-Adapter Plus Face SD1.5, scale 0.3) -- her face is NOT locked: head, gaze, expression move |
| Every frame | prompt built by `compose()`: outfit FIRST (CLIP reads 77 tokens) -- bikini/triangle/string/halter/crop tops, cozy sweater/open hoodie, deep cleavage, bare shoulders/stomach, a skirt half the time, random outfit every 10-20 min -- then the mood, a random dynamic action, gaze (her PC ~75%, camera ~25%) and props/moments picked from **the line she just said** (soda, coffee, snacks, controller, blanket, stretching, victory, facepalm...) |
| Wiring | `unity-cam.py` sends the mood; `persona-studio.cjs` now forwards her line as `caption` to the face service |
| Proof | `.claude/.studio-images/home-live.png` (8 live-path frames) |

### Voice
- **Emotions come only from the model** (her `say`/`reply_chat` emotion+act; the stream host's writer returns `[emotion] line`); no guessing. `[laughter]` reaches her own voice, never chat. `!` is spoken as `.` (the voice has no `!` phoneme; every `!` line was silent before).
- **Owner verdict: monotone.** Diagnosis (pitch/energy weighted 0.1 in training; emotions squashed to ~1.2 st) and a **local prosody retrain** are set up: `training/voice/local_prosody_retrain.ps1`, data `D:\voice-lab\local-retrain-2026-10-13\`. It was started without the owner's go and **stopped at step 3917** (checkpoint kept). **Do not start it again until the owner says "start"** -- he still has prep. The vocoder also needs a re-polish before a new voice can go live.
- Voice test clips: `.local/qa/voice-session/` (her own choices), `.local/qa/voice-ab/` (accepted samples vs pace 1.0/1.2).

### RimPLC / her player (committed, not yet seen in a live game)
- Ladder rebuilt: 380 rungs / 16 families, a meta prompt per rung (`.local/autopilot/rung-prompts.json`), ~33 new game sensors + `set_host` remote I/O for stream readings, warnings/grouped Sensors tab/RimWorld alert column, unarmed colonist = critical. Record: `docs/RIMPLC_DESIGN.md` "Built status (2026-10-13)".
- 24 new mod commands (`build`, `build_room`, `equip`, `capture`, `zone_create`, `schedule`, `research`, ...), Crashlanded camp commands, situation prompt modules, 18k conversation cap.

### Next, in order
1. Check the room-locked `home-live.png` (one identical room, only she changes); then owner review; tune what he flags in `unity-face-sd.py`.
2. Voice: owner's prep, then the retrain only on his explicit "start".
3. Start: Steam, `start.bat`, GO "fresh crash landed colony, new stream" (Earth3); watch her opening, RimPLC alerts, her webcam.

### Gotchas (do not relearn)
- `.local/qa/` shadows Python's `inspect`: run torch/diffusers scripts from `%TEMP%`.
- Git Bash heredocs mangle `\b`, `\x00` and backslash paths: use the Write/Edit tools.
- Killing by command-line match kills the shell running the match: kill by port/PID.
- SD1.5 + IP-Adapter: no attention slicing; set a `feature_extractor`; re-run `enable_model_cpu_offload()` after `load_ip_adapter`.
- Never start a training run without the owner's explicit "start" for that run.
