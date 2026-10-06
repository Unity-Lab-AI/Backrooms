# -*- coding: utf-8 -*-
"""Checker 27 -- the company record book is the company's book, on every route that makes one.

WHY THIS INSTRUMENT EXISTS, AND WHY NOTHING ELSE COULD HAVE CAUGHT IT

`CompRouteEvidence.TransformLabel` returned the company label for a company-issued book from
0.12.9x onward and **was never called once**. `ThingWithComps.LabelNoCount` is where the comp label
chain runs; `Verse.Book` overrides that property, `LabelNoParenthesis` and `DescriptionFlavor`, and
never calls base. So the feature read as built in every file a reader would open, and the owner
found two starting journals still claiming to be about nutrition and aiming.

**Every existing instrument passed.** A checker that reads our source sees a transform that looks
correct. A checker that reads the def sees a comp correctly attached. The fault lived in the gap
between the two -- in a Core class neither of them reads. So this one asserts the *bridge*: that a
`thingClass` exists to restore those chains, that it is on the right def, and that every route
which mints a record book marks it, because an unmarked book makes the bridge a no-op.

THE RULES

 1. `RimroomsRecordBook` exists and derives from `Verse.Book`.
 2. It overrides all three members `Book` hijacks: `LabelNoParenthesis`, `LabelNoCount`,
    `DescriptionDetailed`.
 3. `LabelNoParenthesis` runs the comp chain -- it calls `TransformLabel` over `AllComps`.
 4. `LabelNoCount` is composed from `LabelNoParenthesis` plus `GenLabel.LabelExtras`, never by
    transforming the finished string, or quality and damage are thrown away.
 5. The class holds **no saved state**: no `Scribe_`, no instance field. A `thingClass` swap on a
    def is save-safe only while that is true.
 6. The patch stays **additive and carries no thingClass at all**. Core declares `thingClass` on
    the abstract `BookBase`, so the only xpath that reaches the child is a Replace -- and
    `check-compliance` rule 3 refuses that, correctly, because a replace takes ownership of a def
    by load order. Patching the parent would hand our class to `Novel`, `Schematic` and `Tome`.
 7. The binding lives at `StaticConstructorOnStartup`, assigns our class, **and declines out loud**
    if the class is no longer Core's own `Book`. Two mods silently fighting over a single-valued
    field is worse than one mod visibly standing down.
 8. Every route that creates a record book marks it company-issued. Four are known and named; the
    rule is that each named file carries the call, so deleting one is a failure rather than a
    quieter mod.
 9. The field-created evidence book is **not** marked, deliberately: a book found in a coordinate
    is somebody else's, which is the whole meaning of `RR_Evidence_Unregistered`.
10. Every keyed string these paths display exists in the keyed file.
"""
import io
import os
import re
import sys

NL = chr(10)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CLASS_FILE = os.path.join("src", "RimroomsAsyncIndustries", "Investigation", "RimroomsRecordBook.cs")
COMP_FILE = os.path.join("src", "RimroomsAsyncIndustries", "Investigation", "CompRouteEvidence.cs")
PATCH_FILE = os.path.join("Mod", "Rimrooms - Async Industries", "1.6", "Patches",
                          "RR_ExistingEvidenceBook.xml")
BINDING_FILE = os.path.join("src", "RimroomsAsyncIndustries", "Investigation",
                            "RecordBookClassBinding.cs")
KEYED_FILE = os.path.join("Mod", "Rimrooms - Async Industries", "1.6", "Languages", "English",
                          "Keyed", "RR_Investigation.xml")

CLASS_NAME = "RimroomsAsyncIndustries.Investigation.RimroomsRecordBook"

# Rule 8. Each of these mints or receives a record book on a route the company owns.
ISSUING_ROUTES = (
    (os.path.join("src", "RimroomsAsyncIndustries", "Scenario", "GenStep_Headquarters.cs"),
     "the start def's authored books"),
    (os.path.join("src", "RimroomsAsyncIndustries", "Scenario", "ScenPart_RimroomsArrival.cs"),
     "the scenario arrival sweep"),
    (os.path.join("src", "RimroomsAsyncIndustries", "Company", "RecordBookDelivery.cs"),
     "the corporation's drop"),
    (os.path.join("src", "RimroomsAsyncIndustries", "Procurement", "RimroomsProcurementComponent.cs"),
     "a book bought from the company catalogue"),
)

# Rule 9. This one must NOT mark, and saying so is what stops a future sweep from "fixing" it.
FIELD_CREATION = os.path.join("src", "RimroomsAsyncIndustries", "Investigation",
                              "RimroomsEvidenceCreationComponent.cs")

