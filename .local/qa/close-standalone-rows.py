# -*- coding: utf-8 -*-
"""Close the two dependency/stand-alone rows: the guarantee half is now proven, not asserted."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

CLOSED = [
 ('- [ ] **"rework mod to not need any depeancie mods"**',
  'CLOSED 0.12.95-dev — **THE GUARANTEE HALF IS NOW PROVEN RATHER THAN ASSERTED, and the row named '
  'the exact thing that was missing.** Its words: *"Removing a declaration does not make absence '
  'safe; it only stops advertising. What has to be proven, row by row, is that the Core-only path '
  '**runs**: every by-name `GetNamedSilentFail` lookup degrades rather than returning null into a '
  'dereference."* '
  '`check-standalone-guarantee.py` already proved the package **names** only safe things — 214 '
  'packaged def references, 14 expansion-gated, 64 C# lookups, 5 expansion ones all through '
  '`GetNamedSilentFail`, 4 assembly references all game or Unity. **None of that proved the '
  'lookups degrade.** A silent-fail returning null is the *designed* outcome on a Core-only '
  'install; dereferencing it a line later is a `NullReferenceException` at the exact moment the '
  'guarantee is supposed to hold, and the player sees a red error instead of a feature quietly '
  'not being there. '
  '**It is now checked, and the answer is clean: 152 silent-fail results, every one degrading.** '
  'A `== null` guard, a `??` fallback or a `?.` — all three idioms, because C# has three and a '
  'rule knowing two cries wolf at the third. '
  '**The rule was wrong three times before it was right, and every narrowing was earned:** it '
  'first demanded every result be assigned or guarded and reported **65 findings, 56 of them '
  'innocent** — passing null as an argument and returning null are both perfectly safe, and the '
  'only real hazard is a member access on the result. Then a six-line guard window reported **9 '
  'more on correct code**, because `GenStep_BackroomsDestination` looks up **eleven** Core defs in '
  'a block and guards all eleven in one combined `if` about forty lines below the first — a better '
  'shape than eleven separate guards, and a rule demanding adjacency was demanding worse code. '
  'Then two sites turned out safe through `??`. **Sixty-five false findings would have been a rule '
  'nobody believes**, which protects nothing. '
  '**Proved able to refuse:** a planted unguarded dereference makes it fail, and a plant that '
  'removes `??` from the recogniser makes it report correct code — both now permanent in '
  '`plant-standalone-and-grants.py`, **25 of 25**, every target verified byte-identical afterwards. '
  'The remaining halves of the row were already enforced: `check-dlc-gating.py` for per-entry '
  '`MayRequire`, and `PatchOperationFindMod`/`Conditional` guarding, asserted there.'),

 ('- [ ] **"im reiterating the fact that we need to fix the depancy list so that its accurate to what is required',
  'CLOSED 0.12.95-dev, BOTH HALVES. The row is a **reiteration**, kept because LAW #0 does not let '
  'a repeat be dropped, and it adds the goal in plain words: *"a complete stand-alone mod"*. '
  '**The declaration half was already true and is now also true in the documents.** `About.xml` '
  'has declared **zero** `modDependencies` since 0.12.86-dev — but five live documents were still '
  'telling players the opposite, including `About.xml`’s **own description**, the install page, the '
  'mods page, the README and `PLAYING.md`. All five corrected at 0.12.95-dev and the rule is '
  'enforced in three places, so *"accurate to what is required"* is now accurate everywhere a '
  'reader looks. '
  '**The guarantee half closed with the row above:** 152 silent-fail lookups, every one proven to '
  'degrade. Together those are the whole of the reiteration — the list says what is true, and the '
  'Core-only path is proven to run rather than merely declared to.'),
]

text = io.open(TODO, encoding="utf-8").read()
problems = 0
for anchor, evidence in CLOSED:
    found = text.count(anchor)
    if found != 1:
        print("ANCHOR NOT UNIQUE (%d): %s" % (found, anchor[:85]))
        problems += 1
        continue
    at = text.index(anchor)
    line_end = text.index(NL, at)
    row = "- [x] " + text[at:line_end][len("- [ ] "):]
    text = text[:at] + row + " — **" + evidence + "**" + text[line_end:]
if problems:
    print("%d row(s) not touched; nothing written" % problems)
    sys.exit(1)
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text)
print("closed %d rows" % len(CLOSED))
