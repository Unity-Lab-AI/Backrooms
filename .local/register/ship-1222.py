# -*- coding: utf-8 -*-
"""Ledger for 0.12.22-dev: the last new art is gone."""
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


insert_before('CHANGELOG.md', u'## 0.12.21-dev', u"""## 0.12.22-dev - 2026-09-29 - the last new art is gone

- **This mod no longer adds a single piece of gameplay art.** The four custom images it still shipped - the field recorder, the route recording, the return anchor and the Quiet Pursuer - now use pictures the base game already has.
- **The Quiet Pursuer is a shape you cannot resolve.** It uses the base game's plain black mote, which suits it better than a drawing did: you are not meant to get a good look at it.
- **Nothing about how any of them behaves changed.** Every rule you can learn about the Pursuer, every route recording, every return anchor works exactly as before.
- **The rule is now checked rather than remembered.** The only images this mod ships are the main-menu slides, and a check refuses any other.

Full record: [the last new art is gone](docs/implementation/NO_NEW_ART_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

""")

insert_before('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - the last new art is gone (0.12.22-dev)

**Verbatim user quote:** *"lets get to it and lets not count the test items and the steam collection and mod workshop setup and stuff like that"*

### What shipped

The last four custom gameplay textures replaced with paths **enumerated out of Core's own defs**, and the no-new-gameplay-art half of invariant 10 turned into a check.

### Files touched

`1.6/Defs/ThingDefs_Items/RR_FieldEquipment.xml`, `1.6/Defs/ThingDefs_Misc/RR_SiteObjects.xml`, `tools/package-files.json`, `tools/check-register-compliance.py`, `docs/implementation/NO_NEW_ART_IMPLEMENTATION.md`, four PNGs archived to `historical-content/0.12.22-dev/textures/`, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj.

### Closure notes

- **THE COUNT IN THE ROW WAS STALE BY TEN.** M2 said *"remove the 14 historical gameplay PNGs from the package allowlist"*. **Four shipped.** Ten had already gone in earlier retirements and nobody updated the row - the same stale-number defect as the assembly hash and the C# file count, for the fourth time.
- **The breach was the ART, not the defs.** Three of the four are infrastructure or mechanics defs that invariant 10 explicitly permits: `RR_ReturnAnchor` is a non-deconstructible generator-placed marker, `RR_QuietPursuer` is an `Ethereal` Thing with a custom class, and `RR_RouteRecording` is **already superseded** - `CompRouteEvidence.NativeCarrierDef` resolves Core's `TextBook` and `IsLegacyCarrier` exists purely so old saves keep loading. Only `RR_FieldRecorder` is a buyable carryable item. **Rebuilding working systems was never the fix; the textures were.**
- **Every replacement path was ENUMERATED from Core's own defs, not remembered.** 908 distinct `texPath` values exist in `Data/Core/Defs`, and each chosen path was confirmed to appear in at least one Core def before use. Invariant 19, and the reason this did not become another `Named<TerrainDef>("Carpet")`:
  - field recorder -> `Things/Item/Equipment/WeaponSpecial/OrbitalTargeter`, a handheld device with a radio, which is what the description already claimed it was;
  - route recording -> `Things/Item/Book/Schematic/Schematic`, consistent with `TextBook` being the native carrier;
  - return anchor -> `Things/Building/Furniture/PenMarker`, a marker post;
  - **Quiet Pursuer -> `Things/Mote/Black`.**
- **The Pursuer is better for it.** Its own description says *"a motionless figure seems to occupy a nearer room whenever attention shifts"*, and Core ships no humanoid-figure Thing texture. A plain black shape you cannot resolve is closer to what that sentence promises than a drawing was, and the M2 row's own suggestion - a `Megascarab` reskin - would have put an insect where a figure belongs.
- **Retired art is archived, never deleted** - invariant 37. All four PNGs are in `historical-content/0.12.22-dev/textures/`.
- **The rule is now a check rather than a memory.** `check-register-compliance.py` asserts every image and sound this package ships is a **menu slide** - a shape, not a count - with `About/` exempt because every mod ships a preview. **Fault-planted both ways:** a gameplay texture reappearing under `Textures/Threats/` fails it, and a def naming a texture that no longer ships fails package integrity.
- **Zero gameplay art or audio now ships.** Six menu images, which are the single declared exception, and nothing else.
- Build 0.12.22-dev, 174 C# files, **87 package files** (four fewer), **0 warnings, 0 errors**. **No C# changed.** Nine checkers pass, twenty-one proofs exit zero. Assembly reproduced by two clean recompiles. **No game was launched, so these read correctly by def and by path and nobody has looked at one.**

---

""")

s = read('docs/NOW.md')
pairs = [
    (u'| Published | **0.12.21-dev**.', u'| Published | **0.12.22-dev**.'),
    (u'## What shipped this session, 0.7.1 → 0.12.21',
     u'## What shipped this session, 0.7.1 → 0.12.22'),
    (u'| 0.12.21 | **A way out into the world** — the last unbuilt piece of the topology. Claim a tile under five maps, caravan over. **A dead end removed** |',
     u'| 0.12.21 | **A way out into the world** — the last unbuilt piece of the topology. Claim a tile under five maps, caravan over. **A dead end removed** |\n'
     u'| 0.12.22 | **The last new art is gone** — four custom textures replaced with paths enumerated from Core. **Zero gameplay art ships**, and it is checked |'),
    (u'| Build | **174 C# files, 91 package files**', u'| Build | **174 C# files, 87 package files**'),
]
for old, new in pairs:
    assert old in s, 'NOW anchor missing: %r' % old[:70]
    s = s.replace(old, new, 1)

marker = u'212. **Let Core choose the world tile.**'
idx = s.index(marker)
line_end = s.index(u'\n', idx)
s = (s[:line_end + 1] +
     u'213. **Enumerate the replacement, never remember it.** `Data/Core/Defs` holds **908** distinct '
     u'`texPath` values; every path used here was confirmed present in a real Core def first. This is '
     u'the same discipline that `Named<TerrainDef>("Carpet")` skipped, and that one shipped a wrong '
     u'floor for months.\n'
     u'214. **Check a rule as a SHAPE, not a count.** *"Remove the 14 historical PNGs"* was stale by '
     u'ten. The durable assertion is *"every image this package ships is a menu slide"* — which needs '
     u'no number and cannot go out of date.\n'
     u'215. **When a def is infrastructure, the art is the breach.** Three of the four legacy defs '
     u'were mechanics or generator-placed markers that invariant 10 permits. Rebuilding working '
     u'systems was never the fix. **Separate the def from its texture before deciding what to '
     u'retire.**\n' +
     s[line_end + 1:])
write('docs/NOW.md', s)

# ------------------------------------------------------------------ close the M2 art rows
t = read('docs/TODO.md')
CLOSE = u' — **BUILT, 0.12.22-dev.** '
rows = [
    (u'**Remove the 14 historical gameplay PNGs from the package allowlist**',
     u'**The count was stale by ten: four shipped, not fourteen.** All four are gone, archived to '
     u'`historical-content/0.12.22-dev/textures/` per invariant 37, and every def now names a path '
     u'enumerated out of Core’s own defs. **Zero gameplay art or audio ships**, and '
     u'`check-register-compliance.py` asserts it as a shape rather than a count.'),
    (u'**`RR_QuietPursuer` presentation** → existing native pawn presentation',
     u'Presented with Core’s `Things/Mote/Black` — a shape you cannot resolve, which is closer to '
     u'its own description than a drawing was. **Every learned rule is unchanged.** The row’s '
     u'`Megascarab` suggestion was declined: it would have put an insect where a figure belongs.'),
    (u'**Legacy field gear** `RR_FieldRecorder`, `RR_SurveyTag`, `RR_ReturnBeacon`',
     u'The art half is closed: all four remaining textures now name Core paths. **`RR_RouteRecording` '
     u'was already superseded** — `CompRouteEvidence.NativeCarrierDef` resolves Core’s `TextBook` and '
     u'`IsLegacyCarrier` exists only so old saves keep loading. **Still open:** retiring the '
     u'`RR_FieldRecorder` *def* itself, which is the one genuinely buyable carryable item left, and '
     u'needs a migration decision because saved Things reference it.'),
]
closed = 0
for anchor, note in rows:
    for prefix in (u'- [ ] ', u'- [~] ', u'  - [ ] '):
        target = prefix + anchor
        if target in t and t.count(target) == 1:
            start = t.index(target)
            end = t.index(u'\n', start)
            body = t[start:end].split(u'] ', 1)[1]
            for m in (u' — **STILL OPEN', u' — **PARTLY BUILT'):
                body = body.split(m)[0]
            status = u'[~]' if u'Legacy field gear' in anchor else u'[x]'
            t = t[:start] + prefix.replace(u'[ ]', status).replace(u'[~]', status) + body + CLOSE + note + t[end:]
            closed += 1
            break
write('docs/TODO.md', t)
print('closed %d art rows' % closed)
