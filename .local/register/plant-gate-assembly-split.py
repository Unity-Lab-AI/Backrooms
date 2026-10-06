# -*- coding: utf-8 -*-
"""Planted faults against `.local/register/proof-gate-assembly-split.py`.

**The two faults this split could ship are both silent, and one is arithmetic.** Four sections of
30 steel is a twenty per cent tax nobody decided on and nothing in a build would say so; a section
allocated to a bench is work stranded the moment somebody deconstructs that bench. Neither throws,
neither logs, and both read as correct in every file a reader would open.

So the plants aim at those first, and then at the loud one that is easy to reintroduce: the recipe
worker suspending the bill after the first section, which was correct for the whole life of the
single-bill assembly.

**NEVER RUN A PLANT SUITE CONCURRENTLY WITH ANYTHING ELSE.**

Run from the repository root.
"""
import io
import os
import subprocess
import sys
import time

RECIPES = "Mod/Rimrooms - Async Industries/1.6/Defs/RecipeDefs/RR_GateRecipes.xml"
EQUIPMENT = "Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsGateEquipmentDefs/RR_GateEquipment.xml"
STEPS = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_GateSteps.xml"
GATE_KEYED = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Gate.xml"
SHARES = "src/RimroomsAsyncIndustries/Gate/GateAssemblyShares.cs"
GATE = "src/RimroomsAsyncIndustries/Gate/CompRimroomsGate.cs"
CONSOLE = "src/RimroomsAsyncIndustries/Gate/CompRimroomsGateConsole.cs"
WIKI = "docs/wiki/first-hour.md"

PROOF = ".local/register/proof-gate-assembly-split.py"

NL = chr(10)

