# -*- coding: utf-8 -*-
"""The battery limit, owner's words verbatim."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")

ANCHOR = u"---\n\n## TOMBSTONES"

ENTRY = u"""---

## IN PROGRESS - one battery was the whole reserve - 2026-10-01 (0.12.77-dev)

Owner, verbatim, from a running game:

> **"its the same problem as before: the laboratory address for that is not open.... thats just
> clicking on the portal and trying to send them through not working,,, and using operations
> clicking send pawns through which i think is a power porblem but you can check the game current
> running,, looks like only being able to connect 1 battery isnt anough and there should be no
> loimit"**

**The owner's diagnosis is correct and the mechanism is worse than the symptom suggests.**

- [~] **"only being able to connect 1 battery isnt anough and there should be no loimit"** - a gate
  binds `private Thing nativeBattery`, **one battery**, and `NativeStoredEnergy` reads that one
  battery's `StoredEnergy`. **Every battery else on the same power net counts for nothing.** The
  bound battery was only ever meant to be the anchor that identifies the gate's circuit --
  `NativeGenerationWatts` already sums the whole net, and `NativePowerConnected` already checks
  the whole net. **The stored energy was the one reading that never followed**
- [~] **"the laboratory address for that is not open"** - the refusal is
  `RR_PortalTravel_SessionClosed`, produced by `RimroomsPortalNetwork.Availability` when
  `gate.HasUsablePortalWindow(...)` returns false. Its last condition is
  `NativeStoredEnergy >= OpeningPowerDrawWatts * WattsToWattDaysPerTick`, **checked on every
  attempt to cross**, so a drained bound battery reads as *the connection is not open* rather than
  as *the gate has no charge*. **The message names the wrong thing**, which is why it looked like
  an address fault
- [~] **"thats just clicking on the portal and trying to send them through not working"** - same
  cause, same predicate. Both routes ask `Availability` first
- [~] **"which i think is a power porblem"** - **it is.** And the spend is worse than the read:
  `TrySpendNativeEnergy` refuses outright when `battery.StoredEnergy < remaining`, so a drained
  bound battery stalls the gate **with ten full batteries beside it on the same net**
- [~] **"you can check the game current running"** - **the bridge was not reachable**, so this was
  diagnosed from the source rather than from the running game. Said plainly because a diagnosis
  from reading is a weaker claim than a diagnosis from observing, and the difference matters
- [ ] **`returnReserveCapacityWattDays` is 2 and a Core `Battery` holds 600**, so the bind-time
  *ReserveTooSmall* refusal is **not** the cause. Checked and ruled out rather than assumed
"""

text = io.open(TODO, encoding="utf-8").read()
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(TODO, "w", encoding="utf-8", newline="").write(
    text.replace(ANCHOR, ENTRY + u"\n" + ANCHOR, 1))

after = io.open(TODO, encoding="utf-8").read()
if u"only being able to connect 1 battery isnt anough and there should be no" not in after:
    print("VERBATIM MISSING")
    raise SystemExit(1)
print("TODO opened for the battery defect; owner's words verbatim and verified")
