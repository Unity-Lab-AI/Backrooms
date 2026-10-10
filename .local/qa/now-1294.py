# -*- coding: utf-8 -*-
"""Targeted NOW.md update for 0.12.94-dev.

The file is a one-record handoff, rewritten each publication. The standing-rule sections survive;
the state table, the what-changed list, the next thing and the lesson list are replaced.
"""
import io

NL = chr(10)
P = "docs/NOW.md"
t = io.open(P, encoding="utf-8").read()
before = len(t)


def swap(old, new, label):
    global t
    if t.count(old) != 1:
        raise SystemExit("NOT UNIQUE (%d): %s" % (t.count(old), label))
    t = t.replace(old, new, 1)


swap("| Version | **0.12.93-dev** — read from `About.xml`, never from a document |",
     "| Version | **0.12.94-dev** — read from `About.xml`, never from a document |",
     "version row")
swap("| Instruments | **20 checkers**, **57 proofs**, **31 plant suites**, **1091 plant anchors** |",
     "| Instruments | **21 checkers**, **58 proofs**, **32 plant suites** |",
     "instruments row")
swap("| Queue | **49 open · 20 partial · 38 `[T]` · 0 `[x]`** |",
     "| Queue | **49 open · 20 partial · 38 `[T]` · 0 `[x]`** |" + NL +
     "| Public repos | **`Rimrooms-AsyncIndustries` on BOTH hosts** — `forgejo "
     "GFourteen/...` and `github G-Fourteen/...`, `main` at one commit. **The mod as staged, "
     "the public face, nothing else** |" + NL +
     "| Published site | **LIVE** — `https://g-fourteen.github.io/Rimrooms-AsyncIndustries/`, "
     "200 on the index, a deep page and the stylesheet |",
     "queue row")
swap("- **At publication, once:** 20 checkers → 57 proofs → 31 plant suites.",
     "- **At publication, once:** 21 checkers → 58 proofs → 32 plant suites.",
     "battery line")
swap("- **Batch size is 10–12 closed rows.** 0.12.93 closed **nine** and noted four.",
     "- **Batch size is 10–12 closed rows.** 0.12.93 closed nine and noted four; 0.12.94 closed "
     "**six**, every one of a single owner direction.",
     "batch line")

CHANGED = NL.join([
"## What 0.12.94-dev changed",
"",
"**One owner direction, six rows, and two defects it uncovered in the mod itself.**",
"",
"1. **TWO NEW REPOSITORIES HOLD THE MOD AND NOTHING ELSE**, on both hosts, and **the published site is live** — 200 on the index, a deep page and the stylesheet, verified with `curl -sI`. That is the standard the Backrooms deploy row sets and has never met.",
"2. **ONE DEFINITION OF THE MOD, AND IT WAS ALREADY MACHINE-READABLE.** The payload is the 103 files in `artifacts/build/package-manifest.json` — the same list `stage-mod.ps1` copies — with **every SHA256 verified on the way out**. So *what we stage* and *what we publish* cannot drift. **It refused this batch** when `About.xml` was edited after the build.",
"3. **AN ALLOWLIST DECIDES, A DENYLIST REFUSES THE RESULT, AND BOTH RUN.** The second pass refused the first export it ever saw: `CHANGELOG.md` is a development log and does not ship. The working README does not ship either — **every link in it is wrong there** — so the export generates its own from `About.xml` and refuses if a link would dangle.",
"4. **THE MOD TOLD EVERY PLAYER IT NEEDS 294 MODS, AND IT NEEDS NONE.** `About.xml` has declared zero dependencies since 0.12.86-dev while its description still said it *\"declares every member of it as a dependency\"*. **It is the most-read document this mod has, and nothing checked it**, because the checker globs `.md`.",
"5. **Found by reading generated output, not by auditing.** The export's readme said *\"Needs no other mod and no expansion\"* two lines above a section demanding five expansions. Nothing had ever put those two sentences side by side.",
"6. **`About.xml`'s description is now held to the full claims rules**, including a **new inverse dependency rule** — with nothing declared, *asserting* a dependency is the finding — and it immediately caught a second defect: the description said **\"doorway\"** to a player, banned everywhere else since 0.10.2-dev.",
"7. **The wiki renders to standalone static HTML**, no Jekyll and no build step, **importing the reading order from `build-site.py` rather than copying it**. `docs/.nojekyll` ships, or Pages rebuilds it with Jekyll and can fail outright.",
"8. **`git subtree split` was offered, argued against and declined** — it would have published hundreds of commits of `docs/TODO.md`.",
"",
])
start = t.index("## What 0.12.93-dev changed")
end = t.index("## THE NEXT THING")
t = t[:start] + CHANGED + t[end:]

