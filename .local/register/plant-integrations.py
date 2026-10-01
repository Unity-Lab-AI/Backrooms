# -*- coding: utf-8 -*-
"""Plant a fault, run the check, require failure, restore. Verified writes.

Two targets, because this batch ships a proof and a checker rule:

  * `proof-integrations.py` for the detection layer, the readout and the document
  * `tools/check-doc-conformance.py` for the row 791 claim guard -- and that one is planted with
    a REAL forbidden claim in a real reader-facing document, which is the only way to know the
    guard would have caught the thing it exists for
"""
import io
import os
import subprocess
import sys
import time

SRC = "src/RimroomsAsyncIndustries"
INTEG = SRC + "/Core/InstalledIntegrations.cs"
PANE = SRC + "/UI/OperationsFacilities.cs"
INHAB = SRC + "/Threats/InhabitantService.cs"
DOC = "docs/MULTIPLAYER.md"
CONF = "tools/check-doc-conformance.py"
PROOF = ".local/register/proof-integrations.py"
CHECKER = "tools/check-doc-conformance.py"

# (label, path, old, new, command to run, expected non-zero)
PLANTS = [
    ("a package id drifts from the register", INTEG,
     'PackageId = "3609835606"', 'PackageId = "3609835607"', PROOF),

    ("detection stops using Core's own answer", INTEG,
     "ModsConfig.IsActive(state.PackageId)", "false", PROOF),

    ("the installed list is read once and goes stale", INTEG,
     "            int hash = ModLister.InstalledModsListHash(true);", "            int hash = 0;",
     PROOF),

    ("a tracked mod stops being tracked", INTEG,
     """            new IntegrationState
            {
                RegisterRow = 281,
                PackageId = "3799737423",
                NameKey = "RR_Integration_GravshipTwoName",
                PositionKey = "RR_Integration_GravshipTwoPosition",
            },
""", "", PROOF),

    ("THE DETECTION STARTS DECIDING SOMETHING", SRC + "/Gate/GateIntegrity.cs",
     "        internal void TickIntegrity()\n        {",
     "        internal void TickIntegrity()\n        {\n"
     "            if (Core.InstalledIntegrations.ActiveRow(11)) { return; }", PROOF),

    ("a package id appears outside the detection class", SRC + "/Gate/GateIntegrity.cs",
     "    public sealed partial class CompRimroomsGate\n    {",
     '    public sealed partial class CompRimroomsGate\n    {\n'
     '        private const string Unused = "3014915404";', PROOF),

    ("inhabitant generation opens up to any pawn kind", INHAB,
     "DefDatabase<RimroomsInhabitantDef>", "DefDatabase<PawnKindDef>.AllDefs; var _ =\n"
     "                DefDatabase<RimroomsInhabitantDef>", PROOF),

    ("the document stops denying a shared colony", DOC,
     "There is **no shared colony**.", "Companies can share a colony.", PROOF),

    ("the caveat moves out of the opening line", DOC,
     "**Nothing on this page has been tested in play.**", "Notes on playing together.", PROOF),

    ("the document starts claiming support", DOC,
     "## What you need", "## What you need\n\nRimWorld Together is supported.", PROOF),

    ("the readout stops drawing the heading", PANE,
     'listing.Label("RR_Integration_Heading".Translate(',
     'string unusedHeading = "RR_Integration_Heading".Translate(', PROOF),

    ("the caveat becomes conditional", PANE,
     '            listing.Label("RR_Integration_Caveat".Translate());\n', "", PROOF),

    ("the position is hidden for a mod that is not loaded", PANE,
     "                listing.Label(state.PositionKey.Translate());",
     "                if (state.Active) { listing.Label(state.PositionKey.Translate()); }",
     PROOF),

    ("the section is never reached", PANE, "            DrawIntegrations(listing);\n", "", PROOF),

    ("THE CLAIM GUARD IS BLINDED", CONF,
     "        check_forbidden_claims(rel, prose, problems)\n", "", PROOF),

    # The guard itself, planted with a real claim in a real reader-facing document.
    ("ROW 791: a real shared-research claim lands in a reader-facing document", DOC,
     "## What you need", "## What you need\n\nResearch is synchronised research across every "
     "company on the server.", CHECKER),

    ("ROW 791: a real shared-colony claim lands in a reader-facing document", "README.md",
     "\n## ", "\n\nTwo players run one shared colony together.\n\n## ", CHECKER),
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


caught = 0
for label, path, old, new, command in PLANTS:
    original = io.open(path, encoding="utf-8").read()
    if original.count(old) < 1:
        print("PLANT SETUP BROKEN (0 matches): %s" % label)
        sys.exit(2)
    write_verified(path, original.replace(old, new, 1))
    try:
        code = subprocess.call([sys.executable, command],
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        # **THE RESTORE IS THE ONE LINE THAT MUST ALWAYS RUN.** It is what
        # makes a destructive instrument safe, and it was the one line not
        # protected: a leaked devnull handle raised OSError mid-run twice
        # and left planted source on disk both times.
        write_verified(path, original)
    ok = code != 0
    caught += 1 if ok else 0
    print("%s  %s" % ("CAUGHT " if ok else "MISSED!", label))

print("")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
