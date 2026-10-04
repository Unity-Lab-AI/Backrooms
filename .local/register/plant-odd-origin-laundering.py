# -*- coding: utf-8 -*-
"""Prove the laundering invariant can be broken, so the claims holding it are worth something.

The queue row says the routes *"must stay closed"* and that *"any future code that marks a thing
anywhere else reopens that hole."* Plant 11 is literally that: a stamp written into a file outside
the economy. If the proof does not refuse it, the row's sentence was decoration.

Plant 3 is the one that matters most. It removes the `Outside` arm from the spawn stamp, which is
the single clause that makes colony goods *provably* ordinary at birth. With it gone, nothing is
obviously broken -- odd goods are still odd, contracts still fill -- and ordinary cotton hauled
into a coordinate becomes indistinguishable from cotton found there. **A hole that leaves every
visible behaviour working is the kind only an instrument catches.**
"""
import io
import os
import subprocess
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.chdir(REPO)

PROOF = [".local/register/proof-odd-origin-laundering.py"]

COMP = "src/RimroomsAsyncIndustries/Economy/CompRimroomsOddOrigin.cs"
SERVICE = "src/RimroomsAsyncIndustries/Economy/OddOriginService.cs"
CONTRACTS = "src/RimroomsAsyncIndustries/Company/OddSupplyContracts.cs"
FOREIGN = "src/RimroomsAsyncIndustries/Portals/WorldExit.cs"

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
    sys.stderr.write("FATAL: could not write %s -- CHECK BY HAND%s" % (path, chr(10)))
    sys.exit(3)


PLANTS = [
    # ---- the stamp stops being one-way --------------------------------------------------
    ("the stamp can overwrite an answer, so a thing can be re-origined", COMP,
     "if (origin != ThingOrigin.Unknown || value == ThingOrigin.Unknown) { return; }",
     "if (value == ThingOrigin.Unknown) { return; }", 1),

    ("the stamp can write Unknown back over an answer", COMP,
     "if (origin != ThingOrigin.Unknown || value == ThingOrigin.Unknown) { return; }",
     "if (origin != ThingOrigin.Unknown) { return; }", 1),

    # ---- THE LAUNDERING HOLE ITSELF -----------------------------------------------------
    ("the Outside arm is removed, so colony goods are no longer proven ordinary", COMP,
     "            StampOrigin(OddOriginService.IsBackroomsMap(map)" + chr(10) +
     "                ? ThingOrigin.Backrooms : ThingOrigin.Outside);",
     "            if (OddOriginService.IsBackroomsMap(map)) { StampOrigin(ThingOrigin.Backrooms); }",
     1),

    ("a reloaded thing is restamped from wherever it happens to be", COMP,
     "if (respawningAfterLoad || origin != ThingOrigin.Unknown) { return; }",
     "if (origin != ThingOrigin.Unknown) { return; }", 1),

    # ---- merging and splitting ----------------------------------------------------------
    ("merging is refused in one direction only, so odd can absorb ordinary", COMP,
     "return IsOdd == OddOriginService.IsOdd(other);",
     "return !IsOdd || OddOriginService.IsOdd(other);", 1),

    ("a piece split off an odd stack is no longer odd", COMP,
     "if (split != null) { split.MarkOdd(); }", "if (split != null) { }", 1),

    ("the field becomes public, so any file could assign it", COMP,
     "private ThingOrigin origin;", "public ThingOrigin origin;", 1),

    ("the mark stops being saved, so a reload launders everything", COMP,
     'Scribe_Values.Look(ref origin, "rr_origin", ThingOrigin.Unknown);', "", 1),

    ("the 0.7.2-dev legacy mark is dropped, losing marks an early save earned", COMP,
     'Scribe_Values.Look(ref legacyOdd, "rr_oddOrigin", false);', "", 1),

    # ---- the service --------------------------------------------------------------------
    ("the service restamps something already proven to be from outside", SERVICE,
     "if (marker == null || marker.Origin != ThingOrigin.Unknown) { return false; }",
     "if (marker == null) { return false; }", 1),

    ("the generation pass starts marking pawns as goods", SERVICE,
     "if (thing == null || thing is Pawn) { continue; }",
     "if (thing == null) { continue; }", 1),

    ("the produced list is left in database order, which depends on the mod list", SERVICE,
     "produced.Sort(StringComparer.Ordinal);", "", 1),

    ("the comp is injected a second time", SERVICE,
     "definition.comps.Add(new CompProperties_RimroomsOddOrigin());",
     "definition.comps.Add(new CompProperties_RimroomsOddOrigin());" + chr(10) +
     "                definition.comps.Add(new CompProperties_RimroomsOddOrigin());", 1),

    # ---- the hole the row names, verbatim -----------------------------------------------
    #
    # **THE FIRST VERSION OF THIS PLANT WAS A COMMENT, SO IT TESTED NOTHING.** The proof strips
    # `//` comments before reading -- deliberately, because every file here names the hazard in
    # order to explain the guard -- so a planted comment was correctly ignored and the run
    # reported MISSED with the claim entirely innocent. *"One plant was wrong, not the claim"* is
    # recorded as a lesson from the last batch and this is the same mistake. It plants real code
    # now, in a real method body.
    ("A STAMP IS WRITTEN FROM OUTSIDE THE ECONOMY -- the row's own words", FOREIGN,
     "                if (tileId < 0 || Find.WorldGrid == null) { return false; }",
     "                if (tileId < 0 || Find.WorldGrid == null) { return false; }" + chr(10) +
     "                Tile.StampOrigin(RimroomsAsyncIndustries.Economy.ThingOrigin.Backrooms);",
     1),

    # ---- the readers --------------------------------------------------------------------
    ("supply contracts stop testing origin through the service", CONTRACTS,
     "OddOriginService.IsOdd(thing)", "true", 1),
]

caught = 0
attempted = 0
for label, path, old, new, want in PLANTS:
    attempted += 1
    original = io.open(path, encoding="utf-8").read()
    if original.count(old) < 1:
        print("PLANT SETUP BROKEN (0 matches for %r): %s" % (old[:55], label))
        sys.exit(2)
    _rr_mark(path, label)
    write_verified(path, original.replace(old, new, 1))
    _rr_unmark()
    try:
        code = subprocess.call([sys.executable] + PROOF,
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        write_verified(path, original)
        _rr_unmark()
    ok = code == want
    caught += 1 if ok else 0
    print("%s  %s (exit %d, wanted %d)"
          % ("CAUGHT " if ok else "MISSED!", label, code, want))

print("")
print("%d of %d planted faults caught" % (caught, attempted))
sys.exit(0 if caught == attempted else 1)
