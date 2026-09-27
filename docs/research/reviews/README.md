# Source review records

Save readable source notes here so design and implementation work can follow the evidence without relying on chat history. Creative-reference notes should stay focused on story and useful inspiration, not become shot-by-shot technical logs. Mod/API and runtime notes should include the technical detail needed to reproduce a compatibility claim.

## File layout

- `kane-pixels/<video_id>.md` — one linked note per official playlist upload. Some files are short pending-review placeholders, not completed research. Use [`templates/kane-video-review-template.md`](templates/kane-video-review-template.md) when adding observations.
- `a24-feature/feature-review.md` — complete feature review. Use [`templates/a24-feature-review-template.md`](templates/a24-feature-review-template.md).
- `mods/<workshop_id>-<package_id>.md` — one exact mod-page/source review per Workshop mod. Use [`templates/mod-review-template.md`](templates/mod-review-template.md).
- `rwt/` — pinned-build source inspection and disposable-profile behavior records; do not mark runtime behavior complete without the exact server/client/game/DLC/profile identifiers.

Keep a placeholder for every indexed source so each map and index entry has a stable path. Update [`../kane-pixels-video-index.csv`](../kane-pixels-video-index.csv) or the 294-row workbook only when its status accurately reflects the linked evidence. A source-page review, installed-file inspection, and in-game runtime test are different evidence levels. If a video is only sampled, say so in both the review and index; do not mark the complete review done. Never present viewer comments, search snippets, or a partial sample as canon or a full-source review.

## Required review fields

1. Exact source URL and title/name; local Workshop/package ID where applicable.
2. Date reviewed and the version/build when it matters.
3. What was directly observed; add a timestamp or page section only when it helps locate an important detail.
4. What is uncertain, inaccessible, inferred, or not covered by the source.
5. A separate original RimWorld gameplay translation and the design document it informs.
6. Compatibility/runtime results only when actually reproduced. For mod tests, record the game build, DLC, load order, RWT versions, save, logs, and observed behavior.
