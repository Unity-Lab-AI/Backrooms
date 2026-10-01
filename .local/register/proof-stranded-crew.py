# -*- coding: utf-8 -*-
"""Assert that closing a gate on a crew never takes them away from the player.

The property this exists for
----------------------------
Owner direction, 2026-09-29:

    "turning off a company gate with pawns inside doesnt lose control of those pawns they have to
     survive till a reconnection is made so they can escape"

**This was already true when the direction arrived**, which is the good outcome and precisely why
it needs a proof: it is a *guarantee*, and a guarantee that nothing enforces is one refactor from
gone. The specific refactor that would break it is an obvious-looking optimisation --

    "a coordinate with nobody on it and no live connection does not need to stay loaded"

-- which would delete a map with a crew standing on it, take colonists away from somebody
permanently, and produce no compiler error, no checker failure and no symptom until a player lost
five people.

The guarantee has four parts, and all four must hold:

  * the coordinate map is **never** removed
  * an expiring window touches **no pawn**
  * a **reconnection** exists, and it is the player's to arrange
  * the reconnection is **not on a clock**, because nothing in this mod is but the gate's own
    opening

Run from the repository root.
"""
import glob
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def strip_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return "\n".join(line for line in text.splitlines()
                     if not line.lstrip().startswith("//"))


parent = strip_comments(io.open(os.path.join(SRC, "Generation", "RimroomsDestinationMapParent.cs"),
                                encoding="utf-8-sig").read())
opening = strip_comments(io.open(os.path.join(SRC, "Gate", "PortalGateOpening.cs"),
                                 encoding="utf-8-sig").read())
comp = strip_comments(io.open(os.path.join(SRC, "Gate", "CompRimroomsGate.cs"),
                              encoding="utf-8-sig").read())
alerts = strip_comments(io.open(os.path.join(SRC, "Presentation", "RimroomsAlerts.cs"),
                                encoding="utf-8-sig").read())

print("")

# 1. THE one. The map a stranded crew is standing on is never removed.
remove = re.search(r"public override bool ShouldRemoveMapNow\(out bool alsoRemoveWorldObject\).*?\n        \}",
                   parent, re.S)
remove_text = remove.group(0) if remove else ""
check("the coordinate decides when its map may be removed", bool(remove_text))
check("a coordinate map is NEVER removed",
      bool(remove_text) and re.search(r"alsoRemoveWorldObject = false;\s*return false;", remove_text) is not None,
      "-- a crew standing on it would be deleted with it, permanently, with no symptom")
check("the decision is unconditional",
      bool(remove_text) and "if" not in remove_text,
      "-- any condition here is a condition under which somebody's colonists vanish")

# 2. An expiring window records a failure and touches nobody.
expiry = re.search(r"else if \(emergencyReturnTicksRemaining > 0\).*?\n            \}", comp, re.S)
expiry_text = expiry.group(0) if expiry else ""
check("the window-expiry path was found", bool(expiry_text))
for token in ["DeSpawn", "Destroy(", "PassToWorld", "SetFaction", "Kill("]:
    check("window expiry does not call %s" % token,
          bool(expiry_text) and token not in expiry_text,
          "-- expiry would take the crew away rather than strand them")

# Nothing anywhere in the gate sources hands a pawn to the world pool. That is the specific act
# that would remove player control while leaving the pawn alive.
gate_text = ""
for path in sorted(glob.glob(os.path.join(SRC, "Gate", "*.cs"))):
    gate_text += strip_comments(io.open(path, encoding="utf-8-sig").read())
check("no gate source hands a pawn to the world pawn pool",
      "PassToWorld" not in gate_text,
      "-- a pawn in the world pool is alive and no longer the player's")

# 3. A reconnection exists and the player arranges it.
check("a recovery opening exists", "public CompanyActionResult RecoverPortalOpening" in opening,
      "-- there would be no way back and the crew would be stranded for ever")
