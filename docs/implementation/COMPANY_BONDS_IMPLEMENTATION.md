# Company bonds, from ten credits to a quadrillion (0.7.5-dev)

**Baseline:** `abd9acf` (0.7.4-dev, 125 C# files, 79 package files).

**This checkpoint — 0.7.5-dev:** **131 C# source files** (six new), **81 approved package files** (two new). Zero warnings, zero errors, `TreatWarningsAsErrors` on. Assembly SHA-256 `63205DCF237021A4B238F4E11891B3060DF4833B90CCFC4B095B5FC6F74DE4CD`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The request

> *"silver anfd gold are still in the game and all usable from building to selling ... we want also to be able to store the corprate credits(dollars since 1990 america?) in like company bonds or something that can be used easily and reposed with out leaveing a dead item or thing u are using ... so if u wanted u can have a million credits as one item so we might need a processing facilies production chain simple and easy for handling storing and using like orbital beacons to beable to show that available credits"*

Then, on the ladder: *"they need to go up to values of 1 million like 10, 100, 1000, 10000 ... ect ect and a production bench with buills for makeing the differnt sizes and u are always payed in the highest values with least amount of bonds"* — and immediately after, **"yeah keep teriing it then dont stop at 1 million"**.

## Three layers of money, and the bond is the bridge

| Layer | Untouched? | Can it burn or be stolen? |
|---|---|---|
| Silver, gold, jade, ivory, plasteel | **Yes, entirely vanilla.** Vaults work as they always did | Yes, as always |
| The company account (credits) | The existing branch ledger | **No.** It is not anywhere |
| **Company bonds** | New | **Yes — that is the trade-off** |

The owner chose *"Yes — physical means physical"*, and that choice is what makes the ledger still worth having. Liquidity costs risk.

## The ladder runs to 10^15, not 10^6

Every power of ten from **10 to one quadrillion** — fifteen rungs. A million is a rung in the middle.

Stopping at a million would have needed **a million pieces of paper to represent one trillion**, and the parent corporation is on record at multi-trillion scale. 10^15 keeps a multi-trillion sum to three or four bonds while staying far inside `long`, whose ceiling is ~9.2 × 10^18 — even a hoard of thousands of top bonds cannot overflow a total.

**Every rung is exactly ten of the one below.** That is what makes the chain *simple and easy* as asked, rather than a conversion table, and it is also why the payout rule below is provably correct.

## "Always paid in the highest values with least amount of bonds"

Greedy, largest first — and greedy is **provably optimal here** because every rung is an exact multiple of every rung below it, so there is no case where taking a smaller note first ends up using fewer notes. That is the same reason it works for real currency, and the reason a strict power-of-ten ladder was worth insisting on rather than something like 1/5/10.

Anything below ten credits **stays in the account** rather than being rounded away. A player's money is never quietly lost to the shape of the ladder.

## Why the bench bills produce nothing

A bond's value lives per instance in a comp. A recipe's `products` list can only name a `ThingDef` and a count, and the hook that post-processes a finished product — `GenRecipe.PostProcessProduct` — is **private and static**. There is no supported way to stamp a value onto something a bill just made, and working around it would mean Harmony, which this mod does not use.

So the fifteen recipes declare **no products at all**, and `RecipeWorker_RRPrintBond` mints the bond itself in `Notify_IterationCompleted`, which *is* a documented virtual. Two things fall out of that, both better than the alternative:

- the denomination comes from **the recipe that is running**, not from guessing which object on the floor was the one just made;
- an unfunded print produces **nothing**, rather than an unstamped book worth free market value.

The denomination is parsed from the recipe's own defName (`RR_PrintBond_1000`), so **adding a rung needs one more RecipeDef and no code**. The ladder is the source of truth; a recipe naming a value off it prints nothing and says so.

## Paying for the paper

The face value is debited **before** the bond is made, through the campaign component's idempotent transaction. If the balance will not cover it, nothing is printed — printing paper the company cannot back is printing money, which is the one thing this whole layer exists to prevent. If the paper cannot be *placed*, the money goes straight back.

## The credit beacon was the owner's best reuse

A Core `OrbitalTradeBeacon`, designated. A trade beacon already means exactly this to a player — *the valuables inside this circle are the ones that count* — so nobody learns a new idea, Core already draws the radius on the ground, and the habit of stacking things near a beacon already exists.

**Dormant until designated**, exactly like the gate and emergence comps on Core doors: an unrelated trade beacon in somebody's existing colony behaves as it always has. It does not trade, does not talk to orbital ships, and does not alter Core's own beacon behaviour.

Banking destroys the paper and credits the account **in one transaction for the lot** — counted, then destroyed, then posted — so a reload mid-action cannot credit a subset twice. That is the owner's *"without leaveing a dead item"*: no spent certificate, no zero-value object to haul away.

## Repurposed, not invented

The bond is a Core `Novel` carrying a comp — a printed document, which is what a bearer instrument physically is. **No new item, no new texture.** A `Novel` without a stamped value is still an ordinary novel and reads as one, so the repurposing takes nothing away from a player.

Bonds are stamped `ThingOrigin.Outside` on creation, so a bond can never be sold as odd goods.

`AllowStackWith` keeps different face values apart. `Novel` has a stack limit of one today, so nothing would merge anyway — the guard is there because that is a fact about a Core def rather than a guarantee, and a mod raising a book's stack limit would otherwise silently merge two bonds and destroy the quieter one.

## Not done, and named in `TODO.md` rather than deferred

- **The exchange** — gold, silver, gems and ingots into credits, **above market for odd resources** per the owner's answer.
- **The corporate trader**: *"a trader that is the multi trillion dollar corporation with all kinds of equipenmnt tools amaterials and supplies like a universersal trader but things are tech and company quest locked out till passed"*, and *"even cost credits to unlock item and materials and equipment gates in buying"*.
- **Withdrawing from the account at a console**, as the counterpart to banking at a beacon. Printing a chosen denomination at the bench exists; a one-click "give me this many credits as paper" does not.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled **twice** from clean; identical SHA-256.
- `check-package-integrity.py` PASS — including the class check over the new `workerClass` and two new `CompProperties`.
- `check-keyed-strings.py`: 1,133 references all resolving, 0 duplicates, 0 argument mismatches.
- `check-dlc-gating.py` passes. `audit-gate0.py` PASS, zero errors.
- Compliance: fifteen RecipeDefs and one patch operation adding a comp to a Core def (`PatchOperationAdd`, permitted; `Replace`/`Remove` remain forbidden). **No new gameplay ThingDef, no asset, no new work type.**

## For the post-completion test phase

Printing each denomination and confirming the account is debited exactly once; printing with an empty account and confirming nothing is produced; confirming a printed bond reads its denomination in its label and inspect pane; designating a trade beacon and confirming it reports the right total and that an undesignated one reports nothing; banking and confirming the paper is destroyed and the account credited once; reloading mid-bank and confirming no double credit; burning a bond and confirming the credits are genuinely gone; and confirming a plain `Novel` is unaffected and still readable.
