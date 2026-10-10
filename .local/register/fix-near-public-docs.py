# -*- coding: utf-8 -*-
"""Correct the three documents a person actually reads for current truth.

A top-of-document banner satisfies the rule. It does not satisfy a reader who lands on the
sentence. `PLAYING.md`, `MULTIPLAYER.md` and `COMPATIBILITY.md` are the three closest to public,
so their false sentences are corrected in place rather than covered.

And each gains a pointer to the wiki, which is now the player documentation. **One canonical
place, not two drifting copies** -- the same reason `PLAYING.md` itself was written once instead of
being duplicated onto a web page.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAYING = os.path.join(REPO, "docs", "PLAYING.md")
MULTIPLAYER = os.path.join(REPO, "docs", "MULTIPLAYER.md")
COMPAT = os.path.join(REPO, "docs", "COMPATIBILITY.md")

EDITS = [
    # -------------------------------------------------- PLAYING.md
    (PLAYING,
     u"""It is not a balance document, it is not a compatibility report, and it is not a play report. The
mod is developed against RimWorld 1.6 with **no hard dependencies and no Harmony**, it is
Core-only, and every expansion feature it touches is gated on that expansion being present.""",
     u"""It is not a balance document, it is not a compatibility report, and it is not a play report.

The mod is developed against RimWorld 1.6. **It declares hard dependencies**: all five
expansions and every mod in the collection it is built alongside, so a mod manager can name
anything missing before the game loads. Content from another mod is still looked up by name, so a
missing one degrades what depends on it rather than throwing."""),

    (PLAYING,
     u"""**This is the player-facing how-to.** [`HOWTO.md`](HOWTO.md) is the other one: it documents how the
mod is *built*. This page documents how it is *played*, and it is written once — the repository and
the public page use this file, not two drifting copies of it.""",
     u"""> **The player documentation is the [wiki](wiki/index.md).** Start there — it is shorter, it is
> organised for reading, and it is what the published site serves.
>
> This page is kept as the long-form working version behind it.

[`HOWTO.md`](HOWTO.md) is the other document: it covers how the mod is *built*, not how it is
played."""),

    # -------------------------------------------------- MULTIPLAYER.md
    (MULTIPLAYER,
     u"**This mod requires none of the above.** It is built Core-only with no hard dependencies, and it",
     u"**This mod requires none of the above for solo play.** Its declared requirements are the"),

    # -------------------------------------------------- COMPATIBILITY.md
    (COMPAT,
     u"**Selected support target:** RimWorld **1.6**. Core-only solo play is supported by design; Royalty, Ideology, Biotech, Anomaly, and Odyssey are optional integrations.",
     u"**Selected support target:** RimWorld **1.6**. **All five expansions and the whole collection are declared requirements** as of 2026-10-01; the earlier Core-only-with-optional-expansions target is superseded."),
]

problems = []
for path, old, new in EDITS:
    text = io.open(path, encoding="utf-8-sig").read()
    if text.count(old) != 1:
        problems.append("%d of %r in %s" % (text.count(old), old[:50], os.path.basename(path)))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for path, old, new in EDITS:
    text = io.open(path, encoding="utf-8-sig").read()
    io.open(path, "w", encoding="utf-8-sig", newline="").write(text.replace(old, new, 1))

playing = io.open(PLAYING, encoding="utf-8-sig").read()
multiplayer = io.open(MULTIPLAYER, encoding="utf-8-sig").read()
compat = io.open(COMPAT, encoding="utf-8-sig").read()

failures = []
if u"no hard dependencies and no Harmony" in playing:
    failures.append("PLAYING.md still claims no hard dependencies")
if u"wiki/index.md" not in playing:
    failures.append("PLAYING.md does not point at the wiki")
if u"built Core-only with no hard dependencies" in multiplayer:
    failures.append("MULTIPLAYER.md still claims Core-only")
if u"Core-only solo play is supported by design" in compat:
    failures.append("COMPATIBILITY.md still claims Core-only is supported")
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("three near-public documents corrected inline and pointed at the wiki")
