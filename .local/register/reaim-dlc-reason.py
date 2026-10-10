# -*- coding: utf-8 -*-
"""`check-dlc-gating.py`'s RULE is right and its stated REASON is stale. Fix the reason.

The rule -- refuse a def that references DLC-only content without a `MayRequire` gate -- is
exactly the posture the owner chose on 2026-10-01 when asked how the code should treat required
content: **keep the graceful guards anyway**. Declaring a dependency so RimSort enforces it, and
still degrading rather than throwing for anyone who ignores the warning, is belt and braces, and
`MayRequire` is the XML half of it.

But the docstring justified itself with *"a mod whose entire claim is that it needs nothing but
Core"*, and that claim is no longer true: `About.xml` now declares **294 hard dependencies**
including all five expansions.

**A reason nobody believes is worse than no reason**, which is the same correction already owed to
`FacilityRelief.cs`'s trigger comment. The rule is untouched; only its account of itself changes.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHECKER = os.path.join(REPO, "tools", "check-dlc-gating.py")

OLD = u"""`Childcare` is a Biotech
`WorkTypeDef`, so on a Core-only install that is an **unresolved cross-reference at
load** -- a red error in a mod whose entire claim is that it needs nothing but Core.
The C# side had always degraded correctly through `GetNamedSilentFail`; only the XML
had been forgotten, and nothing was checking it."""

NEW = u"""`Childcare` is a Biotech
`WorkTypeDef`, so on an install without Biotech that is an **unresolved cross-reference
at load** -- a red error, and the kind nothing in the package was watching for.
The C# side had always degraded correctly through `GetNamedSilentFail`; only the XML
had been forgotten, and nothing was checking it.

**This rule survives the 2026-10-01 dependency change, and matters more because of it.**
`About.xml` now declares 294 hard dependencies, the five expansions among them, after the
owner's direction *"the mod DOES HAVE HARD DEPENDANCIES SO GET IT RIGHT AND MAKE SURE ITS
LAYED OUT RIGHT FOR RIMSORT TO NOTICE AND ENFORCE"*. So the old justification -- *a mod
whose entire claim is that it needs nothing but Core* -- is **no longer true and has been
removed rather than left standing**. What replaces it is the owner's own answer on posture:
declare the dependency so a manager enforces it, **and keep the graceful guard anyway**, so
a player who ignores the warning degrades instead of crashing. `MayRequire` is that guard in
XML exactly as `GetNamedSilentFail` is in C#, and a gate is now a deliberate second line
rather than the only line."""

text = io.open(CHECKER, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(CHECKER, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))

after = io.open(CHECKER, encoding="utf-8").read()
if u"entire claim is that it needs nothing but Core" in after:
    print("THE STALE REASON IS STILL ASSERTED")
    raise SystemExit(1)
print("DLC gating rule untouched; its stale justification replaced with the owner's posture")
