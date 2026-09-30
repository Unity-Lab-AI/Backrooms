# The register said don't patch, so the hook is a sentence — 0.12.39-dev

**Rows closed:** 764 (vehicles and space travel as logistics branches), 765 (VGE Chapter 1
logistics summary and operations links), 766 (VGE Chapter 2 orbital hooks), 784 (RWT feature
detection and setup diagnostics), 791 (the server-setup and player-experience document). **Five
rows, one family, one publish.**

No game was launched. Nothing here claims a gameplay, balance, performance or compatibility
result.

---

## 1. The register forbids patching all four, in its own words

The obvious build was patch hooks into the two gravship chapters and the vehicle framework.
Reading the register's own integration approach first — which the LAW requires — made that the
wrong build:

| Row | The register's instruction |
|---|---|
| **247** VGE Chapter 1 | *"**No patch or code/assets copied.** Gate and coordinate progression stays Rimrooms-owned; treat VGE as separate optional orbital content behind DLC/mod checks."* |
| **281** VGE Chapter 2 | *"**No patch or code/assets copied.** Keep Backrooms gate/operations independent; a VGE connected mission is only a future optional bridge **after verification**."* |
| **11** Vehicle Framework | *"Keep the machine gate as the Backrooms entry point… **do not add vehicles solely because the framework is installed**."* |
| **196** RimWorld Together | *"Keep each company's facility, gate, discoveries, research, and ledger on its own branch. **Do not assume** custom dossier or gear transfers."* |

So a hook cannot be a patch, cannot copy anything, and cannot make a Rimrooms route depend on any
of them. What is left is what the rows ask for **in their own words**: *"logistics
summary/operations links"* and *"feature detection and setup diagnostics"* — **a read-only
statement of what is installed and what this package does about it.**

That is a smaller deliverable than it first looked and a more honest one. The player's real
question about a 294-mod profile is *"does the mod I just installed do anything with this one, and
will it break?"* — and until now that answer lived only in a register HTML file **outside the
game**.

---

## 2. What was built

`InstalledIntegrations` detects five optional mods **by package id**, using Core's own
`ModsConfig.IsActive(string)`. The ids are the register's own `Workshop ID / package` column, and
**the proof reads `rimworld-server-mod-inventory.csv` and compares every one** — because a wrong
id produces a silent *"not installed"* forever, which is the defect class this project has been
caught by five times.

The list is re-read when `ModLister.InstalledModsListHash` changes, because a player can enable a
mod and restart into the same save, and asking Core every frame would be a string comparison per
mod per frame on a readout nobody is looking at most of the time.

The readout sits on the facilities page and says, for each: the register row, whether it is loaded,
and **what this package does with it** — in both states, because a player deciding whether to
install one needs to know beforehand. Row 765's *"operations links"* is `OpenNativeTab`, the same
helper the bed summary already uses: a button that opens the game's own surface, with nothing
patched.

### The defence that cannot rot

*"Do not add vehicles solely because the framework is installed"* is a rule about restraint, and
restraint decays. The proof asserts:

* **only two files in the whole package mention `InstalledIntegrations`** — the class itself and
  the readout. A detection layer that starts deciding things is exactly how this rule gets broken
  by accident.
* **no tracked package id appears in any other source file.** A package id outside the detection
  class is a dependency forming.
* the class **issues no job, order, route or spawn**.

A planted fault that makes the gate's integrity tick consult the vehicle framework is caught. So
is one that merely mentions a package id in a gate file.

### Row 766's absolute

*"Orbital enemies must never mix into Backrooms entity generation."* `InhabitantService` draws
only from `DefDatabase<RimroomsInhabitantDef>`, and the proof asserts both that and the absence of
any `PawnGroupMaker`, `FactionDef` or `DefDatabase<PawnKindDef>.AllDefs` source. A plant that opens
generation to any pawn kind is caught.

---

## 3. Row 791: the document, and a checker with teeth

`docs/MULTIPLAYER.md` is the server setup and the player experience, in player-facing language. It
opens with **"Nothing on this page has been tested in play"** and states outright that there is no
shared colony, no live shared map and no synchronised research.

