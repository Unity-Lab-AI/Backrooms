# -*- coding: utf-8 -*-
"""Record the half-wiring criticism verbatim and the instruments built to answer it."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

SECTION = NL.join([
"",
"## Owner direction — half-wiring is a defect class, and now it has an instrument (2026-10-05)",
"",
"**Verbatim owner direction (2026-10-05):** *\"31 open lets get to it some may be partially alreay done u have a habit of half completing and half wiring up and half connecting things\"*",
"",
"**The criticism is accurate and this checkpoint produced four examples of it in one day:** the generation notice was wired to **three of six** paths that can generate a map; the solo/group two-map start was fully built and guarded by **nothing**; grand rooms could be *anywhere* but there was still only **one**; and the viewing-wall direction was answered in code while its queue row was **lost**.",
"",
"**`check-wiring.py` could not see any of them.** It refuses a def nothing reads and an action nothing calls — and a feature called from one site out of seven passes both, because every individual file is correct and the thing missing is a call nobody wrote. **Nothing looked at whether a guard reaches everywhere it has to.**",
"",
"- [x] **\"u have a habit of half completing and half wiring up and half connecting things\"** — **ANSWERED WITH AN INSTRUMENT RATHER THAN A PROMISE, 0.12.98-dev. `check-call-coverage.py` is checker 23.** Each chokepoint in `tools/call-coverage.json` carries a **census of every file that reaches it**, and each of those is either `covered` by a **named** wrapper — whose presence in that same file is then asserted, so deleting the guard and leaving the call behind fails — or `exempt` **with a stated reason**, because a tick genuinely cannot queue a long event and read its result. "
"Four rules: a declared site must still be a real caller so the census cannot rot; a covered site must still contain its wrapper; an exemption must say why; and **every real caller must be declared, so a new path that forgets the guard fails the build.** That last one is the whole point — it is the single moment anybody is in a position to notice they are wiring up half of something. "
"**It earned itself on its first run**, reporting two real call sites the hand-written census had missed — `WorkGiver_ConnectedDeployment.cs` and `WorkGiver_ConnectedWork.cs`, both genuinely guarded, both omitted because the grep that produced the list was truncated at eight lines. **That is the same mistake in miniature as the defect the file exists to catch**, which is why the rule asserts the found set rather than trusting the declared one. Two chokepoints declared: generation-must-be-announced (2 covered, 4 exempt with reasons) and the traversal policy (10 covered, 0 exempt). Three of the four rules proved by planting; the fourth proved itself.",
"- [x] **\"some may be partially alreay done\"** — **SWEPT THE LARGEST HALF-DONE CLUSTER AND IT IS NOT HALF-WIRED. 27 of 27 connected-work deployment providers are fully reachable.** The chain is **three links in three different kinds of file** — registered in `ConnectedDeploymentProviders`, a `WorkGiver_Connected*` subclass overriding `ProviderId`, and a `WorkGiverDef` naming that subclass in `giverClass` — and `Get(id)` is the **only** consumer because `All` is never enumerated, so a break at any link is work a pawn can never be asked to do and nothing else here would notice. **`check-wiring.py` now asserts all three links**, with both failure modes plant-proven. "
"**And the measuring tool was wrong before the mod was:** the first version looked for `workGiverClass` where RimWorld's field is `giverClass`, found zero, and reported **all twenty-seven providers unreachable** — a confident wrong answer about shipped work, caught only because the number was too round to believe. **A tool that cannot see the feature is worse than no tool.** The remaining rows in that cluster are honestly blocked on an owner-launched measurement, not on wiring.",
"",
])

text = io.open(TODO, encoding="utf-8").read()
if "half-wiring is a defect class" in text:
    print("section already present; nothing written")
    sys.exit(1)
if not text.endswith(NL):
    text += NL
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text + SECTION)
print("recorded: %d closed" % SECTION.count("- [x] "))
