# -*- coding: utf-8 -*-
"""Close the arrangements row and the new-art rows. Status marker only."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

CLOSED = [
 ('- [ ] **"so its more rooma corradors facilites infastructure roads neighborrs hood malls shoopping centers military"**',
  'CLOSED 0.12.84-dev. **Both halves now exist: the kinds, and the arrangements.** The kinds '
  'landed at 0.12.83-dev; this row stayed open because its own text was right that *"roads"* and '
  '*"neighborrs hood"* are **arrangements of rooms**, not room shapes.\n\n'
  '  **A road is `RoomLayoutPlanner.OnRoad`** — a straight run of linked rooms that carries on '
  'past at least one of its ends, and every corridor along it is cut at the **wide** half-width '
  'whatever its own roll said. That is the part that makes a through-line read as a road; before '
  'it, a run existed and looked like a chain of ordinary hallways. Derived from the saved graph '
  'and stored nowhere, so the carver, the reachability proof and the probe cannot disagree.\n\n'
  '  **A ROAD BRAID WAS WRITTEN AND THEN DELETED, MEASURED.** A pass that picked a row and linked '
  'every slot along it moved the longest straight run **not at all** — 6 to 8 either way, which '
  'at depth 3 and deeper is the entire slot row. At an average of five links per room the braids '
  'already join almost every adjacent collinear pair. The comment recording that is in the source '
  'so nobody writes it again.\n\n'
  '  **A neighbourhood is a block pressed wall to wall off one hub**, and getting it to work took '
  'two findings, both from the probe. It must run **before** the diagonal and reach braids: a '
  'room holding five or six links cannot slide at all, because `PushAgainst` undoes any move that '
  'carries one past `FurthestLinkedCentres`, and placed after them the whole pass measured as a '
  'no-op — largest group 3 with it and 3 without. And the hub’s neighbours are offered '
  '**least-connected first**, so the mobile ones are tried before the hopeless ones shift the '
  'geometry. Measured after both: back-to-back pairs **248 → 376** at depth 1 and **366 '
  '→ 488** at depth 3, with blocks of four. Nothing was relaxed — every move still has to '
  'satisfy all four of `PushAgainst`’s conditions or be undone.\n\n'
  '  **And it exposed a real leak in the prune.** `PruneUnroutableLinks` refused to touch any '
  'link whose centres shared an axis, reasoning that the spanning tree is non-diagonal so '
  'removing only diagonals cannot disconnect the level. True, and too coarse: the reach braid '
  'makes links two slots apart **along** an axis and the push can leave one routeless. The probe '
  'printed `link 2-6 has no route under it`. It now removes the edge and keeps the removal only '
  'if every room still claiming a route can still be reached from the threshold — exact, and '
  'those refusals are gone.'),
]

text = io.open(TODO, encoding="utf-8").read()
problems = 0
for anchor, evidence in CLOSED:
    found = text.count(anchor)
    if found != 1:
        print("ANCHOR NOT UNIQUE (%d): %s" % (found, anchor[:92]))
        problems += 1
        continue
    at = text.index(anchor)
    end = text.find(NL + "- [", at + 1)
    if end == -1:
        end = text.index(NL + NL, at)
    row = text[at:end]
    row = "- [x] " + row[len("- [ ] "):]
    text = text[:at] + row + " — **" + evidence + "**" + text[end:]

if problems:
    sys.exit(1)
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text)
print("closed %d row(s)" % len(CLOSED))
