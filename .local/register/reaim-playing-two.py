# -*- coding: utf-8 -*-
"""Re-aim two claims whose exact sentences moved into the wiki pointer.

Both were asserting a real property by quoting the sentence that carried it:

* *"it distinguishes itself from the build how-to"* read for the words `documents how the mod is`,
* *"it is written once for both the repository and the site"* read for `written once`.

`PLAYING.md`'s header was rewritten to point at the wiki, so both phrases are gone and **both
properties are still true** -- there is still exactly one play document, and it still says which
document covers building instead.

**Re-aimed at the property, not restored as prose.** Putting the old sentences back to satisfy a
claim would be writing documentation for the checker rather than for the reader, which is the
inverse of the job.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-playing-and-help.py")

OLD = u'''check("it distinguishes itself from the build how-to",
      "documents how the mod is" in playing_flat and "howto.md" in playing_flat,
      "-- HOWTO.md already exists and is about building; two documents with one job is how the "
      "wrong one gets read")

check("it is written once for both the repository and the site",
      "written once" in playing_flat,
      "-- row 1193's own requirement")'''

NEW = u'''check("it distinguishes itself from the build how-to",
      "howto.md" in playing_flat
      and ("built" in playing_flat or "building" in playing_flat),
      "-- HOWTO.md already exists and is about building; two documents with one job is how the "
      "wrong one gets read. **Re-aimed 2026-10-01**: the header was rewritten to point at the "
      "wiki, so the property is asserted rather than the old sentence quoted")

check("THE PLAY DOCUMENTATION EXISTS ONCE, AND THIS POINTS AT IT",
      "wiki/index.md" in playing_flat
      and os.path.isfile(os.path.join(REPO, "docs", "wiki", "index.md")),
      "-- one canonical place, not two drifting copies. The requirement has not changed; the "
      "canonical place has. **Putting the old wording back to satisfy a claim would be writing "
      "documentation for the checker instead of the reader**")'''

text = io.open(PROOF, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))

after = io.open(PROOF, encoding="utf-8").read()
failures = []
if u'"written once" in playing_flat' in after:
    failures.append("the stale phrase claim is still there")
if u"THE PLAY DOCUMENTATION EXISTS ONCE, AND THIS POINTS AT IT" not in after:
    failures.append("the re-aimed claim was not written")
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("two claims re-aimed at the property rather than the retired sentence")
