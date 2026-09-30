# -*- coding: utf-8 -*-
"""Assert a gate's approach cell cannot be built on, that flooring is fine, and that doubt allows.

The property this exists for
---------------------------
Owner answer at the fork, 2026-09-29, verbatim: **"option 2 but flooring is fine"** -- against the
question of what happens when a player walls, mines or builds on the cell a pawn must stand on to
use a gate. Option 2 was *"the approach cell cannot be built on"*, and the owner's addition carves
out terrain.

This sits on top of a guarantee that already shipped. 0.12.3-dev made the approach cell
**re-derived at use time** instead of frozen at registration, which is what stops a connection
breaking when the geometry changes. **This layer stops the player bricking their own gate and tells
them why at the moment they try**, which is the half the owner's answer is about.

Five things have to stay true:

  * **FLOORING IS FREE BY CONSTRUCTION, NOT BY A SPECIAL CASE.** A floor is a `TerrainDef`, and
    terrain placement never consults a `PlaceWorker` at all. If this were implemented as a list of
    allowed defs instead, the carve-out would be something somebody has to remember.

  * **WHAT COUNTS AS BLOCKING IS CORE'S OWN RULE.** `GenGrid.Standable` is walkable plus *every
    thing in the cell having `Traversability.Standable`*. So the test is `passability !=
    Traversability.Standable` -- which admits a power conduit and refuses a wall, a barricade or
    another mod's building this project has never heard of. **A list of def names would have been
    wrong for the 294 mods the moment one of them shipped a new wall.**

  * **THE CELL IS RE-DERIVED, NEVER READ FROM THE SAVE.** The saved endpoint cell is a snapshot
    that exists so moving a door cannot silently redirect a route. The cell a pawn will actually
    use is whatever the geometry says now, and that is the one worth protecting.

  * **EVERY UNCERTAINTY ALLOWS THE PLACEMENT.** This runs on every placement check for every
    building in a profile with 294 other mods. A refusal it gets wrong is a player who cannot
    build; an allowance it gets wrong is a gate re-deriving its approach cell exactly as it already
    does. The asymmetry is not close.

  * **THE PATCH REACHES OTHER MODS' BUILDINGS WITHOUT TOUCHING THEIR FILES.** It adds one place
    worker to Core's abstract `BuildingBase`, which nearly every building descends from, and
    RimWorld merges an inherited list node with a child's own.

Run from the repository root.
"""
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")
GAME = os.path.join("C:", os.sep, "Program Files (x86)", "Steam", "steamapps", "common",
                    "Rimworld", "Data")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def strip_cs_comments(text):
    """The reasoning is written at length in this file and names the very tokens the claims look
    for -- Traversability.Standable, TerrainDef, the owner's words. Prose must not satisfy a claim."""
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return "\n".join(re.sub(r"//.*$", "", line) for line in text.split("\n"))


def strip_xml_comments(text):
    return re.sub(r"<!--.*?-->", " ", text, flags=re.S)


def body_of(text, signature):
    start = text.index(signature)
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    raise AssertionError("unbalanced body for %r" % signature)


worker_path = os.path.join(SRC, "Portals", "PlaceWorker_GateApproach.cs")
worker = strip_cs_comments(read(worker_path))
service = strip_cs_comments(read(os.path.join(SRC, "Portals", "PortalAddressService.cs")))
patch = strip_xml_comments(read(os.path.join(MOD, "Patches", "RR_GateApproachPlacement.xml")))
keys = read(os.path.join(MOD, "Languages", "English", "Keyed", "RR_Portals.xml"))

print("")
print("proof: a gate's approach cell is reserved against blocking, and flooring is fine")
print("")

# ------------------------------------------------------------------ 1. flooring
print("1. flooring is fine, and structurally so")
check("the worker is a PlaceWorker, which terrain placement never consults",
      "class PlaceWorker_GateApproach : PlaceWorker" in worker,
      "-- a floor is a TerrainDef; if this were a tick loop over blueprints the carve-out would "
      "have to be written and remembered")
check("a non-ThingDef buildable is allowed outright",
      "ThingDef definition = checkingDef as ThingDef;" in worker and
      "definition == null" in worker,
      "-- belt and braces: even handed a TerrainDef directly, it allows")
check("no allow-list of def names exists anywhere in the worker",
      not re.search(r'"(Wall|Sandbags|Barricade|Door|Autodoor)"', worker),
      "-- naming defs would be wrong for the 294 mods the moment one shipped a new wall")

