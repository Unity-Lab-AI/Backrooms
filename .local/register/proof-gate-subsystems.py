# -*- coding: utf-8 -*-
"""Row 725: a damaged gate will not hold a connection, and the history records how it went.

The row asks for nine subsystems. **Seven were already built** and were measured before anything
was written, which is the habit that has closed eight rows this session:

    power reserves    the bound battery and the watt-day costs
    calibration       `calibrated`, its work giver and its refusal
    stabilizers       `PortalWindowTier` -- a four-rung project ladder that multiplies the window
                      and stops the countdown entirely at tier 4
    monitoring        the inspect readout, three gate alerts, two containment alerts
    cutoff            `TriggerEmergencyCutoff`, the kill switch, the containment procedure
    cool-down         the opening clock and the return window
    modules           `GateEquipmentLinks` -- roles, maxLinked, single ownership across gates

**Repair and reliability were the genuine gaps**, and the more interesting finding is that a gate
read **no damage at all**: it could be shot to twelve per cent and still hold a connection
perfectly, because `calibrated` was lost only when the binding changed.

Run from the repository root.
"""
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
KEYED = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages", "English",
                     "Keyed")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def strip_cs_comments(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"^\s*///.*$", "", text, flags=re.M)
    return "\n".join(re.sub(r"//.*$", "", line) for line in text.split("\n"))


def body_of(text, signature):
    start = text.index(signature)
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    raise AssertionError("unbalanced body for %r" % signature)


integrity = strip_cs_comments(read(os.path.join(SRC, "Gate", "GateIntegrity.cs")))
gate = strip_cs_comments(read(os.path.join(SRC, "Gate", "CompRimroomsGate.cs")))
history = strip_cs_comments(read(os.path.join(SRC, "Gate", "GateConnectionHistory.cs")))
opening = strip_cs_comments(read(os.path.join(SRC, "Gate", "PortalGateOpening.cs")))
links = strip_cs_comments(read(os.path.join(SRC, "Gate", "GateEquipmentLinks.cs")))
gate_keys = read(os.path.join(KEYED, "RR_Gate.xml"))
history_keys = read(os.path.join(KEYED, "RR_GateHistory.xml"))

print("")
print("repair: a damaged gate loses its calibration")
print("-" * 78)

check("the condition is a FRACTION of Core's own hit points, never an absolute",
      "(float)parent.HitPoints / maximum" in integrity and
      "IntegrityFloorFraction = 0.5f" in integrity,
      "-- the profile contains mods that change building health and armour, and an absolute "
      "number would mean something different in each of them")
check("a building that does not use hit points is always sound",
      "!parent.def.useHitPoints" in integrity,
      "-- and a zero maximum too, so no division by zero and no gate bricked by a modded def")
tick = body_of(integrity, "void TickIntegrity()")
check("the effect is losing calibration, a state that already existed",
      "calibrated = false;" in tick and "stablePowerTicks = 0;" in tick,
      "-- calibration already has a work giver, a refusal and a readout, so the player has "
      "nothing new to learn and this adds no def, job or giver")
check("a live opening is ended through the EMERGENCY path, not just dropped",
      'EnterEmergency("RR_Gate_IntegrityLost")' in tick,
      "-- the emergency path is the one that brings the crew home; dropping the opening is the "
      "difference between a gate failing and a gate losing people")
# The whole call, not the key. A first version checked that the key and the percentage
# APPEARED in the method, and a planted `Find.LetterStack.ReceiveLetter(` -> `Noop(` left both
# arguments in place and the claim passing while nothing was sent. Same defect a fault plant
# caught at 0.12.33-dev: a claim that searches for a string is not a claim about behaviour.
check("the player is told, with the actual condition, through the letter stack",
      'Find.LetterStack.ReceiveLetter("RR_Letter_GateIntegrityLabel".Translate()' in tick and
      "IntegrityFraction.ToStringPercent" in tick,
      "-- invariant 28: a rule that costs work to undo has to be learnable when it fires")
