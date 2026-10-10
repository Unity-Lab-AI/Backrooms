# Unity autopilot: open-weights Unity that runs the stream by herself

**Owner direction (verbatim):** *"remember bhind the scnes you need to be building this whole thing to run on the best model possible thats open souiurce that can basicly do everything you do that u fully set up from streaming to useing rimworld excactly all as i do with coding knowledge but doesnt and never shall edit the mod or fix code"*

The autopilot is a Python orchestrator. It drives a local open-weights model through Ollama's `/api/chat` tool calling and plays "Unity Plays RimWorld" end to end. It plays the colony through RimBridge, narrates in Unity's clean stream voice, greets and answers Twitch chat, posts webcam pictures, follows `docs/PLAYSCRIPT.md` and acts on the first FIX in `.local/qa/run-list.py`. It never edits the mod or fixes code. The **tool layer** enforces that, so it does not depend on the prompt.

## Model choice (October 2026)

| Role | Model | Why |
|---|---|---|
| **Primary, single model** | `qwen3.6:35b` (Qwen3.6 35B-A3B MoE, Q4, about 24 GB) | It handles tools, vision (text+image input) and thinking in one model, has a 256K context and was built for agentic coding. Only about 3B parameters are active per token, so it still runs at usable speed with most experts in the 128 GB of system RAM. That matters because the stream leaves only about 4.5 GB of free VRAM. One model sees screenshots and calls tools, so models never get swapped in and out mid-turn. |
| Fallback (lighter, also vision+tools) | `gemma4:26b` (MoE, about 17 GB) | Use it if Qwen's tool calls misbehave on your Ollama build. |
| Text-only fallback | `gpt-oss:20b` | Its tool calling is strong but it has no vision. `look` and `pawn_check` then return images the model cannot read. |

Dense 27B to 31B models (`qwen3.6:27b`, `gemma4:31b`) are smarter per token, but they crawl when most of the model sits on the CPU. While streaming, MoE is the right shape for this box.

## Setup

1. **Update Ollama first.** The installed version is 0.16.1, which is too old for the qwen3.6 and gemma4 architectures; current is 0.35.x. The updater restarts the Ollama server, and `unity-voice.py` uses that server. Its lines fall back to plain text while the server is down, so do it between streams.
2. Pull the model. It is about 24 GB, so pull between streams; it competes with the stream upload.
   ```
   "C:/Users/gfour/AppData/Local/Programs/Ollama/ollama" pull qwen3.6:35b
   "C:/Users/gfour/AppData/Local/Programs/Ollama/ollama" pull gemma4:26b      # optional fallback
   ```
3. Optional: set `OLLAMA_MAX_LOADED_MODELS=2` so `unity-local` (used by unity-voice.py) and the autopilot model stay resident together. The autopilot speaks with `unity-speak.py` directly and does not call unity-voice, so this only matters if something else does.

## Start it

```
# try it while Claude is still playing: reads the live game (read-only tools only), executes NO action, says nothing,
# uses CPU only (num_gpu 0) so the stream keeps its VRAM
python .local/autopilot/autopilot.py --dry-run --once

# no bridge, no stream, just the model and the tool layer
python .local/autopilot/autopilot.py --offline --once

# LIVE (only when Claude has handed the stream over)
python .local/autopilot/autopilot.py
python .local/autopilot/autopilot.py --think                # slower, smarter turns
python .local/autopilot/autopilot.py --model gemma4:26b
python .local/autopilot/autopilot.py --num-gpu 8            # cap GPU layers if SD/RimWorld run short of VRAM
```
`start-autopilot.cmd` starts the live loop. Env overrides: `AUTOPILOT_MODEL`, `AUTOPILOT_NUM_CTX` (default 32768), `AUTOPILOT_THINK=1`, `AUTOPILOT_DRY_NUM_GPU`, `OLLAMA_URL`, `STUDIO_URL`.

