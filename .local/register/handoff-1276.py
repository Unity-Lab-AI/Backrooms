# -*- coding: utf-8 -*-
"""The NOW.md handoff for 0.12.76-dev, written after staging and before the cascade."""
import io
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOW = os.path.join(REPO, "docs", "NOW.md")

HASH = sys.argv[1] if len(sys.argv) > 1 else None
if not HASH or len(HASH) != 64:
    print("usage: handoff-1276.py <assembly sha256 read back from the game folder>")
    raise SystemExit(1)

HANDOFF = u"""## STATE AT THIS HANDOFF — `0.12.76-dev`, STAGED AND VERIFIED

```
staged      Rimrooms.AsyncIndustries  0.12.76-dev  92 files
assembly    __HASH__
            read back out of the game folder after staging, not from the build
battery     16 checkers - 48 proofs - 19 plant suites - 738 anchors findable
            new suites: 27 of 27, 20 of 20, 7 of 7
tree        no planted fault, porcelain 0
```

### THE OWNER'S QUESTION FOUND TWO FALSE STATEMENTS IN THE PREVIOUS HANDOFF

*"are u shure zero goon squad code is written weve gone over this before by a different name"*.

The handoff had said **"ZERO code written"** on the strength of `src/` matching 0.12.75-dev — which
proves only that **that session** wrote none. It says nothing about what was built earlier under
another name, and this repository has been caught by exactly that **nine times**.

| The claim | What was true |
|---|---|
| *"Nothing in the battery claims anything about `FacilityRelief`"* | **`proof-facility-relief.py` is proof FIVE** and two of its claims contradicted the direction |
| *"Core defs confirmed present: ... `Pyre`"* | **`Pyre` is Ideology.** The check ran against the **installed game** instead of against **Core**, and for a Core-only mod that is the whole distinction |

**Read it as a standing rule:** *"it is identical to the last checkpoint"* answers a different
question from *"does this exist"*. Only a grep for the feature answers the second.

### THE SCOPING SAVED TWO PROOF CLAIMS THAT LOOKED LIKE CASUALTIES

`proof-facility-relief.py` asserts *five roles* and *the living-staff scan does not treat downed as
dead*. Both looked doomed until the owner's own words resolved it — *"this only happens for the lab
secnerio for now"* — so the squad is a **separate path** and the fork sits **above** the relief's
trigger:

```
TickFacilityRelief()
  laboratory  -> TickClearSquad()    downed counts as lost, three staff
  store, solo -> AnyLivingStaff()    dead only, five staff   [UNCHANGED]
```

Both old claims hold untouched. The comment carrying the old reasoning is **scoped, not deleted** —
it is still true about the path it guards. **Making it universal would have silently rewritten the
bargain for two scenarios the owner excluded.**

### THE GRAVE DOES NOT FIT INDOORS, AND IT WAS MEASURED

Core's `Grave` is **(1,2)** and needs **`Diggable`**. **Ten** Core terrains carry it; **every
constructed floor is excluded** — `Concrete`, `SterileTile`, `MetalTile`, every stone tile, every
carpet. **A grave cannot be dug inside the facility at all.** Burial goes to open ground and the
fallback is destruction, which is *"incenerate on propery"*. **No crematorium is built**: a bill
needs a worker and nobody is alive to work it.

### THE DEPENDENCIES, AND THE DEFECT DECLARING THEM EXPOSED

*"the mod DOES HAVE HARD DEPENDANCIES SO GET IT RIGHT AND MAKE SURE ITS LAYED OUT RIGHT FOR RIMSORT
TO NOTICE AND ENFORCE"*, and *"WE ARE USING ALL OF THEM!!!!"*.

`About.xml` declared **nothing** and a description reading *"Core only ... No Harmony, no
dependencies."* It now declares **294** — five expansions and 289 mods, each with a `displayName`
and a `steamWorkshopUrl` — plus **295 `loadAfter` entries**.

**THE REAL FIND: the package sat at position 197 of 296, with 99 mods loading after it.** A patch
cannot see a def from a mod that loads later. `modDependencies` is what a manager reads to warn;
**`loadAfter` is what makes the order right**, and there was one entry.

**NEVER HAND-EDIT THOSE BLOCKS.** `.local/register/build-dependencies.py` generates them from the
owner's own `ModsConfig.xml`, **read-only**, with a cycle check over every active mod's four
load-order tags. 1815 lines of About.xml is not a file anyone edits by hand.

### TWO CHECKERS CARRIED THE OLD PREMISE AND NEITHER WAS DEFECTIVE

`check-register-compliance.py` refused the work with *"The package must load and run against Core
alone."* **The checker was not wrong; its premise was**, and the register is *"not law but
guidance"* by the owner's standing correction. **A prohibition became an assertion** rather than
being deleted. 7 of 7 planted faults caught.

`check-dlc-gating.py`'s rule survives and matters **more** — `MayRequire` is the same graceful
guard in XML that `GetNamedSilentFail` is in C#, which is the posture the owner chose. Only its
stated reason was stale.

### AND THE SIXTH INSTANCE OF AN INSTRUMENT READING ITS OWN PROSE WAS MINE

The fix script searched its own result for the phrase it had removed, and the replacement prose
*quotes* that phrase in the sentence retiring it. **The write had landed; the verification was the
defect.** Then a second of the same family: `"Pawn" not in register` is a **substring test wearing
a type test's clothes** and it is false — `NoteLostPawn` and `lostPawnNames` contain those letters.
**Assert the thing, not letters that spell it.**

### THE THREE PREP ITEMS ARE CLOSED

* **the stranded crew** — `LostPawnRegister.cs` holds a `List<string>` and cannot remove player
  control by construction. But `proof-stranded-crew.py` had **eleven claims and not one mentioned
  it**, so the guarantee rested on nobody adding a `Pawn` field to a file whose name sounds exactly
  like somewhere a pawn would go. **Three claims make it permanent.**
* **review**, the fourth workflow — additive fields, **never a sixth `EvidenceStatus`**:
  `Analyzed` is terminal, eight places compare against it, and the enum is saved by value. Ships
  with a **button**, a readout and an objective line in the same checkpoint.
* **staff prior exposure** — `NoteReturnedFromField` already knew *this person came back from
  there* and **threw it away** as a transient debrief hold. Now kept per person **by load id, never
  by reference**, and spent on the dial **once**, where the branch's own familiarity compounds.

"""
HANDOFF = HANDOFF.replace(u"__HASH__", HASH)

EDITS = [
    (u"| Published | **0.12.75-dev**.", u"| Published | **0.12.76-dev**."),
    (u"SHA-256 `AABE696E79D3745FEDC3397C2E21B179D43538C3C6FB71A9276D444D4663483A`",
     u"SHA-256 `" + HASH + u"`"),
    (u"## NEXT UP, AND IT IS NOT BUILT: THE GOON SQUAD (0.12.76-dev)",
     HANDOFF + u"## BUILT AT 0.12.76-dev — THE SPEC THAT PRECEDED IT, KEPT FOR THE RECORD"),
]

now = io.open(NOW, encoding="utf-8").read()
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

after = io.open(NOW, encoding="utf-8").read()
failures = []
if u"## STATE AT THIS HANDOFF — `0.12.76-dev`, STAGED AND VERIFIED" not in after:
    failures.append("the handoff block is missing")
if HASH not in after:
    failures.append("the staged hash is not recorded")
if u"AND IT IS NOT BUILT: THE GOON SQUAD" in after:
    failures.append("the spec still says it is not built")
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("NOW.md leads with 0.12.76-dev; the old spec is relabelled as built, not deleted")
