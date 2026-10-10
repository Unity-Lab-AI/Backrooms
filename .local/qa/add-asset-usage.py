"""Add a `usage` map to tools/asset-descriptions.json: what a player does with each asset.

Owner, 2026-10-06: *"im not seeing the pictures of the assets in the wiki with theri right up
details and how the are used in game play"*.

The page already had two authored-or-derived facts per asset -- what a drawing **depicts**, and the
def that **loads** it -- and neither of those is what a player does with the thing. This writes the
third. Every line below is taken from the shipped defs, the source, or the wiki page that already
describes that system, never invented: a usage note that is wrong is worse than a blank one, because
a reader checks this page precisely because they cannot see inside the package.

The existing descriptions are loaded and re-dumped untouched. Run once; it is idempotent.
"""
import io
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TARGET = os.path.join(REPO, "tools", "asset-descriptions.json")

CHARGE = ("Drawn over the gate's frame while a connection is coming up, one frame every six ticks. "
          "You see it from designating the ramp until it reaches full.")
ACTIVATION = ("Part of the one-off burst at the moment the ramp reaches full. It plays once and "
              "stops; it is not saved, so reloading mid-cycle does not replay it.")
OPEN = ("Loops over the frame for as long as the connection stands, one frame every ten ticks — "
        "slower than the charge cycle, so an open gate looks settled rather than straining.")
SLIDE = ("Shown behind the main menu, in turn with the other eleven. Turn the slideshow off, or set "
         "reduced motion to hold one still image, in the mod's settings.")

USAGE = {
    # ---- buildings -------------------------------------------------------------------------
    "RR_EmergencyCutoff": (
        "Build it on the conduit run into a gate's equipment, under Power. Flicking it opens the "
        "circuit and ends an open connection, which starts the crew's return window — and flicking "
        "it is ordinary colonist work, so somebody at home can cut a connection while a crew is "
        "still on the far side."),
    "RR_FieldAnalysisBench": (
        "Build under Production, needs Machining. Bind it to a gate on the Machine pane as the "
        "assembly bench and run the assemble-gate-section bill on it; it also makes company field "
        "journals. An ordinary machining table does the same jobs. Turning it swaps a two-cell "
        "counter for a one-wide, two-deep one, so leave room at the operating side."),
    "RR_GateConsole": (
        "Build under Misc, needs Microelectronics basics. A working communications console that can "
        "also be bound to a gate as its control station — the first of up to four stations, so an "
        "operator can stand up to eat the moment another sits down. An ordinary comms console works "
        "too. Remember step 8: the console has to be set to gate control on the console itself."),
    "RR_ReturnBeacon": (
        "Build under Furniture, needs Electricity. A small amber lamp for marking a spot rather "
        "than lighting a room — a landmark at a threshold or a junction you want to find again."),
    "RR_SiteFluorescent": (
        "Build under Furniture, needs Electricity. Throws a wide flat pool rather than a bright "
        "circle, so a corridor reads as lit instead of as three pools of light."),
    "RR_UtilityGenerator": (
        "Build under Power, needs Electricity. Wood-fired, 1400W against a standard set's 1000 for "
        "the same footprint — and it eats and breaks for it. A branch running one is usually a "
        "branch that could not reach a grid."),
    "RR_MachineGate": (
        "Never placed in the world. It is the picture on the **Set Gate** button you click on a "
        "door to designate it, drawn face on, which is right for an icon and wrong for the floor."),

    # ---- the gate frames -------------------------------------------------------------------
    "RR_GateFrame_1x1": (
        "Appears by itself on a designated single-cell door — a door or autodoor. It is cosmetic: "
        "the door keeps its own leaves, opening animation and access rules, and the transparent "
        "centre keeps pawns visible. Hide it with **Show company gate frames** in the settings."),
    "RR_GateFrame_1x2": (
        "Appears on a designated two-cell gate, which Core gives you through an ornate door. Same "
        "cosmetic rules as the 1x1."),
    "RR_GateFrame_1x3": (
        "Appears on a designated three-cell gate — a wide door from another mod, or three ordinary "
        "doors bound into one run. Three cells is the width that passes anything."),
    "RR_GateFrame_2x3": (
        "Appears on the widest supported gate, a bound two-by-three run. A wider gate draws more "
        "power while open and takes longer to bring up, so the footprint is a real choice."),

    # ---- items -----------------------------------------------------------------------------
    "RR_CompanyJournal_Closed": (
        "What you see on a shelf, in a pack, or being hauled. Right-click the book with a colonist "
        "to send it through a gate; right-click and pick *What is this journal for?* for the four "
        "steps in the game."),
    "RR_CompanyJournal_Open": (
        "Drawn while a colonist is actually reading the journal, so you can tell at a glance that "
        "somebody is working on a record rather than carrying it."),
    "RR_CompanyJournal_Vertical": (
        "Drawn when the journal is stood upright on a shelf — including the archive shelf you "
        "designated, which is where a filled book has to end up before a researcher can analyse it."),
    "RR_FieldRecorder": (
        "Build under Production, needs Microelectronics basics. Stand it beside a field analysis "
        "bench and that bench works faster. One per bench. One cell, and it can be uninstalled and "
        "carried, so a crew can take it through a gate and set it down out there."),
    "RR_SealedEvidenceCase": (
        "Build under Furniture. Storage that accepts recordings and journals and nothing else, so "
        "what is inside it is always what it says it is — a shelf will take whatever a hauler "
        "decides belongs there. Carryable through a gate."),
    "RR_SurveyTag": (
        "Build under Misc. Set it down and give it a meaning; the colour **is** the meaning. Read "
        "the same way as a glow pod, with the one difference that matters underground: a glow pod "
        "is alive and dies on its own schedule, and a tag does not."),

    # ---- floors ----------------------------------------------------------------------------
    "RR_FadedInstitutionalCarpet": (
        "Lay it under Floors, needs Carpet making. Same cloth cost, same research and the same "
        "cleaning penalty as any other carpet — what is ours is the surface, which is the one the "
        "places out there are floored with."),

    # ---- sound cues ------------------------------------------------------------------------
    "RR_GateRampUp": (
        "Plays when a ramp starts, after the message and the record. It ends **unresolved** on "
        "purpose: that is what tells you the gate is becoming dangerous rather than becoming safe."),
    "RR_GateCalibrate": (
        "A beat at each of the three interior quarters of the way up. Deliberately not the fourth — "
        "that tick is where the ramp completes, and activation owns it."),
    "RR_GateActivate": (
        "The moment the ramp reaches full, played with the activation flash from the same event so "
        "the two can never drift into a flash with no sound."),
    "RR_GateRampDown": (
        "Plays when a connection closes normally, and when a ramp is stopped on purpose. It "
        "**resolves** into a latch, which is the contrast that says this was a safe outcome."),
    "RR_GateSpinLoop": (
        "Hums under the whole ramp and stops when the ramp does. Reconciled every tick rather than "
        "started and stopped by event, so it cannot be left playing — and it restarts by itself "
        "after a reload mid-ramp."),
    "RR_GateOpenLoop": (
        "The quieter presence while a connection is open. Same self-terminating loop as the spin "
        "hum: a destroyed gate goes quiet on its own."),
    "RR_GateEmergency": (
        "Plays when the gate itself has gone wrong — a fault or a forced return. Distinct from the "
        "ordinary warning on purpose: a window running short is the gate working correctly."),
    "RR_CutoffThrown": (
        "Plays instead of the emergency cue when the cause was **somebody's decision** — the "
        "emergency cutoff or the kill switch. A mechanical clack rather than a failing motor."),
    "RR_GatePowerRise": (
        "Plays when an opening starts and the gate pulls on its reserve, including on a recovery "
        "opening."),
    "RR_GateWarning": (
        "The mod's most-used cue, which is why it is short. The ten, five and two-minute window "
        "warnings, a standing recall, and something coming through a gate."),
    "RR_SectionAssembled": (
        "Plays as each of the gate's four assembly sections completes, and again when the assembly "
        "finishes — so four people working four benches each get the confirmation."),
    "RR_MarkerSet": (
        "Plays when a survey tag is given a meaning, which is the moment the tag starts being worth "
        "anything to you."),
    "RR_JournalFiled": (
        "Plays when a filled journal reaches the records archive and custody is established. That "
        "is the step the light on an accepted job is waiting for."),
    "RR_AnalysisComplete": (
        "Plays when a researcher finishes analysing a finding at a bound laboratory — the point the "
        "insight is actually yours to spend."),
    "RR_ContractPaid": (
        "Plays when the company pays out on a completed request, alongside the letter. A receipt "
        "rather than a jackpot."),
    "RR_FieldRadio": (
        "Plays when a crew member calls in an observation from the field. Silenced by **Mute field "
        "and radio cues**."),
    "RR_SpatialTell": (
        "Plays when the space itself behaves incorrectly. Deliberately unlike every other cue, "
        "because it is the only one that is not a machine or a person."),
}

