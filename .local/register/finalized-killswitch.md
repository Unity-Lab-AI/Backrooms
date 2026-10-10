
---

## 2026-09-29 — The kill switch, and what cutting power already did (0.7.0-dev)

### Verbatim owner requests

> *"get to the work we are doing everything to get this mod 100% and outstanding awesomeness"*

> *"we also need to have the ability to use a switch so cutting power instantly closes the lab gate in emergencies.. idk think of cool shit in how all the equipment needs to connect and operate for a lab gate"*

> *"and remember the gate doent always stay open we need requirment s to be maintained and reached.. ie power(its a big draw if power runs out gate closes, research(maintained amounts of maintance and research on equipment but not crazy amounts like i say the first gate opening should be liek 30minuites real time only increasing from there, and eventually we will need to write a how to to the game paly and systems"*

### What already happened, established before anything was built

- [x] **Cutting power to an open gate already closed it.** `TickGate` tests `HasPowerAndHeadroom()` every tick and calls `EnterEmergency("RR_Gate_PowerLost")` when it fails, starting the bounded emergency-return window. And Core's own `Building_PowerSwitch` stops transmitting when open, so a switch wired upstream **already** cut the supply and **already** closed the gate. The physics was most of the way there.
- [x] **What was missing was everything that makes it a control rather than an accident** — the gate had no idea which switch was *its* switch; nothing verified the switch was on the gate's circuit, so a player could build one, believe in it, and find out otherwise in the one moment it mattered; and a deliberate shutdown and a snapped conduit produced the **identical** message. All three closed.

### The design: the wiring is real, not cosmetic

- [x] **A switch may only be bound while closed and on the gate's own power net.** That single condition is what separates a real kill switch from a decoration: sharing a net while closed means opening it **necessarily** severs the gate from its supply, using Core's own power graph rather than simulating anything. Requiring it closed at bind time is *why* the check can be that simple — an open switch has already split the net, so there would be nothing to compare.
- [x] **Matched by capability, never by name** — anything with both `CompFlickable` and `CompPowerTransmitter` qualifies, so a modded switch works with nothing here naming it. One switch serves one gate; two gates sharing a cutoff would mean one flick closed both.
- [x] **Checked before the generic power test, and that ordering is the point.** A thrown switch would cut the supply a tick later anyway and the cause recorded would be *power lost* — indistinguishable from a broken wire. Somebody threw this, and the log, the readout and the activity record all say so.
- [x] **The emergency-return window is deliberately kept.** It is the entire reason the gate reserves its own watt-days; removing it would mean one flick permanently strands everybody on the far side. *"Instantly closes"* is honoured as **the opening ends the moment the switch is thrown** — sealed to new traffic — while those already through keep the bounded chance to come back that every other emergency gives them.
- [x] **A consequence worth stating out loud, because it is a feature.** Flicking is ordinary colonist work through Core's `Flick` designation, and cross-gate `BasicWorker` support landed in 0.6.7-dev. So somebody at home can be **ordered to throw the cutoff while a team is still inside** — exactly the scenario an emergency cutoff exists for, with the return window keeping it a decision rather than an execution.
- [x] **Optional, as a separate call rather than a fourth argument** on `BindNativeInfrastructure`, so every existing binding is untouched and no saved gate needs rebinding. `KillSwitch` re-derives from its saved reference on every read, so a deconstructed or relocated switch stops being the cutoff with nothing having to clear it.

### The follow-up direction: three of four already matched exactly

Checked against shipped values rather than assumed, because saying so is more useful than rebuilding them.

- [x] **"power(its a big draw if power runs out gate closes"** — already true every tick, and an open gate also spends energy through `SpendNativeOpeningTick()`, so running the supply dry ends a sustained session exactly as losing power does.
- [x] **"the first gate opening should be liek 30minuites real time"** — **already exactly that.** `portalBaseWindowTicks = 108000`; 108,000 ÷ 60 ticks per second = **1,800 seconds = 30 real minutes** at normal speed.
- [x] **"only increasing from there"** — already: `portalWindowMultiplierPerTier = 3f` per earned tier, and `portalIndefiniteTier = 4` stops the countdown entirely while power, operator and energy hold.
- [x] **"research"** — already: tiers come from **completed** projects in `portalWindowTierProjects`, never from spendable insight, so a tier cannot be lost by spending on the next one.
- [ ] **"maintained amounts of maintance ... on equipment but not crazy amounts"** — **GENUINELY NEW and not built.** There is no equipment-upkeep concept anywhere in the gate. Recorded verbatim with the owner's explicit ceiling, and scoped to its own checkpoint for the same reason the kill switch was not folded into the emergence work it interrupted.
- [ ] **"eventually we will need to write a how to to the game paly and systems"** — a player-facing how-to. `docs/HOWTO.md` exists but documents **the build**, not play. Owed, and recorded.

### Saved state

One reference, `rr_gateKillSwitch`, defaulting to null. A 0.6.9-dev save loads unchanged.

### Documents updated in the same change

`implementation/GATE_KILL_SWITCH_IMPLEMENTATION.md` (new record), `TODO.md` (two owner directions captured verbatim, with the four already-satisfied rows checked off against shipped values rather than rebuilt), `DEFERRED.md`, `NOW.md`, `CHANGELOG.md`, `About.xml`, the csproj.

### Build evidence

0.7.0-dev, SDK 9.0.308, Release/net472, zero warnings and zero errors with `TreatWarningsAsErrors` enabled. **119** C# source files (one new), **76** approved package files (unchanged; fourteen keyed strings added to an existing file — **no new def, no patch operation, no asset**). Assembly SHA-256 `3E0DA100B9C78E32AE733429B6F2FAEC48471F46AE40D1A1B11265171BB71464`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. Evidence folder `implementation/evidence/gate-kill-switch-2026-09-29/`. `check-keyed-strings.py` 1,128 keys with 0 duplicates and 0 argument mismatches; `check-dlc-gating.py` passes; `audit-gate0.py` PASS with zero errors; reference manifest recomputed with no drift; no attribution strings. Published via the cascade in `PUBLISHING.md`; refs read back in session output. No game launched, no test run, no RimSort profile touched.

### SESSION SUMMARY

Source files created: 1. Source files modified: 2. Package files modified: 2 (no new files). Docs updated: 6 (1 new).
Owner directions captured verbatim: 3.
**Owner requirements confirmed as already shipped rather than rebuilt: 4**, including the 30-minute first opening, which matches the shipped constant exactly.
New work identified and deliberately deferred to its own checkpoint: 2 (equipment maintenance, the player how-to).
Feature shape: optional, additive, no new def or asset, and refused unless the wiring genuinely carries the gate's power.
