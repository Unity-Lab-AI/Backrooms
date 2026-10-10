# -*- coding: utf-8 -*-
"""0.12.55-dev: one line in one patch file deleted `Door` from RimWorld."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

ROW = u"""## Seventh launch findings — 2026-09-30 (0.12.55-dev)

Owner, verbatim: **"oh my god! look at the debug log!!!! its nothing but red!!!!!!!!!!!!!"**

and then: **"mkae sure to kill the exe and set up the mod for me so i can run rimsort again ,
only once your sure you fixed these issues"**

- [x] **"its nothing but red"** — **587 red lines, and every single one of them named `Door`, `Autodoor` or `CompProperties_Colorable` and nothing else.** One line in one patch file:

      <li Class="CompProperties_Colorable" />

  **There is no `CompProperties_Colorable` type in RimWorld.** `CompColorable` is declared with a plain `CompProperties` carrying a `compClass`, which is how Core declares it for textiles, apparel and the Ideology floor coverings — and the last of those are **buildings**, so it was the right mechanism for a door all along, spelled with a class that does not exist.

  **And a bad `Class` does not fail the one comp.** It throws out of `DirectXmlToObjectNew`, which **discards the entire ThingDef being parsed.** `Door` and `Autodoor` left the game; the remaining 585 errors were other defs — 541 of them vanilla `PrefabThingData` — failing to cross-reference doors that no longer existed. The owner's log went red from line 57 and the game **never left the main menu**, so nothing about generation, gates, materials or budgets was tested at all.

  **Not one mod conflict. Again.** Doors Expanded and Mechhive appear in the wreckage only as victims of our missing `Door`.

- [x] **why thirteen checkers and forty-one proofs passed it** — `check_class_references` has resolved `Class="..."` for a long time, and carried this line:

      if not value.startswith("RimroomsAsyncIndustries"):
          continue                      # Core and DLC types; not ours to verify from source.

  **The one category it exempted is the category that killed the game**, and a Core-shaped name is exactly what a typo produces — so the half taken on trust was the wrong half. Core and DLC names are resolved now against the type names in the installed game's **own assemblies**, read straight out of the CLI metadata `#Strings` heap: no reflection, no DLL load, no dependency, and DLC assemblies under `Data/<Dlc>/Assemblies` included so an Anomaly or Odyssey type resolves exactly as the game resolves it.

- [x] **AND THE PROOF WAS HOLDING THE BUG IN PLACE, which is the sharpest thing here** — `proof-gate-links.py` asserted, as its evidence that a gate is blue, `'<li Class="CompProperties_Colorable" />' in doorpatch`. **That string is the defect.** The proof did not merely miss it, it *required it to be present*, and `plant-gate-links-carry.py` planted a mangled version and watched the proof fail — a plant proving a broken line was load-bearing.

  **The rule this yields: asserting that our XML contains a string proves only that we wrote it, never that the game can use it.** Both assertions are retargeted, and the plant now restores the broken spelling and requires refusal — the opposite verdict on the same string.

- [x] **the first draft of my own fix would have failed correct code, which is worse than the hole** — the metadata `#Strings` heap permits **suffix sharing**: a name may be stored only as the tail of a longer one. `Building` is exactly that, so splitting the heap on NUL rejected `<thingClass>Building</thingClass>`. Membership is a search for `name + NUL`, which finds whole entries and shared suffixes alike and therefore cannot reject a real type.

- [x] **a tenth plant walked past the new proof, and it was the claim-scoping trap for the twenty-first time — mine, in the proof written to close a bug caused by trusting a name.** Restoring the exemption as `if True: continue` passed, because the claim asserted that a **comment** was absent. Fixed structurally rather than with a tighter string: the verdict is a pure function, `unresolved_class_names`, and the proof hands it a crafted set of names and **demands the output**. Blinding it, exempting it, making it always-true and removing its suffix awareness all fail now, and none of those could be caught by reading source text.

- [x] **the forty-second proof is the first one that EXECUTES what it checks** — `proof-class-resolution.py` imports the checker and interrogates the resolver, because a proof that reads text cannot tell whether a resolver resolves. That is the general lesson of the last three launches in one sentence.

