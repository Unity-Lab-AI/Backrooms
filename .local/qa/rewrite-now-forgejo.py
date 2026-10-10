# -*- coding: utf-8 -*-
"""Drop the Forgejo-down section from the handoff and record the recovery.

`docs/NOW.md` told its own reader to delete this section the day the host came
back. Doing that is the row working, not an override of it. The diagnosis it
carried is already in `docs/FINALIZED.md`, proved by claim count before this ran.
"""
import io
import sys

NL = chr(10)
PATH = "docs/NOW.md"

OPEN_ANCHOR = "## ⛔ FORGEJO IS DOWN. THE CASCADE IS GITHUB-ONLY UNTIL IT IS BACK ⛔"
END_ANCHOR = "## ⛔⛔ THE BATTERY RUNS ONCE, AND THE INSTRUMENTS STAY ⛔⛔"

REPLACEMENT = NL.join([
"## ⛔ FORGEJO IS BACK. THE CASCADE IS TEN REFS AGAIN ⛔",
"",
"**Owner, 2026-10-05, verbatim:** *\"okay read now.md to continue then first we need to make the",
"forgejo pushes, its back up and last cascade to forgejo was a while ago\"*",
"",
"It was back, and the first push attempted was the same one that had failed ten times. It was",
"accepted. Forgejo had been stuck at `2d0b677` (0.12.90-dev) for four commits; it is now at",
"`0c2712d` with GitHub, and **both remotes carry every commit.**",
"",
"**So the cascade is ten refs, and the count is the trap `PUBLISHING.md` §5 warns about in its own",
"words.** Push **by refspec from the feature branch** — never by creating local",
"`Prep`/`Develop`/`Main` branches, which that file names as a way previous agents have already got",
"this wrong:",
"",
"```",
"BRANCH=$(git rev-parse --abbrev-ref HEAD)      # never hard-code it",
"for r in forgejo github; do",
"  git push $r \"$BRANCH\"",
"  for b in Prep Develop Main feature/connected-colony-portals; do",
"    git push $r \"$BRANCH:$b\"",
"  done",
"done",
"git ls-remote --heads forgejo; git ls-remote --heads github; git rev-parse HEAD",
"```",
"",
"**The outage and its root cause are recorded in `docs/FINALIZED.md`**, not here — this file holds",
"one record and that one is finished. Read it before investigating any future Forgejo refusal: the",
"answer was `tmp_objdir_create()` on the server, and nothing on this machine changed between the",
"last failure and the first success. **An outage is recorded, not re-investigated.**",
"",
"---",
"",
])

text = io.open(PATH, encoding="utf-8").read()

for anchor in (OPEN_ANCHOR, END_ANCHOR):
    n = text.count(anchor)
    if n != 1:
        print("ANCHOR NOT UNIQUE (%d): %s" % (n, anchor[:60]))
        sys.exit(1)

start = text.index(OPEN_ANCHOR)
stop = text.index(END_ANCHOR)
removed = text[start:stop]
text = text[:start] + REPLACEMENT + text[stop:]

# The standing-rules bullet named the five-ref state as the rule. Replace the
# whole bullet rather than editing round it: a half-updated rule is worse than
# either version.
OLD_BULLET = ("- **THE CASCADE IS FIVE REFS WHILE FORGEJO IS DOWN** — `github` × "
              "`feature/bug-testing, feature/connected-colony-portals, Prep, Develop, Main`, "
              "pushed **by refspec from the feature branch**, never by forcing local branches. "
              "It is ten again the day the host returns. `PUBLISHING.md` is the authority; read "
              "it rather than improvising.")
NEW_BULLET = ("- **THE CASCADE IS TEN REFS** — `forgejo` and `github` × "
              "`feature/bug-testing, feature/connected-colony-portals, Prep, Develop, Main`, "
              "pushed **by refspec from the feature branch**, never by creating local "
              "integration branches. It was five for two versions while the host was down and it "
              "is ten again. `PUBLISHING.md` is the authority; read it rather than improvising, "
              "which is the one thing the owner has corrected about publishing.")
if text.count(OLD_BULLET) != 1:
    print("BULLET NOT FOUND VERBATIM; nothing written")
    sys.exit(1)
text = text.replace(OLD_BULLET, NEW_BULLET)

# The state table should say where the remotes are, because "is it published"
# is the first question a handoff is asked and it was unanswerable for two
# versions.
OLD_ROW = "| Launches | **At least twelve**, all by the owner. **Every defect any launch found was ours** |"
NEW_ROW = (OLD_ROW + NL +
           "| Remotes | **`0c2712d` on all TEN refs** — `forgejo` 5 of 5, `github` 5 of 5. "
           "Forgejo caught up 2026-10-05 after four commits down |")
if text.count(OLD_ROW) != 1:
    print("STATE ROW NOT FOUND VERBATIM; nothing written")
    sys.exit(1)
text = text.replace(OLD_ROW, NEW_ROW)

io.open(PATH, "w", encoding="utf-8", newline=NL).write(text)
print("NOW.md: removed %d chars / %d lines of spent instruction, wrote %d lines of current record"
      % (len(removed), removed.count(NL), REPLACEMENT.count(NL)))
print("        standing-rules bullet replaced, state table gained a Remotes row")
