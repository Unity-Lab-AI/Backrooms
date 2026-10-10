# -*- coding: utf-8 -*-
"""Close the two docs rows the guard work finished, and correct the deploy row.

Evidence sits on the row's own line, per the queue's own rule that a reader must see WHAT was
done and WHERE rather than a checkmark.
"""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

CLOSED = [
 ('- [ ] **The generator stays internal, by the finding that opened this.**',
  'CLOSED 0.12.93-dev, AND THE COMMENT WAS NOT ONLY UNENFORCED, IT WAS WRONG. The row said '
  '*"a comment is not a guard"* and it was righter than it knew. `_config.yml` claimed '
  'everything but the wiki was *"deliberately excluded"* while naming **four directories, two '
  'of which (`evidence`, `reviews`) do not exist** — and **Jekyll publishes every entry in its '
  'source directory it is not told to exclude.** Fifty-four documents sit at `docs/` root. None '
  'carries front matter, so Jekyll would have copied each one verbatim and served it as a raw '
  'download. **Enabling Pages would have published `TODO.md`, `NOW.md`, `FINALIZED.md` and '
  '`DECOMPOSED.md` — the entire work ledger, on the public internet.** '
  '**Two independent instruments now hold it, which is the right shape: one keeps the list '
  'current and one refuses the bad outcome.** `tools/build-site.py` writes the exclude list from '
  'the directory itself and `--check` fails the battery the moment a new document appears '
  'unexcluded — a list nobody maintains is how this got wrong in the first place. '
  '`check-doc-conformance.py` **does not read that list and agree with it**: it models what '
  'Jekyll would publish and fails on the answer, so a broken generator cannot produce a quiet '
  'pass. It refuses fourteen ledger names and any published file outside the declared site '
  'surface, because the names are the hazard we know about and an undeclared surface is how the '
  'next one arrives. **Explicit names, never globs** — `*` crossing a path separator is a '
  'subtlety of Ruby’s `File.fnmatch` that cannot be verified from here, and a pattern that '
  'silently fails to exclude is the one failure mode a ledger guard must not have. '
  '**Seen refusing, not assumed to refuse:** `plant-published-site.py` lands 23 of 23, including '
  '**a valid CNAME that must PASS** — a rule that refuses every input is not a rule — and two '
  'plants that blind the model, because every rule here is an absence rule and an absence rule '
  'over an empty set is satisfied by construction. The checker now refuses outright if it finds '
  'no page under `docs/wiki/`.'),

 ('- [ ] **`check-doc-conformance.py` must cover the published site**',
  'CLOSED 0.12.93-dev, exactly on the gap 0.12.92-dev measured. `living_docs()` already globed '
  'every `.md`, so the wiki prose was never uncovered; what was uncovered is the site’s '
  '**non-markdown** published files, and all five are now held to the version, branch, '
  'retired-def and claims rules: `_layouts/default.html`, `_includes/nav.html`, '
  '`assets/css/rimrooms.css`, `_config.yml` and `docs/index.html`. '
  '**A layout is never fetched by a reader and its text is on every page a reader fetches**, so '
  'a version claimed there ships exactly as widely as one claimed in prose — checking only the '
  'files Jekyll serves would have missed all three templates. **Vocabulary and the wall rule '
  'apply only where a reader meets words:** a stylesheet’s selectors are not prose, and flagging '
  'one would be the crying-wolf failure this checker’s own branch rule warns about. **The wall '
  'rule measures `<p>` elements here, not blank-line blocks**, because an HTML file has no blank '
  'line between paragraphs and the markdown splitter would read a whole page as one wall. '
  '**A `CNAME` is now checked when one exists** — one bare line, no comment, no placeholder — '
  'which `CNAME.example` already warned about and nothing enforced; it fails the way the example '
  'describes, quietly, with Pages serving nothing while DNS gets blamed. '
  '**And the checker count is now read off `tools/` instead of typed.** It said `CHECKER_COUNT = '
  '8` with a phrase list stopping at *"seven checkers"* while **nineteen** shipped, so the one '
  'number the rule exists to protect was eleven out of date. The derived version immediately '
  'caught a real stale claim in `COMPLIANCE_AND_OFFICIAL_VERSIONS.md` that the fixed list '
  'structurally could not see. It also learns *"the other N checkers"*, which is N+1: a rule that '
  'demands wrong prose to pass is a rule people scroll past.'),
]

NOTES = [
 ('- [ ] **"and docs and pages when we deploy the wiki and docs on github"** - the deploy half.',
  'AND THE URL NOW HAS SOMETHING TO ANSWER WITH, 0.12.93-dev. The row says it stays open *"until '
  'that is on and the URL answers"* — and **the URL would have answered 404.** Pages serves '
  '`docs/`, every page inside the wiki worked, and the site’s own address had no document at '
  'all. `docs/index.html` is that front door: no front matter so Jekyll copies it verbatim, a '
  '**relative** link because a project site is served from a subpath and `/wiki/` would resolve '
  'above it, a real anchor as well as the refresh so a reader whose browser ignores one still '
  'has a way in, and no script and no external request. The row stays open because the switch is '
  'still the owner’s: Settings → Pages → source `main` / folder `/docs`.'),
]

text = io.open(TODO, encoding="utf-8").read()
problems = 0

for anchor, evidence in CLOSED:
    found = text.count(anchor)
    if found != 1:
        print("ANCHOR NOT UNIQUE (%d): %s" % (found, anchor[:80]))
        problems += 1
        continue
    at = text.index(anchor)
    line_end = text.index(NL, at)
    row = "- [x] " + text[at:line_end][len("- [ ] "):]
    text = text[:at] + row + " — **" + evidence + "**" + text[line_end:]

for anchor, note in NOTES:
    found = text.count(anchor)
    if found != 1:
        print("NOTE ANCHOR NOT UNIQUE (%d): %s" % (found, anchor[:80]))
        problems += 1
        continue
    at = text.index(anchor)
    line_end = text.index(NL, at)
    text = text[:line_end] + " — **" + note + "**" + text[line_end:]

if problems:
    print("%d row(s) not touched; nothing written" % problems)
    sys.exit(1)
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text)
print("closed %d rows, noted %d" % (len(CLOSED), len(NOTES)))
