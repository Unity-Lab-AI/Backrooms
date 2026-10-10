# -*- coding: utf-8 -*-
"""Append the public-export directions to the queue, verbatim, before any of it is built."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

SECTION = NL.join([
"",
"## Owner direction — a second pair of repos: the mod and the public face only (2026-10-05)",
"",
"**Verbatim owner direction (2026-10-05):** *\"okay do whats next and fyi the repo for the mod only",
"is :https://git.unityailab.com/GFourteen/Rimrooms-AsyncIndustries.git which should include only",
"public facing documents and wiki htmls for deploying the github.io static page  but for forgejo,",
"and the same thing for a github repo of the same name that you will make and set up to have only",
"the mod and only the public facing docs and wiki htmls for deployment to pages, do you",
"understand?\"*",
"",
"**Then, asked what goes in it, three clarifications in a row:** *\"make sure as far as what goes in",
"it is only what the game need to run the mod\"*, *\"ie what we stage\"*, and *\"what goes into the",
"game as the mod, idk , idk how to say it\"*.",
"",
"**It was said clearly enough.** The mod payload is the staged set, and that set is already",
"machine-readable: `artifacts/build/package-manifest.json` holds **103 files with a SHA256 each**,",
"and `tools/stage-mod.ps1` copies exactly that into the game folder. **The exporter reads the same",
"manifest**, so there is one definition of *the mod* and the public repo is hash-identical to what",
"the game runs. Measured: `About/` 3, `1.6/` 99 including the assembly, `LoadFolders.xml` 1.",
"",
"**Four forks were put to the owner before anything was built, and all four were answered:**",
"",
"- **Sync model — generated export, fresh history.** Backrooms stays the only place work happens;",
"  a tool builds the publish set and pushes it. **`git subtree split` was offered and argued",
"  against, and the owner agreed:** any commit that touched both a kept path and `docs/TODO.md`",
"  would carry the ledger into a public repo, which is the one thing this repo must not contain.",
"- **Wiki format — pre-rendered static HTML, no Jekyll.** *\"wiki htmls\"* meant what it said. No",
"  `_config.yml`, no build step, openable from disk, hostable anywhere.",
"- **Mod contents — the package including the committed assembly**, narrowed by the three",
"  clarifications above to exactly the staged manifest.",
"- **GitHub — `G-Fourteen/Rimrooms-AsyncIndustries`, PUBLIC**, with the owner's note *\"itylab ai",
"  but my personal\"*: the lab is Unity AI Lab, this repo is their personal account, mirroring the",
"  Forgejo path `GFourteen/Rimrooms-AsyncIndustries` exactly.",
"",
"**Measured before asking rather than assumed:** the Forgejo repo **already exists and is empty**",
"(`ls-remote` exits 0 with zero refs; a missing repo returns 128), so push-to-create being disabled",
"server-side is not a blocker. The GitHub repo did **not** exist under either account, and the",
"owner's account is org admin with `repo` scope, so it can be created from here.",
"",
"- [ ] **\"the repo for the mod only is :https://git.unityailab.com/GFourteen/Rimrooms-AsyncIndustries.git\"** — the Forgejo half. Push the export to the repo that already exists and is empty, by the procedure in `PUBLISHING.md` rather than improvised, and read the refs back as the receipt.",
"- [ ] **\"and the same thing for a github repo of the same name that you will make and set up\"** — create `G-Fourteen/Rimrooms-AsyncIndustries` PUBLIC and push the same export. **PUBLIC is not a preference here:** Pages does not serve from a private repo on a free plan, so the deploy would wait for ever.",
"- [ ] **\"which should include only public facing documents and wiki htmls for deploying the github.io static page\"** — and **only**. A checker must refuse the export outright if a ledger file, a prep document, an implementation record, a research document or anything under `.claude/` reaches it. A denylist nobody runs is the `_config.yml` mistake again.",
"- [ ] **\"only what the game need to run the mod\"** / **\"ie what we stage\"** / **\"what goes into the game as the mod\"** — the mod payload is the 103 files named in `artifacts/build/package-manifest.json`, **verified by SHA256 on the way out**, so an export cannot ship a file edited after the build. Same discipline the stager already enforces, for the same reason.",
"- [ ] **\"wiki htmls\"** — a renderer that turns the thirteen wiki pages into standalone static HTML with no Jekyll and no build step. It must **import the page order from `tools/build-site.py`** rather than keep a second copy of it, or the two indexes drift and that is the problem the generated nav exists to prevent.",
"- [ ] **\"for deployment to pages\"** — configure Pages on the new GitHub repo so the URL answers, which is the switch the Backrooms deploy row is still waiting on. Here the owner asked for it to be set up, so it is work rather than a switch to hand back.",
"",
])

text = io.open(TODO, encoding="utf-8").read()
if "a second pair of repos" in text:
    print("section already present; nothing written")
    sys.exit(1)
if not text.endswith(NL):
    text += NL
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text + SECTION)
print("appended %d lines, %d new open rows" % (SECTION.count(NL), SECTION.count("- [ ] ")))
