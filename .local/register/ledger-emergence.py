import io

# --- evidence folder is generated separately; this is the ledger only.

# --- CHANGELOG
p = 'CHANGELOG.md'
s = io.open(p, encoding='utf-8').read()
entry = """# Changelog

## 0.6.9-dev - 2026-09-29 - a way out, and it comes up where you said

- **A doorway in the Backrooms can now lead back out into the world**, instead of only ever leading deeper. Roughly one in three ways onward does, once you have somewhere for it to come up.
- **You choose where it comes up.** Any door on a map you hold can be marked as a way home, with one command on the door itself. Nothing is ever marked for you — a way out only ever arrives at a door you picked.
- A door inside the Backrooms cannot be marked, because a way out cannot come up in the place it leads away from.
- With nothing marked, doorways simply lead deeper as before. Nothing is refused and nothing is lost.
- The same doorway always leads to the same place. Saving, reloading and revisiting never change it.
- Unmarking a door stops new ways out coming up there, and deliberately leaves any that already exists alone.

Two unrelated fixes found while working: one message on the gate was sharing a name with another, so one of the two was always wrong — the operator-away refusal and the operator readout now have separate names. And there is now a check that no two messages can share a name again.

Full record: [a way out](docs/implementation/CONNECTED_EMERGENCE_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

"""
s = s if '0.6.9-dev' in s else s.replace("# Changelog\n\n", entry, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

# --- TODO: owner directions verbatim (emergence close + the kill switch, newly asked)
p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()
block = """### Owner direction — a kill switch for the laboratory gate (2026-09-29)

**Verbatim owner request (2026-09-29):** *"we also need to have the ability to use a switch so cutting power instantly closes the lab gate in emergencies.. idk think of cool shit in how all the equipment needs to connect and operate for a lab gate"*

Not yet built. Recorded here in full the moment it was asked so it cannot be lost, and scoped to its own checkpoint rather than folded into the emergence work that was in flight.

- [ ] **"we also need to have the ability to use a switch so cutting power instantly closes the lab gate in emergencies"** — a player-operable switch that closes an open laboratory gate at once by cutting its power. What already exists to build on: `CompRimroomsGate` is a native provider carrying `nativeConsole`, `nativeBattery` and `nativeAssemblyBench`; `NativeBindingFailureKey` already reports `RR_NativeGate_PowerUnavailable` when power is unavailable; and there is already an emergency-return window with its own reserved watt-days. What is missing is the **deliberate** act: cutting power today makes a gate *unavailable*, which is not the same as *closing it now on purpose*, and the difference matters when somebody is on the far side.
- [ ] **"idk think of cool shit in how all the equipment needs to connect and operate for a lab gate"** — open design latitude on how the equipment interconnects. Read `implementation/CONNECTED_TRAVEL_IMPLEMENTATION.md` and the gate records before proposing, and keep every piece existing content: Core's own `PowerSwitch`, conduits, batteries and consoles, matched by capability rather than by name.

### Owner direction — the other half of the topology: a way out into the world (2026-09-29)

**Verbatim owner requests, carried from the topology direction:** *"and or pop out any where in the game world on a tile map"*, and the worked examples *"map>backrrooms>backrroms , map > backrooms > map > backrooms , and backrromms > map>backrooms>backrooms>map"*.

Record: [`implementation/CONNECTED_EMERGENCE_IMPLEMENTATION.md`](implementation/CONNECTED_EMERGENCE_IMPLEMENTATION.md).

- [x] **A portal whose far side is an ordinary map** — **BUILT 0.6.9-dev** as `PortalConnectionKind.Emergence`, an appended enum value. Recorded **anchor-first** (`First` = the marked door on the ordinary branch-owned map, `Second` = the coordinate doorway), which is the same orientation every other kind uses — so `Availability`, the site check in `Register` and the uniqueness rule all needed **no change at all**. This is what makes `map > backrooms > map > backrooms` and `backrooms > map > backrooms > backrooms > map` route end to end.
- [x] **The player marks where it comes up, and nothing ever picks for them** — `CompRimroomsEmergence` on Core `Door` and `Autodoor`, added by one additive patch beside the existing gate comp, dormant until marked. This inherits 0.6.3-dev's rule with more force, because a way out arrives **at** the player's own map: *a door the player built is never quietly turned into a hole in the world*. Marking is refused inside the Backrooms — a way out cannot come up in the place it leads away from — and the command is not even offered there.
- [x] **Withdrawing a mark leaves an existing way out alone** — it means "no more ways out here", not "close the one that exists". A saved edge is evidence of a place somebody found.
- [x] **Found by surveying, with its own independent draw** — a distinct seed key from the frontier draw so the two can never correlate, derived from the coordinate's own seed and the doorway's position so it is stable across saves and revisits. **One in three** ways onward leads out, deliberately common, because a way home is what makes the topology usable rather than a trap. With nothing marked the doorway leads deeper instead: a fallback, not a refusal.
- [ ] **A world tile the branch does not hold** — still the larger half, needing a new world object and a generated map. Its own checkpoint.
- [ ] **`Area_BuildRoof`, `Area_NoRoof`, `Area_SnowOrSandClear` and `Area_PollutionClear` across a gate** — `research/ZONES_AND_AREAS_ACROSS_A_GATE.md` recorded these as a dependency of exactly this endpoint, and they are **now genuinely live rather than hypothetical**: an ordinary map is reachable through a gate, and a colony map gets snow, wants roofs built, and may be polluted.

"""
old = "### Owner direction — zones must work on both sides of any gate (2026-09-29)"
assert old in s
s = s.replace(old, block + old, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

# --- DEFERRED
p = 'docs/DEFERRED.md'
s = io.open(p, encoding='utf-8').read()
block = """## A way out of the Backrooms (2026-09-29)

Record: [`implementation/CONNECTED_EMERGENCE_IMPLEMENTATION.md`](implementation/CONNECTED_EMERGENCE_IMPLEMENTATION.md).

- [x] **A portal whose far side is an ordinary map** — **BUILT 0.6.9-dev.** `PortalConnectionKind.Emergence`, appended. Recorded anchor-first, which made `Availability` and the register's site and uniqueness rules work unchanged. Superseded text, kept per the never-delete rule: *the cheap version, and genuinely useful: the far side is an already-owned ordinary map.*
- [x] **Keyed strings had no duplicate check, and there was a real duplicate** — `RR_Gate_OperatorAway` was declared twice in one file with two different texts and two different uses. Fixed, and `tools/check-keyed-strings.py` now enforces it.
- [ ] **A world tile the branch does not hold** — still open. A new world object and a generated map; its own checkpoint.
- [ ] **A kill switch for the laboratory gate** — newly requested 2026-09-29, recorded verbatim in `TODO.md`, not yet built.

"""
old = "## Zones and areas across a gate (2026-09-29)"
assert old in s
s = s.replace(old, block + old, 1)
s = s.replace("- [ ] **`Area_BuildRoof`, `Area_NoRoof`, `Area_SnowOrSandClear`, `Area_PollutionClear` across a gate** — not covered, and **correctly not covered while the far side of a gate is always a Backrooms coordinate**",
              "- [ ] **`Area_BuildRoof`, `Area_NoRoof`, `Area_SnowOrSandClear`, `Area_PollutionClear` across a gate** — **now genuinely live as of 0.6.9-dev**, because an ordinary map is reachable through a gate. Was correctly not covered while the far side of a gate was always a Backrooms coordinate", 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)

# --- NOW
p = 'docs/NOW.md'
s = io.open(p, encoding='utf-8').read()
s = s.replace("| Published | 0.6.8-dev (`git log -1`; the cascade read-back is in `FINALIZED.md`) |",
              "| Published | 0.6.9-dev (`git log -1`; the cascade read-back is in `FINALIZED.md`) |")
s = s.replace("| Build | 117 C# source files, 76 approved package files, zero warnings, zero errors |",
              "| Build | 118 C# source files, 76 approved package files, zero warnings, zero errors |")
s = s.replace("| Assembly | SHA-256 `4E474FF0A277861CB788A87C893714CF0C9A0CFC3834473B6972D8F4941C9930`, reproduced by two full recompiles after deleting `obj/` and `bin/` |",
              "| Assembly | SHA-256 `33DBB4EF977C7539CAF4E5C066BA29DA437602B37CFC9FC5C101CBC4FCD38A8D`, reproduced by two full recompiles after deleting `obj/` and `bin/` |")
s = s.replace("- **Register checkpoint, still 0.6.4** —",
              "- **0.6.9** — **a way out**: `PortalConnectionKind.Emergence`, a player-marked door on an ordinary map as the place a way out comes up. Plus a duplicated keyed string fixed and `check-keyed-strings.py` added.\n- **Register checkpoint, still 0.6.4** —", 1)
old = "2. **A portal whose far side is an ordinary map**, then **a world tile the branch does not hold.**"
new = "2. ~~**A portal whose far side is an ordinary map**~~ — **BUILT 0.6.9-dev.** Still open: **a world tile the branch does not hold**, which needs a new world object and a generated map."
assert old in s
i = s.index(old)
j = s.index("\n", s.index("a colony map has both.", i))
s = s[:i] + new + "\n   **Now live because of it:** `Area_BuildRoof`, `Area_NoRoof`, `Area_SnowOrSandClear` and `Area_PollutionClear` have no cross-gate route, and an ordinary map reachable through a gate genuinely gets snow, wants roofs built and may be polluted. See `research/ZONES_AND_AREAS_ACROSS_A_GATE.md`.\n   **Also queued:** the owner's **kill switch** for the laboratory gate, captured verbatim in `TODO.md`." + s[j:]
# ritual: run the keyed-string check too
old = "5b. **If any def was added or edited**"
new = ("5b. **If any keyed string or `RR_` literal changed**, run `python tools/check-keyed-strings.py`. It must exit zero. It catches duplicate keys (there was a real one, used for two different messages), unresolved references, and format arguments that do not line up.\n"
       "5c. **If any def was added or edited**")
assert old in s
s = s.replace(old, new, 1)
s = s.replace("5c. **If any register CSV changed**", "5d. **If any register CSV changed**", 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print("ledger updated for 0.6.9-dev")