DISPLAYED_KEYS = ("RR_Evidence_CompanyBookLabel", "RR_Evidence_CompanyBookDesc",
                  "RR_UI_JournalHowTo", "RR_UI_JournalHowToTitle")


def read(relative):
    path = os.path.join(ROOT, relative)
    if not os.path.isfile(path):
        return None
    return io.open(path, encoding="utf-8-sig").read()


def strip_comments(source):
    """Drop line and block comments so a rule cannot be satisfied by prose about itself.

    The doc comment in `RimroomsRecordBook.cs` quotes Core's own `LabelNoCount` body verbatim to
    show what `Book` skips. Every containment rule below would pass on that quotation alone, which
    is the fault this project has met often enough to have a name for: a claim that reads the
    comment beside the code rather than the code.
    """
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.S)
    return NL.join(line for line in source.split(NL) if not line.lstrip().startswith("//"))


def main():
    problems = []

    # ---------------------------------------------------------------- rules 1 to 5, the class
    raw = read(CLASS_FILE)
    if raw is None:
        problems.append("%s is missing; the company label and description have no route to a book"
                        % CLASS_FILE)
        code = ""
    else:
        code = strip_comments(raw)
        if not re.search(r"class\s+RimroomsRecordBook\s*:\s*Book\b", code):
            problems.append("RimroomsRecordBook does not derive from Verse.Book, so a thingClass "
                            "patch pointing at it would fail the def's own Book check")
        for member in ("LabelNoParenthesis", "LabelNoCount", "DescriptionDetailed"):
            if not re.search(r"public\s+override\s+string\s+" + member + r"\b", code):
                problems.append("RimroomsRecordBook does not override %s, which Verse.Book "
                                "hijacks; the comp chain stays broken for that surface" % member)
        if "TransformLabel" not in code or "AllComps" not in code:
            problems.append("RimroomsRecordBook does not run the comp label chain over AllComps, "
                            "so CompRouteEvidence.TransformLabel is still dead code on a book")
        if "GenLabel.LabelExtras" not in code:
            problems.append("RimroomsRecordBook does not append GenLabel.LabelExtras, so a book's "
                            "quality and damage would be dropped from its label")
        if "LabelNoParenthesis" not in code.split("LabelNoCount", 1)[-1][:400] \
                and "LabelNoParenthesis\n" not in code:
            # Composition rule 4: LabelNoCount must build on the transformed name.
            if not re.search(r"LabelNoCount[\s\S]{0,300}LabelNoParenthesis", code):
                problems.append("RimroomsRecordBook.LabelNoCount is not composed from "
                                "LabelNoParenthesis; transforming the finished string instead "
                                "discards the quality and damage suffix")
        if "Scribe_" in code:
            problems.append("RimroomsRecordBook writes save data. A thingClass swap on an existing "
                            "def is save-safe only while the class holds no state")
        fields = re.findall(r"^\s+(?:private|internal|public|protected)\s+(?!override|static\s+readonly)"
                            r"[\w<>\[\]\.]+\s+\w+\s*;", code, flags=re.M)
        if fields:
            problems.append("RimroomsRecordBook declares %d instance field(s) (%s); it must hold no "
                            "state, so everything it reads lives in the comp or the campaign record"
                            % (len(fields), ", ".join(f.strip()[:40] for f in fields[:3])))

    # ---------------------------------------------------------------- rules 6 and 7, the patch
    # **THE BINDING IS IN CODE AND THE PATCH MUST STAY ADDITIVE.** The first version of this rule
    # asserted an XML thingClass operation, and `check-compliance` rule 3 refused the patch it was
    # written for: Core declares thingClass on the abstract `BookBase`, so the only operation that
    # reaches the child is a Replace, and a Replace takes ownership of a def where the last mod to
    # load wins. **The rule was right and the patch was wrong**, so the binding moved to
    # `StaticConstructorOnStartup` -- which also sees the resolved value and can decline instead of
    # clobbering. This checker now guards that shape instead.
    patch = read(PATCH_FILE)
    if patch is None:
        problems.append("%s is missing; the comp is no longer attached to TextBook" % PATCH_FILE)
    else:
        body = re.sub(r"<!--[\s\S]*?-->", "", patch)
        if 'defName="TextBook"' not in body:
            problems.append("the patch does not target TextBook by defName")
        if "BookBase" in body:
            problems.append("the patch references BookBase outside a comment. Core declares "
                            "thingClass on that abstract parent, so patching it would hand our "
                            "class to Novel, Schematic and Tome as well")
        if "PatchOperationReplace" in body or "PatchOperationRemove" in body:
            problems.append("the patch carries a destructive operation. check-compliance rule 3 "
                            "already refuses this, and the binding belongs at startup precisely "
                            "because a replace takes ownership of a def by load order")
        if "thingClass" in body:
            problems.append("the patch writes thingClass. Core declares it on the abstract parent, "
                            "so an Add here risks a duplicate element and a Replace takes the def "
                            "over; the binding belongs in %s" % BINDING_FILE)

    binding = read(BINDING_FILE)
    if binding is None:
        problems.append("%s is missing, so nothing puts the class on the def and the comp label "
                        "chain stays broken" % BINDING_FILE)
    else:
        bind = strip_comments(binding)
        if "StaticConstructorOnStartup" not in bind:
            problems.append("the binding does not run at StaticConstructorOnStartup, so it would "
                            "read a thingClass before inheritance and other mods had resolved")
        if not re.search(r"thingClass\s*=\s*typeof\(RimroomsRecordBook\)", bind):
            problems.append("the binding never assigns RimroomsRecordBook to thingClass, so Core's "
                            "Book class stays on TextBook and the book keeps its generated title")
        if not re.search(r"thingClass\s*!=\s*typeof\(Book\)", bind):
            problems.append("the binding does not check that the class is still Core's own Book. "
                            "Without that it clobbers another mod's class silently, which is the "
                            "exact failure the XML Replace was refused for")
        if "Log.Warning" not in bind:
            problems.append("the binding declines without saying so. A mod that quietly does "
                            "nothing is indistinguishable from a mod that is broken")
        if "GetNamedSilentFail" not in bind:
            problems.append("the binding does not resolve TextBook tolerantly, so a game without "
                            "Core books would throw during startup rather than stay quiet")

    # ---------------------------------------------------------------- rule 8, every issuing route
    for relative, description in ISSUING_ROUTES:
        source = read(relative)
        if source is None:
            problems.append("%s is missing, and it is one of the four routes that issue a record "
                            "book (%s)" % (relative, description))
            continue
        if "MarkCompanyIssued" not in strip_comments(source):
            problems.append("%s does not call MarkCompanyIssued, so %s arrives wearing Core's "
                            "generated title and the company label never applies"
                            % (relative, description))

    # ---------------------------------------------------------------- rule 9, the one that must not
    field = read(FIELD_CREATION)
    if field is not None and "MarkCompanyIssued" in strip_comments(field):
        problems.append("%s marks a field-created book as company-issued. A book found in a "
                        "coordinate is somebody else's, which is the entire meaning of "
                        "RR_Evidence_Unregistered" % FIELD_CREATION)

    # ---------------------------------------------------------------- rule 10, the displayed strings
    keyed = read(KEYED_FILE)
    comp = read(COMP_FILE)
    if keyed is None:
        problems.append("%s is missing" % KEYED_FILE)
    else:
        for key in DISPLAYED_KEYS:
            if "<" + key + ">" not in keyed:
                problems.append("keyed string %s is displayed by the record book but is not in %s"
                                % (key, KEYED_FILE))
    if comp is not None:
        body = strip_comments(comp)
        # **THE SIGNATURE, WITH A WORD BOUNDARY, BECAUSE CONTAINMENT PASSED ON A RENAME.** A plant
        # renamed the member to `CompanyDescriptionDisabled` and the first draft's `in` test still
        # saw the string. `in` cannot tell a member from a prefix of one -- the same lesson as `in`
        # not being able to tell one call site from three.
        if not re.search(r"public\s+string\s+CompanyDescription\b", body):
            problems.append("CompRouteEvidence has no CompanyDescription member, so the class has "
                            "nothing to show in place of Core's generated subject")
        if code and not re.search(r"\.CompanyDescription\b", code):
            problems.append("RimroomsRecordBook never reads CompanyDescription, so the company's "
                            "write-up exists and never reaches the card")
        if "RR_Evidence_CompanyBookDesc" not in body:
            problems.append("CompRouteEvidence never reads RR_Evidence_CompanyBookDesc")

    print("check-record-book-class")
    print("  class                  : %s" % (CLASS_FILE if raw is not None else "MISSING"))
    print("  issuing routes checked : %d" % len(ISSUING_ROUTES))
    print("  displayed keys checked : %d" % len(DISPLAYED_KEYS))
    print("")
    if problems:
        for problem in problems:
            print("  FAIL   : %s" % problem)
        print("")
        print("  %d problem(s)" % len(problems))
        return 1
    print("  PASS   : the company's book is the company's book on every route that makes one")
    return 0


if __name__ == "__main__":
    sys.exit(main())
