# -*- coding: utf-8 -*-
"""Record the twelve-ref direction verbatim and close it: procedure, tool and handoff all updated."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
NOW = "docs/NOW.md"

SECTION = NL.join([
"",
"## Owner direction — staging includes the mod-only repository (2026-10-05)",
"",
"**Verbatim owner direction (2026-10-05):** *\"and remember staging now includeds pushes to the mod only repo\"*",
"",
"**It was being done, and it was being done from memory, which is the thing worth fixing.** Every publication since 0.12.94-dev has pushed the mod-only pair — but **`docs/PUBLISHING.md` said nothing about it**, and that file is the cascade authority and the one document an agent is told to read instead of improvising. A step that is not in there is a step that gets forgotten, and the owner has already corrected improvised publishing once.",
"",
"**A publication that updates this repository and not that one leaves the published site and the downloadable mod behind — silently, with every instrument still green.**",
"",
"- [x] **\"staging now includeds pushes to the mod only repo\"** — **MADE STRUCTURAL 0.12.98-dev, in three places, because a rule in one place is a rule somebody can miss.** "
"**The procedure:** `PUBLISHING.md` opens with it now — publication is **twelve refs, not ten**: ten here across five branches on both remotes, plus two on `Rimrooms-AsyncIndustries`. Its **§7 one-screen version** is corrected too, and it had **two** faults of exactly the kind that pass silently: the loop pushed three integration branches and omitted `feature/connected-colony-portals`, producing the **eight-ref publish §5 warns about in its own words**, and it named no mod-only repository at all. "
"**The order is recorded with its reason:** the export runs **before** the commit here, because it is built from `artifacts/build/package-manifest.json` and verifies every file's SHA256 against the working tree, so it must run against the tree that was built and checked. "
"**The tool:** `export-public-repo.py --push` now **receipts its own push** — it reads both remotes back and refuses if either does not hold the export commit, because **`git push` exiting zero is not the same statement as *the remote holds this commit*.** That is the same discipline §5 exists for: nobody noticed an eight-ref publish was missing a branch for forty-five checkpoints. "
"**The handoff:** the standing cascade rule in `NOW.md` says twelve. "
"**And the refusal is documented as non-negotiable:** the exporter refuses for two real reasons "
"— a package edited after the build, or something in the export that must never be published "
"— and *“do not work around it”* is written next to them. It has refused twice "
"already, both times correctly, when a version bump landed after a build.",
"",
])

text = io.open(TODO, encoding="utf-8").read()
if "staging includes the mod-only repository" in text:
    print("section already present; nothing written")
    sys.exit(1)
if not text.endswith(NL):
    text += NL
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text + SECTION)
print("queue row recorded and closed")

now = io.open(NOW, encoding="utf-8").read()
OLD = ("- **THE CASCADE IS TEN REFS** — `forgejo` and `github` × "
       "`feature/bug-testing, feature/connected-colony-portals, Prep, Develop, Main`, "
       "pushed **by refspec from the feature branch**, never by creating local "
       "integration branches. It was five for two versions while the host was down and it "
       "is ten again. `PUBLISHING.md` is the authority; read it rather than improvising, "
       "which is the one thing the owner has corrected about publishing.")
NEW = ("- **THE CASCADE IS TWELVE REFS, NOT TEN.** Owner, 2026-10-05: *\"and remember staging now "
       "includeds pushes to the mod only repo\"*. **Ten here** — `forgejo` and `github` × "
       "`feature/bug-testing, feature/connected-colony-portals, Prep, Develop, Main`, pushed **by "
       "refspec from the feature branch**, never by creating local integration branches — **plus "
       "two** on `Rimrooms-AsyncIndustries` via `python tools/export-public-repo.py --push`, which "
       "**runs BEFORE the commit here** because it verifies every file's SHA256 against the build "
       "manifest and must see the tree that was built. **The exporter reads its own remotes back "
       "and refuses if either is behind**, because `git push` exiting zero does not mean the remote "
       "holds the commit. A publication that skips it leaves the published site and the "
       "downloadable mod behind with every instrument still green. `PUBLISHING.md` is the "
       "authority; read it rather than improvising, which is the one thing the owner has corrected "
       "about publishing.")
if now.count(OLD) != 1:
    print("NOW.md cascade bullet not found verbatim (%d); handoff NOT updated" % now.count(OLD))
    sys.exit(1)
io.open(NOW, "w", encoding="utf-8", newline=NL).write(now.replace(OLD, NEW, 1))
print("handoff cascade rule updated to twelve")