**Owner orders** go in `.local/autopilot/owner-orders.txt`. You write it by hand and the autopilot only reads it, at the start of every turn. That file is its only channel for orders. Chat is not one.

Logs and state: `scratch/autopilot.log`, `scratch/state.json` (dry runs use `scratch/state-dry.json`, so viewers it only pretended to greet are not marked as greeted).

## The turn loop (PLAYSCRIPT order of operations)

The loop follows the owner's order of operations from the PLAYSCRIPT. Each turn:
1. Collect new chat from the studio's `GET /api/chat`.
2. Read the game (`game_state`: colonists, letters, alerts, messages, UI).
3. Every 3rd turn, run `run-list.py`.
4. Read `owner-orders.txt`.

The model then follows the playscript's six steps:
1. Greet every new chatter by name.
2. Check pawn needs and health and fix the worst.
3. Talk to chat.
4. Post an image when something happens.
5. Walk viewers through its thinking.
6. Act on the first FIX.

After that it lets time move (`play_slices`). There are up to 12 tool rounds per turn. **Backstop:** if the model skips greeting a joiner or a first-time chatter, the code greets them by name itself. An unanswered message is carried into the next turn once.

## Tools (the model's entire world)

- **Game (bridge allowlist).** Read: list_colonists, list_letters, list_alerts, list_messages, get_cells_info, get_cell_info, get_map_target_info, get_ui_state, get_ui_layout, get_camera_state, list_zones, list_areas, list_architect_categories/designators, list_main_tabs, list_inspect_tabs, get_selected_pawn_inventory_state, get_designator_state, get_game_info, find_random_cell_near. Act: select/deselect/clear selection, right_click_cell, get/execute/close context menu, set_draft, frame_pawns, jump camera, frame_cell_rect, zoom, move_camera, set_time_speed, pause_game, play_for, play_until_letter, save_game, apply/select architect designator, drag_cell, click_cell, open/close main tab, click_ui_target, open/dismiss letter, list_selected_gizmos, execute_gizmo, open_inspect_tab, close_window, press_accept, activate_alert, set_zone_target, take_screenshot.
- **Composite:** `look` (screenshot that the model sees through vision), `game_state`, `pawn_check` (Needs/Health tab plus a screenshot), `order_pawn` (api-prio.py), `play_slices` (play.py, 1 to 6 slices), `run_list`, `empire_pass` (empire.py, optional `--dry`).
- **Stream:** `say` (outbox, Piper voice and an auto glance image), `reply_chat` (outbox reply row and voice, with the viewer's name), `webcam` (unity-cam.py mood and caption), `snap` (unity-snap.py annotated rect).
- **Knowledge / notes:** `read_doc` (read-only: docs/, src/, Mod/, About/, README, CHANGELOG, its own folder) and `note` (write **only** inside `scratch/`).

## Hard guards (guards.py, enforced in code under the model)

- **No shell tool and no generic file-write tool. Nothing can build, compile, stage, commit or push.** The only write path is `note` into `scratch/`: plain relative names, `.md/.txt/.json/.jsonl/.log`, at most 64 KB, realpath-checked. The scripts it may run are a fixed list of absolute paths, launched with `shell=False` and typed arguments.
- **Bridge allowlist plus a deny pattern.** Lua, scripts, debug actions, DPA, mod settings, mod enable/reorder, load game, main menu, spawn, god mode and language can never be called. That holds even if someone widens the allowlist later.
- `click_ui_target` only clicks a target id taken from the last `get_ui_layout`. It refuses mods, dev mode, debug, quit, load, delete, overwrite, options, abandon/banish/execute-prisoner. Context-menu labels get the same filter.
- **Saves** are forced to `rimbridge_save_<name>`.
- `play_for` drops `ticks` and is capped at 30 s.
- `list_selected_gizmos` is rate-limited to once every 20 s. The game once crashed when gizmos were listed over and over.
- **THE STREAM IS CLEAN:** every spoken line, chat reply, webcam caption and snap note goes through `clean_for_stream`. That function applies unity-voice.py's own SOFTEN and CLEAN_BLOCK rules, blocks extra degrading words, and strips emoji, stage directions, URLs, file paths, filenames and hashtags. It also replaces secret words (`secret-words.txt`, which holds the owner's Twitch handle and which the model cannot read). A line that is still dirty is dropped, never spoken. There is also a 3 s minimum gap between lines.
- **Chat only drives the game.** Chat goes into the prompt as quoted viewer data. More importantly, the tool layer has nothing that can touch files, code, accounts or the web, so a chat message cannot cause any of that even if the model obeyed it.
- **Dry-run** executes only read-only bridge tools. Every action, line, image and script is logged as `DRY-RUN would ...`. `look` reuses the last saved `.local/qa/_w.png` rather than taking a new screenshot.