# ------------------------------------------------------------------ 2. Core's rule
print("")
print("2. what counts as blocking is Core's own standability rule")
decision = body_of(worker, "private static AcceptanceReport Check(")
check("anything Traversability.Standable is allowed",
      "definition.passability == Traversability.Standable" in decision,
      "-- GenGrid.Standable requires every thing in the cell to be Standable, so this is the "
      "exact complement of Core's own test")
check("the whole footprint is tested, not just the centre cell",
      "GenAdj.OccupiedRect(loc, rot, definition.Size)" in decision,
      "-- a 2x2 building placed beside the approach cell still covers it")

# ------------------------------------------------------------------ 3. re-derived
print("")
print("3. the protected cell is re-derived, never read from the save")
endpoint = body_of(worker, "private static AcceptanceReport CheckEndpoint(")
check("the cell comes from ApproachCellFor at check time",
      "PortalAddressService.ApproachCellFor(door)" in endpoint)
check("the saved endpoint cell is NOT used as the protected cell",
      "endpoint.AnchorCell" not in endpoint,
      "-- the snapshot exists so a moved door cannot redirect a route, not to say where to stand")
check("ApproachCellFor is still the single implementation",
      "This is the single implementation; callers must not re-derive it" in read(
          os.path.join(SRC, "Portals", "PortalAddressService.cs")),
      "-- two derivations would protect one cell and use another")
check("an invalid approach cell reserves nothing",
      "!approach.IsValid" in endpoint,
      "-- a gate with no standable neighbour is already unusable; refusing construction around it "
      "would punish the player for a state they cannot see")
check("a despawned, destroyed or off-map door reserves nothing",
      "door.Destroyed" in endpoint and "door.Spawned" in endpoint and "door.Map != map" in endpoint)

# ------------------------------------------------------------------ 4. doubt allows
print("")
print("4. every uncertainty allows the placement")
allows = body_of(worker, "public override AcceptanceReport AllowsPlacing(")
check("a thrown exception allows the placement",
      "catch (Exception)" in allows and "AcceptanceReport.WasAccepted" in allows,
      "-- this runs for every building in the game; it must never be the reason somebody cannot build")
check("no game, no network or no connections allows the placement",
      "network == null" in decision and "connections.Count == 0" in decision)
check("the refusal names the gate it is protecting",
      "RR_Portals_ApproachCellReserved" in endpoint and "door.LabelShortCap" in endpoint,
      "-- invariant 28: the rule has to be learnable, so the message says which gate and why")
check("the refusal is translated",
      "<RR_Portals_ApproachCellReserved>" in keys)
check("the refusal tells the player flooring is allowed",
      "floor" in keys[keys.index("<RR_Portals_ApproachCellReserved>"):][:400].lower(),
      "-- the carve-out is useless if nobody knows about it")

# ------------------------------------------------------------------ 5. the patch
print("")
print("5. the patch reaches other mods' buildings without touching their files")
check("it targets Core's abstract BuildingBase",
      'Defs/ThingDef[@Name="BuildingBase"]' in patch)
check("BuildingBase really is an abstract def in the installed game",
      os.path.isdir(GAME) and any(
          'Name="BuildingBase"' in read(os.path.join(root, name)) and 'Abstract="True"' in read(os.path.join(root, name))
          for root, _, files in os.walk(os.path.join(GAME, "Core", "Defs", "ThingDefs_Buildings"))
          for name in files if name.endswith(".xml")),
      "-- if this parent is renamed the patch silently reaches nothing")
check("it adds the element when absent AND appends when present",
      patch.count("PatchOperationConditional") == 3 and patch.count("PatchOperationAdd") == 2,
      "-- doing only the first would append a SECOND placeWorkers element the day Core adds one")
check("it never replaces an existing list",
      "PatchOperationReplace" not in patch and "PatchOperationRemove" not in patch,
      "-- another mod's place worker on the same parent must survive this")
check("no other mod's def is named by the patch",
      "PatchOperationFindMod" not in patch and "PH_" not in patch,
      "-- Core only; this is not a compatibility patch")
check("the patch file is on the package allowlist",
      "RR_GateApproachPlacement.xml" in read(os.path.join(REPO, "tools", "package-files.json")))

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: the approach cell is reserved against blocking, flooring is fine, doubt allows")
