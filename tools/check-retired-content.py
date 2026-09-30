# -*- coding: utf-8 -*-
"""Refuse to ship player-facing text that tells somebody to use equipment this mod retired.

Why this exists
---------------
Nine keyed strings were instructing the player to use a **return beacon** (retired 0.9.9-dev), a
**survey tag** (0.10.7-dev), a **sealed evidence case** (0.10.9-dev) and a **field recorder**
(0.12.24-dev). The tutorial text told people to do things they cannot do. Nothing caught it: the
keyed-string checker verifies that every key *resolves*, not that what it says is still true, and
three of those keys resolved to text about an item that had not existed for fifteen checkpoints.

The shape of the rule, and why it is not a list
-----------------------------------------------
Invariant 214: check a rule as a SHAPE, not a count. A checker holding the four names above would
be stale the next time something is retired, which is the exact failure it is meant to prevent.

So the names are **derived**:

  * **Retired** = a def with a label in `docs/implementation/historical-content/` that the package no
    longer declares. Invariant 37 already requires retired content to be archived, so this list
    maintains itself.
  * **Superseded but still loadable** = a live item def that is *unobtainable*: `tradeability` is
    `None`, no live recipe produces it, and no scenario grants it. That is `RR_FieldRecorder`, which
    stays in the database on purpose so old saves open, and `RR_RouteRecording`, which only legacy
    saves contain. Nothing should be telling a player to go and use either.

From each retired label the check derives every candidate phrase and then requires a **disposition**
for it, because the one thing that cannot be derived is whether the CONCEPT survived the item:

    "emergency return cutoff" is retired, but an emergency return is a live mechanic.
    "legacy field analysis bench" is retired, but the analysis bench is a live designated Core bench.
    "gate control console" is retired, but a gate console is a live designated Core comms console.

Those are judgements, so they live in `tools/retired-vocabulary.json` as decisions with reasons, and
the check enforces the shape around them:

  1. Every derived candidate must be dispositioned. **A new retirement therefore fails the build
     until somebody says whether its words survived it.**
  2. Every `stale` phrase must appear in no keyed string.
  3. Every entry in the file must still be a derived candidate, so the file cannot rot either.

Exit status is the result. Run from the repository root.
"""
import glob
import io
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKAGE = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")
ARCHIVE = os.path.join(REPO, "docs", "implementation", "historical-content")
VOCABULARY = os.path.join(REPO, "tools", "retired-vocabulary.json")

# Words that carry no identity. A phrase containing one of these is not a name for anything, so
# "make six survey tags" yields "survey tags" rather than eight useless fragments.
STOPWORDS = set("a an the of and or for with make six new old legacy this that its".split())

# Core def types plus this mod's OWN namespaced ones. Leaving the namespaced types out made
# the check blind to most of what this mod actually authors -- requests, projects, catalogue
# entries -- and a research project description naming "route recordings" went unseen.
DEF_TAGS = ("ThingDef|RecipeDef|TerrainDef|JobDef|SoundDef|ResearchProjectDef|FactionDef"
            r"|IncidentDef|ScenarioDef|ThingCategoryDef|RimroomsAsyncIndustries\.[A-Za-z0-9_.]+")

problems = []


def fail(message):
    problems.append(message)


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def def_blocks(text):
    """Every def in one file as (defName, label, body)."""
    for match in re.finditer(r"<(%s)[^>]*>(.*?)</\1>" % DEF_TAGS, text, re.S):
        body = match.group(2)
        name = re.search(r"<defName>([^<]+)</defName>", body)
        label = re.search(r"<label>([^<]+)</label>", body)
        if name:
            yield name.group(1).strip(), (label.group(1).strip() if label else None), body


def live_defs():
    found = {}
    for path in glob.glob(os.path.join(PACKAGE, "Defs", "**", "*.xml"), recursive=True):
        for name, label, body in def_blocks(read(path)):
            found[name] = {"label": label, "body": body, "path": path}
    return found


def archived_labels():
    found = {}
    for path in glob.glob(os.path.join(ARCHIVE, "**", "Defs", "**", "*.xml"), recursive=True):
        for name, label, _ in def_blocks(read(path)):
            if label and name not in found:
                found[name] = label
    return found


def keyed_strings():
    """Every translated value, keyed by file and key. These are the player's own words."""
    found = []
    for path in glob.glob(os.path.join(PACKAGE, "Languages", "**", "Keyed", "*.xml"), recursive=True):
        inner = re.search(r"<LanguageData>(.*)</LanguageData>", read(path), re.S)
        if inner is None:
            fail("%s has no LanguageData element" % os.path.basename(path))
            continue
        for key, value in re.findall(r"<([A-Za-z0-9_]+)>(.*?)</\1>", inner.group(1), re.S):
            found.append((os.path.basename(path), key, value))
    return found


