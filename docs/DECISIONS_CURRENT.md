# Current owner decisions — the index

**What this file is.** A short list of the owner decisions that are in force *now*, each linked to the
record that holds the owner's exact words. Older guides in this repository still carry rules written
before these decisions; those rules are kept as history and are marked *Superseded on &lt;date&gt;*
where they stand. When a guide and this index disagree, the later dated owner decision in the linked
record wins. This index adds no scope of its own: every line below points at an existing record.

**Last reconciled:** 2026-10-10. Measure counts and versions from the files named, never from this page.

| Area | In force now | Date | Owner's words (verbatim) | Source record |
|---|---|---|---|---|
| Original content | **Reversed in part.** Original gameplay art, audio, items, benches, gate equipment and terrain may ship. Reuse remains the default; the gate stays a designation on a real door; another package's assets are never copied; things rotate. | 2026-10-06 | *"are we making our own items and benches and gates? becasue if so i fucking love it!"* / *"remember things rotate"* | [CONTENT_REUSE_POLICY.md](CONTENT_REUSE_POLICY.md), [GATE_0_DECISIONS.md decision log](GATE_0_DECISIONS.md#decision-log) |
| Dependencies and expansions | **No hard dependency at all.** `About.xml` declares no `modDependencies`; the five expansions and the profile mods are optional, load-order-only (`loadAfter`), with graceful by-name guards. | 2026-10-03 | *"rework mod to not need any depeancie mods"* / *"we hope to have the mod as a complete stand alone"* | [GATE_0_DECISIONS.md D3/D4 rows](GATE_0_DECISIONS.md#decision-log) |
| Version | **0.13.0-dev.** Read it from `Mod/Rimrooms - Async Industries/About/About.xml` (`modVersion`); older 0.2/0.3/0.4 checkpoints are historical. | — | — | `About.xml`, [CHANGELOG.md](../CHANGELOG.md) |
| Who launches the game | **The local player (agent or local model) may launch and play**, and restart scenarios as needed. The owner's own saves are never overwritten; saves the player writes are prefixed and additive. The earlier "only the owner launches, through RimSort" rule is superseded. | 2026-10-06, extended 2026-10-10 | *"okay u fucking play the game and restart the scenerios as needed to test whats needed"*; then *"UNITY FUCKING RUNS EVERYTHING AS HERSELF PERFECTLY LOCAL MODEL on start.bat press and stop.bat properly kills everything"* | [TODO.md](TODO.md) (owner direction 2026-10-06), [NOW.md](NOW.md) (standing order 2026-10-10) |
| Who may cross a gate | **Anything on your own map may walk out through an open gate, and a prisoner of the colony may cross both ways**, governed by zoning, door permissions and the profile's access/prisoner mods. Nothing is ever lured: an open gate is still never an objective, spawn target or raid route, and inhabitants further in still do not seek it. | 2026-10-06 | *"not anyone in base, but anyone on your map.. a enemy can break in and cross the gate to get valuables and members"* / *"hold up now friendlys can too"* / *"a prisoner should be able to cross a gate is allowed to ( send the prisonerrs to live and work in there and cross path back if zoned to and door are allowed access remmebr mods we have also along side all of that.. locks and prisoner mods"* | [CONNECTED_COLONY_PORTALS.md](CONNECTED_COLONY_PORTALS.md#who-may-cross-and-the-pacing-of-what-waits-on-the-other-side) |
| Branches | **One lowercase standard: `main`, `develop`, `feature/*`**, with pull requests at each merge boundary. The stale capitalised `Main` and `Develop` were archived as `archive/Main-do-not-use` and `archive/Develop-do-not-use` and are never recreated. | 2026-10-10 | *"make it one only maybe archive the other with do not use"* | [NOW.md](NOW.md) (Branch row) |
| Repositories | **No separate mod-only repository.** The mod is `Mod/Rimrooms - Async Industries` plus `src/RimroomsAsyncIndustries` in this repository. | 2026-10-10 | — (recorded as fact in the handoff) | [NOW.md](NOW.md) (Branch row) |
| Forgejo remote | **Held.** No pushes until the owner says the host is back; not lifted by time or by a push happening to succeed. | 2026-10-06 | *"fyi the git.unityailab.com is going down so stop pushes to it until further notice, github two repos is still good"* | [PUBLISHING.md](PUBLISHING.md) |
| Distribution | Public Steam Workshop is the first target; no compatibility is announced until validated. | 2026-09-29 | *"option 3 and remeber we dont have other peoples saves we just publish it all and update it as we go fixing bugs"* | [GATE_0_DECISIONS.md D1](GATE_0_DECISIONS.md#d1-superseded-2026-09-29--public-workshop-is-the-first-distribution-target) |

## Open for the owner

- The local-player permission is recorded from the two directions above. Whether it also covers
  attaching the QA bridge and changing the active mod list, which older guides forbid separately, is
  not stated in either direction and has not been assumed.
- The tracked inspection and decompiled reference material under `.local/` needs a public/private
  boundary review: [INSPECTION_MATERIAL.md](INSPECTION_MATERIAL.md).
- Publication is not authorised by this file. Any push must first inspect the actual remote refs and
  follow the latest direction; the Forgejo hold stands until lifted.