## What it cannot do yet

- It has not been run against `qwen3.6:35b`; the model is not pulled yet. Tool-call quality and turn latency on CPU offload are unmeasured. Expect roughly 10 to 30 s per model step.
- It does not read needs and health as numbers. `list_colonists` has no needs or health fields, so `pawn_check` relies on vision reading the Needs or Health tab.
- There are no raw clicks or keys (eyes.py, hands.py, keys.py are deliberately not wrapped; the owner said not to fight for the mouse). Anything that needs typing into a text field (bill counts, renames) is out of reach.
- There is no designate-cells.py, work-set.py, gizmo.py or dismiss.py wrapper yet. It uses the raw bridge equivalents, which are slower and easier to get wrong (for example, the one-cell work-tab rule).
- It does not close TEST rows or touch docs/TODO or FINALIZED. It is not supposed to, because that is workflow, not play.
- The memory between turns is a short rolling summary, so long plans can drift. It re-reads `docs/NOW.md` and `PLAYSCRIPT.md` through `read_doc` when needed.
- It does not start the stream stack itself. Run `Unity Plays RimWorld.cmd` first, which starts the studio, the face server, SD, the Twitch bridge and the overlay.

## Scope (owner, 2026-10-09, verbatim)

> "the opern source version on handles the steam requirememnts and the rimworld play it doesnt code in our mod or on the computer"

Stream requirements and RimWorld play only. No coding in the mod or anywhere on the computer: no shell tool, no file writes outside `scratch/`.

## GPU budget while the stream is live (measured 2026-10-09)

Do not offload the big model onto the card during a stream. Measured on this box, 16 GB card:

| State | VRAM free |
|---|---|
| RimWorld + OBS + SD, `dolphin3:8b` at its default 131072 context | **1.0 GB** -- the context window alone was holding 14.7 GB |
| same, `dolphin3:8b` capped at `num_ctx` 4096 | **13.3 GB** (the model loads at 5.27 GB instead of 23 GB) |
| same, plus `qwen3.6:35b --num-gpu 14` | **0.3 GB** -- the game and the encoder are then fighting for nothing |

So the shape that works: **the small model talks, the big model thinks.** `dolphin3:8b` (capped context) carries
greetings and replies, where a second of latency is the whole product. `qwen3.6:35b` runs the play decisions on
CPU (`--num-gpu 0`) at a slower cadence -- one turn took 223 s that way, which is fine for *what do we do next*
and useless for *say hi back*. Offload the big model only when the stream is down.

**Corrected 2026-10-09, measured live:** the 200-odd second figure is the **cold** step -- loading 22 GB off
disk and filling the context. Once warm, steps run **18 to 56 s** (observed: 55.9, 22.0, 30.6, 21.9, 18.4).
That is usable for play decisions on CPU, so the earlier "unusable" read was wrong: it was one cold start,
not the steady state. Chat still belongs to the small model, where even 20 s is too slow for a greeting.