def def_descriptions(live):
    """Every live def's own description, which the player reads on its info card.

    Read as player-facing text, with one exemption: **a def may name itself.**
    `RR_FieldRecorder` is labelled "field recorder and radio" and has to be able to say so, and
    `RR_RouteRecording` likewise. What neither may do is instruct somebody to use some *other*
    retired thing -- which is how the legacy recording's description was still telling people to
    return it with an evidence case that stopped existing at 0.10.9-dev.
    """
    found = []
    for name, entry in sorted(live.items()):
        description = re.search(r"<description>(.*?)</description>", entry["body"], re.S)
        if description is None:
            continue
        own = (entry["label"] or "").lower()
        found.append((os.path.basename(entry["path"]), name, description.group(1), own))
    return found


def unobtainable_items(live):
    """Live item defs a player cannot get: untradeable, unbuilt, ungranted.

    Derived rather than listed, so retiring an item by making it unobtainable -- which is how
    `RR_FieldRecorder` was retired without a save break -- brings its words into this check
    automatically.
    """
    products = set()
    for path in glob.glob(os.path.join(PACKAGE, "Defs", "RecipeDefs", "*.xml"), recursive=True):
        for _, _, body in def_blocks(read(path)):
            block = re.search(r"<products>(.*?)</products>", body, re.S)
            if block:
                products.update(re.findall(r"<([A-Za-z0-9_]+)>", block.group(1)))
    granted = set()
    for path in glob.glob(os.path.join(PACKAGE, "Defs", "ScenarioDefs", "*.xml"), recursive=True):
        granted.update(re.findall(r"<thingDef>([^<]+)</thingDef>", read(path)))

    found = {}
    for name, entry in live.items():
        if entry["label"] is None or os.sep + "ThingDefs_Items" + os.sep not in entry["path"]:
            continue
        if "<tradeability>None</tradeability>" not in entry["body"]:
            continue
        if name in products or name in granted:
            continue
        found[name] = entry["label"]
    return found


def candidates(label):
    words = [w for w in re.split(r"\W+", label.lower()) if w]
    found = set()
    for start in range(len(words)):
        for end in range(start + 2, len(words) + 1):
            segment = words[start:end]
            if any(word in STOPWORDS for word in segment):
                continue
            found.add(" ".join(segment))
    return found


def main():
    live = live_defs()
    archived = archived_labels()
    unobtainable = unobtainable_items(live)

    retired = {name: label for name, label in archived.items() if name not in live}
    retired.update(unobtainable)
    if not retired:
        fail("no retired labels derived at all; the archive or the package layout has moved")

    live_label_text = " | ".join(
        entry["label"].lower() for entry in live.values()
        if entry["label"] and entry["label"] not in unobtainable.values())

    derived = {}
    for name, label in sorted(retired.items()):
        for phrase in candidates(label):
            # A phrase a LIVE def still uses as its own name is live vocabulary by construction,
            # and no judgement is needed for it.
            if phrase in live_label_text:
                continue
            derived.setdefault(phrase, set()).add(name)

    if not os.path.isfile(VOCABULARY):
        fail("tools/retired-vocabulary.json is missing; every derived phrase needs a disposition")
        return report(0, 0)

    data = json.loads(read(VOCABULARY))
    entries = data.get("phrases", {})

    undispositioned = sorted(p for p in derived if p not in entries)
    if undispositioned:
        fail("%d derived phrase(s) have no disposition in tools/retired-vocabulary.json -- say "
             "whether the CONCEPT survived the item:\n%s" %
             (len(undispositioned), "\n".join(
                 "      %-34s from %s" % (p, ", ".join(sorted(derived[p]))) for p in undispositioned)))

    orphaned = sorted(p for p in entries if p not in derived)
    if orphaned:
        fail("%d disposition(s) are no longer derived from any retired label; remove them so the "
             "file cannot rot:\n%s" % (len(orphaned), "\n".join("      %s" % p for p in orphaned)))

    for phrase, entry in sorted(entries.items()):
        if entry.get("disposition") not in ("stale", "live"):
            fail("%r has no usable disposition; expected \"stale\" or \"live\"" % phrase)
        if not entry.get("why"):
            fail("%r carries no reason; a disposition without one is a guess somebody will trust" % phrase)

    strings = keyed_strings()
    descriptions = def_descriptions(live)
    stale = sorted(p for p, e in entries.items() if e.get("disposition") == "stale")
    for phrase in stale:
        pattern = re.compile(r"\b" + re.escape(phrase) + r"s?\b", re.I)
        for filename, key, value in strings:
            if pattern.search(value):
                fail("%s: %s tells the player about %r, which this mod retired (%s)" %
                     (filename, key, phrase, entries[phrase].get("why", "")))
        for filename, name, value, own in descriptions:
            # A def naming itself is not an instruction to go and use a retired thing.
            if phrase in own:
                continue
            if pattern.search(value):
                fail("%s: %s's own description tells the player about %r, which this mod retired "
                     "(%s)" % (filename, name, phrase, entries[phrase].get("why", "")))

    return report(len(derived), len(strings) + len(descriptions))


def report(derived_count, string_count):
    print("retired-content check")
    print("  derived phrases   : %d" % derived_count)
    print("  keyed strings read: %d" % string_count)
    if problems:
        print("")
        for problem in problems:
            print("  FAIL %s" % problem)
        print("")
        print("FAILED: %d problem(s)" % len(problems))
        return 1
    print("  no player-facing string names retired equipment")
    return 0


if __name__ == "__main__":
    sys.exit(main())
