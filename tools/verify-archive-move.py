"""Independently verify a queue -> FINALIZED move was verbatim and complete.

Named by `.claude/CONSTRAINTS.md §FINALIZED BEFORE DELETE` as the re-check of
`archive-finished-todo.py`'s own proof. Checks the result rather than trusting the
mover, against the snapshot the mover takes before it writes anything:

  1. The queue equals, byte for byte, the KEEP half recomputed from the snapshot.
  2. Every MOVED line appears in an archive region of docs/FINALIZED.md, in the
     same relative order (an ordered-subsequence walk, so a line cannot satisfy
     the check by matching some unrelated earlier copy).
  3. The multiset of all lines is conserved: snapshot == current queue + moved.
  4. docs/FINALIZED.md still contains every line it had before the append.
  5. The queue holds no [x] row at all.

Run it immediately after `archive-finished-todo.py --apply`, which writes the
snapshot this reads. `--backup <dir>` picks a specific one; the default is the
newest. Works on any queue tier, because the mover records which file its
snapshot came from.

Three outcomes, deliberately distinct:

  VERBATIM TRANSFER CONFIRMED   exit 0
  FAILED                        exit 1  one of the five checks did not hold
  STALE SNAPSHOT                exit 2  the baseline predates other edits to the
                                        queue, so nothing was checked -- see the
                                        note on `gained` below for why that is
                                        not the same thing as a failure

Until 2026-10-03 this hardcoded a single hand-made folder, `backup-20261002`, and
the mover wrote no snapshot at all, so the re-check the LAW promises worked on one
day and printed `FAILED` on every move after it.
"""

import collections
import importlib.util
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# `tools/`, alongside the mover; both moved out of gitignored `.local/qa/` on
# 2026-10-03 so the LAW's proof of verbatim transfer is version-controlled and
# reaches every machine. Snapshots stay machine-local where the mover writes them.
REPO = os.path.dirname(HERE)
BACKUPS = os.path.join(REPO, ".local", "qa")

spec = importlib.util.spec_from_file_location(
    "mover", os.path.join(HERE, "archive-finished-todo.py")
)
mover = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mover)


def pick_backup():
    """The snapshot to verify against: `--backup <dir>`, else the newest one.

    ## What this replaced, and why it mattered

    This read `BACKUP = os.path.join(HERE, "backup-20261002")` -- a single folder,
    copied by hand on one day. So this script verified the 2026-10-02 move and
    then, for every later move, compared a newer queue against that same older
    baseline and printed `FAILED`. The failure was arithmetic, not a finding: a
    queue that has legitimately changed since October 2nd cannot equal the KEEP
    half recomputed from October 2nd, and saying so tells nobody anything about
    whether a transfer was verbatim.

    **A safety instrument that always fails is worse than one that is absent**,
    because a red light nobody can act on is a red light people learn to ignore --
    and `.claude/CONSTRAINTS.md §FINALIZED BEFORE DELETE` names this script as the
    independent re-check of the only proof standing between a queue edit and a
    lost owner direction.

    The mover now writes `backup-<YYYYMMDD-HHMMSS>/` before it writes anything
    else, so the newest folder is the one belonging to the move just made. Sorted
    by name, which is chronological for both the new stamp and the legacy folder.
    """
    if "--backup" in sys.argv:
        named = sys.argv[sys.argv.index("--backup") + 1]
        folder = named if os.path.isabs(named) else os.path.join(REPO, named)
        if not os.path.isdir(folder):
            raise SystemExit("no such backup folder: %s" % folder)
        return folder
    if not os.path.isdir(BACKUPS):
        raise SystemExit("no snapshot folder at %s; run the mover with --apply first, "
                         "which writes one before it changes anything" % BACKUPS)
    found = sorted(name for name in os.listdir(BACKUPS)
                   if name.startswith("backup-") and os.path.isdir(os.path.join(BACKUPS, name)))
    if not found:
        raise SystemExit("no backup-* folder in %s; run the mover with --apply first, "
                         "which writes one before it changes anything" % BACKUPS)
    return os.path.join(BACKUPS, found[-1])


BACKUP = pick_backup()


def backed_up_queue():
    """Which queue this snapshot was taken from, repo-relative.

    Recorded by the mover so a `--queue docs/DECOMPOSED.md` move verifies on the
    same footing as a TODO move; this script used to assume `TODO.md` by name and
    therefore could not check a DECOMPOSED move at all, which `docs/NOW.md`
    documents as a normal thing to run. Legacy folders predate the stamp, and
    those were all TODO moves.
    """
    stamp = os.path.join(BACKUP, mover.QUEUE_STAMP)
    if not os.path.isfile(stamp):
        return "docs/TODO.md"
    return io.open(stamp, encoding="utf-8").read().strip() or "docs/TODO.md"


QUEUE_NAME = backed_up_queue()

BEGIN = "<!-- archived-queue:begin -->"
END = "<!-- archived-queue:end -->"
DONE_ROW = re.compile(r"^\s*- \[x\]")


def lines_of(path):
    return io.open(path, encoding="utf-8").read().split("\n")


failures = []

