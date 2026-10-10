# -*- coding: utf-8 -*-
"""Ledger for 0.12.17-dev: four more menu slides, and a guard against silent ones."""
import io
import os
import re

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


# ------------------------------------------------------------------ tidy the allowlist ordering
# The four new entries were appended rather than sorted in. The checker sorts before comparing so
# order is functionally irrelevant, but the file is human-maintained and alphabetical everywhere
# else, and a list people read should stay readable.
allow_rel = os.path.join('tools', 'package-files.json')
allow = read(allow_rel)
menu_lines = re.findall(r'^\s*"1\.6/Textures/UI/Menu/[^"]+",\n', allow, re.M)
assert len(menu_lines) == 6, 'expected six menu entries, found %d' % len(menu_lines)
block_start = allow.index(menu_lines[0])
block_text = ''.join(menu_lines)
assert block_text in allow, 'menu entries are not contiguous; not reordering blindly'
indent = re.match(r'^\s*', menu_lines[0]).group(0)
sorted_block = ''.join(
    indent + '"' + path + '",\n'
    for path in sorted(re.search(r'"([^"]+)"', line).group(1) for line in menu_lines))
if sorted_block != block_text:
    write(allow_rel, allow.replace(block_text, sorted_block, 1))
else:
    print('allowlist menu entries already sorted')

# ------------------------------------------------------------------ CHANGELOG
insert_before('CHANGELOG.md', u'## 0.12.16-dev', u"""## 0.12.17-dev - 2026-09-29 - four more menu slides

- **Six main-menu images now cycle instead of two.** Laboratory operations, industrial gate logistics, a corridor encounter and a silent recovery join the two that were already there.
- **A slide that would never have appeared is now caught before it ships.** The slideshow only shows files whose name starts with `RR_Menu_`, so a correctly-drawn image with the wrong filename used to be invisible with nothing anywhere saying so.
- **A truncated or half-copied image is caught too**, which matters because the game would only fail when it tried to load it, long after the build said everything was fine.
- **How the images were made is recorded and ships with the mod**, including the exact instructions used for each one.

Full record: [four more menu slides](docs/implementation/MENU_SLIDES_LANDED_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

""")

