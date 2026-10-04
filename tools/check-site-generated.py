# -*- coding: utf-8 -*-
"""Fail the battery when the published site's generated files are out of date.

Why this exists as a separate file
----------------------------------
`tools/build-site.py --check` already answers the question. **It is not a `check-*.py`, so a
battery that globs `tools/check-*.py` never ran it** -- and 0.12.93-dev had written into
`docs/_config.yml`, and into the queue row that closed, that `--check` *"fails the battery"*.
That was not true as written. This file makes it true rather than softening the claim.

**The generator stays a generator.** `build-site.py` writes two artefacts and can verify them;
renaming it to `check-*` would make a tool that edits the repository look like one that only
reads it, which is a worse lie than the one being fixed. So the battery gets an entry point and
the generator keeps its job.

What it covers, both through the generator
------------------------------------------
* `docs/_includes/nav.html` matches the pages actually in `docs/wiki/`.
* `docs/_config.yml`'s generated `exclude:` block names every entry at `docs/` root that is not
  part of the published site -- which is what stops Pages publishing the work ledger. It fails
  both ways: a document that is not excluded, and an exclude naming something that is gone,
  because a dead exclude reads as protection and gives none.

Usage
-----
    python tools/check-site-generated.py
"""
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENERATOR = os.path.join(REPO, "tools", "build-site.py")


def main():
    print("check-site-generated")
    if not os.path.isfile(GENERATOR):
        print("  tools/build-site.py is missing, so the generated site cannot be verified")
        print("")
        print("FAIL")
        return 1
    # Run it as the battery would run any other checker: by exit status, never by reading the
    # output. The generator's own words are printed so a failure says what to do about it.
    code = subprocess.call([sys.executable, GENERATOR, "--check"], cwd=REPO)
    print("")
    if code != 0:
        print("FAIL: the published site's generated files are out of date.")
        print("      Run python tools/build-site.py and commit the result.")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
