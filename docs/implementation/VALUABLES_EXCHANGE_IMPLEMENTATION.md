# The exchange, and credits back out as paper (0.7.7-dev)

**Baseline:** `7cdd70e` (0.7.6-dev, 135 C# files, 84 package files).

**This checkpoint — 0.7.7-dev:** **137 C# source files** (two new), **84 approved package files** (unchanged; eleven keyed strings added to an existing file). Zero warnings, zero errors, `TreatWarningsAsErrors` on. Assembly SHA-256 `ED36F5C73ADAF2C11230F0B22210B238386859C5D6CEB1FD3329CD97309CC617`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The request

> *"a way to turn gold silver gems ingots maybe needs to exchange for cradits with the company"*

> *"above market for (odd) resources"*

This closes the money loop. Credits now have a source (contracts, the exchange), a physical form (bonds), a store (the account, or a vault), and a sink (catalogue access fees).

## The rate is the whole design

| What | Rate | Why |
|---|---|---|
| **Odd goods** | **×1.5** | The owner's answer. The corporation cannot source these anywhere else, and the player paid for them in gate time, power and risk rather than in silver. |
| **Ordinary valuables** | **×0.85** | Instant, no trader, no caravan, no travel. The company takes a cut for that. |

**Traders stay the better price for ordinary goods if you are willing to wait for one**, and that is deliberate. A company paying full market would make every trader who buys valuables pointless and would make the convenience free. Paying *above* market for odd and *below* for ordinary is what keeps the two economies pulling in different directions instead of one swallowing the other.

It also gives gold and silver a job they did not have. Until now a vault of gold was dead weight until a trader turned up wanting it.

Value comes from each thing's own `MarketValue`, so the exchange tracks the game's economy and any mod that reprices anything — rather than a table this mod would have to maintain against 294 others.

## Everything in range, because that contract already exists

The exchange runs on a designated credit beacon's radius and takes **everything tradeable inside it**. That is exactly what a Core orbital trade beacon already means — *what is in the circle is what is on the table* — so it borrows a mental model the player has rather than inventing selection rules. **The radius is the control.**

The gizmo shows the split before committing: how many items, total credits, and how much of that is the odd premium.

**Bonds in range are never sold.** A bond is already credits; banking one is a different action with a different meaning, and quietly selling a million-credit bond at 0.85 would be a way to destroy a player's money by accident. Pawns and corpses are excluded outright.

**Valued first, then destroyed, then posted as a single transaction** — the same shape bond banking uses, so a reload mid-sale cannot credit a subset twice.

## Withdrawal: the ladder is the menu

The amounts offered are **the denomination ladder itself**, filtered to what the account can cover, largest first. No number to type, no slider, and no way to ask for an amount that cannot be represented: pick a rung, get exactly one bond of that size.

That is honest about what is happening — the corporation prints a specific instrument, it does not dispense change. Withdrawing a larger sum is what `IssueBonds` is for, and it still pays out largest-first as required.

## The loop, end to end

1. Cross a gate, work a coordinate, haul things out. They are **odd**.
2. An odd-supply contract wants them by origin — it cannot be filled from your own fields.
3. Or sell them at the beacon for **above market**, because nobody else has them.
4. Credits land in the account. Draw them as bonds; store them in a vault; lose them in a fire.
5. Spend them on catalogue access, which unlocks what the corporation will sell you.
6. Which makes the next coordinate survivable, and the pressure system means you need ordinary material down there to work at all.

## Not done, and named in `TODO.md`

- **Corporate catalogue balance**, and now **exchange-rate balance** with it. Both are constants in one place and neither has any play behind it.
- **A confirmation step on the sale.** Today the gizmo shows the total and the click is the commitment. With a full beacon that is a large irreversible action, and it deserves a confirmation before release.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled **twice** from clean; identical SHA-256.
- All four checkers pass. `check-keyed-strings.py`: 1,166 references all resolving, 0 duplicates, 0 argument mismatches.
- Compliance: **no new def of any kind**, no asset, no patch operation, no new work type. Eleven keyed strings added to an existing file.

## For the post-completion test phase

Confirming odd goods quote at 1.5× and ordinary at 0.85×; confirming a bond in range is never sold; confirming the quote matches what is actually credited; reloading mid-sale and confirming no double credit; confirming pawns and corpses are untouched; withdrawing each rung and confirming exactly one bond of that size appears and the account falls by exactly that much; and confirming the withdraw menu offers nothing the account cannot cover.
