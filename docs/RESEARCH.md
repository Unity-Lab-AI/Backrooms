# Research and references

**Research snapshot: 2026-09-27.** This file separates source facts, design inspiration, and content that still needs review. The selected references are Kane Pixels' Backrooms continuity and the A24 feature, to be adapted indirectly. Broader community canon is excluded from shipped content and is not treated as one unified canon.

Keep creative-reference research story-first and readable: capture the people, mystery, atmosphere, and ideas useful to RimWorld. A timestamp is optional; detailed shot logs, production analysis, and transcript work are only needed when they answer a design question.

## First-pass design findings

### Official Kane Pixels series

The official [“The Backrooms (Found Footage)” video](https://www.youtube.com/watch?v=H4dGpz6cnHo) is dated 2022-01-07. It presents the incursion through recorded footage and minimal context. The official [Backrooms playlist by Kane Pixels](https://www.youtube.com/playlist?list=PLVAh-MgDVqvDUEq6qDXqORBioE4Yhol_z) currently lists 23 entries; titles and IDs are captured in the [video index](research/kane-pixels-video-index.csv). Useful design techniques include delayed explanation, evidence that admits multiple interpretations, ordinary equipment becoming important, and environmental rules discovered through fieldwork.

The A24 interview [“Thirty Thousand Square Feet with Kane Parsons & James Wan”](https://a24films.com/notes/2026/05/thirty-thousand-square-feet-with-kane-parsons-james-wan) provides a creator-side summary. Parsons describes starting with visual exploration of liminal spaces and extending the premise into an institutional research mystery. He emphasizes treating spatial changes as intentional continuity, presenting the phenomenon as indifferent rather than morally targeted, and limiting a feature's lore load while giving the people caught in it meaningful lives outside the anomaly. The game translation is persistent coordinate records and learnable spatial rules, combined with staff histories, company motives, and evidence-based investigation; variation should not be reduced to random jump scares.

The official Kane Pixels playlist is the selected story reference. The 23-entry snapshot reviewed on 2026-09-27 is indexed, and every indexed upload has a concise, linked fan-summary note in [`research/KANE_PIXELS_FAN_CLIFF_NOTES.md`](research/KANE_PIXELS_FAN_CLIFF_NOTES.md). The owner approved this first-pass route: focus on people, events, organization, memorable spaces or threats, mysteries, and a few useful RimWorld ideas, and label fan interpretation separately from confirmed details. A full watch is not required for the current preparation pass; check an official upload only for a source-critical uncertainty or a visual detail the mod needs to reproduce. The guide identifies fan-reported supplemental clips outside the official playlist; keep them separate and recheck the playlist when content production starts.

### A24 feature film

The [official A24 page](https://a24films.com/films/backrooms) identifies Kane Parsons as director and says the premise begins with a strange doorway appearing in the basement of a furniture showroom. That ordinary commercial setting and mundane threshold are the source cue for the **Furniture & Knickknack Store** scenario. A separate first-pass plot note is recorded from the fan-maintained movie summary in [`research/reviews/a24-feature/feature-review.md`](research/reviews/a24-feature/feature-review.md); its claims remain labeled as secondary. A24's [official press notes](https://praesens.com/praesens-pro-presse/katalog/backrooms/regional/de/backrooms-press-kit-dch/) and [creator interview](https://a24films.com/notes/2026/05/thirty-thousand-square-feet-with-kane-parsons-james-wan) add the filmmakers' context about the people, Async, memory-shaped spaces, and the film's visual language. The press notes explicitly describe an Async branch and callbacks to the web series. Use those explicit links as shared reference context, while keeping plot claims and game adaptations traceable to the right story track. Full feature viewing is optional unless a design-critical question remains unresolved. The [scenario contract](SCENARIOS.md) distinguishes the confirmed furniture-store doorway cue from original scenario mechanics.

Use the selected series and feature as indirect design references. Translate broad themes and production ideas into original RimWorld systems: recruit and equip researchers and security, power and maintain a machine gate, plan openings, investigate coordinates, manage evidence, contain threats, and expand the organization. Avoid directly recreating specific scenes or characters. Keep source/provenance records for any source-linked material considered for release and apply the owner's stated rights premise as an owner-provided assertion.

### Source and rights provenance

Per the project owner's direction, the Backrooms creative reference is treated under the owner's stated MIT rights premise, with Kane Pixels' continuity as the selected canon. This is a project-supplied basis rather than a ruling re-verified in this workspace. Keep a provenance record for specific names, text, images, sounds, characters, and designs that enter the distributed mod. The project does not bundle code or assets from the 294 third-party RimWorld mods; each remains installed and governed by its own publisher's terms. The Gravship Expanded pages, for example, identify CC BY-NC-ND 4.0, so the mod plan integrates their installed gameplay and does not repackage their files.

Keep creator-led references, community-authored pages, photographs, fan games, and the A24 feature distinguishable in the source log. Broader community material is not part of the selected shipped-content scope; consult it only when needed to identify provenance or avoid accidental conflation.

## Primary technical sources

- [RimWorld 1.6 and Odyssey release announcement](https://store.steampowered.com/news/posts/?appgroupname=RimWorld&appids=294100&enddate=1753200027&feed=steam_community_announcements) — confirms 1.6 is a free update separate from owning Odyssey.
- [RimWorld 1.6 modding update guide](https://rimworldwiki.com/wiki/Modding_Tutorials/RimWorld_1.6_Mod_Updates) — versioning, load folders, assembly recompilation, and compatibility process.
- [Official RimWorld 1.6 Modder Primer](https://docs.google.com/document/d/e/2PACX-1vRKE9u5ZW_zG45pxzwNvy4sxvozDeqtxlxpac5jwenOeW6liQCPgmPl9bIbtcMuqL1NPIDHOLFg64M_/pub) — 1.6 room layouts/parts, prefabs, map-generation stages, and tick-rate guidance; exact API use remains unprototyped.
- [RimWorld `About.xml` guide](https://www.rimworldwiki.com/wiki/Modding_Tutorials/About.xml) and [mod folder structure](https://rimworldwiki.com/wiki/Modding_Tutorials/Mod_folder_structure) — required package metadata and the expected mod directory layout.
- [RimWorld Together repository](https://github.com/RimWorld-Together/Rimworld-Together) — upstream server project linked to workshop ID `3005289691` in the local configuration.
- [RimWorld Together releases](https://github.com/RimWorld-Together/Rimworld-Together/releases) — upstream currently lists 26.8.31.1 as the latest release, dated 2026-08-31. That release notes Odyssey asteroid compatibility and world/site synchronization fixes. Record the exact local build before treating those features as an installed fact.
- [RWT and gravship feasibility audit](research/RWT_AND_GRAVSHIP_FEASIBILITY.md) — local client/server ID and order comparison, active action/scenario settings, RWT design boundary, and sourced VGE requirements. Direct trade/gifts are online-only per the RWT guide; offline-visit availability is not established locally.
- [Gravship, vehicle, cargo, and orbital profile interactions](research/GRAVSHIP_PROFILE_INTERACTIONS.md) — source-backed review of selected profile families that may touch VGE and a staged test order; no compatibility pass is claimed.
- [Installed mod metadata and relationships](research/RIMWORLD_1_6_PACKAGE_AND_GENERATION.md) — local 294-package facts and open path/API/runtime checks; repeatable detailed CSVs link from that note.
- [RimWorld Together Workshop page](https://steamcommunity.com/sharedfiles/filedetails/?id=3005289691), [official wiki introduction](https://rimworldtogether.wiki.gg/wiki/Introduction), [server configuration guide](https://rimworldtogether.wiki.gg/wiki/Server_Configuration), and [trading guide](https://rimworldtogether.wiki.gg/wiki/Trading) — primary co-op feature references. Direct trades and gifts require both players online; local offline-visit availability and runtime behavior remain untested. See the [per-mod review](research/reviews/mods/3005289691-nova.rimworldtogether.md).
- [RimWorld Together repository](https://github.com/RimWorld-Together/Rimworld-Together) and [release 26.8.31.1](https://github.com/RimWorld-Together/Rimworld-Together/releases/tag/26.8.31.1) — upstream source/release route and local server artifact match. No supported Rimrooms client extension contract is established yet.
- [Vanilla Gravship Expanded Chapter 1](https://steamcommunity.com/sharedfiles/filedetails/?id=3609835606) and [Chapter 2](https://steamcommunity.com/sharedfiles/filedetails/?id=3799737423) — dependency chain, selected late-game systems, and gravship compatibility caveat.

Use sources for the actual project being targeted. The separate `rwmt/Multiplayer` project and its old compatibility notes are not interchangeable with RimWorld Together.

## Source-to-design translation

| Reference observation | Original design translation |
| --- | --- |
| A breach can start in an everyday commercial interior. | Start the campaign in a modest company facility; let familiar storage and work spaces become operationally important. |
| Information arrives through footage, reports, and gaps in the record. | Use interview notes, radio transcripts, equipment logs, and contradictory crew reports as research evidence. |
| Rooms are recognizable before they become spatially wrong. | Use room templates plus coordinate-seeded changes to adjacency, lighting, size, and route logic. |
| People are sent in because the company wants reliable knowledge or assets. | Make each expedition a budgeted contract with a crew, a cargo limit, an opening window, and an explicit return plan. |
| The threat is only partly understood. | Give each threat discoverable rules, clues, and countermeasures; keep outcomes learnable instead of arbitrary. |

## Open research work

- The first-pass Kane fan story notes are complete in [`research/KANE_PIXELS_FAN_CLIFF_NOTES.md`](research/KANE_PIXELS_FAN_CLIFF_NOTES.md). The scope decision keeps `Faultline.mov` as a separate unresolved companion lead and excludes `Simpsons` from shipped scope. Consult direct creator sources only to answer unresolved questions that affect a planned feature.
- The first-pass A24 fan-summary story note is complete. Only use the optional chaptered fan recap or direct feature when a planned feature depends on a detail that the existing fan summary and official synopsis do not settle.
- If a candidate motif has uncertain provenance, identify whether it belongs to Kane Pixels' continuity, the A24 feature, the broader community, or another contributor before deciding whether it fits the selected scope.
- Test offline visits, cargo/pawn aid, scenario joining, and save/reconnect in the pinned RWT profile. Keep each player's facility and progression separate; only explore a Rimrooms-specific extension if a concrete feature needs one.
- Record MIT for original source code; decide text, art, audio, and outside-contribution terms separately before accepting contributions or adding assets. Broader community canon remains outside shipped-content scope.
