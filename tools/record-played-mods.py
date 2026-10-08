# -*- coding: utf-8 -*-
"""Record which profile mods were active in the game Rimrooms is being played in, from the game.

Why this exists
---------------
The public mod list said **"Read, but not yet confirmed in a running game"** for 195 of 297 mods,
while the full profile had been loaded and played under Rimrooms through the 2026-10-05..07
sessions. Owner, 2026-10-07: *"your probably going to have to update the wiki and mod registry on
the wiki once your done as all the shit says never tested and we dont want that"*.

A label may only move on evidence, so this reads two things the game itself wrote, never a
memory of having played:

* the game's own `ModsConfig.xml` -- the package ids that were active -- each resolved to its
  name through that mod's `About.xml`;
* the game's own `Player.log` and `Player-prev.log` -- every error or exception line, counted against each active mod
  whose package id, folder or name it mentions.

It writes `tools/register-played.json`, which `build-public-register.py` reads. Run it with the
game having been played on the profile; it refuses to write when `ModsConfig.xml` lists nothing.

    python tools/record-played-mods.py
"""
from __future__ import annotations

import datetime
import io
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "tools", "register-played.json")
GAME = os.environ.get("RIMWORLD_PATH") or r"C:\Program Files (x86)\Steam\steamapps\common\Rimworld"
WORKSHOP = os.path.join(os.path.dirname(os.path.dirname(GAME)), "workshop", "content", "294100")
USERDATA = os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "LocalLow", "Ludeon Studios",
                        "RimWorld by Ludeon Studios")


def normal(name: str) -> str:
    """A name with brackets, punctuation and case taken out, so a register row and an About.xml meet."""
    return re.sub(r"[^a-z0-9]+", "", (name or "").lower())


def about_index() -> dict:
    """packageId (lower) -> (name, folder), over the game's Mods folder and the workshop."""
    index = {}
    for root in (os.path.join(GAME, "Mods"), WORKSHOP, os.path.join(GAME, "Data")):
        if not os.path.isdir(root):
            continue
        for folder in os.listdir(root):
            about = os.path.join(root, folder, "About", "About.xml")
            if not os.path.isfile(about):
                continue
            try:
                node = ET.parse(about).getroot()
            except ET.ParseError:
                continue
            package = (node.findtext("packageId") or "").strip().lower()
            name = (node.findtext("name") or folder).strip()
            if package:
                index[package] = (name, folder)
    return index


def main() -> int:
    config = os.path.join(USERDATA, "Config", "ModsConfig.xml")
    # Both sessions the game keeps: it rewrites Player.log on every launch and keeps the one
    # before as Player-prev.log, and this project relaunches after every stage.
    logs = [os.path.join(USERDATA, "Player.log"), os.path.join(USERDATA, "Player-prev.log")]
    if not os.path.isfile(config):
        print("FAILED: %s is missing." % config)
        return 1
    active = [li.text.strip().lower() for li in ET.parse(config).getroot().iter("li")
              if li.text and li.text.strip() and "." in li.text]
    if not active:
        print("FAILED: ModsConfig.xml lists no active mods; nothing was played to record.")
        return 1
    abouts = about_index()
    # **An error is a block, not a line.** The line that says "Exception" rarely names the mod;
    # the stack under it does -- "PREFIX com.spdskatr.lightningrod.detours" sat three lines below
    # a NullReferenceException in this very log. So each error line takes the indented stack,
    # Harmony patch notes and [Ref] lines that follow it.
    errors = []
    for log in logs:
        if not os.path.isfile(log):
            continue
        block = None
        for line in io.open(log, encoding="utf-8", errors="replace"):
            starts = ("Exception" in line or "Error" in line) and not line.startswith((" ", "\t"))
            if starts:
                if block is not None:
                    errors.append(block.lower())
                block = line
            elif block is not None and (line.startswith((" ", "\t", "[Ref", "Rethrow")) or
                                        line.strip().startswith(("at ", "- ", "--- "))):
                block += line
            elif block is not None:
                errors.append(block.lower())
                block = None
        if block is not None:
            errors.append(block.lower())

    mods = {}
    for package in active:
        name, folder = abouts.get(package, (package, package))
        needles = {package, folder.lower()}
        if len(normal(name)) >= 6:
            needles.add(name.lower())
        count = sum(1 for line in errors if any(n and n in line for n in needles))
        mods[normal(name)] = {"name": name, "packageId": package, "logErrors": count}

    record = {
        "note": "Written by tools/record-played-mods.py from the game's own ModsConfig.xml and "
                "Player.log. Read by build-public-register.py; never edited by hand.",
        "recorded": datetime.date.today().isoformat(),
        "activeCount": len(active),
        "mods": mods,
    }
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(record, indent=1, sort_keys=True) + "\n")
    print("active mods recorded : %d" % len(active))
    print("with a logged error  : %d" % sum(1 for m in mods.values() if m["logErrors"]))
    print("written              : %s" % os.path.relpath(OUT, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
