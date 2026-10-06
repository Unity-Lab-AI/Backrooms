# -*- coding: utf-8 -*-
"""Battery entry point for the player-facing mod register.

`tools/build-public-register.py --check` already answers the question: every entry carries a tag
from the vocabulary, every cell is filled, and the generated page on disk matches what the register
would produce today. **It is not a `check-*.py`, so a battery that globs `tools/check-*.py` would
never run it** -- the exact gap `check-site-generated.py` was written to close for the site
generator, and the same answer is used here rather than a second one.

**The generator stays a generator.** Renaming it to `check-*` would make a tool that writes a
published page look like one that only reads, which is a worse lie than the gap being fixed.

Why it matters more than most generated artefacts: this page is **published**, it carries a claim
about **296 other people's mods**, and the owner's instruction was *"for all mods"*. A drifted copy
would tell a player that a mod they have installed does something it no longer does, which is worse
than saying nothing.

Run from the repository root. Exits non-zero when the page is stale or a row is incomplete.
"""
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENERATOR = os.path.join(REPO, "tools", "build-public-register.py")
PAGE = os.path.join(REPO, "docs", "wiki", "mods-list.md")


def main():
    print("check-public-register")
    if not os.path.isfile(GENERATOR):
        print("  tools/build-public-register.py is missing, so the published mod list cannot be")
        print("  verified against the register it is generated from.")
        print("")
        print("FAIL")
        return 1
    if not os.path.isfile(PAGE):
        print("  docs/wiki/mods-list.md does not exist. The mods page links to it, so the site")
        print("  would publish a link that goes nowhere.")
        print("")
        print("FAIL")
        return 1
    # By exit status, never by reading the output, exactly as the battery runs any other checker.
    code = subprocess.call([sys.executable, GENERATOR, "--check"], cwd=REPO)
    if code != 0:
        print("")
        print("FAIL: the published mod list does not match the register it is generated from.")
        return 1
    print("")
    print("PASS: the published mod list is current and every row is complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
