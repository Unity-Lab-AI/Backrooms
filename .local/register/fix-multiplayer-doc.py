# -*- coding: utf-8 -*-
"""Take the banner off `MULTIPLAYER.md` and re-aim one claim at the wiki.

`proof-integrations.py` failed two claims, and both are consequences of this session's own edits:

1. *"it says nothing has been tested, and says it in the opening line"* -- the supersession banner
   pushed that caveat past the first 200 characters. **The claim is right**: on a page about
   multiplayer, *nothing here has been tested* belongs at the top, not under a notice about
   dependencies. The banner is unnecessary there anyway, because the false sentence was already
   corrected inline.

2. *"it is held to the reader-facing rules"* -- `MULTIPLAYER.md` left `READER_FACING`. The concise
   public page is `docs/wiki/multiplayer.md`, which **is** in the set. `MULTIPLAYER.md` keeps the
   server detail a player does not need and a maintainer does: `AllowAllMods`, the forced
   scenario, the disposable-copy advice.

Re-aimed, not relaxed: the claim still demands that the page a reader opens is supervised.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MULTIPLAYER = os.path.join(REPO, "docs", "MULTIPLAYER.md")
PROOF = os.path.join(REPO, ".local", "register", "proof-integrations.py")

BANNER_START = u"> **Superseded 2026-10-01 — dependencies.**"

text = io.open(MULTIPLAYER, encoding="utf-8-sig").read()
lines = text.split(u"\n")
kept = []
dropping = False
removed = 0
for line in lines:
    if line.startswith(BANNER_START):
        dropping = True
        removed += 1
        continue
    if dropping:
        if line.startswith(u">"):
            removed += 1
            continue
        dropping = False
        if line.strip() == u"":
            removed += 1
            continue
    kept.append(line)
if removed == 0:
    print("NO BANNER FOUND IN MULTIPLAYER.md")
    raise SystemExit(1)
io.open(MULTIPLAYER, "w", encoding="utf-8-sig", newline="").write(u"\n".join(kept))
print("banner removed from MULTIPLAYER.md (%d line(s))" % removed)

OLD = u'''check("it is held to the reader-facing rules",'''
text = io.open(PROOF, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("PROOF ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)

# Find the whole claim so the condition can be replaced with the wiki one.
start = text.index(OLD)
end = text.index(u"\ncheck(", start + 1)
OLD_CLAIM = text[start:end]
NEW_CLAIM = u'''check("THE MULTIPLAYER PAGE A READER OPENS IS HELD TO THE READER-FACING RULES",
      'os.path.join(WIKI, "multiplayer.md")' in conformance
      and os.path.isfile(os.path.join(REPO, "docs", "wiki", "multiplayer.md")),
      "-- **re-aimed 2026-10-01.** The concise public page is `docs/wiki/multiplayer.md` and it "
      "is in the set; `MULTIPLAYER.md` keeps the server detail a player does not need and a "
      "maintainer does. Otherwise the vocabulary and wall rules skip the page people actually "
      "read")'''
io.open(PROOF, "w", encoding="utf-8", newline="").write(
    text[:start] + NEW_CLAIM + text[end:])

after = io.open(PROOF, encoding="utf-8").read()
failures = []
if u'os.path.join(WIKI, "multiplayer.md")' not in after:
    failures.append("the claim does not read the wiki page")
if u"conformance" not in after:
    failures.append("the claim no longer reads the conformance checker")
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("claim re-aimed at docs/wiki/multiplayer.md")
