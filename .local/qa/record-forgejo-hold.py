# -*- coding: utf-8 -*-
"""Record the Forgejo hold as a queue row with the owner's verbatim words."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)
ANCHOR = "### Owner direction — the solo start's way out must be found, not handed over (2026-10-06)"

S = NL.join([
"### Owner direction — Forgejo is going down; push GitHub only (2026-10-06)",
"",
"**Verbatim owner direction (2026-10-06):** *" + Q + "fyi the git.unityailab.com is going down so "
"stop pushes to it until further notice, github two repos is still good" + Q + "*",
"",
"- [x] **HELD, NOT REMOVED, AND LOUDLY. 0.12.99-dev.** The cascade is **six refs** while the hold "
"stands: `github` × five branches here, plus `github/main` on the mod-only repository. **Zero to "
"forgejo, both repositories.** "
"**The distinction between held and removed is the whole point.** Deleting the remote would make "
"every receipt read *complete*, and a future reader would never learn a destination had gone "
"missing — which is exactly the eight-ref publication that went unnoticed for forty-five "
"checkpoints, wearing a different hat. So `tools/export-public-repo.py` keeps `forgejo` in "
"`REMOTES`, skips it by name through `HELD_REMOTES`, **prints the hold and its reason on every "
"run**, and **refuses outright if every remote is held** — a publication with no destination must "
"not report success. `PUBLISHING.md` opens with the hold so nobody re-adds it from habit. "
"**Restored by the owner saying the host is back — never by time passing, and never because a push "
"happens to succeed.** The procedure also says not to push to it in order to *test* whether it is "
"up: a push that half-succeeds against a host mid-shutdown is how a remote ends up holding a commit "
"nobody recorded. "
"**And the twelve-ref receipt is not weakened for GitHub.** Each active remote is still read back by "
"`ls-remote` and still has to hold the exact commit; the count simply says *of the active remotes*, "
"with the held one named beside it.",
"",
])


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    if "Forgejo is going down" in text:
        print("already recorded")
        return 1
    if text.count(ANCHOR) != 1:
        print("anchor matched %d time(s); refusing" % text.count(ANCHOR))
        return 1
    at = text.index(ANCHOR)
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(text[:at] + S + NL + text[at:])
    print("Forgejo hold recorded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