PLANTS = [
    # ================================================= 1. the arithmetic, silently
    ("THE SPLIT QUIETLY TAXES THE PLAYER: 30 steel a section is 120 for the gate", RECIPES,
     "<count>25</count>", "<count>30</count>", PROOF),

    ("the component cost drifts, so four sections cost twelve components", RECIPES,
     "<count>2</count>", "<count>3</count>", PROOF),

    ("the work per section drifts, so the gate takes a third longer to build", RECIPES,
     "<workAmount>1500</workAmount>", "<workAmount>2000</workAmount>", PROOF),

    ("the section count changes without the cost, so the price moves with it", SHARES,
     "AssemblySharesRequired = 4", "AssemblySharesRequired = 5", PROOF),

    # ================================================= 2. one recipe, one cost
    ("the bill still reads as the whole gate while building a quarter of one", RECIPES,
     "<label>assemble gate section</label>", "<label>assemble gate</label>", PROOF),

    # ================================================= 3. the role
    # **THIS PLANT WAS WRONG BEFORE THE RULE WAS.** Its first version inserted an XML COMMENT into
    # the role, and the proof strips comments before reading - correctly, because a rule about data
    # must read data. The plant edited prose and the instrument rightly saw nothing change. It now
    # swaps the thing the role links, which is the fault it always meant to describe.
    ("the role links comms consoles, which can never build anything", EQUIPMENT,
     # **Anchored on the role's own defName, not on its display order.** The first version pinned
     # `<displayOrder>2</displayOrder>`, which moved to 13 when the order was found colliding with
     # RR_Link_Tooling -- so the anchor broke and the suite would have died with PLANT SETUP
     # BROKEN. A plant must be aimed at what identifies the thing, not at a number beside it.
     "    <defName>RR_Link_GateAssembly</defName>" + NL
     + "    <label>assembly bench</label>",
     "    <defName>RR_Link_GateAssembly</defName>" + NL
     + "    <label>assembly bench</label>" + NL
     + "    <thingDefNames><li>CommsConsole</li></thingDefNames>", PROOF),

    ("THE ROLE BECOMES A DECLARED LINK NOTHING READS, which changes nothing", SHARES,
     '"RR_Link_GateAssembly"', '"RR_Link_GateAssemblyUnused"', PROOF),

    ("an unpowered machining table counts as a bench", SHARES,
     "if (!IsEquipmentLinkActive(linked)) { continue; }", "if (false) { continue; }", PROOF),

    ("maxLinked opens past the owner's four", EQUIPMENT,
     "    <maxLinked>3</maxLinked>" + NL
     + "    <!-- 13. The first draft said 2, which collided with RR_Link_Tooling. -->",
     "    <maxLinked>8</maxLinked>" + NL
     + "    <!-- 13. The first draft said 2, which collided with RR_Link_Tooling. -->", PROOF),

    # ================================================= 4. the named cost
    ("A SECTION GETS ALLOCATED TO A BENCH, which is the remainder nowhere can finish", SHARES,
     "        private int assemblyShares;",
     "        private Dictionary<Thing, int> assemblySharesByBench;", PROOF),

    ("the credit goes back to identity with the one designated bench", GATE,
     "!IsBoundAssemblyBench(billGiver)", "billGiver != nativeAssemblyBench", PROOF),

    # ================================================= 5. one question, both sides
    ("a bench is offered a section the gate would refuse to credit", CONSOLE,
     "                && gate.IsBoundAssemblyBench(thing);", ";", PROOF),

    ("GATE CONTROL BECOMES UNREACHABLE ON A LINKED BENCH, so the role does nothing", CONSOLE,
     "public bool IsGateControl { get { return gateControl && Gate != null; } }",
     "public bool IsGateControl { get { return gateControl && linkedGate != null; } }", PROOF),

    # ================================================= 6. the bill survives a section
    ("THE BILL SUSPENDS AFTER THE FIRST SECTION, stopping the build with no explanation",
     CONSOLE, "            gate.CompleteAssemblyFromBill(billGiver, billDoer.CurJob.bill.recipe);",
     "            if (gate.CompleteAssemblyFromBill(billGiver, billDoer.CurJob.bill.recipe)"
     + ".Success)" + NL + "            { console.MarkAssemblyBillComplete(); }", PROOF),

    ("the gate is marked complete on the first section", GATE,
     "            if (assemblyShares < AssemblySharesRequired)" + NL
     + "            {" + NL,
     "            if (false)" + NL
     + "            {" + NL, PROOF),

    ("only the finishing bench's bill is suspended, so three keep spending steel", GATE,
     "            foreach (Thing bench in BoundAssemblyBenches)", "            foreach (Thing bench in new Thing[0])",
     PROOF),

    # ================================================= 7. older saves
    ("A GATE BUILT BEFORE THE SPLIT READS AS NOUGHT OF FOUR", SHARES,
     "                if (assemblyComplete) { assemblyShares = AssemblySharesRequired; }", "",
     PROOF),

    ("the loaded count stops being clamped", SHARES,
     "                if (assemblyShares > AssemblySharesRequired) { assemblyShares = AssemblySharesRequired; }",
     "", PROOF),

    # ================================================= 8. what the player is told
    ("the step pane still promises one bill of a hundred steel", STEPS,
     "four sections of 25 steel and 2 industrial components",
     "100 steel and 8 industrial components", PROOF),

    ("the readout loses its keyed string and renders a raw key on the gate", GATE_KEYED,
     "<RR_Gate_AssemblySections>", "<RR_Gate_AssemblySectionsUnused>", PROOF),

    ("the readout is computed and never shown", GATE,
     "            string assemblyText = AssemblyReadout();",
     "            string assemblyText = null;", PROOF),

    ("THE WIKI STOPS SAYING THE TOTAL, so a reader cannot tell the price held", WIKI,
     "100 steel + 8 industrial components  for all four",
     "the same as it always was                 for all four", PROOF),
]

for _plant in PLANTS:
    if len(_plant) != 5:
        sys.stderr.write("PLANT LIST MALFORMED: %r has %d field(s), not 5\n"
                         % (_plant[0], len(_plant)))
        sys.exit(2)

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
    for _ in range(6):
        try:
            with io.open(path, "w", encoding="utf-8", newline="") as handle:
                handle.write(text)
            if io.open(path, encoding="utf-8").read() == text:
                return
        except OSError:
            pass
        time.sleep(0.4)
    sys.stderr.write("FATAL: could not write %s -- CHECK BY HAND\n" % path)
    sys.exit(3)


print("baseline -- the verifier must pass before anything is planted")
for command in sorted(set(plant[4] for plant in PLANTS)):
    code = subprocess.call([sys.executable, command],
                           stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print("  exit %d  %s" % (code, command))
    if code != 0:
        sys.stderr.write("BASELINE BROKEN: %s already fails, so every plant against it would "
                         "register as caught and the run would prove nothing.\n" % command)
        sys.exit(2)
print("")

opening = dict((path, io.open(path, encoding="utf-8").read())
               for path in set(plant[1] for plant in PLANTS))

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
for path, text in opening.items():
    if io.open(path, encoding="utf-8").read() != text:
        sys.stderr.write("%s IS NOT AS IT WAS FOUND -- CHECK BY HAND\n" % path)
        sys.exit(3)
if os.path.isfile(_RR_SENTINEL):
    sys.stderr.write("SENTINEL STILL PRESENT AT %s\n" % _RR_SENTINEL)
    sys.exit(3)
print("every touched file verified byte-identical to how it was found; no sentinel left behind")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
