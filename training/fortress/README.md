# Fortress training episodes

These are brain training episodes taken from the owner's fortress session on 2026-10-10. Unity planned a mountain fortress, built an embrasure camp ring and took owner orders and corrections into the build. The recipe is in `ANALYSIS.md`.

## Files

| File | What |
|---|---|
| `fortress.jsonl` | 193 rows, kind `fortress`: 47 episodes, each with 4 coordinate-shifted variants. The 5 sample episodes get a fifth variant. |
| `samples.jsonl` | The 5 reviewed samples (variant 0 of episodes 1–5 below), with coordinates corrected to the real camp ring. |
| `build_fortress.py` | The generator and validator. It writes both files. |
| `ANALYSIS.md` | Where the work is in the session, the tool mapping, the hazards and the recipe. |

## Episodes

Every episode starts from a real owner order or game event. Its source transcript lines are in `meta.source_lines`.

**Core camp and fortress window (lines 67711–72500):**
- Mountain plan v1, v2 (throne room first) and v3 (2-cell rock margin).
- Food before digging.
- North-east farmland.
- Wood wall and marble firebreak.
- Leaving the gate room alone.
- Embrasure ring, side doors and corner-door correction.
- Fridge and workshop, then layout rules.
- Raid found in the letter backlog; field-tending and capture.
- Rock outcrop; prison swap; finishing the prison in a hurry; prisoner lost.
- Heat and coolers.
- Farm plots and the merged-field correction.
- Marsh terraforming; rec room and farms outside; cool workshop.
- Horseshoes against a wall; ordered build priorities.
- Unity trapped; wall lamps; work priorities.
- Table into the rec room; 6x6 fields and far sowing off.
- Walls over embrasures (repair); no material on site; raid still preparing.

**Earlier clusters:**
- Barricades, perimeter and killbox.
- Walls on water; roofs and generators outside.
- Bastions built outward with rows of 5.
- Holes and unpowered embrasures; trade beacons.
- Corner-tower raid and rebuild; tower lights.
- Answering chat first.

## Mapping and what is not real

- Bash bridge calls are rewritten as brain tools, one call per rect.
- Mouse-only steps (bed owner, storage filter, crop, work priority, bills) become `game_set` and `pawn_priorities`, which the brain has.
- Coordinates, designator ids, cell counts and pawn names come from the session.
- Tool results are short summaries of the real output. Some rect splits and per-plot counts that the session only gave as totals are reconstructed so that they add up.
- Pawn ids, except Scar's (`Thing_Human1089`) and Lloga's (`Thing_Human1080`), are placeholders.
- Viewer names are anonymised. The owner's words are rewritten as clean `OWNER:` lines.
- Variants shift every coordinate by (dx,dz): (-14,8), (19,-11) and (-27,-19), plus (33,6) for the samples. Turn numbers also change.

## Corrections made to the samples

- **Sample 2 (corner doors).** The real ring runs x137–168, not x138–168. The corners are (137,127), (168,127), (137,154) and (168,154). The doors went to (139,127) south-west, (166,127) south-east and (139,154) north-west, each two cells in from its corner. The north gate at (165,154) serves the north-east corner. The rule text now says exactly that (session lines 68680–68698).
- **Sample 1 (ring).** Moved to x137 with the real cell counts: 32+26+28+3+17+8 = 114 cells. It now looks up the embrasure id first.
- **Sample 4 (walls over embrasures).** It now matches the real repair:
  - 6 blueprints cancelled at x168, z139–147.
  - Built wall deconstructed at x168, z140–146.
  - (167,146) and the x138 lane behind the west embrasures cleared.
  - The column read again to verify.
- Spoken lines say "firing slits", because the stream filter blocks the word "port".

## Rebuild and check

```
python training/fortress/build_fortress.py      # writes samples.jsonl + fortress.jsonl, validates every row
python training/check_player.py training/fortress/fortress.jsonl
```

The generator checks:
- tool names and arguments against both `training/data/tools.json` and `training/data/brain/tools.json`;
- `check_player.check_episode`, including the secret words from `.local/autopilot/secret-words.txt` and `.local/tw/owner.txt`;
- the stream filter on all narration and spoken lines;
- 1–3 sentences, with emotion and act, on every `say`;
- coordinates inside the 300x300 map.

It exits non-zero if any row fails.
