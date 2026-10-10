# -*- coding: utf-8 -*-
"""Staging is done. The handoff said it was pending, and that is now false.

`tools/stage-mod.ps1` refused while RimWorld was open, so the handoff was written with **STAGING
IS PENDING** as the first thing to do. The owner then authorised closing the game -- *"saves dont
matter shits getting remade they are always trash tests"* -- and the package is staged and
hash-verified against the game folder.

**A handoff that still says pending after it is done is the dated-claim defect**, which this
project has met repeatedly: a sentence that was true when written, read as current afterwards.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOW = os.path.join(REPO, "docs", "NOW.md")

HASH = u"5E87D3842B559E8ABCF44654D2178923D39D8EBE2A7D9F9D36A4FCAB441E39CC"

OLD_HEADER = u"## STATE AT THIS HANDOFF — `0.12.77-dev`, BUILT AND NOT YET STAGED"
NEW_HEADER = u"## STATE AT THIS HANDOFF — `0.12.77-dev`, STAGED AND VERIFIED"

OLD_BLOCK = u"""```
built       Rimrooms.AsyncIndustries  0.12.77-dev  92 files
assembly    __HASH__
            measured after the version bump, reproduced by two clean rebuilds
battery     16 checkers - 49 proofs - 20 plant suites - 752 anchors
            new suite: 12 of 12
tree        no planted fault, porcelain 0
```

### ⚠ STAGING IS PENDING AND THAT IS THE FIRST THING TO DO

`tools/stage-mod.ps1` **refused**: *"Close RimWorld before staging a new DLL."* The owner had the
game open. **The owner's fix is in this build and not in their game folder yet.** Re-run staging
once RimWorld is closed:

```
powershell -NoProfile -ExecutionPolicy Bypass -File tools/stage-mod.ps1 -UpdateExisting
```

Then read the hash back out of the game folder and confirm it matches the line above.
""".replace(u"__HASH__", HASH)

NEW_BLOCK = u"""```
staged      Rimrooms.AsyncIndustries  0.12.77-dev  92 files
assembly    __HASH__
            read back out of the game folder after staging, not from the build
package     294 declared dependencies, and the description names the wiki
battery     16 checkers - 49 proofs - 20 plant suites - 752 anchors
            new suite: 12 of 12
tree        no planted fault, porcelain 0
```

**Staging refused on the first attempt** -- *"Close RimWorld before staging a new DLL"* -- because
the owner had the game open with 3.8 GB resident. They authorised closing it: *"saves dont matter
shits getting remade they are always trash tests"*. `RimWorldWin64.exe` was stopped, the package
staged, and the hash read back out of the game folder matches the build.

**Refresh local mods in RimSort before launching.** The staged copy is current at this checkpoint.
""".replace(u"__HASH__", HASH)

text = io.open(NOW, encoding="utf-8").read()
problems = []
for old in (OLD_HEADER, OLD_BLOCK):
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:52]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
text = text.replace(OLD_BLOCK, NEW_BLOCK, 1).replace(OLD_HEADER, NEW_HEADER, 1)
io.open(NOW, "w", encoding="utf-8", newline="").write(text)

after = io.open(NOW, encoding="utf-8").read()
failures = []
if u"STAGING IS PENDING" in after:
    failures.append("the handoff still says staging is pending")
if NEW_HEADER not in after:
    failures.append("the header was not corrected")
if u"read back out of the game folder after staging" not in after:
    failures.append("the read-back is not recorded")
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("handoff corrected: staged and verified, with the read-back recorded")
