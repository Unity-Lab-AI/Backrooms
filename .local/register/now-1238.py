# -*- coding: utf-8 -*-
"""NOW.md for 0.12.38-dev. Row 725 closed; every number re-measured."""
import io
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "docs", "NOW.md")

s = io.open(PATH, encoding="utf-8").read()


def sub(old, new):
    global s
    assert old in s, "anchor missing: %r" % old[:90]
    assert s.count(old) == 1, "anchor not unique: %r" % old[:90]
    s = s.replace(old, new, 1)


# ------------------------------------------------------------------ drop the closed item
sub(u"""4. **Gate subsystems**: monitoring, cool-down, modules, repair and reliability. Row 725. Power
    reserves, calibration and the cutoff already ship.
""", u"")

start = s.index(u"### Systems still unbuilt")
end = s.index(u"### Cannot close before the game runs once")
block = s[start:end]
numbers = re.findall(r"^(\d+)\. ", block, re.M)
for new_index, old_index in enumerate(numbers, start=1):
    block = re.sub(r"^%s\. " % old_index, u"\x00%d. " % new_index, block, count=1, flags=re.M)
block = block.replace(u"\x00", u"")
s = s[:start] + block + s[end:]

remaining = len(numbers)
sub(u"**13 genuine build items**, counted at 0.12.37-dev, listed in full under **What is left** "
    u"below. **Five more rows closed in this batch**: 1005 built, 1011 and 1101 by proof, and 922 "
    u"and 1055 as tooling. **Eleven rows across the last two batches.**",
    u"**%d genuine build items**, counted at 0.12.38-dev, listed in full under **What is left** "
    u"below. **Row 725 closed completely this batch** — seven of its nine subsystems turned out "
    u"already built. **Twelve rows across the last three batches.**" % remaining)
sub(u"**13 genuine build items**, counted rather than estimated:",
    u"**%d genuine build items**, counted rather than estimated:" % remaining)

io.open(PATH, "w", encoding="utf-8", newline="").write(s)
print("NOW.md updated for 0.12.38-dev: %d items remain" % remaining)