- [x] **a plant that could never have been caught, found by running every suite instead of the ones I touched** — `plant-areas-and-debrief.py` planted `/* Backrooms Coordinate check */` into the roof provider and required a failure the proof could not deliver: it reads that file through `strip_cs_comments` **on purpose**, because a comment naming the Backrooms is not a second opinion that can drift. The proof was right and the plant was wrong — the inverse of the usual trap. It plants real code now.

---

"""

ENTRY = u"""
---

## Session 2026-09-30 - one line deleted `Door` from RimWorld (0.12.55-dev)

**Verbatim user quote:** *"oh my god! look at the debug log!!!! its nothing but red!!!!!!!!!!!!!"*
and *"mkae sure to kill the exe and set up the mod for me so i can run rimsort again , only once
your sure you fixed these issues"*

**Files touched:** `Patches/RR_NativeGateProviders.xml`, `tools/check-package-integrity.py`,
`.local/register/proof-class-resolution.py` (new), `plant-class-resolution.py` (new),
`proof-gate-links.py`, `plant-gate-links-carry.py`, `plant-areas-and-debrief.py`,
About/csproj/README, `docs/TODO.md`, `docs/NOW.md`.

**Closure notes.** **587 red lines. One line.**

Every error in the log named `Door`, `Autodoor` or `CompProperties_Colorable` and nothing else.
`<li Class="CompProperties_Colorable" />` names a type RimWorld does not have - `CompColorable`
is declared with a plain `CompProperties` carrying a `compClass`, as Core does for textiles,
apparel and the Ideology floor coverings, the last of which are buildings. And a bad `Class`
throws out of `DirectXmlToObjectNew`, which **discards the whole ThingDef**: `Door` and `Autodoor`
left the game and 585 further errors were other defs failing to cross-reference them. The game
never left the main menu, so **the seventh launch tested nothing but def load.** Not one mod
conflict - Doors Expanded and Mechhive appear only as victims of our missing `Door`.

**The hole was an exemption, and it was explicit.** `check_class_references` skipped every name
that was not ours, commented *"Core and DLC types; not ours to verify from source"* - so the one
category it trusted is the category that killed the game, and a Core-shaped name is exactly what
a typo produces. Those names now resolve against the installed game's own assemblies, read out of
the CLI metadata `#Strings` heap with no reflection and no DLL load, DLC assemblies included.

**And the proof was holding the bug in place.** `proof-gate-links.py` asserted
`'<li Class="CompProperties_Colorable" />' in doorpatch` as its evidence that a gate is blue, and
the matching plant mangled that string and watched the proof fail - a plant proving a broken line
was load-bearing. **Asserting our XML contains a string proves we wrote it, never that the game
can use it.**

**Two of my own mistakes inside the fix, both caught by running it.** The first draft split the
`#Strings` heap on NUL, which misses suffix-shared names and **rejected `Building`** - failing
correct code, which is worse than the hole. And a plant restoring the exemption as
`if True: continue` walked past the new proof, because the claim asserted a **comment** was
absent: the claim-scoping trap for the twenty-first time, mine, in the proof written to close a
bug caused by trusting a name. Fixed structurally - the verdict is a pure function and the proof
demands its **output**, so blinding, exempting, always-true and suffix-blind all fail.

**The forty-second proof is the first that executes what it checks**, because a proof that reads
text cannot tell whether a resolver resolves. Running every plant suite rather than the ones I
touched also surfaced a plant that could never have been caught: it planted a comment at a proof
that strips comments on purpose. The proof was right and the plant was wrong.

**200 C# files, 91 package files**, zero warnings, zero errors. Assembly SHA-256
`154428928909D68FFA599193CCE8997FBF10AC70671118AB958EEE701E3A3CF9`, reproduced by two clean
recompiles. **Thirteen checkers pass, forty-two proofs hold. 474 of 474** planted faults caught
across fourteen suites.

