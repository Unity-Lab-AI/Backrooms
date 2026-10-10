# -*- coding: utf-8 -*-
"""Record the stacked-doc-comment defect class found while fixing the wiki's root cause."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

SECTION = NL.join([
"",
"### The defect class behind the published lie — 29 stacked doc comments (measured 2026-10-05)",
"",
"Found by asking *why* `gates.md` said depth 3. The answer was not the page: `MaximumNaturalDepth` carried **two consecutive `<summary>` blocks**, the first still arguing for three in full and the second noting the raise to six. **Whoever wrote the page read the first one.** That one is fixed and the superseded value is now recorded inside the single surviving block.",
"",
"**Then the same shape was swept for, and there are 29 of them** — a member with two `<summary>` elements and nothing between. That is malformed XML documentation in its own right; tooling keeps one and discards the other, so **half of every pair is invisible to the reader who needs it and visible to the reader who should not trust it.**",
"",
"Three kinds were sampled and all three are live faults, not tidiness:",
"",
"| File | What the stale half does |",
"|---|---|",
"| `Scenario/RimroomsStartDef.cs` | **Describes a different field entirely** — *\"The name offered at setup\"* sits on the field for whether a start begins in contact with the corporation |",
"| `Gate/NativeGateBinding.cs` | **Describes a different member** — the door-allowlist summary sits on the shape test |",
"| `Generation/RoomLayoutPlanner.cs` | A leftover group header — *\"Fewest and most slots per axis\"* — stranded on the depth-1 constant |",
"",
"- [ ] **Clear all 29 stacked `<summary>` blocks, and add the checker that refuses a new one.** The rule is cheap and exact: a `</summary>` followed by `/// <summary>` with only whitespace between is always wrong, so it cannot cry wolf. **The checker has to land in the same commit as the fixes**, because a rule that reports 29 known faults is a rule people learn to scroll past. Worth doing deliberately rather than quickly — each pair needs reading to tell which half is current, and guessing would replace a stale comment with a wrong one.",
"- [ ] **And the standing lesson, because this one generalises past comments:** a document is only ever as accurate as the thing its author read. **The wiki was rewritten from constants and keyed strings this pass rather than from doc comments**, which is why it is now right — but the comments are what the *next* author will reach for. **A stale comment is the upstream of a published lie.**",
"",
])

text = io.open(TODO, encoding="utf-8").read()
if "29 stacked doc comments" in text:
    print("section already present; nothing written")
    sys.exit(1)
if not text.endswith(NL):
    text += NL
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text + SECTION)
print("recorded: %d open rows added" % SECTION.count("- [ ] "))
