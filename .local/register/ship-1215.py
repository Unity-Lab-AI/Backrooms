# -*- coding: utf-8 -*-
"""Ledger for 0.12.15-dev: the universe has factions in it."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def read(rel):
    return io.open(os.path.join(REPO, rel), encoding='utf-8').read()


def write(rel, s):
    io.open(os.path.join(REPO, rel), 'w', encoding='utf-8', newline='').write(s)
    print('updated %s' % rel)


def insert_before(rel, anchor, block):
    s = read(rel)
    assert anchor in s, '%s: anchor not found' % rel
    write(rel, s.replace(anchor, block + anchor, 1))


insert_before('CHANGELOG.md', u'## 0.12.14-dev', u"""## 0.12.15-dev - 2026-09-29 - the universe has factions in it

- **Seven organisations now exist in the world.** A federal oversight office that wants your paperwork, competing interests that want your figures, former staff who know where everything is, an acquisition crew that will just take it, industrial intelligence you may never see arrive, concerned citizens who noticed the trucks, and an independent press that wants to publish all of it.
- **All seven start neutral.** None of them is an enemy until your branch makes one. Hostility is earned by what you actually do.
- **None of them changes your world map.** They have people and intentions, not towns, so generating a world is exactly as it was before. This matters when you are running 294 other mods.
- **Nothing new was added to the game to build them.** Every person they can send is one RimWorld already ships, and every icon is one the base game already uses.

Full record: [the universe has factions in it](docs/implementation/UNIVERSE_FACTIONS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

""")

insert_before('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - the universe has factions in it (0.12.15-dev)

**Verbatim user quote:** *"lets start knocking out these todo items in droves thouroghly efficient and professionaally with out error"*

**The owner direction this closes, verbatim from 2026-09-28:** *"the factions should be the factions of the universe"*, *"so US government"*, *"other corporations trying to get propietary tech"*, *"ex employes disgruntleed"*, *"high tech theives"*, *"corporate spys and sbaatosh"*, *"concerned citizens.."*, *"and anything other type of factions along these lines that will increses the backrromms universe feeling"*, *"this is 1990's when this all starts"*.

### What shipped

**Seven `FactionDef`s** - the largest completely unbuilt owner direction, found by the 0.12.14-dev backlog audit. Six named by the owner plus one in the same vein.

### Files touched

`1.6/Defs/FactionDefs/RR_UniverseFactions.xml` (new), `tools/package-files.json`, `docs/implementation/UNIVERSE_FACTIONS_IMPLEMENTATION.md`, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj, and `proof-universe-factions.py` (new, the eighteenth).

### Closure notes

- **A `FactionDef` is the one new Def this project permits, and the permission is narrow.** The owner answered on 2026-09-28 that a faction is **world configuration rather than a physical gameplay Def**, provided it reuses existing pawn kinds and existing faction icon paths. The proof enumerates the **installed game** for both - invariant 19, never trust a remembered list - and a planted pawn kind or icon path this mod authored makes it fail.
- **The icon failure would otherwise have been invisible until runtime.** `ContentFinder` returns null for a missing texture, so a wrong `factionIconPath` loads clean and the faction simply has no icon. Nothing in the build would have said so.
- **NONE OF THE SEVEN GENERATES SETTLEMENTS**, and that is the decision that keeps this non-invasive. `settlementGenerationWeight` is 0 for all of them, `canMakeRandomly` is false and `requiredCountAtGameStart` is 1. **Seven settlement-generating factions would change every world map every player generates, alongside 294 other mods.** These are conspiratorial and institutional interest groups: they have people and intentions, not towns.
- **All seven begin neutral, and that was achieved by NOT setting something.** `FactionDef` has **no starting-goodwill field** - confirmed by decompiling the type rather than by memory - so a faction that is not `permanentEnemy` starts neutral through Core's own relation logic. Exactly the owner's answer: *all neutral, escalating from play*. The proof asserts the absence, because nothing looks wrong when a flag quietly appears.
- **Every faction can field both a peaceful and a combat group.** A faction that cannot arrive either way is a name on a list, and earning its hostility would change nothing observable - the same test invariant 136 applies to research unlocks.
- **The period is prose, not a field.** RimWorld has no year; `techLevel` Industrial is the 1990s in its vocabulary. The decade lives in how these organisations talk about themselves. The proof also asserts **no start grants spacer-tier content**, which is the measurable half of the owner's answer that the framing *"also constrains starting grants"* - research may still climb anywhere, so no start is dead-ended.
- **The owner's own wording was deliberately kept out of the def descriptions**, because the recorded row asked for exactly that. The proof searches the descriptions for the owner's phrasings and fails if any leaked in.
- **Five planted faults, five catches, clean on restore**: an authored pawn kind, an icon path Core does not ship, a settlement-generating faction, a faction that starts hostile, and the file dropped from the package allowlist.
- Build 0.12.15-dev, 173 C# files, **87 package files** (one new def file), **0 warnings, 0 errors**. **No C# changed.** Eight checkers pass, **eighteen** proofs exit zero. Assembly reproduced by two clean recompiles. **No game was launched, and nothing in this mod has ever been played.**

---

""")

