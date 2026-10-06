# -*- coding: utf-8 -*-
"""Planted faults against the offer half of `.local/register/proof-request-generation.py`.

**That proof had no plant suite, and one of its claims had been enforcing a defect for its whole
life.** It asserted *"only one request is ever open"* against `OpenRequest != null`, which is
offered **or accepted** -- so it was holding in place the rule that a branch may hold exactly one
job, while the owner had asked for *"ability to accept more than one quests at a time"* and two
shipped features depended on it.

A green instrument over a defect is the failure this battery exists to end, and a claim nobody has
ever broken on purpose is a claim nobody has checked. So the restated claims get faults aimed at
them, including the one that is an absence: **the old open-or-accepted guard must not come back
looking like a tidy-up.**

**NEVER RUN A PLANT SUITE CONCURRENTLY WITH ANYTHING ELSE.**

Run from the repository root.
"""
import io
import os
import subprocess
import sys
import time

GENERATION = "src/RimroomsAsyncIndustries/Company/RequestGeneration.cs"
LINE = "src/RimroomsAsyncIndustries/Company/RequestLine.cs"

PROOF = ".local/register/proof-request-generation.py"

NL = chr(10)

PLANTS = [
    # ===================================== the restated offer guard, both directions
    ("THE OLD OPEN-OR-ACCEPTED GUARD COMES BACK, limiting a branch to one job again", GENERATION,
     "            if (OfferedRequest != null) { return; }",
     "            if (OpenRequest != null) { return; }", PROOF),

    ("the offer guard goes entirely, so the company asks two questions at once", GENERATION,
     "            if (OfferedRequest != null) { return; }", "", PROOF),

    # ===================================== the save-level half of the same rule
    ("THE VALIDITY COUNTER GOES BACK TO COUNTING OBLIGATIONS, invalidating any branch with two jobs",
     LINE, "                if (record.status == RequestStatus.Offered) { open++; }",
     "                if (record.Open) { open++; }", PROOF),

    ("the offer bound loosens, so a save may hold two questions", LINE,
     "            return open <= 1;", "            return open <= 2;", PROOF),

    # ===================================== the guards that were already right
    ("generated work arrives during the tutorial and competes with it", GENERATION,
     "            if (!PastTheHinge) { return; }", "", PROOF),

    ("a branch nobody has heard of gets client work", GENERATION,
     "            if (!corporationContact) { return; }" + NL,
     "", PROOF),

    ("A CLOCK COMES BACK, which chart 1.1 forbids outright", GENERATION,
     "            List<RimroomsRequestDef> eligible = EligibleFamilies();",
     "            if (nextRequestTick > 0) { return; }" + NL
     + "            List<RimroomsRequestDef> eligible = EligibleFamilies();", PROOF),

    ("the candidate list stops being sorted, so the same seed rolls differently per mod list",
     GENERATION, ".OrderBy(definition => definition.defName, System.StringComparer.Ordinal)",
     ".OrderBy(definition => definition.label)", PROOF),

    ("variety stops being least-asked-first and becomes whatever is first", GENERATION,
     "                int asked = TimesAsked(eligible[index].defName);",
     "                int asked = 0;", PROOF),
]

for _plant in PLANTS:
    if len(_plant) != 5:
        sys.stderr.write("PLANT LIST MALFORMED: %r has %d field(s), not 5\n"
                         % (_plant[0], len(_plant)))
        sys.exit(2)

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
    sys.stderr.write("FATAL: could not write %s -- CHECK BY HAND\n" % path)
    sys.exit(3)


print("baseline -- the verifier must pass before anything is planted")
for command in sorted(set(plant[4] for plant in PLANTS)):
    code = subprocess.call([sys.executable, command],
                           stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print("  exit %d  %s" % (code, command))
    if code != 0:
        sys.stderr.write("BASELINE BROKEN: %s already fails, so every plant against it would "
                         "register as caught and the run would prove nothing.\n" % command)
        sys.exit(2)
print("")

opening = dict((path, io.open(path, encoding="utf-8").read())
               for path in set(plant[1] for plant in PLANTS))

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
        write_verified(path, original)
        _rr_unmark()
    ok = code != 0
    caught += 1 if ok else 0
    print("%s  %s" % ("CAUGHT " if ok else "MISSED!", label))

print("")
for path, text in opening.items():
    if io.open(path, encoding="utf-8").read() != text:
        sys.stderr.write("%s IS NOT AS IT WAS FOUND -- CHECK BY HAND\n" % path)
        sys.exit(3)
if os.path.isfile(_RR_SENTINEL):
    sys.stderr.write("SENTINEL STILL PRESENT AT %s\n" % _RR_SENTINEL)
    sys.exit(3)
print("every touched file verified byte-identical to how it was found; no sentinel left behind")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
