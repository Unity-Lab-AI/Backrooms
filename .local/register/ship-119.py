# -*- coding: utf-8 -*-
"""Ledger for 0.11.9-dev. Every insertion re-includes its anchor (invariant 144)."""
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


def swap(rel, old, new):
    s = read(rel)
    assert old in s, '%s: %r not found' % (rel, old[:60])
    write(rel, s.replace(old, new, 1))


# --------------------------------------------------------------------------- CHANGELOG
insert_before('CHANGELOG.md', u'## 0.11.8-dev', u"""## 0.11.9-dev - 2026-09-29 - a shop with a door in the back

- **A second start: the Furniture and Knickknack Store.** Three ordinary people, a sales floor, a stockroom, two hundred silver in the till, and a door in the back room that should not be there.
- **No corporation, no research, and no rescue.** Nobody is watching this place. There is no clean-up team and no unsolicited delivery until you reach Async Industries, and reaching them at all is the achievement.
- **Async Industries now starts with the research an authorised branch would already have** - the first rung of the gate ladder and the entry project of all seven branches. It also means something can follow a crew out from the very first opening.
- **The threshold in the shop's back room is an ordinary door**, because that is what every gate in this mod is until somebody designates it. What it becomes is up to you.
- **Both starts stay fully editable** with native setup, Prepare Carefully or Character Editor.

Full record: [a shop with a door in the back](docs/implementation/STORE_START_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

""")

