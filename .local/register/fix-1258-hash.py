# -*- coding: utf-8 -*-
"""The recorded assembly hash was measured before the version bump, so it was wrong.

`0.12.58-dev`'s determinism pass ran while the csproj still said `0.12.57-dev`, and the version
string is compiled into the assembly -- so the hash written into `docs/NOW.md`, `docs/TODO.md`
and `docs/FINALIZED.md` was the hash of a build that is not the one being published.

**Caught by printing the staged assembly's hash beside the commit rather than trusting the number
already written down.** Re-verified at the published version, deterministic across two clean
recompiles, and corrected in all three records.

THE ORDER THAT PREVENTS IT: bump the version FIRST, then measure. A hash is only evidence about
the artefact it was taken from.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

WRONG = u"521BCBE4EA437ED9A9BD93C5A054B1ADA4179F00A74303F89BADECCDAFCA6DC6"
RIGHT = u"F513B9D2B17ABF1B10DF36CED4B7DFE868B2FB423712338F1780F3BA2A5EEDA3"

total = 0
for name in ("NOW.md", "TODO.md", "FINALIZED.md"):
    path = os.path.join(REPO, "docs", name)
    text = io.open(path, encoding="utf-8").read()
    count = text.count(WRONG)
    if count == 0:
        print("  %-14s no stale hash" % name)
        continue
    io.open(path, "w", encoding="utf-8", newline="").write(text.replace(WRONG, RIGHT))
    after = io.open(path, encoding="utf-8").read()
    if WRONG in after:
        print("WRITE NOT VERIFIED in %s" % name)
        raise SystemExit(1)
    print("  %-14s %d corrected" % (name, count))
    total += count

print("stale hash replaced in %d place(s); the published assembly is %s" % (total, RIGHT))
