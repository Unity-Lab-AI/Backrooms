# -*- coding: utf-8 -*-
"""Record the one-deploy direction verbatim, and resolve what it supersedes."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

SECTION = NL.join([
"",
"## Owner direction — ONE Pages deploy, and it is the public mod repository (2026-10-05)",
"",
"**Verbatim owner direction (2026-10-05):** *\"the only page deploy will be on the new github mod and wiki and public docs ONLY!!! DO YOU UNDERSTAND!!!!????? DO YOU HAVE QUESTIONS!!!!???\"*",
"",
"**Then, on how to carry it out:** *\"just make sure u do shit for what we need i dont know code just do what s right without losing capability and functioning and documentiaons\"*",
"",
"**Then, naming the supersession itself:** *\"but wait there are supper seeding rules that only the mod and public docs go into the new mod repo as the deployable repo for the wiki\"*",
"",
"**Then:** *\"nothing should refrence the build repos anywhere\"*",
"",
"**And:** *\"the links we wiull use later are the stewam mod collection and mod listing in the workshops\"*",
"",
"### What this supersedes, recorded rather than silently applied",
"",
"The owner's third message is the important one: these are **superseding rules**, and this project records a supersession the way `docs/CAMPAIGN_CHART.md` records four superseded prep documents — by naming what it replaces.",
"",
"- **SUPERSEDED: *\"docs/ root on this repo, github.io for now\"* (2026-10-01).** That answer is now overruled. This repository is never deployed; `docs/PUBLIC_RELEASE_PLAN.md` §3.3 and §3.4 recorded it as *ANSWERED* and both are corrected.",
"- **SUPERSEDED: the deploy half of *\"and docs and pages when we deploy the wiki and docs on github\"*.** The deploy happened — on the public mod repository, not here.",
"- **RE-AIMED: *\"A real domain, not a `github.io` path\"*.** Still the owner's to buy, and now it belongs to the public repository.",
"- **ALREADY TRUE, MEASURED NOT ASSUMED:** Pages on this repository returns **404** and has never been enabled. The direction describes the live state; what was wrong was the documents.",
"",
"### Nothing was deleted to achieve it",
"",
"Owner: *\"without losing capability and functioning and documentiaons\"*. So the Jekyll configuration, the layout, the include and the front door all **stay exactly where they are**. Nothing lost. What changed is that every document now says this repository is not deployed, and **the exclude list stays as a guard** — it is the only thing that would refuse the work ledger if Pages were ever switched on here by mistake.",
"",
"- [x] **\"the only page deploy will be on the new github mod and wiki and public docs ONLY\"** — **ENFORCED, NOT WRITTEN DOWN, 0.12.94-dev.** `check_only_one_pages_deploy` in `check-doc-conformance.py` refuses any living document that tells a reader to deploy Pages from this repository, or that names an address this repository does not serve. It is negation-aware and allows a sentence naming the public repository, so a document recording the rule passes while one instructing the forbidden action fails. **It immediately caught two documents written earlier in this same session** — `NOW.md` and the `TODO.md` deploy row — which is exactly the class of defect it exists for: a queue row instructing a forbidden action is worse than a stale one, because somebody does it.",
"- [x] **\"nothing should refrence the build repos anywhere\"** — **LIVE WHEN THE RULE WAS GIVEN, AND NOW REFUSED.** `docs/wiki/links.md` pointed its **Repository** and **Issues** rows at the working repository, so the published site sent every reader who wanted the source — or who wanted to report a bug — to the repository that holds the work ledger. Re-pointed, and `export-public-repo.py` now **refuses any export referencing a build repository**. Matched on **repository forms only** (`owner/repo` pairs and hostnames), never on the bare word: *Backrooms* is the name of the setting and appears all over the wiki as prose, so a rule banning the word would be unusable and would be scrolled past.",
"- [x] **\"the links we wiull use later are the stewam mod collection and mod listing in the workshops\"** — `docs/wiki/links.md` is reoriented around the **Steam Workshop mod and collection** as the destinations it exists for, both still *pending publication*. One row remains for source and issues so a bug report has somewhere to go, pointing at the public repository. **A dangling `../../CHANGELOG.md` link was removed** — it escaped the site root and pointed at a file the export deliberately does not carry.",
"- [x] **\"that needs ficxing because i inaccuratly told u evry mod was required, when that is in no way the case and needs rectify, with that major major task i told you about\"** — **THE DOCUMENTATION HALF OF THE MAJOR MAJOR TASK, AND IT HAD NEVER BEEN DONE.** The *code* half shipped at 0.12.86-dev: `About.xml` declares **zero** `modDependencies`, on the owner's direction *\"rework mod to not need any depeancie mods\"* and *\"we hope to have the mod as a complete stand alone\"*. **The documents never followed it**, and five of them were still telling players the opposite — in the places it does the most damage. **`docs/wiki/install.md`** had a Requirements table listing all five expansions, the full collection and **Harmony** as *Required*, on the one page a player reads to find out what to install. **`docs/wiki/mods.md`** was built on the same premise end to end: *\"This build is authored against a specific collection and declares every member of it\"*, with a table of required expansions and prose about declarations a manager reads. **`About.xml`'s own description** said it *\"declares every member of it as a dependency\"* — the text in the mod list itself. **`README.md`** said *\"RimWorld 1.6, all five expansions, and the collection this build is authored against. Every requirement is declared.\"* **`docs/PLAYING.md`** said *\"It declares hard dependencies\"*. All five corrected, and **the rule is enforced in three places now** — reader-facing documents, `About.xml`, and the public export — so it cannot come back quietly. **Nothing was found by auditing; every one was found by a checker or by reading generated output.**",
"- [x] **\"without losing capability and functioning and documentiaons\"** — **nothing was deleted.** `_config.yml`, `_layouts/default.html`, `_includes/nav.html` and `docs/index.html` all remain, and `build-site.py` and `check-site-generated.py` keep maintaining them. Two renderers of one source is not duplication while the source of truth is single, and it is: the static renderer **imports** the reading order from `build-site.py` rather than copying it. The exclude list is retained purely as the anti-accident guard.",
"",
])

CLOSE = [
 ('- [ ] **"and docs and pages when we deploy the wiki and docs on github"** - the deploy half.',
  'CLOSED 0.12.94-dev — **the deploy happened, and it is not here.** Owner, 2026-10-05: *"the only '
  'page deploy will be on the new github mod and wiki and public docs ONLY"*. The wiki is live at '
  '`https://g-fourteen.github.io/Rimrooms-AsyncIndustries/` — 200 on the index, a deep page and the '
  'stylesheet, verified with `curl -sI`. **The row’s own standard is met:** it said it stays open '
  '*"until that is on and the URL answers"*, and the URL answers. '
  '**Its earlier evidence told a reader to switch Pages on for THIS repository, which is now the '
  'forbidden action**, and `check_only_one_pages_deploy` refuses that sentence. Pages here returns '
  '**404 and has never been enabled** — measured, not assumed. Recorded as superseded rather than '
  'quietly re-aimed, because the 2026-10-01 answer *"docs/ root on this repo, github.io for now"* '
  'was explicit and is now overruled.'),

 ('- [ ] **A real domain, not a `github.io` path.**',
  'RE-AIMED 0.12.94-dev AT THE PUBLIC REPOSITORY, STILL THE OWNER’S TO BUY. The domain now belongs '
  'to `G-Fourteen/Rimrooms-AsyncIndustries`, which is the only thing that deploys. `CNAME.example` '
  'carries the DNS records, the copy step and the `curl -sI` verification, and **the export needs '
  'no page edits when the domain arrives** because nothing in the rendered site hard-codes its own '
  'address — every link is relative. The row stays open because the thing it asks for is a domain.'),
]

text = io.open(TODO, encoding="utf-8").read()
if "ONE Pages deploy" in text:
    print("section already present; nothing written")
    sys.exit(1)

problems = 0
for anchor, evidence in CLOSE:
    found = text.count(anchor)
    if found != 1:
        print("ANCHOR NOT UNIQUE (%d): %s" % (found, anchor[:80]))
        problems += 1
        continue
    at = text.index(anchor)
    line_end = text.index(NL, at)
    marker = "- [x] " if anchor.startswith("- [ ] **\"and docs") else "- [ ] "
    row = marker + text[at:line_end][len("- [ ] "):]
    text = text[:at] + row + " — **" + evidence + "**" + text[line_end:]
if problems:
    print("%d row(s) not touched; nothing written" % problems)
    sys.exit(1)

if not text.endswith(NL):
    text += NL
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text + SECTION)
print("recorded the direction, closed the deploy row, re-aimed the domain row")
