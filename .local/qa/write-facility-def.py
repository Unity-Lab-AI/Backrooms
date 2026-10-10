# -*- coding: utf-8 -*-
"""Write the computed facility changes into `RR_Starts.xml`.

Separate from `apply-facility-read.py` on purpose: that one **measures** and this one **writes**, so
the measurement can be read and argued with before a single line of the def moves. The owner said
*"these places i put everything is exact and purposfully and should use them exactly"*, which is a
reason to be able to check the numbers first.

Every edit is anchored and counted, and the whole thing refuses rather than writing a partial def.
"""
import io
import json
import os
import re
import sys

NL = chr(10)
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
STARTS = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                      "RimroomsStartDefs", "RR_Starts.xml")
DEF_NAME = "RR_AsyncIndustriesStart"
PLAN = os.path.join(HERE, "facility-apply-%s.json" % DEF_NAME)

# The owner asked for a beacon in the middle of every room that already holds a shelf, and for none
# anywhere else: *"if room doesnt have a shelf no trade beacon is wanted and not required"*.
BEACON = "OrbitalTradeBeacon"


def say(line):
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode("ascii", "replace").decode("ascii"))


def cell(pair):
    return "(%d, 0, %d)" % (pair[0], pair[1])


def comment(lines):
    """An XML comment that cannot be malformed by this repository's prose style.

    **`--` IS ILLEGAL INSIDE AN XML COMMENT and I wrote one twice in a row** -- once in
    `RR_GateJobs.xml` and again here. The em dash is the correct character in reader prose anyway;
    the double hyphen was a habit from the markdown in every other file. Sanitised here rather than
    remembered, because remembering is what failed.
    """
    body = NL.join(lines).replace("--", chr(8212))
    return "    <!-- " + body + NL + "    -->"