s = read('docs/NOW.md')
pairs = [
    (u'| Published | **0.12.14-dev**.', u'| Published | **0.12.15-dev**.'),
    (u'## What shipped this session, 0.7.1 → 0.12.14',
     u'## What shipped this session, 0.7.1 → 0.12.15'),
    (u'| 0.12.14 | **The queue could not answer the question** — 155 backlog rows re-measured against the code; open rows 254 → 107. **No `FactionDef` exists at all** |',
     u'| 0.12.14 | **The queue could not answer the question** — 155 backlog rows re-measured against the code; open rows 254 → 107. **No `FactionDef` exists at all** |\n'
     u'| 0.12.15 | **The universe has factions in it** — seven, all neutral, **no settlements and no new content**. Closes the largest unbuilt owner direction |'),
    (u'| Build | **173 C# files, 86 package files**', u'| Build | **173 C# files, 87 package files**'),
    (u'| Proofs | **SEVENTEEN** in `.local/register/proof-*.py`.',
     u'| Proofs | **EIGHTEEN** in `.local/register/proof-*.py`.'),
    (u'7b. **Every proof (SEVENTEEN), by exit status:**', u'7b. **Every proof (EIGHTEEN), by exit status:**'),
    (u"   `live-effects`, `offer-routes`, `portal-footprint`, `remote-sites`, `request-generation`,\n"
     u"   `request-line`, `research-branches`, `spinup`, `starts`, `stranded-crew`, `tier-ladder`.",
     u"   `live-effects`, `offer-routes`, `portal-footprint`, `remote-sites`, `request-generation`,\n"
     u"   `request-line`, `research-branches`, `spinup`, `starts`, `stranded-crew`, `tier-ladder`,\n"
     u"   `universe-factions`."),
]
for old, new in pairs:
    assert old in s, 'NOW anchor missing: %r' % old[:60]
    s = s.replace(old, new, 1)

marker = u'190. **Say when a row cannot close without the owner.**'
idx = s.index(marker)
line_end = s.index(u'\n', idx)
s = (s[:line_end + 1] +
     u'191. **A `FactionDef` is world configuration, and that is the whole of the permission.** It '
     u'may reuse existing pawn kinds and existing icon paths and nothing else. **Enumerate the '
     u'installed game for both** — a `factionIconPath` Core does not ship loads clean and fails at '
     u'runtime, because `ContentFinder` returns null and the faction simply has no icon.\n'
     u'192. **`settlementGenerationWeight` 0 for anything this mod adds to the world.** Seven '
     u'settlement-generating factions would change every world map every player generates, '
     u'alongside 294 other mods. An interest group has people and intentions, not towns.\n'
     u'193. **Some correctness is achieved by NOT setting a field.** `FactionDef` has no '
     u'starting-goodwill field, so *all neutral* is the default and the risk is a flag quietly '
     u'appearing later. **Assert the absence**, because nothing looks wrong when it does.\n' +
     s[line_end + 1:])
write('docs/NOW.md', s)

# Close the thirteen faction rows.
t = read('docs/TODO.md')
BUILT = u' — **BUILT, 0.12.15-dev.** '
rows = [
    (u'**"this is 1990\'s when this all starts"**',
     u'`techLevel` Industrial is the 1990s in RimWorld\'s vocabulary, and the decade lives in how '
     u'the seven organisations talk about themselves. The proof also asserts **no start grants '
     u'spacer-tier content**.'),
    (u'**"the factions should be the factions of the universe"**', u'Seven `FactionDef`s ship.'),
    (u'**"so US government"**', u'`RR_Faction_Government` — the federal oversight office.'),
    (u'**"other corporations trying to get propietary tech"**',
     u'`RR_Faction_RivalCorporations` — competing interests.'),
    (u'**"ex employes disgruntleed"**', u'`RR_Faction_FormerStaff` — the former staff association, '
     u'and the only group on the list that has stood where your crews stand.'),
    (u'**"high tech theives"**', u'`RR_Faction_TechThieves` — the acquisition crew.'),
    (u'**"corporate spys and sbaatosh"**', u'`RR_Faction_Espionage` — industrial intelligence.'),
    (u'**"concerned citizens.."**', u'`RR_Faction_ConcernedCitizens`.'),
    (u'**"and anything other type of factions along these lines',
     u'`RR_Faction_Press` — the independent press, whose whole purpose is that other people find '
     u'out, which is the thing every other faction on the list is trying to prevent.'),
    (u'**"as all this needs to be defgault set in the game settup',
     u'All seven exist in every world at `requiredCountAtGameStart` 1 and **all begin neutral**, '
     u'which is the owner\'s own answer to what the per-scenario default should be. What differs '
     u'per scenario is what the branch then does.'),
    (u'**The seven named universe factions** as new `FactionDef`s',
     u'Six named plus one in the same vein. Every pawn kind and every icon path is one the '
     u'installed game already ships, enumerated rather than remembered, and fault-planted both ways.'),
    (u'**Per-scenario default faction setup**',
     u'All seven neutral in every start, per the owner\'s answer. Hostility is earned from saved '
     u'observable causes rather than declared per scenario.'),
    (u'**Period-plausible starting grants** for every start',
     u'Asserted by the proof: **no start grants spacer-tier content** (no Glitterworld, bionic, '
     u'archotech, charge weapons, power armour, persona or luciferium). Research may still climb '
     u'anywhere, so no start is dead-ended.'),
]
closed = 0
for anchor, note in rows:
    target = u'- [ ] ' + anchor
    assert target in t, 'faction row not found: %r' % anchor[:50]
    assert t.count(target) == 1, 'faction row not unique: %r' % anchor[:50]
    start = t.index(target)
    end = t.index(u'\n', start)
    body = t[start:end].split(u'] ', 1)[1]
    t = t[:start] + u'- [x] ' + body + BUILT + note + t[end:]
    closed += 1
write('docs/TODO.md', t)
print('closed %d faction rows' % closed)