The setup section records what was actually observed in the local server files, because it changes
what a player should expect: the server reports `AllowAllMods=true` and `EnforceSettings=false`, so
**every player must match their mod list by hand and nothing will warn them**; `ScenarioConfig.json`
forces `Crashlanded`, so any other start needs a disposable configuration copy; and whether offline
visiting is available is **unknown** from what was inspected.

### The claim guard

Row 791 is an absolute: *"No statement may describe live shared-colony control or synchronized
research unless implemented and demonstrated."* An absolute with no check is a promise, so
`check-doc-conformance.py` gained one.

The rule is about **asserting**, not mentioning — and a naive substring ban would fail the one
document written to obey it. That is precisely the trap `disposition_stance()` fell into by testing
`"required" in text` and calling *"not required"* a requirement. So each occurrence is checked for a
negator in its own sentence, and only an un-negated one is a claim.

**It found a real denial on its first run.** `docs/SCENARIOS.md` says *"shared research … stay
**unpromised** until the exact RWT profile passes the disposable-server test"* — a denial my
negator list did not know. The list is now documented as **maintained, not complete**, with the
failure direction chosen deliberately: a missing negator produces a **false positive that blocks a
build**, which is loud and gets fixed, rather than a false negative that lets a claim ship
silently.

Two of the seventeen plants put a **real** forbidden claim into a **real** reader-facing document —
*"Research is synchronised research across every company on the server"* in `MULTIPLAYER.md` and
*"Two players run one shared colony together"* in `README.md`. Both are caught, which is the only
way to know the guard would catch the thing it exists for.

---

## 4. Four of my own claims were too weak, and one 17-of-17 was worthless

The plants caught **four** loose claims in my own proof, all the same defect — *a claim that
searches for a string is not a claim about behaviour*:

1. *"the position is drawn in both states"* passed when the line was wrapped in
   `if (state.Active)`, because the inner text still matched. Fixed by making the indentation part
   of the claim.
2. *"the claim guard is wired in"* passed when the **call** was deleted, because the function's own
   `def` line contains the same substring. Fixed by requiring the indented call.
3. and 4. two document claims failed against a correct document, because `MULTIPLAYER.md` is
   hard-wrapped and a literal phrase search cannot cross a newline. Fixed by normalising
   whitespace — **seventh time this session the search was the defect and the code was fine.**

**And one fault-plant run reported 17 of 17 that was worthless.** My fix for (1) and (2) introduced
a syntax error, so the proof exited non-zero unconditionally and **every plant registered as
caught**. It was found by checking that the proof passes clean *before* planting, which is now the
thing to do first every time: **a plant run against a broken proof proves nothing and looks
perfect.**

---

## 5. Files

**New:** `src/.../Core/InstalledIntegrations.cs`, `docs/MULTIPLAYER.md`,
`.local/register/proof-integrations.py`, this record.

**Edited:** `src/.../UI/OperationsFacilities.cs` (the readout),
`tools/check-doc-conformance.py` (the reader-facing set gains `MULTIPLAYER.md`, and the row 791
claim guard), `1.6/Languages/English/Keyed/RR_Company.xml` (fifteen strings), `CHANGELOG.md`,
`README.md`, `About.xml`, the csproj, `docs/NOW.md`, `docs/TODO.md`, `docs/FINALIZED.md`.

**No new gameplay content, and no patch of any kind.** Fifteen keyed strings; no `ThingDef`,
`PatchOperation`, recipe, bench, item, texture or sound. **Nothing in another mod is read, changed
or copied.**

## 6. Verification

* **Build 0.12.39-dev** — 191 C# files, 87 package files, **0 warnings, 0 errors**.
* **Assembly reproduced across two clean rebuilds.**
* **Twelve checkers pass. Thirty-six proofs exit zero.**
* **17 of 17 planted faults caught**, verified after confirming the proof passes clean first.
* **No game was launched.** Every statement here is structural, and the document says so to the
  player as well.
