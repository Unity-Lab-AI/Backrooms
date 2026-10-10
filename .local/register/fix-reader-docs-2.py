# -*- coding: utf-8 -*-
"""The rest of the reader-facing set."""
import io

def patch(path, pairs):
    text = io.open(path, encoding='utf-8-sig').read()
    for old, new in pairs:
        assert old in text, '%s: not found: %r' % (path, old[:70])
        text = text.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8-sig', newline='').write(text)
    print('  patched %s (%d)' % (path, len(pairs)))


patch('docs/HOWTO.md', [
    (u"- **Connected colony portals** supersede dispatch-only ordinary travel "
     u"([`CONNECTED_COLONY_PORTALS.md`](CONNECTED_COLONY_PORTALS.md)). Natural portals are "
     u"permanently open. One local branch's labour and materials work across an open portal "
     u"without crew manifests.",

     u"- **Connected colony gates** supersede dispatch-only ordinary travel "
     u"([`CONNECTED_COLONY_PORTALS.md`](CONNECTED_COLONY_PORTALS.md)). Natural gates are "
     u"permanently open. One local branch's labour and materials work across a live connection "
     u"without crew manifests."),
])


patch('docs/GAME_DESIGN.md', [
    (u"**Latest owner requirement — connected colony portals (2026-09-28):** "
     u"[CONNECTED_COLONY_PORTALS.md](CONNECTED_COLONY_PORTALS.md) governs travel, work, "
     u"materials, portal lifetime, coordinate persistence and procedural inhabitants. Open "
     u"portals unify local-branch labor and physical job/material access across both sides; "
     u"ordinary crossing must not require expedition dispatch. Natural portals remain "
     u"permanently open.",

     u"**Latest owner requirement — connected colony gates (2026-09-28):** "
     u"[CONNECTED_COLONY_PORTALS.md](CONNECTED_COLONY_PORTALS.md) governs travel, work, "
     u"materials, connection lifetime, coordinate persistence and procedural inhabitants. A "
     u"live connection unifies local-branch labour and physical job and material access across "
     u"both sides; ordinary crossing must not require expedition dispatch. Natural gates remain "
     u"permanently open."),

    (u"**Latest scenario/gate direction:** [the setup and portal-network contract]"
     u"(SCENARIO_SETUP_AND_PORTAL_NETWORK.md) defines separate customizable openings, a "
     u"company-selected surface tile, the proposed automatic inside start, and existing-door "
     u"portals governed by physical connected equipment and power.",

     u"**Latest scenario/gate direction:** [the setup and gate-network contract]"
     u"(SCENARIO_SETUP_AND_PORTAL_NETWORK.md) defines separate customizable openings, a "
     u"company-selected surface tile, the proposed automatic inside start, and existing-door "
     u"gates governed by physical connected equipment and power."),

    (u"inventory, funds, gate/portal state, known coordinates",
     u"inventory, funds, gate state, known coordinates"),

    (u"### The machine gate and expeditions",
     u"### The gate and expeditions"),

    # 1,274-character paragraph, and "power the machine" for the gate.
    (u"The first playable focuses on **Async Industries**: a new save starts at its facility; "
     u"the player can build and power the machine, complete its assembly project, assign a "
     u"viable crew, open one seeded expedition site, explore and extract, close/recall through "
     u"the gate, return to the same saved coordinate, analyze the recovered evidence, receive a "
     u"payment or research reward, and respond to the first distortion and hostile encounter. "
     u"Its target values and acceptance checks are in the [first playable contract]"
     u"(FIRST_PLAYABLE_CONTRACT.md), [first-slice content inventory]"
     u"(FIRST_SLICE_CONTENT_INVENTORY.md), [threat sheets](THREAT_DESIGN_SHEETS.md), and "
     u"[economy model](CAMPAIGN_ECONOMY_MODEL.md). The scenario framework and the Store and "
     u"Lone Survivor starts are defined in [SCENARIOS.md](SCENARIOS.md) and implemented after "
     u"the vertical slice proves the shared systems. The co-op design target is separate player "
     u"branches that can exchange only tested items/dossiers, send supported aid, and visit "
     u"another facility only if the pinned RWT build and settings expose a safe visit route. "
     u"Each branch keeps its own gate, map, staff, research completion, contracts, and ledger; "
     u"the design does not promise live shared-map control or synchronized company research. "
     u"Test whether distinct scenario starts can coexist in one RWT server before making that a "
     u"support promise. See the [complete multiplayer and systems plan]"
     u"(MOD_INTEGRATION_PLAN.md#2-cooperative-company-model).",

     u"The first playable focuses on **Async Industries**. A new save starts at its facility, "
     u"and the player can:\n"
     u"\n"
     u"- build and power the gate, and complete its assembly project;\n"
     u"- assign a viable crew and bring a connection up to one seeded coordinate;\n"
     u"- explore, extract, and recall through the gate;\n"
     u"- return to the same saved coordinate and find it as they left it;\n"
     u"- analyse the recovered evidence for a payment or a research reward;\n"
     u"- and meet the first distortion and the first hostile encounter.\n"
     u"\n"
     u"Target values and acceptance checks live in the [first playable contract]"
     u"(FIRST_PLAYABLE_CONTRACT.md), the [first-slice content inventory]"
     u"(FIRST_SLICE_CONTENT_INVENTORY.md), the [threat sheets](THREAT_DESIGN_SHEETS.md) and the "
     u"[economy model](CAMPAIGN_ECONOMY_MODEL.md). The scenario framework and the Store and "
     u"Lone Survivor starts are defined in [SCENARIOS.md](SCENARIOS.md), and are implemented "
     u"after the vertical slice proves the shared systems.\n"
     u"\n"
     u"The co-op design target is separate player branches that exchange only tested items and "
     u"dossiers, send supported aid, and visit another facility only if the pinned RWT build "
     u"and settings expose a safe visit route. Each branch keeps its own gate, map, staff, "
     u"research completion, contracts and ledger. **The design does not promise live shared-map "
     u"control or synchronised company research**, and whether distinct scenario starts can "
     u"coexist in one RWT server has to be tested before it becomes a support promise. See the "
     u"[complete multiplayer and systems plan]"
     u"(MOD_INTEGRATION_PLAN.md#2-cooperative-company-model)."),
])


