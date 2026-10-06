# -*- coding: utf-8 -*-
"""Planted faults against `tools/check-record-book-class.py`.

**The checker passed on its first run, which proves nothing at all.** The defect it exists for was a
feature that read as built in every file a reader would open -- `CompRouteEvidence.TransformLabel`
returning the company label and never once being called, because `Verse.Book` overrides the property
that runs the comp chain. A green instrument over that kind of fault is exactly what let it live
through thirteen launches.

So every rule gets a fault aimed at it, including the two that are easy to write and hard to notice:
a `LabelNoCount` that transforms the finished string and silently drops quality, and a patch aimed at
Core's abstract `BookBase`, which would hand our class to three defs we have no business touching.

Run from the repository root.
"""
import io
import os
import subprocess
import sys
import time

BOOK = "src/RimroomsAsyncIndustries/Investigation/RimroomsRecordBook.cs"
COMP = "src/RimroomsAsyncIndustries/Investigation/CompRouteEvidence.cs"
PATCH = "Mod/Rimrooms - Async Industries/1.6/Patches/RR_ExistingEvidenceBook.xml"
BINDING = "src/RimroomsAsyncIndustries/Investigation/RecordBookClassBinding.cs"
KEYED = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Investigation.xml"
HQ = "src/RimroomsAsyncIndustries/Scenario/GenStep_Headquarters.cs"
ARRIVAL = "src/RimroomsAsyncIndustries/Scenario/ScenPart_RimroomsArrival.cs"
DELIVERY = "src/RimroomsAsyncIndustries/Company/RecordBookDelivery.cs"
PROCUREMENT = "src/RimroomsAsyncIndustries/Procurement/RimroomsProcurementComponent.cs"
FIELD = "src/RimroomsAsyncIndustries/Investigation/RimroomsEvidenceCreationComponent.cs"

CHECK = "tools/check-record-book-class.py"

NL = chr(10)

