"""Plant suite for the archived-queue scoping of check-doc-conformance rule 6.

A rule that was just widened has to be shown to still refuse the thing it exists
to refuse, and to actually use its new escape. Four plants:

  1. An owner direction quoted in FINALIZED.md as a blockquote, placed OUTSIDE
     every archived-queue region and absent from TODO.md  -> MUST FAIL.
     This is the original defect: acted on, archived, never queued.
  2. The same direction placed INSIDE an archived-queue region               -> MUST PASS.
     This is the new escape. If this plant fails, the escape is dead code.
  3. The begin/end markers removed while an archived direction relies on them
                                                                             -> MUST FAIL.
     Proves the regions are load-bearing rather than decorative.
  4. The unplanted tree                                                      -> MUST PASS.

Every plant writes a sentinel naming the file it is about to mutate, and removes
it only after restoring, so `check-plant-residue.py` refuses while a planted
fault is still in the tree.
"""

import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
FINALIZED = os.path.join(REPO, "docs", "FINALIZED.md")
SENTINEL = os.path.join(HERE, ".plant-archived-queue-scope.active")
CHECKER = os.path.join(REPO, "tools", "check-doc-conformance.py")

# Long enough to clear MIN_QUOTE_CHARS, and nowhere in either ledger already.
PLANT = ('> *"plant suite only, a direction that was never written into the working '
         'queue at all"*')

BEGIN = "<!-- archived-queue:begin -->"
END = "<!-- archived-queue:end -->"


def run_checker():
    done = subprocess.run([sys.executable, CHECKER], cwd=REPO,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return done.returncode, done.stdout.decode("utf-8", "replace")


def read():
    return io.open(FINALIZED, encoding="utf-8").read()


def write(text):
    io.open(FINALIZED, "w", encoding="utf-8", newline="").write(text)


def plant(name, mutate, expect_fail):
    original = read()
    io.open(SENTINEL, "w", encoding="utf-8").write("docs/FINALIZED.md\n")
    try:
        write(mutate(original))
        code, output = run_checker()
    finally:
        write(original)
        os.remove(SENTINEL)
    failed = code != 0
    verdict = "OK" if failed == expect_fail else "WRONG"
    print("  %-4s %-62s checker %s" % (verdict, name, "FAILED" if failed else "PASSED"))
    if verdict == "WRONG":
        print("       expected the checker to %s" % ("FAIL" if expect_fail else "PASS"))
        tail = [line for line in output.split("\n") if line.strip()][-4:]
        for line in tail:
            print("       | %s" % line)
    return verdict == "OK"


def outside_region(text):
    """Append the direction after the last archived-queue region."""
    return text.rstrip("\n") + "\n\n" + PLANT + "\n"


def inside_region(text):
    """Insert the direction just before the last archived-queue end marker."""
    cut = text.rindex(END)
    return text[:cut] + PLANT + "\n\n" + text[cut:]


def inside_region_markers_stripped(text):
    """The direction inside what WAS a region, with the markers taken away."""
    planted = inside_region(text)
    return planted.replace(BEGIN, "<!-- marker removed by plant -->") \
                  .replace(END, "<!-- marker removed by plant -->")


print("plant-archived-queue-scope")
code, _output = run_checker()
print("  %-4s %-62s checker %s" % ("OK" if code == 0 else "WRONG",
                                   "4. unplanted tree", "PASSED" if code == 0 else "FAILED"))
results = [code == 0]
results.append(plant("1. direction outside every region, absent from the queue",
                     outside_region, expect_fail=True))
results.append(plant("2. same direction inside an archived-queue region",
                     inside_region, expect_fail=False))
results.append(plant("3. inside a region whose markers were removed",
                     inside_region_markers_stripped, expect_fail=True))

print()
print("  %d of %d plants behaved correctly" % (sum(results), len(results)))
if not all(results):
    sys.exit(1)
print("PROOF HELD")
