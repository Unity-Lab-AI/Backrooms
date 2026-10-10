# -*- coding: utf-8 -*-
"""Assert a way out to the world map cannot take a crew from the player, and obeys the map cap.

The property this exists for
---------------------------
A found way out used to require a door the player had already marked on a map the branch already
owned. With nothing marked, `TryRecordWayOut` returned null and the door led **deeper** instead --
so a branch with no marked anchor could never get out at all. That is a dead end for exactly the
player least equipped for one.

It now leads to a world tile the branch does not hold, and there are two outcomes, per the owner:

    "but at that not a player can have up to five maps if settings are right so lets have that 5
     map count be universal max for back rooms main map and claiming maps where u pop out and
     anything over 5 maps defaults to caravans"

Three things have to stay true, and none of them is visible by reading:

  * **THE STRANDED-CREW GUARANTEE IS NOT WEAKENED.** It says no gate source may ever call
    `PassToWorld`, because a pawn in the world pool is alive and no longer the player's. The owner
    decided this feature ships because **a player caravan is still yours**. The narrowing has to be
    exact: a gate **closing**, a window **expiring** and any **traversal** must still never take a
    crew anywhere, and the new path must be reachable only from a player's click.

    In the event our source gained **no new `PassToWorld` call at all** -- the only route to it is
    inside Core's own caravan formation. Our one direct call is pre-existing and releases a
    **declined job applicant**, who was never the player's to begin with.

  * **THE MAP CAP IS THE STRICTER OF TWO.** Ours is five, counting the coordinate the crew is
    standing in. The player's is `Prefs.MaxNumberOfPlayerSettlements`, read through Core's
    `PlayerSettlementsCountLimitReached`. Somebody who set that to one meant it, and ignoring it
    would be this mod overruling a setting the player chose.

  * **NOBODY IS LOST.** The claimed map is generated **before** any pawn is despawned, and a failed
    spawn puts that pawn back. Invariant 55: a transfer that can lose a pawn is a corruption, not a
    threat.

Run from the repository root.
"""
import glob
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def strip_comments(text):
    """Comments must never satisfy OR break a claim. This file names PassToWorld repeatedly in
    prose explaining why it is not called, which would defeat a naive search both ways."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return "\n".join(line for line in text.splitlines()
                     if not line.lstrip().startswith("//") and not line.lstrip().startswith("///"))


def read(*parts):
    return strip_comments(io.open(os.path.join(*parts), encoding="utf-8-sig").read())


def body_of(text, signature):
    start = text.find(signature)
    if start < 0:
        return ""
    brace = text.find("{", start)
    if brace < 0:
        return ""
    depth = 0
    for index in range(brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[brace:index + 1]
    return ""


exit_src = read(SRC, "Portals", "WorldExit.cs")
comp = read(SRC, "Portals", "CompRimroomsEmergence.cs")
frontier = read(SRC, "Portals", "NaturalFrontierService.cs")

# ---------------------------------------------------------------- 1. the dead end is gone
record_call = "campaign.RecordWorldExit(door, origin.OriginId, origin.Seed)"
check("a way out with no marked anchor now leads to the world instead of deeper",
      record_call in frontier,
      "-- a branch with nothing marked could never find a way out at all, which is a dead end for "
      "exactly the player least equipped for one")

# ---------------------------------------------------------------- 2. the guarantee, exactly
all_source = {}
for path in glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True):
    all_source[os.path.relpath(path, SRC).replace(os.sep, "/")] = strip_comments(
        io.open(path, encoding="utf-8-sig").read())

callers = sorted(rel for rel, text in all_source.items() if "PassToWorld" in text)
print("our own PassToWorld callers: %s" % (", ".join(callers) or "NONE"))
check("our source calls PassToWorld in at most one place, and it is the applicant release",
      callers == ["Personnel/RimroomsPersonnelComponent.cs"],
      "-- expected only the declined-applicant release, who was never the player's. Found: %s"
      % ", ".join(callers))
check("the world exit never calls PassToWorld itself",
      "PassToWorld" not in exit_src,
      "-- the only route must be inside Core's own caravan formation")

gate_text = ""
for path in sorted(glob.glob(os.path.join(SRC, "Gate", "*.cs"))):
    gate_text += strip_comments(io.open(path, encoding="utf-8-sig").read())
check("no gate source hands a pawn to the world pawn pool",
      "PassToWorld" not in gate_text,
      "-- unchanged from the original guarantee; a gate closing must never take a crew")

crossing = read(SRC, "Portals", "PortalCrossingService.cs")
check("no traversal hands a pawn to the world pawn pool",
      "PassToWorld" not in crossing,
      "-- crossing a gate must never route a pawn through the world pool")

# ---------------------------------------------------------------- 3. player-ordered only
leave = body_of(exit_src, "public CompanyActionResult LeaveThroughWorldExit(")
check("the leave routine was found", bool(leave))

leave_callers = []
for rel, text in all_source.items():
    if rel == "Portals/WorldExit.cs":
        continue
    leave_callers += [rel] * len(re.findall(r"LeaveThroughWorldExit\s*\(", text))
print("callers of LeaveThroughWorldExit: %s" % (", ".join(sorted(leave_callers)) or "NONE"))
check("exactly one thing calls the leave routine",
      len(leave_callers) == 1,
      "-- more than one caller means one of them might not be a player command. Found: %s"
      % ", ".join(sorted(leave_callers)))
# The call moved into one private method, reached from a gizmo AND from a float-menu option --
# both player clicks. This claim refused that, correctly, because "every caller is a player
# command" is not something source text can decide. It is widened only to things that can be
# checked: which method holds the call, and that both ways into it are clicks.
check("its one caller is a player command action",
      "return campaign.LeaveThroughWorldExit(parent);" in comp
      and "private CompanyActionResult WalkOutToWorld()" in comp
      and "action = delegate { Show(WalkOutToWorld()); }" in comp
      and "Show(WalkOutToWorld());" in comp
      and comp.count("WalkOutToWorld()") == 3,
      "-- it must sit behind a gizmo the player clicks or a float-menu option they choose, never "
      "a tick. Three mentions and no more: the declaration, the gizmo and the menu")

# Nothing automatic may reach it. Keyed off the routine bodies that DO run automatically.
for rel, text in sorted(all_source.items()):
    if "LeaveThroughWorldExit" not in text or rel == "Portals/WorldExit.cs":
        continue
    for automatic in ("GameComponentTick", "MapComponentTick", "TryExecuteWorker", "JobDriver"):
        check("%s does not reach the leave routine from %s" % (rel, automatic),
              automatic not in text,
              "-- an automatic caller would make this the mod taking a crew rather than the player "
              "moving one")

# ---------------------------------------------------------------- 4. the map cap
cap = body_of(exit_src, "public bool CanClaimAnotherMap")
check("the claim gate was found", bool(cap))
check("our own five-map cap is applied",
      "BranchMapCount >= MaximumBranchMaps" in cap,
      "-- the owner's universal max counts the Backrooms map and every claimed tile")
check("the cap is five",
      "MaximumBranchMaps = 5" in exit_src,
      "-- owner-stated: five maps, universally")
check("the player's own settlement limit is honoured too",
      "SettleUtility.PlayerSettlementsCountLimitReached" in cap,
      "-- somebody who set Prefs.MaxNumberOfPlayerSettlements to one meant it, and this mod does "
      "not get to overrule a setting the player chose")
check("the branch map count uses the one ownership predicate",
      "OwnsMap(maps[index])" in body_of(exit_src, "public int BranchMapCount"),
      "-- a second idea of which maps are ours would disagree with the first")
check("over the cap forms a caravan, under it claims",
      "CanClaimAnotherMap" in leave and "ClaimTileAndWalkOut" in leave
      and "FormCaravanAndWalkOut" in leave,
      "-- both outcomes must be reachable, or the cap decides nothing")

# ---------------------------------------------------------------- 5. nobody is lost
claim = body_of(exit_src, "private CompanyActionResult ClaimTileAndWalkOut(")
check("the claim routine was found", bool(claim))
generate_at = claim.find("GetOrGenerateMapUtility.GetOrGenerateMap")
despawn_at = claim.find("pawn.DeSpawn()")
check("the map is generated before any pawn is despawned",
      generate_at >= 0 and despawn_at >= 0 and generate_at < despawn_at,
      "-- if generation fails after a despawn, somebody is standing nowhere. Invariant 55")
check("a failed spawn puts the pawn back where it was",
      "GenSpawn.Spawn(pawn, was, origin);" in claim,
      "-- a pawn that fails to arrive must not be left unspawned")
check("a claim that moves nobody is reported as a refusal",
      "RR_WorldExit_NobodyMoved" in claim,
      "-- reporting success when nobody moved is the dishonest outcome")

travellers = body_of(exit_src, "private List<Pawn> TravellersAt(")
check("the traveller selection was found", bool(travellers))
for forbidden, why in (("pawn.IsPrisoner", "invariant 17: a prisoner can never cross a gate, and "
                        "walking out into the world is a crossing"),
                       ("pawn.IsSlave", "a slave is not staff and is never taken"),
                       ("pawn.Downed", "somebody unconscious on the floor is not walking anywhere, "
                        "and taking them would be the mod moving a crew")):
    check("the leaving party excludes %s" % forbidden.split(".")[1],
          forbidden in travellers,
          "-- %s" % why)
check("only the player's own pawns leave",
      "pawn.Faction != Faction.OfPlayer" in travellers,
      "-- anything else would be this mod abducting somebody else's pawn")

# ---------------------------------------------------------------- 6. the destination is Core's
record = body_of(exit_src, "internal CompanyActionResult RecordWorldExit(")
check("the destination tile is chosen by Core's own site placement",
      "TileFinder.TryFindNewSiteTile" in record,
      "-- our own validity test would be a second opinion that disagrees with the game the first "
      "time somebody installs a biome mod")
check("the tile roll is seeded, so a way out does not move on reload",
      "Rand.PushState" in record and "Rand.PopState" in record,
      "-- TileFinder rolls against Rand; an unseeded roll is a different world every load")
check("no tile found is an honest refusal rather than an invented destination",
      "RR_WorldExit_NoTileFound" in record,
      "-- inventing a tile Core rejected is how a crew ends up in the sea")


# ===================================================== and the trip is two-way, added 2026-10-03
#
# Owner, verbatim: *"ther natureal gates in the backrrooms that lead to the world map tiles( these
# gats currently dont have a way back into the backrooms ... currently and incorrectyl there is no
# way for a pawn to go back into the backrooms when they exit via a natural gate"*.
#
# **`grep -l` across all forty-nine proofs for a return-side claim found NOTHING.** Not one claim
# had ever been made about getting back, which is why a one-way trip reached the owner in play --
# the same blind spot, in the same shape, as the one that let a flat battery report an address
# fault. `LeaveThroughWorldExit` was the only direction that existed, while `WorldExitRecord` had
# been saving `coordinateId` and `doorLoadId` all along with nothing reading them.
portal_keys = io.open(os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6",
                                   "Languages", "English", "Keyed", "RR_Portals.xml"),
                      encoding="utf-8-sig").read()

check("WALKING OUT ONTO A CLAIMED TILE BUILDS THE WAY BACK IN",
      "private CompanyActionResult EstablishReturnGate(" in exit_src
      and "EstablishReturnGate(record, claimed, coordinateDoor, arrival)" in exit_src
      and "PortalConnectionKind.Emergence" in exit_src,
      "-- a recorded way back that nothing reads is not a way back. This is the step that turns "
      "the saved coordinateId and doorLoadId into an edge a pawn can walk")

# **ORDERING IS THE SAFETY PROPERTY**, and it is asserted as an ordering rather than a presence.
# Establishing the gate after the crew moves would mean a failure stranded them ON A MAP instead
# of on a tile -- worse, because it looks finished. This file's own docstring already claimed that
# property for map generation; the return gate has to sit inside it.
check("AND IT IS BUILT BEFORE ANYBODY IS DESPAWNED, EXACTLY ONCE",
      # **The count is part of the claim, not padding.** An ordering asserted with `.index()`
      # alone finds the FIRST occurrence, so adding a SECOND call after the despawn satisfies it
      # while doing the exact thing the claim forbids -- which is how the matching plant went
      # MISSED. "Once, before" is the property; "before" on its own is not.
      exit_src.count("EstablishReturnGate(record, claimed, coordinateDoor, arrival)") == 1
      and "pawn.DeSpawn();" in exit_src
      and exit_src.index("EstablishReturnGate(record, claimed, coordinateDoor, arrival)")
          < exit_src.index("pawn.DeSpawn();"),
      "-- if the way home cannot be made, nothing has moved and the door is still there")

check("and its refusal actually stops the walk-out",
      "if (!returnGate.Success) { return returnGate; }" in exit_src,
      "-- building the gate and then ignoring whether it worked is the same one-way trip with "
      "extra steps. The guard IS the fix")

check("and the map is made the branch's own first, because Register refuses otherwise",
      "CompanyActionResult site = RegisterRemoteSite(claimed);" in exit_src
      and exit_src.index("RegisterRemoteSite(claimed)")
          < exit_src.index("PortalConnectionKind.Emergence"),
      "-- `Register` line 82 wants `OwnsMap(firstAnchor.Map)`, and a Core player settlement is "
      "neither the headquarters nor a coordinate. `OrdinaryBranchMap` asks the same question, "
      "which is why `Mark()` cannot run before this")

# A door standing with no edge behind it is a gate that LOOKS like the way home and is not. That
# is the same lie as a section titled DONE full of open rows, and it is worse than no door.
check("AND A FAILED REGISTRATION TAKES THE GATE BACK DOWN",
      exit_src.count("gate.Destroy(DestroyMode.Vanish);") >= 4
      and '"RR_WorldReturn_NotRegistered"' in exit_src,
      "-- every failure after the spawn removes the door again rather than leaving a false way "
      "home standing on the tile")

check("and the one-way caravan path is still the owner's own rule, not an oversight",
      "FormCaravanAndWalkOut" in exit_src and "CanClaimAnotherMap" in exit_src,
      "-- *\"anything over 5 maps defaults to caravans\"*. A caravan has no map for a gate to "
      "stand on; it walks home overland, which is what a caravan is for")

for key in ("RR_WorldReturn_NotRegistered", "RR_WorldReturn_NoGateCell",
            "RR_WorldReturn_Unavailable", "RR_Event_WorldReturnGateBuilt"):
    check("%s is translated" % key, ("<%s>" % key) in portal_keys,
          "-- a refusal with no string prints a raw key at the player")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: a way out reaches the world, obeys the five-map cap, and takes nobody from you")
