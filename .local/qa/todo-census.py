"""Per-section marker census for docs/TODO.md.

Read-only. For every `##` section (with `###` rolled into its parent), count the
status markers so a section can be classified:

  CLEAN   - no open markers at all; the whole section is a completed record
  MIXED   - carries open ([ ] / [~]) and done ([x]) markers together
  OPEN    - no done markers; nothing to move
  TEST    - only [T] rows, which are the post-completion test phase and never done

[T] never counts as done and never counts as open-blocking, because a [T] row
cannot be closed without the game running and gates no work.
"""

import re

PATH = "docs/TODO.md"

MARKER = re.compile(r"^(\s*)- \[( |x|~|T)\]")
H2 = re.compile(r"^## (.*)$")

with open(PATH, encoding="utf-8") as handle:
    lines = handle.read().split("\n")

sections = []
current = {"title": "(preamble)", "start": 1, "counts": {" ": 0, "x": 0, "~": 0, "T": 0}}

for index, line in enumerate(lines, start=1):
    head = H2.match(line)
    if head:
        current["end"] = index - 1
        sections.append(current)
        current = {
            "title": head.group(1),
            "start": index,
            "counts": {" ": 0, "x": 0, "~": 0, "T": 0},
        }
        continue
    marker = MARKER.match(line)
    if marker:
        current["counts"][marker.group(2)] += 1

current["end"] = len(lines)
sections.append(current)

clean_lines = 0
for section in sections:
    counts = section["counts"]
    span = section["end"] - section["start"] + 1
    open_count = counts[" "] + counts["~"]
    if counts["x"] and not open_count:
        kind = "CLEAN"
        clean_lines += span
    elif counts["x"] and open_count:
        kind = "MIXED"
    elif open_count:
        kind = "OPEN"
    elif counts["T"]:
        kind = "TEST"
    else:
        kind = "PROSE"
    print(
        f"{kind:<6} {section['start']:>5}-{section['end']:<5} "
        f"({span:>4}L)  x={counts['x']:<3} o={counts[' ']:<3} p={counts['~']:<3} "
        f"T={counts['T']:<3}  {section['title'][:72]}"
    )

print()
print("sections:", len(sections), "| lines inside CLEAN sections:", clean_lines)
