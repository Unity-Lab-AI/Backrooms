# -*- coding: utf-8 -*-
"""Every suite writes a sentinel while a fault is on disk, so an interrupted sweep is visible.

`finally` protects the restore from an exception. **It does not protect it from the process being
killed**, and that is how a planted fault reached the working tree for the third time: the sweep
was interrupted between the plant and the restore, and `!anchor.Destroyed` sat deleted in
`RimroomsPortalNetwork.cs` until a proof happened to notice.

So each suite writes `.local/register/.plant-in-progress` naming the file and the plant before it
mutates anything, and deletes it in the same `finally` that restores. `tools/check-plant-residue.py`
-- checker fifteen -- refuses while that file exists, and prints the path to restore.
"""
import io
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REGISTER = os.path.join(REPO, ".local", "register")

HELPER = u'''
# **THE RESTORE DOES NOT SURVIVE THE PROCESS BEING KILLED.** `finally` handles an exception; it
# does nothing for an interrupted sweep, and that is how a planted fault reached the working tree
# for the third time. The sentinel makes it visible: `tools/check-plant-residue.py` refuses while
# this file exists and prints the path to restore.
_RR_SENTINEL = os.path.join(".local", "register", ".plant-in-progress")


def _rr_mark(path, label):
    io.open(_RR_SENTINEL, "w", encoding="utf-8", newline="").write(
        u"planted %r into %s" % (label, path))


def _rr_unmark():
    try:
        os.remove(_RR_SENTINEL)
    except OSError:
        pass

'''

changed = 0
for name in sorted(os.listdir(REGISTER)):
    if not name.startswith("plant-") or not name.endswith(".py"):
        continue
    path = os.path.join(REGISTER, name)
    text = io.open(path, encoding="utf-8").read()
    if "_rr_mark(" in text:
        continue

    if "import os" not in text:
        text = text.replace("import io", "import io\nimport os", 1)

    # The helper goes in just before the plant table.
    anchor = "PLANTS = ["
    if anchor not in text:
        print("%-44s no PLANTS table, skipped" % name)
        continue
    text = text.replace(anchor, HELPER + "\n" + anchor, 1)

    # Mark before the write, unmark in the finally beside the restore.
    before = len(text)
    text = re.sub(
        r"(\n([ \t]*)(?:write_verified\(path, original\.replace\(old, new, 1\)[^\n]*\)"
        r"|io\.open\(path, \"w\", encoding=\"utf-8\", newline=\"\"\)"
        r"\.write\(original\.replace\(old, new, 1\)\)))",
        lambda match: "\n%s_rr_mark(path, label)%s" % (match.group(2), match.group(1)),
        text, count=1)
    text = re.sub(
        r"(\n([ \t]*)(?:write_verified\(path, original[^\n]*\)"
        r"|io\.open\(path, \"w\", encoding=\"utf-8\", newline=\"\"\)\.write\(original\)))"
        r"(?=\n)",
        lambda match: "%s\n%s_rr_unmark()" % (match.group(1), match.group(2)),
        text, count=0)
    if len(text) == before:
        print("%-44s SHAPE NOT RECOGNISED -- check by hand" % name)
        continue

    io.open(path, "w", encoding="utf-8", newline="").write(text)
    changed += 1
    print("%-44s sentinel added" % name)

print("")
print("%d suite(s) now mark the tree while a fault is on disk" % changed)
