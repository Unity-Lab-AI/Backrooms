# -*- coding: utf-8 -*-
"""Fail the battery if the public export would carry anything it must not.

Why this exists as a separate file
----------------------------------
`tools/export-public-repo.py` already refuses an unclean export -- that is where the audit lives.
But **a guard only somebody remembers to run is the `_config.yml` mistake again**: 0.12.93-dev
found a configuration file that *described* an exclusion policy it did not implement, and enabling
Pages would have published the whole work ledger. The lesson was that the rule has to be in the
battery, not in a comment and not in a tool nobody fires.

So this is the battery's entry point to the export audit. It builds the export and reports; it
never commits and never pushes, because a checker that mutates a remote is not a checker.

**It runs the real exporter rather than reimplementing the audit.** A second copy of the denylist
would be a second place the truth lives, and the one that drifted would be the one that mattered.

What makes it skip rather than fail
-----------------------------------
The export is assembled from `artifacts/build/package-manifest.json`, which only exists after a
build. On a fresh clone there is none, and **failing then would be reporting a defect that is not
there** -- the same reason `check-standalone-guarantee.py` skips when the game's own data is not
reachable. A skip says so out loud; it never prints PASS.

Usage
-----
    python tools/check-public-export.py
"""
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTER = os.path.join(REPO, "tools", "export-public-repo.py")
MANIFEST = os.path.join(REPO, "artifacts", "build", "package-manifest.json")


def main():
    print("check-public-export")
    if not os.path.isfile(EXPORTER):
        print("  tools/export-public-repo.py is missing, so the export cannot be audited")
        print("")
        print("FAIL")
        return 1
    if not os.path.isfile(MANIFEST):
        print("  no build manifest at artifacts/build/package-manifest.json.")
        print("  SKIPPED: the export is assembled from the manifest, so there is nothing to")
        print("           audit until a build has run. This is not a pass.")
        return 0

    # No --commit and no --push. Build the tree, run the audit, report the exit status.
    code = subprocess.call([sys.executable, EXPORTER], cwd=REPO)
    print("")
    if code != 0:
        print("FAIL: the public export would carry something it must not, or the mod payload")
        print("      does not match the build manifest. Read the refusal above.")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
