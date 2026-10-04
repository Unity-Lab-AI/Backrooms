# -*- coding: utf-8 -*-
"""Planted faults against `proof-standalone-and-grants.py`.

## The ones that matter most

**A diagnostic that causes the defect it looks for.** The starting-goods report reads the promise
through `GetSummaryListEntries`, which creates nothing. Swap it for `PlayerStartingThings()` and
the report manufactures a second set of goods on every start -- the exact double-grant the arrival
receipt exists to prevent. It would look like a more direct reading of the same data.

**A report that blocks a start.** Setting `receipt.failure` from the shortfall turns a branch that
is merely short of supplies into one that will not initialise. One line, and the cure is worse
than the disease.

**An expansion role becoming load-bearing.** Give one a stock target and the branch is told it is
short of something only an expansion can supply.

**The guarantee checker passing on a machine with no game installed.** That is the
absence-claim-against-an-empty-file defect, which once reported eight green claims against nothing.

Run from the repository root.
"""
import io
import os
import subprocess
import sys
import time

SRC = "src/RimroomsAsyncIndustries"
ROLES = ("Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsGateEquipmentDefs/"
         "RR_GateEquipment.xml")
LINKS = SRC + "/Gate/GateEquipmentLinks.cs"
ARRIVAL = SRC + "/Scenario/ScenPart_RimroomsArrival.cs"
START = SRC + "/Scenario/ScenPart_RimroomsStart.cs"
RECEIPT = SRC + "/Scenario/HeadquartersSetupComponent.cs"
GUARANTEE = "tools/check-standalone-guarantee.py"
GATING = "tools/check-dlc-gating.py"
PROOF = ".local/register/proof-standalone-and-grants.py"
NL = chr(10)

PLANTS = [
    # ================================================= expansions only add content
    ("AN EXPANSION ROLE DISAPPEARS", ROLES,
     "    <defName>RR_Link_Containment</defName>",
     "    <defName>RR_Link_ContainmentGone</defName>", PROOF),

    ("A ROLE'S ACCEPTED DEFS BECOME DEF REFERENCES instead of strings", LINKS,
     "        public List<string> thingDefNames = new List<string>();",
     "        public List<ThingDef> thingDefNames = new List<ThingDef>();", PROOF),

    ("the name resolution stops degrading", LINKS,
     "                    if (DefDatabase<ThingDef>.GetNamedSilentFail(thingDefNames[index]) != null)",
     "                    if (DefDatabase<ThingDef>.GetNamed(thingDefNames[index]) != null)",
     PROOF),

    ("A ROLE NOTHING CAN FILL IS OFFERED AGAIN", LINKS,
     "                .Where(definition => definition.Fillable)" + NL, "", PROOF),

    ("AN EXPANSION ENTRY LOSES ITS GATE", ROLES,
     '      <li MayRequire="Ludeon.RimWorld.Anomaly">HoldingPlatform</li>',
     "      <li>HoldingPlatform</li>", PROOF),

    # **PER ENTRY, NOT PER ROLE.** Gating the whole role deletes one that also takes Core things.
    ("THE WHOLE ROLE IS GATED instead of the entries", ROLES,
     "  <RimroomsAsyncIndustries.Gate.RimroomsGateEquipmentDef>" + NL
     + "    <defName>RR_Link_Containment</defName>",
     '  <RimroomsAsyncIndustries.Gate.RimroomsGateEquipmentDef'
     + ' MayRequire="Ludeon.RimWorld.Anomaly">' + NL
     + "    <defName>RR_Link_Containment</defName>", PROOF),

    ("the gating checker goes back to reading MayRequire off the def alone", GATING,
     "            for node, required in nodes_with_requirements(definition):",
     "            required = set()" + NL + "            for node in definition.iter():", PROOF),

    ("AN EXPANSION ROLE BECOMES LOAD-BEARING, so the branch is told it is short", ROLES,
     "    <maxLinked>6</maxLinked>" + NL + "    <displayOrder>8</displayOrder>",
     "    <maxLinked>6</maxLinked>" + NL + "    <displayOrder>8</displayOrder>" + NL
     + "    <stockCategoryDefName>Medicine</stockCategoryDefName>" + NL
     + "    <stockTarget>5</stockTarget>", PROOF),

    # ================================================= the stand-alone guarantee checker
    # **RE-AIMED. The first version rewrote the refusal's MESSAGE**, which does not stop the
    # checker refusing anything -- it still appends a problem and still fails the build, so the
    # claim was right to pass and the plant was testing nothing. A message is not a rule in this
    # direction too. Aimed at the condition that decides, which is what actually has to hold.
    ("THE GUARANTEE CHECKER STOPS REFUSING A FOREIGN DEF", GUARANTEE,
     "                    if not owners:",
     "                    if False:", PROOF),

    ("its reference fields go back to a hand-kept list", GUARANTEE,
     "def reference_fields():", "def unused_reference_fields():", PROOF),

    ("A HARD GetNamed ON EXPANSION CONTENT STOPS BEING REFUSED", GUARANTEE,
     '                    "%s: looks up expansion def %r (%s) with GetNamed, which throws when the "',
     '                    "%s: looks up expansion def %r (%s) which is fine "', PROOF),

    ("a third-party assembly reference stops being refused", GUARANTEE,
     "ALLOWED_ASSEMBLIES = ", "UNUSED_ALLOWED = ", PROOF),

    # **THE EMPTY-HAYSTACK DEFECT.** A checker that passes with no game installed proves nothing.
    ("THE GUARANTEE CHECKER PASSES WITH NO GAME INSTALLED", GUARANTEE,
     "    if len(core) < 1000:", "    if False:", PROOF),

    # ================================================= the starting-goods diagnostic
    ("THE PROMISE STOPS BEING RECORDED", RECEIPT,
     "        public List<string> promisedGrants = new List<string>();",
     "        private List<string> unusedPromised = new List<string>();", PROOF),

    ("the promise stops being saved", RECEIPT,
     '            Scribe_Collections.Look(ref promisedGrants, "rr_promisedGrants", LookMode.Value);'
     + NL, "", PROOF),

    # **THE DIAGNOSTIC CAUSING THE DEFECT.** This is the one that would look like an improvement.
    ("THE DIAGNOSTIC STARTS MANUFACTURING A SECOND SET OF GOODS", ARRIVAL,
     '                try { entries = part.GetSummaryListEntries("PlayerStartsWith"); }',
     "                try { entries = part.PlayerStartingThings()"
     + ".Select(t => t.LabelCap.ToString()); }", PROOF),

    ("the promise stops being recorded on the fallback path", ARRIVAL,
     "                    RecordPromisedGrants(receipt);" + NL
     + "                }" + NL
     + "                try { base.GenerateIntoMap(map); }",
     "                }" + NL
     + "                try { base.GenerateIntoMap(map); }", PROOF),

    ("a part that will not summarise itself fails the whole start", ARRIVAL,
     "                catch (Exception exception)" + NL
     + "                {" + NL
     + "                    // A part from another mod may refuse to summarise itself. That is one missing",
     "                catch (Exception exception)" + NL
     + "                {" + NL
     + "                    throw;" + NL
     + "                    // A part from another mod may refuse to summarise itself. That is one missing",
     PROOF),

    ("THE REPORT STARTS BLOCKING THE START", START,
     "            Log.Error(\"[Rimrooms][Scenario] The scenario promised starting goods and none \"",
     "            receipt.failure = \"RR_Setup_ArrivalIncomplete\";" + NL
     + "            Log.Error(\"[Rimrooms][Scenario] The scenario promised starting goods and none \"",
     PROOF),

    ("the report starts crying wolf on a working start", START,
     "            if (receipt.deliveredGrants != null && receipt.deliveredGrants.Count > 0) { return; }"
     + NL, "", PROOF),

    ("and it fires on a save that recorded no promise at all", START,
     "            if (receipt.promisedGrants == null || receipt.promisedGrants.Count == 0) { return; }"
     + NL, "", PROOF),

    ("THE REPORT MOVES BELOW THE BRANCH INITIALISATION, where success buries it", START,
     "            ReportGrantShortfall(Verse.Current.Game.CurrentMap);" + NL
     + "            CompanyActionResult result = TryInitializeExistingHeadquarters("
     + "Verse.Current.Game.CurrentMap);",
     "            CompanyActionResult result = TryInitializeExistingHeadquarters("
     + "Verse.Current.Game.CurrentMap);" + NL
     + "            ReportGrantShortfall(Verse.Current.Game.CurrentMap);", PROOF),

    ("the eliminated causes stop being recorded, so the next reader repeats the work", RECEIPT,
     "        /// * *the gen steps run out of order* — they do not. Core's `ScenParts` is order **875**,"
     + NL + "        ///   after both.", "", PROOF),
]

