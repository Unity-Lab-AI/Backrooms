
---

## 2026-09-29 — The parent corporation as a trader, behind three locks (0.7.6-dev)

### Verbatim owner requests

> *"get starded"*

> *"and ther should be a trader that is the multi trillion dollar corporation with all kinds of equipenmnt tools amaterials and supplies like a universersal trader but things are tech and company quest locked out till passed"*

> *"and even cost credits to unlock item and materials and equipment gates in buying"*

### What was built

- [x] **Three locks per tier, each gating a different kind of progress**, which is why none is redundant: research means you understand it, a completed company contract means you have done something for them, and a credit access fee means you paid for the privilege rather than only for the goods.
- [x] **The credit lock is the structurally important one: it is what makes the bond layer worth anything beyond storage.** Before this, a vault of paper was a place to keep money. Now it buys capability.
- [x] **The contract lock reuses the existing `ContractRecord`** rather than inventing a parallel quest system, so an odd-goods supply contract or the onboarding survey **is** the thing that earns a tier. The whole economy keeps pointing at one loop instead of growing a second beside it.
- [x] **The first tier has no locks at all, on purpose.** A corporation that sells you nothing until you have already succeeded is not a supplier, it is a wall.
- [x] **Universal by category, not by hand-listed item.** Each tier names a `ThingCategoryDef`, so it sells whatever the loaded game puts there — Core, DLC and any of the other 274 mods alike. **This mod lists no items and invents none**; a profile that adds new metals sells new metals here the day it is installed.
- [x] **Locked means invisible, and the second half of that is easy to miss.** A locked tier yields no stock **and reports it handles none of its own definitions**, because `HandlesThingDef` is what decides whether a trader will *buy* a thing. A tier that generated nothing but still claimed its category would quietly let a player **sell into a catalogue they had not unlocked**.
- [x] **Not a subclass of Core's category generator, and that was checked rather than assumed.** Every field of `StockGenerator_Category` is **private** — category, count range, exclusions — so a subclass could neither read them nor reuse its generation. Reproducing the forty lines that matter is honest; inheriting a class whose state is invisible would be a subclass in name only. Generation still runs through Core's own `StockGeneratorUtility.TryMakeForStock`.
- [x] **Called in through Core's own `passingShipManager`** from the designated gate console, so the trade window, the beacon rule and the delivery are vanilla. **No new building, no new bench, no new UI window** — a gizmo and a float menu.
- [x] **A locked row says which lock is holding it.** With three independent conditions, "you cannot do this" is a useless message.
- [x] **All three locks are re-checked at the moment of unlocking**, not just the one the UI thought was outstanding. A menu that offered the button is not evidence that the conditions still hold.
- [x] **A tier naming a research project that is not loaded stays shut** — a DLC project on a Core-only install. Saying "unavailable" is honest; opening a gate because its key is missing is not.

### The checkers earned their place again

- [x] **Two of the three new def files did not parse**, because their comments contained `--`, which XML forbids inside a comment. **The compiler was perfectly happy and the build succeeded.** `check-dlc-gating` and `check-package-integrity` both caught it, and the knock-on showed in `check-keyed-strings` too.
- [x] The parser's own message is *"not well-formed (invalid token)"* at a column, which says nothing about the rule, and prose naturally wants an em-dash typed as `--`. Since this has now bitten more than once, `check-package-integrity.py` gained a **targeted check naming the rule and the line**. Sanity-tested by planting a bad comment, confirming the failure, and removing it.

### Build evidence

0.7.6-dev, SDK 9.0.308, Release/net472, zero warnings and zero errors with `TreatWarningsAsErrors` enabled. **135** C# source files (four new), **84** approved package files (three new). Assembly SHA-256 `E1475C7F34E63380D6C0E04A48FA1F6501A323DA6DE9DF4946CB2A27034DDD7B`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. All four checkers pass; `check-keyed-strings` 1,155 references all resolving. One TraderKindDef, five RimroomsSupplyTierDefs, one keyed file. **No new gameplay ThingDef, no asset, no patch operation, no new work type.** No game launched, no test run, no RimSort profile touched.

### SESSION SUMMARY

Source files created: 4. Package files created: 3. Docs updated: 5 (1 new).
Owner directions captured verbatim: 3.
Core classes rejected as base classes after reading their source: 1 — `StockGenerator_Category`, whose every field is private.
Defects caught by the project's own checkers that the compiler and build both passed: 2 (unparseable def files).
Checker gaps closed in the same checkpoint: 1, sanity-tested by breaking it.
Still open and named in `TODO.md`, not deferred: the valuables exchange paying above market for odd; withdrawing credits as paper at a console; and corporate catalogue balance, which is data.
