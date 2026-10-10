# Stream switch

Two presses, nothing to remember.

| Platform | Start | Stop |
|---|---|---|
| Windows | `stream/windows/start.bat` | `stream/windows/stop.bat` |
| Linux / macOS | `stream/linux/start.sh` | `stream/linux/stop.sh` |

Both call `.local/qa/services.py`, which starts anything that is not already running and stops everything
it finds. A service already up by another route is recognised, never started twice. Each one logs to
`.local/qa/_svc_<name>.log`.

**RimWorld is never touched.** The game is yours to launch and to close.

Services under the switch: the studio window, the webcam renderer, the Twitch chat bridge, the host voice,
the pop-up guard, the heat guard, the cursor-job queue, and the autopilot.

Status any time: `python .local/qa/services.py status`

## What the autopilot is allowed to touch

Enforced in code, under the model, in `.local/autopilot/guards.py` — the model cannot talk its way past it:

- **The game, through the bridge only.** An explicit allowlist of bridge calls. A second filter rejects
  anything matching lua, script, debug, mod, reorder, load_game, main_menu, god_mode, spawn or compile even
  if someone widens the allowlist later. UI clicks and menu options carrying *mods*, *dev mode*, *quit*,
  *load*, *delete*, *abandon*, *banish* or *execute prisoner* are refused.
- **The stream.** Spoken lines, chat replies and captions, every one through the clean-stream filter, with
  emoji, URLs, paths and anything secret-shaped stripped.
- **Nothing else on the machine.** There is no shell and no process control. Writes are limited to small text
  files inside `.local/autopilot/scratch`; reads are allowlisted, and `.env`, `user.json`, tokens, passwords,
  credentials, keys and the Twitch profile are unreadable — so it cannot see the stream key or any account
  secret. Saves are forced to the `rimbridge_save_` prefix.
- **It never edits the mod or writes code.** That is the reason it exists in this shape.
