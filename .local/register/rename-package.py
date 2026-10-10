# -*- coding: utf-8 -*-
"""The lab's name comes out of the shipped package and the live documentation.

Owner: *"take the Unity Lab AI and the Unity AI Lab out of all refrences and nameing but we will
keep the repos as is for now. especially remove the Unitylabai from the mod information that i see
on Rimsort ie the package id and folder naming and such and files"*.

Chosen at the fork: packageId **`Rimrooms.AsyncIndustries`**, sweep across the shipped package and
the project documentation, `.claude/` and the git remotes untouched.

## What changes and what deliberately does not

The identity is asserted in six live places and they must all agree or the build refuses itself:
`About.xml`, `RimroomsMod.PackageId`, `tools/package-files.json`, and three checks in
`BuildCommon.ps1` / `stage-mod.ps1`. The staging guard is the important one -- it refuses to touch
a folder whose `packageId` differs, which is what stops it overwriting somebody else's mod.

**Dated records are not rewritten.** `docs/FINALIZED.md` and everything under
`docs/implementation/evidence/` are the permanent archive: manifests and receipts that recorded
what was true on the day they were written. Editing them would make the archive lie about history
to make the present tidy, and the project's own rule is that FINALIZED entries are never altered.
The live documents -- `AGENTS.md`, `ARCHITECTURE.md`, `GATE_0_DECISIONS.md`,
`MOD_INTEGRATION_PLAN.md`, `README.md`, `CREDITS.md` -- describe what *is* true and are updated.

**The folder name never carried it.** It is already `Rimrooms - Async Industries`, and so is the
displayed title and the namespace. The only thing a player could see was the packageId.

**This is a new mod identity to RimWorld.** An existing save keyed to the old id will not find
this one, which matters not at all here: the maze rework in the same checkpoint needs a new start
anyway, and the owner has been starting fresh every launch.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OLD = u"UnityLabAI.RimroomsAsyncIndustries"
NEW = u"Rimrooms.AsyncIndustries"

# Live identity. Every one of these must agree or the build refuses.
IDENTITY = [
    os.path.join("Mod", "Rimrooms - Async Industries", "About", "About.xml"),
    os.path.join("src", "RimroomsAsyncIndustries", "Core", "RimroomsMod.cs"),
    os.path.join("tools", "package-files.json"),
    os.path.join("tools", "BuildCommon.ps1"),
    os.path.join("tools", "stage-mod.ps1"),
]

# Live documentation. Dated records are deliberately absent -- see the module docstring.
LIVE_DOCS = [
    "AGENTS.md",
    "README.md",
    "CREDITS.md",
    os.path.join("docs", "ARCHITECTURE.md"),
    os.path.join("docs", "GATE_0_DECISIONS.md"),
    os.path.join("docs", "MOD_INTEGRATION_PLAN.md"),
    os.path.join("docs", "BUILDING.md"),
    os.path.join("docs", "PUBLISHING.md"),
    os.path.join("docs", "COMPATIBILITY.md"),
    os.path.join("docs", "RIMROOMS_MOD_OVERVIEW.md"),
    os.path.join("docs", "HOWTO.md"),
    os.path.join("docs", "NOW.md"),
]

changed = 0
missing = []
for relative in IDENTITY + LIVE_DOCS:
    path = os.path.join(REPO, relative)
    if not os.path.isfile(path):
        missing.append(relative)
        continue
    encoding = "utf-8-sig" if relative.endswith(".xml") else "utf-8"
    text = io.open(path, encoding=encoding).read()
    if OLD not in text:
        continue
    count = text.count(OLD)
    io.open(path, "w", encoding=encoding, newline="").write(text.replace(OLD, NEW))
    changed += 1
    print("%-62s %d occurrence(s)" % (relative, count))

if missing:
    print("")
    print("NOT PRESENT (skipped, not an error): %s" % ", ".join(missing))

print("")
print("%d file(s) renamed to %s" % (changed, NEW))

# And say plainly what still carries the old id, so nothing is hidden by a tidy report.
import subprocess
remaining = subprocess.check_output(
    ["git", "grep", "-l", OLD], cwd=REPO).decode("utf-8", "replace").split("\n")
remaining = [line for line in remaining if line.strip()]
print("")
print("Still carrying the old id, ON PURPOSE (%d file(s)):" % len(remaining))
for line in remaining:
    kind = ("dated archive" if "FINALIZED" in line or "/evidence/" in line
            else "workflow template" if line.startswith(".claude/") else "REVIEW THIS")
    print("  %-70s %s" % (line, kind))