insert_before('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - four more menu slides (0.12.17-dev)

**Verbatim user quote:** *"okay get to doing next up and those additional main menu images should be good to go now"*

### What shipped

Four original menu illustrations produced on the owner's parallel track, plus **a proof that a slide cannot fail silently**. The art itself was not produced here: this session has no image-generation tool.

### Files touched

Four PNGs in `1.6/Textures/UI/Menu/`, `outputs/menu-art-2026-09-29/prompts-and-provenance.json`, `tools/package-files.json`, `docs/implementation/MENU_SLIDES_LANDED_IMPLEMENTATION.md`, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj, and `proof-menu-slides.py` (new, the nineteenth).

### Closure notes

- **The drop-in design worked exactly as intended.** Four images landed, correctly prefixed, and the slideshow picked all four up with **no code change** - which was the whole point of replacing the hardcoded two-entry array in 0.12.16-dev. `check-package-integrity.py` reports six textures covered by the folder scan.
- **THE SILENT FAILURE THIS GUARDS IS REAL AND WAS LIKELY.** The slideshow only shows files whose name starts with `RR_Menu_`, so **a correctly-drawn image with the wrong filename is loaded by nothing, shown to nobody, and nothing in the build, the checkers or the log would say so.** With the art produced separately from the code, a naming mistake was probable rather than hypothetical. Fault-planted: a stray `MenuBackdrop_NoPrefix.png` makes the proof exit 1.
- **A truncated image is caught at build rather than at load.** Unity fails when it tries to read a malformed PNG, which is long after the build has reported success, and a half-finished copy is the obvious way parallel art delivery goes wrong. The proof checks the signature **and** that `IEND` is the final chunk with zero trailing bytes. My first attempt at that check compared the last eight bytes literally and reported **every** file as broken, including the two that already shipped - the check was wrong, not the files, and it was corrected rather than believed.
- **Aspect ratios are checked as a set, not individually.** `BackgroundRect` reads each image's own aspect, so mismatched slides letterbox differently and the crossfade between them reads as a bug. `RR_Menu_LaboratoryOperations.png` is **1672x940 against the others' 1672x941** - a one-pixel difference, 0.1% of aspect, inside the tolerance and **reported explicitly rather than hidden**. It does not need regenerating.
- **The folder and prefix are read out of the source, never restated in the proof**, so renaming either one moves the proof with it instead of leaving it checking a value that no longer exists.
- **Provenance ships, and it is a release obligation rather than a nicety.** `prompts-and-provenance.json` records the tool and the exact prompt for each image. **Steam requires AI-content disclosure**, and original menu images are the *one* exception to this project's no-new-art rule, so a record is what makes both statements auditable at release instead of remembered. The proof asserts it exists.
- **Three planted faults, three catches, clean on restore.**
- Build 0.12.17-dev, 173 C# files, **91 package files**, **0 warnings, 0 errors**. **No C# changed.** Eight checkers pass, **nineteen** proofs exit zero. Assembly reproduced by two clean recompiles. **No game was launched, so how these read behind the menu buttons, and the dwell and crossfade timing, remain unverified by play.**

---

""")

s = read('docs/NOW.md')
pairs = [
    (u'| Published | **0.12.16-dev**.', u'| Published | **0.12.17-dev**.'),
    (u'## What shipped this session, 0.7.1 → 0.12.16',
     u'## What shipped this session, 0.7.1 → 0.12.17'),
    (u'| 0.12.16 | **The menu takes any number of slides** — folder-scanned with a load-bearing name prefix, plus the art brief. Two integrity notes that were always wrong, fixed |',
     u'| 0.12.16 | **The menu takes any number of slides** — folder-scanned with a load-bearing name prefix, plus the art brief. Two integrity notes that were always wrong, fixed |\n'
     u'| 0.12.17 | **Four more menu slides** — six now cycle. A slide that would never have appeared is caught before it ships; provenance ships for the Steam disclosure |'),
    (u'| Build | **173 C# files, 87 package files**', u'| Build | **173 C# files, 91 package files**'),
    (u'| Proofs | **EIGHTEEN** in `.local/register/proof-*.py`.',
     u'| Proofs | **NINETEEN** in `.local/register/proof-*.py`.'),
    (u'7b. **Every proof (EIGHTEEN), by exit status:**', u'7b. **Every proof (NINETEEN), by exit status:**'),
    (u"   `live-effects`, `offer-routes`, `portal-footprint`, `remote-sites`, `request-generation`,",
     u"   `live-effects`, `menu-slides`, `offer-routes`, `portal-footprint`, `remote-sites`, `request-generation`,"),
]
for old, new in pairs:
    assert old in s, 'NOW anchor missing: %r' % old[:60]
    s = s.replace(old, new, 1)

marker = u'196. **When a checker flags something legitimately new, fix it by its own design.**'
idx = s.index(marker)
line_end = s.index(u'\n', idx)
s = (s[:line_end + 1] +
     u'197. **A drop-in folder needs a proof that nothing dropped in can fail silently.** A slide '
     u'named without the prefix is loaded by nothing and shown to nobody, and no build, checker or '
     u'log says so. When content arrives from outside the code, **assert the naming contract** and '
     u'plant a stray file to prove it fails.\n'
     u'198. **Validate delivered binary assets structurally, at build.** A truncated PNG fails when '
     u'Unity reads it, long after the build reported success. Check the signature **and** that '
     u'`IEND` is the final chunk. My first version of that check compared the last eight bytes '
     u'literally and condemned every file, including ones already shipping — **the check was wrong, '
     u'not the files.**\n'
     u'199. **Provenance for generated art is a release obligation, not a nicety.** Steam requires '
     u'AI-content disclosure and menu images are the single exception to the no-new-art rule. '
     u'`prompts-and-provenance.json` records tool and prompt per image, and a proof asserts it '
     u'exists.\n' +
     s[line_end + 1:])
write('docs/NOW.md', s)

t = read('docs/TODO.md')
old_row = u'**The images’ themselves are the owner’s parallel track**'
if old_row in t:
    t = t.replace(old_row, u'**The images landed 0.12.17-dev.**', 1)
anchor = u'- [~] Slideshow integration review, additional menu images per shipped scenario.'
assert anchor in t, 'slideshow row not found'
start = t.index(anchor)
end = t.index(u'\n', start)
t = (t[:start] + u'- [~] Slideshow integration review, additional menu images per shipped scenario. — '
     u'**MOSTLY BUILT.** **Six slides ship as of 0.12.17-dev** — the four new ones landed on the '
     u'owner’s parallel art track and the folder scan picked them up with no code change. '
     u'`proof-menu-slides.py` now guards the naming contract, structural PNG validity, a shared '
     u'aspect and the provenance record. **Still open: the integration REVIEW itself, which needs '
     u'a launch** — how they read behind the menu buttons, and whether 30 s dwell and 2 s crossfade '
     u'feel right, cannot be judged from here.' + t[end:])
write('docs/TODO.md', t)
