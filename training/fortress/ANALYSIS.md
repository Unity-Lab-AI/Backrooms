# Fortress / embrasure distillation: analysis

Owner, verbatim: *"we are training it how you played the game earlier in the week when you buiilt the fortress with the empbrasure rooms all around it... u had great planing and editing skills in designing the base and took instruction well building it into future action emenslly well... i know it wont be as good but we are shooting for close"*.

Source: Claude Code session `~/.claude/projects/C--Users-gfour-Desktop-Backrooms/372a4068-59cd-43c2-a79d-e04a8fcf9cb0.jsonl` (94,982 lines, 1.2 GB). It was streamed with Python, and line numbers are 0-based JSONL indexes.

## 1. Where the fortress work is

There are 222 lines matching `embrasure|fortress|killbox`, in 14 clusters. The core build is one continuous run on 2026-10-10 (UTC):

| Lines | Time | Content |
|---|---|---|
| 67711–67850 | 00:37–00:50 | Owner mountain-cutout order. Unity scans the rock and draws the fortress in 8 plan-designator rects. The NE pocket becomes soil |
| 68160–68260 | ~01:00 | Mining starts on the door, entry and a 19x13 throne room (247 cells). A 2-cell rock-margin check is made on all 13 rooms. Mining is cancelled for food first, and the plan markers are kept |
| 68309–68445 | ~01:05–01:20 | Owner: wood wall plus a 3-wide marble firebreak. This becomes a 114-cell ring with 2 gates, then the whole ring is swapped to embrasures and doors are added |
| 68559–68700 | ~01:20–01:40 | Owner layout rules, and a corner correction: doors moved 2 cells in from the corners |
| 68900–69200 | ~01:45–02:05 | First raid held at the wall. Prison cell built in the SE corner |
| 69381–70250 | 02:05–03:00 | Soil inside the walls, farms moved outside, rec room, coolers, lamps, kitchen, graves and dump. The foreman hands out embrasure builds. A pawn gets trapped by her own wall |
| 72380–72500 | ~03:30 | Owner: "why u putting walls up against and replacing embrasures". Unity cancels her walls on x168, restores the embrasures and gate, and verifies the column |

Earlier clusters (design talk and raid positioning) are at 15731–16327, 41150–41322, 56844–57490 and 59805–61778.

## 2. How the game was driven, and the mapping to the brain's tools

There are no `mcp__rimbridge__*` calls. All 760 game actions are Bash calls: `bridge.py call rimworld/<method>` (386) plus helper scripts. The main mappings:

| Session call | Count | Brain tool |
|---|---|---|
| apply_architect_designator | 96 | `game_apply_architect_designator` |
| get_cells_info | 109 | `game_get_cells_info` |
| list_colonists | 146 | `game_list_colonists` |
| list_letters / dismiss_letter | 53 / 6 | `game_list_letters` / `game_dismiss_letter` |
| get_game_info | 52 | `game_state` |
| jump_camera_to_cell | 48 | `game_jump_camera_to_cell` |
| list_architect_designators | 45 | same |
| list_alerts | 33 | `game_list_alerts` |
| right_click / context menu | 76 | `order_pawn` / `game_*` equivalents |
| list_selected_gizmos / execute_gizmo | 24 / 5 | same |
| set_time_speed / set_draft / pause_game | 37 | same |
| unity-say.py | 69 | `say` |
| unity-snap.py / shot.py | — | `snap` / `look` |
| api-prio.py / set-priorities.py | — | `order_pawn` / `pawn_priorities` |
| run-list.py / play.py | — | `run_list` / `play_slices` |

**Plumbing to drop:** `select_pawn` (205) and `clear_selection` (81).

**No brain equivalent (excluded):**
- UI and mouse calls (`click_cell`, `click_ui_target`, `get_ui_*`, `open_*tab`, `press_cancel`; about 150).
- `delete_zone`, shift-queued builds, and real-mouse gizmo jobs (`cursor-jobs.py`, `real-click.py`).
- Orchestration (services, stream-host, autopilot, foreman, guards).
- Git and docs work.

Bash loops that placed many rects are expanded into one designator call per rect.

**Designator ids differ between sessions** (`structure:build-vin-embrasure` here, `security:` in the existing rows). Episodes teach looking the id up with `game_list_architect_designators` when unsure.

## 3. Planning and owner orders

**Planning:**
- Assistant text with coordinates and sizes, plus rock-margin checks.
- Before-and-after ASCII cell columns.
- The plan designator drawn in-game before digging.
- Owner rules written down as standing rules.

In the brain this becomes `plan` for big layouts, the plan designator via `game_apply_architect_designator`, `note` for standing rules, and `snap` with marks.

**Owner orders** are short and misspelled, and buried among hundreds of cron prompts. The loop:
1. Restate the order.
2. Find the designator.
3. Place it rect by rect.
4. Check with `game_get_cells_info`.
5. Save it as a rule.
6. Tell chat.

**Corrections are the most valuable episodes:** corner doors, and walls built over embrasures.

## 4. Hazards

- **Rough owner language:** owner messages are rough. Rewrite them as a clean `OWNER:` line, and never let it reach `say`. Unity's own assistant text in the window is clean (1 of 305 blocks has profanity). Spoken lines are trimmed to 1–3 sentences.
- **Secrets:** the owner's handle is not in the window, but words from the secret list appear in many lines (mostly short common words). Every row goes through the filter (`owner.txt`, `secret-words.txt`). Viewer names are anonymised.
- **Screenshots:** about 1,140 screenshot lines in the file. Replace them with `look`/`snap` result strings.
- **Failures:**
  - 24 flagged errors, plus unflagged failures (marsh rejections, missed hunt marks, a modal blocking clicks, the wrong map, walls over embrasures).
  - Keep short fail-and-fix chains; drop bridge plumbing failures.
- **Long context:** compaction summaries, KB-sized heredocs, dumps and safety-classifier interruptions (70646–70976). Rebuild each episode from a short state header.
- **Off-topic work:** 70580–74300 is mostly autopilot, stream-host and LoRA engineering, and is excluded.

## 5. Conversion recipe and yield

- **Segmenting:** split on real owner messages and game events. An episode runs from the order or event to the done line.
- **Message mapping:**
  - **system:** the standard play system prompt, verbatim.
  - **user:** `UPDATE (turn N)` + `OWNER: "<clean paraphrase>"` or `ALERT:` + a compact state block.
  - **assistant:** a short reason + one brain tool call.
  - **tool:** the trimmed real result.
  - **Tail:** `note` for standing rules, a clean `say`, and a next-step line.
- **Checks:** validator, secret and profanity filter, and tool name/argument check against `training/data/brain/tools.json`.
- **Yield:** about 25–30 orders or events in the core window plus 10–15 from earlier clusters gives about 35–45 episodes. With 3–5 coordinate variants each, that is about 150–200 rows. They are mixed into the play set, not trained alone.

## Samples

`samples.jsonl` holds 5 episodes, kind `fortress`: the embrasure ring, the corner-door correction, the mountain plan, the walls-over-embrasures repair, and raid positioning. Every tool call is checked against `tools.json`.

What is not real in them:
- Pawn ids in episode 5 are made up, except Scar's `Thing_Human1089`.
- All tool results are hand-written.
- The samples were built by a helper script (`%TEMP%\fortgen\fortgen.py`), so they need a careful human read before the full conversion follows the same recipe.
