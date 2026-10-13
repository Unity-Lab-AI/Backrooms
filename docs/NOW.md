# NOW — the handoff

**ONE RECORD. Owner direction, 2026-10-02, verbatim:** *"and the now.md needs to be completedy deleted, then written current. The NOW .md is a temp read file not a history of all work ever done.. its a one time record only ever holding one record"*

| Ledger | Grain |
|--------|-------|
| `docs/ROADMAP.md` / `docs/TODO.md` / `docs/DECOMPOSED.md` | major / minor / smallest work |
| `docs/TEST.md` | test phase, `[T]` rows |
| **`docs/NOW.md`** (this file) | **the handoff — one record** |
| `docs/FINALIZED.md` | permanent archive, append-only |

---

## LIVE NOW (2026-10-13, early morning local): stream DOWN, RimPLC rebuilt, Unity's new look, SDXL webcam being built

**Nothing is running.** The owner stopped the stream after her first 1.7 run went badly (looping, deferring orders, building
in the mountain, no laughs, flat voice). Everything since has been rebuild work, committed on `feature/bug-testing`, not pushed.
No pods, RunPod spend $0. **Steam must be running before `start.bat`** (2026-10-13: Steam did not start after the PC
restart, RimWorld launched without workshop mods, Harmony was missing and RimBridgeServer failed to load).

### What changed tonight (all committed, none of it seen in a live game yet)
| Area | State |
|---|---|
| **RimPLC ladder** | Rebuilt: 380 rungs / 16 families from 880 owner orders + walkthroughs, a meta prompt per rung, ~33 new game sensors, a `set_host` remote-I/O channel for stream readings, sensor warnings + grouped Sensors tab + RimWorld alert column. Record: `docs/RIMPLC_DESIGN.md` "Built status (2026-10-13)"; working files `.local/plc-rebuild/` |
| **Her player** | Prompt = small core + one situation module (top rung's family) + the live rung's `HOW TO DO` prompt; conversation cap 18k inside the 32k context (the prompt was being cut from the front); 3rd identical tool call refused; owner orders outrank the ladder (rule 0); `num_gpu` no longer sent (reload risk) |
| **Crashlanded opening** | Mod commands `unforbid`, `chop`, `shelter`, `stockpile_camp`; explore no longer digs into far mountain pockets; start kind recorded; meat counts as food; arms first (rung 2.6 unarmed = critical) |
| **Personality / voice** | Flirty, confident, banters beyond the game, real back-and-forth with viewers; laughs (`[laughter]` reaches her own voice, never chat); every line carries an emotion (unlabelled/neutral lines get one worked out from the words); answers the owner's chat out loud without his name |
| **Her look** | Locked: girl-next-door with a hint of emo, light caucasian skin, black wavy bob with pink ends, choker, busty, very short crop tops (wardrobe `.claude/.studio-images/wardrobe/`, rotates every 20 min), no tattoos, human-realism prompts. Reference `.claude/likeness/unity-likeness-2026-10-13.png`. Owner allows underboob/sideboob (Twitch risk explained, his call) |
| **Drugs** | Colonists on No drugs; drugs are for hospitality guests |

### In progress
- **SDXL webcam renderer** (background agent): face-locked SDXL + IP-Adapter for real expressions, the desk IN FRONT of her
  (room behind), standing shots from mid-thigh in a skirt, "walked away" shots, half the fabric on the chest. It must show a
  sample sheet, seconds per frame and peak VRAM before anything switches live.

### Next, in order
1. Owner approves (or not) the SDXL sheet; switch `unity-face-sd` only on his yes.
2. Start: Steam, then `start.bat`, GO "fresh crash landed colony, new stream" (Earth3). Watch: arms first, unforbid/chop/
   stockpile_camp/shelter beside the crew, no mountain digging, laughs, emotions, chat answered, the RimPLC Sensors tab and
   alert column.
3. RimPLC build list still open (`.local/plc-rebuild/inventory.md` D/E): schedule, drug-policy, barricade, build and
   research commands; window displays beyond the Sensors tab; `pawns_unconfigured`.
4. Sync the standalone RimPLC repos (GitHub `G-Fourteen/RimPLC`, Forgejo `GFourteen/RimPLC`) -- needs the owner's go.

### Gotchas (do not relearn)
- `.local/qa/` shadows Python's `inspect`: run torch/diffusers/Playwright scripts from `%TEMP%`.
- Git Bash heredocs turn `\b` into a backspace and `\x00` into a NUL byte: use the Write/Edit tools for regex/escapes.
- Killing a process by command-line match kills the shell that runs the match; kill by port/PID.
- CLIP reads 77 tokens: put the mood/layout words FIRST in image prompts.
- SD1.5 img2img cannot change an outfit or a pose while keeping the face: inpaint the torso/face region instead.
- Never ask Ollama for load-time options that differ from the loaded brain (it loads a second copy and hangs).
- 1.7 log: `<LocalLow>/.../Logs/Player.log`; line 8 shows the launch path (check the casing and that Steam is up).
