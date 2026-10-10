# -*- coding: utf-8 -*-
"""Bring the reader-facing documents into the mod's own vocabulary, and unwall them."""
import io

def patch(path, pairs):
    text = io.open(path, encoding='utf-8-sig').read()
    for old, new in pairs:
        assert old in text, '%s: not found: %r' % (path, old[:70])
        text = text.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8-sig', newline='').write(text)
    print('  patched %s (%d)' % (path, len(pairs)))


# --------------------------------------------------------------------------- README
patch('README.md', [
    # One 725-character paragraph, and "doorway"/"machine" for the gate. Split into a list:
    # it was already a list of clauses joined by semicolons.
    (u"What works in source today, briefly: a gate is an **ordinary door you designate** rather "
     u"than a custom machine, at sizes from 1x1 to 2x3; **bringing a connection up is work** an "
     u"operator does at a console, faster on a route the crew has run before; each gate keeps "
     u"its own **address book** of everywhere it has dialled; colonists and animals cross, with "
     u"the gate's width deciding what fits through; coordinates generate as rooms, corridors "
     u"and **facilities** that span several rooms at once; what lives there **follows a crew to "
     u"the doorway** in the worst spaces and, on an advanced machine, can come through behind "
     u"them; and an **odd-origin economy**, company bonds, a corporate trader and a credits "
     u"ladder sit on top of it.",

     u"What works in source today:\n"
     u"\n"
     u"- A gate is an **ordinary door you designate**, never a custom object, at sizes from 1x1 "
     u"to 2x3.\n"
     u"- **Bringing a connection up is work** an operator does at a console, and it is faster on "
     u"a route the crew has run before.\n"
     u"- Each gate keeps its own **address book** of everywhere it has dialled.\n"
     u"- Colonists and animals cross. The gate's width decides what fits through.\n"
     u"- Coordinates generate as rooms, corridors and **facilities** that span several rooms at "
     u"once.\n"
     u"- What lives down there **follows a crew to the threshold** in the worst spaces, and "
     u"through an advanced gate it can come out behind them.\n"
     u"- An **odd-origin economy** sits on top of all of it: company bonds, a corporate trader "
     u"and a credits ladder."),

    (u"connected colony portals super",
     u"the connected-colony contract super"),

    (u"The latest required direction is [one connected local colony through open portals]"
     u"(docs/CONNECTED_COLONY_PORTALS.md): shared work/material access, permanent natural "
     u"portals and persistent procedural inhabitants. This unified work network is not yet "
     u"implemented by the native-provider foundation.",

     u"The latest required direction is [one connected local colony through open gates]"
     u"(docs/CONNECTED_COLONY_PORTALS.md): shared work and material access, permanently open "
     u"natural gates, and persistent procedural inhabitants. This unified work network is not "
     u"yet implemented by the native-provider foundation."),

    # A 1,275-character paragraph that was also badly stale: it cited the 0.2.0 build record,
    # "original sprites" that were retired in 0.9.0-dev, and a register row count that is 295.
    (u"Gate 0 documentation/source criteria passed. The [0.2.0 build record]"
     u"(docs/implementation/PHASE_2_BUILD_RECORD.md) now maps the implemented first-expedition "
     u"slice, original sprites, compiler evidence and remaining work. Gate 2 gameplay "
     u"acceptance, full campaign content, final audio and the main-menu slideshow remain open. "
     u"Fan-summary story coverage is complete for the 23 indexed Kane Pixels uploads and the "
     u"separate A24 feature note; the notes clearly mark secondary-source claims, and watching "
     u"every video or the full film is not a Gate 0 requirement. Check creator or official film "
     u"sources only when a planned feature depends on an unresolved detail. All 294 profile "
     u"rows have accepted source-fact notes and linked review records, including direct "
     u"publisher-source follow-up for rows 96, 237, and 278. No gameplay or multiplayer "
     u"workflow tests were run for Rimrooms before a build; the two-client RWT baseline and "
     u"combined-profile compatibility remain pending post-build acceptance through the "
     u"[RimBridgeServer harness plan](docs/research/RIMBRIDGE_TEST_HARNESS.md). The product "
     u"test target is 295 entries (the current 294 plus Rimrooms); a separately loaded "
     u"RimBridgeServer QA overlay normally makes the test session 296 entries. The staging tool "
     u"copies the mod into RimSort's configured Local Mods directory; the owner alone "
     u"activates, sorts and launches it.",

     u"Gate 0's documentation and source criteria passed. Every checkpoint since has its own "
     u"record under [`docs/implementation/`](docs/implementation/).\n"
     u"\n"
     u"**Still open.** Gameplay acceptance, the remaining campaign content, the last two "
     u"starting sites, and the main-menu slideshow.\n"
     u"\n"
     u"**Story sources.** Coverage is complete for the 23 indexed Kane Pixels uploads and the "
     u"separate A24 feature note. Secondary-source claims are marked as such throughout, and "
     u"watching every video or the full film was never a requirement. Check a creator or "
     u"official source only when a planned feature turns on an unresolved detail.\n"
     u"\n"
     u"**The profile.** All rows in the integration register carry source-fact notes and a "
     u"linked review, including direct publisher follow-up for rows 96, 237 and 278. Query it "
     u"with `python tools/register-query.py`.\n"
     u"\n"
     u"**Testing.** No gameplay or multiplayer test has been run. The two-client baseline and "
     u"combined-profile compatibility are pending through the [RimBridgeServer harness plan]"
     u"(docs/research/RIMBRIDGE_TEST_HARNESS.md). The staging tool copies the mod into "
     u"RimSort's configured Local Mods directory; **the owner alone activates, sorts and "
     u"launches it**."),
])
