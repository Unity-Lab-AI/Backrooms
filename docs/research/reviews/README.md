# Source review records

Save detailed source observations here so future design and implementation work can follow the evidence without relying on chat history.

## File layout

- `kane-pixels/<video_id>.md` — one linked note per official playlist upload. Some files are short pending-review placeholders, not completed research. Use [`templates/kane-video-review-template.md`](templates/kane-video-review-template.md) when adding observations.
- `a24-feature/feature-review.md` — complete feature review. Use [`templates/a24-feature-review-template.md`](templates/a24-feature-review-template.md).
- `mods/<workshop_id>-<package_id>.md` — one exact mod-page/source review per Workshop mod. Use [`templates/mod-review-template.md`](templates/mod-review-template.md).
- `rwt/` — pinned-build source inspection and disposable-profile behavior records; do not mark runtime behavior complete without the exact server/client/game/DLC/profile identifiers.

Keep a placeholder for every indexed source so each map and index entry has a stable path. Update [`../kane-pixels-video-index.csv`](../kane-pixels-video-index.csv) or the 294-row workbook only when its status accurately reflects the linked evidence. A source-page review, installed-file inspection, and in-game runtime test are different evidence levels. If a video is only sampled, say so in both the review and index; do not mark the complete review done. Never present viewer comments, search snippets, or a partial sample as canon or a full-source review.

## Required review fields

1. Exact source URL and title/name; local Workshop/package ID where applicable.
2. Date reviewed and the version/build visible at that time.
3. What was directly observed, including timestamps or page sections where possible.
4. What is uncertain, inaccessible, inferred, or not covered by the source.
5. A separate original RimWorld gameplay translation and the design document it informs.
6. Compatibility/runtime result only when actually reproduced, with game build, DLC, load order, RWT versions, save, logs, and observed behavior.
