# -*- coding: utf-8 -*-
"""Which strings are the text wall? Rank a pane's on-screen keys by word count.

`tools/check-operations-density.py` says a pane is too heavy. It does not say
which line to pick up, and guessing from the source reads the wrong half: the
longest *call site* is rarely the longest *string*.

Imports the checker's own harvesting so the two can never disagree about what
counts as on-screen -- the split between screen and hover is the whole premise of
the measurement and a second implementation of it would be a second authority.
"""
import importlib.util
import io
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# `.local/qa/<this>` -- three levels up, not two. The two-level version resolved
# to `.local/tools/` and died on the import, which is the same depth mistake
# `tools/archive-finished-todo.py` records in its own header.
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location(
    "density", os.path.join(REPO, "tools", "check-operations-density.py"))
density = importlib.util.module_from_spec(spec)
spec.loader.exec_module(density)

STRINGS = density.keyed_strings()


def classify(source):
    onscreen, tooltip, other = set(), set(), set()
    for statement in source.split(";"):
        found = re.findall(r'"([A-Za-z0-9_]*RR_[A-Za-z0-9_]+)"\.Translate', statement)
        if not found:
            continue
        if "TipRegion" in statement or "tooltip" in statement or "Tooltip" in statement:
            tooltip.update(found)
        elif (".Label(" in statement or ".ButtonText(" in statement
              or ".CheckboxLabeled(" in statement or "Widgets.Label(" in statement
              or ".RadioButton(" in statement):
            onscreen.update(found)
        else:
            other.update(found)
    tooltip -= onscreen
    other -= onscreen | tooltip
    return onscreen, tooltip, other


for name in sys.argv[1:]:
    path = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "UI", name)
    source = io.open(path, encoding="utf-8-sig").read()
    onscreen, tooltip, other = classify(source)
    rows = sorted(((density.words_of(STRINGS.get(key, "")), key) for key in onscreen),
                  reverse=True)
    print("%s  on-screen %d words in %d keys  (hover %d keys, other %d keys)"
          % (name, sum(n for n, _ in rows), len(rows), len(tooltip), len(other)))
    for count, key in rows:
        if count == 0:
            continue
        print("  %4d  %-42s %s" % (count, key, STRINGS.get(key, "")[:96].replace("\\n", " / ")))
    print()
