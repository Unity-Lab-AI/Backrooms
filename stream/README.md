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
