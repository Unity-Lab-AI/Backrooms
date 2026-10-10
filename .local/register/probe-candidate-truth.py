# -*- coding: utf-8 -*-
"""Make the probe say WHICH candidate won, and why the others lost.

`TrySelect` tries three real candidates and then falls back to a simple serpentine. **So
`refused 0/200` can mean "every real layout failed and the safety net caught every seed"** -- and
that is exactly what it meant the first time the braided maze was measured. The probe reported
total success while not one maze had been built.

The giveaway was indirect: `rooms 24.0` and `widest 40` at every depth, which are the fallback's
own signature -- `MinSlotsPerAxis * MinSlotsPerAxis * 2 / 3` is 24 and the fallback builds no
grand hall. **An instrument that can only be read by recognising a number's fingerprint is an
instrument with a blind spot.**

So it asks the direct question now: of the three real candidates, how many pass
`CandidateIsSafe`, and when none do, what key does `ValidateRooms` give for the first one. Both
are reflected off the shipping planner, so the probe cannot disagree with the game about what is
acceptable.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROBE = os.path.join(REPO, ".local", "harness", "PlannerProbe", "Program.cs")

EDITS = [
    (u"        private static MethodInfo onRouteCross;",
     u"        private static MethodInfo onRouteCross;\n"
     u"        private static MethodInfo buildCandidate;\n"
     u"        private static MethodInfo candidateIsSafe;\n"
     u"        private static int candidateBudget;"),

    (u'            onRouteCross = builder.GetMethod("OnRouteCross", Statics);',
     u'            onRouteCross = builder.GetMethod("OnRouteCross", Statics);\n'
     u'            buildCandidate = planner.GetMethod("Build", Statics);\n'
     u'            candidateIsSafe = planner.GetMethod("CandidateIsSafe", Statics);\n'
     u'            candidateBudget = (int)planner.GetField("CandidateBudget", Statics)'
     u'.GetValue(null);'),

    (u"                int shapedRooms = 0;",
     u"                int shapedRooms = 0;\n                int fellBack = 0;"),

    (u"                    backToBack += BackToBackPairs(layout);",
     u"                    // **WHICH CANDIDATE WON.** `TrySelect` falls back to a serpentine when\n"
     u"                    // all three real candidates are refused, so a clean `refused` column\n"
     u"                    // can still mean not one real layout was built. It meant exactly that\n"
     u"                    // the first time the maze was measured.\n"
     u"                    int safeCandidates = 0;\n"
     u"                    for (int which = 0; which < candidateBudget; which++)\n"
     u"                    {\n"
     u"                        object built = buildCandidate.Invoke(\n"
     u"                            null, new object[] { coordinate, which });\n"
     u"                        if ((bool)candidateIsSafe.Invoke(null, new object[] { built, depth }))\n"
     u"                        { safeCandidates++; continue; }\n"
     u"                        object[] why = { built, null };\n"
     u"                        validateRooms.Invoke(null, why);\n"
     u"                        if (why[1] != null)\n"
     u"                        { reasons.Add(\"candidate refused: \" + why[1]); }\n"
     u"                        else if (which == 0)\n"
     u"                        { reasons.Add(\"candidate refused: reachability or family rule\"); }\n"
     u"                    }\n"
     u"                    if (safeCandidates == 0) { fellBack++; }\n"
     u"                    backToBack += BackToBackPairs(layout);"),
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

# The format line is one long literal; find it by its stable head rather than by the whole string.
marker = u'                    "{0} depth {1,-2} refused {2,3}/{3} rooms {4,4:0.0}'
start = text.index(marker)
end = text.index(u"\n", start)
old_line = text[start:end]
text = text[:start] + old_line.replace(
    u'rock {10,4:0.0}%",', u'rock {10,4:0.0}% fellback {11,4}",') + text[end:]

close = u"                    interiorTotal == 0 ? 0.0 : 100.0 * rockTotal / interiorTotal));"
if text.count(close) != 1:
    print("CLOSE ANCHOR PROBLEM: %d" % text.count(close))
    raise SystemExit(1)
text = text.replace(
    close,
    u"                    interiorTotal == 0 ? 0.0 : 100.0 * rockTotal / interiorTotal,\n"
    u"                    fellBack));", 1)

# And falling back on every seed is a FAILURE, not a note.
held = u'''            if (totalBackToBack == 0)'''
guard = u'''            if (fellBackEverywhere)
            {
                Console.WriteLine("PROBE FAILED: at least one depth band built no real candidate "
                                  + "at all and the fallback caught every seed.");
                return 1;
            }
            if (totalBackToBack == 0)'''
if text.count(held) != 1:
    print("HELD ANCHOR PROBLEM: %d" % text.count(held))
    raise SystemExit(1)
text = text.replace(held, guard, 1)
text = text.replace(u"            int totalBackToBack = 0;",
                    u"            int totalBackToBack = 0;\n"
                    u"            bool fellBackEverywhere = false;", 1)
text = text.replace(u"                if (refused != 0) { failures++; }",
                    u"                if (refused != 0) { failures++; }\n"
                    u"                if (fellBack >= Seeds) { fellBackEverywhere = true; }", 1)

io.open(PROBE, "w", encoding="utf-8", newline="").write(text)
print("the probe reports fallbacks and the refusal key, and fails when the net catches everything")
