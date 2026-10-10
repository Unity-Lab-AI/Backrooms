# -*- coding: utf-8 -*-
"""Close the six public-export rows."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

CLOSED = [
 ('- [ ] **"the repo for the mod only is :https://git.unityailab.com/GFourteen/Rimrooms-AsyncIndustries.git"**',
  'CLOSED 0.12.94-dev. **Pushed, and the repo was already there and empty** — measured before '
  'asking: `ls-remote` exits 0 with zero refs, where a missing repo returns 128, so push-to-create '
  'being disabled server-side was never a blocker. `tools/export-public-repo.py --push` delivers '
  'it, and the read-back is the receipt: `refs/heads/main` at the same commit on both remotes.'),

 ('- [ ] **"and the same thing for a github repo of the same name that you will make and set up"**',
  'CLOSED 0.12.94-dev. **`G-Fourteen/Rimrooms-AsyncIndustries` created PUBLIC and pushed**, on the '
  'owner’s answer and their note *"itylab ai but my personal"* — the lab is Unity AI Lab, this repo '
  'is their personal account, mirroring the Forgejo path exactly. **PUBLIC was not a preference:** '
  'Pages does not serve from a private repository on a free plan, so a private one would have left '
  'the deploy waiting for ever. Created with `gh` from this machine, which the owner’s account '
  'could do: org admin, `repo` scope.'),

 ('- [ ] **"which should include only public facing documents and wiki htmls for deploying the github.io static page"**',
  'CLOSED 0.12.94-dev, **and the denylist earned its keep on its first run.** An allowlist decides '
  'what goes in; a denylist then **refuses the assembled tree**, and both run — because 0.12.93-dev '
  'learned the cost of a policy that was only described. The second pass refused the very first '
  'export: **`CHANGELOG.md` contains *"VERBATIM TRANSFER CONFIRMED"***, and it is a development log '
  'full of queue counts and instrument tallies. The owner’s standing rule settles it — *"public '
  'facing docs are concise easy to read and have no in house dev names and no todo numbering and no '
  'actual work information"* — so **it does not ship**, and a player-facing *what is new* is '
  'recorded as authoring work rather than faked by filtering this one. '
  '**`README.md` is not copied either**, and that is the same finding in a different coat: the '
  'working readme is clean of internal vocabulary, but **every link in it is wrong here** — it '
  'points at `docs/wiki/*.md`, at `CONTRIBUTING.md` and at `docs/BUILDING.md`. Copying it would '
  'have published a readme of dead links. The export generates its own from `About.xml`, the text '
  'that already describes this mod to a player, and **refuses if any link would point at a page '
  'the export does not have**. '
  '**The refusals are named, not implied:** the ledger filenames in both `.md` and `.html` form, '
  '`.claude/`, `.local/`, `implementation/`, `research/`, `src/`, `tools/`, the archive’s own '
  'transfer banner as *text* under any filename, and **a queue row’s own shape anywhere in the '
  'tree**. `tools/check-public-export.py` makes it the battery’s business rather than one tool’s, '
  'because a guard only somebody remembers to run is the `_config.yml` mistake again.'),

 ('- [ ] **"only what the game need to run the mod"**',
  'CLOSED 0.12.94-dev, and the owner said it fine three times — *"ie what we stage"*, *"what goes '
  'into the game as the mod"*. **It was already machine-readable.** '
  '`artifacts/build/package-manifest.json` is written by the build and holds **103 files with a '
  'SHA256 each**; `tools/stage-mod.ps1` copies exactly that into the game folder. **The exporter '
  'reads the same manifest**, so *what we stage* and *what we publish* cannot drift: one list, '
  'produced by the build, two consumers. Measured: `About/` 3, `1.6/` 99 including the assembly, '
  '`LoadFolders.xml` 1. '
  '**Every hash is verified on the way out, and the copy is read back.** The stager refuses a '
  'package edited after the build for good reason, and publishing has the same requirement with a '
  'worse failure mode — a wrong file in the game folder is one machine, a wrong file in a public '
  'repository is everybody’s. A plant that globs the package instead of reading the manifest fails '
  'the claim, which is what stops *the mod* quietly acquiring a second definition.'),

 ('- [ ] **"wiki htmls"**',
  'CLOSED 0.12.94-dev. `tools/render-wiki-html.py` renders the thirteen pages to standalone static '
  'HTML — **no Jekyll, no `_config.yml`, no build step, no network** — and the row’s own condition '
  'is met: **`SECTIONS`, `page_title` and `page_summary` are IMPORTED from `tools/build-site.py`**, '
  'never copied, so the two sites cannot disagree about what the wiki is. '
  '**`tools/make-readable-html.py` could not be reused, and the reason is specific:** it emits one '
  '`<p>` per source line, and every wiki page is hard-wrapped near ninety characters, so a '
  'four-line paragraph would have rendered as four paragraphs. It also has no blockquote, and '
  'blockquote is the wiki’s callout. The internal reader and the published site want different '
  'renderers; pretending one tool does both is how the published site would quietly look wrong. '
  '**Output is flat** — every link a sibling, the stylesheet one path from everywhere — because a '
  'nested directory means `..` in some links and not others, which works locally and 404s on a '
  'project subpath. The stylesheet is the **same file** the Jekyll site uses, so one sheet serves '
  'both and `aria-current` marks the current page identically. '
  '**An all-empty table header row is dropped rather than rendered:** the wiki writes its '
  'two-column link tables as `| | |`, and an empty `<th>` announces nothing useful to a screen '
  'reader. Demoting it to a body row was the first attempt and showed as a blank first row.'),

 ('- [ ] **"for deployment to pages"**',
  'CLOSED 0.12.94-dev — **and the URL answers, which is the standard the Backrooms deploy row sets '
  'and could not meet.** Pages configured on `main` / `/docs` via the API, status `built`, and '
  'verified by `curl -sI` rather than assumed: **200 on the index, 200 on a deep page, 200 on the '
  'stylesheet** at `https://g-fourteen.github.io/Rimrooms-AsyncIndustries/`, with the stylesheet’s '
  'Content-Length matching the source byte for byte. '
  '**`docs/.nojekyll` ships, and without it the deploy would have undone the decision.** Pages runs '
  'Jekyll over the published folder by default, which would reintroduce the build step this export '
  'exists to remove — and a Jekyll build that finds no `_config.yml` can fail the deployment '
  'outright rather than falling back to serving the files. '
  '**The live page fetches nothing:** zero `http` or `https` references in what GitHub actually '
  'serves, confirmed against the served bytes and not just the template. No webfont, no CDN, no '
  'analytics, no script — the same instinct as the package depending on nothing but Core.'),
]

text = io.open(TODO, encoding="utf-8").read()
problems = 0
for anchor, evidence in CLOSED:
    found = text.count(anchor)
    if found != 1:
        print("ANCHOR NOT UNIQUE (%d): %s" % (found, anchor[:90]))
        problems += 1
        continue
    at = text.index(anchor)
    line_end = text.index(NL, at)
    row = "- [x] " + text[at:line_end][len("- [ ] "):]
    text = text[:at] + row + " — **" + evidence + "**" + text[line_end:]
if problems:
    print("%d row(s) not touched; nothing written" % problems)
    sys.exit(1)
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text)
print("closed %d rows" % len(CLOSED))
