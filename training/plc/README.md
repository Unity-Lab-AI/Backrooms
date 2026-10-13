# training/plc: teaching Unity to use her PLC (RimPLC ladder)

Owner: "they all are getting traing on how to use the PLC". Before this set, the brain data had 8 `ladder` calls in
7,201 rows. `plc.jsonl` adds **692 episodes** (kind `"play"`), with **1,026 `ladder` calls** and **756 `ladder_set`
calls** (610 mark, 77 tag, 63 add_rung, 6 remove_rung). These rows are not merged into `training/data/brain/` yet.

## Files

| File | What it is |
|---|---|
| `plc.jsonl` | The episodes. LF line endings, one JSON row per line: `tools: "TOOLS"`, `kind: "play"`, `meta` (category, family, chain, explore_done, marks), `messages`. |
| `build_plc.py` | The builder: every scenario generator, the registry (counts per family and chain), and `main()`. |
| `plc_engine.py` | The engine: measured states, genuine ladder output, `ladder_set` results, the episode writer, and tool-result helpers. |

Rebuild with `python training/plc/build_plc.py`. It takes about 3 minutes, and the output is deterministic because the
seeds are fixed. The build reads the repo and writes only `training/plc/plc.jsonl`. It never touches the game, a Mods
folder or a bridge.

## Why the tool results are genuine

- **`ladder`.** Each scenario is a measured-state dict that uses the keys `gates.derive()` writes. Its base comes from
  `derive()` run over the captured `.local/qa` replies (`gi`, `letters`, `cols`, `zones`, and 5,020 captured cells).
  The scenario then overrides values on top of that base. The state goes through
  `gates.decide(every=True, write=False)` against `docs/playbook.gates.json`. The result is formatted exactly as
  `tools.py t_ladder` formats it: `live_rungs` (top 4, with `matched` and `then`), `tags`, `my_marks`, `my_rungs`,
  `unknown_keys`, cut at 5,000 characters. Every generator **asserts that the rung it is written for really is the
  first live rung**. If a random state lights a different rung, the scenario is drawn again.
- **`ladder_set`.** Results are what `t_ladder_set` returns:
  - `ladder updated: ...`
  - `REFUSED BY GUARD: X is a constant: a safety limit only the owner changes`
  - `... is not a variable on the ladder`
  - the clamp note
  - the `unity-` id prefix on added rungs
  - the unsensed-key note on `add_rung`
- **Other tools** use the formats in `train.jsonl` and in the source:
  - `game_set` results come through the inbox, and `add_bill` uses the current `... at X,Z now has <label> until N`.
  - `say` / `reply_chat` / `reply_owner` / `webcam` match `tools.py`.
  - `play_slices` uses `done N slices, tick T`.
  - Bridge tools return `{"success": true, ...}`.

## Families and chains (rows)

