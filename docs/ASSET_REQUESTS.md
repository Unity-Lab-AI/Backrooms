# Asset requests — audio, gate animation, and the aura

Written 2026-10-06. **This is a brief for whoever authors the next assets**, with the engine
constraints that decide what is usable and the code facts that decide what is needed.

**Asset delivery — 2026-10-06:** all thirteen requested WAVs, eight shared charge frames (`RR_GateCharge_01..08`), six activation frames (`RR_GateActivation_01..06`) and eight calmer live/open frames (`RR_GateOpen_01..08`) are now present in the stated master and package folders, with provenance and explicit package entries: **35 new assets total**. See the [delivery and integration handoff](implementation/GATE_CYCLE_ASSET_DELIVERY.md) for exact paths, measurements and previews. **Files delivered does not mean playback/animation accepted:** integration is the continuing build agent's work. Concurrent SoundDef/call-site work appeared during delivery; inspect the current code and generated [asset catalog](wiki/assets.md) rather than treating the handoff's initial missing-consumer count as current. The one-shot admission switch, event bindings, sustainer lifecycle, aura and frame indexing must be reconciled by that agent. No new assets were staged or published by this delivery.

**Owner direction, verbatim:**

> *"an make a write up about any other audio we need for chatgpt to find and create"*
>
> *"and things like the gates activating animations and charge up and stuff"*
>
> *"can be still frame made into gif like thing or whatever the game needs"*
>
> *"and maybe have the auro for the gat be gate sensitive change color to the state of the gate and
> like strobe on charge up callibation and activation and shit like star trek warp core"*
>
> *"ramp up and down and rev"*

---

## Format, and why it is not negotiable

The four cues already shipping are **48 kHz, mono, 16-bit WAV, 0.6 to 2.0 seconds**. Match that.

| Rule | Reason |
|---|---|
| **Mono, always** | A map cue is positional. The engine places it in the world and pans it; a stereo file fights that and arrives sounding wrong at the edge of the screen |
| **48 kHz, 16-bit** | What the existing four are. A mixed-rate set is a mixing problem nobody will trace |
| **Masters outside the package** | Put sources in `assets/source/audio/`. A build check requires every shipped asset to have a master, and refuses one that has none |
| **No silence padding** | Trim hard at both ends. A cue with 200 ms of lead sounds late, and late reads as broken |

---

## What already exists

| Cue | Length | Played when |
|---|---|---|
| `RR_GatePowerRise` | 2.0 s | A gate draws its reserve |
| `RR_GateWarning` | 1.1 s | Six places: a fault, an incursion, an egress, a standing recall |
| `RR_FieldRadio` | 0.6 s | A crew notices something in the field |
| `RR_SpatialTell` | 1.4 s | The space itself misbehaves |

---

## ⛔ Read this before writing a loop ⛔

**The cue system refuses sustained sounds today.** `RimroomsAudio.Usable` rejects any `SoundDef`
with `sustain` set, because every existing cue is a one-shot and a sustainer that nobody stops runs
until the map unloads.

So a looping sound needs **code as well as a file**: a sustainer that is started on a state change
and explicitly stopped on the opposite one, including when the gate is destroyed, the map unloads
or a save is reloaded mid-cycle. **That is the risky half, not the audio.**

If a loop is not wanted, the ramp can be done entirely with one-shots — see the alternative in the
gate cycle below. **Deliver the one-shots first either way**: they are useful on their own, and the
loop can land later without re-cutting them.

---

## Priority 1 — the gate cycle

This is what the owner asked for by name: *ramp up and down and rev*.

The gate has four states a player can already see, and only one of them makes a sound today.

| State | What it is | Cue wanted | Length | Notes |
|---|---|---|---|---|
| **Spin-up begins** | An operator starts bringing the gate up | `RR_GateRampUp` | 2.0–3.0 s | The rev. Starts low and climbs. It should end *unresolved* — the listener should expect more |
| **Spin-up continues** | Work accrues over minutes | `RR_GateSpinLoop` | 2.0–4.0 s, **seamless loop** | Needs the sustainer work above. A warp-core idle: a low cycling hum with a faint periodic pulse |
| **Calibration beat** | Progress crosses each quarter | `RR_GateCalibrate` | 0.4–0.8 s | Short, dry, mechanical. Four of these per cycle, so it must not be annoying |
| **Activation** | The connection goes live | `RR_GateActivate` | 1.5–2.5 s | The payoff. This is the one a player will remember |
| **Live** | A connection is open | `RR_GateOpenLoop` | 3.0–6.0 s, **seamless loop** | Quieter than the spin loop. Presence, not drama |
| **Ramp down** | The connection closes normally | `RR_GateRampDown` | 2.0–3.0 s | The reverse of the rev, and it must *resolve* — closing is a safe outcome |
| **Emergency** | A fault, or a forced return | `RR_GateEmergency` | 1.5–2.5 s | Distinct from `RR_GateWarning`, which is already used for six smaller things. This one means *the gate itself has gone wrong* |

**The one thing to get right:** ramp-up ends unresolved and ramp-down resolves. That single contrast
is what tells a player whether the gate is becoming dangerous or becoming safe, without reading a
word.