check("recovery is only offered once the return window has gone",
      "if (!IsAwaitingRecovery) { return CompanyActionResult.Refused(\"RR_Gate_RecoveryWindowStillActive\"); }" in opening,
      "-- it would compete with the emergency return instead of following it")
check("recovery re-opens a real window",
      "openingTicksRemaining = PortalOpeningIsIndefinite ? 0 : PortalWindowTicksForTier;" in opening,
      "-- the crew could not actually walk home")
check("recovery costs energy, so it is a decision",
      "GateProps.recoveryOpeningCostWattDays" in opening)

# 4. Nothing about being stranded is on a clock. The chart permits exactly one, the gate's own
#    opening window, and a stranded crew must not acquire a second.
recovery = re.search(r"public CompanyActionResult RecoverPortalOpening.*?\n        \}", opening, re.S)
recovery_text = recovery.group(0) if recovery else ""
check("the recovery path was found", bool(recovery_text))
for token in ["Expire", "expiry", "Deadline", "deadline", "TicksUntil"]:
    check("recovery has no %s" % token,
          bool(recovery_text) and token not in recovery_text,
          "-- a stranded crew is somewhere hard, not on a countdown")

# 5. The player is told. A silent guarantee is one nobody can act on.
# --------------------------------------------------------- the register of the lost
# **The owner asked for this verification by name**, 2026-10-01: check the stranded-crew rows
# against `Company/LostPawnRegister.cs`. The row names the fear: *"If a closing gate hands its
# crew to the world-pawn pool, or despawns them, or marks them lost in any way that removes
# player control, that is a defect against this direction and the most consequential kind."*
#
# **Eleven claims above and not one mentioned the register**, so the guarantee rested on nobody
# ever adding a `Pawn` field to a file whose name sounds exactly like somewhere a pawn would go.
register = strip_comments(io.open(os.path.join(
    SRC, "Company", "LostPawnRegister.cs"), encoding="utf-8-sig").read())

check("THE LOST-PAWN REGISTER HOLDS NAMES, NOT PAWNS",
      "private List<string> lostPawnNames = new List<string>();" in register
      and "public void NoteLostPawn(string name)" in register
      and "public string TakeLostPawnName()" in register
      # **NOT `"Pawn" not in register`.** That is a substring test wearing a type test's clothes,
      # and it is false: `NoteLostPawn`, `TakeLostPawnName`, `LostPawnCapacity`, `lostPawnNames`
      # and `LostPawnCount` all contain those letters. Duplicate-string trap, same shape as
      # 0.12.75-dev's label claim. What matters is whether the **type** is referenced at all.
      and not any(token in register for token in
                  ("List<Pawn>", "Pawn pawn", "Pawn ", "(Pawn", "<Pawn>", "Pawn)")),
      "-- *\"marks them lost in any way that removes player control\"* is impossible here BY "
      "CONSTRUCTION: there is no pawn to mark. It is a list of names, so a stranger in a corridor "
      "can be somebody the player recognises")

check("and it cannot despawn, destroy or hand anybody to the world",
      not any(token in register for token in
              ("PassToWorld", "DeSpawn", "Destroy", "worldPawns", "Discard")),
      "-- the four verbs that would take a colonist away. **None of them is in the file**, and "
      "this claim is what keeps it that way")

check("and nothing it stores can outlive the save or point at a living colonist",
      "Scribe_Collections.Look(ref lostPawnNames" in register
      and "LookMode.Value" in register
      and "Scribe_References" not in register,
      "-- saved by VALUE. A `Scribe_References` list in this file would be a set of live pawn "
      "handles, which is the shape the row is afraid of")

check("an alert reports a crew awaiting recovery",
      "class Alert_RimroomsRecoveryOverdue" in alerts,
      "-- the player would have to notice a stranded crew themselves")
check("that alert keys on the gate's own awaiting-recovery state",
      "IsAwaitingRecovery" in alerts,
      "-- an alert recomputing the condition can disagree with the gate")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: a gate closing on a crew strands them; it never takes them away")
