# -*- coding: utf-8 -*-
"""Ledger for 0.12.3-dev."""
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


insert_before('CHANGELOG.md', u'## 0.12.2-dev', u"""## 0.12.3-dev - 2026-09-29 - a portal is its own door cell

- **You can build, mine and explore right behind a gate without affecting it.** A portal takes up its own doorway and nothing else: no reserved space, no protected circle, no invisible claim on your map.
- **A real bug is fixed.** Walling one particular cell beside a gate used to break that gate permanently, silently, for the rest of the save - even with three other perfectly walkable cells around the same door. Build your airlock; the gate keeps working.
- **Seal a door in on all four sides and it stops working**, exactly like any other door you wall off. That much has always been fair.
- **A crossing in progress is never disturbed.** If somebody is mid-transfer the gate waits before adjusting anything, because losing a colonist in a doorway is not a risk worth taking.
- **The only placement rules near a gate are the equipment's own** - a console or a bound battery has to be within reach. That is the equipment needing to be close, not the gate claiming ground.

Full record: [a portal is its own door cell](docs/implementation/PORTAL_FOOTPRINT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

""")

insert_before('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - the portal footprint (0.12.3-dev)

**Verbatim user direction:** *"and technically the way the gate works and make a portal when placing it on your map or having a natural one(natruals can not be destoryed or moved, so one can technically build a roomm directly on the other side of the portal door and it shouldnt interfere with the portal transition to the seeded backrooms"*

**And the clarification, verbatim:** *"if u get what i mean .. in the real world maps the portals dont extend into the real world environment so in the real world you can mine and build and explore directly behind the gates with out actually effecting the gate, unless there is connected need requipremd equipemnet directly required placemnets behind the pgate doors.. so yeah you get it"*

### What shipped

`PortalEndpointRecord.TryRepairApproach()`, called from `RimroomsPortalNetwork.Availability` when no crossing is in flight. A portal is its own door cell and reserves nothing; building beside a gate no longer breaks it.

### Files touched

`src/RimroomsAsyncIndustries/Portals/PortalConnectionRecord.cs`, `Portals/RimroomsPortalNetwork.cs`, `docs/implementation/PORTAL_FOOTPRINT_IMPLEMENTATION.md`, `CHANGELOG.md`, `README.md`, `docs/TODO.md`, `docs/NOW.md`, `About.xml`, the csproj, and an eighth proof.

### Closure notes

- **A real defect, invisible from any single file.** `PortalEndpointRecord` snapshots the approach cell at registration and `Availability` validated that saved cell forever, so **a wall on one cell beside a gate reported `Obstructed` for the life of the save** - with up to three other walkable cells beside the same door, and no error or message. Both files look correct alone; the bug lives only in the relationship. Same failure family as the beacon that could never fire and the tier ladder that could never be climbed.
- **The anchor cell is deliberately NOT refreshed.** That snapshot is what stops a moved door silently redirecting a saved route. Refreshing both would have traded one silent failure for a worse one, and the proof asserts the asymmetry.
- **The repair is skipped while a crossing is in flight**, because a `PortalCrossingReceipt` stores the approach cells it began with and `ConnectionStillMatches` refuses to continue if they changed - the guard that stops a transfer losing a pawn (invariant 55). **The naive fix, re-deriving live everywhere, would have quietly weakened the most safety-critical system in the mod.** Finding every read site before changing the value is the only reason it did not.
- **An eighth proof**, which also enforces a forward-looking rule: no portal source may contain `ReserveCell`, `ClaimRadius`, `portalRadius`, `ProtectedRadius` or `ReservedCells`. If one ever appears, somebody has started projecting the gate onto the map.
- **Still owed:** *"natruals can not be destoryed or moved"*. Core decides destructibility at the **def** level, and this mod may not change that because it would make every door in every colony indestructible for every player and every other mod. Damage can be absorbed per-instance via the vanilla `PostPreApplyDamage` comp hook; **deconstruction has no comp-level veto**, and the three honest options are all defensible - so it is queued with the question attached rather than guessed at (invariant 134).
- Build 0.12.3-dev, 169 C# files, 86 package files, **0 warnings, 0 errors**. Eight checkers pass, eight proofs hold. Assembly reproduced by two clean recompiles. **No game was launched, and nothing here has been played.**

---

""")

s = read('docs/NOW.md')
pairs = [
    (u'| Published | **0.12.2-dev**.', u'| Published | **0.12.3-dev**.'),
    (u'`D9090678DBFBABFB02B144A9E0C23777E23680D2164D3369742D2BE7BB26421F`',
     u'`826C21158ECB93979E2D89FEDBFB8FFC9EC4D825C439215F14A9B3A3D73AC46D`'),
    (u'| Proofs | **seven** in `.local/register/proof-*.py`, all holding.',
     u'| Proofs | **eight** in `.local/register/proof-*.py`, all holding.'),
    (u'| Build | **168 C# files, 86 package files**, zero warnings, zero errors |',
     u'| Build | **169 C# files, 86 package files**, zero warnings, zero errors |'),
    (u'## What shipped this session, 0.7.1 → 0.12.2',
     u'## What shipped this session, 0.7.1 → 0.12.3'),
    (u'| 0.12.2 | **The way out was already there** — the guaranteed exit; two maps, a real coordinate, `GenStep_InsideStart` retired |',
     u'| 0.12.2 | **The way out was already there** — the guaranteed exit; two maps, a real coordinate, `GenStep_InsideStart` retired |\n'
     u'| 0.12.3 | **A portal is its own door cell** — a wall beside a gate no longer bricks it; eighth proof |'),
]
for old, new in pairs:
    assert old in s, old[:70]
    s = s.replace(old, new, 1)

start = s.index(u'1. **Natural gates that cannot be destroyed or moved, and building around a portal.**')
end = s.index(u'2. **The solo/group tutorial line.**')
s = s[:start] + u"""1. **Natural gates that cannot be destroyed or moved.** Owner, verbatim: *"natruals can not be
   destoryed or moved"*. The **build-around half shipped in 0.12.3**; this is the rest.
   - **Core decides destructibility at the def level** — `def.destroyable`,
     `def.building.IsDeconstructible` — and this mod **may not change those**, because it would
     make every door in every colony indestructible for every player and every other mod.
   - **Damage is solvable per-instance**: `ThingComp.PostPreApplyDamage(ref DamageInfo, out bool
     absorbed)` is a vanilla comp hook and these doors already carry this mod's comps.
   - **Deconstruction has no comp-level veto.** Three defensible options: let the designation
     happen and re-place the door; refuse the crossing afterwards and explain; or accept that a
     player who deliberately deconstructs their own natural gate has closed it. **Ask** — invariant
     134.
""" + s[end:]

marker = u'154. **Open-ended is a constraint on the content, not a mood.**'
idx = s.index(marker)
line_end = s.index(u'\n', idx)
s = (s[:line_end + 1] +
     u'155. **A portal is its own door cell and reserves nothing.** No radius, no claimed cells, no '
     u'protected zone. Owner, verbatim: *"in the real world you can mine and build and explore '
     u'directly behind the gates with out actually effecting the gate"*. The only placement rules '
     u'near a gate belong to **linked equipment**, which has a reach of its own. Enforced by '
     u'`proof-portal-footprint.py`, including a banned-name check.\n'
     u'156. **A snapshot and a live check, in two different files, is a silent failure waiting.** '
     u'The approach cell was frozen at registration and validated forever; a wall on it bricked a '
     u'gate for the life of the save. **Both files read correctly alone.** When a value is '
     u'snapshotted, ask what happens when the world moves under it.\n'
     u'157. **Find every read site before changing a shared value.** Re-deriving the approach cell '
     u'live everywhere — the obvious fix — would have tripped the crossing receipt’s equality '
     u'guard, which is what stops a transfer losing a pawn. The repair is skipped while a crossing '
     u'is in flight because the read sites were enumerated first.\n' +
     s[line_end + 1:])
write('docs/NOW.md', s)
