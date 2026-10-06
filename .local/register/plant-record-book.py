# -*- coding: utf-8 -*-
"""Planted faults against `proof-record-book.py`, which had none.

**Thirty-four claims and nobody had ever watched one fail.** The proof shipped with the recorder
fold and passed from the day it was written, which is exactly the condition that makes a proof
decorative: a claim nobody has seen refuse is indistinguishable from a comment that agrees with
itself.

The row this closes was one line: *"NEXT: build the recorder fold. Four live read sites move onto
the book."* It came from the decision *"the book is the recorder. One Core `TextBook`: carried in
blank, written in the field, carried home as the evidence. lose the book, lose the run."*

Three of these plants are the ones worth naming:

* **One of the four read sites drifts.** `RecorderGap` is handled in two switches, raised in one
  place and read in a fourth; removing a single `case` leaves an observation that is **stored and
  never surfaces**. Nothing throws, nothing logs, and an expedition quietly stops noticing a
  missing book.
* **The literal instead of the constant.** `"recorder_gap"` typed at a call site works until
  somebody types `"recorder-gap"`, and then one site silently stops matching the other three.
* **A recipe that produces a recorder.** The whole point is that the book is Core's `TextBook` and
  nothing hands one out; a recipe would reintroduce the thing the fold removed.
"""
import io
import os
import subprocess
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.chdir(REPO)

PROOF = [".local/register/proof-record-book.py"]

SRC = "src/RimroomsAsyncIndustries"
OBS = SRC + "/Company/EvidenceObservations.cs"
SITE = SRC + "/Threats/FirstSliceSiteComponent.cs"
REQUEST = SRC + "/Company/RequestLine.cs"
CARGO = SRC + "/Expedition/ExpeditionCargo.cs"
COMP = SRC + "/Investigation/CompRouteEvidence.cs"
MOD = "Mod/Rimrooms - Async Industries/1.6"
# **`RR_FieldEquipment.xml` IS GONE AS OF 0.13.0-dev** and both of the defs it held moved. The
# recorder is a building in `RR_FieldKit.xml`; the route recording became the company journal in
# `RR_CompanyJournal.xml`, which also resolved a duplicate defName that file had been shipping.
KIT = MOD + "/Defs/ThingDefs_Buildings/RR_FieldKit.xml"
JOURNAL = MOD + "/Defs/ThingDefs_Items/RR_CompanyJournal.xml"
KEYED = MOD + "/Languages/English/Keyed/RR_Expedition.xml"

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


def read_bytes(path):
    return io.open(path, "rb").read()


def write_verified(path, data):
    """Bytes in, bytes out, verified. A byte-order mark is part of a file and must survive."""
    for _ in range(6):
        try:
            io.open(path, "wb").write(data)
            if read_bytes(path) == data:
                return
        except OSError:
            pass
        time.sleep(0.4)
    sys.stderr.write("FATAL: could not write %s -- CHECK BY HAND%s" % (path, chr(10)))
    sys.exit(3)


