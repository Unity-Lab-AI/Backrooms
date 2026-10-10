# -*- coding: utf-8 -*-
"""Prepend the 0.12.94-dev entry. CHANGELOG.md has no BOM and must keep none."""
import io
import sys

NL = chr(10)
PATH = "CHANGELOG.md"
HEADING = "# Changelog"

ENTRY = NL.join([
"## 0.12.94-dev - 2026-10-05 - The mod and its public face get their own pair of repositories",
"",
"- **TWO NEW REPOSITORIES, HOLDING THE MOD AND NOTHING ELSE.** Owner: *\"the repo for the mod only",
"  is :https://git.unityailab.com/GFourteen/Rimrooms-AsyncIndustries.git which should include only",
"  public facing documents and wiki htmls for deploying the github.io static page but for forgejo,",
"  and the same thing for a github repo of the same name that you will make and set up\"*. The",
"  Forgejo repository already existed and was empty; `G-Fourteen/Rimrooms-AsyncIndustries` was",
"  created PUBLIC, and both now hold the same export.",
"- **PAGES IS LIVE AND THE URL ANSWERS**, which is the standard the Backrooms deploy row sets and",
"  has never met: 200 on the index, 200 on a deep page, 200 on the stylesheet at",
"  `https://g-fourteen.github.io/Rimrooms-AsyncIndustries/`, verified with `curl -sI` rather than",
"  assumed, with the stylesheet's Content-Length matching the source byte for byte.",
"- **ONE DEFINITION OF \"THE MOD\", AND IT WAS ALREADY MACHINE-READABLE.** Asked what goes in, the",
"  owner said *\"only what the game need to run the mod\"*, *\"ie what we stage\"*, *\"what goes into",
"  the game as the mod\"*. `artifacts/build/package-manifest.json` holds **103 files with a SHA256",
"  each** and `stage-mod.ps1` copies exactly that; the exporter reads **the same manifest**, so",
"  what we stage and what we publish cannot drift. Every hash is verified on the way out and every",
"  copy is read back. **It refused this very batch** when `About.xml` was edited after the build.",
"- **AN ALLOWLIST DECIDES AND A DENYLIST REFUSES THE RESULT, AND BOTH RUN.** 0.12.93-dev learned",
"  the cost of a policy that was only described. The second pass refused the first export it ever",
"  saw: **`CHANGELOG.md` contains \"VERBATIM TRANSFER CONFIRMED\"**. It is a development log, and the",
"  owner's rule for public documents is *\"no actual work information\"* -- so it does not ship, and",
"  a player-facing *what is new* is recorded as authoring work rather than faked by filtering this.",
"- **The working README does not ship either, for a different reason.** It is clean of internal",
"  vocabulary, but **every link in it is wrong there**: `docs/wiki/*.md`, `CONTRIBUTING.md`,",
"  `docs/BUILDING.md`. The export generates its own from `About.xml` and **refuses if any link",
"  would point at a page the export does not have**.",
"- **The refusals are named rather than implied:** the ledger filenames in `.md` and `.html` form,",
"  `.claude/`, `.local/`, `implementation/`, `research/`, `src/`, `tools/`, the archive's transfer",
"  banner as *text* under any filename, and **a queue row's own shape anywhere in the tree**.",
"- **`git subtree split` was offered to the owner, argued against, and declined.** Backrooms'",
"  history carries the ledger in essentially every commit, so a split would have published",
"  hundreds of commits of `docs/TODO.md`. The export repository starts its own history.",
"- **THE MOD TOLD EVERY PLAYER IT NEEDS 294 MODS, AND IT NEEDS NONE.** `About.xml` has declared",
"  **zero** `modDependencies` since 0.12.86-dev, but its description still said the build",
"  *\"declares every member of it as a dependency\"*, naming all five expansions and 288 mods. That",
"  is the most-read document this mod has -- it is what a player sees in the mod list before",
"  deciding whether they can run it at all -- and **it was the one document nothing here checked**,",
"  because `living_docs()` globs `.md`. It survived six versions of a checker written to catch",
"  exactly this.",
"- **Found by reading generated output, not by auditing.** The export's readme said *\"Needs no",
"  other mod and no expansion\"* two lines above a section demanding five expansions. A",
"  contradiction that blatant survived because nothing had ever put the two sentences side by side.",
"- **`check-doc-conformance.py` now holds `About.xml`'s description to the same claims rules as a",
"  reader-facing document:** version, branch, retired defs, checker count, banned vocabulary, the",
"  expansion-optional rule, and a **new** inverse dependency rule -- with nothing declared, a",
"  document asserting a dependency is the finding. Which direction applies is read off `About.xml`",
"  itself, never typed. It immediately caught a second defect: the description said **\"doorway\"**",
"  to a player, which the vocabulary rule has banned everywhere else since 0.10.2-dev.",
"- **`tools/render-wiki-html.py` renders the thirteen pages to standalone static HTML** -- no",
"  Jekyll, no `_config.yml`, no build step, no network -- and **imports `SECTIONS`, `page_title`",
"  and `page_summary` from `tools/build-site.py` rather than copying them**, so the two sites",
"  cannot disagree about what the wiki is.",
"- **`make-readable-html.py` could not be reused, for a specific reason:** it emits one `<p>` per",
"  source line, and every wiki page is hard-wrapped near ninety characters, so a four-line",
"  paragraph would have rendered as four. It also has no blockquote, and blockquote is the wiki's",
"  callout. One tool pretending to do both jobs is how the published site would quietly look wrong.",
"- **Output is flat**, so every link is a sibling and the stylesheet is one path from everywhere; a",
"  nested directory means `..` in some links and not others, which works locally and 404s on a",
"  project subpath. The stylesheet is the **same file** the Jekyll site uses.",
"- **An all-empty table header row is dropped rather than rendered.** The wiki writes its",
"  two-column link tables as `| | |`, and an empty `<th>` announces nothing useful to a screen",
"  reader. Demoting it to a body row was the first attempt and showed as a blank first row.",
"- **`docs/.nojekyll` ships, and without it the deploy would have undone the decision.** Pages runs",
"  Jekyll over the published folder by default, reintroducing the build step this export exists to",
"  remove -- and a Jekyll build that finds no `_config.yml` can fail the deployment outright.",
"- **The live page fetches nothing.** Zero `http` or `https` references in what GitHub actually",
"  serves, checked against the served bytes rather than the template. No webfont, no CDN, no",
"  analytics, no script.",
"- **`tools/check-public-export.py` makes the audit the battery's business**, because a guard only",
"  somebody remembers to run is the `_config.yml` mistake again. It runs the real exporter rather",
"  than reimplementing the denylist, never commits, never pushes, and **skips rather than failing**",
"  when there is no build to export -- a skip that says so out loud and never prints PASS.",
"- **Three of my own claims were too weak in the same way, and the plants caught all three:**",
"  `\\bsubtree\\b` cannot match inside `git_subtree_split` because an underscore is a word",
"  character; `\"--push\" in sys.argv` appears twice, so containment survived deleting the push",
"  guard; and `stash` is the nested function's own name, so it stayed when the call that used it",
"  was removed. **A word being present is not the word doing anything** -- the lesson written into",
"  the handoff earlier in this same session.",
"- **One plant was unrealistic as well as uncaught:** the subtree-split plant used an identifier",
"  name, which is not how anybody writes a subtree split. Both the plant and the claim were wrong.",
"- **The new plant suite reads and writes BYTES**, because it plants into `About.xml`, which has a",
"  byte-order mark that `io.open(..., \"w\", encoding=\"utf-8\")` would silently strip -- the exact",
"  defect recorded when a version bump stripped three BOMs. Verified: the BOM survived 29 plants.",
"- New instrument pair: `proof-public-export.py` **59 of 59** with `plant-public-export.py` **29 of",
"  29**. **Totals: 21 checkers, 58 proofs, 32 plant suites.**",
"- Build 0.12.94-dev, **232 C# files, 103 package files, 0 warnings, 0 errors**. Six rows closed",
"  and archived with `VERBATIM TRANSFER CONFIRMED`; queue **49 open / 20 partial / 38 test / 0",
"  completed**. **No game was launched, and nothing here has been played.**",
"",
])

raw = io.open(PATH, "rb").read()
if raw.startswith(b"\xef\xbb\xbf"):
    print("CHANGELOG.md has a BOM and should not; refusing to write")
    sys.exit(1)
text = raw.decode("utf-8")
if not text.startswith(HEADING):
    print("CHANGELOG.md does not open with %r" % HEADING)
    sys.exit(1)
if "0.12.94-dev" in text:
    print("already present; nothing written")
    sys.exit(1)
rest = text[len(HEADING):].lstrip(NL)
io.open(PATH, "wb").write((HEADING + NL + NL + ENTRY + NL + rest).encode("utf-8"))
if io.open(PATH, "rb").read().startswith(b"\xef\xbb\xbf"):
    print("a BOM was added -- ABORT")
    sys.exit(1)
print("prepended %d lines; no BOM added" % ENTRY.count(NL))
