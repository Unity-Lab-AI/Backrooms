# -*- coding: utf-8 -*-
"""Close what the site work actually finished. Evidence on the row's own line."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

CLOSED = [
 ('- [ ] **"the beautiful and masterfully way paossible so the thing needs to NOT pop like a text',
  'CLOSED 0.12.92-dev. **The theme is gone and the layout is ours.** The row’s reading of '
  '`jekyll-theme-primer` was blunt and right — a text wall with a margin: one column, one type '
  'size, and no way into a page except reading it from the top. '
  '`docs/_layouts/default.html` and `docs/assets/css/rimrooms.css` replace it, and the row’s '
  'own framing decided the approach — *"a layout answer as much as a prose one"*. **Four devices '
  'do that work:** a persistent index of every page, visible on every page; a **summary line** at '
  'the top of each; a prose column capped near 68 characters, because a full-width paragraph *is* '
  'the text wall; and headings that read as dividers with a rule and real space above them, with '
  'tables and blockquotes styled so a skimming eye lands on them. '
  '**No webfont, no script, no external request, and no remote theme gem** — the site is a '
  'handful of static files, which is the same instinct as the package depending on nothing but '
  'Core. Dark mode, a keyboard skip link, and the current page marked by weight and an inset rule '
  'rather than by colour alone.'),

 ('- [ ] **Style and format across the thirteen WIKI pages is the remaining half**',
  'CLOSED 0.12.92-dev, and the row said where it belonged: *"it belongs with the site build below '
  'rather than here"*. All thirteen pages now carry `title` and `summary` front matter, so each '
  'one **says what it is before it says anything else** — rendered as a callout at the top of '
  'the page and as the hover text on its index entry. The structural half is the layout above; '
  'this is the half that had to be on the pages themselves, because no stylesheet can invent a '
  'one-line answer to *what is this page for*.'),

 ('- [ ] **Generated, never hand-maintained.**',
  'CLOSED 0.12.92-dev. `tools/build-site.py` writes `docs/_includes/nav.html` from whatever is '
  'actually in `docs/wiki/` — the title from each page’s own first heading, the hover text '
  'from its `summary` front matter. **A hand-written list of pages is a second place the truth '
  'lives:** add a page and the list is wrong, rename one and the list is a broken link. '
  '`--check` fails when the include and the directory disagree, so the battery catches a stale '
  'index rather than a reader finding it. '
  '**A page not named in the declared reading order is still published and still indexed**, under '
  '*More* — a new page is never silently dropped. Order is declared rather than alphabetical '
  'because a newcomer wants *install* before *credits*, and alphabetical would open with '
  '*backrooms* by accident.'),

 ('- [ ] **"docs/ root on this repo, github.io for now"**',
  'CLOSED 0.12.92-dev, exactly as the row specified: **CNAME support authored now, the domain '
  'left open.** `_config.yml` publishes `wiki` and excludes the working material, and it now '
  'states in the file why the ledger can never be published. `docs/CNAME.example` carries the '
  'shape, the four apex A records, the subdomain alternative, the Settings step and the '
  '`curl -sI` verification — and it is **inert on purpose**. '
  '**No file in this repository names a hostname the deploy does not serve**, which is the rule '
  'the row sets. A live `CNAME` naming a domain nobody owns yet does not fail loudly: Pages stops '
  'answering on `github.io` and waits for DNS that never arrives. So the shape is ready and '
  'nothing pretends. **And no page hard-codes the site’s own address** — links go through '
  'Jekyll’s `relative_url`, so they follow whatever domain serves them and the real domain '
  'needs no page edits at all.'),
]

NOTES = [
 ('- [ ] **"and docs and pages when we deploy the wiki and docs on github"** - the deploy half.',
  'THE SITE IS BUILT AND WAITING ON ONE SWITCH 0.12.92-dev. Layout, stylesheet, generated index, '
  'per-page summaries, config and CNAME support all ship and `tools/build-site.py --check` is '
  'green. **What is left is not work, it is the owner enabling Pages:** repository Settings → '
  'Pages → source `main` / folder `/docs`. The row stays open until that is on and the URL '
  'answers, because a deploy nobody has turned on is not a deploy.'),

 ('- [ ] **A real domain, not a `github.io` path.**',
  'SUPPORT AUTHORED 0.12.92-dev, DOMAIN STILL THE OWNER’S TO BUY. `docs/CNAME.example` has the '
  'DNS records, the copy step and the verification, and the site needs **no page edits** when the '
  'domain arrives because nothing hard-codes its own address. The row stays open because the '
  'thing it asks for is a domain, and naming one this repository does not serve is the specific '
  'failure the row’s sibling forbids.'),

 ('- [ ] **The generator stays internal, by the finding that opened this.**',
  'STATED IN THE CONFIG 0.12.92-dev, NOT YET ENFORCED. `_config.yml` now records in the file that '
  '`outputs/readable/` is an internal reading convenience and that the work ledger is never '
  'published. **The row stays open because a comment is not a guard** — the enforcement belongs '
  'in `check-doc-conformance.py`, alongside the published-site coverage on the row below it, and '
  'both are the same small piece of work. Written down rather than claimed.'),

 ('- [ ] **`check-doc-conformance.py` must cover the published site**',
  'NOT DONE 0.12.92-dev, and the gap is now precise rather than general. `living_docs()` already '
  'globs **every** `.md` under the repository, so the thirteen wiki pages are **already** covered '
  'for version and branch claims — that half was never missing. **What is uncovered is the '
  'site’s non-markdown published files:** `_layouts/default.html`, `_includes/nav.html`, '
  '`assets/css/rimrooms.css`, `_config.yml` and a future `CNAME`. A version or a branch claimed '
  'in a layout would ship unchecked today. Measured rather than assumed, and it is the same piece '
  'of work as the ledger guard above.'),

 ('- [~] Research IDs across tiers T0–T6 and the nine branches;',
  'MEASURED 0.12.92-dev AND THE ROW WAS WRONG ABOUT T3. It says *"Tiers 0–2 complete across '
  'seven branches; T3 is the next checkpoint"*. **T3 is fully built** — seven projects, one per '
  'branch, each requiring its tier-2 sibling plus three route, two distortion and one entity log, '
  'with its own header at `RR_CompanyProjects.xml` line 418 and a record in '
  '`BUILD_ORDER_CORRECTION.md`. **T4 is built too**, six of seven, and both absences are reasoned '
  'in the file: Logistics has no tier 4 because lead time, dispatch delay, order capacity and '
  'unattended delivery are already taken by tiers 1, 2, 0 and 3, and what remains in Procurement '
  'is safety bounds no player will ever reach — *"a project here would promise something and '
  'change nothing, which is exactly what 0.12.5-dev deleted four projects for"*. The gate line '
  'has none and cannot: there is nothing above indefinite. '
  '**And the tier system is measurably healthy: 34 capabilities granted, 34 read, a perfect '
  'bijection** — no hollow unlock and no dead read. '
  '**So what is actually open is T5 and T6**, and the file’s own rule makes that a knob sweep '
  'rather than an authoring job: a tier may only exist where an unclaimed, player-noticeable knob '
  'does. 274 tunable constants exist and 34 are claimed, so the sweep has somewhere to look — but '
  'deciding which of the remainder a player could *name the effect of* is the work, and inventing '
  'seven projects without it would ship exactly the lie the file deletes projects for.'),
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
    marker = "- [~] " if anchor.startswith("- [~]") else "- [ ] "
    row = "- [x] " + text[at:line_end][len(marker):]
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
