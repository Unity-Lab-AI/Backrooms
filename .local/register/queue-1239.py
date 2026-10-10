# -*- coding: utf-8 -*-
"""Close the five optional-mod rows. Status changes and appended closure notes only."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "docs", "TODO.md")

s = io.open(PATH, encoding="utf-8").read()

SHARED = (u"**CLOSED 0.12.39-dev, and the register changed what a hook could be.** Its integration "
          u"approach forbids exactly the obvious build, in its own words: **\"No patch or "
          u"code/assets copied\"** for both gravship chapters, and *\"do not add vehicles solely "
          u"because the framework is installed\"* for the vehicle framework. So a hook here is a "
          u"**read-only statement of what is installed and what this package does about it** — "
          u"which is what these rows ask for in their own words (*\"logistics summary/operations "
          u"links\"*, *\"feature detection and setup diagnostics\"*). `InstalledIntegrations` "
          u"detects five mods by **package id read from the register**, and the readout on the "
          u"facilities page says the row, whether it is loaded, and this mod's position on it in "
          u"both states. **The defence that cannot rot:** the proof asserts only two files in the "
          u"package mention the detection class, and **no tracked package id appears in any other "
          u"source file** — an id outside that class is a dependency forming. Operations links are "
          u"`OpenNativeTab`, the game's own surface, with nothing patched. Record "
          u"`implementation/INTEGRATIONS_IMPLEMENTATION.md`, proof `proof-integrations.py`. Was: ")


def sub(old, new):
    global s
    assert old in s, "anchor missing: %r" % old[:90]
    assert s.count(old) == 1, "anchor not unique: %r" % old[:90]
    s = s.replace(old, new, 1)


sub(u"- [ ] Add vehicles and space travel as logistics branches;",
    u"- [x] " + SHARED + u"Add vehicles and space travel as logistics branches;")

sub(u"- [ ] Add VGE Chapter 1 logistics summary/operations links",
    u"- [x] " + SHARED + u"Add VGE Chapter 1 logistics summary/operations links")

sub(u"- [ ] Add VGE Chapter 2 orbital security/contracts/wreck sal",
    u"- [x] **CLOSED 0.12.39-dev.** Same read-only shape as rows 764 and 765 — nothing patched, "
    u"nothing copied. **This row's absolute is now asserted by proof:** *\"orbital enemies must "
    u"never mix into Backrooms entity generation\"* — `InhabitantService` draws only from "
    u"`DefDatabase<RimroomsInhabitantDef>`, and the proof also asserts the absence of any "
    u"`PawnGroupMaker`, `FactionDef` or `DefDatabase<PawnKindDef>.AllDefs` source, so no installed "
    u"content can leak in. A planted fault that opens generation to any pawn kind is caught. "
    u"Record `implementation/INTEGRATIONS_IMPLEMENTATION.md`. Was: Add VGE Chapter 2 orbital "
    u"security/contracts/wreck sal")

sub(u"- [ ] Implement feature detection and setup diagnostics for",
    u"- [x] **BUILT 0.12.39-dev.** Detection is `ModsConfig.IsActive` against the **package id "
    u"read from the register**, re-read when `ModLister.InstalledModsListHash` changes because a "
    u"player can enable a mod and restart into the same save. **The three states this row asks "
    u"for**, said in the readout: *not loaded*, *loaded*, and — for every one of them — "
    u"**unverified in play**, because no game has ever been launched from this repository. "
    u"Saying *\"supported\"* would be a claim nobody has earned. **It remains unverifiable "
    u"without a launch the owner performs**, and per the standing instruction that is never a "
    u"reason to defer building: the detection is built and proved structurally, and the readout "
    u"says plainly that it is unproven. Was: Implement feature detection and setup diagnostics "
    u"for")

sub(u"- [ ] Document exact server setup and player experience.",
    u"- [x] **WRITTEN 0.12.39-dev as `docs/MULTIPLAYER.md`, and this row's absolute now has a "
    u"checker.** The document opens with *\"Nothing on this page has been tested in play\"* and "
    u"states outright that there is **no shared colony, no live shared map and no synchronised "
    u"research**. The setup section records what was actually observed: the server reports "
    u"`AllowAllMods=true` and `EnforceSettings=false`, so **every player must match their mod "
    u"list by hand and nothing will warn them**; `ScenarioConfig.json` forces `Crashlanded`, so "
    u"any other start needs a disposable configuration copy; and whether offline visiting works "
    u"is **unknown** from what was inspected. **`check-doc-conformance.py` gained a claim "
    u"guard** — an absolute with no check is a promise. It tests for **assertion rather than "
    u"mention**, because a naive substring ban would fail the one document written to obey the "
    u"rule (the exact trap `disposition_stance()` fell into), and it **found a real denial on its "
    u"first run** in `SCENARIOS.md`. Two fault plants put a real forbidden claim into a real "
    u"reader-facing document and both are caught. Was: Document exact server setup and player "
    u"experience.")

io.open(PATH, "w", encoding="utf-8", newline="").write(s)
print("five rows closed")
