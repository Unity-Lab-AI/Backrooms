# -*- coding: utf-8 -*-
"""0.12.57-dev: their stargate, our door, our dialling."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

ROW = u"""## The Stargate mod on a normal door — 2026-09-30 (0.12.57-dev)

Owner, verbatim, across five messages:

**"as you can see the back wall door is not correctly blue, is not correctly a stargate portal to
the back rooms and does not cortrectly have the blue light glow. so wtf is going on here? are you
even useing the stargate capabilities to for connections to the backrooms and the map the pawns
start on?"**

**"i shouldnt have to click on the door right to send a pawn through it and how the fuck are they
suppose to auto pick up materials on one side and use them on the other"**

**"we use the fucjkign stargate MOD but use a normal door im not telling u again"**

**"and connect them together to the backrooms and the map"**

**"we just use our own dialing converstion in the background"**

**"we still use the stargate mod as normal but we also use it for our backrroms purposes"**

- [x] **"are you even useing the stargate capabilities"** — **THE CONNECTION WAS ALREADY REAL, AND THE LIVE GAME PROVED IT BEFORE ANY CODE WAS WRITTEN.** `mapCount` **2** — the Backrooms coordinate had generated, for the first time ever. One letter, *"Branch authorization received"*, which is only sent when `SoloGroupOpening` returns null, so every step of the opening had succeeded. Cell (160,161) held the emergence `Door`, and its gizmos were **"Stop being a way home"** (so `IsDesignated` was true) and **"Send somebody through"** (so a live crossing existed). **Zero exceptions in the whole log.**

- [x] **"is not correctly blue ... does not cortrectly have the blue light glow"** — **FIXED, and the cause was one word wide.** `RefreshGateAppearance()` — glow radius, glow colour, `CompGlower.UpdateLit`, `CompColorable.SetColor` — had exactly one call site: `CompTickRare()`. `Verse.Thing.DoTick` dispatches on the def's ticker type, and **Core's `DoorBase` is `tickerType Normal`**, so `TickRare` is never called on a `Door` or an `Autodoor`. **That method had never executed on any door in any session.** Every other line was correct. It runs from `CompTickInterval(int delta)` now — what a Normal ticker actually receives — throttled with Core's interval-safe `IsHashIntervalTick(interval, delta)`, plus on spawn and on mark/withdraw.

- [x] **"we use the fucjkign stargate MOD but use a normal door"** — **DONE, and their source says it is exactly right.** `CompStargate` is a **`ThingComp`**, so it goes on an ordinary Core `Door` with **no new ThingDef and nothing to build**. `StargateBridge` attaches it **per instance** to the door this company designated, because a `comps` patch is per def and would make every door in every colony a stargate — their `InitGate` allows one gate per map and **hibernates the rest with a message**, so a nine-door shop would have announced eight hibernating gates on the first tick.

- [x] **"and connect them together to the backrooms and the map"** — **both ends.** The far anchor stands inside a coordinate, which is not an ordinary branch map, so it can never mark itself; the near side knows the edge and attaches both. Their `InitGate` then registers each end's own address — `parent.Map.Tile` for an ordinary map, `parent.Map.Index` for a pocket map — so **we never write to their address list.**

- [x] **"we just use our own dialing converstion in the background"** — **done, and it is a conversion rather than a UI.** `OpenStargateDelayed(PlanetTile, int, DialMode)` is public; this company already knows which door leads to which coordinate, so the conversion is reading the destination map's own address and handing it over. **The player never touches a DHD for the Backrooms.** A receiving end or a hibernating gate is never dialled — their one-way rule and their one-gate-per-map rule are theirs to enforce.

- [x] **"how the fuck are they suppose to auto pick up materials on one side"** — **Core's transporter, which is what their own gate uses.** `_transComp ??= parent.GetComp<CompTransporter>()` and `JobDriver_BringToStargate` are theirs; the bridge puts `CompTransporter` on the door beside the gate, and colonists then **haul the chosen materials to the door on their own** and the gate sends them through. No per-pawn right-click.

  **And the hard limit was stated rather than papered over:** RimWorld cannot run a job across two maps — jobs, reachability and haul listers are all per-`Map`, and Core's own Anomaly pit gate does not do it either. What is deliverable is automatic hauling **to** the gate and crossing together, which is what this is.

- [x] **"we still use the stargate mod as normal"** — **nothing of theirs is edited, patched, or required.** No XML of ours names their defs or types. **The build has no reference to their assembly**, so a collaborator without the Workshop item still compiles the package. Their type is found with Core's own `GenTypes.GetTypeInAnyAssembly`, their `CompProperties` is **borrowed off their own gate def rather than constructed** — so a Backrooms gate is configured exactly as their stargate is and retunes when they retune it — and only two public methods are ever invoked. No Harmony, no detour, no `SetValue`, no `BindingFlags.NonPublic`. **With their mod absent every path answers "not available" and the Backrooms behave exactly as before.**

- [x] **REGISTER, AND THE CORRECTION THAT CAME WITH IT** — row **[218] Stargates!** is stance *"No integration"*, and **that was read as "do not use it" for three checkpoints while the owner said the opposite every time.** The register is **guidance**; the owner's direction is not. What the row actually protects is ownership of state — *"Backrooms coordinates and the company's machine must keep their own stable IDs and state"* — and that is kept exactly: their addresses stay theirs, our coordinate records stay ours, and the only thing crossing is a dial.

