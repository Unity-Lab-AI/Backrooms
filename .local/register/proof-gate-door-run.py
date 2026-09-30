# -*- coding: utf-8 -*-
"""Assert a bound run of ordinary doors is ONE gate, one width, solid, and never a second gate.

The property this exists for
---------------------------
Owner answer at the fork, verbatim: *"i suppose the fallback is okay of building mulitple doors 1x1
to make the sizes needed to fit vehicals and the like"*, and the recorded decision was **BOTH
paths** -- Doors Expanded's real 1x3 and 2x3 for anyone running it, and a bound run of Core 1x1
doors for anyone not. The single-door half shipped at 0.9.2-dev, where Core's `OrnateDoor` gives
2x1 free. **1x3 and 2x3 are what the run adds.**

Four invariants govern it, and none of them is visible by reading the diff:

  * **INVARIANT 32 -- one gate, one spin-up.** There is exactly one way a laboratory gate opens and
    every entry point routes into it. A run is one gate with extensions, so an extension must
    report `IsDesignated` **false** -- no address, no console, no window, no operator. Three gates
    in a row pretending to be one would be three spin-ups and three addresses.

  * **INVARIANT 47 -- one width, both directions.** Per-endpoint measuring traps an animal in the
    Backrooms. Width is derived once from the run's rectangle, and every consumer reads that.

  * **INVARIANT 41 -- throughput is never capped.** A wide gate gets more entry cells and no
    quota. A run must add cells, never a counter.

  * **A RUN IS A SOLID RECTANGLE.** A ring of doors around a gap has a legal-looking bounding box
    and is not an opening. And the run's footprint is validated against the **same four shapes** a
    single door is, so a fallback cannot reach a size a real door could not.

And the owner's rule on changing a working gate applies unchanged: *"gate doors expansions can NOT
be done on a working gate"*, where a spin-up counts as working.

Run from the repository root.
"""
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def strip_cs_comments(text):
    """The invariants are quoted at length in these files, naming the very tokens the claims
    search for. Prose must never satisfy a claim."""
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return "\n".join(re.sub(r"//.*$", "", line) for line in text.split("\n"))


def body_of(text, signature):
    start = text.index(signature)
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    raise AssertionError("unbalanced body for %r" % signature)


run = strip_cs_comments(read(os.path.join(SRC, "Gate", "GateDoorRun.cs")))
footprint = strip_cs_comments(read(os.path.join(SRC, "Gate", "GateFootprint.cs")))
binding = strip_cs_comments(read(os.path.join(SRC, "Gate", "NativeGateBinding.cs")))
comp = strip_cs_comments(read(os.path.join(SRC, "Gate", "CompRimroomsGate.cs")))
keys = read(os.path.join(MOD, "Languages", "English", "Keyed", "RR_NativeGate.xml"))

print("")
print("proof: a bound door run is one gate, one width, solid, and refuses while working")
print("")

# ------------------------------------------------------------------ 1. one gate
print("1. one gate, one spin-up, one address")
designated = body_of(binding, "public bool IsDesignated")
check("an extension is NOT designated",
      "!IsRunExtension" in designated,
      "-- invariant 32: three gates in a row would be three spin-ups and three addresses")
check("being an extension needs a live host",
      "nativeRunHost.Destroyed" in run and "nativeRunHost.Spawned" in run,
      "-- a host lost to a raid must release its extensions rather than freeze them")
check("a door that is already a gate cannot be taken in",
      '"RR_GateRun_AlreadyAGate"' in run)
check("a door already in another run cannot be taken in",
      '"RR_GateRun_AlreadyAnExtension"' in run)
check("a gate that is itself an extension cannot take anything in",
      "if (IsRunExtension) { return CompanyActionResult.Refused(\"RR_GateRun_AlreadyAnExtension\"); }"
      in run,
      "-- otherwise a chain of hosts forms and no single thing is the gate")

# ------------------------------------------------------------------ 2. one width
print("")
print("2. one width, derived once, read by everything")
check("the occupied rect IS the run's rect",
      "get { return RunRect; }" in body_of(footprint, "public CellRect GateOccupiedRect"),
      "-- invariant 47: width measured per endpoint traps an animal in the Backrooms")
check("width still derives from the entry cells, unchanged",
      "List<IntVec3> cells = GateEntryCells;" in body_of(footprint, "public int GateWidth"),
      "-- the run flows through the existing derivation rather than adding a second one")
