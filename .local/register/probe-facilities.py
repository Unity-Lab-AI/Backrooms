# -*- coding: utf-8 -*-
"""Measure whether institutions actually form, not just whether the planner compiles.

`FacilityPlanner` groups rooms so three rooms read as a laboratory wing rather than three rooms
that each happen to have a bench. It was gated on `coordinate.Depth <= 1`, so **a first level had
none**, and nothing in the battery could see that: the planner existed, was called, and returned
an empty map.

That is the shape of defect this run has found seven times. So the probe counts them: how many
institutions a layout has and how big the largest is. **A depth band that forms none is a
failure**, because the owner asked for complexes on every level.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROBE = os.path.join(REPO, ".local", "harness", "PlannerProbe", "Program.cs")

EDITS = [
    (u"        private static MethodInfo buildCandidate;",
     u"        private static MethodInfo buildCandidate;\n"
     u"        private static MethodInfo anchorFor;\n"
     u"        private static FieldInfo coordinateRooms;"),

    (u'            buildCandidate = planner.GetMethod("Build", Statics);',
     u'            buildCandidate = planner.GetMethod("Build", Statics);\n'
     u'            Type facilities = assembly.GetType(\n'
     u'                "RimroomsAsyncIndustries.Generation.FacilityPlanner", true);\n'
     u'            anchorFor = facilities.GetMethod("AnchorFor", Statics);\n'
     u'            coordinateRooms = coordinateType.GetField("rooms",\n'
     u'                BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);'),

    (u"                int fellBack = 0;",
     u"                int fellBack = 0;\n                int institutions = 0;\n"
     u"                int biggest = 0;"),

    (u"                    if (safeCandidates == 0) { fellBack++; }",
     u"                    if (safeCandidates == 0) { fellBack++; }\n\n"
     u"                    // **DO INSTITUTIONS ACTUALLY FORM?** `FacilityPlanner` was gated on\n"
     u"                    // `coordinate.Depth <= 1`, so a first level had none -- and nothing in\n"
     u"                    // the battery could see it, because the planner existed, was called,\n"
     u"                    // and returned an empty map. Seventh instance of that shape this run.\n"
     u"                    coordinateRooms.SetValue(coordinate, layout);\n"
     u"                    var groups = new Dictionary<int, int>();\n"
     u"                    foreach (object room in layout)\n"
     u"                    {\n"
     u"                        int index = Field<int>(room, \"index\");\n"
     u"                        var anchor = (int)anchorFor.Invoke(\n"
     u"                            null, new object[] { coordinate, index });\n"
     u"                        if (anchor < 0) { continue; }\n"
     u"                        int seen;\n"
     u"                        groups[anchor] = groups.TryGetValue(anchor, out seen) ? seen + 1 : 1;\n"
     u"                    }\n"
     u"                    institutions += groups.Count;\n"
     u"                    foreach (int size in groups.Values)\n"
     u"                    { if (size > biggest) { biggest = size; } }"),
]

text = io.open(PROBE, encoding="utf-8").read()
problems = []
for old, _ in EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:58]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    text = text.replace(old, new, 1)

marker = u'                    "{0} depth {1,-2} refused {2,3}/{3} rooms {4,4:0.0}'
start = text.index(marker)
end = text.index(u"\n", start)
line = text[start:end]
text = text[:start] + line.replace(
    u'fellback {11,4}",',
    u'fellback {11,4} institutions {12,5:0.0} biggest {13,3}",') + text[end:]

close = u"                    fellBack));"
if text.count(close) != 1:
    print("CLOSE ANCHOR PROBLEM: %d" % text.count(close))
    raise SystemExit(1)
text = text.replace(
    close,
    u"                    fellBack,\n"
    u"                    refused == Seeds ? 0.0 : (double)institutions / (Seeds - refused),\n"
    u"                    biggest));", 1)

# No institutions anywhere in a band is a failure, not a note.
guard_anchor = u"                if (fellBack >= Seeds) { fellBackEverywhere = true; }"
if text.count(guard_anchor) != 1:
    print("GUARD ANCHOR PROBLEM: %d" % text.count(guard_anchor))
    raise SystemExit(1)
text = text.replace(
    guard_anchor,
    guard_anchor + u"\n"
    u"                if (institutions == 0) { noInstitutions = true; }", 1)
text = text.replace(u"            bool fellBackEverywhere = false;",
                    u"            bool fellBackEverywhere = false;\n"
                    u"            bool noInstitutions = false;", 1)
text = text.replace(
    u"            if (totalBackToBack == 0)",
    u"            if (noInstitutions)\n"
    u"            {\n"
    u"                Console.WriteLine(\"PROBE FAILED: a depth band formed no institutions at \"\n"
    u"                                  + \"all, so no school, hospital, armoury or storage \"\n"
    u"                                  + \"complex can exist there.\");\n"
    u"                return 1;\n"
    u"            }\n"
    u"            if (totalBackToBack == 0)", 1)

io.open(PROBE, "w", encoding="utf-8", newline="").write(text)
print("the probe counts institutions and fails a band that forms none")