for stem in ("RR_GateCharge_%02d" % n for n in range(1, 9)):
    USAGE[stem] = CHARGE
for stem in ("RR_GateActivation_%02d" % n for n in range(1, 7)):
    USAGE[stem] = ACTIVATION
for stem in ("RR_GateOpen_%02d" % n for n in range(1, 9)):
    USAGE[stem] = OPEN
for stem in ("RR_Menu_BreachedVault", "RR_Menu_CorridorEncounter", "RR_Menu_EmptyCinema",
             "RR_Menu_FacilityThreshold_v2", "RR_Menu_FamiliarStranger", "RR_Menu_FieldSurvey_v2",
             "RR_Menu_IndustrialGateLogistics", "RR_Menu_LaboratoryOperations",
             "RR_Menu_LightsOut", "RR_Menu_PanicJunction", "RR_Menu_RedTrail",
             "RR_Menu_SilentRecovery"):
    USAGE[stem] = SLIDE

data = json.load(io.open(TARGET, encoding="utf-8"))
known = set(data["assets"])
missing = sorted(known - set(USAGE))
extra = sorted(set(USAGE) - known)
if missing or extra:
    print("REFUSED, because a partial map would publish blanks:")
    for stem in missing:
        print("  no usage line for a shipped asset: %s" % stem)
    for stem in extra:
        print("  usage line for something not shipped: %s" % stem)
    raise SystemExit(1)

data["usageNote"] = (
    "What a player DOES with each asset, as opposed to what the drawing depicts. Owner, 2026-10-06: "
    "\"im not seeing the pictures of the assets in the wiki with theri right up details and how the "
    "are used in game play\". Taken from the shipped defs, the source, or the wiki page that already "
    "describes that system -- never invented, because a reader checks this page precisely because "
    "they cannot see inside the package. An asset with no entry here is reported, never left blank.")
data["usage"] = dict((stem, USAGE[stem]) for stem in sorted(USAGE))

io.open(TARGET, "w", encoding="utf-8", newline="\n").write(
    json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False) + "\n")
print("wrote %d description(s) and %d usage line(s) to %s"
      % (len(data["assets"]), len(data["usage"]), os.path.relpath(TARGET, REPO)))