NEXT = NL.join([
"## THE NEXT THING",
"",
"**The public face is done and live.** What remains of it is authoring, not plumbing: a",
"**player-facing changelog** for the public repository — deliberately not faked by filtering the",
"development one — and the **Workshop page and collection**, which the queue already orders behind",
"a working site.",
"",
"**Then the four expansion rows**, each needing a decision about what the *optional* version of",
"genes, rituals, or a gravship that carries a branch actually is. These are the largest open design",
"questions left and they are not measurement jobs.",
"",
"**T5/T6 of the research tree is a knob sweep**, not an authoring job: 274 tunable constants exist",
"and 34 are claimed, but a tier may only exist where a player could *name the effect*.",
"",
"Then: **entity/anomaly design sheets as authored documents**; **vehicles and the VGE hooks**; and",
"the **world-tile rows**, which need a new world object and a generated map.",
"",
"**And the two starting-goods rows wait on a launch, not on code.** They are the only rows whose",
"next step is a `Player.log`.",
"",
"**One thing worth the owner's attention, blocking nothing:** Backrooms still carries its own Jekyll",
"site under `docs/`, and the public deploy now lives in the new repository. Enabling Pages on",
"Backrooms is no longer needed for the wiki to reach anybody. That row stays open and the switch is",
"still the owner's; it is simply no longer the only route.",
"",
])
start = t.index("## THE NEXT THING")
end = t.index("## Read these before touching anything")
t = t[:start] + NEXT + t[end:]

anchor = "## Read these before touching anything" + NL + NL
NEW_LESSONS = NL.join([
"- **A WORD BEING PRESENT IS NOT THE WORD DOING ANYTHING. THREE MORE THIS BATCH, EVERY ONE CAUGHT BY ITS PLANT.** A regex with word boundaries cannot match inside `git_subtree_split`, because an underscore is a word character. `\"--push\" in sys.argv` appears twice, so containment survived a plant that deleted the push guard entirely. And `stash` is a nested function's own name, so it stayed when the call using it was removed. **Assert the call, the whole anchored statement, or the condition — never the identifier.**",
"- **A GENERATED ARTEFACT IS THE BEST AUDIT YOU WILL EVER RUN.** The mod telling every player it needs 294 mods had survived six versions of a checker written to catch stale claims. It was found by generating a readme from that text and reading the result, where the contradiction sat two lines apart. **Render the thing and look at it.**",
"- **A PLANT SUITE THAT TOUCHES A FILE WITH A BOM MUST USE BYTES.** `io.open(..., \"w\", encoding=\"utf-8\")` strips one silently, which is how three were lost. `plant-public-export.py` reads and writes bytes throughout, and the BOM survived 29 plants.",
"- **A GUARD BELONGS IN THE BATTERY, NOT ONLY IN THE TOOL THAT KNOWS ABOUT IT.** The export audit lives in the exporter; `check-public-export.py` is what makes the battery run it. A guard only somebody remembers to fire is the `_config.yml` mistake with a different filename.",
"- **IMPORT, NEVER COPY, ANYTHING TWO GENERATORS AGREE ABOUT.** The static renderer imports `SECTIONS`, `page_title` and `page_summary` from `build-site.py`. A copied reading order drifts the first time a page is added, and then the two sites disagree about what the wiki is.",
"- **WHAT GOES IN A PUBLIC REPOSITORY IS DECIDED TWICE.** An allowlist assembles it; a denylist then refuses the assembled tree. The second pass is not redundant — it is the one that catches a mistake in the first, and it did so on its first run.",
"",
])
swap(anchor, anchor + NEW_LESSONS, "lesson anchor")

io.open(P, "w", encoding="utf-8", newline=NL).write(t)
print("NOW.md: %d -> %d chars" % (before, len(t)))
