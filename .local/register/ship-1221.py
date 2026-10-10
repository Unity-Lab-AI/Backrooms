# -*- coding: utf-8 -*-
"""Ledger for 0.12.21-dev: a way out into the world."""
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


insert_before('CHANGELOG.md', u'## 0.12.20-dev', u"""## 0.12.21-dev - 2026-09-29 - a way out into the world

- **You can now get out of the Backrooms without having marked a door first.** Before this, a way out could only ever arrive at a door you had already marked back home - and if you had not marked one, the survey quietly turned the way out into a way *deeper*. A branch with nothing marked could never get out at all.
- **A way out now leads somewhere on the world map you do not own.** Walk through, and if the company can take on another place, that tile becomes yours and your crew is standing in it. If you are already running as many places as you can, they come out as a caravan and make their own way from there.
- **Five places is the limit**, counting the Backrooms level you are standing in and every tile you have claimed this way - and if you have set your own colony limit lower than that, yours wins.
- **Nobody can be taken from you by any of this.** A gate closing on a crew, a window running out, and crossing a gate all still leave your people yours. Walking out is something you click, and the crew stays yours on the other side.

Full record: [a way out into the world](docs/implementation/WORLD_EXIT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

""")

insert_before('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - a way out into the world (0.12.21-dev)

**Verbatim user quotes, in order:** *"okay and remember test cases arnt being worried about right now we are trying to get the build complete so we can test"*, then the owner decision *"Build it - a player caravan is still yours"*, then *"but at that not a player can have up to five maps if settings are right so lets have that 5 map count be universal max for back rooms main map and claiming maps where u pop out and anything over 5 maps defaults to caravans"*.

### What shipped

The last genuinely unbuilt piece of the portal topology: **a way out that leads to a world tile the branch does not hold**, with two outcomes decided by a five-map cap.

### Files touched

`Portals/WorldExit.cs` (new), `Portals/NaturalFrontierService.cs`, `Portals/CompRimroomsEmergence.cs`, `Company/RimroomsCampaignComponent.cs`, `1.6/Languages/English/Keyed/RR_Portals.xml`, `docs/implementation/WORLD_EXIT_IMPLEMENTATION.md`, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj, and `proof-world-exit.py` (new, the twenty-first).

### Closure notes

- **THE OWNER OVERRULED MY OWN CAUTION, AND WAS RIGHT TO.** I had parked this because it moves pawns between maps and cannot be verified without a launch. *"test cases arnt being worried about right now we are trying to get the build complete so we can test"* - unverifiable-without-a-launch is not a reason to slow the build. It is built.
- **THE GAP WAS WORSE THAN THE ROW SAID.** The row described a missing feature. The reality was a **dead end**: `TryRecordWayOut` required a marked anchor on an owned map, and with nothing marked it returned null, so the draw that said *"this leads out"* silently produced a way **deeper** instead. A branch with no marked door could never find a way out **at all** - worst for exactly the player least equipped for it.
- **A CARAVAN, NOT A NEW WORLD OBJECT - and the register's `trace` column is what settled that.** Querying `RR-OUT` grouped the four Settled transport mods that bear on this exact feature: Carryalls intercontinental transport, Giddy-Up 2, Pack Mules Extended, Alpha Vehicles Age of Sail. **All four already integrate with caravans; none integrates with a bespoke world object of ours.** Core already has *"people standing on a tile you do not own"*. Nothing in the `family` column would have grouped those four together.
- **THE GUARANTEE CONFLICT WAS REAL AND WAS THE OWNER'S TO SETTLE.** Forming any caravan calls `PassToWorld`, and the stranded-crew guarantee says no gate source ever may, because *"a pawn in the world pool is alive and no longer the player's"*. I stopped and asked rather than deciding. **Owner decision: build it, because a player caravan is still yours.** And I said plainly that the proof only watched `Gate/*.cs`, so shipping this in `Portals/` would have passed on a **directory technicality** - which would have been evading the guarantee, not honouring it.
- **In the event our source gained NO new `PassToWorld` call at all.** The only route is inside Core's own `ExitMapAndCreateCaravan`. Our one direct call is pre-existing and releases a **declined job applicant**, who was never the player's. The proof asserts that the only caller in our source is that one, that gate sources and traversal still never call it, and that the world exit never calls it directly.
- **THE OWNER'S FIVE-MAP CAP IMPROVED THE DESIGN RATHER THAN CONSTRAINING IT.** Under the cap the tile is **claimed** through Core's own `SettleUtility.AddNewHome` and the crew walks onto a new map - **which never touches `PassToWorld` at all**, so the narrowed guarantee is not even reached until somebody already holds five maps. At or over it, a caravan. Two gates and **the stricter wins**: ours is five counting the coordinate they are standing in, the player's is `Prefs.MaxNumberOfPlayerSettlements` read through Core's own limit. **Somebody who set that to one meant it**, and this mod does not get to overrule a setting the player chose.
- **Nobody can be lost.** The claimed map is generated **before** any pawn is despawned, so a failure means nothing has moved; a failed spawn puts that pawn back where it stood. Prisoners, slaves and the downed are never taken - invariant 17, and somebody unconscious on the floor is not walking anywhere. Only the player's own pawns leave.
- **The destination is Core's choice, not ours.** `TileFinder.TryFindNewSiteTile` already refuses water, space and impassable terrain and already honours every mod that patches tile validity; our own test would be a second opinion that disagrees with the game the first time somebody installs a biome mod. The roll is wrapped in a seeded `Rand` state, so a way out does not move on reload. **`PlanetTile` is a readonly struct and not `IExposable`**, with a private `layerId`, so both halves are saved and the tile rebuilt - losing the layer would put a crew on the wrong planet layer, which reads as a teleport bug rather than a save bug.
- **Seven planted faults, seven catches, clean on restore**, including a direct `PassToWorld` added to the world exit, the map cap removed, the player's own limit ignored, a prisoner made takeable, the put-back removed, and the dead end restored.
- Build 0.12.21-dev, **174 C# files**, 91 package files, **0 warnings, 0 errors**. Nine checkers pass, **twenty-one** proofs exit zero. Assembly reproduced by two clean recompiles. **No game was launched, and nothing in this mod has ever been played.**

---

""")

s = read('docs/NOW.md')
pairs = [
    (u'| Published | **0.12.20-dev**.', u'| Published | **0.12.21-dev**.'),
    (u'## What shipped this session, 0.7.1 → 0.12.20',
     u'## What shipped this session, 0.7.1 → 0.12.21'),
    (u'| 0.12.20 | **The register, by the column that matters** — `trace` querying, and a **ninth checker** verifying how this mod uses other mods |',
     u'| 0.12.20 | **The register, by the column that matters** — `trace` querying, and a **ninth checker** verifying how this mod uses other mods |\n'
     u'| 0.12.21 | **A way out into the world** — the last unbuilt piece of the topology. Claim a tile under five maps, caravan over. **A dead end removed** |'),
    (u'| Build | **173 C# files, 91 package files**', u'| Build | **174 C# files, 91 package files**'),
    (u'| Proofs | **TWENTY** in `.local/register/proof-*.py`.',
     u'| Proofs | **TWENTY-ONE** in `.local/register/proof-*.py`.'),
    (u'7b. **Every proof (TWENTY), by exit status:**', u'7b. **Every proof (TWENTY-ONE), by exit status:**'),
    (u'   `spinup`, `starts`, `stranded-crew`, `tier-ladder`,',
     u'   `spinup`, `starts`, `stranded-crew`, `tier-ladder`, `world-exit`,'),
]
for old, new in pairs:
    assert old in s, 'NOW anchor missing: %r' % old[:70]
    s = s.replace(old, new, 1)

marker = u'208. **A `PatchOperationFindMod` does not edit anybody’s files**'
idx = s.index(marker)
line_end = s.index(u'\n', idx)
s = (s[:line_end + 1] +
     u'209. **A guarantee narrowed on a directory boundary is a guarantee evaded.** '
     u'`proof-stranded-crew.py` watched `Gate/*.cs` only, so a `PassToWorld` shipped in `Portals/` '
     u'would have passed on a technicality. **Say so, ask the owner, and assert the forbidden paths '
     u'by name** — closing, expiry, traversal — rather than relying on where a file sits.\n'
     u'210. **The five-map cap is the stricter of ours and the player’s.** Ours is five, counting '
     u'the coordinate they are standing in; the player’s is `Prefs.MaxNumberOfPlayerSettlements`. '
     u'**A setting the player chose is never overruled by this mod.**\n'
     u'211. **Generate the destination before despawning anybody.** The claimed map exists before a '
     u'pawn is touched, so a failure means nothing moved, and a failed spawn puts that pawn back. '
     u'Invariant 55 in the one place it would have been easiest to get wrong.\n'
     u'212. **Let Core choose the world tile.** `TileFinder.TryFindNewSiteTile` already refuses '
     u'water, space and impassable terrain and honours every mod that patches tile validity. Our own '
     u'test would be a second opinion that disagrees with the game the first time somebody installs '
     u'a biome mod. **Seed the roll**, or the way out moves on every reload.\n' +
     s[line_end + 1:])
write('docs/NOW.md', s)

# ------------------------------------------------------------------ close the topology rows
t = read('docs/TODO.md')
CLOSE = u' — **BUILT, 0.12.21-dev.** '
rows = [
    (u'**A portal whose far side is a world tile the branch does not yet hold**',
     u'A way out leads to a tile chosen by Core’s own `TileFinder.TryFindNewSiteTile`, seeded so it '
     u'does not move on reload. **Under the five-map cap the tile is claimed** through '
     u'`SettleUtility.AddNewHome` and the crew walks onto a new map, touching `PassToWorld` not at '
     u'all; **at or over the cap they form a caravan** they control. No new world object and no '
     u'bespoke map generation — the register’s `RR-OUT` trace showed the four Settled transport '
     u'mods that bear on this all integrate with caravans and none with a world object of ours.'),
    (u'**"and or pop out any where in the game world on a tile map"**',
     u'Both halves now ship: onto a map the branch already holds, and onto a tile it does not.'),
    (u'**"map > backrooms > map > backrooms"**',
     u'Every step of this chain now routes. The remaining dependency was the unheld tile.'),
    (u'**"backrromms > map>backrooms>backrooms>map"**',
     u'Every step of this chain now routes, including the second departure to the world.'),
    (u'**"to different maps in the world"**',
     u'Separate unheld tiles along one chain now work, up to the five-map cap, after which the '
     u'crew arrives as a caravan instead.'),
]
closed = 0
for anchor, note in rows:
    for prefix in (u'- [ ] ', u'- [~] '):
        target = prefix + anchor
        if target in t and t.count(target) == 1:
            start = t.index(target)
            end = t.index(u'\n', start)
            body = t[start:end].split(u'] ', 1)[1]
            for marker in (u' — **STILL OPEN', u' — **PARTLY BUILT'):
                body = body.split(marker)[0]
            t = t[:start] + u'- [x] ' + body + CLOSE + note + t[end:]
            closed += 1
            break
write('docs/TODO.md', t)
print('closed %d topology rows' % closed)
