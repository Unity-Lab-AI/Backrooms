# VOICE v2 OVERNIGHT RUNBOOK — read this FIRST on every cron wake

Owner, 2026-10-13 ~05:45 local, verbatim: *"SO IM GOOD TO GOTO BED AND YOULL HANDLE THE START OF THE MULIPASS 2ND PASS WHEN IT COMES?"* -> answered yes.
**This IS the owner's explicit "start" for THIS run only** (the unity-voice-v2 multi-pass). It is not a go for any other training.
Also verbatim: *"set a wake up for when it error or finished so you can take casre and do the checks then instantly jump in to the pass 2nd"*.

## Never, without the owner awake
- Never switch the stream to v2 (`stream/services.py` keeps `models/unity-voice/`). He listens to the A/B first.
- Never touch `models/unity-voice/`. Never push. Never delete anything on D:.
- Never start any OTHER training run.

## Stages, in order (every one resumes if re-run)
| # | Stage | Done when | Log | Start command (from `%TEMP%`, never from the repo: `.local/qa` shadows `inspect`) |
|---|---|---|---|---|
| 1 | Emotional clips re-performed (GPU, Cosy) | `D:/voice-lab/dataset-v2-expressive-2026-10-13/rerender-report.json` | `.local/qa/_rerender.log` | `.local/voice-lab/.venv-cosy/Scripts/python.exe training/voice/expressive_rerender.py` |
| 2 | Off-game lines written (her brain, Ollama) | `training/voice/OFFGAME_CORPUS.report.json` | `.local/qa/_offgame.log` | `python training/voice/build_offgame_corpus.py --target 1500` |
| 3+ | Everything else, one command: offgame render -> screen -> feats -> prosody -> GTA -> vocoder -> A/B -> package | `models/unity-voice-v2/` exists + `D:/voice-lab/unity-voice-v2-2026-10-13/ab-report.json` | `D:/voice-lab/unity-voice-v2-2026-10-13/multipass.log` | `powershell -ExecutionPolicy Bypass -File training\voice\local_multipass.ps1` |

Run stage 3 with `nohup ... > .local/qa/_multipass.log 2>&1 &` (background). Only start it when BOTH 1 and 2 are done.

## Before starting stage 3 (the checks)
1. Both reports exist; no `Traceback` in `_rerender.log` / `_offgame.log`.
2. **Kill Ollama** (stage 3 needs the GPU): `taskkill //IM ollama.exe //F` and any `llama-server.exe` (by PID from `nvidia-smi`/`tasklist`). GPU should drop under ~1 GB.
3. `powershell -ExecutionPolicy Bypass -File training\voice\local_multipass.ps1 -Check` must print `CHECK PASSED` (it will say features not prepared yet — that is fine).
4. Then start stage 3 in the background.

## On every wake
- Progress: `wc -l` on `D:/voice-lab/dataset-v2-expressive-2026-10-13/progress.jsonl` and `training/voice/OFFGAME_CORPUS.jsonl`; tail of the stage-3 log once it runs.
- **Stalled** (no growth for 20+ min) or **error**: read the log tail, fix the cause, re-run the same command (it resumes). Commit code fixes on `feature/bug-testing` (no push).
- Known fix already in: off-game writer skips lines with stage markup (crashed once at 100 lines).
- Known slow-down: re-render runs ~0.16 rows/s while the brain shares the GPU; faster once stage 2 ends.
- If nothing changed: one short line.

## When stage 3 finishes
- Read `ab-report.json` (pitch spread, accent, emotion spread: live vs new) and the end of `multipass.log`.
- Update `docs/NOW.md` (voice section) with the result and where the A/B clips are (`D:/voice-lab/unity-voice-v2-2026-10-13/ab/live` vs `/new`), commit.
- Stop the cron watch (CronDelete) and leave one clear summary for the owner: what finished, the numbers, where to listen, and that v2 is NOT live yet.