patch('docs/SCENARIOS.md', [
    (u"**Latest owner requirement — connected colony portals (2026-09-28):** "
     u"[CONNECTED_COLONY_PORTALS.md](CONNECTED_COLONY_PORTALS.md) governs travel, work, "
     u"materials, portal lifetime, coordinate persistence and procedural inhabitants. Open "
     u"portals unify local-branch labor and physical job/material access across both sides; "
     u"ordinary crossing must not require expedition dispatch. Natural portals remain "
     u"permanently open.",

     u"**Latest owner requirement — connected colony gates (2026-09-28):** "
     u"[CONNECTED_COLONY_PORTALS.md](CONNECTED_COLONY_PORTALS.md) governs travel, work, "
     u"materials, connection lifetime, coordinate persistence and procedural inhabitants. A "
     u"live connection unifies local-branch labour and physical job and material access across "
     u"both sides; ordinary crossing must not require expedition dispatch. Natural gates remain "
     u"permanently open."),

    (u"**Latest setup refinement:** [Scenario setup and physical door portals]"
     u"(SCENARIO_SETUP_AND_PORTAL_NETWORK.md)",
     u"**Latest setup refinement:** [Scenario setup and physical door gates]"
     u"(SCENARIO_SETUP_AND_PORTAL_NETWORK.md)"),

    # The A24 synopsis's own word, so it is quoted rather than reworded.
    (u"which describes a strange doorway in a furniture-showroom basement",
     u'which describes a strange "doorway" in a furniture-showroom basement'),

    (u"buildings, gate or portal state, known coordinates",
     u"buildings, gate and connection state, known coordinates"),
])


patch('docs/CONTENT_REUSE_POLICY.md', [
    (u"**Explicit door direction:** the owner selected actual existing doors, native "
     u"recoloring/aura and supported installed doorway sizes for portals. See "
     u"[the scenario/portal contract](SCENARIO_SETUP_AND_PORTAL_NETWORK.md)",

     u"**Explicit door direction:** the owner selected actual existing doors, native "
     u"recolouring and aura, and the installed door sizes the game already supports. See "
     u"[the scenario and gate contract](SCENARIO_SETUP_AND_PORTAL_NETWORK.md)"),
])


patch('docs/RESEARCH.md', [
    # The A24 page's own word. Quoted, not reworded.
    (u"says the premise begins with a strange doorway appearing in the basement of a furniture "
     u"showroom",
     u'says the premise begins with a strange "doorway" appearing in the basement of a '
     u'furniture showroom'),
    (u"distinguishes the confirmed furniture-store doorway cue from original scenario mechanics",
     u'distinguishes the confirmed furniture-store "doorway" cue from original scenario '
     u'mechanics'),
])


patch('docs/RIMROOMS_MOD_OVERVIEW.md', [
    (u"### Build a company. Open the machine. Discover what lies beyond.",
     u"### Build a company. Open the gate. Discover what lies beyond."),
])


patch('docs/TUTORIAL_SCRIPT.md', [
    (u"The tag is on the wrong side of the doorway.",
     u"The tag is on the wrong side of the door."),
])
