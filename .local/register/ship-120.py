# -*- coding: utf-8 -*-
"""Ledger for 0.12.0-dev. Every insertion re-includes its anchor (invariant 144)."""
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


insert_before('CHANGELOG.md', u'## 0.11.9-dev', u"""## 0.12.0-dev - 2026-09-29 - you are already in

- **The third start: solo or group, inside.** You begin in the Backrooms with what you were carrying. No gate, no company, no research, and nobody looking for you.
- **One to five people, your choice.** Groups have been known to end up in together. Set it up natively or with Prepare Carefully or Character Editor, the same as the other two starts.
- **The whole map is the Backrooms**, wall to wall. Solid rock between the rooms, and a roof that does not come off however far you dig.
- **There is no power and there are no lights.** Nobody wired the place. You have three glow pods and whatever else you brought.
- **No money, no wages, no overhead** - there is no company here to run an account.
- **All three starts are now in**, and only Async Industries begins in contact with the corporation. The other two have no clean-up team and no deliveries until they earn one.

Full record: [you are already in](docs/implementation/SOLO_GROUP_START_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

""")

insert_before('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - the solo/group start (0.12.0-dev)

**Verbatim user quote:** *"yup get to it"*

**Owner direction this closes, verbatim:** *"remember the other one is solo/group start.. group have been known to end up together inside so leets use the in backrooms start to be 1-5 pawns player settable with normal set up or edb prepare carefully mod and or character editor"*

### What shipped

The **third and last** of the chart's starts. The map itself is a Backrooms coordinate, wall to wall. One to five people through Core's own config page. No company, no gate, no research, no power, no money.

### Files touched

`src/RimroomsAsyncIndustries/Scenario/GenStep_InsideStart.cs` (new), `Scenario/RimroomsStartDef.cs`, `Generation/GenStep_BackroomsDestination.cs` (shell extracted), `Mod/.../Defs/RimroomsStartDefs/RR_Starts.xml`, `Mod/.../Defs/ScenarioDefs/RR_Scenarios.xml`, `Mod/.../Defs/MapGeneratorDefs/RR_BackroomsGeneration.xml`, `docs/implementation/SOLO_GROUP_START_IMPLEMENTATION.md`, `CHANGELOG.md`, `README.md`, `docs/TODO.md`, `docs/NOW.md`, `About.xml`, the csproj, and the starts proof.

### Closure notes

- **No Harmony and no trick.** `Game.InitNewGame` picks `initData.mapGeneratorDef ?? settlement.MapGeneratorDef`, `GameInitData.mapGeneratorDef` is a public field, and `ScenPart_RimroomsStart.PreMapGenerate` has assigned it from the start def since the Async headquarters was built. A start that opens inside simply names a different generator.
- **The coordinate SHELL is now shared** between the destination generator and the inside start - void terrain, `RoofRockThick` over every cell, rock fill, carved rooms, corridors, walls, doors. That block carries **invariant 13**, and a second copy would have drifted the promise that you cannot dig your way into open sky. Same reasoning as the `AnomalyEventService` re-scoping one checkpoint earlier.
- **Three absences, each deliberate and each cheaper than a half-built version:** no power or lights, no gate anchor or return cell, and the coordinate is not registered in the branch atlas. Reload safety comes from the map being saved whole, which is what `SCENARIOS.md` actually requires.
- **Zero funding, wages and overhead** - not a balance call. There is no company, so nobody is paid and nothing is billed.
- **The starts proof learned a second shape.** An inside start has no layout, so it asserts what is true instead: no declared facility, the coordinate map size, a generator the mod ships, and a genstep class that resolves. **That last one fails as an ordinary RimWorld colony rather than a crash**, with the scenario description still promising the Backrooms.
- Build 0.12.0-dev, 168 C# files, 86 package files, **0 warnings, 0 errors**. Eight checkers pass, seven proofs hold, the starts proof fault-planted four more ways. Assembly reproduced by two clean recompiles. **No game was launched.**

---

""")

s = read('docs/NOW.md')
pairs = [
    (u'| Published | **0.11.9-dev**.', u'| Published | **0.12.0-dev**.'),
    (u'| Build | **167 C# files, 86 package files**, zero warnings, zero errors |',
     u'| Build | **168 C# files, 86 package files**, zero warnings, zero errors |'),
    (u'`490158EDEF1F88F2E060E70E127567C9DB4351C988021C5B765650FDA46661CE`',
     u'`C6810C8DD2E0B422B4B5F3BBF1CA05E178B8AC0F9D60FAF16D84598E7CB46AEB`'),
    (u'## What shipped this session, 0.7.1 → 0.11.9',
     u'## What shipped this session, 0.7.1 → 0.12.0'),
    (u'| 0.11.9 | **A shop with a door in the back** — the Store start; three new-game crashes caught by a new proof |',
     u'| 0.11.9 | **A shop with a door in the back** — the Store start; three new-game crashes caught by a new proof |\n'
     u'| 0.12.0 | **You are already in** — the solo/group start; the map itself is a coordinate. **All three starts ship.** |'),
]
for old, new in pairs:
    assert old in s, old[:70]
    s = s.replace(old, new, 1)

start = s.index(u'1. **The solo/group start.**')
end = s.index(u'2. **Research tiers 3–4**')
s = s[:start] + u"""1. **Research tiers 3–4** — remote and deep operations. The band meanings are in
   `docs/CAMPAIGN_CHART.md` §3.1: tier 3 is *"support more than one site; work beyond
   headquarters"*, tier 4 is *"combine known techniques; extend reach"*. **Check every knob
   against its real read site before building** — invariant 136, which deleted three of the
   seven tier-2 unlocks before a line was written.
""" + s[end:]
s = s.replace(u'2. **Research tiers 3–4** — remote and deep operations.\n', u'', 1)

marker = u'148. **Exactly one start begins in corporation contact.**'
idx = s.index(marker)
line_end = s.index(u'\n', idx)
s = (s[:line_end + 1] +
     u'149. **Core already lets a scenario choose the starting map’s generator.** '
     u'`Game.InitNewGame` reads `initData.mapGeneratorDef ?? settlement.MapGeneratorDef`, and '
     u'`GameInitData.mapGeneratorDef` is a public field. **No Harmony is needed to open a game '
     u'anywhere**, and this mod had already been assigning it from the start def.\n'
     u'150. **Share the half that carries the promises.** The coordinate shell — rock to every '
     u'edge, `RoofRockThick` over every cell, rooms carved out — is one implementation used by '
     u'both generators, because invariant 13 lives inside it. The furniture differs; the shell '
     u'never may. Same reasoning as the anomaly effects at 0.11.8.\n'
     u'151. **A `workerClass` or `genStep Class` that does not resolve fails as ORDINARY '
     u'BEHAVIOUR, not as a crash.** A missing genstep gives the player a normal colony while the '
     u'description promises the Backrooms. Assert that every class named in XML exists in source.\n' +
     s[line_end + 1:])
write('docs/NOW.md', s)

swap('docs/TODO.md',
     u'- [ ] **"remember the other one is solo/group start"** - the next checkpoint.',
     u'- [x] **"remember the other one is solo/group start"** - SHIPPED 0.12.0-dev.')
swap('docs/TODO.md',
     u'- [ ] **"group have been known to end up together inside so leets use the in backrooms start to be 1-5 pawns player settable"**',
     u'- [x] **"group have been known to end up together inside so leets use the in backrooms start to be 1-5 pawns player settable"** - SHIPPED.')
swap('docs/TODO.md',
     u'- [ ] **"with normal set up or edb prepare carefully mod and or character editor"**',
     u'- [x] **"with normal set up or edb prepare carefully mod and or character editor"** - SHIPPED.')
