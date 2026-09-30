# -*- coding: utf-8 -*-
"""Assert that every request offers a way through even to a branch that has nothing.

The safety property is an ORDERING, not a count:

    the authored floor is counted BEFORE any capability is consulted.

If deriving ever returned nothing -- no catalogue, no witnesses, a broken save, a mod that
removed the procurement defs -- a request must still offer two ways through. This proof checks
the floor alone, with capability deliberately ignored, because that is the case nobody plays and
therefore the case nobody notices is broken.

Run from the repository root.
"""
import io
import os
import re
import sys
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REQUESTS = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                        "RimroomsRequestDefs", "RR_Requests.xml")
ROUTES_SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Company", "RequestRoutes.cs")
DEFS_SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Company", "RequestDefs.cs")
KEYED = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages", "English",
                     "Keyed")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


# --------------------------------------------------------------------------- the requests
root = ET.parse(REQUESTS).getroot()
requests = []
for node in root:
    routes = []
    container = node.find("successRoutes")
    for li in (container if container is not None else []):
        routes.append({
            "kind": (li.findtext("kind") or "Deliver").strip(),
            "labelKey": (li.findtext("labelKey") or "").strip(),
            "descriptionKey": (li.findtext("descriptionKey") or "").strip(),
            "thingDefName": (li.findtext("thingDefName") or "").strip(),
            "logKind": (li.findtext("logKind") or "").strip(),
            "projectDefName": (li.findtext("projectDefName") or "").strip(),
            "redirectTo": (li.findtext("redirectTo") or "").strip(),
        })
    requests.append({
        "defName": node.findtext("defName"),
        "tutorial": (node.findtext("tutorial") or "false").strip().lower() == "true",
        "order": int(node.findtext("tutorialOrder") or "0"),
        "prereqs": [li.text.strip() for li in (node.find("prerequisiteRequests") or [])],
        "routes": routes,
    })

print("requests defined : %d" % len(requests))
check("at least one request is defined", len(requests) > 0)

# 1. THE absolute. Two or more authored routes, capability ignored entirely.
for request in requests:
    check("%s authors at least two routes (%d)" % (request["defName"], len(request["routes"])),
          len(request["routes"]) >= 2,
          "-- a branch with nothing would see one path")

# 2. The rule that makes the count mean something.
for request in requests:
    kinds = set(route["kind"] for route in request["routes"])
    check("%s authors at least two DIFFERENT kinds (%s)"
          % (request["defName"], ", ".join(sorted(kinds))),
          len(kinds) >= 2,
          "-- one route written twice")

# 3. Every route's strings must resolve, or a player reads a raw key off the card.
keys = set()
for name in os.listdir(KEYED):
    if not name.endswith(".xml"):
        continue
    for node in ET.parse(os.path.join(KEYED, name)).getroot():
        if isinstance(node.tag, str):
            keys.add(node.tag)

for request in requests:
    for route in request["routes"]:
        for field in ("labelKey", "descriptionKey"):
            value = route[field]
            check("%s route %s %s resolves" % (request["defName"], route["kind"], field),
                  value in keys, "-- %r is not a keyed string" % value)

# 4. The derived routes' own strings must resolve too. They are written once and reused, so a
#    missing one breaks every request that ever derives that kind.
for key in ("RR_Route_PurchaseLabel", "RR_Route_PurchaseDesc",
            "RR_Route_TestifyLabel", "RR_Route_TestifyDesc"):
    check("derived route string %s resolves" % key, key in keys)

# 5. THE ORDERING. The floor must be assembled before capability is consulted, in the source.
#    Checked textually because it is a property of the code's shape, and a test cannot prove it
#    without a running game.
source = io.open(ROUTES_SRC, encoding="utf-8-sig").read()
floor_at = source.find("routes.AddRange(definition.successRoutes")
derive_at = source.find("foreach (RimroomsSuccessRoute extra in Derived(")
check("the authored floor is added before capability is consulted",
      floor_at != -1 and derive_at != -1 and floor_at < derive_at,
      "-- deriving first would let a capability route stand in for an authored one")

# 6. A derived route must never be counted toward the floor.
check("AuthoredKinds counts only definition.successRoutes",
      re.search(r"AuthoredKinds\(.*?\)\s*\{[^}]*definition\.successRoutes", source, re.S) is not None
      and "Derived(" not in source[source.find("AuthoredKinds"):],
      "-- the floor must not be able to include a derived route")

