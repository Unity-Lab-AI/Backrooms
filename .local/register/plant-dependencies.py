# -*- coding: utf-8 -*-
"""Planted faults against the re-aimed dependency rule in `check-register-compliance.py`.

Why this suite exists
---------------------
Owner direction, 2026-10-01, verbatim: *"see thats WRONG the mod DOES HAVE HARD DEPENDANCIES SO
GET IT RIGHT AND MAKE SURE ITS LAYED OUT RIGHT FOR RIMSORT TO NOTICE AND ENFORCE"*, and when
asked which ones: *"there are alot more depeandacies than just the DLC we have alkinds of mods in
the 274 mod list WE ARE USING ALL OF THEM!!!!"*.

`check-register-compliance.py` carried the rule *"About.xml must declare no modDependencies; the
package has to load and run against Core alone."* That premise is overruled. **A prohibition was
replaced by an assertion, and an assertion is worth exactly what its ability to fail is worth** --
so this plants one fault per branch of the new rule.

The branch that matters most is **a dependency required but never ordered**. Our mod sat at
**position 197 of 296** in the owner's live load order with **99 mods loading after it**, and a
`modDependencies` entry with no matching `loadAfter` reproduces exactly that: required, and still
loaded too early to see the defs it requires.

**The first draft of this suite used `(name, function)` tuples and
`tools/check-plant-anchors.py` refused all seven as malformed.** It was right: the house shape is
`(label, target, anchor, replacement, verifier)` precisely so a seventeenth instrument can read
every anchor and say which have gone stale. A suite the battery cannot inspect is a suite that
rots silently.

Run from the repository root.
"""
import io
import os
import subprocess
import sys
import time

ABOUT = "Mod/Rimrooms - Async Industries/About/About.xml"
REGISTER = "tools/check-register-compliance.py"

# The first dependency row in the generated block, used as the handle for several plants. It is
# Harmony because the owner's load order puts `brrainz.harmony` first.
FIRST = (u"    <li>" + chr(10)
         + u"      <packageId>brrainz.harmony</packageId>" + chr(10)
         + u"      <displayName>Harmony</displayName>" + chr(10)
         + u"      <steamWorkshopUrl>steam://url/CommunityFilePage/2009463077</steamWorkshopUrl>"
         + chr(10) + u"    </li>")

SELF_ROW = (u"    <li>" + chr(10)
            + u"      <packageId>Rimrooms.AsyncIndustries</packageId>" + chr(10)
            + u"      <displayName>Rimrooms - Async Industries</displayName>" + chr(10)
            + u"      <steamWorkshopUrl>steam://url/CommunityFilePage/1</steamWorkshopUrl>"
            + chr(10) + u"    </li>" + chr(10))

CORE_ROW = (u"    <li>" + chr(10)
            + u"      <packageId>Ludeon.RimWorld</packageId>" + chr(10)
            + u"      <displayName>RimWorld</displayName>" + chr(10)
            + u"    </li>" + chr(10))

PLANTS = [
    # ------------------------------------------- the position-197 defect, planted back in
    ("A DEPENDENCY IS REQUIRED AND NEVER ORDERED", ABOUT,
     u"    <li>brrainz.harmony</li>" + chr(10), u"", REGISTER),

    ("loadAfter stops naming Core at all", ABOUT,
     u"    <li>Ludeon.RimWorld</li>" + chr(10), u"", REGISTER),

    # ------------------------------------------- a declaration a manager cannot act on
    ("A DEPENDENCY CARRIES NO NAME TO SHOW THE PLAYER", ABOUT,
     u"      <displayName>Harmony</displayName>" + chr(10), u"", REGISTER),

    ("a dependency gives the player no way to obtain it", ABOUT,
     u"      <steamWorkshopUrl>steam://url/CommunityFilePage/2009463077</steamWorkshopUrl>"
     + chr(10), u"", REGISTER),

    # ------------------------------------------- declarations that are nonsense on their face
    ("the package is declared as its own dependency", ABOUT,
     FIRST, SELF_ROW + FIRST, REGISTER),

    ("Core is declared as a mod dependency", ABOUT,
     FIRST, CORE_ROW + FIRST, REGISTER),

    ("the same dependency is declared twice", ABOUT,
     FIRST, FIRST + chr(10) + FIRST, REGISTER),
]


# **THE RESTORE DOES NOT SURVIVE THE PROCESS BEING KILLED.** `finally` handles an exception and
# does nothing for a killed sweep, which is how a planted fault reached the working tree four
# times. **ONE SENTINEL PER SUITE, named after the suite**, because all sixteen once shared a
# single path and a later suite's unmark erased an earlier suite's failure record.
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
    """Write and do not believe it until it reads back identical.

    About.xml carries a BOM. Reading and writing both as plain `utf-8` keeps the BOM as the
    leading character of the string, so the round trip is byte-identical -- which is the property
    the final comparison in this suite depends on.
    """
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


print("baseline -- the target must pass before anything is planted")
for command in sorted(set(plant[4] for plant in PLANTS)):
    code = subprocess.call([sys.executable, command],
                           stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print("  exit %d  %s" % (code, command))
    if code != 0:
        sys.stderr.write("BASELINE BROKEN: %s already fails, so every plant against it would "
                         "register as caught and the run would prove nothing.\n" % command)
        sys.exit(2)
print("")

opening = io.open(ABOUT, encoding="utf-8").read()

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
        # **The restore is the one line that must always run**, and the sentinel is held until
        # after it rather than cleared straight after the write -- so an interruption *during the
        # verifier* is still visible to `tools/check-plant-residue.py`.
        write_verified(path, original)
        _rr_unmark()
    ok = code != 0
    caught += 1 if ok else 0
    print("%s  %s" % ("CAUGHT " if ok else "MISSED!", label))

print("")
if io.open(ABOUT, encoding="utf-8").read() != opening:
    sys.stderr.write("ABOUT.XML IS NOT AS IT WAS FOUND -- CHECK BY HAND\n")
    sys.exit(3)
if os.path.isfile(_RR_SENTINEL):
    sys.stderr.write("SENTINEL STILL PRESENT AT %s\n" % _RR_SENTINEL)
    sys.exit(3)
print("About.xml verified byte-identical to how it was found; no sentinel left behind")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
