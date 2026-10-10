import io

# --- CHANGELOG
p = 'CHANGELOG.md'
s = io.open(p, encoding='utf-8').read()
entry = """# Changelog

## 0.7.0-dev - 2026-09-29 - a cutoff you can throw

- **A gate can now be given an emergency cutoff**: a power switch on its own circuit that somebody can throw to shut an open gate at once.
- **The switch has to actually carry the gate's power.** One that is not wired into the line feeding the gate cannot be chosen at all, and says why. No believing in a cutoff that would not work.
- Throwing it ends the opening immediately and says so plainly — *the cutoff was thrown*, not *the power failed*. Those were the same message before, and they are not the same event.
- **Anyone still on the other side keeps their emergency return window.** That window is the whole reason the gate holds its own power reserve, and one flick should not strand people for good.
- Throwing a switch is ordinary work, so you can order somebody at home to do it while a team is still inside. That is what it is for.
- Gates without a cutoff work exactly as before. Nothing needs rebuilding or rebinding.

Worth knowing: cutting a gate's power already closed it. What was missing was the gate knowing *which* switch was its own, checking that the switch really powers it, and telling you apart a deliberate shutdown from a broken wire.

Full record: [the kill switch](docs/implementation/GATE_KILL_SWITCH_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""
s = s if '0.7.0-dev' in s else s.replace("# Changelog\n\n", entry, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

# --- TODO
p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()
old = """- [ ] **"we also need to have the ability to use a switch so cutting power instantly closes the lab gate in emergencies"**"""
new = """- [x] **"we also need to have the ability to use a switch so cutting power instantly closes the lab gate in emergencies"** — **BUILT 0.7.0-dev.** An optional cutoff bound to a Core power switch, refused unless the switch is **closed and on the gate's own power net**, which is what separates a real kill switch from a decorative one: sharing a net while closed means opening it *necessarily* severs the supply, using Core's own power graph rather than simulating anything. Thrown ends the opening at once with its own cause, checked **before** the generic power test so a deliberate shutdown is never logged as a snapped conduit. **The emergency-return window is deliberately kept** — it is why the gate reserves watt-days, and one flick should not permanently strand the far side. Record `implementation/GATE_KILL_SWITCH_IMPLEMENTATION.md`. Was: """
assert old in s
s = s.replace(old, new, 1)
old = """- [ ] **"idk think of cool shit in how all the equipment needs to connect and operate for a lab gate"**"""
new = """- [x] **"idk think of cool shit in how all the equipment needs to connect and operate for a lab gate"** — answered by making the **wiring real rather than cosmetic**: the bind is refused unless the switch genuinely carries the gate's power, matched by capability (`CompFlickable` + `CompPowerTransmitter`) so a modded switch works unnamed, one switch to one gate, and the whole thing optional so no saved gate needs rebinding. A further consequence fell out for free: flicking is ordinary `Flick` work and this mod gained cross-gate `BasicWorker` support in 0.6.7-dev, so somebody at home can be ordered to throw the cutoff while a team is still inside. Was: """
assert old in s
s = s.replace(old, new, 1)