# 7. The def shape must have nowhere to put a deadline. Enforcement by absence.
defs_source = io.open(DEFS_SRC, encoding="utf-8-sig").read()
for forbidden in ("expiresTick", "expiryTick", "deadline", "timeLimit"):
    check("RimroomsRequestDef has no %r field" % forbidden,
          not re.search(r"public\s+\w+\s+" + forbidden, defs_source, re.I),
          "-- a deadline could be configured onto a request")

# 8. Every def name a route references must resolve. A route naming a def that does not exist
#    loads clean, shows on the card, and can never be satisfied -- the exact failure mode that
#    put "Multianalyzer" in a marker role and matched nothing.
GAME = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data"
import glob as _glob
game_things = set()
# EVERY def file, not just the ones under a ThingDefs* path. The first version of this globbed
# "**/ThingDefs*/*.xml" and reported TextBook as missing -- it is a ThingDef declared in
# Core/Defs/Books/BookDefs.xml. The index was wrong, not the content. RimWorld does not require
# a ThingDef to live in a file whose name says so, and a proof that assumes otherwise reports a
# correct reference as a fault, which is the worst thing a proof can do.
for _path in _glob.glob(os.path.join(GAME, "**", "*.xml"), recursive=True):
    try:
        _root = ET.parse(_path).getroot()
    except ET.ParseError:
        continue
    if _root.tag != "Defs":
        continue
    for _node in _root:
        _name = _node.findtext("defName") if isinstance(_node.tag, str) else None
        if _node.tag == "ThingDef" and _name:
            game_things.add(_name.strip())

PROJECTS = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                        "RimroomsProjectDefs", "RR_CompanyProjects.xml")
projects = set()
for _node in ET.parse(PROJECTS).getroot():
    _name = _node.findtext("defName")
    if _name:
        projects.add(_name.strip())

check("the installed game data was found", len(game_things) > 1000,
      "(only %d ThingDefs)" % len(game_things))

for request in requests:
    for route in request["routes"]:
        thing = route["thingDefName"]
        if thing:
            check("%s route %s names %s, which exists" % (request["defName"], route["kind"], thing),
                  thing in game_things, "-- not a ThingDef in the installed game")
        project = route["projectDefName"]
        if project:
            check("%s route %s names project %s, which exists"
                  % (request["defName"], route["kind"], project),
                  project in projects, "-- not a defined company project")
        redirect = route["redirectTo"]
        if redirect:
            check("%s route %s redirects to %s, which exists"
                  % (request["defName"], route["kind"], redirect),
                  redirect in projects or redirect in set(r["defName"] for r in requests),
                  "-- redirects nowhere")

# 9. A route that names a log must name one the campaign can actually count. A typo here is
#    silent: CompletedLogCount returns 0 for an unknown kind, so the route would never satisfy.
for request in requests:
    for route in request["routes"]:
        if route["logKind"]:
            check("%s route %s names a real log kind (%s)"
                  % (request["defName"], route["kind"], route["logKind"]),
                  route["logKind"] in ("route", "distortion", "entity"),
                  "-- CompletedLogCount returns 0 for anything else, silently")

# 10. The tutorial prerequisite chain must be a single ordered line: request N requires N-1.
#     Without this a branch could be offered the hinge before anything it is a hinge for.
by_order = {r["order"]: r for r in requests if r["tutorial"]}
for order in sorted(by_order)[1:]:
    current, previous = by_order[order], by_order[order - 1]
    check("%s requires %s" % (current["defName"], previous["defName"]),
          previous["defName"] in current["prereqs"],
          "-- the tutorial line can be taken out of order")

# 11. No prerequisite cycle, checked transitively.
by_name = {r["defName"]: r for r in requests}
def reaches(start, target, seen=None):
    seen = seen or set()
    if start in seen:
        return False
    seen.add(start)
    for required in by_name.get(start, {}).get("prereqs", []):
        if required == target or reaches(required, target, seen):
            return True
    return False
cycles = [n for n in by_name if reaches(n, n)]
check("no request requires itself through any chain", not cycles, "-- " + ", ".join(cycles))

# 12. The tutorial line must be contiguous from zero, or there is a gap nothing fills.
check("tutorial orders are contiguous from 0 (%s)" % sorted(by_order),
      sorted(by_order) == list(range(len(by_order))))

# 13. The tutorial line must be orderable: distinct orders, starting at the first.
tutorial = sorted([r for r in requests if r["tutorial"]], key=lambda r: r["order"])
orders = [r["order"] for r in tutorial]
check("tutorial orders are distinct (%s)" % orders, len(set(orders)) == len(orders))
if tutorial:
    check("the tutorial line starts at order 0", orders[0] == 0)

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: every request offers a way through to a branch that has nothing")
