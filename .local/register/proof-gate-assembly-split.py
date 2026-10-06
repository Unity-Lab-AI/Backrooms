# -*- coding: utf-8 -*-
"""Assert the gate's assembly is four sections that cost exactly what one bill cost, that any
bound bench may build any section, and that losing a bench cannot orphan work.

The property this exists for
---------------------------
**Owner, 2026-10-06:** *"with say upto 4 of them available so pawns can do geate process better and
faster"*, and *"and same with the coms and machine benches"*. Asked how to make a second bench mean
anything, they chose **split the gate's component count across the linked benches** over *any
linked bench satisfies the bill*.

Three things can go wrong here and two of them are silent:

1. **The split quietly changes the price.** Four sections of 30 steel is a 20% tax nobody decided
   on, and nothing in a build would say so. So the arithmetic is asserted: section cost times
   section count must equal the figures the gate has always cost, and the documents that state
   those figures must state these.
2. **A section gets allocated to a bench.** That is the cost the fork named *before* the owner
   chose the split: a destroyed or unlinked bench leaves *"an unfinishable remainder"*. The answer
   is that an allocation does not exist -- the count lives on the gate -- so this proof asserts the
   absence of per-bench state rather than the correctness of a redistribution.
3. **Availability and credit disagree.** A bench offered a section it is then refused credit for is
   a pawn carrying twenty-five steel across the base for nothing. One question decides both, and
   that is asserted by reading both call sites.

And one that is loud but easy to ship: **the bill suspending itself after the first section**. The
recipe worker used to call `MarkAssemblyBillComplete` on any success, which was right while the
assembly was one bill and stops a four-section build dead.

Run from the repository root.
"""
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")
RECIPES = os.path.join(MOD, "Defs", "RecipeDefs", "RR_GateRecipes.xml")
EQUIPMENT = os.path.join(MOD, "Defs", "RimroomsGateEquipmentDefs", "RR_GateEquipment.xml")
STEPS_KEYED = os.path.join(MOD, "Languages", "English", "Keyed", "RR_GateSteps.xml")
GATE_KEYED = os.path.join(MOD, "Languages", "English", "Keyed", "RR_Gate.xml")
WIKI = os.path.join(REPO, "docs", "wiki", "first-hour.md")

