
---

## 2026-09-29 — The exchange, and credits back out as paper (0.7.7-dev)

### Verbatim owner requests

> *"get to it"*

> *"a way to turn gold silver gems ingots maybe needs to exchange for cradits with the company"*

> *"above market for (odd) resources"*

### What was built

- [x] **The rate is the whole design.** **Odd goods ×1.5** — the owner's answer, and justified: the corporation cannot source them anywhere else and the player paid in gate time, power and risk rather than silver. **Ordinary valuables ×0.85** — instant, no trader, no caravan, no travel, and the company takes a cut for that.
- [x] **Traders stay the better price for ordinary goods, deliberately.** A company paying full market would make every trader who buys valuables pointless and make the convenience free. Paying above market for odd and below for ordinary is what keeps the two economies pulling in different directions instead of one swallowing the other. It also finally gives gold and silver a job — until now a vault of gold was dead weight until a trader turned up wanting it.
- [x] **Value comes from each thing's own `MarketValue`**, so the exchange tracks the game's economy and any mod that reprices anything, rather than a table this mod would maintain against 294 others.
- [x] **Everything in range, because that contract already exists.** A Core trade beacon already means *what is in the circle is what is on the table*, so the exchange borrows a mental model the player has rather than inventing selection rules. The radius is the control, and the gizmo shows the split — item count, total, and how much of it is the odd premium — before committing.
- [x] **Bonds in range are never sold.** A bond is already credits; banking one is a different action with a different meaning, and quietly selling a million-credit bond at 0.85 would be a way to **destroy a player's money by accident**. Pawns and corpses excluded outright.
- [x] **Valued, then destroyed, then posted as one transaction** — the same shape bond banking uses, so a reload mid-sale cannot credit a subset twice.
- [x] **Withdrawal: the ladder is the menu.** Amounts offered are the denomination ladder filtered to what the account can cover, largest first. No number to type, no slider, no way to ask for an amount that cannot be represented. Honest about what is happening: the corporation prints a specific instrument, it does not dispense change.

### The loop now closes end to end

Cross a gate and haul things out — they are **odd**. An odd-supply contract wants them *by origin* and cannot be filled from your own fields; or sell them at the beacon **above market**, because nobody else has them. Credits land in the account. Draw them as bonds, store them in a vault, lose them in a fire. Spend them on catalogue access, which decides what the corporation will sell you. Which makes the next coordinate survivable — and the pressure system means you need **ordinary** material down there to work at all.

### Build evidence

0.7.7-dev, SDK 9.0.308, Release/net472, zero warnings and zero errors with `TreatWarningsAsErrors` enabled. **137** C# source files (two new), **84** approved package files (unchanged; eleven keyed strings added to an existing file). Assembly SHA-256 `ED36F5C73ADAF2C11230F0B22210B238386859C5D6CEB1FD3329CD97309CC617`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. All four checkers pass; `check-keyed-strings` 1,166 references all resolving. **No new def of any kind, no asset, no patch operation, no new work type.** No game launched, no test run, no RimSort profile touched.

### SESSION SUMMARY

Source files created: 2. Source files modified: 2. Package files created: 0. Docs updated: 5 (1 new).
Owner directions captured verbatim: 3.
Accidental-loss cases designed out before shipping: 1 — selling a player's own bonds at 0.85 while sweeping a beacon.
Still open and named in `TODO.md`, not deferred: a confirmation step on the beacon sale, which is a large irreversible action with only a gizmo click in front of it; and balance for both the catalogue fees and the exchange rates, neither of which has any play behind it.
