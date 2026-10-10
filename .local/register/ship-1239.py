# -*- coding: utf-8 -*-
"""Ledger, queue and NOW.md for 0.12.39-dev. Five rows, one family."""
import io
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def sub(rel, old, new):
    path = os.path.join(REPO, rel)
    s = io.open(path, encoding="utf-8").read()
    assert old in s, "%s: anchor missing %r" % (rel, old[:80])
    assert s.count(old) == 1, "%s: anchor not unique %r" % (rel, old[:80])
    io.open(path, "w", encoding="utf-8", newline="").write(s.replace(old, new, 1))
    print("updated %s" % rel)


sub("CHANGELOG.md", u"## 0.12.38-dev", u"""## 0.12.39-dev - 2026-09-29 - the game now tells you what it does with your other mods

- **The company panel lists the optional mods this mod has a position on, and what that position is.** Five of them, with the register row each came from, whether it is loaded, and in plain words what this mod will and will not do with it. That answer used to live only in a spreadsheet outside the game.
- **Nothing changes because a mod is installed.** No route, contract, gate or expedition will ever ask you for a vehicle or a gravship. Nothing another mod owns is patched, read or copied.
- **Nothing from orbit will ever turn up in a Backrooms space.** What lives in there comes only from this mod's own list, and that is checked on every build.
- **There is a page about playing together now**, with the server setup and what the experience actually is. It says plainly that each player runs their own company - no shared colony, no shared map, no shared research - and that none of it has been tested in play.
- **Every line of that says "loaded", never "supported".** No game has been launched from this project yet, and the build now refuses any document that claims otherwise.

Full record: [the register said don't patch, so the hook is a sentence](docs/implementation/INTEGRATIONS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.38-dev""")

sub("docs/FINALIZED.md", u"## Completed sessions", u"""## Session 2026-09-29 - the register said don't patch, so the hook is a sentence (0.12.39-dev)

**Verbatim user quote:** *"lets keep working 12 left lest get moving"*

### What shipped

**Five rows, one family**: 764, 765, 766, 784 and 791. All of them optional-mod work, all governed by the same register instruction.

### Files touched

`src/.../Core/InstalledIntegrations.cs` **new**, `docs/MULTIPLAYER.md` **new**, `src/.../UI/OperationsFacilities.cs`, `tools/check-doc-conformance.py`, `1.6/Languages/English/Keyed/RR_Company.xml`, `.local/register/proof-integrations.py` **new**, `docs/implementation/INTEGRATIONS_IMPLEMENTATION.md` **new**, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj, `NOW.md`, `TODO.md`.

### Closure notes

- **THE REGISTER CHANGED WHAT A HOOK COULD BE, AND READING IT FIRST IS THE ONLY REASON.** The obvious build was patch hooks into both gravship chapters and the vehicle framework. The register's integration approach forbids exactly that, in its own words: *"**No patch or code/assets copied.** Gate and coordinate progression stays Rimrooms-owned"* (row 247), the same for row 281 plus *"a VGE connected mission is only a future optional bridge **after verification**"*, and for row 11 *"**do not add vehicles solely because the framework is installed**"*. So a hook cannot be a patch, cannot copy anything, and cannot make a Rimrooms route depend on any of them.
- **WHAT IS LEFT IS WHAT THE ROWS ACTUALLY ASK FOR.** Row 765 wants *"logistics summary/operations links"*; row 784 wants *"feature detection and setup diagnostics"*. Both are satisfied by **a read-only statement of what is installed and what this package does about it** — and the player's real question about a 294-mod profile is *"does the mod I just installed do anything with this one"*, which until now was answerable only from a register HTML file **outside the game**.
- **Detection is by package id, and every id is checked against the register's own CSV by the proof.** A wrong id is a silent *"not installed"* forever, which is the defect class this project has been caught by five times. The list is re-read when `ModLister.InstalledModsListHash` changes, because a player can enable a mod and restart into the same save.
- **THE DEFENCE THAT CANNOT ROT.** *"Do not add vehicles solely because the framework is installed"* is a rule about restraint, and restraint decays. The proof asserts that **only two files in the package mention `InstalledIntegrations`** — the class and the readout — and that **no tracked package id appears in any other source file**, because an id outside the detection class is a dependency forming. A plant that makes the gate's integrity tick consult the vehicle framework is caught; so is one that merely mentions an id in a gate file.
- **Row 766's absolute is asserted:** *"orbital enemies must never mix into Backrooms entity generation."* `InhabitantService` draws only from `DefDatabase<RimroomsInhabitantDef>`, and the proof also asserts the absence of any `PawnGroupMaker`, `FactionDef` or `DefDatabase<PawnKindDef>.AllDefs` source.
- **ROW 791 GOT A CHECKER, because an absolute with no check is a promise.** *"No statement may describe live shared-colony control or synchronized research unless implemented and demonstrated."* The rule is about **asserting**, not mentioning, and a naive substring ban would fail the one document written to obey it — **exactly the trap `disposition_stance()` fell into** by testing `"required" in text` and calling *"not required"* a requirement. So each occurrence is checked for a negator in its own sentence.
- **AND IT FOUND A REAL DENIAL ON ITS FIRST RUN.** `docs/SCENARIOS.md` says *"shared research … stay **unpromised** until the exact RWT profile passes the disposable-server test"* — a denial my negator list did not know. The list is now documented as **maintained, not complete**, with the failure direction chosen deliberately: a missing negator is a **false positive that blocks a build**, which is loud and gets fixed, rather than a false negative that ships a claim silently.
- **Two plants put a REAL forbidden claim into a REAL reader-facing document** — *"Research is synchronised research across every company on the server"* in `MULTIPLAYER.md` and *"Two players run one shared colony together"* in `README.md`. Both caught, which is the only way to know the guard catches what it exists for.
- **FOUR OF MY OWN CLAIMS WERE TOO WEAK, all the same defect.** (1) *"the position is drawn in both states"* passed when the line was wrapped in `if (state.Active)` because the inner text still matched. (2) *"the claim guard is wired in"* passed when the **call** was deleted, because the function's own `def` line contains the same substring. (3) and (4) two document claims failed against a **correct** document, because `MULTIPLAYER.md` is hard-wrapped and a literal phrase search cannot cross a newline — **seventh time this session the search was the defect and the code was fine.**
- **AND ONE FAULT-PLANT RUN REPORTED 17 OF 17 THAT WAS WORTHLESS.** My fix for the first two introduced a syntax error, so the proof exited non-zero unconditionally and **every plant registered as caught**. Found by checking that the proof passes clean *before* planting. **That is now the first step every time: a plant run against a broken proof proves nothing and looks perfect.**
- Build 0.12.39-dev, **191 C# files, 87 package files**, **0 warnings, 0 errors**, assembly identical across two clean rebuilds. Twelve checkers pass, **thirty-six** proofs exit zero, **17 of 17** planted faults caught after the proof was verified clean. **No game was launched.**

---

## Completed sessions""")

sub("README.md", u"**Current development version: 0.12.38-dev.**",
    u"**Current development version: 0.12.39-dev.**")

print("ledger written for 0.12.39-dev")
