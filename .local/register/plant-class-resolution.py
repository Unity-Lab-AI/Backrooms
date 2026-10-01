# -*- coding: utf-8 -*-
"""Plant the seventh launch's defect and require the new check to refuse the package.

Plant a fault, run the target, require failure, restore. Verified writes. Clean run first.

The headline plant is **the exact line that cost the launch**, replanted verbatim:

    <li Class="CompProperties_Colorable" />

The rest are the same defect wearing different clothes, plus the two plants that matter most
after the first draft of this fix FAILED CORRECT CODE: the resolver must not be satisfiable by
being blinded, and it must not be satisfiable by being made always-true. Both of those are
invisible to a text-reading proof, which is why `proof-class-resolution.py` executes the
resolver instead of reading it.
"""
import io
import os
import subprocess
import sys
import time

INTEGRITY = "tools/check-package-integrity.py"
PROOF = ".local/register/proof-class-resolution.py"
PATCH = "Mod/Rimrooms - Async Industries/1.6/Patches/RR_NativeGateProviders.xml"
GENSTEP = "Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsCoordinateDefs/RR_Coordinates.xml"

COLORABLE = "          <li>\n            <compClass>CompColorable</compClass>\n          </li>"

# (label, path, old, new, target)

# **THE RESTORE DOES NOT SURVIVE THE PROCESS BEING KILLED.** `finally` handles an exception; it
# does nothing for an interrupted sweep, and that is how a planted fault reached the working tree
# for the third time. The sentinel makes it visible: `tools/check-plant-residue.py` refuses while
# this file exists and prints the path to restore.
# **ONE SENTINEL PER SUITE, named after the suite.** All sixteen shared a single path, so when
# `plant-containment.py` left one behind after a failed restore, the next suite's `_rr_unmark()`
# deleted it -- and `check-plant-residue.py` reported a clean tree with a planted fault in it.
# Fourth instance of residue reaching the tree and the first the sentinel could not see.
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


def _rr_restore(path, original):
    """Put the file back, and do not believe it until it reads back identical.

    The failure this exists for was transient -- `OSError: [Errno 22]` on a path this same loop
    had already written twice -- so a retry turns it into a non-event. A restore that still will
    not verify raises with the sentinel left in place, which is what stops the sweep from planting
    the next fault on top of this one.
    """
    last = None
    for attempt in range(5):
        try:
            io.open(path, "w", encoding="utf-8", newline="").write(original)
            if io.open(path, encoding="utf-8").read() == original:
                return
            last = "the file read back different from what was written"
        except (OSError, IOError) as error:
            last = repr(error)
        time.sleep(0.25 * (attempt + 1))
    raise RuntimeError("RESTORE FAILED for %s after 5 attempts: %s. The sentinel %s is left in "
                       "place; tools/check-plant-residue.py will refuse until the file is "
                       "restored." % (path, last, _RR_SENTINEL))


PLANTS = [
    ("THE SEVENTH-LAUNCH DEFECT, REPLANTED VERBATIM: Class=\"CompProperties_Colorable\"",
     PATCH, COLORABLE, '          <li Class="CompProperties_Colorable" />', INTEGRITY),

    ("a British spelling of the same absent type", PATCH,
     COLORABLE, '          <li Class="CompProperties_Colourable" />', INTEGRITY),

    ("a compClass naming a type the game does not have", PATCH,
     "<compClass>CompColorable</compClass>", "<compClass>CompColorableThing</compClass>",
     INTEGRITY),

    ("a namespaced Core type that does not exist", PATCH,
     COLORABLE, '          <li Class="Verse.CompProperties_Colorable" />', INTEGRITY),

    ("the glower is mis-spelled, which the old check also waved through", PATCH,
     'Class="CompProperties_Glower"', 'Class="CompProperties_Glow"', INTEGRITY),

    # The pre-existing half must still work, so it is planted too rather than assumed.
    ("one of OUR OWN types is named that no C# file declares", PATCH,
     "RimroomsAsyncIndustries.Portals.CompProperties_RimroomsEmergence",
     "RimroomsAsyncIndustries.Portals.CompProperties_RimroomsEmergenceGate", INTEGRITY),

    # ------------------------------------------------------------------ the resolver itself
    # These two are the reason the proof executes the resolver. A blinded or always-true
    # resolver reports a clean package while checking nothing, and no amount of reading the
    # source can tell the difference.
    ("THE RESOLVER IS BLINDED and reports no game assemblies at all", INTEGRITY,
     "    blobs = []", "    blobs = []\n    paths = []", PROOF),

    ("THE RESOLVER IS MADE ALWAYS-TRUE", INTEGRITY,
     "    return needle in heaps", "    return True or needle in heaps", PROOF),

    ("the resolver loses suffix awareness, the way the first draft of this fix did", INTEGRITY,
     "    return needle in heaps",
     "    return simple.encode('utf-8') in heaps.split(b'\\0')", PROOF),

    ("the exemption that caused all of this is restored", INTEGRITY,
     "        if game_types is None:\n            continue\n        if not type_name_exists(",
     "        if True:\n            continue\n        if not type_name_exists(", PROOF),
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
for target in (INTEGRITY, PROOF):
    code = run(target)
    print("  %-46s exit %d" % (target, code))
    if code != 0:
        print("ABORTED: %s does not pass clean" % target)
        sys.exit(2)
print("")

caught = 0
for label, path, old, new, target in PLANTS:
    original = io.open(path, encoding="utf-8").read()
    hits = original.count(old)
    if hits != 1:
        print("PLANT SETUP BROKEN (%d matches, need exactly 1): %s" % (hits, label))
        sys.exit(2)
    _rr_mark(path, label)
    write_verified(path, original.replace(old, new, 1))
    _rr_unmark()
    try:
        code = run(target)
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