# --------------------------------------------------------------------------- FINALIZED
insert_before('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - the Store start (0.11.9-dev)

**Verbatim user quote:** *"continue, that all sounds well"*

**Owner answers at the fork, verbatim:** *"All seven tier-0 roots"* and *"option 1 and remember the other one is solo/group start.. group have been known to end up together inside so leets use the in backrooms start to be 1-5 pawns player settable with normal set up or edb prepare carefully mod and or character editor"*

### What shipped

The **Furniture and Knickknack Store** start: 50x50 shop, three ordinary people, 200 silver in the till, an ordinary door in the back room, **no corporation contact and no completed research**. And a correction to Async Industries, which listed nothing finished despite the direction it was written under.

### Files touched

`Mod/.../Defs/RimroomsStartDefs/RR_Starts.xml`, `Mod/.../Defs/ScenarioDefs/RR_Scenarios.xml`, `src/RimroomsAsyncIndustries/Scenario/RimroomsStartDef.cs`, `docs/implementation/STORE_START_IMPLEMENTATION.md`, `CHANGELOG.md`, `README.md`, `docs/TODO.md`, `docs/NOW.md`, `About.xml`, the csproj, and a seventh proof.

### Closure notes

- **Async began with zero completed research**, contradicting *"Async industries starts with this tech research and other basic gate techs it needs to operate"*. Asked rather than guessed; the owner chose all seven tier 0 roots plus `RR_GateTelemetry`. **Consequence named before the choice and taken knowingly:** Telemetry puts `PortalWindowTier` at 1, so Async is exposed to incursion from its first opening.
- **`proof-starts.py` found three new-game crashes in a layout that built with zero warnings** - a 2x2 `WoodFiredGenerator` and a `Battery` sitting on the stockroom's south wall, then a shelf colliding with the moved generator. `GenStep_Headquarters` throws on each, and no checker can see it. Building sizes are read from Core's own `ThingDef`s so a 1x1 assumption cannot hide a 2x2.
- **It also asserts the failure that does NOT throw:** a sealed room. The map generates, the colony starts, and part of the shop can never be entered. Flood-fill from the arrival cell; removing one door fails it.
- **An assertion was wrong and the source was right, for the THIRD time this session.** The wall rule said a wall must not land inside another room's interior - which would have failed Async, which ships and works. The generator throws only on an *edifice* collision. Restated as: two rooms must not share a wall cell.
- **`ConfigErrors` demanded exactly five roles**, with an Async-specific message, as a rule for every start. The Store opens with three and the solo/group start with as few as one. Relaxed to one to five.
- Build 0.11.9-dev, 167 C# files, 86 package files, **0 warnings, 0 errors**. Eight checkers pass, seven proofs hold, the new one fault-planted four ways. Assembly reproduced by two clean recompiles. **No game was launched.**

---

""")

# --------------------------------------------------------------------------- NOW
s = read('docs/NOW.md')
pairs = [
    (u'| Published | **0.11.8-dev**.', u'| Published | **0.11.9-dev**.'),
    (u'`3E7B151603CFA38B2066DD5F7DD57EB1DE1EE60317E3A2634D12F452FB05C528`',
     u'`490158EDEF1F88F2E060E70E127567C9DB4351C988021C5B765650FDA46661CE`'),
    (u'| Proofs | **six** in `.local/register/proof-*.py`, all holding.',
     u'| Proofs | **seven** in `.local/register/proof-*.py`, all holding.'),
    (u'## What shipped this session, 0.7.1 → 0.11.8',
     u'## What shipped this session, 0.7.1 → 0.11.9'),
    (u'| 0.11.8 | **The storyteller finally knows this mod exists** — the first two `IncidentDef`s; no `StorytellerDef`, now asserted |',
     u'| 0.11.8 | **The storyteller finally knows this mod exists** — the first two `IncidentDef`s; no `StorytellerDef`, now asserted |\n'
     u'| 0.11.9 | **A shop with a door in the back** — the Store start; three new-game crashes caught by a new proof |'),
]
for old, new in pairs:
    assert old in s, old[:70]
    s = s.replace(old, new, 1)

start = s.index(u'1. **The Store and Solo/Group starts.**')
end = s.index(u'2. **Research tiers 3–4**')
s = s[:start] + u"""1. **The solo/group start.** Owner direction at the fork, verbatim: *"remember the other one is
   solo/group start.. group have been known to end up together inside so leets use the in
   backrooms start to be 1-5 pawns player settable with normal set up or edb prepare carefully
   mod and or character editor"*. It begins **inside a generated coordinate**, which is unlike
   both surface starts: the coordinate has to be created, seeded and registered at new-game so a
   reload does not silently make a different destination. **Neither it nor the Store begins in
   corporation contact**, and as of 0.11.7–0.11.9 that absence is a real mechanical difference.
""" + s[end:]

marker = u'144. **A ledger patch must INSERT, never replace.**'
idx = s.index(marker)
line_end = s.index(u'\n', idx)
s = (s[:line_end + 1] +
     u'145. **An assertion written from what the code LOOKS like is a guess; one written from '
     u'what the code THROWS on is a fact.** All three wrong assertions this session came from the '
     u'first kind — the depth rule, the incursion word-search, and the wall rule that would have '
     u'failed the headquarters that ships and works. See 130, 142.\n'
     u'146. **A start layout is a new-game crash nothing else can see.** `GenStep_Headquarters` '
     u'throws on a wall collision, a door with no wall, or a bad rectangle, and the build and all '
     u'eight checkers pass regardless. **Read building sizes from Core’s own `ThingDef`s** — a '
     u'2×2 generator on a 1×1 assumption put three crashes in a layout that built clean.\n'
     u'147. **A sealed room does not throw.** The map generates and part of it can never be '
     u'entered, forever, silently. Flood-fill every start from its arrival cell.\n'
     u'148. **Exactly one start begins in corporation contact.** Async Industries. The other two '
     u'earn it, and until they do there is no clean-up team and no courier. That absence is what '
     u'makes those openings frightening, and it is asserted.\n' +
     s[line_end + 1:])
write('docs/NOW.md', s)

# --------------------------------------------------------------------------- TODO
insert_before('docs/TODO.md', u'\n### Research tier 2 - what the sweep changed before a line was written', u"""
**Verbatim owner answers (2026-09-29), at the starts fork:** *"All seven tier-0 roots"* / *"option 1 and remember the other one is solo/group start.. group have been known to end up together inside so leets use the in backrooms start to be 1-5 pawns player settable with normal set up or edb prepare carefully mod and or character editor"*

- [x] **"All seven tier-0 roots"** - SHIPPED 0.11.9-dev. Async Industries listed `<completedProjects />`, nothing finished, which contradicted *"Async industries starts with this tech research and other basic gate techs it needs to operate and begin researching and gate operations at basic levels"*. It now begins with all seven tier 0 branch roots **plus `RR_GateTelemetry`**. Named before the choice and taken knowingly: Telemetry puts `PortalWindowTier` at 1, the floor at which something may follow a crew out, so **Async is exposed to incursion from its first opening**.
- [x] **The Store start** - SHIPPED 0.11.9-dev. 50x50 shop, three ordinary people, 200 silver in the till, an ordinary door in the back room, **no corporation contact and no completed research**.
- [ ] **"remember the other one is solo/group start"** - the next checkpoint. It is `lone_survivor` by stable scenario ID and **solo/group** by name.
- [ ] **"group have been known to end up together inside so leets use the in backrooms start to be 1-5 pawns player settable"** - a `ScenPart_ConfigPage_ConfigureStartingPawns` with a default the player may raise to five. The fiction is that a group can be taken together.
- [ ] **"with normal set up or edb prepare carefully mod and or character editor"** - already the pattern both shipped starts follow: the native config page goes first, every starting item is a native `ScenPart_StartingThing_Defined`, and the mod's own scen parts are `visible=false` and carry only the layout and the branch. Register row **[85] EdB Prepare Carefully** and Character Editor see an ordinary scenario.
""")
