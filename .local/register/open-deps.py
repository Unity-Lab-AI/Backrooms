# -*- coding: utf-8 -*-
"""The hard-dependency direction, verbatim, every clause its own row."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")

ANCHOR = u"---\n\n## TOMBSTONES"

ENTRY = u"""---

## IN PROGRESS - the hard dependencies, and RimSort enforcing them - 2026-10-01 (0.12.76-dev)

Owner, verbatim:

> **"see thats WRONG the mod DOES HAVE HARD DEPENDANCIES SO GET IT RIGHT AND MAKE SURE ITS LAYED
> OUT RIGHT FOR RIMSORT TO NOTICE AND ENFORCE"**

and when asked which ones, verbatim:

> **"there are alot more depeandacies than just the DLC we have alkinds of mods in the 274 mod
> list WE ARE USING ALL OF THEM!!!!"**

and on how the code should then treat that content, the owner chose **keep the graceful guards
anyway**: declare the dependency so a mod manager enforces it, and keep the name-based lookups so
a player who ignores the warning degrades instead of crashing.

- [x] **"the mod DOES HAVE HARD DEPENDANCIES"** - `About.xml` declared **none at all**. It carried
  `loadAfter: Ludeon.RimWorld` and a description reading *"Core only. Royalty, Ideology, Biotech,
  Anomaly and Odyssey are optional and used when present. No Harmony, no dependencies."* **294
  hard dependencies are now declared** - the five expansions and 289 mods - generated from the
  owner's live load order by `.local/register/build-dependencies.py`. **Never hand-edit the
  dependency blocks; edit that script and re-run it**
- [x] **"MAKE SURE ITS LAYED OUT RIGHT FOR RIMSORT TO NOTICE AND ENFORCE"** - two blocks, because
  they do different jobs. **`modDependencies`** is what a manager reads to say *this is missing*,
  and each row carries a `displayName` and a `steamWorkshopUrl` so it can tell the player which
  mod and where to get it. **`loadAfter`** is what makes the order right, and it is the
  functionally load-bearing half
- [x] **The defect this exposed, which nobody was looking for** - our package sat at **position
  197 of 296** in the owner's live order, so **99 mods were loading after us**. A patch cannot see
  a def from a mod that loads later, so anything we patch against those 99 was reading a def that
  did not exist yet. Declaring `loadAfter` against all of them is what moves us last; RimSort does
  the sorting itself
- [x] **"WE ARE USING ALL OF THEM!!!!"** - the source of truth is the owner's own
  `ModsConfig.xml`, read **read-only**: 296 active entries, Core plus five expansions plus 290
  mods, one of which is ours. Every one resolved to an installed folder and **every non-expansion
  dependency has a Workshop id**, so no row sends the player nowhere. **The active RimSort list
  was never written to**, per the standing constraint
- [x] **The cycle check, which is not optional** - declaring `loadAfter` against 289 mods
  deadlocks if any one of them declares a constraint back on us. Every active mod's `loadAfter`,
  `loadBefore`, `forceLoadAfter` and `forceLoadBefore` was read and **none names us**. The
  generator refuses rather than emitting an order no sorter can satisfy
- [x] **`check-register-compliance.py` refused the whole thing, and its premise was what was
  wrong** - the rule read *"About.xml must declare no `modDependencies`. The package must load and
  run against Core alone."* **That was a fair reading of the register's guidance in September and
  the owner has overruled it** - and the register is *"not law but guidance"* by the owner's own
  standing correction, so an owner decision supersedes a register-derived rule. **A prohibition
  became an assertion** rather than being deleted: every declaration must carry a name, a way to
  obtain it, and a matching `loadAfter` entry; our own id and Core are refused; duplicates are
  refused
- [x] **Seven planted faults, 7 of 7 caught** - `.local/register/plant-dependencies.py`, suite
  SEVENTEEN. **A rule that cannot fail is not a rule**, and the branch that matters most plants
  the position-197 defect back in: a dependency required and never ordered. **The first draft used
  `(name, function)` tuples and `check-plant-anchors.py` refused all seven as malformed** - it was
  right, the house shape exists so a seventeenth instrument can read every anchor. **691 anchors
  findable**, up from 684
- [x] **`check-dlc-gating.py`'s rule survives and its stated reason did not** - the rule refuses a
  def referencing DLC-only content without a `MayRequire` gate, and that **is** the owner's chosen
  posture: `MayRequire` in XML is the same graceful guard `GetNamedSilentFail` is in C#. But it
  justified itself with *"a mod whose entire claim is that it needs nothing but Core"*, which is
  no longer true. **The reason was replaced and the rule was not touched** - a reason nobody
  believes is worse than no reason
- [x] **The sixth instance of an instrument reading its own explanatory prose, and the first that
  was mine** - the fix script searched its own result for the phrase it had removed, and the
  replacement prose *quotes* that phrase in the sentence retiring it. **The write had already
  landed; only the verification was wrong.** Same shape as `check-compliance.py` flagging
  `PatchOperationReplace` inside the comment explaining why a replace is wrong (0.12.46-dev) and
  `check-register-compliance.py` matching `statBases` inside the comment saying it cannot be one
  (0.12.75-dev). The fix is the one both checkers took: **assert against the live form, not the
  mention**
- [ ] **The register drift this surfaced, not yet resolved** - `tools/register-query.py` parses
  **295 rows** against **289 live other-mods**. The live load order is the right source for a
  dependency list and was used; **the gap between the two is unexamined** and belongs to the
  register, not to About.xml
"""

text = io.open(TODO, encoding="utf-8").read()
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(TODO, "w", encoding="utf-8", newline="").write(
    text.replace(ANCHOR, ENTRY + u"\n" + ANCHOR, 1))

after = io.open(TODO, encoding="utf-8").read()
for phrase in (u"the mod DOES HAVE HARD DEPENDANCIES SO GET IT RIGHT",
               u"WE ARE USING ALL OF THEM!!!!"):
    if phrase not in after:
        print("VERBATIM MISSING: %s" % phrase)
        raise SystemExit(1)
print("TODO opened for the dependency work; both owner quotes verbatim and verified")