**Seven launches, seventeen defects, every one ours. Still not a single mod conflict.**
"""

todo = io.open(TODO, encoding="utf-8").read()
ANCHOR = u"## TOMBSTONES"
if todo.count(ANCHOR) != 1:
    print("TODO ANCHOR PROBLEM: %d" % todo.count(ANCHOR))
    raise SystemExit(1)

final = io.open(FINAL, encoding="utf-8").read()
io.open(FINAL, "w", encoding="utf-8", newline="").write(final + ENTRY)
if ENTRY not in io.open(FINAL, encoding="utf-8").read():
    print("FINALIZED WRITE NOT VERIFIED -- nothing else touched")
    raise SystemExit(1)
print("FINALIZED written and verified")

io.open(TODO, "w", encoding="utf-8", newline="").write(todo.replace(ANCHOR, ROW + ANCHOR, 1))
print("seventh-launch rows recorded")

now = io.open(NOW, encoding="utf-8").read()
EDITS = [
    (u"| Published | **0.12.54-dev**.", u"| Published | **0.12.55-dev**."),
    (u"SHA-256 `1FA1CEE1987B5FF32042F6DBA8D4ED279F76843B59A9881C331CE0F174EBF39C`",
     u"SHA-256 `154428928909D68FFA599193CCE8997FBF10AC70671118AB958EEE701E3A3CF9`"),
    (u"""## DO THIS FIRST — READ THE LOG FROM THE SEVENTH LAUNCH

**The owner is testing 0.12.53-dev. Read the log before anything else**, and read it before
telling them anything works.""",
     u"""## DO THIS FIRST — READ THE LOG FROM THE EIGHTH LAUNCH

**Read `Player.log` before anything else, and read it before telling the owner anything works.**
Three checkpoints in a row have now been answered from proofs rather than from a log, and three
times the answer was wrong.

### WHAT THE SEVENTH LAUNCH FOUND: 587 RED LINES FROM ONE LINE

**The game never left the main menu, so the seventh launch tested NOTHING but def load.**

```
Exception loading def from file Buildings_Structure.xml: System.ArgumentException:
  Could not find type named CompProperties_Colorable from node
  <li Class="CompProperties_Colorable" />
Could not resolve cross-reference to Verse.ThingDef named Door ...        (x529)
Could not resolve cross-reference: No Verse.ThingDef named Autodoor ...   (x59)
```

Every one of the 587 errors named `Door`, `Autodoor` or `CompProperties_Colorable` **and nothing
else**. There is no `CompProperties_Colorable` type: `CompColorable` takes a plain
`CompProperties` with a `compClass`. And a bad `Class` throws out of `DirectXmlToObjectNew`, which
**discards the entire ThingDef** — so `Door` and `Autodoor` left the game and 585 further errors
were other defs, 541 of them vanilla prefabs, failing to cross-reference them.

**Still not one mod conflict in seven launches.** Doors Expanded and Mechhive appear in that log
only as victims of our missing `Door`.

### THREE THINGS TO KNOW BEFORE WRITING ANOTHER PROOF

1. **A proof that reads text cannot tell whether a resolver resolves.** The forty-second proof,
   `proof-class-resolution.py`, is the first that **imports the checker and interrogates it**.
   When a claim is about whether something *works* rather than whether it is *written*, execute it.
2. **Asserting our XML contains a string proves we wrote it, never that the game can use it.**
   `proof-gate-links.py` required `'<li Class="CompProperties_Colorable" />'` as its evidence that
   a gate is blue — **it held the bug in place**, and the matching plant proved a broken line was
   load-bearing.
3. **Run EVERY plant suite, not the ones you touched.** Doing so found a plant that could never
   have been caught: it planted a comment at a proof that strips comments on purpose.

### What the EIGHTH launch has to settle, in this order

1. **DOES A COORDINATE GENERATE AT ALL.** Fourth attempt, and the generator has still never run
   end to end. Everything below depends on it.
2. **is the back-room door blue and glowing** once a level exists
3. **select a colonist, right-click the gate → "Enter the gate"** — they should walk over and come
   out on the other map
4. **every other door in the colony is unlit and unchanged** — the `IThingGlower` veto
5. **level 0 reads as the yellow rooms** — wood walls, yellow carpet, coherent, everything matching
6. **one level in, the materials go wild** — two tables in one room in different stuffs, each
   room's walls a different material. Newest thing in the build, least like anything that has run
7. **no cave-in** when a wall or a pillar is deconstructed
8. **Operations → Places** lists the colony and any level, with the budget as `n/5`"""),
]
problems = []
for old, _ in EDITS:
    if now.count(old) != 1:
        problems.append("%d of %r" % (now.count(old), old[:56]))
if problems:
    for problem in problems:
        print("NOW ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    now = now.replace(old, new, 1)
io.open(NOW, "w", encoding="utf-8", newline="").write(now)
print("NOW.md updated for 0.12.55-dev")
