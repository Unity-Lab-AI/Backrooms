# Research and references

**Research snapshot: 2026-09-27.** This file separates source facts, design inspiration, and content that still needs review. The project's chosen primary lore reference is Kane Pixels' Backrooms continuity, alongside the 2026 A24 feature. The broader Backrooms concept and community wiki remain separate sources, not one unified canon.

## First-pass design findings

### Official Kane Pixels series

The official [“The Backrooms (Found Footage)” video](https://www.youtube.com/watch?v=H4dGpz6cnHo) is dated 2022-01-07. It presents the incursion through recorded footage and minimal context. The official [Backrooms playlist by Kane Pixels](https://www.youtube.com/playlist?list=PLVAh-MgDVqvDUEq6qDXqORBioE4Yhol_z) currently lists 23 entries; titles and IDs are captured in the [video index](research/kane-pixels-video-index.csv). Useful design techniques include delayed explanation, evidence that admits multiple interpretations, ordinary equipment becoming important, and environmental rules discovered through fieldwork.

The A24 interview [“Thirty Thousand Square Feet with Kane Parsons & James Wan”](https://a24films.com/notes/2026/05/thirty-thousand-square-feet-with-kane-parsons-james-wan) provides a creator-side summary. Parsons describes starting with visual exploration of liminal spaces and extending the premise into an institutional research mystery. He emphasizes treating spatial changes as intentional continuity, presenting the phenomenon as indifferent rather than morally targeted, and limiting a feature's lore load while giving the people caught in it meaningful lives outside the anomaly. The game translation is persistent coordinate records and learnable spatial rules, combined with staff histories, company motives, and evidence-based investigation; variation should not be reduced to random jump scares.

The full Kane Pixels playlist remains a required review corpus. For each official upload, note its date, new rule revealed, spatial motif, human decision, evidence type, threat behavior, and gameplay translation. All 23 titles are indexed, but video-by-video review remains pending. YouTube's transcript export reports no transcript for the first official video; check transcript availability per entry rather than assuming captions exist. Distinguish official Kane Pixels material from fan interpretations and community wiki lore.

### A24 feature film

The [official A24 page](https://a24films.com/films/backrooms) identifies Kane Parsons as director and says the premise begins with a strange doorway appearing in the basement of a furniture showroom. That ordinary commercial setting and mundane threshold are the source cue for the **Furniture & Knickknack Store** scenario. The [A24 interview](https://a24films.com/notes/2026/05/thirty-thousand-square-feet-with-kane-parsons-james-wan) describes using human character context as an entry point, maintaining spatial continuity, and keeping the feature legible without overloading it with lore. The official [A24 home-video listing](https://shop.a24films.com/products/backrooms-blu-ray) lists a 111-minute feature and production extras, including a set-build featurette, VFX breakdowns, and a prop walkthrough. These sources support scenario and research priorities, but do not replace the still-pending full feature viewing log. The [scenario contract](SCENARIOS.md) distinguishes the synopsis cue from original scenario mechanics.

Use the series and feature as the requested primary lore reference. Translate that material into RimWorld decisions: recruit and equip researchers and security, power and maintain the machine, plan openings, investigate coordinates, manage evidence, contain threats, and expand the organization. Keep a source/provenance entry for any specific names, text, image, sound, character, or design carried into the release so the project can apply the user's supplied rights basis consistently.

### Source and rights provenance

Per the project owner's direction, the Backrooms creative reference is treated under the owner's stated MIT rights premise, with Kane Pixels' continuity as the selected canon. This is a project-supplied basis rather than a ruling re-verified in this workspace. Keep a provenance record for specific names, text, images, sounds, characters, and designs that enter the distributed mod. The project does not bundle code or assets from the 294 third-party RimWorld mods; each remains installed and governed by its own publisher's terms. The Gravship Expanded pages, for example, identify CC BY-NC-ND 4.0, so the mod plan integrates their installed gameplay and does not repackage their files.

Keep creator-led Backrooms material, community-authored pages, photographs, fan games, and the A24 feature distinguishable in the source log. This preserves attribution and makes it clear which material informed each original gameplay implementation.

## Primary technical sources

- [RimWorld 1.6 and Odyssey release announcement](https://store.steampowered.com/news/posts/?appgroupname=RimWorld&appids=294100&enddate=1753200027&feed=steam_community_announcements) — confirms 1.6 is a free update separate from owning Odyssey.
- [RimWorld 1.6 modding update guide](https://rimworldwiki.com/wiki/Modding_Tutorials/RimWorld_1.6_Mod_Updates) — versioning, load folders, assembly recompilation, and compatibility process.
- [RimWorld `About.xml` guide](https://www.rimworldwiki.com/wiki/Modding_Tutorials/About.xml) and [mod folder structure](https://rimworldwiki.com/wiki/Modding_Tutorials/Mod_folder_structure) — required package metadata and the expected mod directory layout.
- [RimWorld Together repository](https://github.com/RimWorld-Together/Rimworld-Together) — upstream server project linked to workshop ID `3005289691` in the local configuration.
- [RimWorld Together releases](https://github.com/RimWorld-Together/Rimworld-Together/releases) — upstream currently lists 26.8.31.1 as the latest release, dated 2026-08-31. That release notes Odyssey asteroid compatibility and world/site synchronization fixes. Record the exact local build before treating those features as an installed fact.
- [RWT and gravship feasibility audit](research/RWT_AND_GRAVSHIP_FEASIBILITY.md) — local client/server ID and order comparison, exact local settings/build gap, profile vehicle/space shortlist, and sourced VGE requirements.
- RWT's official [Workshop page](https://steamcommunity.com/sharedfiles/filedetails/?id=3005289691) and [upstream releases](https://github.com/RimWorld-Together/Rimworld-Together/releases) — use as the published feature/release source. Project wiki endpoints returned HTTP 403 during this review; detailed visit, transfer, and settings semantics remain unverified until checked in the pinned build.
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

- Review all 23 official playlist entries in the [direct-linked index](research/kane-pixels-video-index.csv), save a [timestamped review record](research/reviews/README.md) for each, and include relevant transcripts only when actually available. Do not treat user-uploaded compilations as authoritative.
- Review the feature film in full and add a high-level design analysis of systems, pacing, spaces, company behavior, equipment, training, and story missions. Current notes use the official A24 synopsis and interview; a scene-by-scene viewing log has not been completed.
- Identify which room and entity motifs belong to the broad community corpus, Kane Pixels' own continuity, individual contributors, or the film.
- Identify the local RWT server commit as a published release and pin the exact client/server/game/DLC profile; the local config comparison is complete but the deployed build identity is not.
- Inspect RWT source for supported extension points and verify item, pawn, visit, save/reconnect, and transaction behavior in a disposable profile.
- Decide Rimrooms - Async Industries' code, text, and asset licenses before accepting outside contributions or adapting community work.