check("the tick costs one comparison when the gate is sound",
      "if (!IsDesignated || IntegritySound) { return; }" in tick,
      "-- this runs on every designated gate forever")
check("the integrity tick is actually called",
      "TickIntegrity();" in gate,
      "-- a subsystem nothing ticks is a subsystem that never runs")
# The property is declared across two lines, which a single-line search cannot see. Match the
# declaration and its body separately rather than guessing at the whitespace between them.
check("opening refuses on the same answer the readout shows",
      "if (IntegrityFailureKey != null)" in gate and
      "public string IntegrityFailureKey" in integrity and
      'return IntegritySound ? null : "RR_Gate_IntegrityTooLow";' in integrity,
      "-- one property read by both, so the refusal and the readout cannot disagree")
check("the readout speaks only when the machine is NOT sound",
      "string integrityText = IntegritySound ? null" in gate,
      '-- a line reading "condition 100%" on every gate forever is noise, and Core already '
      "draws a health bar")
check("and the readout is actually joined into the inspect string",
      "footprint, integrityText, operatorText" in gate,
      "-- a key present in the file is not a claim that anything is drawn")
check("nothing here repairs anything",
      not re.search(r"HitPoints\s*=|HitPoints\s*\+=|TryRepair|Repair\(", integrity),
      "-- fixing it is Core's own construction work; this only refuses to run on a broken "
      "machine")

print("")
print("THE SET OF WAYS A GATE CAN STOP WORKING IS NOW SEVEN, ON PURPOSE")
print("-" * 78)

reasons = sorted(set(re.findall(r'EnterEmergency\("(\w+)"\)', gate + integrity)))
check("the set is enumerated and there are seven",
      len(reasons) == 7,
      "-- measured %s" % reasons)
check("the seventh is the new one, and the other six are unchanged",
      set(reasons) == {"RR_NativeGate_KillSwitchThrown", "RR_Gate_PowerLost",
                       "RR_Gate_OperatorLost", "RR_Gate_WindowExpired",
                       "RR_Gate_TimeCostWindowExhausted", "RR_Gate_EmergencyCutoff",
                       "RR_Gate_IntegrityLost"},
      "-- measured %s. `proof-areas-and-debrief.py` asserted six precisely so that an addition "
      "has to be made deliberately and cannot arrive unnoticed" % reasons)
check("and row 98 is untouched: not one reason reads a neighbouring cell",
      not re.search(r"CellsAdjacent|AdjacentCells", gate + integrity),
      "-- this is a change to the machine, not to its surroundings; mine, wall and roof around "
      "a gate still does nothing to it")

print("")
print("reliability: what actually happened, counted and never rolled")
print("-" * 78)

check("no randomness anywhere in the subsystem",
      "Rand." not in integrity and "Rand." not in history,
      "-- invariant 28 wants every rule learnable, and a machine that sometimes fails for no "
      "visible reason is the definition of unlearnable")
check("outcomes are counted, not stored as a rate",
      "internal int completed;" in history and "internal int emergencies;" in history,
      "-- a stored percentage would be a second number that could disagree with the counts "
      "it came from")
reliability = body_of(history, "public float Reliability")
check("NO DATA reads as no data, not as perfect and not as hopeless",
      "recorded <= 0 ? -1f" in reliability,
      "-- 0% or 100% would be a claim about a coordinate nobody has come back from yet")
check("there is exactly one writer of either count",
      history.count("emergencies++") == 1 and history.count("completed++") == 1,
      "-- two writers is two chances to disagree about how many trips there were")
outcome = body_of(history, "void NoteOpeningOutcome(bool emergency)")
# The comparison itself. `historyCoordinateId` appears three times in this method -- the early
# return, the match and the clear -- so merely finding the name proved nothing, and a planted
# removal of the match left the claim passing while every outcome filed against the first entry.
check("the outcome is filed against the coordinate the opening was actually to",
      "string.Equals(entry.coordinateId, historyCoordinateId," in outcome and
      "entry.NoteOutcome(emergency)" in outcome,
      "-- remembered explicitly rather than read off the front of the list: the history is "
      "most-recently-used first, so 'the first entry is the one we are connected to' is true "
      "today and would be a silent lie the moment anything else records a connection between "
      "opening and closing")
