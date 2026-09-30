# -*- coding: utf-8 -*-
"""Assert that a value with a read site actually has an EFFECT.

The property this exists for
----------------------------
Invariant 136, written at 0.11.6-dev after three research unlocks were deleted for moving numbers
no player could observe:

    A live read site is not a live effect.

`proof-research-branches.py` asserts that every capability a project grants is read by real code.
It cannot see one level further in, and that is exactly where the next bug was:

    public float MinimumPowerHeadroomWatts   // reads the prop, applies RR_Cap_ReserveDiscipline
    { get { ... } }                          // and was itself READ BY NOTHING

So the tier 0 Facilities project promised *"the gate needs less spare headroom above its draw
before it will open"* and changed nothing observable. The capability was read. The reader was dead.

This walks the gate comp's own exposed surface and insists every member of it is consulted
somewhere else. It is the sweep that would have caught it, and the sweep is the method -- finding
dead values one at a time produces both false negatives and false positives (invariant 132).

Run from the repository root.
"""
import glob
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
GATE = os.path.join(SRC, "Gate")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


sources = {}
for path in sorted(glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True)):
    rel = os.path.relpath(path, REPO).replace(os.sep, "/")
    sources[rel] = io.open(path, encoding="utf-8-sig").read()
everything = "\n".join(sources.values())

gate_sources = {rel: text for rel, text in sources.items() if "/Gate/" in rel}
gate_text = "\n".join(gate_sources.values())


def strip_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return "\n".join(line for line in text.splitlines()
                     if not line.lstrip().startswith("//"))


code = {rel: strip_comments(text) for rel, text in sources.items()}
code_all = "\n".join(code.values())

# --------------------------------------------------------------------------- the exposed surface
# Public properties on the gate comp that exist to expose a tuned value. Only ones whose body
# mentions GateProps, because those are the props-with-an-opinion this is about.
#    The first version of this used one regex with a brace-nesting limit and matched NOTHING --
#    a property body is `{ get { ... } }`, which is two levels deep. It reported "0 exposed
#    properties" and passed every per-property claim by having none to check, which is a proof
#    that fails OPEN (invariant 152). Now it finds declarations and reads the window after each,
#    which cannot silently match zero.
DECL = re.compile(r"public\s+(?:float|int|bool|string)\s+(\w+)\s*\{")
exposed = []
matches = list(DECL.finditer(gate_text))
for position, match in enumerate(matches):
    start = match.end()
    finish = matches[position + 1].start() if position + 1 < len(matches) else len(gate_text)
    if "GateProps." in gate_text[start:finish]:
        exposed.append(match.group(1))
exposed = sorted(set(exposed))

print("gate sources            : %d" % len(gate_sources))
print("exposed tuned properties: %d" % len(exposed))
print("")

check("the gate comp exposes tuned properties", len(exposed) > 0)

for name in exposed:
    # A read is any mention outside its own declaration line. Counted over comment-stripped
    # source so a doc comment explaining the value cannot masquerade as a use.
    uses = len(re.findall(r"\b" + re.escape(name) + r"\b", code_all))
    declarations = len(re.findall(r"public\s+(?:float|int|bool|string)\s+" + re.escape(name) + r"\b",
                                  code_all))
    check("%s is consulted somewhere (%d use(s) beyond %d declaration(s))"
          % (name, uses - declarations, declarations),
          uses - declarations >= 1,
          "-- exposed, tuned, and read by nothing: a value with no effect")

# --------------------------------------------------------------------------- the supply requirement
# Owner answer, 2026-09-29: reserveChargePowerWatts is "A supply requirement before opening".
print("")
comp = code.get("src/RimroomsAsyncIndustries/Gate/CompRimroomsGate.cs", "")
binding = code.get("src/RimroomsAsyncIndustries/Gate/NativeGateBinding.cs", "")

check("the opening supply check exists",
      "ProjectedOpeningPowerFailure()" in comp,
      "-- nothing consumes reserveChargePowerWatts")
check("it requires generation to meet reserveChargePowerWatts",
      re.search(r"generation < GateProps\.reserveChargePowerWatts", comp) is not None,
      "-- the owner's answer was a supply requirement before opening")
check("it requires headroom above the current draw",
      re.search(r"generation < CurrentPowerDrawWatts \+ MinimumPowerHeadroomWatts", comp) is not None,
      "-- MinimumPowerHeadroomWatts goes back to being read by nothing")
check("generation counts production, not stored charge",
      "PowerOutput" in binding and "StoredEnergy" not in
      (re.search(r"private float NativeGenerationWatts\(\).*?\n        \}", binding, re.S)
       or type("x", (), {"group": lambda self, n: ""})()).group(0),
      "-- a battery is a buffer, not supply")

# THE safety claim. This gates OPENING only. Wiring it into the binding failure key would make a
# generation dip emergency-return a crew that is already through, and the chart's clock rules say
# a lapse blocks the NEXT opening, never the current one.
check("the supply check is not part of the live binding failure key",
      "ProjectedOpeningPowerFailure" not in binding,
      "-- a generation dip would emergency-return a crew that is already across")
check("the supply check is consulted exactly once",
      len(re.findall(r"ProjectedOpeningPowerFailure\(\)", comp)) == 2,
      "-- one declaration and one call site is the whole intent")

# --------------------------------------------------------------------------- the revived capability
check("RR_Cap_ReserveDiscipline is still read",
      'HasCapability("RR_Cap_ReserveDiscipline")' in comp,
      "-- the tier 0 Facilities project would promise an unlock again and deliver none")
check("the property it modifies is now consulted",
      "MinimumPowerHeadroomWatts" in comp and
      len(re.findall(r"\bMinimumPowerHeadroomWatts\b", code_all)) >= 2,
      "-- the capability would be read by a reader that is itself dead")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: every tuned value the gate exposes is consulted by something")