def main():
    data = json.load(io.open(PLAN, encoding="utf-8-sig"))
    text = io.open(STARTS, encoding="utf-8-sig").read()

    start = text.index("<defName>%s</defName>" % DEF_NAME)
    end = text.index("</RimroomsAsyncIndustries", start)
    body = text[start:end]
    original_body = body

    # ---------------------------------------------------------------- 1. conduits, all hidden now
    runs = NL.join(
        "      <li><start>%s</start><length>%d</length><alongX>%s</alongX></li>"
        % (cell(c), length, "true" if along else "false")
        for c, length, along in data["conduits"])
    match = re.search(r"    <conduits>.*?</conduits>", body, re.S)
    if match is None:
        say("no <conduits> block found; refusing")
        return 1
    body = body[:match.start()] + (
        comment([
            "THE OWNER'S OWN WIRING, read back from the live facility 2026-10-06.",
            "         Owner: \"ive added hidden conduit where needed and missing\", and asked",
            "         which type, \"All HiddenConduit\". The generator places HiddenConduit for",
            "         every run; both it and PowerConduit ship in Core, so neither was ever a",
            "         mod's. As authored the facility had 205 conduit cells in 17 runs and NOT",
            "         ONE of its 34 powered buildings was within reach of a wire. This is 233",
            "         cells in %d runs." % len(data["conduits"]),
        ]) + NL
        + "    <conduits>" + NL + runs + NL + "    </conduits>") + body[match.end():]

    # ---------------------------------------------------------------- 2. walls the owner cut open
    cuts = NL.join("      <li>%s</li>" % cell(c) for c in data["removedWalls"])
    body = body.replace(
        "    <conduits>",
        comment([
            "Owner: \"readjusted the room by dleteing some walls\". Six authored wall cells they",
            "         opened by hand. Skipped as the rooms are built, so there is no rubble and no",
            "         work order: a wall that never existed rather than one taken down.",
        ]) + NL
        + "    <removedWalls>" + NL + cuts + NL + "    </removedWalls>" + NL + NL
        + "    <conduits>", 1)

    # ---------------------------------------------------------------- 3. the gate door they moved
    # **It goes among the buildings, NOT in `<autodoors>`.** That list exists for a door replacing
    # an authored wall, and its loop demands one; (39, 41) is not an authored wall cell. The owner
    # built a NEW wall segment there -- Steel at (38, 41) and (40, 41) with the door between them --
    # so the door is a building like any other, and `canPlaceOverWall` handles it.

    # ------------------------------------------- 3b. the receiving bay moves off the owner's stove
    # `check-start-layout` caught this: an `ElectricStove` is 3x1 and the owner's covers
    # (26..28, 19), which is the cell company orders land on. Their placements are exact and
    # purposeful, so **the bay moves rather than the stove** -- one step along the same aisle, so
    # somebody standing at the stove can still reach a delivery.
    if "<stockCell>(27, 0, 19)</stockCell>" in body:
        body = body.replace(
            "    <stockCell>(27, 0, 19)</stockCell>",
            comment([
                "MOVED ONE CELL 2026-10-06 because the owner put a stove on the old one.",
                "         Owner: \"these places i put everything is exact and purposfully and",
                "         should use them exactly\", so the receiving bay moves rather than the",
                "         stove. (27, 20) is the nearest free cell in the same room.",
            ]) + NL + "    <stockCell>(27, 0, 20)</stockCell>", 1)

    # ---------------------------------------------------------------- 4. buildings
    match = re.search(r"    <buildings>(.*?)</buildings>", body, re.S)
    if match is None:
        say("no <buildings> block found; refusing")
        return 1
    existing = match.group(1)
    kept = []
    dropped = 0
    absent = {(tuple(c), n) for c, n in data["absent"]}
    for line in existing.split(NL):
        hit = re.search(r"<thing>([^<]+)</thing>.*?<cell>\(\s*(-?\d+)\s*,\s*-?\d+\s*,\s*(-?\d+)\s*\)",
                        line)
        if hit and ((int(hit.group(2)), int(hit.group(3))), hit.group(1)) in absent:
            dropped += 1
            continue
        kept.append(line)
    if dropped != len(absent):
        say("expected to drop %d absent entry/entries and matched %d; refusing"
            % (len(absent), dropped))
        return 1

    freezer = {tuple(c) for c in data["freezerCoolers"]}
    added = []
    added.append("      <!-- Owner's own additions, read back from the live facility 2026-10-06."
                 " Every cell")
    added.append("           is theirs: \"these places i put everything is exact and purposfully"
                 " and should")
    added.append("           use them exactly\". -->")
    for position, stuff in data["addedWalls"]:
        added.append("      <li><thing>Wall</thing><stuff>%s</stuff><cell>%s</cell>"
                     "<rotation>0</rotation></li>" % (stuff, cell(position)))
    for name, stuff, anchor, rotation in data["additions"]:
        parts = ["<thing>%s</thing>" % name]
        if stuff:
            parts.append("<stuff>%s</stuff>" % stuff)
        parts.append("<cell>%s</cell>" % cell(anchor))
        # A moved thing keeps the facing it was authored with; the read carries none.
        parts.append("<rotation>%d</rotation>" % rotation)
        if name == "Cooler" and tuple(anchor) in freezer:
            parts.append("<targetTemperature>%s</targetTemperature>" % data["freezerTarget"])
        added.append("      <li>%s</li>" % "".join(parts))
    for position in data["autodoorsAsBuildings"]:
        added.append("      <!-- Owner: \"the door i moved and set to the gate and where i want it"
                     " with steel")
        added.append("           walls on both sides of it\". Listed here rather than in"
                     " <autodoors>, because it")
        added.append("           replaces no authored wall: the owner built the wall segment"
                     " around it. -->")
        added.append("      <li><thing>Autodoor</thing><cell>%s</cell><rotation>0</rotation></li>"
                     % cell(position))
    added.append("      <!-- Owner: \"We will also need trade beacons in middle of rooms that"
                 " already have")
    added.append("           shelfs in them(if room doesnt have a shelf no trade beacon is wanted"
                 " and not")
    added.append("           required\". Eight rooms hold a shelf; each gets one, in the middle. -->")
    for position in data["beacons"]:
        added.append("      <li><thing>%s</thing><cell>%s</cell><rotation>0</rotation></li>"
                     % (BEACON, cell(position)))

    body = body[:match.start()] + (
        "    <buildings>" + NL.join(kept).rstrip() + NL + NL.join(added) + NL
        + "    </buildings>") + body[match.end():]

    if body == original_body:
        say("nothing changed; refusing to write")
        return 1
    io.open(STARTS, "w", encoding="utf-8", newline=NL).write(text[:start] + body + text[end:])

    import xml.etree.ElementTree as ET
    ET.parse(STARTS)
    say("write-facility-def  %s" % DEF_NAME)
    say("  conduit runs written      : %d, all HiddenConduit" % len(data["conduits"]))
    say("  removed wall cells        : %d" % len(data["removedWalls"]))
    say("  autodoor as a building    : %d" % len(data["autodoorsAsBuildings"]))
    say("  walls added               : %d" % len(data["addedWalls"]))
    say("  buildings added           : %d" % len(data["additions"]))
    say("  trade beacons             : %d" % len(data["beacons"]))
    say("  freezer coolers at %s C   : %d" % (data["freezerTarget"], len(freezer)))
    say("  absent entries dropped    : %d" % dropped)
    say("  XML parses                : yes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