| Family / chain | Rows | Scenarios |
|---|---|---|
| combat chain | 119 | walk-fight 21 (damage pause, then fight, then hold, then reset, over 3 turns); fight 12, help-coming 12, call-help-comms 12, call-help-permit 12, retreat 12, kite 12; reassess (worse/better) 14; reset 12 |
| medical chain | 40 | walk 18 (bleeding under fire, then combat reset, then field tend, then carry to hospital, over 3 turns); field-tend 12; carry 10 |
| repairs chain | 30 | wait 10 (`raid-posted` on top, `repair-1-wait` under it, nobody repairs under fire); set 12; reset 8 |
| defense chain | 44 | embrasures 12, turrets 12 (including the steel-short branch), secure 10, reset 10 (embrasures, turrets or damage) |
| supply chain | 69 | food-low 10, steel-buy 8, steel-mine 8, podfuel 7, shipfuel 7 (late game, gravship), weapons-sell 7, weapons-smelt 7, plus resets: food 4, steel 4, podfuel 3, weapons 4 |
| A read | 121 | hostile-on-map then raid-posted 16; downed 8; pawn-starving 8; starving 7; food-low 7; fire 6; mental-break 5; cold 5; disease 5; raid-cleanup 5; food-rotting 5; start-tribal 7; start-naked 4; start-crashlanded 4; tame-mounts 5; throne-room 4; letters 10; grav-core 5; anomaly-entity 5 |
| B act and close | 43 | rung-2 latch closed on measured outcomes 8; grav-ready (`gravship_ready`) 8; bestowing (numeric marks `title_rank` and `psylink_level`) 7; grav core received 6; research complete 8; war-prep 6 |
| C missing key | 40 | camera-away 18 (camera off home, so only `always` is live; she jumps home and rescans, and the real rung appears); unsensed rung 12 (`add_rung` note, then rewritten on a measured key); preparing raid 10 (`hostiles_on_map` 0, chat says draft, she does not draft) |
| D edit a setpoint | 69 | owner `OWNER:` requests 22 (including over-max values with the clamp reported back); embrasure target 7; her own judgement 40 (turrets after sieges, meal bill, winter food, fight ratio up and down, steel for the ship, weapons for recruits, medicine for war, grav parts, silver floor) |
| E write a rung | 45 | manhunters 6, solar flare 5, toxic fallout 5, infestation 5, eclipse 4, mech cluster 4, trader 5, mount gizmo 5 (each rung added, then a rescan shows it live); remove-own 6 |
| F refuse a bad edit | 52 | chat 28 (constants, book rungs, mod edits, unclean rungs); owner asks to change a constant 8 (tool refuses, so she tells the owner it is CLI only); unknown tag name 8 (checks the tags and asks); chat pushes a variable to an extreme 8 (declined with numbers) |
| chat-status | 20 | Chat asks what she is doing, and she answers from the live rung in one clean line. About 30% of the other episodes also carry chat. |

Each control chain is also walked across rows. One row ends with a `ladder_set mark`, and another row starts from that
mark as its input: the defense rows go embrasures, then turrets, then secure, then reset; the supply rows go from the
low alarm to the reset.

## Validation (last build)

- 692 rows. `check_player.check_episode` against `training/data/brain/tools.json`, with the owner's secret words
  loaded: **0 failing**.
- Every tool call is in `tools.json` and its arguments validate against the schema.
- Every spoken line (`say` / `reply_chat`) and every narration passes `check_player.dirty`.
- 827 spoken lines, **all distinct**.
- No secret word anywhere in the file, and no stale habit lines.
- Narrations: 2,966 total, 1,848 distinct. Every narration over 60 characters and every spoken line is unique across
  the file. The ones that repeat are short connectives such as "Read it back." (77) and "Rescan." (33).
- Turn-opening think lines: 531 distinct out of 770.

## Things to know

- **The `no-medicine` rung (priority 8) cannot appear in training data.** Its book `then` text contains a word on the
  owner's secret-word list (step 2, "...rather than hunting f-r-v-r"), and `check_brain` scans every data file for those
  words. The engine redraws any state that would show that rung, so there are no no-medicine episodes. Rewording that
  step in `docs/playbook.gates.json` ("...rather than searching endlessly") would let it in. That is the owner's call;
  it was not changed here.
- **`starving-no-game` (4.01) can never be the top rung.** `starving` (4.0) has only `alert_starv: true` as its
  condition, so it always wins first.
- **Unverified formats used:**
  - `game_jump_camera_to_cell` → `{"success": true, "x", "z"}` (no captured reply).
  - `order_pawn` → `ok: <pawnId> -> <option> (x,z)` for the options `Tend` / `Rescue` / `Call`.
  - Alert labels follow `ALERT_MATCH` substrings: "Colonist bleeding", "Life-threatening condition", "Colonist needs
    treatment", "Starvation", "Hypothermia", "Sick colonist: ...". `ALERT_MATCH` itself is UNVERIFIED in `gates.py`.
- Comms and permit help is called with `order_pawn ... option "Call"` on the console, and the trade itself is left to the
  dialog. The chains are advise-only, so the episode latches the mark right after the call.
- The user turn mirrors `autopilot.brief()` without the THE LIVE RUNG block, because she reads the ladder herself here.
  That block is: UPDATE header, optional OWNER and CHAT blocks, GAME STATE in the `t_state` shape, and TURN line. The
  system prompt is copied verbatim from a `train.jsonl` play row.