PLANTS = [
    # ---- the four read sites, one at a time ---------------------------------------------
    ("ONE OF TWO SWITCH CASES DRIFTS, so the observation is stored and never surfaces", OBS,
     "                case EvidenceObservationKinds.RecorderGap:",
     "                case EvidenceObservationKinds.RecorderGapUnused:", 1),

    ("the site tick stops noticing a missing book", SITE,
     "EvidenceObservationKinds.RecorderGap", "EvidenceObservationKinds.RouteMismatch", 1),

    ("the request line stops treating it as a finding", REQUEST,
     "observationKind == EvidenceObservationKinds.RecorderGap",
     "observationKind == EvidenceObservationKinds.RouteMismatch", 1),

    ("the declared constant becomes a literal typed at the call site", OBS,
     'public const string RecorderGap = "recorder_gap";',
     'public const string RecorderGap = "recorder-gap";', 1),

    # ---- the book is Core's, and nothing hands one out ----------------------------------
    # **RE-AIMED: the def moved file, and the claim is unchanged.** Something in a saved game and in
    # `FailedSiteRecovery`'s required-content list must keep resolving, wherever it is declared.
    ("the recorder def stops being declared", KIT,
     "RR_FieldRecorder", "RR_FieldRecorderGone", 1),

    # **THIS CLAIM IS GONE, AND IT IS RESTATED HERE RATHER THAN QUIETLY DELETED.** It was *"the
    # recorder becomes tradeable"*, planting against `<tradeability>None</tradeability>` -- the
    # rule being that a superseded item must stay untradeable, unbuilt and ungranted so nothing
    # tells a player to go and use one. **The owner overruled it on 2026-10-06** by answering
    # "Build the three items, hold the Pursuer": the recorder is live, buildable and useful, so a
    # rule demanding it stay unobtainable is a rule about a decision that was reversed. A green
    # instrument over a dead restraint is worse than no instrument.
    #
    # What replaces it is the claim that now matters, and it is stricter: **the journal must carry
    # the component the whole evidence pipeline reads.** Without it `CompanyCarrierDef` silently
    # returns null and every caller falls back to Core's textbook forever -- working software,
    # wrong book, no error anywhere.
    ("the company journal loses the route evidence component", JOURNAL,
     'li Class="RimroomsAsyncIndustries.Investigation.CompProperties_RouteEvidence"',
     'li Class="RimroomsAsyncIndustries.Investigation.CompProperties_RouteEvidenceGone"', 1),

    # ---- the carrier predicate ----------------------------------------------------------
    # **AIMED AT THE PROPERTY.** The first version renamed the declaration, which neither
    # breaks the reference in ExpeditionCargo nor clears a word-boundary test -- and
    # `NativeCarrierDefUnused` contains the name anyway. What the claim protects is the Core
    # provenance test: without it, ANY mod's TextBook passes as company gear.
    ("THE CARRIER STOPS REQUIRING CORE PROVENANCE, so any mod's book is company gear", COMP,
     "IsCoreMod", "IsAnyMod", 1),

    ("the carrier stops requiring exactly one of our comps", COMP,
     "OfType<CompProperties_RouteEvidence>().Count() == 1",
     "OfType<CompProperties_RouteEvidence>().Count() >= 0", 1),

    # Same correction: the claim is about refusing on null, not about a constant's name. A
    # silent null makes the kit check pass for a crew carrying nothing.
    # **RE-AIMED AND RENAMED 0.13.0-dev.** The kit counted a single def and refused on a null one;
    # it counts every accepted record book now -- Core's and the company's own journal -- and
    # refuses when the set is empty. **The claim is identical and the word NULL had stopped being
    # true**, which is the kind of name that makes a reader trust a rule that is testing something
    # else. The anchor matches twice, in CheckKit and in QueueLoadout; the first is CheckKit, which
    # is the one this claim reads.
    ("THE KIT CHECK STOPS REFUSING WHEN NO RECORD BOOK RESOLVES, so a crew carrying nothing passes",
     CARGO, "if (books.Count == 0)", "if (false)", 1),

    # **AIMED INSIDE QueueLoadout.** `GetStatValue(StatDefOf.Mass)` appears four times in this
    # file and the harness replaces the first, which is in a different method -- so the first
    # version planted somewhere the claim does not read and reported MISSED on an innocent claim.
    # This anchor is the loadout's own line, and it is unique.
    ("the loadout takes its mass from a constant instead of the item", CARGO,
     "float mass = Math.Max(0.001f, item.GetStatValue(StatDefOf.Mass));",
     "float mass = Math.Max(0.001f, 1f);", 1),

    # ---- the refusal a player actually reads --------------------------------------------
    ("the refusal loses its keyed string, so a player sees an identifier", KEYED,
     "<RR_Exp_MissingRecordBook>", "<RR_Exp_MissingRecordBookUnused>", 1),
]

caught = 0
attempted = 0
for label, path, old, new, want in PLANTS:
    attempted += 1
    original = read_bytes(path)
    needle = old.encode("utf-8")
    if original.count(needle) < 1:
        print("PLANT SETUP BROKEN (0 matches for %r): %s" % (old[:55], label))
        sys.exit(2)
    _rr_mark(path, label)
    write_verified(path, original.replace(needle, new.encode("utf-8"), 1))
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
