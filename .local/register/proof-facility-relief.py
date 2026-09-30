# -*- coding: utf-8 -*-
"""Assert every claim the clean-up team rests on.

The property this exists for
----------------------------
The clean-up team is a **guarantee**: *"so that facilities never die"*. A guarantee that
silently stops applying is worse than no guarantee, because the player has been told they
cannot lose and has arranged their play around it.

Every load-bearing claim here is invisible at compile time. A missing `PawnKindDef` is a
`GetNamedSilentFail` returning null. A renamed Core `ThingDef` is a supply line that quietly
drops out of the drop. A change to Core's `GameEnder` is a game-over screen landing on a player
who was promised a rescue. The build reports none of it.

Run from the repository root.
"""
import io
import glob
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GAME = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data"
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")
RELIEF = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Company", "FacilityRelief.cs")
ROLES = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Personnel", "HiringPolicyDef.cs")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


source = io.open(RELIEF, encoding="utf-8-sig").read()

# --------------------------------------------------------------------------- our own defs
our_kinds = set()
for path in glob.glob(os.path.join(MOD, "Defs", "**", "*.xml"), recursive=True):
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        continue
    for node in root.iter("PawnKindDef"):
        name = node.findtext("defName")
        if name:
            our_kinds.add(name.strip())

# --------------------------------------------------------------------------- Core defs
core_things = set()
for path in glob.glob(os.path.join(GAME, "**", "*.xml"), recursive=True):
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError):
        continue
    for node in root.iter("ThingDef"):
        name = node.findtext("defName")
        if name:
            core_things.add(name.strip())

print("our pawn kinds      : %d" % len(our_kinds))
print("core thing defs     : %d" % len(core_things))
print("")

# 1. Every kind the relief names must exist. A missing one is a silent fallback to Core's
#    ordinary colonist, which works but is not the crew the branch was promised.
named_kinds = sorted(set(re.findall(r'return "(RR_\w*Staff)";', source)))
check("the relief names at least five staff kinds (%d)" % len(named_kinds), len(named_kinds) >= 5)
for kind in named_kinds:
    check("%s exists as a PawnKindDef" % kind, kind in our_kinds,
          "-- the relief would silently fall back to Core's ordinary colonist")

# 2. Those five kinds are the whole point of this checkpoint: they existed and nothing read
#    them. If a later change stops the relief reading them, they go back to being dead defs.
for kind in sorted(our_kinds):
    if not kind.endswith("Staff"):
        continue
    check("%s is read by the relief" % kind, kind in named_kinds,
          "-- authored, loaded, and wired to nothing again")

# 3. Every role the relief requisitions must be a role the company actually recognises, or
#    the arrival lands with a role no work assignment understands.
role_block = re.search(r"ReliefRoles\s*=\s*\{([^}]*)\}", source)
relief_roles = re.findall(r'"([a-z_]+)"', role_block.group(1)) if role_block else []
valid_roles = re.findall(r'"([a-z_]+)"', re.search(
    r"ids\s*=\s*\{([^}]*)\}", io.open(ROLES, encoding="utf-8-sig").read()).group(1))
check("the relief requisitions five roles (%d)" % len(relief_roles), len(relief_roles) == 5)
for role in relief_roles:
    check("role %s is a real company role" % role, role in valid_roles,
          "-- valid roles are " + ", ".join(valid_roles))
for role in valid_roles:
    check("role %s is covered by the relief" % role, role in relief_roles,
          "-- the branch comes back missing a discipline")

# 4. Every supply line must be a Core def. A renamed one is a line that silently disappears
#    from the drop, and the player is told they were resupplied.
SUPPLY = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Company", "CompanySupplyDrop.cs")
supply_source = io.open(SUPPLY, encoding="utf-8-sig").read()
supply_block = re.search(r"Lines\s*=\s*\{(.*?)\n        \};", supply_source, re.S)
supplies = re.findall(r'"(\w+)"', supply_block.group(1)) if supply_block else []
check("the relief drops at least four supply lines (%d)" % len(supplies), len(supplies) >= 4)
for item in supplies:
    check("%s is a Core ThingDef" % item, item in core_things,
          "-- the line would vanish from the drop without a word")

# 5. Contact gates the whole thing. Owner: "clena up tema is only once u are in communication
#    and working with the corporation". If this guard ever moves below another early return,
#    a branch that has not earned contact gets the rescue anyway.
check("the relief refuses before corporation contact",
      re.search(r"if \(!corporationContact\) \{ return; \}", source) is not None,
      "-- the Store and Solo/Group starts would begin un-loseable")

# 6. THE subtle one. "Alive anywhere" must not become "alive here". A crew standing in a
#    Backrooms coordinate is alive and the facility is not dead -- if this scan ever starts
#    asking about Spawned or Map, a player who takes everybody through a gate comes home to a
#    relief team and a duplicate payroll.
living = re.search(r"private bool AnyLivingStaff\(\).*?\n        \}", source, re.S)
living_text = living.group(0) if living else ""
check("the living-staff scan was found", bool(living_text))
check("the living-staff scan does not ask where the pawn is",
      "Spawned" not in living_text and ".Map" not in living_text,
      "-- a crew inside the Backrooms would read as a dead facility")
check("the living-staff scan does not treat downed as dead",
      "Downed" not in living_text,
      "-- unconscious staff would be replaced while they were still breathing")

# 7. No cap and no escalation. The corporation "will put up with anything", and a rescue that
#    gets stingier is a deadline wearing a different hat.
check("nothing compares the relief count against a limit",
      re.search(r"reliefCount\s*[<>]=?\s*\d", source) is None,
      "-- a capped guarantee is not a guarantee")
check("nothing compares the relief timestamp against a limit",
      re.search(r"lastReliefTick\s*[<>+-]", source) is None,
      "-- a timestamp compared against a limit is a countdown")

# --------------------------------------------------------------------------- Core facts
assembly = os.path.join(os.path.dirname(GAME), "RimWorldWin64_Data", "Managed",
                        "Assembly-CSharp.dll")
ilspy = os.path.join(REPO, ".local", "tools", "ilspycmd.exe")
out = subprocess.check_output([ilspy, "-t", "RimWorld.GameEnder", assembly],
                              stderr=subprocess.STDOUT).decode("utf-8", "replace")

# 8. The relief clears Core's game-over flag directly. That is only legal because the field is
#    public, and only sufficient because Core clears it again whenever a free colonist exists.
check("Core GameEnder.gameEnding is still a public field",
      re.search(r"public bool gameEnding;", out) is not None,
      "-- the relief writes to it without Harmony")
check("Core still clears gameEnding when a map has a free colonist",
      re.search(r"FreeColonistsSpawnedOrInPlayerEjectablePodsCount >= 1", out) is not None
      and re.search(r"gameEnding = false;", out) is not None,
      "-- landing a crew would no longer cancel the countdown on its own")
check("Core's game-over countdown is still 400 ticks",
      re.search(r"GameEndCountdownDuration = 400", out) is not None,
      "-- the relief's 60-tick cadence is chosen to land well inside it")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: the facilities-never-die guarantee still has everything it stands on")
