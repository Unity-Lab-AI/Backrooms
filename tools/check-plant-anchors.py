# -*- coding: utf-8 -*-
"""Every plant's anchor must appear exactly once in its target, checked without running anything.

Why this checker exists
-----------------------
A plant suite reports `PLANT SETUP BROKEN (n matches)` and **stops** -- correctly, because an
anchor that no longer exists would silently skip a planted fault. But it only discovers the next
broken anchor after running every plant before it, and the sixteen suites take minutes each. A
checkpoint that changes a widely-anchored file therefore costs one full suite run **per stale
anchor**, discovered one at a time.

0.12.73-dev rebuilt the Async facility and renamed three gate methods, and paid that cost eight
times in a row. This reads every suite's `PLANTS` table with `ast` -- no execution, nothing
mutated -- and reports **all** stale anchors at once.

It is a pre-flight check, not a replacement for the suites: it proves an anchor is findable, and
only running the suite proves the proof catches the fault.
"""
from __future__ import annotations

import ast
import glob
import io
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTER = os.path.join(REPO, ".local", "register")


def literal(node, names):
    """Evaluate a plant-table expression: literals, named constants and `+` of those."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return names.get(node.id)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = literal(node.left, names), literal(node.right, names)
        if isinstance(left, str) and isinstance(right, str):
            return left + right
        return None
    if isinstance(node, ast.Call):
        # `chr(10)` is how every suite spells a newline in an anchor. It is a call, not a
        # literal, so `ast.literal_eval` refuses it -- and refusing it made every anchor built
        # from `NL`/`CHR_NL` read as unevaluable, which is most of them.
        if (isinstance(node.func, ast.Name) and node.func.id == "chr"
                and len(node.args) == 1 and isinstance(node.args[0], ast.Constant)):
            return chr(node.args[0].value)
        try:
            return ast.literal_eval(node)
        except Exception:
            return None
    return None


def module_names(tree):
    """Top-level string constants, so `GEN`, `CHR_NL` and friends resolve."""
    names = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or not isinstance(node.targets[0], ast.Name):
            continue
        value = literal(node.value, names)
        if isinstance(value, str):
            names[node.targets[0].id] = value
    return names


def main() -> int:
    suites = sorted(glob.glob(os.path.join(REGISTER, "plant-*.py")))
    if not suites:
        print("FAILED: no plant suites found, so nothing was checked.")
        return 1
    stale = []
    ambiguous = []
    skipped = []
    total = 0
    for suite in suites:
        source = io.open(suite, encoding="utf-8").read()
        tree = ast.parse(source)
        names = module_names(tree)
        table = None
        for node in tree.body:
            if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "PLANTS":
                table = node.value
        if table is None or not isinstance(table, (ast.List, ast.Tuple)):
            print("FAILED: %s has no readable PLANTS table." % os.path.basename(suite))
            return 1
        checked = 0
        for entry in table.elts:
            if not isinstance(entry, ast.Tuple) or len(entry.elts) < 3:
                stale.append((os.path.basename(suite), "(unreadable entry)", "malformed tuple"))
                continue
            label = literal(entry.elts[0], names)
            target = literal(entry.elts[1], names)
            anchor = literal(entry.elts[2], names)
            # **A SUITE MAY SKIP ITS OWN ENTRY**, and `plant-def-fields.py` does: its loop reads
            # `if want is None: continue`, with a comment saying the two blinding plants above
            # cover the same property. Refusing that entry would make this checker stricter than
            # the thing it guards, which is the cry-wolf failure this battery has had five of.
            if (isinstance(entry.elts[-1], ast.Constant) and entry.elts[-1].value is None):
                skipped.append((os.path.basename(suite), label))
                continue
            if not isinstance(target, str) or not isinstance(anchor, str):
                # A computed anchor this reader cannot evaluate. Reported rather than assumed
                # sound: a check that quietly skips what it cannot read is the shape of defect
                # this battery exists to refuse.
                stale.append((os.path.basename(suite), label or "(unlabelled)",
                              "anchor or target could not be read statically"))
                continue
            path = os.path.join(REPO, target)
            if not os.path.isfile(path):
                stale.append((os.path.basename(suite), label, "target missing: %s" % target))
                continue
            text = io.open(path, encoding="utf-8").read()
            found = text.count(anchor)
            if found < 1:
                stale.append((os.path.basename(suite), label,
                              "no match in %s" % target))
            elif found > 1:
                ambiguous.append((os.path.basename(suite), label,
                                  "%d matches in %s" % (found, target)))
            checked += 1
            total += 1
        print("  %-34s %3d plant anchor(s)" % (os.path.basename(suite), checked))

    print("")
    if stale:
        print("FAILED: %d plant anchor(s) will not find their target." % len(stale))
        for suite, label, detail in stale:
            print("  - %-30s %s" % (suite, label))
            print("      %s" % detail)
        print("")
        print("Each one would stop its suite with PLANT SETUP BROKEN. Re-aim the anchor at the")
        print("code as it stands; never weaken the claim it plants against.")
        return 1
    if ambiguous:
        # Reported, not refused: the suites plant into the FIRST match, which several anchors
        # rely on deliberately. Worth seeing, because an anchor that became ambiguous by accident
        # plants somewhere nobody intended.
        print("%d anchor(s) match more than once; the suites plant into the first:" % len(ambiguous))
        for suite, label, detail in ambiguous:
            print("  - %-30s %s" % (suite, label))
            print("      %s" % detail)
        print("")
    if skipped:
        print("%d entry/entries the suite skips itself (last element None):" % len(skipped))
        for suite, label in skipped:
            print("  - %-30s %s" % (suite, label))
        print("")
    print("OK: all %d plant anchors are findable in their target." % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
