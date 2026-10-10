# -*- coding: utf-8 -*-
"""Fourteen plants for the bonds, against proof-bonds.py. Added to plant-rest.py."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUITE = os.path.join(REPO, ".local", "register", "plant-rest.py")

T_ANCHOR = u'PANE = SRC + "/UI/OperationsFacilities.cs"'
T_NEW = (u'PANE = SRC + "/UI/OperationsFacilities.cs"\n'
         u'PAPER = SRC + "/Economy/BondPaper.cs"\n'
         u'BONDCOMP = SRC + "/Economy/CompRimroomsBond.cs"\n'
         u'BONDSVC = SRC + "/Economy/BondService.cs"\n'
         u'HANDLING = SRC + "/Economy/BondHandling.cs"\n'
         u'TREASURY = SRC + "/Company/BondTreasury.cs"\n'
         u'BONDTEXT = ("Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/'
         u'RR_Bonds.xml")\n'
         u'BONDS_PROOF = ".local/register/proof-bonds.py"')

P_ANCHOR = u"PLANTS = ["
P_NEW = u'''PLANTS = [
    # ------------------------------------------------------------------ the bonds
    # Nothing in this battery had ever claimed anything about bonds, which is why five defects
    # shipped in one feature. Four of the five were the same shape: built, correct, unreachable.
    ("THE CARRIER'S CLASS IS NEVER SWAPPED, SO THE LABEL GOES BACK TO A NOVEL TITLE", BONDSVC,
     "                { bond.thingClass = typeof(Book_RimroomsBond); }",
     "                { }", BONDS_PROOF),

    ("the label override stops reading the face value", PAPER,
     '                return "RR_Bond_Label".Translate(CreditDenominations.ShortName(bond.FaceValue));',
     "                return base.LabelNoCount;", BONDS_PROOF),

    ("an ordinary novel loses its own name too", PAPER,
     "                if (bond == null) { return base.LabelNoCount; }",
     "                if (bond == null) { return null; }", BONDS_PROOF),

    ("THE DEAD COMP HOOK COMES BACK, READING LIKE A FIX", BONDCOMP,
     "        public override string CompInspectStringExtra()",
     "        public override string TransformLabel(string label)" + chr(10)
     + "        {" + chr(10)
     + '            return "RR_Bond_Label".Translate(faceValue);' + chr(10)
     + "        }" + chr(10) + chr(10)
     + "        public override string CompInspectStringExtra()", BONDS_PROOF),

    ("the label stops being the value and goes back to a bare word", BONDTEXT,
     "  <RR_Bond_Label>{0} credit bearer bond</RR_Bond_Label>",
     "  <RR_Bond_Label>company bond</RR_Bond_Label>", BONDS_PROOF),

    ("A BOND GOES BACK TO BEING WORTH A NOVEL", PAPER,
     "            if (face > 0L) { value = face; }", "            return;", BONDS_PROOF),

    ("the stat part is written and never added to the stat", BONDSVC,
     "                        market.parts.Add(valuePart);", "                        _ = valuePart;",
     BONDS_PROOF),

    ("the value part stops asking for a thing, so it answers for defs too", PAPER,
     "            if (!request.HasThing) { return 0L; }", "            if (false) { return 0L; }",
     BONDS_PROOF),

    ("DEPOSIT IS DEFINED AND NEVER OFFERED", BONDCOMP,
     "                action = delegate { Show(BondHandling.Deposit(parent)); }",
     "                action = delegate { }", BONDS_PROOF),

    ("combine is defined and never offered", BONDCOMP,
     "                action = delegate { Show(BondHandling.Combine(parent)); }",
     "                action = delegate { }", BONDS_PROOF),

    ("the treasury loses the deposit it is asked for", TREASURY,
     "        internal CompanyActionResult DepositBondPaper(",
     "        internal CompanyActionResult DepositBondPaperUnused(", BONDS_PROOF),

    ("COMBINING STOPS BALANCING THE LEDGER", TREASURY,
     '            CompanyActionResult paid = PostTransaction(operationId + ".out", -payable,',
     '            CompanyActionResult paid = PostTransaction(operationId + ".out", 0L,',
     BONDS_PROOF),

    ("combining shreds a pile it cannot improve", HANDLING,
     "            if (wanted >= paper.Count && remainder <= 0L)",
     "            if (false)", BONDS_PROOF),

    ("a refusal goes silent", BONDCOMP,
     '            Messages.Message((result.MessageKey ?? "RR_Bond_NoneInRange").Translate(),',
     "            if (false) Messages.Message((result.MessageKey ?? \\"RR_Bond_NoneInRange\\").Translate(),",
     BONDS_PROOF),

    ("the description stops describing the instrument", BONDTEXT,
     "COMPANY BEARER BOND", "A company bearer bond", BONDS_PROOF),
'''

suite = io.open(SUITE, encoding="utf-8").read()
if suite.count(T_ANCHOR) != 1:
    print("TARGET ANCHOR PROBLEM: %d" % suite.count(T_ANCHOR))
    raise SystemExit(1)
suite = suite.replace(T_ANCHOR, T_NEW, 1)
if suite.count(P_ANCHOR) != 1:
    print("PLANT ANCHOR PROBLEM: %d" % suite.count(P_ANCHOR))
    raise SystemExit(1)
suite = suite.replace(P_ANCHOR, P_NEW, 1)

# plant-rest.py runs one fixed proof for every plant. The bond plants assert against their own,
# so the loop takes the command from the row -- the shape plant-startplacement.py already uses.
OLD_LOOP = u'''for label, path, old, new in PLANTS:'''
NEW_LOOP = u'''# **THE PROOF COMES FROM THE ROW.** This suite ran one fixed proof for every plant, which is
# fine while every plant belongs to one subsystem and wrong the moment one does not: a bond plant
# run against the areas proof would pass and prove nothing. Same shape
# `plant-startplacement.py` already uses.
for label, path, old, new, command in PLANTS:'''
if suite.count(OLD_LOOP) == 1:
    suite = suite.replace(OLD_LOOP, NEW_LOOP, 1)
    suite = suite.replace(
        u'''        code = subprocess.call([sys.executable, ".local/register/proof-areas-and-debrief.py"],''',
        u'''        code = subprocess.call([sys.executable, command],''', 1)
else:
    print("LOOP ANCHOR PROBLEM: %d" % suite.count(OLD_LOOP))
    raise SystemExit(1)

# Every pre-existing row is a 4-tuple and needs the proof it already ran.
import re
def widen(match):
    return match.group(0)[:-1] + ", AREAS_PROOF)"

head, sep, tail = suite.partition(P_NEW)
if not sep:
    print("SPLIT PROBLEM")
    raise SystemExit(1)
tail = re.sub(r'\)\),\n', '), AREAS_PROOF),\n', tail)
tail = re.sub(r'"\),\n', '", AREAS_PROOF),\n', tail)
suite = head + sep + tail
suite = suite.replace(u'BONDS_PROOF = ".local/register/proof-bonds.py"',
                      u'BONDS_PROOF = ".local/register/proof-bonds.py"\n'
                      u'AREAS_PROOF = ".local/register/proof-areas-and-debrief.py"', 1)
io.open(SUITE, "w", encoding="utf-8", newline="").write(suite)
print("fourteen bond plants added, and the suite takes its proof from the row")