PLANTS = [
    # ============================================================ rule 1, the class is a Book
    ("THE CLASS STOPS BEING A BOOK, SO THE DEF'S OWN BOOK CHECK WOULD REFUSE IT", BOOK,
     "class RimroomsRecordBook : Book", "class RimroomsRecordBook : ThingWithComps", CHECK),

    # ============================================================ rule 2, the three overrides
    # **ANCHORED ON THE BRACE, BECAUSE THE DOC COMMENT QUOTES CORE'S OWN BODIES VERBATIM.** The
    # first draft of these two plants replaced the first occurrence of the signature, which is
    # inside the comment that explains what `Book` skips -- so they edited prose and the checker
    # correctly saw unchanged code. The plant was wrong, not the instrument.
    ("the name override goes, so the company label never reaches the label", BOOK,
     "public override string LabelNoParenthesis" + NL + "        {",
     "public string LabelNoParenthesisDisabled" + NL + "        {", CHECK),

    ("the full label override goes, so quality and damage come back without the company name", BOOK,
     "public override string LabelNoCount" + NL + "        {",
     "public string LabelNoCountDisabled" + NL + "        {", CHECK),

    ("THE DESCRIPTION OVERRIDE GOES AND THE i PANEL GOES BACK TO CLAIMING NUTRITION", BOOK,
     "public override string DescriptionDetailed", "public string DescriptionDetailedDisabled", CHECK),

    # ============================================================ rule 3, the comp chain
    ("the comp chain is not run, which is the EXACT defect this instrument exists for", BOOK,
     "text = part.TransformLabel(text);", "text = text;", CHECK),

    ("the chain stops walking every comp", BOOK,
     "List<ThingComp> parts = AllComps;", "List<ThingComp> parts = null;", CHECK),

    # ============================================================ rule 4, composition order
    ("THE LABEL IS BUILT WITHOUT THE EXTRAS, SO A MASTERWORK BOOK STOPS SAYING SO", BOOK,
     "                return LabelNoParenthesis" + NL
     + "                    + GenLabel.LabelExtras(this, includeHp: true, includeQuality: true);",
     "                return LabelNoParenthesis;", CHECK),

    # ============================================================ rule 5, no saved state
    ("the class starts saving state, which would make the thingClass swap a save break", BOOK,
     "    public class RimroomsRecordBook : Book" + NL + "    {",
     "    public class RimroomsRecordBook : Book" + NL + "    {" + NL
     + "        private int planted;" + NL
     + "        public override void ExposeData() { Scribe_Values.Look(ref planted, \"p\", 0); }",
     CHECK),

    # ============================================================ rule 6, the patch stays additive
    ("THE DESTRUCTIVE PATCH COMES BACK, which check-compliance rule 3 refused and was right to", PATCH,
     '    <nomatch Class="PatchOperationAdd">',
     '    <nomatch Class="PatchOperationReplace">', CHECK),

    ("the patch starts writing thingClass again, where Core's abstract parent makes it unsafe", PATCH,
     "          <analysisWorkRequired>3000</analysisWorkRequired>",
     "          <analysisWorkRequired>3000</analysisWorkRequired>" + NL
     + "        </li>" + NL
     + "        <li><thingClass>Verse.Book</thingClass>", CHECK),

    # ============================================================ rule 7, the startup binding
    ("THE BINDING NEVER ASSIGNS OUR CLASS, so the whole repair is inert", BINDING,
     "book.thingClass = typeof(RimroomsRecordBook);", "Bound = Bound;", CHECK),

    ("the binding stops running at startup, so it reads a value before mods have resolved", BINDING,
     "    [StaticConstructorOnStartup]", "    // startup attribute removed", CHECK),

    ("THE BINDING CLOBBERS ANOTHER MOD'S CLASS SILENTLY, which is what the Replace was refused for",
     BINDING, "            if (book.thingClass != typeof(Book))", "            if (false)", CHECK),

    ("the binding declines without saying so, which looks identical to being broken", BINDING,
     "                Log.Warning(", "                Noop(", CHECK),

    ("the binding resolves TextBook in a way that throws when Core books are absent", BINDING,
     'DefDatabase<ThingDef>.GetNamedSilentFail("TextBook")',
     'DefDatabase<ThingDef>.GetNamed("TextBook")', CHECK),

    # ============================================================ rule 8, every issuing route
    ("the start def's authored books stop being marked", HQ,
     "placedBook.MarkCompanyIssued();", "placedBook.EvidenceId.ToString();", CHECK),

    ("the scenario arrival sweep stops marking", ARRIVAL,
     "issued.MarkCompanyIssued();", "issued.ToString();", CHECK),

    ("THE CORPORATION'S OWN DROP STOPS MARKING, which is the gap this batch found", DELIVERY,
     "issued.MarkCompanyIssued();", "issued.ToString();", CHECK),

    ("A BOOK BOUGHT FROM THE COMPANY CATALOGUE STOPS BEING THE COMPANY'S", PROCUREMENT,
     "ordered.MarkCompanyIssued();", "ordered.ToString();", CHECK),

    # ============================================================ rule 9, the one that must not
    ("a book FOUND in a coordinate gets branded as the company's, which is a lie on the card", FIELD,
     "                    attempt.itemLoadId = attempt.item.GetUniqueLoadID();",
     "                    attempt.item.TryGetComp<CompRouteEvidence>().MarkCompanyIssued();" + NL
     + "                    attempt.itemLoadId = attempt.item.GetUniqueLoadID();", CHECK),

    # ============================================================ rule 10, displayed strings
    ("the instruction block loses its keyed string and the i panel renders a raw key", KEYED,
     "<RR_Evidence_CompanyBookDesc>", "<RR_Evidence_CompanyBookDescUnused>", CHECK),

    ("the click action's own label loses its keyed string", KEYED,
     "<RR_UI_JournalHowTo>", "<RR_UI_JournalHowToUnused>", CHECK),

    ("the comp stops offering a description, so the class has nothing to show", COMP,
     "        public string CompanyDescription", "        public string CompanyDescriptionDisabled",
     CHECK),
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
