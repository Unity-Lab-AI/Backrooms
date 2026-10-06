# -*- coding: utf-8 -*-
"""Generate the player-facing mod register from the engineering one.

Why this exists
---------------
Owner direction, 2026-10-06, verbatim:

    "okay we are adding to todo everything we need to make a similar mod registry as the one we
     have but this one will be pubvlic facing with all new writes in it so that it says the
     important stuff all players would need to know like mod interferances, what if's if not used
     uses in rimrooms, required/recommended/(whatever else(s) is needed) as tags per mod in this
     recommended mod list for all modsand anything else relevant of note"

**"ALL NEW WRITES" IS THE WHOLE INSTRUCTION AND IT IS LOAD BEARING.** The engineering register's
prose -- Planned Use, Integration Approach, Compatibility Watch, FinalDisposition -- is written for
whoever is about to build something. A player does not need our integration approach. They need to
know whether to install the thing and what happens if they do not. **So not one sentence is copied
across.** Every line below is either composed here from the register's structured columns, or
hand-authored in `public-register-text.json`.

The tag vocabulary, chosen by the owner at a fork
-------------------------------------------------
Owner's answer: **"Your words, with the page saying nothing is required to run"**.

So the tags are the owner's own -- Required, Recommended, Optional, Visual only, Not needed -- and
the page states at the top, before the table, that **Required never means required to launch**.
That distinction is not decoration: `check-register-compliance.py` refuses `stance=Required` on any
engineering row while `About.xml` declares no dependencies, and a player reading a bare "Required"
would reasonably conclude the mod will not start without it. The only row that carries Required
here is the game itself.

The count, reconciled rather than quietly differing
---------------------------------------------------
Owner: *"i cuttenlty have 296 (6DLCs, Rimbridge , Rimrooms(locally))"*. The engineering register
holds **294 profile mods** plus a Core row; the six `Data/` folders are inside that 294 as rows 4
to 9. **294 + Rimbridge + Rimrooms = 296**, and the two the engineering register never had are
declared in the overrides file so the published list really is *"for all mods"*.

Usage
-----
    python tools/build-public-register.py            report, write nothing
    python tools/build-public-register.py --apply    write docs/wiki/mods-list.md
"""
import importlib.util
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(REPO, "tools")
OVERRIDES = os.path.join(TOOLS, "public-register-text.json")
TARGET = os.path.join(REPO, "docs", "wiki", "mods-list.md")

TAGS = ("Required", "Recommended", "Optional", "Visual only", "Not needed")

# What each feature trace means to somebody playing, in their words rather than ours. The
# engineering register's trace column names a Rimrooms subsystem; a player has never heard of a
# subsystem and has definitely seen a gate.
TRACE_MEANING = {
    "RR-GATE": "gates and their equipment",
    "RR-EXP": "expeditions and the crews you send",
    "RR-FAC": "building and powering a branch",
    "RR-STA": "your colonists and who does the work",
    "RR-EVD": "evidence, journals and analysis",
    "RR-ECO": "company money and trade",
    "RR-MSN": "contracts and what the company asks for",
    "RR-OUT": "outposts and the world map",
    "RR-THREAT": "what you meet out there",
    "RR-UI": "the interface",
    "RR-STYLE": "how things look",
    "RR-SCEN": "setting up a new game",
    "RR-DLC": "expansion content",
    "RR-MP": "playing with other people",
    "RR-SPACE": "ships and space travel",
    "RR-COMPAT": "nothing directly",
}

# A trace that means the mod touches something a player would notice losing.
LOAD_BEARING = {"RR-GATE", "RR-EXP", "RR-FAC", "RR-STA", "RR-EVD", "RR-ECO", "RR-MSN", "RR-SCEN"}


