# The parent corporation as a trader, behind three locks (0.7.6-dev)

**Baseline:** `f5efea7` (0.7.5-dev, 131 C# files, 81 package files).

**This checkpoint — 0.7.6-dev:** **135 C# source files** (four new), **84 approved package files** (three new). Zero warnings, zero errors, `TreatWarningsAsErrors` on. Assembly SHA-256 `E1475C7F34E63380D6C0E04A48FA1F6501A323DA6DE9DF4946CB2A27034DDD7B`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The request

> *"and ther should be a trader that is the multi trillion dollar corporation with all kinds of equipenmnt tools amaterials and supplies like a universersal trader but things are tech and company quest locked out till passed"*

> *"and even cost credits to unlock item and materials and equipment gates in buying"*

## Three locks, and each one gates a different kind of progress

A tier opens only when **all three** are satisfied, which is why none of them is redundant:

| Lock | What it actually means |
|---|---|
| **Research** | you understand it — ordinary tech progression |
| **A completed company contract** | you have *done something for them* |
| **A credit access fee** | you paid for the *privilege*, not just for the goods |

The credit lock is the one that matters most structurally: **it is what makes the bond layer worth anything beyond storage.** Before this, a vault of paper was a place to keep money. Now it buys capability.

The contract lock reuses the existing `ContractRecord` rather than inventing a quest system, so an odd-goods supply contract or the onboarding survey **is** the thing that earns a tier. That keeps the whole economy pointing at the same loop instead of growing a second one beside it.

**The first tier has no locks at all, on purpose.** A corporation that sells you nothing until you have already succeeded is not a supplier, it is a wall.

## Universal by category, not by hand-listed item

The owner asked for *"all kinds of equipenmnt tools amaterials and supplies like a universersal trader"*. Each tier names a **`ThingCategoryDef`**, so it sells whatever the loaded game puts in that category — Core, DLC, and any of the other 274 mods alike. **This mod lists no items and invents none.** A profile that adds new metals sells new metals here the day it is installed.

| Tier | Research | Contract | Access fee |
|---|---|---|---|
| Basics | — | — | free |
| Tools and equipment | — | onboarding survey | 25,000 |
| Construction | Smithing | — | 100,000 |
| Medical | Medicine production | odd-goods supply | 1,000,000 |
| Restricted catalogue | Microelectronics | odd-goods supply | 100,000,000 |

## Locked means invisible, not greyed out — and the second half matters

A locked tier yields no stock **and reports that it handles none of its own definitions**. That second part is the one that is easy to miss: `HandlesThingDef` is what decides whether a trader will *buy* a thing and at what price. A tier that generated nothing but still claimed its category would quietly let a player **sell into a catalogue they had not unlocked**.

## Why this is not a subclass of Core's category generator

`StockGenerator_Category` was the obvious parent, but **every one of its fields is private** — the category, the count range, the exclusions. A subclass could neither read them nor reuse its generation. Reproducing the forty lines that matter is honest; inheriting a class whose state is invisible would have been a subclass in name only.

Generation still goes through Core's own `StockGeneratorUtility.TryMakeForStock`, so stuff, quality and stacking behave exactly as they do for every vanilla trader.

## Calling them in

An orbital `TraderKindDef` added to Core's own `passingShipManager` from the designated gate console. **The trade window, the beacon rule and the delivery are all vanilla** — nothing about trading is reimplemented here. The console is used because it is already what a branch talks to the company through: **no new building, no new bench, no new UI window.**

A locked tier's row in the float menu **says which lock is holding it**, rather than being greyed out silently. With three independent conditions, "you cannot do this" is a useless message.

All three locks are **re-checked at the moment of unlocking**, not just the one the UI thought was outstanding. A menu that offered the button is not evidence that the conditions still hold.

## A def that does not exist leaves the tier shut

If a tier names a research project that is not loaded — a DLC one on a Core-only install — the tier stays **closed**. Saying "unavailable" is honest; opening a gate because its key is missing is not.

## The checkers earned their place again

Two of the three new def files **did not parse**, because their comments contained `--`, which XML forbids inside a comment. The compiler was perfectly happy; the build succeeded. The parse failure was caught by `check-dlc-gating` and `check-package-integrity`, and the knock-on was visible in `check-keyed-strings` too.

The parser's own message is *"not well-formed (invalid token)"* at a column, which says nothing about the rule. Since prose naturally wants an em-dash typed as `--`, and this has now bitten more than once, `check-package-integrity.py` gained a **targeted check that names the rule and the line**. Sanity-tested by planting a bad comment, confirming the failure, and removing it.

## Not done, and named in `TODO.md`

- **The valuables exchange** — gold, silver, gems and ingots into credits, above market for odd resources.
- **Withdrawing credits as paper at a console**, the counterpart to banking at a beacon.
- **Tier balance.** The five tiers and their fees are a first pass with no play behind them; they are data, and changing them is a def edit.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled **twice** from clean; identical SHA-256.
- All four checkers pass. `check-keyed-strings.py`: 1,155 references all resolving, 0 duplicates, 0 argument mismatches.
- Compliance: one TraderKindDef, five RimroomsSupplyTierDefs, one keyed file. **No new gameplay ThingDef, no asset, no patch operation, no new work type.**

## For the post-completion test phase

Confirming a locked tier neither sells nor buys its category; confirming the first tier is open from a fresh start; confirming each lock reports itself by name; unlocking and confirming the fee is charged exactly once and survives a reload; hailing and confirming only one supplier can be in orbit at a time; confirming goods still have to be near a trade beacon to sell; and confirming a tier whose research project is missing stays shut rather than opening.
