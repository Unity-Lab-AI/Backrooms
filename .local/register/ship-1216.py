# -*- coding: utf-8 -*-
"""Ledger for 0.12.16-dev: the menu takes any number of slides."""
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


insert_before('CHANGELOG.md', u'## 0.12.15-dev', u"""## 0.12.16-dev - 2026-09-29 - the menu takes any number of slides

- **New main-menu art is now a drop-in.** Any image named `RR_Menu_*.png` placed in the menu texture folder becomes a slide, in filename order, with no code change at all.
- **Another mod's menu art can never leak into the slideshow.** The folder is a shared content path, so the name prefix is what keeps the slideshow ours.
- **A full art brief ships with the mod**, naming twelve scenes drawn from things the mod actually contains, with the exact image size, the screen regions to keep clear, and the palette the game already uses.
- **Two integrity notes that had been wrong since the art was added are fixed.** Both existing slides were reported as unused every single run; the checker could not see how they were loaded.

Full record: [the menu takes any number of slides](docs/implementation/MENU_SLIDESHOW_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

""")

insert_before('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - the menu takes any number of slides (0.12.16-dev)

**Verbatim user request:** *"and some of the art for the manu menu when mod is loaded needs to have like content scenrio art like and ecounter and like lab opertions or gate industrial usage and scary creepy backrrom univers sill art for the manu menu slide show in dramatic and tragic and creepy moments of differnt scense and possible run ins, go hand ful or so or all these needs to be genrated well and rimwolrd styled"*

**Verbatim owner follow-up:** *"okay ill get another ai to tdo the art in parrallel"*

### What shipped

The slideshow now loads **any** `RR_Menu_*.png` from its folder, and `docs/MENU_ART_BRIEF.md` is the hand-off spec. **No image was produced here: this session has no image-generation tool**, which was said plainly rather than worked around, and the owner is having the art done in parallel.

### Files touched

`src/RimroomsAsyncIndustries/Presentation/RimroomsMenuBackground.cs`, `tools/check-package-integrity.py`, `tools/check-keyed-strings.py`, `docs/MENU_ART_BRIEF.md` (new), `docs/implementation/MENU_SLIDESHOW_IMPLEMENTATION.md`, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj.

### Closure notes

- **The slide list was a hardcoded two-entry string array.** It is now `ContentFinder<Texture2D>.GetAllInFolder`, so art produced in parallel drops in and works with no code change - which is the only shape that makes sense when the art and the code are being made by different parties at the same time.
- **A folder scan alone would have been a compatibility defect.** `UI/Menu` is a generic content path and `ContentFinder` resolves across **every loaded mod**, so a bare scan would pull another mod's menu art into this slideshow. In the 294-mod target install that is a certainty rather than a risk. The **`RR_Menu_` prefix is load-bearing**, and the doc comment says so at the site.
- **Slides are sorted ordinally by name** - invariant 26. A slideshow whose order depends on whatever order the loader returned is one nobody can describe or reproduce a screenshot from.
- **Two integrity notes had been wrong since the art was added.** Both menu PNGs were reported *"ships but nothing references it"* on **every run**, because the checker only recognised `ContentFinder<Texture2D>.Get("literal")` and the old code called `Get(variable)` out of an array. **A note nobody can act on is noise, and noise is how a real finding gets scrolled past.** The checker now understands `GetAllInFolder` and reports the folder and its slide count instead. This is not a widening: `GetAllInFolder` genuinely loads every image under the folder.
- **`check-keyed-strings.py` correctly flagged the new prefix**, because `RR_Menu_` looks exactly like a keyed key. Fixed the way that file already works - **classified by call site, not by spelling**: a `const string` counts as internal only when it is passed to `StartsWith`. **Fault-planted:** an undeclared `RR_` const that is not used in `StartsWith` still fails, so the narrowing did not blind the rule.
- **The brief names twelve scenes drawn from what the mod actually contains** - the threshold, gate assembly, spin-up, a field survey, marked routes, coherence decay, something waiting at the threshold, a crew that did not come back, the clean-up team, the store basement, the solo start, and a door standing in a residential street. **None of it is invented lore.** It also records the real numbers rather than guesses: 1920x1080 at 16:9 (the two existing slides are 1672x941, the same aspect), the version-label rect at `x 350-770, y 10-74`, and the expansion strip in the bottom-left 104 px, all read out of the source.
- **The one manual step is stated and cannot be skipped:** each new PNG needs a line in `tools/package-files.json`, and the brief warns **not** to add the line before the file exists, because a listed-but-missing file breaks the staging script.
- Build 0.12.16-dev, 173 C# files, 87 package files, **0 warnings, 0 errors**. Eight checkers pass, **eighteen** proofs exit zero. Assembly reproduced by two clean recompiles. **No game was launched, so dwell timing, crossfade and legibility behind the menu buttons are unverified by play and only the owner can confirm them.**

---

""")

s = read('docs/NOW.md')
pairs = [
    (u'| Published | **0.12.15-dev**.', u'| Published | **0.12.16-dev**.'),
    (u'## What shipped this session, 0.7.1 → 0.12.15',
     u'## What shipped this session, 0.7.1 → 0.12.16'),
    (u'| 0.12.15 | **The universe has factions in it** — seven, all neutral, **no settlements and no new content**. Closes the largest unbuilt owner direction |',
     u'| 0.12.15 | **The universe has factions in it** — seven, all neutral, **no settlements and no new content**. Closes the largest unbuilt owner direction |\n'
     u'| 0.12.16 | **The menu takes any number of slides** — folder-scanned with a load-bearing name prefix, plus the art brief. Two integrity notes that were always wrong, fixed |'),
]
for old, new in pairs:
    assert old in s, 'anchor missing: %r' % old[:60]
    s = s.replace(old, new, 1)

marker = u'193. **Some correctness is achieved by NOT setting a field.**'
idx = s.index(marker)
line_end = s.index(u'\n', idx)
s = (s[:line_end + 1] +
     u'194. **`ContentFinder` resolves across every loaded mod, so a folder scan is not ours.** '
     u'`UI/Menu` is a generic content path; without a name prefix another mod’s art appears in our '
     u'slideshow. **Scan the folder, then filter by prefix**, and say at the site that the prefix '
     u'is load-bearing.\n'
     u'195. **A note nobody can act on is noise, and noise is how a real finding gets scrolled '
     u'past.** Both menu textures were reported unreferenced on every run for months because the '
     u'checker could not follow `Get(variable)`. **Teach the checker the API** rather than leaving '
     u'a permanent false note.\n'
     u'196. **When a checker flags something legitimately new, fix it by its own design.** '
     u'`check-keyed-strings.py` classifies by **call site, not spelling**, so a texture prefix '
     u'counts as internal only when it is passed to `StartsWith` — and the narrowing was '
     u'fault-planted to prove it still catches an undeclared key.\n' +
     s[line_end + 1:])
write('docs/NOW.md', s)

# M5's slideshow rows: the mechanism is done, the images are the owner's parallel track.
t = read('docs/TODO.md')
old_row = u'- [~] Slideshow integration review, additional menu images per shipped scenario. — **PARTLY BUILT.** The slideshow ships. **Additional images per scenario are not authored**, and images are the one place new art is permitted.'
new_row = (u'- [~] Slideshow integration review, additional menu images per shipped scenario. — '
           u'**PARTLY BUILT.** The slideshow ships, and **0.12.16-dev made new art a drop-in**: any '
           u'`RR_Menu_*.png` in the menu folder becomes a slide, in filename order, with no code '
           u'change. `docs/MENU_ART_BRIEF.md` specifies twelve scenes drawn from shipped content, '
           u'the exact size, the screen regions to keep clear and the palette. **The images '
           u'themselves are the owner’s parallel track** — *"okay ill get another ai to tdo the '
           u'art in parrallel"* — because this session has no image-generation tool.')
assert old_row in t, 'M5 slideshow row not found'
write('docs/TODO.md', t.replace(old_row, new_row, 1))