backup_todo = lines_of(os.path.join(BACKUP, os.path.basename(QUEUE_NAME)))
backup_final = lines_of(os.path.join(BACKUP, "FINALIZED.md"))
todo_now = lines_of(os.path.join(REPO, QUEUE_NAME))
final_now = lines_of(os.path.join(REPO, "docs", "FINALIZED.md"))

labels, _sections, _groups, _blocks, _untouched = mover.plan(backup_todo)
kept = [line for line, label in zip(backup_todo, labels) if label == mover.KEEP]
moved = [line for line, label in zip(backup_todo, labels) if label == mover.MOVE]

# A STALE SNAPSHOT IS NOT A FAILED TRANSFER, and conflating the two is what made
# this script useless.
#
# A verbatim move only ever REMOVES lines from the queue -- that is the whole
# content of the claim. So if the queue now holds a line the snapshot never had,
# the queue was edited by something other than the move, and this snapshot simply
# does not describe the current state. Every check below would then fail for
# arithmetic reasons that say nothing about whether a transfer was verbatim.
#
# Reported as its own outcome with its own exit code, because `FAILED` on a stale
# baseline is a red light nobody can act on, and those are the ones people learn
# to ignore.
gained = collections.Counter(todo_now) - collections.Counter(backup_todo)
gained = +collections.Counter({line: count for line, count in gained.items() if line.strip()})
if gained:
    sample = sorted(gained)[0]
    print("verify-archive-move")
    print("  queue verified           : %s" % QUEUE_NAME)
    print("  snapshot                 : %s" % os.path.relpath(BACKUP, REPO))
    print()
    print("STALE SNAPSHOT - nothing was checked")
    print("  %s holds %d line(s) this snapshot never had, and a move only ever"
          % (QUEUE_NAME, sum(gained.values())))
    print("  removes lines. So the queue was edited after the snapshot was taken and this")
    print("  baseline cannot describe the current state.")
    print("  first such line: %r" % sample[:100])
    print()
    print("  The mover writes its own snapshot before it changes anything, so run this")
    print("  immediately after `archive-finished-todo.py --apply`, or point it at the")
    print("  right folder with  --backup .local/qa/backup-<stamp>")
    sys.exit(2)

# 1 - the queue is exactly the KEEP half.
if todo_now != kept:
    failures.append("%s does not equal the recomputed KEEP half "
                    "(%d lines vs %d)" % (QUEUE_NAME, len(todo_now), len(kept)))
    for index, (left, right) in enumerate(zip(todo_now, kept)):
        if left != right:
            failures.append("  first difference at line %d:\n    got  %r\n    want %r"
                            % (index + 1, left[:100], right[:100]))
            break

# 2 - every moved line is in an archive region, in order.
#
# EVERY region, not the first. Each run of the mover appends another begin/end
# pair, so reading only the first one reported the second run's rows as missing.
# The regions are concatenated in file order, which is also the order the rows
# were moved in, so the ordered walk below still means what it says.
region = []
inside = False
found_any = False
for line in final_now:
    if line == BEGIN:
        inside = True
        found_any = True
        continue
    if line == END:
        inside = False
        continue
    if inside:
        region.append(line)
if not found_any:
    failures.append("docs/FINALIZED.md has no %s / %s region" % (BEGIN, END))

if region:
    cursor = 0
    unmatched = []
    for line in moved:
        if not line.strip():
            continue
        while cursor < len(region) and region[cursor] != line:
            cursor += 1
        if cursor >= len(region):
            unmatched.append(line)
            cursor = 0
        else:
            cursor += 1
    if unmatched:
        failures.append("%d moved lines are missing from the archive region, or are "
                        "out of order. First: %r" % (len(unmatched), unmatched[0][:110]))

# 3 - no line of the original queue was lost or invented.
if collections.Counter(backup_todo) != collections.Counter(todo_now) + collections.Counter(moved):
    failures.append("line multiset not conserved: backup != current TODO + moved")

# 4 - the archive only grew.
if final_now[:len(backup_final) - 1] != backup_final[:len(backup_final) - 1]:
    failures.append("docs/FINALIZED.md was altered above the append point")

# 5 - no finished row remains in the queue.
leftovers = [(index + 1, line) for index, line in enumerate(todo_now) if DONE_ROW.match(line)]
if leftovers:
    failures.append("%s still holds %d [x] rows; first at line %d"
                    % (QUEUE_NAME, len(leftovers), leftovers[0][0]))

print("verify-archive-move")
print("  queue verified           : %s" % QUEUE_NAME)
print("  snapshot                 : %s" % os.path.relpath(BACKUP, REPO))
print("  backup queue lines       : %d" % len(backup_todo))
print("  queue now                : %d" % len(todo_now))
print("  moved lines              : %d" % len(moved))
print("  archive region lines     : %d" % len(region))
print("  archive grew by          : %d lines" % (len(final_now) - len(backup_final)))
print("  [x] rows left in queue   : %d" % len(leftovers))
print()
if failures:
    print("FAILED")
    for failure in failures:
        print("  -", failure)
    sys.exit(1)
print("  1 queue == KEEP half             : byte-identical")
print("  2 moved lines in archive, in order: all present")
print("  3 line multiset conserved         : yes")
print("  4 archive altered above append    : no")
print("  5 finished rows left in queue     : none")
print()
print("VERBATIM TRANSFER CONFIRMED")