check("the cell count derives from the rect, not the def size",
      "CellRect rect = GateOccupiedRect;" in body_of(footprint, "public int GateCellCount"),
      "-- three bound doors are three cells of machine to power and to bring up")
check("no quota or counter was introduced",
      not re.search(r"(?i)(maxCrossings|throughputCap|crossingQuota|maxPawnsPerOpening)", run),
      "-- invariant 41: a wide gate gets more cells, never a permit limit")

# ------------------------------------------------------------------ 3. solid and legal
print("")
print("3. a run is a solid rectangle of a legal size")
rect = body_of(run, "internal CellRect RunRect")
check("a non-solid bounding box falls back to the parent's own rect",
      "union.Area != extensions.Count + own.Area" in rect,
      "-- a ring of doors around a gap is not an opening")
check("an illegal run size falls back too",
      "LegalGateFootprint(new IntVec2(union.Width, union.Height))" in rect)
check("the run is validated against the SAME four shapes a single door is",
      "LegalGateFootprint" in run and
      "private static readonly IntVec2[] LegalFootprints" in footprint,
      "-- a fallback must not reach a size a real door could not")
extend = body_of(run, "public CompanyActionResult ExtendGateAcrossRun(")
check("extending proposes, checks, and puts it back on failure",
      "nativeRunExtensions.Remove(door)" in extend and
      '"RR_GateRun_NotASolidRun"' in extend,
      "-- legality is a property of the whole run, so it can only be checked after the fact")
check("only a one-cell door may be taken in",
      '"RR_GateRun_NotSingleCell"' in extend,
      "-- a wider door is already a wider gate")
check("the candidate search asks by proposing rather than reimplementing the rules",
      "nativeRunExtensions.Add(door)" in body_of(run, "private bool WouldJoinRun("),
      "-- a second copy of the solidity rule would drift out of step with the first")
check("candidates are sorted before being shown",
      "found.Sort(" in body_of(run, "internal List<Thing> AdjacentRunCandidates("),
      "-- invariant 26: a menu whose rows move between frames is a menu somebody misclicks")

# ------------------------------------------------------------------ 4. not while working
print("")
print("4. not while the gate is working, and it survives a reload")
check("extending refuses during an opening or a spin-up",
      "IsOpening || IsSpinningUp" in extend,
      '-- owner: "gate doors expansions can NOT be done on a working gate"')
check("releasing refuses too",
      "IsOpening || IsSpinningUp" in body_of(run, "public CompanyActionResult ReleaseGateRun("))
check("releasing clears the host reference on every extension",
      "other.nativeRunHost = null" in run,
      "-- an extension left pointing at a released host is a door that is nothing")
check("both sides of the run are saved",
      'Scribe_Collections.Look(ref nativeRunExtensions, "rr_gateRunExtensions", LookMode.Reference)'
      in run and 'Scribe_References.Look(ref nativeRunHost, "rr_gateRunHost")' in run,
      "-- an unsaved run silently becomes three ordinary doors on reload")
check("the save is actually called from the comp",
      "ExposeGateRun();" in comp,
      "-- a save method nothing calls is the same defect one layer up")

# ------------------------------------------------------------------ 5. the player surface
print("")
print("5. the player can do it, and is told why not")
check("the gizmo is only offered when there is something to do",
      "RunDoorCount > 1 || AdjacentRunCandidates().Count > 0" in comp,
      "-- a button that can only refuse is worse than no button")
for key in ("RR_GateRun_Label", "RR_GateRun_Desc", "RR_GateRun_Extend", "RR_GateRun_Release",
            "RR_GateRun_NoCandidate", "RR_GateRun_NotAGate", "RR_GateRun_AlreadyAGate",
            "RR_GateRun_AlreadyAnExtension", "RR_GateRun_ActiveCannotExtend",
            "RR_GateRun_NotADoor", "RR_GateRun_SameDoor", "RR_GateRun_NotSingleCell",
            "RR_GateRun_NotASolidRun"):
    check("%s is translated" % key, "<%s>" % key in keys)
check("no refusal key is assembled at run time",
      '"RR_GateRun_" +' not in run,
      "-- the fifth time this project has caught that pattern; a built key cannot be checked")
check("the run readout uses the mod's own vocabulary",
      "doorway" not in keys.lower(),
      "-- a plain door is a 'door' and the far-side arrival point is a 'threshold'")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: a run is one gate of one width, solid, legal, and frozen while working")