check("the remembered coordinate is cleared whichever way the filing goes",
      outcome.count("historyCoordinateId = null;") == 2,
      "-- otherwise a stale id files the next trip's outcome against the wrong address")
check("it is filed from the one place an opening is torn down",
      gate.count("NoteOpeningOutcome(") == 1 and
      "NoteOpeningOutcome(IsEmergency);" in body_of(gate, "void CloseOpeningCore()"),
      "-- so an outcome cannot be counted twice and cannot be missed")
# Scoped to the method, because `failureKey = null;` appears three times in the file and the
# first is in an unrelated method -- comparing whole-file indices was the check being wrong
# rather than the order being wrong.
close_body = body_of(gate, "void CloseOpeningCore()")
check("and it is read BEFORE failureKey is cleared, inside that method",
      "NoteOpeningOutcome(IsEmergency);" in close_body and
      "failureKey = null;" in close_body and
      close_body.index("NoteOpeningOutcome(IsEmergency);")
      < close_body.index("failureKey = null;"),
      "-- failureKey IS the emergency; reading IsEmergency after clearing it would record "
      "every trip as a success")
check("both counts and the remembered coordinate are saved",
      'Scribe_Values.Look(ref completed, "rr_completed", 0);' in history and
      'Scribe_Values.Look(ref emergencies, "rr_emergencies", 0);' in history and
      'Scribe_Values.Look(ref historyCoordinateId, "rr_gateHistoryCoordinateId");' in history,
      "-- a save made mid-opening must file its outcome against the right address on reload")
check("the player can read it where they choose an address",
      "ReliabilityRow(entry)" in history and
      "new FloatMenuOption(ReliabilityRow(entry), null)" in history,
      "-- the only place the number is a decision rather than trivia")
check("and the no-data case says so in words",
      "RR_GateHistory_NoOutcomes" in history)

print("")
print("the seven that were already built, so nobody rebuilds them")
print("-" * 78)

check("STABILIZERS: the window tier ladder exists and multiplies the window",
      "public int PortalWindowTier" in opening and
      "GateProps.portalWindowMultiplierPerTier" in opening,
      "-- row 725's 'stabilizers'")
check("and it stops the countdown entirely at the top rung",
      "PortalWindowTier >= GateProps.portalIndefiniteTier" in opening,
      "-- which is what a stabiliser is for")
check("and it is earned from COMPLETED projects, so it cannot be lost by spending",
      "record.Completed &&" in opening)
check("MODULES: the equipment link system exists with roles and a per-role cap",
      "class RimroomsGateEquipmentDef" in links and "maxLinked" in links and
      "RoleFor(Thing thing)" in links,
      "-- row 725's 'modules'")
check("and a module linked to one gate is refused to every other",
      "EquipmentLinkFailureKey" in links)
check("CALIBRATION, CUTOFF and COOL-DOWN all still exist",
      "calibrated" in gate and "TriggerEmergencyCutoff" in gate and
      "openingTicksRemaining" in gate and "emergencyReturnTicksRemaining" in gate)

for key in ("RR_Gate_IntegrityTooLow", "RR_Gate_IntegrityLost", "RR_Gate_IntegrityReadout",
            "RR_Letter_GateIntegrityLabel", "RR_Letter_GateIntegrityText"):
    check("%s is translated" % key, "<%s>" % key in gate_keys)
for key in ("RR_GateHistory_Reliability", "RR_GateHistory_NoOutcomes"):
    check("%s is translated" % key, "<%s>" % key in history_keys)

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: a broken gate will not hold a connection, and the history says how the "
      "trips went")
