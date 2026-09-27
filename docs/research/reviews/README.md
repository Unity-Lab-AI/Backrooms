# Source review records

Save readable source notes here so design and implementation work can follow the evidence without relying on chat history. Creative-reference notes should stay focused on story and useful inspiration, not become shot-by-shot technical logs. Fan-written summaries are approved first-pass sources for the Kane series and A24 feature; label them as secondary and keep fan interpretations separate from confirmed story details. Mod/API and runtime notes should include only the technical detail needed to reproduce a compatibility claim.

## File layout

- `kane-pixels/<video_id>.md` — one linked direct-source review record per official playlist upload. Some files are partial or pending direct review. The separate [`../KANE_PIXELS_FAN_CLIFF_NOTES.md`](../KANE_PIXELS_FAN_CLIFF_NOTES.md) contains first-pass fan story summaries for all 23 entries; it does not turn a pending direct review into a completed viewing.
- `a24-feature/feature-review.md` — first-pass feature story note, currently based on a fan summary rather than direct viewing. Use [`templates/a24-feature-review-template.md`](templates/a24-feature-review-template.md) for later updates.
- `mods/<workshop_id>-<package_id>.md` — one exact mod-page/source review per Workshop mod. Use [`templates/mod-review-template.md`](templates/mod-review-template.md).
- `rwt/` — pinned-build source inspection and disposable-profile behavior records; do not mark runtime behavior complete without the exact server/client/game/DLC/profile identifiers.

Keep a placeholder for every indexed source so each map and index entry has a stable path. Update [`../kane-pixels-video-index.csv`](../kane-pixels-video-index.csv) or the 294-row workbook only when its status accurately reflects the linked evidence. A source-page review, fan summary, direct viewing, installed-file inspection, and in-game runtime test are different evidence levels. If a video is only sampled, say so in both the review and index. Never present viewer comments, search snippets, or a partial sample as canon or a direct-source review. A fan summary can support a short story note when clearly labeled, but do not upgrade it to a direct-source review.

## Required review fields

1. Exact source URL and title/name; local Workshop/package ID where applicable.
2. Date reviewed and the version/build when it matters.
3. What was directly observed; add a timestamp or page section only when it helps locate an important detail.
4. What is uncertain, inaccessible, inferred, or not covered by the source.
5. A separate original RimWorld gameplay translation and the design document it informs.
6. Compatibility/runtime results only when actually reproduced. For mod tests, record the game build, DLC, load order, RWT versions, save, logs, and observed behavior.

For creative references, state the method as **fan summary**, **official page**, or **direct viewing**. A fan summary or official synopsis is not a direct viewing; mark uncertain details as pending instead of filling gaps by inference.