# What one bill cost before the split, and what four sections must still cost together. These are
# the historical figures, written down so the arithmetic has something to be checked against rather
# than being checked against itself.
TOTAL_STEEL = 100
TOTAL_COMPONENTS = 8
TOTAL_WORK = 6000

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def strip_cs_comments(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return "\n".join(re.sub(r"//.*$", "", line) for line in text.split("\n"))


def strip_xml_comments(text):
    return re.sub(r"<!--.*?-->", " ", text, flags=re.S)


def body_of(text, signature):
    at = text.find(signature)
    if at < 0:
        return None
    end = text.find("\n        }", at)
    return text[at:end] if end > at else text[at:]


def ordered(text, first, second):
    """True when BOTH appear and `first` comes before `second`.

    **A PLANT CAUGHT THIS AS A BARE `find() < find()` COMPARISON AND IT WAS A REAL HOLE.** Python's
    `str.find` returns **-1** for absent, and -1 is less than every real index -- so deleting the
    first string entirely made every ordering claim in this file pass. The plant that marked the
    gate complete on its first section did exactly that and was MISSED.

    So an ordering claim now fails on absence as well as on inversion, which is what it always meant
    to say. This is the fourth time in this repository that a rule has been satisfied by the thing
    it was watching for simply not being there.
    """
    if text is None:
        return False
    at = text.find(first)
    then = text.find(second)
    return at >= 0 and then >= 0 and at < then


source = {}
for root, _, files in os.walk(SRC):
    if os.sep + "obj" + os.sep in root or os.sep + "bin" + os.sep in root:
        continue
    for name in files:
        if name.endswith(".cs"):
            source[os.path.join(root, name)] = strip_cs_comments(read(os.path.join(root, name)))
all_source = "\n".join(source.values())

shares = source.get(os.path.join(SRC, "Gate", "GateAssemblyShares.cs"), "")
gate = source.get(os.path.join(SRC, "Gate", "CompRimroomsGate.cs"), "")
console = source.get(os.path.join(SRC, "Gate", "CompRimroomsGateConsole.cs"), "")
recipes = strip_xml_comments(read(RECIPES))
equipment = strip_xml_comments(read(EQUIPMENT))

print("")
print("proof: four sections at the same price, any bench, and no remainder nowhere can finish")
print("")

# ------------------------------------------------------------------ 1. the arithmetic
print("1. the split did not change the price")
required = re.search(r"AssemblySharesRequired = (\d+);", shares)
steel = re.search(r"<li>Steel</li></thingDefs></filter>\s*<count>(\d+)</count>", recipes)
components = re.search(r"<li>ComponentIndustrial</li></thingDefs></filter>\s*<count>(\d+)</count>",
                       recipes)
work = re.search(r"<workAmount>(\d+)</workAmount>", recipes)
check("the gate declares how many sections it takes", required is not None)
check("the section recipe declares its steel, components and work",
      steel is not None and components is not None and work is not None)
if None not in (required, steel, components, work):
    count = int(required.group(1))
    check("four sections, matching the owner's four benches", count == 4,
          "-- found %d" % count)
    check("SECTIONS TIMES COST EQUALS WHAT ONE BILL COST: %d steel" % TOTAL_STEEL,
          int(steel.group(1)) * count == TOTAL_STEEL,
          "-- %d x %d is not %d. A split that changes the price is a tax nobody decided on"
          % (int(steel.group(1)), count, TOTAL_STEEL))
    check("sections times components equals %d" % TOTAL_COMPONENTS,
          int(components.group(1)) * count == TOTAL_COMPONENTS,
          "-- %d x %d is not %d" % (int(components.group(1)), count, TOTAL_COMPONENTS))
    check("sections times work equals %d" % TOTAL_WORK,
          int(work.group(1)) * count == TOTAL_WORK,
          "-- %d x %d is not %d" % (int(work.group(1)), count, TOTAL_WORK))

# ------------------------------------------------------------------ 2. one recipe, one cost
print("")
print("2. one recipe states the section cost, so there is nothing to disagree with")
check("exactly one recipe uses the gate assembly worker",
      recipes.count("RimroomsAsyncIndustries.Gate.RecipeWorker_RimroomsGateAssembly") == 1,
      "-- four recipe defs would be four places stating the cost")
check("exactly one recipe def named RR_AssembleMachineGate exists",
      recipes.count("<defName>RR_AssembleMachineGate</defName>") == 1)
check("the recipe reads as a section rather than as the gate",
      "<label>assemble gate section</label>" in recipes,
      "-- a bill labelled 'assemble gate' that builds a quarter of one is a lie on the bill")

# ------------------------------------------------------------------ 3. the role
print("")
print("3. the role that makes a second bench mean something")
role = re.search(r"<defName>RR_Link_GateAssembly</defName>(.*?)</RimroomsAsyncIndustries"
                 r"\.Gate\.RimroomsGateEquipmentDef>", equipment, re.S)
check("RR_Link_GateAssembly is declared", role is not None)
if role is not None:
    check("it links machining tables and nothing else",
          "<li>TableMachining</li>" in role.group(1)
          and role.group(1).count("<li>") == 1)
    check("maxLinked is three, so the designated bench plus three links is the owner's four",
          "<maxLinked>3</maxLinked>" in role.group(1),
          "-- found something else; four is the owner's number and the provider is the first")
check("the role is read by the gate",
      '"RR_Link_GateAssembly"' in shares,
      "-- a declared role nothing reads is a link that changes nothing")
check("an inactive bench is not a bench",
      "IsEquipmentLinkActive(linked)" in shares,
      "-- an unpowered machining table cannot build a section, which is the answer Core gives "
      "for an unpowered multi-analyzer")
benches = body_of(shares, "public IEnumerable<Thing> BoundAssemblyBenches")
check("the designated bench is yielded first",
      ordered(benches, "AssemblyBench", "LinkedEquipment"),
      "-- the bound bench is the one every other subsystem already names")

# ------------------------------------------------------------------ 4. no allocation to orphan
print("")
print("4. THE NAMED COST: a section is never allocated to a bench, so none can be orphaned")
check("the section count is a single integer on the gate",
      re.search(r"private int assemblyShares;", shares) is not None,
      "-- per-bench state is the thing that strands work when a bench dies")
check("NOTHING KEYS SECTION STATE BY BENCH ANYWHERE",
      not re.search(r"(Dictionary|List)<[^>]*>\s+\w*[Ss]hare", all_source)
      and not re.search(r"\w*[Ss]haresBy\w*", all_source),
      "-- the fork named this cost before the owner chose the split: a destroyed or unlinked "
      "bench must not leave an unfinishable remainder")
check("any bound bench may be credited",
      "public bool IsBoundAssemblyBench(Thing bench)" in shares
      and "billGiver != nativeAssemblyBench" not in gate,
      "-- the old test was identity with the ONE designated bench")

# ------------------------------------------------------------------ 5. one question, both sides
print("")
print("5. availability and credit ask the same question")
available = body_of(console, "public override bool AvailableOnNow(")
complete = body_of(gate, "public CompanyActionResult CompleteAssemblyFromBill(")
check("the recipe is offered only at a bench the gate would credit",
      available is not None and "IsBoundAssemblyBench(thing)" in available,
      "-- offering a section at a bench that is then refused credit is a pawn carrying twenty-five "
      "steel across the base for nothing")
check("the credit asks the same method",
      complete is not None and "IsBoundAssemblyBench(billGiver)" in complete)
check("the gate control switch is reachable on a linked bench",
      "public bool IsGateControl { get { return gateControl && Gate != null; } }" in console,
      "-- a linked bench with no primary binding could never enter gate control, and the role "
      "would be a link that changes nothing")
resolve = body_of(console, "public CompRimroomsGate Gate")
check("the primary binding is asked first and always wins",
      ordered(resolve, "linkedGate", "LinkedAssemblyGate()"),
      "-- the designated bench must behave exactly as it did")

# ------------------------------------------------------------------ 6. the bill survives a section
print("")
print("6. a finished section does not stop the build")
check("THE RECIPE WORKER NO LONGER SUSPENDS THE BILL PER SECTION",
      "MarkAssemblyBillComplete" not in (body_of(console, "public override void "
                                                 "Notify_IterationCompleted(") or ""),
      "-- correct while the assembly was one bill; it would stop a four-section build after the "
      "first with the bill suspended and nothing saying why")
check("every bound bench's bill is suspended when the LAST section lands",
      complete is not None
      and "foreach (Thing bench in BoundAssemblyBenches)" in complete
      and "MarkAssemblyBillComplete()" in complete,
      "-- a repeating bill left running on another bench would spend another twenty-five steel "
      "on a gate that is already assembled")
check("a partial section returns before the gate is marked complete",
      ordered(complete, "if (assemblyShares < AssemblySharesRequired)", "assemblyComplete = true;"),
      "-- marking the gate complete on the first section is the whole fault this split could ship")

# ------------------------------------------------------------------ 7. saves written before it
print("")
print("7. a save written before the split")
expose = body_of(shares, "internal void ExposeAssemblyShares()")
check("a finished gate from an older save reads as every section installed",
      expose is not None and "if (assemblyComplete) { assemblyShares = AssemblySharesRequired; }"
      in expose,
      "-- otherwise a built gate reads as nought of four and the readout contradicts the status")
check("the count is clamped on load at both ends",
      expose is not None and "assemblyShares < 0" in expose
      and "assemblyShares > AssemblySharesRequired" in expose)

# ------------------------------------------------------------------ 8. what the player is told
print("")
print("8. the player is told the section cost, in every place that states a cost")
steps = read(STEPS_KEYED)
check("gate step 5 names the section cost rather than the old single bill",
      "four sections of 25 steel and 2 industrial components" in steps
      and "assemble gate section" in steps,
      "-- the step pane promising one bill of 100 steel is the pane lying about the build")
check("the readout strings exist",
      "<RR_Gate_AssemblySections>" in read(GATE_KEYED)
      and "<RR_Gate_AssemblyBenches>" in read(GATE_KEYED))
check("the readout is actually printed",
      '"RR_Gate_AssemblySections"' in shares and "AssemblyReadout()" in gate,
      "-- a keyed string nothing shows is a string that does not exist")
check("THE WIKI STATES BOTH THE SECTION COST AND THE TOTAL",
      "25 steel + 2 industrial components" in read(WIKI)
      and "100 steel + 8 industrial components" in read(WIKI),
      "-- a reader needs to know the price did not change, and the total is the number they "
      "remember from before")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: four sections, the same price, any bound bench, and no work left nowhere")
