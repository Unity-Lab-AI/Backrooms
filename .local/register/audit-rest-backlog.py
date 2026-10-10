# -*- coding: utf-8 -*-
"""Re-measure the remaining open backlog blocks against the shipped code, 0.12.14-dev.

Covers Phase 2, period and factions, continuous portal topology, the Backrooms has no outside,
M4 and M5. Same rules as `audit-m3-backlog.py`: LAW forbids deleting TODO information, so this
changes the STATUS ONLY and APPENDS evidence. Every original word is kept.

The headline finding is in the factions block: **no `FactionDef` exists anywhere in the package**,
so all thirteen rows of a direct owner direction from 2026-09-28 are genuinely unbuilt. The owner
already answered that new `FactionDef`s are permitted, so this is authorised work that was simply
never done -- and it is the largest such block left.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, 'docs', 'TODO.md')

BUILT = u'**BUILT.** '
PART = u'**PARTLY BUILT.** '
OPEN = u'**STILL OPEN.** '
SUP = u'**SUPERSEDED.** '

VERDICTS = [
    # ------------------------------------------------------------------ Phase 2
    (u'Implement one authoritative gate state machine with validated transitions', u'x',
     BUILT + u'The spin-up is the one way a gate opens and every entry point routes into it '
     u'(invariant 32); 68 dead branches were collapsed in 0.9.1-dev to leave exactly one.'),
    (u'Implement a single transaction service for stock/currency/job/project changes', u'x',
     BUILT + u'`PostTransaction` with idempotent operation ids and a receipt-mismatch refusal; the '
     u'running balance is revalidated on load and a mismatch disables company actions rather than '
     u'silently correcting itself.'),
    (u'Implement stable site/coordinate IDs, deterministic seed construction', u'x',
     BUILT + u'`CampaignSeed.Derive` (FNV, never `String.GetHashCode`), `generatorVersion`, '
     u'`roomLibraryVersion`, saved room graphs, `OwnsMap`, and revisit displacement.'),
    (u'Implement stable references to pawns/buildings/sites via game-supported serialization', u'x',
     BUILT + u'`Scribe_References` throughout, `GetUniqueLoadID` bindings, and '
     u'`Company/LostPawnRegister.cs` for a reference that does go missing.'),
    (u'Add structured log categories and debug summaries for campaign/coordinate/gate', u'x',
     BUILT + u'`Core/RimroomsDiagnostics.cs`, with `Measure(...)` scopes on the company and '
     u'expedition ticks.'),
    (u'Add versioned save components and migration from each released schema', u'x',
     BUILT + u'`schemaVersion` with `CurrentSchemaVersion` 2, migration at `PostLoadInit`, and a '
     u'save-integrity fault that disables actions rather than corrupting a save.'),
    (u'Create the Async Industries new-game scenario with starter facility, staff, stock', u'x',
     BUILT + u'And it now opens with **eight completed research projects**, so the branch can '
     u'operate from the first minute.'),
    (u'Add gate frame, control console, power requirements, emergency cutoff', u'x',
     BUILT + u'Console, power and reserve requirement, kill switch, assembly and calibration work, '
     u'inspect feedback and failure states all ship. **Repair and reliability are still open** and '
     u'are tracked on the machine-subsystems row in M3.'),
    (u'Add staff role recommendations, field kit assignment, readiness checks', u'~',
     PART + u'Configurable roles, operator assignment and readiness refusals ship. **Field kit '
     u'assignment is superseded** with the rest of the custom field gear, and native pawn and work '
     u'controls are untouched throughout.'),
    (u'Create one seeded, finite Backrooms site with a short room graph, one hazard', u'x',
     BUILT + u'And considerably exceeded: archetypes, depth bands, facilities as contiguous runs, '
     u'four anomaly effects, inhabitants with a bounded escalation ladder, and the evidence chain.'),
    (u'Add expedition dispatch/recall/close flow; track crew/cargo/location/return', u'x',
     BUILT + u'`Expedition/RimroomsExpeditionComponent.cs`, with the stranded-crew guarantee: a '
     u'gate closing on a crew **strands them and never takes them**, proved rather than asserted.'),
    (u'Add evidence intake, one lab analysis recipe/project, one researched capability', u'x',
     BUILT + u'Intake, custody on a linked archive shelf, analysis, insight, research capabilities '
     u'that real code must read, contract settlement and the ledger entry.'),
    (u'Provide a safe fallback map and recoverable error message when generation cannot', u'x',
     BUILT + u'`Generation/FailedSiteRecovery.cs`.'),

    # ------------------------------------------------------------------ factions: ALL OPEN
    (u'**"this is 1990\'s when this all starts"**', u' ',
     OPEN + u'**No `FactionDef` exists anywhere in the package** — verified by searching the whole '
     u'`Defs` tree. This is the largest completely unbuilt owner direction remaining.'),
    (u'**"the factions should be the factions of the universe"**', u' ',
     OPEN + u'Nothing built.'),
    (u'**"so US government"**', u' ', OPEN + u'Nothing built.'),
    (u'**"other corporations trying to get propietary tech"**', u' ', OPEN + u'Nothing built.'),
    (u'**"ex employes disgruntleed"**', u' ', OPEN + u'Nothing built.'),
    (u'**"high tech theives"**', u' ', OPEN + u'Nothing built.'),
    (u'**"corporate spys and sbaatosh"**', u' ', OPEN + u'Nothing built.'),
    (u'**"concerned citizens.."**', u' ', OPEN + u'Nothing built.'),
    (u'**"and anything other type of factions along these lines', u' ', OPEN + u'Nothing built.'),
    (u'**"as all this needs to be defgault set in the game settup', u' ', OPEN + u'Nothing built.'),
    (u'**The seven named universe factions** as new `FactionDef`s', u' ',
     OPEN + u'**And explicitly authorised:** the owner answered on 2026-09-28 that these are new '
     u'`FactionDef`s reusing existing pawn kinds and existing faction icon paths, because a '
     u'`FactionDef` is world configuration rather than a physical gameplay Def. **This is the next '
     u'checkpoint.**'),
    (u'**Per-scenario default faction setup**', u' ',
     OPEN + u'Owner-answered: all seven begin **neutral**, and hostility is earned by what the '
     u'branch actually does, from saved observable causes.'),
    (u'**Period-plausible starting grants** for every start', u' ',
     OPEN + u'Owner-answered: the 1990s framing **does** constrain starting grants, while research '
     u'may still climb anywhere, so no start can be dead-ended.'),

    # ------------------------------------------------------------------ portal topology
    (u'**"the solo/group start  and industry async start and furnature store start all need', u'x',
     BUILT + u'All three starts ship with their portals, 0.11.9-dev through 0.12.2-dev.'),
    (u'**"a back room can have a protal to another normal worlds map"**', u'x',
     BUILT + u'`Portals/CompRimroomsEmergence.cs` — a way out surfaces on an ordinary map the '
     u'branch owns.'),
    (u'**"or a portal to a deep level of the backrooms"**', u'x',
     BUILT + u'`Portals/NaturalFrontierService.cs`. Found doors stop at depth 3 (0.12.1-dev); '
     u'deeper needs a gate the branch builds.'),
    (u'**"ect ect"**', u'x',
     BUILT + u'By construction, not by enumeration: invariant 18, the topology is an **unbounded '
     u'alternation** of world maps and coordinates, so no fixed set of link kinds exists to limit.'),
    (u'**"so that any one backrooms portal corroridanet weither from a lab portal or a natural', u'x',
     BUILT + u'`RimroomsPortalNetwork` links arbitrary endpoints regardless of which kind of '
     u'portal reached them.'),
    (u'**"and other backroom instance seeds"**', u'x',
     BUILT + u'Each coordinate carries its own seed and the network links endpoints across them.'),
    (u'**"and or pop out any where in the game world on a tile map"**', u'~',
     PART + u'A way out onto an ordinary map the branch **already holds** ships. A far side on a '
     u'world tile the branch does **not** hold is still open — see its own row below.'),
    (u'**"there can be portals with in portals"**', u'x',
     BUILT + u'Nesting is unbounded, again by invariant 18 rather than by a depth counter.'),
    (u'**"and portals found on world maps"**', u'x',
     BUILT + u'`NaturalFrontierService.MaximumFrontiersPerOrdinaryMap` — a separate budget from the '
     u'per-coordinate one, so frontiers appear on ordinary maps too.'),
    (u'**"when u do the cites and build the furnature store and starting lab maps basic defaults', u'x',
     BUILT + u'All three starts have authored layouts with starting equipment and facilities, and '
     u'`proof-starts.py` reads building sizes from Core’s own ThingDefs to guard them — which is '
     u'how three new-game crashes were caught before shipping.'),
    (u'**"if you know how to do that or we just give them starting equipment building', u'x',
     SUP + u'The owner offered a fallback of *"just give them equipment and they build it"*. It was '
     u'**not needed**: authored layouts ship for all three starts.'),
    (u'**"i dont know how good you will be at designing starting building faciliteis', u'x',
     BUILT + u'The attempt was made and it shipped, and the honest note is that it needed a proof '
     u'to be safe — a start layout is a new-game crash nothing else can see (invariant 146).'),
    (u'**"map>backrrooms>backrroms"**', u'x',
     BUILT + u'This chain already routes, as the row itself notes.'),
    (u'**"map > backrooms > map > backrooms"**', u'~',
     PART + u'Every step routes **except** re-entering the world on a tile the branch does not '
     u'already hold. The row’s original blocker — the solo/group first-exit question — is now '
     u'**answered and closed**; what remains is the unheld-tile emergence.'),
    (u'**"backrromms > map>backrooms>backrooms>map"**', u'~',
     PART + u'Same single remaining dependency: the second departure to the world needs the '
     u'unheld-tile case.'),
    (u'**"are just a few of the portal connections allowed"**', u'x',
     BUILT + u'No length limit, no ordering rule and no forbidden combination exists, deliberately.'),
    (u'**"to different maps in the world"**', u'~',
     PART + u'Separate owned maps along one chain work. Separate **unheld** tiles need the row '
     u'below.'),
    (u'**"with different portal combos built and found"**', u'x',
     BUILT + u'Laboratory-built gates and natural frontiers mix freely along a chain; '
     u'`PortalConnectionKind` distinguishes them without restricting how they compose.'),
    (u'**A portal whose far side is an already-owned ordinary map**', u'x',
     BUILT + u'`CompRimroomsEmergence.OrdinaryBranchMap`, and 0.12.6-dev widened it to any '
     u'registered site for free, from the ownership predicate rather than a new rule.'),
    (u'**A portal whose far side is a world tile the branch does not yet hold**', u' ',
     OPEN + u'**The one genuinely unbuilt piece of the topology.** Needs a new world object and a '
     u'generated map, so it touches world generation rather than only the portal network. Three '
     u'chain rows above are waiting on exactly this.'),
    (u'**The three starting sites, implemented against their existing specification.**', u'x',
     BUILT + u'0.11.9-dev and 0.12.0-dev through 0.12.2-dev.'),

    # ------------------------------------------------------------------ no outside
    (u'**"a backrooms environment can never have an out side in of itselfe"**', u'x',
     BUILT + u'`Generation/BackroomsContainment.cs` roofs every unroofed cell with '
     u'`RoofDefOf.RoofRockThick`. Invariant 13.'),
    (u'**"so mods like remove roof for removing mountain need something in our mod', u'x',
     BUILT + u'A thick rock roof is what makes this survive another mod’s roof removal, rather '
     u'than a check on a specific mod — which is why it also survives mods nobody has seen yet.'),
    (u'**"and all roof in a backrroms is never revovable"**', u'x',
     BUILT + u'Thick roof, and the containment component re-roofs on a sweep, so a hole made by '
     u'any means closes again.'),
    (u'**"and no one in any scerio can find them selfs in a world map eara but by finding', u'x',
     BUILT + u'The only way out of a coordinate is a registered portal, and the solo/group start '
     u'is **guaranteed** one on its first level (0.12.2-dev).'),
    (u'**"liken the one the scenerio start has for the furnature store and the one that', u'x',
     BUILT + u'The Store’s basement threshold (0.11.9-dev) and the solo/group guaranteed way out '
     u'(0.12.2-dev).'),
    (u'**"all rooms and walls and doors are all deconstructable"**', u'x',
     BUILT + u'Generation places with **no faction** (invariant 75), so every wall and door is an '
     u'ordinary deconstructable building.'),
    (u'**"and areas minable and of all types of materisals throughout"**', u' ',
     OPEN + u'**Confirmed unbuilt by grep: there is no mineable-rock placement anywhere in '
     u'`Generation/`.** The containment file’s own summary comment claims mineability, and a '
     u'comment is not an implementation — invariant 130.'),
    (u'**"and capte ands tile can all be uninstalled , moved, resued , sold , studied"**', u' ',
     OPEN + u'Carpet and tile are placed as real `TerrainDef`s by `BackroomsPalette`, so they can '
     u'be **removed**; being uninstalled, moved and reused needs the floor-recovery row below.'),
    (u'**"all of it"**', u'~',
     PART + u'Walls, doors and buildings: yes. **Mineable materials and recoverable floors: not '
     u'yet**, and those are the two rows above.'),
    (u'**Floors recovered when lifted.**', u' ',
     OPEN + u'**Confirmed unbuilt by grep: no leavings or floor-removal handling exists.** Vanilla '
     u'returns no materials when a floor is removed, so this needs real work rather than a setting. '
     u'Together with mineable materials this is one coherent piece: **the interior is a resource.**'),

    # ------------------------------------------------------------------ M4
    (u'Implement feature detection and setup diagnostics for the pinned RWT release', u' ',
     OPEN + u'Multiplayer. Requires the RWT mod present to detect anything, so it cannot be '
     u'verified without a launch the owner performs.'),
    (u'Implement no custom server schema or patches until supported extension points', u'x',
     BUILT + u'Held as a rule: no server schema or patch exists, and none may be written until '
     u'extension points are read out of the exact pinned version.'),
    (u'Document exact server setup and player experience. No statement may describe', u' ',
     OPEN + u'Documentation, and it must never claim live shared-colony control. Belongs with the '
     u'player-facing how-to.'),
    (u'Base Core-only campaign works and loads with every DLC absent.', u'x',
     BUILT + u'**Zero hard dependencies, and it is checked every build:** `check-dlc-gating.py` '
     u'passes and every DLC-touching def carries `MayRequire` (invariant 15).'),
    (u'Royalty conditional content: titles/quests/faction/psycasts', u'~',
     PART + u'The **gating mechanism** ships and is enforced. **No Royalty-specific content is '
     u'authored**, which is honest rather than a gap: it must be an optional route or nothing.'),
    (u'Ideology conditional content: beliefs, meditation, rituals, staff policies', u'~',
     PART + u'Gating ships; no Ideology-specific content authored.'),
    (u'Biotech conditional content: genes, mechanitors, children, medicine', u'~',
     PART + u'Gating ships; no Biotech-specific content authored. Nothing is mandatory.'),
    (u'Anomaly conditional content: containment/research links', u'~',
     PART + u'Gating ships, and the Backrooms entities **do** retain a base-game implementation, '
     u'which is the load-bearing half of this row. Anomaly’s `SecurityDoor` is already recognised '
     u'as a 2×1 gate when present.'),
    (u'Odyssey conditional content: gravship/off-world logistics', u'~',
     PART + u'Gating ships. Arc 7’s request families exist; no gravship integration is written, '
     u'and it stays DLC-optional throughout.'),
    (u'Check DLC-only XML folders, Def references, textures, recipes, quests', u'x',
     BUILT + u'`tools/check-dlc-gating.py`, run every checkpoint.'),
    (u'For each workbook row, close its status with evidence: reviewed version', u'~',
     PART + u'The register retro sweep is genuinely in progress: 14 families swept, 7 not yet '
     u'(medical, world operations, cargo, hospitality, materials, visitor economy, staff '
     u'psychology).'),
    (u'Resolve duplicate Defs/patch collisions in the exact 294 profile', u' ',
     OPEN + u'**Structurally requires a launch with the 294 profile loaded**, which only the owner '
     u'does, through RimSort.'),
    (u'Add a user-facing compatibility report with tested order, versions, DLC', u' ',
     OPEN + u'Cannot honestly state a tested order before anything has been tested.'),

    # ------------------------------------------------------------------ M5
    (u'Build the Operations overview and panes: Overview, Personnel, Facilities', u'x',
     BUILT + u'**Twelve panes ship**, one more than the eleven asked for: Overview, Personnel, '
     u'Contracts, Ledger, Atlas, Activity, Investigation, Machine, Expedition, Facilities, '
     u'Procurement, Sites.'),
    (u'Make each screen deep-link to the relevant pawn, building, map, quest', u'~',
     PART + u'Pane-to-pane deep links exist (a failed coordinate jumps to the Expedition pane, a '
     u'facility jumps to the Machine pane). **Deep links out to a pawn, building or research '
     u'project do not.**'),
    (u'Add explainable alerts, reason codes, action previews, confirmation only for', u'x',
     BUILT + u'The alerts readout (0.10.5-dev), `CompanyActionResult` refusal keys everywhere, and '
     u'confirmation on exactly the irreversible case — the deconstruct warning (0.12.4-dev). '
     u'Refusals are stated **before** the click as well as enforced after it.'),
    (u"Remap RimWorld's menus, tabs, and campaign views into the finished company-first", u' ',
     OPEN + u'**And it should be challenged before it is built.** Remapping Core’s own menus is '
     u'invasive, would fight every interface mod in the register, and no owner direction has asked '
     u'for it since. The twelve-pane tab is the company-first surface.'),
    (u'Add tutorial/guide, help glossary, keyboard/controller paths as appropriate', u' ',
     OPEN + u'This is queue item 7, the player-facing how-to, written **once** for the repo and '
     u'the site.'),
    (u'Create and integrate the approved original RimWorld-style Backrooms main-menu', u'x',
     BUILT + u'`Presentation/RimroomsMenuBackground.cs`. Original images are **the single declared '
     u'exception** to the no-new-art rule.'),
    (u'Integrate the slideshow through the verified 1.6 menu surface without redistributing', u'x',
     BUILT + u'No vanilla or DLC art is redistributed, and `MenuSlideshowEnabled` is a real '
     u'settings toggle that turns it off.'),
    (u'Eleven-pane Company Command, deep links, reason codes, native menu remap.', u'~',
     PART + u'**Twelve panes and reason codes: done.** Deep links partial; the native menu remap '
     u'is open and questioned on its own row above.'),
    (u'**Door gizmo for the deliberate-cross order, naming the refusal reason in place.**', u' ',
     OPEN + u'**Crossing itself works** — `RR_CrossPortal`, `PortalCrossingService`, ordered from '
     u'the Atlas pane — so this is a convenience and a readability gap, not a functional one. The '
     u'refusal keys it would print already exist in `PortalTraversalPolicy`.'),
    (u'Tutorial, glossary, keyboard paths, contrast/scale, localization completeness.', u' ',
     OPEN + u'With the how-to. Localization completeness is measurable now: '
     u'`check-keyed-strings.py` reports 1408 declared keys with zero unresolved references.'),
    (u'Slideshow integration review, additional menu images per shipped scenario.', u'~',
     PART + u'The slideshow ships. **Additional images per scenario are not authored**, and images '
     u'are the one place new art is permitted.'),
    (u'Validation sweep, invalid-state matrix, balance, release report, packaging.', u' ',
     OPEN + u'**Structurally requires a launch.** Balance in particular cannot be claimed: nothing '
     u'in this mod has ever been played.'),
]

s = io.open(PATH, encoding='utf-8').read()
tally = {'x': 0, '~': 0, ' ': 0}
for anchor, status, note in VERDICTS:
    found = None
    for prefix in (u'- [ ] ', u'  - [ ] ', u'   - [ ] '):
        target = prefix + anchor
        if target in s:
            assert s.count(target) == 1, 'anchor not unique: %r' % anchor[:60]
            found = (target, prefix)
            break
    assert found is not None, 'anchor not found: %r' % anchor[:70]
    target, prefix = found
    start = s.index(target)
    end = s.index(u'\n', start)
    row = s[start:end]
    body = row.split(u'] ', 1)[1]
    new_prefix = prefix.replace(u'[ ]', u'[%s]' % status)
    s = s[:start] + new_prefix + body + u' — ' + note + s[end:]
    tally[status] += 1

io.open(PATH, 'w', encoding='utf-8', newline='').write(s)
print('remaining blocks re-measured: %d built or superseded, %d partial, %d confirmed open'
      % (tally['x'], tally['~'], tally[' ']))