_RR_SENTINEL = os.path.join(".local", "register",
                            ".plant-in-progress-"
                            + os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0])


def _rr_mark(path, label):
    io.open(_RR_SENTINEL, "w", encoding="utf-8", newline="").write(
        u"planted %r into %s" % (label, path))


def _rr_unmark():
    try:
        os.remove(_RR_SENTINEL)
    except OSError:
        pass


def write_verified(path, text):
    """Write, and do not believe it until it reads back identical. Retried both ways."""
    last = None
    for attempt in range(6):
        try:
            io.open(path, "w", encoding="utf-8", newline="").write(text)
            if io.open(path, encoding="utf-8").read() == text:
                return
            last = "the file read back different from what was written"
        except (OSError, IOError) as error:
            last = repr(error)
        time.sleep(0.4 * (attempt + 1))
    sys.stderr.write("FATAL: could not write %s (%s) -- sentinel left in place on purpose\n"
                     % (path, last))
    sys.exit(3)


ORIGINALS = {path: io.open(path, encoding="utf-8").read()
             for path in sorted({plant[1] for plant in PLANTS})}

print("baseline -- the target must pass before anything is planted")
for command in sorted({plant[4] for plant in PLANTS}):
    code = subprocess.call([sys.executable, command],
                           stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print("  exit %d  %s" % (code, command))
    if code != 0:
        sys.stderr.write("BASELINE BROKEN: %s already fails, so every plant against it would "
                         "register as caught and the run would prove nothing.\n" % command)
        sys.exit(2)
print("")

caught = 0
for label, path, old, new, command in PLANTS:
    original = io.open(path, encoding="utf-8").read()
    if original.count(old) < 1:
        print("PLANT SETUP BROKEN (0 matches): %s" % label)
        sys.exit(2)
    _rr_mark(path, label)
    write_verified(path, original.replace(old, new, 1))
    try:
        code = subprocess.call([sys.executable, command],
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        write_verified(path, original)
        _rr_unmark()
    ok = code != 0
    caught += 1 if ok else 0
    print("%s  %s" % ("CAUGHT " if ok else "MISSED!", label))

print("")
for path, text in ORIGINALS.items():
    if io.open(path, encoding="utf-8").read() != text:
        sys.stderr.write("%s IS NOT AS IT WAS FOUND -- CHECK BY HAND\n" % path)
        sys.exit(3)
if os.path.isfile(_RR_SENTINEL):
    sys.stderr.write("SENTINEL STILL PRESENT AT %s\n" % _RR_SENTINEL)
    sys.exit(3)
print("every target verified byte-identical to how it was found; no sentinel left behind")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
