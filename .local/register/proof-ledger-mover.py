# -*- coding: utf-8 -*-
"""The ledger mover's orphan sweep must never separate a heading from its own content.

Why this exists
---------------
**A wrong fix to `sweep_orphans` shipped on 2026-10-06 and was caught by eye, not by an
instrument.** Measuring a heading's body to the next *anchor* counted a `**...:**` lead-in as the
end of the section, so four headings in `docs/TEST.md` were swept **away from their own content**,
leaving the owner's verbatim quotes standing under nothing. That is the stranded-body defect the
sweep exists to prevent, produced by the sweep.

**Nothing could have caught it.** `tools/archive-finished-todo.py` is the instrument
`.claude/CONSTRAINTS.md §FINALIZED BEFORE DELETE` names as the proof of verbatim transfer, and it
had **no plant suite and no proof of its own**. Worse, the two guards that look closest both pass:

  * the mover's **reassembly identity** holds, because every line is still either kept or moved --
    *where a line goes is not the thing that proof proves*;
  * `check-queue-integrity` rule 1 looks for an **indented** continuation with no owning bullet, and
    an orphaned paragraph under a removed heading is not indented.

So this asks the question directly, against crafted input rather than against whatever the real
ledgers happen to contain today: **does the sweep give a heading and its body the same label?**

What it proves
--------------
  1. A heading whose body is a lead-in and prose is **kept whole** -- heading and body together.
  2. A heading with nothing at all under it **is swept**, which is the residue case the sweep was
     extended for: `docs/TEST.md` carried one such heading from the day it was created.
  3. A heading whose body still holds a kept row is **never** swept, which is the original rule.

Run by exit status. Never by reading the output.
"""
import importlib.util
import io
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
MOVER = os.path.join(REPO, "tools", "archive-finished-todo.py")

spec = importlib.util.spec_from_file_location("rr_mover", MOVER)
mover = importlib.util.module_from_spec(spec)
sys.modules["rr_mover"] = mover
spec.loader.exec_module(mover)

KEEP, MOVE = mover.KEEP, mover.MOVE

failures = []


def label_run(lines, preset=None):
    """Run the sweep over `lines` with an optional starting label map."""
    labels = list(preset) if preset else [KEEP] * len(lines)
    mover.sweep_orphans(lines, labels)
    return labels


def check(name, condition, detail=""):
    print("  %-62s %s" % (name, "OK" if condition else "FAILED"))
    if not condition:
        failures.append("%s%s" % (name, (" -- " + detail) if detail else ""))


print("proof-ledger-mover")

# ---------------------------------------------------------------- 1. a heading with a lead-in body
#
# This is the exact shape that was mis-swept: heading, blank, a bold line ENDING IN A COLON, then
# the owner's words. The lead-in is an anchor, so a naive body measurement stops at it.
with_lead_in = [
    "### Owner direction - something the owner said (2026-10-06)",
    "",
    "**Verbatim owner direction (2026-10-06), four messages in a row.** The first:",
    "",
    "> *\"the owner's actual words, which must not be left standing under nothing\"*",
    "",
]
labels = label_run(with_lead_in)
heading_kept = labels[0] == KEEP
body_kept = all(labels[i] == KEEP for i in range(1, len(with_lead_in)))
check("a heading whose body is a lead-in and prose is kept", heading_kept and body_kept,
      "labels were %r; a lead-in is part of the section it introduces" % (labels,))

# **AND THE HEADING MUST NEVER MOVE WITHOUT ITS BODY.** Stated as its own assertion rather than
# inferred from the one above, because that separation is the defect itself and a future edit could
# satisfy "kept" for one and not the other.
check("heading and body carry the SAME label, whatever it is",
      len(set(labels)) == 1, "labels were %r" % (labels,))

# ---------------------------------------------------------------- 2. a genuinely empty heading
empty = [
    "### Owner direction - a heading whose body already went (2026-10-06)",
    "",
    "## Public face: the next real section",
    "",
    "**Verbatim owner direction (2026-09-29):** *\"content belonging to the section below\"*",
    "",
]
labels = label_run(empty)
check("a heading with nothing before the next heading is swept", labels[0] == MOVE,
      "labels were %r" % (labels,))
check("the following section is untouched by that sweep",
      all(labels[i] == KEEP for i in range(2, len(empty))), "labels were %r" % (labels,))

# ---------------------------------------------------------------- 3. a heading over live work
live = [
    "### Owner direction - a section that still holds an open row (2026-10-06)",
    "",
    "**Verbatim owner direction:** *\"something still to do\"*",
    "",
    "- [T] **a row nobody has closed**",
    "",
]
labels = label_run(live)
check("a heading over a kept row is never swept", all(label == KEEP for label in labels),
      "labels were %r" % (labels,))

# ---------------------------------------------------------------- 4. the real ledgers are stable
#
# An absence rule over crafted input only proves the function. This proves the property holds on the
# documents that actually exist, which is where it has to hold.
for name in ("TODO.md", "TEST.md", "DECOMPOSED.md", "ROADMAP.md"):
    path = os.path.join(REPO, "docs", name)
    if not os.path.isfile(path):
        continue
    lines = io.open(path, encoding="utf-8").read().split("\n")
    labels = label_run(lines)
    split = []
    for index, line in enumerate(lines):
        if not mover.H3.match(line) or labels[index] != MOVE:
            continue
        # A swept heading whose section still has a kept, non-blank line is the defect.
        for walk in range(index + 1, len(lines)):
            if mover.H2.match(lines[walk]) or mover.H3.match(lines[walk]):
                break
            if lines[walk].strip() and labels[walk] == KEEP:
                split.append((index + 1, lines[index].strip()[:60]))
                break
    check("docs/%s: no heading is swept away from kept content" % name, not split,
          "; ".join("line %d %r" % row for row in split))

print("")
if failures:
    print("FAILED: %d claim(s)" % len(failures))
    for failure in failures:
        print("  - %s" % failure)
    sys.exit(1)
print("PASS: the orphan sweep never separates a heading from its own content")
sys.exit(0)
