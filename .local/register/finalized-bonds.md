
---

## 2026-09-29 — Company bonds, from ten credits to a quadrillion (0.7.5-dev)

### Verbatim owner requests

> *"and silver anfd gold are still in the game and all usable from building to selling but we need a ingame credit system with denominations in the exponents so that when the playthroughts build scrudge mcduck vaults they can store all the stuff like silver and gold and gems and ivory and everything pricey in theri vaults(this is already in the game) but we want also to be able to store the corprate credits(dollars since 1990 america?) in like company bonds or something that can be used easily and reposed with out leaveing a dead item or thing u are using (repurposing to be our cash bonds or what ever that can be converted and such to bigger values so if u wanted u can have a million credits as one item so we might need a processing facilies production chain simple and easy for handling storing and using like orbital beacons to beable to show that available credits and a way to turn gold silver gems ingots maybe needs to exchange for cradits with the company ect ect and all things pertaining, mind you these are ideas that are good but i expect u to expound on them"*

> *"option 1 works but they need to go up to values of 1 million like 10, 100, 1000, 10000 ... ect ect and a production bench with buills for makeing the differnt sizes and u are always payed in the highest values with least amount of bonds"*

> *"yeah keep teriing it then dont stop at 1 million"*

### What was built

- [x] **Three layers of money, with the bond as the bridge.** Silver, gold, jade and ivory are **entirely untouched vanilla** and a vault works as it always did. The company account stays the abstract ledger. The bond is the only one of the three that can burn — which, per the owner's *"Yes — physical means physical"*, is exactly the trade-off that makes the account still worth having.
- [x] **Fifteen rungs, 10 to one quadrillion**, after the owner's follow-up. Stopping at a million would have needed **a million pieces of paper to represent one trillion**, against a parent corporation recorded at multi-trillion scale. 10^15 keeps that to three or four bonds and stays far inside `long` (~9.2 × 10^18), so even thousands of top bonds cannot overflow a total.
- [x] **Greedy largest-first payout, and it is provably optimal here** because every rung is an exact multiple of every rung below it. That is why a strict power-of-ten ladder was worth insisting on over something like 1/5/10. Anything under ten credits **stays in the account** rather than being rounded away.
- [x] **The bench bills produce nothing, deliberately.** A bond's value is per-instance and Core's `GenRecipe.PostProcessProduct` is **private and static**, so there is no supported way to stamp a value onto something a bill just made, and the workaround would be Harmony. The worker mints the bond itself in the documented `Notify_IterationCompleted` instead. Two things fall out, both better than the alternative: the denomination comes from **the recipe that is running** rather than from guessing which object on the floor was just made, and an unfunded print produces **nothing** rather than an unstamped book worth free market value.
- [x] **Adding a rung needs one more RecipeDef and no code** — the denomination is parsed from the recipe's own defName, and the ladder stays the source of truth.
- [x] **Debit before mint, refund if unplaceable.** Printing paper the company cannot back is printing money, which is the one thing this layer exists to prevent.
- [x] **The credit beacon, and it was the owner's best reuse of the session.** A Core `OrbitalTradeBeacon`, designated. A trade beacon already means *the valuables in this circle are the ones that count*, so nobody learns a new idea and Core already draws the radius. **Dormant until designated**, so an unrelated beacon in an existing colony behaves exactly as it always has.
- [x] **Banking destroys the paper and credits the account in one transaction for the lot** — counted, destroyed, then posted — so a reload mid-action cannot credit a subset twice. That is the *"without leaveing a dead item"*.
- [x] **Repurposed, not invented.** A Core `Novel` with a comp. **No new item, no new texture.** An unstamped `Novel` is still an ordinary novel. Bonds are stamped `Outside` so one can never be sold as odd goods.
- [x] **A guard against a fact that is not a guarantee.** `AllowStackWith` keeps face values apart even though `Novel` has a stack limit of one today — a mod raising a book's stack limit would otherwise silently merge two bonds and destroy the quieter one.

### Build evidence

0.7.5-dev, SDK 9.0.308, Release/net472, zero warnings and zero errors with `TreatWarningsAsErrors` enabled. **131** C# source files (six new), **81** approved package files (two new). Assembly SHA-256 `63205DCF237021A4B238F4E11891B3060DF4833B90CCFC4B095B5FC6F74DE4CD`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. All four checkers pass; `check-keyed-strings` 1,133 references all resolving. Fifteen RecipeDefs and one `PatchOperationAdd` on a Core def (permitted; `Replace`/`Remove` remain forbidden). **No new gameplay ThingDef, no asset, no new work type.** No game launched, no test run, no RimSort profile touched.

### SESSION SUMMARY

Source files created: 6. Package files created: 2. Docs updated: 5 (1 new).
Owner directions captured verbatim: 3 in this checkpoint, plus 2 more recorded for the next.
Core limitations found by reading rather than by failing: 1 — `GenRecipe.PostProcessProduct` being private and static, which redirected the entire bench design toward something more robust than the original plan.
Still open and named in `TODO.md`, not deferred: the valuables exchange paying above market for odd; the multi-trillion corporate trader with tech, quest **and credit** gates on its stock tiers; and withdrawing credits as paper at a console.
