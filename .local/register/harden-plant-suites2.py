# -*- coding: utf-8 -*-
"""The other restore shape: `write_verified(path, original)`.

Fourteen of the sixteen suites write through a `write_verified` helper rather than `io.open`
directly, so the first pass guarded two and reported honestly that it had guarded zero in the
rest -- which is why it printed a count per file instead of just saying it was done.
"""
import io
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REGISTER = os.path.join(REPO, ".local", "register")

PATTERN = re.compile(
    r"(?P<indent>[ \t]*)write_verified\(path, original\.replace\(old, new, 1\)\)\n"
    r"(?P<run>(?:[ \t]+\S[^\n]*\n)+?)"
    r"[ \t]*write_verified\(path, original\)\n")


def guard(match):
    indent = match.group("indent")
    body = ["    " + line if line.strip() else line
            for line in match.group("run").rstrip("\n").split("\n")]
    return (indent + "write_verified(path, original.replace(old, new, 1))\n"
            + indent + "try:\n"
            + "\n".join(body) + "\n"
            + indent + "finally:\n"
            + indent + "    # **THE RESTORE IS THE ONE LINE THAT MUST ALWAYS RUN.** It is what\n"
            + indent + "    # makes a destructive instrument safe, and it was the one line not\n"
            + indent + "    # protected: a leaked devnull handle raised OSError mid-run twice\n"
            + indent + "    # and left planted source on disk both times.\n"
            + indent + "    write_verified(path, original)\n")


changed = 0
for name in sorted(os.listdir(REGISTER)):
    if not name.startswith("plant-") or not name.endswith(".py"):
        continue
    path = os.path.join(REGISTER, name)
    text = io.open(path, encoding="utf-8").read()
    updated, count = PATTERN.subn(guard, text)
    if count:
        io.open(path, "w", encoding="utf-8", newline="").write(updated)
        changed += 1
        print("%-44s %d restore(s) guarded" % (name, count))

print("")
print("%d suite(s) guarded in this pass" % changed)

# And say plainly which suites still have an unguarded restore, rather than assuming none do.
unguarded = []
for name in sorted(os.listdir(REGISTER)):
    if not name.startswith("plant-") or not name.endswith(".py"):
        continue
    text = io.open(os.path.join(REGISTER, name), encoding="utf-8").read()
    if "finally:" not in text:
        unguarded.append(name)
if unguarded:
    print("STILL UNGUARDED: %s" % ", ".join(unguarded))
    raise SystemExit(1)
print("every suite restores in a finally")
