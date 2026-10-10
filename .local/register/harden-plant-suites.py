# -*- coding: utf-8 -*-
"""The plant suites leaked a file handle and could leave the source tree planted.

**This has corrupted the working tree twice**, both times leaving
`Campaign.NoteReturnedFromField(run.crew, run.coordinateId);` deleted out of
`RimroomsExpeditionComponent.cs` -- a line that would have shipped silently if a build had gone
out between the crash and the next `git status`.

Two defects, one cause:

  * **`stdout=open(os.devnull, "w")` is never closed.** Sixteen suites, five hundred and seventy
    plants, one leaked handle each. On Windows that eventually raises
    `OSError: [Errno 22] Invalid argument`, which is exactly what was seen.
  * **plant, run and restore were not in a `try` / `finally`.** So when that OSError landed
    between the plant and the restore, the planted source stayed on disk. Fifteen of the sixteen
    suites had no `finally` at all.

The restore is the single most important line in the instrument -- it is what makes a destructive
test safe -- and it was the one line not protected. Both are fixed in every suite: the handle
becomes `subprocess.DEVNULL`, which needs no closing, and the restore moves into a `finally` so
it happens on any exception, including a keyboard interrupt.
"""
import io
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REGISTER = os.path.join(REPO, ".local", "register")

LEAK = re.compile(r"stdout=open\(os\.devnull, \"w\"\)")

changed = 0
for name in sorted(os.listdir(REGISTER)):
    if not name.startswith("plant-") or not name.endswith(".py"):
        continue
    path = os.path.join(REGISTER, name)
    text = io.open(path, encoding="utf-8").read()
    before = text

    # 1. The leaked handle. `subprocess.DEVNULL` is an int the child inherits; nothing to close.
    text = LEAK.sub("stdout=subprocess.DEVNULL", text)

    # 2. The restore has to happen whatever else does. Every suite writes the plant, calls a
    #    proof, then writes the original back; the three statements are always adjacent and
    #    always at the same indent.
    pattern = re.compile(
        r"(?P<indent>[ \t]*)io\.open\(path, \"w\", encoding=\"utf-8\", newline=\"\"\)"
        r"\.write\(original\.replace\(old, new, 1\)\)\n"
        r"(?P<run>(?:[ \t]*\S[^\n]*\n|[ \t]*\n)*?)"
        r"[ \t]*io\.open\(path, \"w\", encoding=\"utf-8\", newline=\"\"\)\.write\(original\)\n")

    def guard(match):
        indent = match.group("indent")
        run = match.group("run")
        body = []
        for line in run.split("\n"):
            body.append(("    " + line) if line.strip() else line)
        return (indent + "io.open(path, \"w\", encoding=\"utf-8\", newline=\"\").write("
                "original.replace(old, new, 1))\n"
                + indent + "try:\n"
                + "\n".join(body).rstrip("\n") + "\n"
                + indent + "finally:\n"
                + indent + "    # **THE RESTORE IS THE ONE LINE THAT MUST ALWAYS RUN.** It is\n"
                + indent + "    # what makes a destructive instrument safe, and it was the one\n"
                + indent + "    # line not protected -- a leaked devnull handle raised OSError\n"
                + indent + "    # mid-run twice and left the planted source on disk.\n"
                + indent + "    io.open(path, \"w\", encoding=\"utf-8\", newline=\"\")"
                ".write(original)\n")

    text, count = pattern.subn(guard, text)
    if text != before:
        io.open(path, "w", encoding="utf-8", newline="").write(text)
        changed += 1
        print("%-44s devnull fixed, %d restore(s) guarded" % (name, count))

print("")
print("%d suite(s) hardened" % changed)
