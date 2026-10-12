# tools-coverage -- every tool Unity has, used in real play

Brain training rows (kind `play`) that use the tools `training/data/brain/train.jsonl` never used or barely used.
Owner's ask: train on "rimworld game paly, how to play, ... the tools, the everything ... it should be the whole show".

Rebuild: `python training/tools-coverage/gen_tools_coverage.py` (seeded, so the output is the same each run). It reads only
repo files and writes only into this folder. It does not touch the game, the Mods folder, or any build.

## Files

| File | Rows | Validation |
|---|---|---|
| `tools.jsonl` | 568 | `check_player.check_episode` against `data/brain/tools.json`, the same way `check_brain.py` runs it: **0 failing** |
| `tools_clicks.jsonl` | 60 | every rule except the UI-click ban: **0 failing**. Kept out of the main file on purpose, see below |
| `counts.json` | | per-tool call counts and categories |
| `gen_tools_coverage.py` | | the generator |

`python training/check_player.py training/tools-coverage/tools.jsonl` checks against the older `data/tools.json`, which has no `reply_owner`, so the rows that use it fail there. Check against the brain tool list instead, the way `check_brain.py` does.

## Where the content comes from

- The system prompt is copied word for word from the first `play` row of `data/brain/train.jsonl`. User turns use the same UPDATE, MEASURED STATE, OWNER, CHAT and TURN blocks.
- Local tool results (`look`, `game_state`, `pawn_check`, `run_list`, `empire_pass`, `new_colony` and its refusal, `plan`, `reply_owner`, `note`, `say`, `webcam`, `play_slices`, `game_set`) use the exact text that `.local/autopilot/tools.py`, `run-list.py` and `empire.py` produce.
- `read_doc` results are the real lines of `docs/wiki/*.md` and `docs/PLAYSCRIPT.md`, numbered the way the live tool numbers them. Each answer she gives repeats only what those lines say: gate control on both table and console, 100 steel and 8 components, Intellectual 4, door widths, the reserve, four stations, the 85% sale, the colony limit, freezer rules, and Esc opening the pause menu.
- Every designator and category id is a real one captured from the live game (`.local/qa/*.json`). Letter, zone, colonist and context-menu result shapes follow the captured bridge JSON. Alert, gizmo, time-speed, close-window and press-accept results use the field names found in the RimBridgeServer 2.1.1 assembly (`alertId`, `selection-gizmo:`, `Time speed set to {0}.`, `closedWindowTypes`).
- Vanilla facts used: alert labels, Make_Apparel_Parka, CookMealSimple, plant defs, leader abilities (Combat command, Work drive), the moral guide's Counsel, and Fire at will.
- Not modelled on purpose: `ladder` and `ladder_set` (another agent covers those in training/plc/).

## Why the mouse tools live in a separate file

`check_player.py` rejects `game_right_click_cell`, `game_drag_cell`, `game_get_context_menu_options` and `game_execute_context_menu_option` in every episode ("UI click where game_set does it in one call"). That rule cannot be met by any row that uses those tools, so they are in `tools_clicks.jsonl` (rescue, prioritize tending, prioritize hauling, hand-dragged areas). That file passes every other rule. It only goes into training if the owner lifts the click rule for these cases. Merging it as it stands would make `check_brain.py` fail.

## Per-tool counts (tool calls in tools.jsonl)

| Tool | Calls | Target? |
|---|---|---|
| `say` | 560 |  |
| `game_set` | 224 |  |
| `game_apply_architect_designator` | 147 |  |
| `reply_chat` | 105 |  |
| `game_set_draft` | 97 |  |
| `pawn_check` | 91 | yes |
| `game_jump_camera_to_cell` | 84 | yes |
| `read_doc` | 78 | yes |
| `play_slices` | 77 |  |
| `game_set_time_speed` | 75 | yes |
| `game_select_architect_designator` | 73 | yes |
| `game_list_architect_designators` | 70 |  |
| `game_select_pawn` | 64 | yes |
| `game_state` | 64 | yes |
| `empire_pass` | 63 | yes |
| `game_open_letter` | 61 |  |
| `note` | 60 |  |
| `game_dismiss_letter` | 51 |  |
| `game_list_alerts` | 50 | yes |
| `game_list_colonists` | 42 | yes |
| `look` | 42 | yes |
| `game_set_zone_target` | 37 | yes |
| `game_take_screenshot` | 37 | yes |
| `game_list_architect_categories` | 35 | yes |
| `webcam` | 35 |  |
| `game_close_window` | 34 | yes |
| `game_list_zones` | 34 | yes |
| `reply_owner` | 31 |  |
| `game_execute_gizmo` | 30 | yes |
| `game_list_letters` | 30 | yes |
| `game_list_selected_gizmos` | 30 | yes |
| `game_list_areas` | 28 | yes |
| `run_list` | 28 | yes |
| `new_colony` | 25 | yes |
| `plan` | 22 | yes |
| `twitch_chat` | 22 |  |
| `game_press_accept` | 20 | yes |
| `snap` | 3 |  |

## Per-tool counts (tools_clicks.jsonl)

| Tool | Calls |
|---|---|
| `say` | 60 |
| `game_execute_context_menu_option` | 37 |
| `game_get_context_menu_options` | 37 |
| `game_right_click_cell` | 37 |
| `game_select_pawn` | 37 |
| `game_drag_cell` | 23 |

## Categories

| Category | Rows |
|---|---|
| fresh.game_state | 50 |
| mid.alerts | 50 |
| build.architect | 45 |
| mid.dialog | 44 |
| mid.read_doc | 34 |
| build.zones | 30 |
| mid.gizmos | 30 |
| mid.letters | 30 |
| maint.empire_pass | 28 |
| maint.run_list | 28 |
| mid.areas | 28 |
| mid.colonists | 24 |
| mid.time_speed | 24 |
| big.plan | 22 |
| build.read_doc | 22 |
| owner.new_colony | 22 |
| stream.select | 22 |
| stream.camera | 16 |
| stream.camera_event | 16 |
| owner.new_colony_refused | 3 |

The three `owner.new_colony_refused` rows are weight-0 mistakes: she calls `new_colony` because a viewer pushed for it, the guard refuses with no owner grant, and her next step corrects course. That is the only pattern `check_player` accepts for teaching a refusal.