block = """### Owner direction — the gate must keep meeting its requirements, and a how-to is owed (2026-09-29)

**Verbatim owner request (2026-09-29):** *"and remember the gate doent always stay open we need requirment s to be maintained and reached.. ie power(its a big draw if power runs out gate closes, research(maintained amounts of maintance and research on equipment but not crazy amounts like i say the first gate opening should be liek 30minuites real time only increasing from there, and eventually we will need to write a how to to the game paly and systems"*

**Checked against the shipped values rather than assumed. Three of the four already match exactly**, and saying so is more useful than rebuilding them:

- [x] **"power(its a big draw if power runs out gate closes"** — already true every tick: `HasPowerAndHeadroom()` fails and `TickGate` calls `EnterEmergency("RR_Gate_PowerLost")`. An open gate also spends energy every tick through `SpendNativeOpeningTick()`, so running the supply dry ends a sustained session exactly as losing power does.
- [x] **"the first gate opening should be liek 30minuites real time"** — already exactly that. `portalBaseWindowTicks = 108000`, and 108,000 ÷ 60 ticks per second = **1,800 seconds = exactly 30 real minutes** at normal speed.
- [x] **"only increasing from there"** — already: `portalWindowMultiplierPerTier = 3f` per earned tier, and `portalIndefiniteTier = 4` stops the countdown entirely while power, operator and energy hold.
- [x] **"research"** — already: tiers come from **completed** projects listed in `portalWindowTierProjects`, never from spendable insight, so a tier can never be lost by spending currency on the next one.
- [ ] **"maintained amounts of maintance ... on equipment but not crazy amounts"** — **GENUINELY NEW. There is no equipment-upkeep concept anywhere in the gate today.** Needs its own checkpoint: what wears, what restores it, what lapsing costs, and the owner's explicit ceiling that it must not be *"crazy amounts"*. Build it from existing content only — Core's own repair, `CompRefuelable`, breakdown or bill-driven servicing, matched by capability rather than by name.
- [ ] **"eventually we will need to write a how to to the game paly and systems"** — a player-facing how-to for the gameplay and the systems. `docs/HOWTO.md` exists but documents **the build**, not play. This is a real deliverable and is owed; scope it once the systems stop moving.

"""
old = "### Owner direction — a kill switch for the laboratory gate (2026-09-29)"
assert old in s
s = s.replace(old, block + old, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

# --- DEFERRED
p = 'docs/DEFERRED.md'
s = io.open(p, encoding='utf-8').read()
old = "- [ ] **A kill switch for the laboratory gate** — newly requested 2026-09-29, recorded verbatim in `TODO.md`, not yet built."
new = ("- [x] **A kill switch for the laboratory gate** — **BUILT 0.7.0-dev.** Refused unless the switch is closed and on the gate's own power net, which is the condition that makes it real rather than decorative. The emergency-return window is deliberately kept.\n"
       "- [ ] **Equipment maintenance on the gate** — requested 2026-09-29 and **genuinely new**: no upkeep concept exists in the gate today. The owner's ceiling is explicit — not *\"crazy amounts\"*. Its own checkpoint.\n"
       "- [ ] **A player-facing how-to for the gameplay and systems** — requested 2026-09-29. `docs/HOWTO.md` documents the build, not play. Owed; scope it once the systems stop moving.")
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

# --- NOW
p = 'docs/NOW.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace("| Published | 0.6.9-dev (`git log -1`; the cascade read-back is in `FINALIZED.md`) |",
              "| Published | 0.7.0-dev (`git log -1`; the cascade read-back is in `FINALIZED.md`) |")
s = s.replace("| Build | 118 C# source files, 76 approved package files, zero warnings, zero errors |",
              "| Build | 119 C# source files, 76 approved package files, zero warnings, zero errors |")
s = s.replace("| Assembly | SHA-256 `33DBB4EF977C7539CAF4E5C066BA29DA437602B37CFC9FC5C101CBC4FCD38A8D`, reproduced by two full recompiles after deleting `obj/` and `bin/` |",
              "| Assembly | SHA-256 `3E0DA100B9C78E32AE733429B6F2FAEC48471F46AE40D1A1B11265171BB71464`, reproduced by two full recompiles after deleting `obj/` and `bin/` |")
s = s.replace("- **Register checkpoint, still 0.6.4** —",
              "- **0.7.0** — **the gate kill switch**: an optional cutoff bound to a Core power switch, refused unless it genuinely carries the gate's power.\n- **Register checkpoint, still 0.6.4** —", 1)
old = "   **Also queued:** the owner's **kill switch** for the laboratory gate, captured verbatim in `TODO.md`."
new = ("   **Also queued:** ~~the kill switch~~ (BUILT 0.7.0-dev), and two things newly asked for and **not** built — **equipment maintenance on the gate** (genuinely new; no upkeep concept exists, and the owner's ceiling is explicitly not *\"crazy amounts\"*) and a **player-facing how-to for the gameplay and systems** (`docs/HOWTO.md` covers the build, not play). Both verbatim in `TODO.md`.\n"
       "   **Confirmed rather than changed** by that same direction, checked against shipped values: power loss already closes an open gate every tick; the first opening is already **exactly 30 real minutes** (`portalBaseWindowTicks = 108000` ÷ 60 ticks per second = 1,800 seconds); it already only increases from there (×3 per tier); and tiers already come from completed research.")
assert old in s
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print("ledger updated for 0.7.0-dev")