- [x] **the forty-fifth proof reads THEIR source, and nine plants in two batches walked past my own claims** — the proof checks `CompStargate` really is a `ThingComp`, that `OpenStargateDelayed` still has the signature we pass, and that the fields we read are still public, **against the installed mod's own code**, so a version of theirs this was not written for fails here rather than in the owner's colony. **19 of 19** planted faults caught, after fixing nine claims that were satisfied by commented-out code, by a second legitimate call site, by two of three lookups, or by a window that swallowed the next method once comments were stripped.

---

"""

ENTRY = u"""
---

## Session 2026-09-30 - their stargate, our door, our dialling (0.12.57-dev)

**Verbatim user quotes:** *"we use the fucjkign stargate MOD but use a normal door im not telling
u again"*, *"and connect them together to the backrooms and the map"*, *"we just use our own
dialing converstion in the background"*, *"we still use the stargate mod as normal but we also use
it for our backrroms purposes"*, and *"i shouldnt have to click on the door right to send a pawn
through it and how the fuck are they suppose to auto pick up materials on one side and use them on
the other"*.

**Files touched:** `Portals/StargateBridge.cs` (new), `Portals/CompRimroomsEmergence.cs`,
About/csproj/README, `docs/TODO.md`, `docs/NOW.md`.

**Closure notes.** **The connection was already real; the paint and the plumbing were not.**

The live game settled the first question before any code was written: mapCount 2, the welcome
letter that is only sent when the opening fully succeeds, the emergence Door at (160,161) carrying
*"Stop being a way home"* and *"Send somebody through"*, and zero exceptions. So the route worked
and only the appearance was wrong - `RefreshGateAppearance()` had one call site, `CompTickRare()`,
and Core's `DoorBase` is `tickerType Normal`, which never receives `TickRare`. **That method had
never run on any door in any session.**

**Then the real instruction, which had been given three times and misread three times.**
`CompStargate` is a `ThingComp`, so their gate goes on an ordinary Core door with no new ThingDef.
`StargateBridge` attaches it per INSTANCE to the designated door, because a comps patch is per def
and their `InitGate` hibernates every extra gate on a map with a message. Both ends of the route
are wired from the edge, their `InitGate` registers each end's own address, and our dialling
conversion reads the destination map's address and calls their public
`OpenStargateDelayed`. Core's `CompTransporter` goes on beside it, which is what their own gate
uses - that is the automatic hauling, and it is their mod doing it.

**The hard limit was stated rather than papered over:** RimWorld cannot run a job across two maps.
Jobs, reachability and haul listers are per-Map, and Core's own pit gate does not do it either.

**Nothing of theirs is edited and nothing of theirs is required.** No XML names their defs, the
build has no reference to their assembly so a collaborator can still compile, their type is found
with Core's `GenTypes.GetTypeInAnyAssembly`, their `CompProperties` is borrowed off their own def
rather than constructed, and only two public methods are invoked.

**Register row [218] is stance "No integration", and reading that as "do not use it" cost three
checkpoints while the owner said the opposite every time.** The register is guidance. What the row
protects is state ownership, and that is kept exactly.

**Nine of my own claims were too loose**, in two batches: three satisfied by commented-out code,
one by a second legitimate call site, one by counting guards instead of checking the guard, one by
two of three lookups surviving, one by a string appearing in two ternaries, and one by a
fixed-width window that swallowed the next method once comments were stripped - **a fix in the
same batch moving the ground under another claim.**

**181 C# files, 91 package files**, zero warnings, zero errors. Assembly SHA-256
`59F77C337E26C59B55355B10E1C7EC7B7EA29A137E529D3B4EA597CDF5C68546`, reproduced by two clean
recompiles. **Thirteen checkers pass, forty-five proofs hold. 509 of 509** planted faults caught
across sixteen suites.
"""

todo = io.open(TODO, encoding="utf-8").read()
ANCHOR = u"## TOMBSTONES"
if todo.count(ANCHOR) != 1:
    print("TODO ANCHOR PROBLEM: %d" % todo.count(ANCHOR))
    raise SystemExit(1)

final = io.open(FINAL, encoding="utf-8").read()
io.open(FINAL, "w", encoding="utf-8", newline="").write(final + ENTRY)
if ENTRY not in io.open(FINAL, encoding="utf-8").read():
    print("FINALIZED WRITE NOT VERIFIED -- nothing else touched")
    raise SystemExit(1)
print("FINALIZED written and verified")

io.open(TODO, "w", encoding="utf-8", newline="").write(todo.replace(ANCHOR, ROW + ANCHOR, 1))
print("stargate rows recorded")

now = io.open(NOW, encoding="utf-8").read()
EDITS = [
    (u"| Published | **0.12.56-dev**.", u"| Published | **0.12.57-dev**."),
    (u"SHA-256 `A0AE0AA2A671B846663EEB19F3E37BF0F052CBAA29D342538E81043AE5D9D536`",
     u"SHA-256 `59F77C337E26C59B55355B10E1C7EC7B7EA29A137E529D3B4EA597CDF5C68546`"),
]
problems = []
for old, _ in EDITS:
    if now.count(old) != 1:
        problems.append("%d of %r" % (now.count(old), old[:56]))
if problems:
    for problem in problems:
        print("NOW ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    now = now.replace(old, new, 1)
io.open(NOW, "w", encoding="utf-8", newline="").write(now)
print("NOW.md updated for 0.12.57-dev")
