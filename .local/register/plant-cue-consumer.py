# -*- coding: utf-8 -*-
"""Plant the failures check-wiring.py must catch about shipped content nothing reads.

A rule satisfied by its subject not being there is not a rule, and this one was satisfied three
different ways at once. Measured 2026-10-06: **five of the seventeen shipped sound cues had no
consumer anywhere** -- `RR_AnalysisComplete`, `RR_ContractPaid`, `RR_CutoffThrown`,
`RR_JournalFiled`, `RR_MarkerSet`, the whole of `ASSET_REQUESTS.md`'s *"events that happen now and
make no sound"* band. Delivered, described on the published asset page, given SoundDefs, never
played. Every instrument was green.

Three holes had to close before a single planted fault was caught, and **the first two were only
found because this plant stayed green after each fix**:

  1. `SoundDef` sat in `CORE_CONSUMED`, which declared every cue wired by existing.
  2. Rule 3 asked whether a name appears "somewhere OTHER than its own declaration" by counting
     occurrences in all def XML and testing `> 1` -- and every cue's own block names itself twice,
     as `<defName>` and as the `<clipPath>` of the identically-named file. Each cue cross-referenced
     itself.
  3. `enumerated` matched `DefDatabase<T>` anywhere, so `DefDatabase<SoundDef>.GetNamedSilentFail`
     counted as *this type is enumerated*. A by-name lookup on a variable proves the opposite.

The faults below are the realistic shapes of reopening each: a cue's only call site renamed, and the
two loopholes restored as the plausible-looking simplifications they were.
"""
import io
import os
import subprocess
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.chdir(REPO)

CHECKER = ["tools/check-wiring.py"]

SRC = "src/RimroomsAsyncIndustries"
MARKERS = SRC + "/Investigation/RouteMarkers.cs"
SETTLEMENT = SRC + "/Company/EvidenceSettlement.cs"
WIRING = "tools/check-wiring.py"

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
    # ---- a shipped cue loses its only consumer -------------------------------------------
    # The realistic edit: a cue id retyped during a rename, or a call site deleted with the
    # feature around it. The cue keeps its SoundDef and its row on the published asset page.
    ("A SHIPPED CUE LOSES ITS ONLY CALL SITE, so RR_MarkerSet ships and never plays",
     MARKERS, 'Audio.RimroomsAudio.Play("RR_MarkerSet"',
     'Audio.RimroomsAudio.Play("RR_PlantedCueThatDoesNotExist"', 1),

    # A second cue, in a different subsystem, so the rule is not accidentally specific to one file.
    ("A SECOND CUE LOSES ITS ONLY CALL SITE, this one in evidence settlement",
     SETTLEMENT, 'Audio.RimroomsAudio.Play("RR_JournalFiled"',
     'Audio.RimroomsAudio.Play("RR_PlantedCueThatDoesNotExist"', 1),

    # ---- WHY THE THREE LOOPHOLES ARE NOT PLANTED SEPARATELY ------------------------------
    #
    # The first draft of this suite planted each of them: SoundDef back into `CORE_CONSUMED`, the
    # `> 1` count back in place of the subtraction, and the short `DefDatabase<T>` regex back in
    # place of `AllDefs`. **All three were reported MISSED, and the suite was wrong rather than the
    # checker.** Loosening a rule on a tree where every cue is already wired correctly fails
    # nothing: there is no orphan for the loosened rule to miss.
    #
    # **The two plants above already guard all three**, which is the better arrangement anyway.
    # Reopen any one loophole and `RR_MarkerSet` with its call site renamed stops being reported --
    # so the regression surfaces as those plants turning MISSED, pointing at the cue rather than at
    # a line of the checker. A plant whose claim is "a weaker rule still catches a fault that is not
    # there" asserts something untrue and would have to be deleted the first time anyone read it.
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
        code = subprocess.call([sys.executable] + CHECKER,
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        write_verified(path, original)
        _rr_unmark()
    ok = code == 1
    caught += 1 if ok else 0
    print("%s  %s (exit %d, wanted 1)" % ("CAUGHT " if ok else "MISSED!", label, code))

print("")
print("%d of %d planted faults caught" % (caught, attempted))
sys.exit(0 if caught == attempted else 1)