**Without the loop**, use `RR_GateRampUp` on start, `RR_GateCalibrate` at each quarter, and
`RR_GateActivate` on completion. Four one-shots carry the whole cycle.

---

## Priority 2 — events that happen now and make no sound

Each of these is a real moment in the code with a letter or a state change behind it.

| Cue | Length | Played when |
|---|---|---|
| `RR_CutoffThrown` | 0.3–0.6 s | The emergency cutoff opens the circuit. A heavy mechanical clack |
| `RR_SectionAssembled` | 0.6–1.0 s | One of the gate's four assembly sections completes |
| `RR_JournalFiled` | 0.5–0.9 s | A filled journal reaches the records archive. Paper and a latch |
| `RR_AnalysisComplete` | 0.8–1.2 s | A researcher finishes analysing a finding |
| `RR_MarkerSet` | 0.3–0.5 s | A survey tag is given a meaning. A small click and a lamp |
| `RR_ContractPaid` | 0.8–1.2 s | The company pays out. Should feel like a receipt, not a jackpot |

---

## Priority 3 — the aura

**What exists:** one colour, `(70, 130, 220)` blue, on or off. `CompRimroomsEmergence` sets it when
a gate is live and clears it otherwise.

**What the owner asked for:** colour by state, and a strobe through charge-up, calibration and
activation — *"like star trek warp core"*.

**This needs no art at all.** Both the glow colour and its radius are settable per instance, so the
whole effect is code: interpolate the colour, and drive the radius from the spin-up fraction the
gate already computes.

A proposed palette, **to be approved rather than assumed** — the fairness rule in
`THREAT_DESIGN_SHEETS.md` binds here: *"Do not use colour or sound as the only way to notice a
tell."* Every state below already has text and a pane indicator. The aura is allowed to be
beautiful; it is not allowed to be the only signal.

| State | Colour | Behaviour |
|---|---|---|
| Designated, idle | dim blue | Steady, low radius |
| Spinning up | blue warming toward white | Radius climbs with the progress fraction; a pulse at each quarter |
| Live | the current blue | Steady, full radius. **Unchanged, so existing colonies look the same** |
| Emergency | amber | Slow strobe |
| Awaiting recovery | red | Faster strobe |

---

## Gate activation animation

**The frame is already drawn by us**, in `GateWorldFrames.PostDraw`, so an animation is a frame
index rather than a new engine concept. There is no video format in play: *"still frame made into
gif like thing"* is exactly right — it is a numbered sequence of PNGs and the code picks one.

**Do not author a sequence per footprint.** There are four footprints and three facings, so a
six-frame animation drawn that way is **72 files**, and every future footprint multiplies it.

**Author one overlay instead.** A single square sheet, stretched across whatever run it is drawn
over:

| Thing | Value |
|---|---|
| Files | `RR_GateCharge_01.png` … `RR_GateCharge_NN.png` |
| Size | **256 × 256**, square |
| Frames | **6 to 12.** Fewer reads as a stutter; more is weight nobody sees |
| Content | **Energy only — no frame, no door, no structure.** It is drawn *over* the existing frame art and must not fight it |
| Background | Fully transparent. The door, its leaves, the tint and any pawn beneath must stay visible |
| Loop | Must cycle cleanly, last frame back to first |

**Two sequences are worth having:** a **charge** cycle that loops through spin-up, and a short
**activation** burst that plays once when the connection goes live and does not loop.

### Live open portal loop

**Owner extension, verbatim:** *"what about active portal ones. should you do those to and write an ote to claude in todo"*

Add a third shared sequence: **`RR_GateOpen_01.png` … `RR_GateOpen_08.png`**, eight 256 x 256 RGBA frames. This is the calmer, repeating energy visible while a **company machine portal is live**, after the activation burst. Match the existing blue-white filament style while using a steadier, quieter presence; keep the aperture and native doors/pawns visible. No solid portal fill, frame, hardware or aura disk. One set stretches across all supported footprints and facings; do not multiply assets by size/direction. Natural portals retain ordinary native door graphics.

The [TODO note to Claude](TODO.md#active-portal-artwork-and-code-handoff-2026-10-06) owns display/state integration, stopping and reload/reduced-motion behavior. [The delivery record](implementation/GATE_CYCLE_ASSET_DELIVERY.md#active-portal-extension) records authoring progress and final paths. Artwork alone does not implement an active connection effect.

---

## What is NOT wanted, so nobody spends a day on it

- **A frame for natural gates.** Owner, 2026-10-06: *"lets keep natural doors just normal doors in
  game so there is distinction for it"*. A framed opening was built; an unframed one was found, and
  that difference is the information.
- **Quiet Pursuer artwork.** Still deferred by owner decision. It needs a creature definition before
  a texture means anything.
- **Music, ambience or room tone.** Nothing in the mod plays a bed, and adding one would fight
  whatever the player already has.
- **Anything stereo.** See the format table.

---

## Where it goes

| Kind | Masters | Shipped to |
|---|---|---|
| Audio | `assets/source/audio/` | `1.6/Sounds/Rimrooms/` |
| Animation frames | `assets/source/phase2/` | `1.6/Textures/Things/Building/Rimrooms/Gates/` |

Every shipped asset must be added to `tools/package-files.json`, and every one must have a master —
a build check refuses an asset that has neither.
