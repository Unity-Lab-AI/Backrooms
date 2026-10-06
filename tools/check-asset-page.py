# -*- coding: utf-8 -*-
"""Battery entry point for the published asset page.

`tools/build-asset-page.py --check` already answers the question: the page on disk matches what the
package actually contains. **It is not a `check-*.py`, so a battery that globs `tools/check-*.py`
would never run it** -- the same gap `check-site-generated.py` and `check-public-register.py` exist
to close, and the same answer rather than a third one.

**Why it matters more than most generated artefacts.** Assets are being authored by more than one
party at once. A page claiming the package holds a drawing it no longer holds -- or missing one it
gained an hour ago -- is a published statement about shipped content that is simply false, and a
reader checks that page precisely because they cannot see inside the package.

Run from the repository root. Exits non-zero when the page is stale.
"""
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENERATOR = os.path.join(REPO, "tools", "build-asset-page.py")
PAGE = os.path.join(REPO, "docs", "wiki", "assets.md")


def main():
    print("check-asset-page")
    if not os.path.isfile(GENERATOR):
        print("  tools/build-asset-page.py is missing, so the published asset list cannot be")
        print("  verified against the package it describes.")
        print("")
        print("FAIL")
        return 1
    if not os.path.isfile(PAGE):
        print("  docs/wiki/assets.md does not exist, and the site index links to it.")
        print("")
        print("FAIL")
        return 1
    code = subprocess.call([sys.executable, GENERATOR, "--check"], cwd=REPO)
    if code != 0:
        print("")
        print("FAIL: the published asset list does not match the package.")
        return 1
    print("")
    print("PASS: the published asset list matches what the package ships")
    return 0


if __name__ == "__main__":
    sys.exit(main())