def register_module():
    spec = importlib.util.spec_from_file_location(
        "register_query", os.path.join(TOOLS, "register-query.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def traces_of(row):
    return [t.strip().upper() for t in (row.get("trace") or "").split(";") if t.strip()]


def tag_for(row):
    stance = (row.get("stance") or "").strip()
    family = (row.get("family") or "").strip().lower()
    firmness = (row.get("firmness") or "").strip()
    marks = set(traces_of(row))

    if family == "rimworld base game":
        return "Required"
    if stance == "Visual only":
        return "Visual only"
    if stance == "No integration":
        return "Not needed"
    if stance == "Configuration only":
        return "Optional"
    if firmness == "Settled" and (marks & LOAD_BEARING):
        return "Recommended"
    return "Optional"


def uses_here(row):
    marks = [t for t in traces_of(row) if t in TRACE_MEANING]
    meanings = [TRACE_MEANING[t] for t in marks if TRACE_MEANING[t] != "nothing directly"]
    if not meanings:
        return "Nothing directly. It is on the list so the two are known to sit together."
    if len(meanings) == 1:
        return "Rimrooms uses it for %s." % meanings[0]
    return "Rimrooms uses it for %s and %s." % (", ".join(meanings[:-1]), meanings[-1])


def without_it(row, tag):
    if tag == "Required":
        return "This is the game itself."
    if tag == "Not needed":
        return "Nothing at all. Rimrooms never touches it."
    if tag == "Visual only":
        return "Nothing changes in play. Things look different, that is the whole of it."
    if tag == "Recommended":
        return "Nothing breaks. Rimrooms falls back to what the base game ships, and says so."
    return "Nothing breaks. The feature it feeds still works without it."


def watch_for(row):
    firmness = (row.get("firmness") or "").strip()
    if firmness == "Settled":
        return "Read and settled. No interference expected."
    if firmness == "Provisional":
        return "Read, but not yet confirmed in a running game."
    return "Not yet read in full."


def load_overrides():
    if not os.path.isfile(OVERRIDES):
        return {"extra": [], "rows": {}}
    return json.load(io.open(OVERRIDES, encoding="utf-8"))


def build():
    module = register_module()
    rows = module.rows()
    overrides = load_overrides()
    per_row = overrides.get("rows", {})

    entries = []
    for row in rows:
        name = (row.get("mod") or "").strip()
        key = (row.get("load") or "").strip()
        custom = per_row.get(key) or per_row.get(name) or {}
        tag = custom.get("tag") or tag_for(row)
        entries.append({
            "name": name,
            # **THE COUNT ONLY RECONCILES IF THE GAME IS NOT COUNTED AS A MOD**, and the owner's
            # figure is the one to match: "i cuttenlty have 296 (6DLCs, Rimbridge ,
            # Rimrooms(locally))". The engineering register holds 295 rows -- the 294 profile
            # entries plus a row for Core -- so 294 + Rimbridge + Rimrooms is exactly 296, and
            # Core is shown for context rather than added to the total.
            "is_game": (row.get("family") or "").strip().lower() == "rimworld base game",
            "tag": tag,
            "uses": custom.get("uses") or uses_here(row),
            "without": custom.get("without") or without_it(row, tag),
            "watch": custom.get("watch") or watch_for(row),
        })

    for extra in overrides.get("extra", []):
        entries.append({
            "name": extra["name"],
            "is_game": False,
            "tag": extra["tag"],
            "uses": extra["uses"],
            "without": extra["without"],
            "watch": extra["watch"],
        })

    entries.sort(key=lambda e: (TAGS.index(e["tag"]) if e["tag"] in TAGS else 99, e["name"].lower()))
    return entries


def page(entries):
    counts = {}
    for entry in entries:
        counts[entry["tag"]] = counts.get(entry["tag"], 0) + 1

    out = []
    out.append("---")
    out.append("title: The mod list")
    out.append("summary: Every mod Rimrooms was built alongside, what each one is for, and what "
               "you lose by skipping it.")
    out.append("---")
    out.append("")
    out.append("# The mod list")
    out.append("")
    mods = sum(1 for e in entries if not e.get("is_game"))
    out.append("Rimrooms was built alongside **%d** mods and expansions. This page says what each "
               "one is for, and what changes if you leave it out." % mods)
    out.append("")
    out.append("The base game is listed too, for context. It is not counted in that %d." % mods)
    out.append("")
    out.append("## Nothing here is required to launch")
    out.append("")
    out.append("**Rimrooms declares no mod as a hard dependency and starts on its own.** *Required* "
               "below means required for the experience as it was built, never required to run.")
    out.append("")
    out.append("Leave out anything tagged Optional and nothing breaks. Rimrooms falls back to what "
               "the base game already ships.")
    out.append("")
    out.append("| Tag | How many | What it means |")
    out.append("|---|---|---|")
    meanings = {
        "Required": "The game itself.",
        "Recommended": "Built against this. Skipping it loses a part of the intended experience.",
        "Optional": "Works with it, works without it.",
        "Visual only": "Changes how things look and nothing else.",
        "Not needed": "Rimrooms does not interact with it at all.",
    }
    for tag in TAGS:
        if counts.get(tag):
            out.append("| **%s** | %d | %s |" % (tag, counts[tag], meanings[tag]))
    out.append("")

    for tag in TAGS:
        group = [e for e in entries if e["tag"] == tag]
        if not group:
            continue
        out.append("## %s (%d)" % (tag, len(group)))
        out.append("")
        out.append("| Mod | What it does here | Without it | Watch for |")
        out.append("|---|---|---|---|")
        for entry in group:
            out.append("| **%s** | %s | %s | %s |"
                       % (entry["name"], entry["uses"], entry["without"], entry["watch"]))
        out.append("")

    return "\n".join(out) + "\n"


def main():
    apply_changes = "--apply" in sys.argv
    entries = build()
    counts = {}
    for entry in entries:
        counts[entry["tag"]] = counts.get(entry["tag"], 0) + 1

    mods = sum(1 for e in entries if not e.get("is_game"))
    print("public mod register")
    print("  entries           : %d (%d mods, plus the base game shown for context)"
          % (len(entries), mods))
    for tag in TAGS:
        if counts.get(tag):
            print("    %-14s %d" % (tag, counts[tag]))
    hand = len(load_overrides().get("rows", {}))
    print("  hand-authored rows: %d (everything else is composed from the register's own columns)"
          % hand)

    # Every entry must carry a tag from the vocabulary and four non-empty cells. A generated page
    # with a blank cell is the owner's "for all mods" quietly becoming "for most mods".
    problems = []
    for entry in entries:
        if entry["tag"] not in TAGS:
            problems.append("%s carries tag %r, which is not one of %s"
                            % (entry["name"], entry["tag"], ", ".join(TAGS)))
        for field in ("name", "uses", "without", "watch"):
            if not (entry.get(field) or "").strip():
                problems.append("%s has an empty %s" % (entry["name"] or "an unnamed row", field))
    if problems:
        print("")
        print("FAIL: %d problem(s)" % len(problems))
        for problem in problems[:10]:
            print("  - %s" % problem)
        return 1

    body = page(entries)
    if "--check" in sys.argv:
        # **A GENERATED FILE THAT DRIFTS IS THE DEFECT, not the inconvenience.** The battery runs
        # this so the published page can never describe a register it no longer matches.
        current = io.open(TARGET, encoding="utf-8").read() if os.path.isfile(TARGET) else ""
        if current != body:
            print("")
            print("FAIL: %s is out of date. Run `python tools/build-public-register.py --apply`."
                  % os.path.relpath(TARGET, REPO).replace(os.sep, "/"))
            return 1
        print("  generated page    : up to date")
        return 0

    if apply_changes:
        io.open(TARGET, "w", encoding="utf-8", newline="\n").write(body)
        print("  wrote             : %s" % os.path.relpath(TARGET, REPO).replace(os.sep, "/"))
    else:
        print("  nothing written; re-run with --apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
