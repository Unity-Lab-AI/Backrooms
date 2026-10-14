# RimPLC branding artwork — 2026-10-12

Owner request: "and we need some proper RimPLC images mad for it not menu and load screens tho"

## Delivered artwork

| Image | Master | Installed package path | Use |
|---|---|---|---|
| Wide preview, 1672 × 941 RGB | `RimPLC_Preview.png` | `RimPLC/About/Preview.png` | RimWorld/RimSort mod preview and README/wiki branding |
| Square badge, 1254 × 1254 RGBA | `RimPLC_Badge.png` | `RimPLC/About/RimPLC_Badge.png` | Transparent reusable branding; no current in-game icon consumer |

Both are original cream/brass ladder-circuit illustrations on the charcoal industrial identity.
The preview reads `RimPLC`, `COLONY LOGIC & CONTROL`, `RIMWORLD 1.7`, and `Operator`.
It carries no development release number. The colony/sensor artwork is illustrative, not a gameplay screenshot.

`provenance.json` contains the exact built-in image-generation prompts and original output paths.
`delivery.json` records dimensions, modes, alpha observations, bytes and SHA256 hashes.
Package copies are byte-identical to these masters; no image editing or resampling was performed.

## Integration and review

- Visual inspection confirmed the requested title, version label and styling.
- Badge alpha spans 0–255 and all four corners are transparent.
- Both images are explicit required entries in `tools/export-rimplc-repo.py` and the RimPLC package manifests.
- The workspace and generated standalone README show the preview and link the badge.
- RimPLC's own wiki (`RimPLC/docs/wiki/`, published at https://g-fourteen.github.io/RimPLC/) uses the preview as its cover; the page that lived in the Rimrooms wiki was removed on 2026-10-13.
- The local standalone export contains 35 files, including both artwork files.
- Original mod release remains 0.1.0. Source, compiled DLLs, MainButtonDef and gameplay behavior are unchanged.
- No menu/load art, game launch/staging, profile changes, training or pod work occurs in this task.

This artwork completes the bounded branding request. RimWorld 1.7 runtime acceptance remains
separate from the promotional image's target label. Publication receipts belong in tool output
and the bounded appended handoff in `docs/NOW.md`.
