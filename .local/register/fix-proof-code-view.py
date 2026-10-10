# -*- coding: utf-8 -*-
"""An absence claim read my own comment and called it code.

`"a.maxX == b.minX" not in planner` failed, correctly, because the comment explaining why that
test was WRONG quotes the test. That is the thirty-sixth instance of one defect class in this
project: **a claim about source text cannot tell code from prose about code**, and an absence
claim is where it bites, because prose about a removed thing is exactly what you write when you
remove it.

`check-compliance.py` already hit this from the other side -- it flagged a patch for containing
`PatchOperationReplace` in the comment explaining why a replace is wrong -- and the fix there was
the same: strip the comments first.

So this proof gets a `code()` view, and every absence claim reads it instead. Presence claims keep
reading the raw text: a thing that is present in the code is present in the file either way, and
stripping would only add a way to be wrong.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-coordinate-layout.py")

HELPER_ANCHOR = u'''planner = read(os.path.join(SRC, "Generation", "RoomLayoutPlanner.cs"))'''

HELPER = u'''def code(text):
    """The source with its comments removed.

    **An absence claim cannot read raw source.** `"a.maxX == b.minX" not in planner` failed
    against correct code, because the comment explaining why that test was wrong quotes it --
    which is exactly what a comment about a removed thing does. Thirty-six instances of this one
    defect class now, and `check-compliance.py` met it from the other side when it flagged a patch
    for naming `PatchOperationReplace` in the comment saying not to use one.

    Line comments and documentation comments only. A `//` inside a string literal would be
    mangled by this, and there is none in the files it reads; a claim is not the place to write a
    C# parser.
    """
    kept = []
    for line in text.split("\\n"):
        stripped = line.lstrip()
        if stripped.startswith("//"):
            continue
        kept.append(line)
    return "\\n".join(kept)


''' + HELPER_ANCHOR

BINDINGS_ANCHOR = u'''genstep = read(os.path.join(SRC, "Generation", "GenStep_BackroomsDestination.cs"))'''
BINDINGS = BINDINGS_ANCHOR + u'''

# Comment-free views, for absence claims only.
planner_code = code(planner)
service_code = code(service)'''

ABSENCE_OLD = u'''      and "a.maxX == b.minX" not in planner
      and "SharedDoorCell" not in planner,'''
ABSENCE_NEW = u'''      and "a.maxX == b.minX" not in planner_code
      and "SharedDoorCell" not in planner_code,'''

SECOND_OLD = u'''      "if (cell == SharedDoorCell" not in planner
      and "other.Bounds.minX > room.Bounds.maxX && cell.x == room.Bounds.maxX" in planner,'''
SECOND_NEW = u'''      "SharedDoorCell" not in planner_code
      and "other.Bounds.minX > room.Bounds.maxX && cell.x == room.Bounds.maxX" in planner,'''

CEILING_OLD = u'''      and "SlotRoomSpan(\\n                    RoomLayoutPlanner.SlotSpacing" not in service,'''
CEILING_NEW = u'''      and "RoomLayoutPlanner.SlotRoomSpan(" not in service_code,'''

EDITS = [
    (HELPER_ANCHOR, HELPER),
    (BINDINGS_ANCHOR, BINDINGS),
    (ABSENCE_OLD, ABSENCE_NEW),
    (SECOND_OLD, SECOND_NEW),
    (CEILING_OLD, CEILING_NEW),
]

text = io.open(PROOF, encoding="utf-8").read()
problems = []
for old, _ in EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:64]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    text = text.replace(old, new, 1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text)
print("proof now reads a comment-free view for every absence claim")
