# -*- coding: utf-8 -*-
"""Ledger for 0.12.2-dev."""
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


insert_before('CHANGELOG.md', u'## 0.12.1-dev', u"""## 0.12.2-dev - 2026-09-29 - the way out was already there

- **The solo or group start now has a guaranteed way out, from the first tick.** A door on the surface, connected to the level you wake up in. Nobody built it and nobody knows who did.
- **You still start inside.** Your people and everything they were carrying are in the Backrooms before you see anything; the surface is a bare tile with one small concrete shell on it, and that shell is where you will come out.
- **Nothing is prepared for you up there.** No power, no furniture, no stockpile. Everything a facility needs, you build.
- **Using the way out is entirely your choice.** It is permanently open and it does not ask anything of you. A group that would rather stay down there and dig is playing correctly.

Full record: [the way out was already there](docs/implementation/SOLO_GROUP_EXIT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

""")

insert_before('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - the solo/group exit (0.12.2-dev)

**Verbatim user quote:** *"sweet! im excited you are doing such a great job i think and hope, till we finish we wont know"*

**Owner answer at the exit-route fork, verbatim:** *"Two maps at start, coordinate is real (Recommended)"*

**Owner direction this closes, verbatim:** *"and remember the solo/group start in a backroom needs to 100% have a exit to map natural portal on their first backrroms level with natural portals deeper to an extent till they would need to buidl theri own gate"*

### What shipped

The guaranteed exit. The solo/group start generates two maps: an ordinary surface map holding one small concrete shell with one door, and a **real Backrooms coordinate** beside it. The people and their supplies begin inside, and an ordinary `Emergence` connection is registered at the opening - not found by a survey draw.

### Files touched

`src/RimroomsAsyncIndustries/Scenario/SoloGroupOpening.cs` (new), `Scenario/RimroomsStartDef.cs`, `Scenario/ScenPart_RimroomsStart.cs`, `Scenario/GenStep_InsideStart.cs` (**retired, archived**), `Mod/.../Defs/RimroomsStartDefs/RR_Starts.xml`, `Mod/.../Defs/MapGeneratorDefs/RR_BackroomsGeneration.xml`, keyed strings, `docs/implementation/SOLO_GROUP_EXIT_IMPLEMENTATION.md`, `historical-content/0.12.0-dev/RETIRED_GENSTEP_INSIDESTART.md`, `CHANGELOG.md`, `README.md`, `docs/TODO.md`, `docs/NOW.md`, `About.xml`, the csproj, and the starts proof.

### Closure notes

- **A hard constraint decided the architecture, and it was found by reading rather than assumed.** `RimroomsPortalNetwork.Register` requires the Backrooms side of every connection to be a `RimroomsDestinationMapParent` with a matching `CoordinateRecord`. The starting map can never be one, because `Game.InitNewGame` generates it for a player `Settlement`. **0.12.0-dev's design was the thing in the way**, and the alternative was widening the validation every existing gate depends on. Taken to the owner rather than decided quietly.
- **The order of the opening is its safety.** The party is moved inside **last**, so a failure anywhere above leaves everybody safely on the surface rather than sealed in a coordinate with no registered exit - the exact trap invariant 28 forbids. Asserted, and a plant that reorders it fails immediately.
- **`GenStep_InsideStart` and `RR_InsideStart` retired and archived verbatim** with the reason (invariant 37). `BuildShell` stays: it is the destination generator's own shell and the single implementation carrying invariant 13.
- **`check-keyed-strings.py` caught two refusal keys I invented** - `RR_Portal_InvalidState` and `RR_Portal_LocalThresholdUnavailable`. The real prefix is `RR_PortalAddress_`, built by the service's own `Refuse` helper. A refusal key that does not exist shows the player the raw key.
- Build 0.12.2-dev, 168 C# files, 86 package files, **0 warnings, 0 errors**. Eight checkers pass, seven proofs hold. Assembly reproduced by two clean recompiles. **No game was launched, and nothing here has been played.**

---

""")

s = read('docs/NOW.md')
pairs = [
    (u'| Published | **0.12.1-dev**.', u'| Published | **0.12.2-dev**.'),
    (u'`62935DFB887DED243394A1A6C5440ED3DE39F364AF055AAB17E5CF8491FCFA57`',
     u'`D9090678DBFBABFB02B144A9E0C23777E23680D2164D3369742D2BE7BB26421F`'),
    (u'## What shipped this session, 0.7.1 → 0.12.1',
     u'## What shipped this session, 0.7.1 → 0.12.2'),
    (u'| 0.12.1 | **The free doors run out** — found doors stop at depth 3; deeper needs a built gate. Corrects 0.12.0 |',
     u'| 0.12.1 | **The free doors run out** — found doors stop at depth 3; deeper needs a built gate. Corrects 0.12.0 |\n'
     u'| 0.12.2 | **The way out was already there** — the guaranteed exit; two maps, a real coordinate, `GenStep_InsideStart` retired |'),
]
for old, new in pairs:
    assert old in s, old[:70]
    s = s.replace(old, new, 1)

start = s.index(u"1. **The guaranteed exit on the solo/group start's first level.**")
end = s.index(u'2. **The solo/group tutorial line.**')
s = s[:start] + u"""1. **Natural gates that cannot be destroyed or moved, and building around a portal.** Owner
   direction, verbatim: *"natruals can not be destoryed or moved, so one can technically build a
   roomm directly on the other side of the portal door and it shouldnt interfere with the portal
   transition to the seeded backrooms"*.
   - **Check first, do not assume.** A natural gate is a Core `Door` today: it has hit points and
     a deconstruct designation, so a player can very probably destroy one — which would break a
     connection the design calls **permanently open**.
   - **The build-around half is the one most likely broken today.** Every threshold is validated
     by `PortalAddressService.UsableThreshold(door, approach, map)` against an **approach cell**,
     and a wall built on that cell would make a permanently open gate refuse. A player who builds
     a proper airlock around their own gate must not lose it by doing so.
   - **An open question before any of it is built:** whether the approach cell is re-derived when
     the local geometry changes, or whether a portal door's approach cell simply cannot be built
     on — and if the latter, how the player is told. Both readings are defensible, so invariant
     134 says ask.
""" + s[end:]
write('docs/NOW.md', s)
