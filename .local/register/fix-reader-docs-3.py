# -*- coding: utf-8 -*-
"""The last of the reader-facing set: the stale traversal rule, and four walls."""
import io

def patch(path, pairs):
    text = io.open(path, encoding='utf-8-sig').read()
    for old, new in pairs:
        assert old in text, '%s: not found: %r' % (path, old[:70])
        text = text.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8-sig', newline='').write(text)
    print('  patched %s (%d)' % (path, len(pairs)))


# The same paragraph is duplicated at the head of both documents. It was stale in two ways:
# it still said gate and portal were one word, which 0.10.2-dev settled into three words for
# three different things, and it still said nothing but our own pawns ever crosses, which
# 0.9.6-dev made a bounded exception to.
OLD_RULE = (
    u"Pressure escalates gradually from saved causes, bounded per opening and per coordinate, "
    u"with quiet stretches as required content. Gate, machine door and portal are one thing in "
    u"the owner's vocabulary; every start can eventually run several gates.")
NEW_RULE = (
    u"Pressure escalates gradually from saved causes, bounded per opening and per coordinate, "
    u"with quiet stretches as required content. Every start can eventually run several gates.\n"
    u"\n"
    u"**Two later directions refine this rule and are not in conflict with it.** The words are "
    u"now three rather than one: the **gate** is the designated door, the **connection** is the "
    u"live link it holds open, and the **threshold** is where you arrive. And there is exactly "
    u"one bounded exception to nothing-crosses-under-its-own-will: at the deepest pressure "
    u"band, through an advanced gate, while an opening is live, something that fits may follow "
    u"a crew out. A gate is still never an objective, a lure or a spawn target, and nothing is "
    u"ever drawn toward one.")

for path in ('docs/GAME_DESIGN.md', 'docs/SCENARIOS.md'):
    patch(path, [(OLD_RULE, NEW_RULE)])


patch('docs/COMPATIBILITY.md', [
    (u"The server configuration is a useful real-world profile, but `AllowAllMods=true`, "
     u"`EnforceSettings=false`, and an unset order mean the server does not guarantee that "
     u"every future client keeps the same list. The current exact local match is a dated "
     u"observation; a co-op release still needs a pinned/enforced join profile and an in-game "
     u"run. RWT's official wiki describes configurable offline visits/raids; its trading guide "
     u"says direct trades and gifts require both players online. Local Aid and Trade actions "
     u"are enabled, while offline-visit availability is not established. Test visits, aid, "
     u"direct trade, and reconnect as separate workflows. Keep company maps, research, gate "
     u"state, and ledgers separate. See the [source register](SOURCE_REGISTER.md), "
     u"[per-mod RWT review](research/reviews/mods/3005289691-nova.rimworldtogether.md), and "
     u"[RWT feasibility audit](research/RWT_AND_GRAVSHIP_FEASIBILITY.md).",

     u"The server configuration is a useful real-world profile, but `AllowAllMods=true`, "
     u"`EnforceSettings=false` and an unset order mean the server does **not** guarantee that "
     u"every future client keeps the same list. The current exact local match is a dated "
     u"observation, and a co-op release still needs a pinned, enforced join profile and an "
     u"in-game run.\n"
     u"\n"
     u"RWT's official wiki describes configurable offline visits and raids; its trading guide "
     u"says direct trades and gifts require both players online. Local Aid and Trade actions "
     u"are enabled, while offline-visit availability is not established.\n"
     u"\n"
     u"Test visits, aid, direct trade and reconnect as **separate workflows**, and keep company "
     u"maps, research, gate state and ledgers separate. See the [source register]"
     u"(SOURCE_REGISTER.md), the [per-mod RWT review]"
     u"(research/reviews/mods/3005289691-nova.rimworldtogether.md) and the [RWT feasibility "
     u"audit](research/RWT_AND_GRAVSHIP_FEASIBILITY.md)."),
])


