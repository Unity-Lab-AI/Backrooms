# A description you can read (0.10.4-dev)

Part of the `0.10.4-dev` checkpoint, recorded separately because it is a different subject
from the register audit.

---

## The request

> *"real quick make this html open able : file:///…/About/About.xml as if i open this with edge to read it its all fucked up"*

> *"and its a massive text wall needs style formating and beautiful layout"*

> *"check for other shit text walls youve made too after you fix this one"*

> *"now the about.xml show a blank screen when i open it with edge and i still dont see the html versions"*

## What was wrong

The About description had become **a single unbroken line of 6,724 characters** — one sentence appended per checkpoint for twenty-odd checkpoints, never once re-read as a whole.

That is unreadable in any viewer, and far worse, unreadable in **RimWorld's own mod description panel**, which is where a player actually meets it.

Rewritten into four titled sections across 37 lines, and **half the length**, because most of what had accumulated was repetition.

## The first attempt was wrong, and made it worse

An XSLT stylesheet was added to About.xml so a browser would render it as a page.

**Chromium blocks XSLT loaded from a `file://` URL.** Edge showed a **blank page** — strictly worse than the raw XML it replaced. The owner reported it immediately.

Reverted completely: the stylesheet link, the `About.xsl` file and its allowlist entry are all gone. The mod package is back to exactly the files it shipped with.

**The lesson is not "XSLT is bad".** It is that a fix for *"I open this in Edge"* has to be tested against **how the file is actually opened**, and a local file opened from disk is a different security context from a page served over HTTP.

## What replaced it

`tools/make-readable-html.py` generates **standalone styled HTML** — styling inlined, no external references, no restriction on where it is opened from:

```
outputs/readable/index.html      every page, linked
outputs/readable/About.html      the mod description as a player sees it
outputs/readable/README.html
outputs/readable/CHANGELOG.html
outputs/readable/NOW.html
outputs/readable/TODO.html
outputs/readable/ROADMAP.html
```

Nothing there ships in the mod package, and it is regenerated rather than edited.

## The other walls

Sweeping every player-facing string found **42 over 220 characters**. Three mattered most:

| | Length | Where a player meets it |
|---|---|---|
| scenario description | 710 | the scenario picker, before anything else |
| setup welcome | 470 | first letter of a new game |
| start welcome | 430 | first letter of a new game |

All reflowed into paragraphs.

## And a rule, so they cannot come back

`check-info-cards.py` now fails the build on any displayed string past **420 characters with no paragraph break**, proved by planting a 510-character one.

**RimWorld renders newlines** in descriptions, letters and summaries — so a wall of text is a choice, not a limitation. Job strings, report strings, verbs, gerunds and labels are exempt, because those are meant to be one short line.

## A vocabulary leak the earlier rule missed

The sweep also caught **"the machine"** still meaning the gate in three places, including a research project description. The 0.10.2-dev rule banned `"machine gate"` but not `"the machine"`, because banning `machine` outright would have caught **machining table**, which is real Core content.

`"the machine"` is banned as a phrase now. The article is what makes it precise.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled twice from clean; identical SHA-256.
- All six checkers pass. Package back to **79 files** after the stylesheet was reverted.
- The wall rule proved by planting a wall; the vocabulary rule proved in 0.10.2-dev and extended here.

## For the post-completion test phase

Confirming the mod description reads as sections in RimWorld's own mod panel; that both welcome letters arrive as paragraphs rather than a block; and that the scenario picker shows a readable summary.
