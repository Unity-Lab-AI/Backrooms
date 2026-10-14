# Test-run notes — RimWorld 1.7 + Rimrooms + RimPLC, the full kit (2026-10-13 evening)

Owner, verbatim: *"kil the cron, and start a new one that monitors Unity , the game , and the stream, and takes nots of issues that all we will be fixing after the test run of rimworld 1.7 rimrooms and rimplc to test the full kit and cabutel"*.

**This file is a ledger of what was seen, not a work queue.** Nothing here is fixed during the run; every entry is read after the run and turned into TODO rows in the owner's words, then fixed. Append-only, newest at the bottom. Each entry: when (local), area, what was seen, the evidence (log line / file / screenshot path), how bad.

Areas watched, once a minute, read-only:
- **Unity** — her play loop (`.local/qa/_svc_autopilot.log`: stalls over 3 min with no model step, talk with no matching tool call, refusal loops, commands she asks for that nothing answers), her voice (`_svc_voice.log`, silence over 30 s with chat waiting, garbled or runaway lines from v2), her webcam (`_svc_studio.log` / `_svc_face.log`: frames failing, wrong girl, nudity refusal misfires), the clean-stream rule (anything rough reaching the overlay/voice), chat answered or missed.
- **The game** — `Player.log`: red errors naming Rimrooms or RimPLC, `[RimBridge]` server state, missing textures, exceptions on load; `RimroomsAutomation/outbox.jsonl` lines starting `refused:` (commands she tried that the mod would not do); RimPLC alerts that fire wrongly or never; rungs stuck unresolved; freezes.
- **The stream** — `python stream/services.py status` (anything DOWN), OBS/Twitch/host logs, Ollama 500/499 or calls over 60 s, GPU memory over 15.5 GB or pinned over 95 %.

Severity: **blocker** (stream or game down, she cannot play), **wrong** (does the wrong thing, says the wrong thing, breaks a rule), **rough** (works but ugly, slow or confusing), **note** (worth knowing, no action implied).

| When | Area | What was seen | Evidence | How bad |
|---|---|---|---|---|