patch('docs/GAME_DESIGN.md', [
    (u"The full-mod interface goal is a company-first remaster of RimWorld's menus, tabs, and "
     u"campaign views, so players manage facilities, staff, money, research, the gate, "
     u"expeditions, cases, contracts, discovered spaces, and outposts as one connected "
     u"operation. Start with an **Operations** board in the first playable, then grow it into "
     u"Company Command pages for those work areas. Existing pawn, building, map, work, "
     u"research, and world actions must remain reachable and retain their familiar RimWorld "
     u"behavior; reorganize their presentation without breaking the underlying colony "
     u"simulation. Decide the final tab arrangement through playability and profile-interaction "
     u"checks rather than treating the first-slice layout as the finished interface.",

     u"The full-mod interface goal is a company-first remaster of RimWorld's menus, tabs and "
     u"campaign views, so that facilities, staff, money, research, the gate, expeditions, "
     u"cases, contracts, discovered spaces and outposts are managed as one connected "
     u"operation.\n"
     u"\n"
     u"Start with an **Operations** board in the first playable, then grow it into Company "
     u"Command pages for those work areas.\n"
     u"\n"
     u"**Existing pawn, building, map, work, research and world actions must remain reachable "
     u"and keep their familiar RimWorld behaviour.** Reorganise their presentation without "
     u"breaking the underlying colony simulation. Decide the final tab arrangement through "
     u"playability and profile-interaction checks rather than treating the first-slice layout "
     u"as the finished interface."),
])


patch('docs/RESEARCH.md', [
    (u"Parsons describes starting with visual exploration of liminal spaces and extending the "
     u"premise into an institutional research mystery. He emphasizes treating spatial changes "
     u"as intentional continuity, presenting the phenomenon as indifferent rather than morally "
     u"targeted, and limiting a feature's lore load while giving the people caught in it "
     u"meaningful lives outside the anomaly. The game translation is persistent coordinate "
     u"records and learnable spatial rules, combined with staff histories, company motives, and "
     u"evidence-based investigation; variation should not be reduced to random jump scares.",

     u"Parsons describes starting with visual exploration of liminal spaces and extending the "
     u"premise into an institutional research mystery. He emphasises three things:\n"
     u"\n"
     u"- treating spatial changes as **intentional continuity** rather than randomness;\n"
     u"- presenting the phenomenon as **indifferent** rather than morally targeted;\n"
     u"- limiting a feature's lore load while giving the people caught in it meaningful lives "
     u"outside the anomaly.\n"
     u"\n"
     u"The game translation is persistent coordinate records and learnable spatial rules, "
     u"combined with staff histories, company motives and evidence-based investigation. "
     u"**Variation must not be reduced to random jump scares.**"),

    (u"The official Kane Pixels playlist is the selected story reference. The 23-entry snapshot "
     u"reviewed on 2026-09-27 is indexed, and every indexed upload has a concise, linked "
     u"fan-summary note in [`research/KANE_PIXELS_FAN_CLIFF_NOTES.md`]"
     u"(research/KANE_PIXELS_FAN_CLIFF_NOTES.md). The owner approved this first-pass route: "
     u"focus on people, events, organization, memorable spaces or threats, mysteries, and a few "
     u"useful RimWorld ideas, and label fan interpretation separately from confirmed details. A "
     u"full watch is not required for the current preparation pass; check an official upload "
     u"only for a source-critical uncertainty or a visual detail the mod needs to reproduce. "
     u"The guide identifies fan-reported supplemental clips outside the official playlist; keep "
     u"them separate and recheck the playlist when content production starts.",

     u"The official Kane Pixels playlist is the selected story reference. The 23-entry snapshot "
     u"reviewed on 2026-09-27 is indexed, and every indexed upload has a concise, linked "
     u"fan-summary note in [`research/KANE_PIXELS_FAN_CLIFF_NOTES.md`]"
     u"(research/KANE_PIXELS_FAN_CLIFF_NOTES.md).\n"
     u"\n"
     u"The owner approved this first-pass route: focus on people, events, organisation, "
     u"memorable spaces or threats, mysteries, and a few useful RimWorld ideas, and label fan "
     u"interpretation separately from confirmed details.\n"
     u"\n"
     u"A full watch is not required for the current preparation pass. Check an official upload "
     u"only for a source-critical uncertainty or a visual detail the mod needs to reproduce. "
     u"The guide identifies fan-reported supplemental clips outside the official playlist; keep "
     u"those separate, and recheck the playlist when content production starts."),

    (u"That ordinary commercial setting and mundane threshold are the source cue for the "
     u"**Furniture & Knickknack Store** scenario. A separate first-pass plot note is recorded "
     u"from the fan-maintained movie summary in "
     u"[`research/reviews/a24-feature/feature-review.md`]"
     u"(research/reviews/a24-feature/feature-review.md); its claims remain labeled as "
     u"secondary.",

     u"That ordinary commercial setting and mundane threshold are the source cue for the "
     u"**Furniture & Knickknack Store** scenario.\n"
     u"\n"
     u"A separate first-pass plot note is recorded from the fan-maintained movie summary in "
     u"[`research/reviews/a24-feature/feature-review.md`]"
     u"(research/reviews/a24-feature/feature-review.md); its claims remain labelled as "
     u"secondary."),
])
