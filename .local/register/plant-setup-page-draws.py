# -*- coding: utf-8 -*-
"""Plant the truncation back and require the proof to refuse it.

Plant a fault, run the target, require failure, restore. Verified writes. Clean run first.

The headline plant removes `maxOneColumn` from the page the owner was looking at, which is the
exact state that drew three lines and stopped. The rest cover the other six listings, a NEW
listing added with no declaration at all (the case this is really guarding against, since the
defect ships the moment somebody writes one), the supplies source, and the gate line's promise.
"""
import io
import os
import subprocess
import sys
import time

PROOF = ".local/register/proof-setup-page-draws.py"
SRC = "src/RimroomsAsyncIndustries"
PAGE = SRC + "/Scenario/Page_RimroomsCompanySetup.cs"
COMPONENT = SRC + "/Scenario/RimroomsStartupComponent.cs"
SETTINGS = SRC + "/Core/RimroomsMod.cs"
OPS = SRC + "/UI/MainTabWindow_Operations.cs"
RECORDS = SRC + "/UI/ExpeditionRecordDialogs.cs"
KEYED = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_StartupSetup.xml"

# (label, path, old, new)

# **THE RESTORE DOES NOT SURVIVE THE PROCESS BEING KILLED.** `finally` handles an exception; it
# does nothing for an interrupted sweep, and that is how a planted fault reached the working tree
# for the third time. The sentinel makes it visible: `tools/check-plant-residue.py` refuses while
# this file exists and prints the path to restore.
_RR_SENTINEL = os.path.join(".local", "register", ".plant-in-progress")


def _rr_mark(path, label):
    io.open(_RR_SENTINEL, "w", encoding="utf-8", newline="").write(
        u"planted %r into %s" % (label, path))


def _rr_unmark():
    try:
        os.remove(_RR_SENTINEL)
    except OSError:
        pass


PLANTS = [
    ("THE DEFECT THE OWNER SAW: the setup page's listing loses its one-column flag", PAGE,
     "listing.maxOneColumn = true;\n            listing.Begin(content);",
     "listing.Begin(content);"),

    ("the pinned confirm row loses it, so Start can become unsatisfiable", PAGE,
     "gate.maxOneColumn = true;\n            gate.Begin(confirm);",
     "gate.Begin(confirm);"),

    ("THE OPERATIONS BOARD loses it, which is the main window of the mod", OPS,
     "listing.maxOneColumn = true;\n            listing.Begin(content);",
     "listing.Begin(content);"),

    ("an expedition record dialog loses it", RECORDS,
     "var listing = new Listing_Standard(); listing.maxOneColumn = true;\n"
     "            listing.Begin(content);",
     "var listing = new Listing_Standard(); listing.Begin(content);"),

    # The real guard: the next listing somebody writes.
    ("A NEW LISTING IS ADDED THAT DECLARES NEITHER", PAGE,
     "        private void DrawReview(Listing_Standard listing)\n        {",
     "        private void DrawSomethingNew(Rect rect)\n        {\n"
     "            var extra = new Listing_Standard();\n            extra.Begin(rect);\n"
     "            extra.End();\n        }\n\n"
     "        private void DrawReview(Listing_Standard listing)\n        {"),

    ("the settings window is flattened to one column, breaking a deliberate layout", SETTINGS,
     "listing.ColumnWidth = (inRect.width - 34f) / 2f;",
     "listing.maxOneColumn = true;"),

    # ------------------------------------------------------------------- the supplies source
    ("THE SUPPLIES GO BACK TO THE LIVE SCENARIO another mod rewrites", PAGE,
     "StartupReview.CompanySupplies(start)", "StartupReview.SupplySummary()"),

    ("the authored-scenario lookup is removed", COMPONENT,
     "internal static ScenarioDef AuthoredScenario(RimroomsStartDef start)",
     "internal static ScenarioDef AuthoredScenarioUnused(RimroomsStartDef start)"),

    ("the lookup stops matching on the start and takes the first scenario it sees", COMPONENT,
     "ours != null && ours.startDef == start", "ours != null"),

    ("the company list is described by BUILDING the things", COMPONENT,
     "            ScenarioDef authored = AuthoredScenario(start);\n"
     "            if (authored == null) { return lines; }",
     "            ScenarioDef authored = AuthoredScenario(start);\n"
     "            if (authored == null) { return lines; }\n"
     "            foreach (ScenPart p in authored.scenario.AllParts)\n"
     "            { foreach (Thing t in p.PlayerStartingThings()) { lines.Add(t.LabelCap); } }"),

    ("reflection is used to read the protected counts", COMPONENT,
     "        internal static List<string> CompanySupplies(RimroomsStartDef start)",
     "        internal static object Peek(ScenPart p)\n"
     "        { return p.GetType().GetField(\"count\", BindingFlags.NonPublic).GetValue(p); }\n\n"
     "        internal static List<string> CompanySupplies(RimroomsStartDef start)"),

    ("only one of the two lists is drawn, so 'on top of' is lost", PAGE,
     '                listing.Label("RR_Setup_Supplies".Translate());\n'
     "                List<string> live = StartupReview.SupplySummary();",
     '                List<string> live = StartupReview.SupplySummary();'),

    ("an empty list shows a bare heading again", PAGE,
     '                if (company.Count == 0) { listing.Label("RR_Setup_None".Translate()); }\n',
     ""),

    ("a disagreement between the two lists goes unmentioned", PAGE,
     "if (StartupReview.EquipmentManagedElsewhere(start))", "if (false)"),

    # --------------------------------------------------------------------------- the promise
    ("THE GATE LINE GOES BACK TO PROMISING MATERIALS THE STORE START DOES NOT HAVE", KEYED,
     "Check the starting supplies below for them.", "Those are in the supplies below."),

    ("a new key is used in code but never written", KEYED,
     "  <RR_Setup_CompanySupplies>", "  <RR_Setup_CompanySuppliesUnused>"),
]


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


def run(target):
    return subprocess.call([sys.executable, target],
                           stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


print("clean run first, so a plant that 'fails' cannot be a pre-existing fault")
code = run(PROOF)
print("  %-46s exit %d" % (PROOF, code))
if code != 0:
    print("ABORTED: the proof does not pass clean")
    sys.exit(2)
print("")

caught = 0
for label, path, old, new in PLANTS:
    original = io.open(path, encoding="utf-8").read()
    hits = original.count(old)
    if hits != 1:
        print("PLANT SETUP BROKEN (%d matches, need exactly 1): %s" % (hits, label))
        sys.exit(2)
    _rr_mark(path, label)
    write_verified(path, original.replace(old, new, 1))
    _rr_unmark()
    try:
        code = run(PROOF)
    finally:
        # **THE RESTORE IS THE ONE LINE THAT MUST ALWAYS RUN.** It is what
        # makes a destructive instrument safe, and it was the one line not
        # protected: a leaked devnull handle raised OSError mid-run twice
        # and left planted source on disk both times.
        write_verified(path, original)
        _rr_unmark()
    if io.open(path, encoding="utf-8").read() != original:
        sys.stderr.write("FATAL: %s not restored -- CHECK BY HAND\n" % path)
        sys.exit(3)
    ok = code != 0
    caught += 1 if ok else 0
    print("%s  %s (exit %d)" % ("CAUGHT " if ok else "MISSED!", label, code))

print("")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
