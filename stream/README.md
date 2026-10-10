# Stream switch

One press each, nothing to remember. The presses live in the **Backrooms root**:

| Platform | Start | Stop | Panel |
|---|---|---|---|
| Windows | `windows\start.bat` | `windows\stop.bat` | `windows\admin.bat` |
| Linux / macOS | `linux/start.sh` | `linux/stop.sh` | `linux/admin.sh` |

All of them call `stream/services.py`, the engine (tracked here). `.local/qa/services.py` is the same file
resolving its paths from the dev surface; the old root `Stream Start.cmd` / `Stream Stop.cmd` just call the
`windows\*.bat` pair, so there is exactly one way the rig comes up and goes down.

**Start** brings up Ollama and both models (the voice pre-warmed), OBS, the Twitch window, the studio, the
webcam, chat, the host voice, the guards, the click queue, Unity the player, and the admin panel at
`http://127.0.0.1:4318/`. Then she **asks** -- out loud and in the panel's Ready? card -- what you want
tonight. **GO** in the panel makes that binding, launches RimWorld, takes OBS live, and arms the company
colony. Nothing goes live before GO.

**Stop** kills by name first (`llama-server`, `ollama`, `obs64`, `RimWorldWin64`), then sweeps the services,
then prints the GPU so you can see the memory came back. It never touches your browsers.

Each service logs to `.local/qa/_svc_<name>.log`. Status any time: `python stream/services.py status`.

## What the autopilot is allowed to touch

Enforced in code, under the model, in `.local/autopilot/guards.py` -- the model cannot talk its way past it:

- **The game, through the bridge and the mod's own automation channel only.** An explicit allowlist of
  bridge calls. A second filter rejects anything matching lua, script, debug, mod, reorder, load_game,
  main_menu, god_mode, spawn or compile even if someone widens the allowlist later. UI clicks and menu
  options carrying *mods*, *dev mode*, *quit*, *load*, *delete*, *abandon*, *banish* or *execute prisoner*
  are refused. She cannot start a game herself; the switch does that at GO.
- **The stream.** Spoken lines, the real Twitch chat, title and category, captions -- every one through the
  clean-stream filter, with emoji, URLs, paths and anything secret-shaped stripped.
- **Nothing else on the machine.** There is no shell and no process control. Writes are limited to small
  text files inside `.local/autopilot/scratch`; reads are allowlisted, and `.env`, `user.json`, tokens,
  passwords, credentials, keys and the Twitch profile are unreadable -- so it cannot see the stream key or
  any account secret. Saves are forced to the `rimbridge_save_` prefix.
- **It never edits the mod or writes code.** That is the reason it exists in this shape.

## Restart without dropping the stream

`windowsestart.bat` / `linux/restart.sh` restart everything **except the broadcast**: OBS switches to the BRB
scene and keeps streaming, so viewers never see Twitch's network error. She asks Ready? again, and GO switches the
stream back to Live (GO never relaunches an OBS that is already up). Only **stop** ends the broadcast.
