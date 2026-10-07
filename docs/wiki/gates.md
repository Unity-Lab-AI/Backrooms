---
title: Gates and connections
summary: "How a gate is built, bound, staffed and opened, and what the window depends on."
---

# Gates and connections

Three words, used strictly.

| Word | What it means |
|---|---|
| **Gate** | The built machine. An ordinary door you designated. |
| **Connection** | The live link an opened gate holds. |
| **Threshold** | The cell you arrive on, on the far side. |

A gate is a door and nothing else. It does not teleport, scan or think.

---

## The gate is the only clock in this mod

An open connection has a duration. **Nothing else here does** — no request, contract, offer or
trade ever expires, and nothing penalises you for taking your time.

And the connection's duration is not a timer set against you. It is the result of five things you
control:

| Factor | Effect on how long a connection holds |
|---|---|
| **Power** | The gate is a load on its circuit while the connection stands; a circuit that can no longer carry it ends it |
| **Technology** | The window ladder multiplies the base window; the top rung removes the countdown |
| **Maintenance** | A lapsed assembly blocks the *next* opening, never the current one |
| **Workforce** | An operator off station, or none at all, ends it |
| **Physical factors** | The kill switch, a broken battery, an EMP, a condition disabling power |

## The window ladder

A first opening holds about **thirty minutes of real time** at normal speed.

Each earned tier in gate engineering **multiplies that by three**. The top rung is a **standing
connection**: no countdown at all, for as long as power, the operator and the reserve hold.

---

## Any door will do

A gate is a door you designate — not a custom building.

| Door | Gate width |
|---|---|
| Door, Autodoor | 1 cell |
| Ornate door | 2 cells |
| Wider doors from other mods | 3+ cells |

A designated gate is **blue, with a blue glow**, so you can tell it from an ordinary door at a
glance. It also wears a **machine frame** drawn across the whole run — the company built it, and it
looks built. You can switch the frame off in the mod's settings if you prefer the bare door.

**A natural gate never wears one, and that is the point.** The permanent ways through you find out
there were not manufactured by anyone: in the places this mod is drawn from, they are ordinary doors
and stretches of wall you simply pass through. **A frame means somebody built it. No frame means it
was already there.**

## The glow tells you what the gate is doing

A designated gate carries a light, and **its colour is its state**. You can read a gate across the
room without selecting it.

| The gate is | The light |
|---|---|
| Designated, doing nothing | A dim steady blue, close in |
| Bringing a connection up | Blue warming toward white, brightening as the work completes |
| **Open** | Steady blue at full reach — **exactly as it has always looked** |
| In an emergency | Amber, pulsing slowly |
| Waiting on a recovery | Red, pulsing faster |

**The pulse quickens as the ramp fills**, from a slow breath at the start to a hard beat at full, so
a gate coming up reads as a machine winding up rather than a warning light blinking.

**The light is never the only signal.** Every state above already writes a message, marks the
Machine pane, or both. Nothing here is information you can only get by seeing a colour.

## It is drawn and heard as it works

The frame carries three animations over it: a **charge** cycle while the connection comes up, a
one-off **activation** flash at the moment it reaches full, and a quieter **live** cycle that loops
while the connection stands.

The live cycle runs slower than the charge one on purpose — work in progress should look busy, and
an open connection should look settled.

The gate also has a voice. A **rev** climbs when a ramp starts and holds, unresolved; a **detent**
clicks at each quarter of the way up; the rev **resolves** into a latch when a connection closes
normally. A low **hum** loops through the ramp and a quieter one while the connection is open.

**A fault sounds different from a countdown.** A window running short is the gate working correctly
and uses the ordinary warning. A failing gate has its own cue, and **throwing the cutoff or the kill
switch has another** — a mechanical clack, because that one is somebody's decision rather than a
failure.

## Turning any of it off

All of it is presentation, and none of it is load-bearing. In the mod's settings:

| Setting | What it does |
|---|---|
| **Show native gate aura** | Off leaves the door its blue tint and no light of its own |
| **Show company gate frames** | Off leaves the bare door, with no frame and no animation over it |
| **Reduce gate motion (hide aura; keep status text)** | Stops the light and the animations. **The panes and messages are untouched** |
| **Mute gate cues** | Silences the gate's sounds |
| **Mute field and radio cues** | Silences the reporting sounds — a tag set, a journal filed, an analysis finished, a payment |
| **Cue volume** | Scales all of them, under the game's own volume |

## Width decides what fits

| Width | Passes |
|---|---|
| 1 | People, dogs, working animals |
| 2 | Pack animals — muffalo, dromedaries |
| 3+ | Anything |

A wider gate is more machine: more power while open, and longer to bring up.

---

## Opening one is work

An operator brings the gate up at the console over time. The console shows progress.

- Walk away and it **loses charge**.
- A route your crew has run before comes up **faster**.
- An operator who has personally walked that address comes up faster still.

## Four stations, so a window is not one person's bladder

**Link up to three more communications consoles to the gate** on the Machine pane. Any qualified
staff member at any of the four holds the connection, and one can stand up to eat the moment
another sits down.

The gate's own control console is the first of the four. An unpowered or switched-off console is
not a station — the gate does not count it.

**Nothing is researched for this.** It is how a gate should always have worked.

**An empty chair is forgiven for half an hour**, which is long enough for somebody to walk across a
sprawling facility and sit down. Longer than that and the connection drops. The company project
**Standing Relief** doubles that grace to a full hour; nothing makes a gate hold with nobody at the
controls at all.

## Four benches, so four people can build it

**Link up to three more machining tables the same way.** The gate's assembly is **four sections**,
so four people can build a section each at the same time instead of queueing behind one bench.

The total never changes: 25 steel and 2 components a section, 100 steel and 8 components for the
gate, whether you use one bench or four.

**A section is not reserved for a bench.** Destroy or unlink one halfway through and its unfinished
sections are still outstanding on the others, including on the designated table on its own. You can
never be left with work that nowhere can finish.

## The reserve

An open connection draws power while it stands, and holds a reserve back so **one return is always
paid for**. You cannot open a connection you could not bring people home through.

**The draw is an ordinary load on the gate's circuit**, the same as a stove or a light. Your
generators carry it first, and whatever they cannot cover comes out of **every battery on that
circuit equally** — not out of the one you bound. A generator with spare output keeps a connection
open without touching the batteries at all.

When the batteries run down to what a return costs, the connection closes on its own and gives the
crew their return window, rather than spending the charge they need to come home. A closed gate's
small standby draw stops at the same line.

---

## Three gates, and any of them dials anything

A branch may run **three operational gates at once**. The count is across every map you hold, not
per map.

It is a cap on gates, not on addresses. No gate is tied to a place: any operational gate dials
anything the branch has on its records, so three gates can hold three different places open.

## Dialling an address nobody gave you

Alongside requests and contracts, a gate can **dial an unknown address** — in the game's own words,
*let the gate choose somewhere. No request, no contract, nobody waiting.*

| | |
|---|---|
| **How deep** | As deep as found doors currently reach for you — 6, or 7 with **Deep Reach** — weighted toward the shallow end |
| **Repeatable** | Dial the same slot again and you get the same place. Reloading does not reshuffle it |
| **What it costs** | Nothing. It creates an **address**, not a map |

Nothing is generated until somebody crosses, so discovering an address is free and the cost arrives
when you open it.

---

## Places held open, and when a gate refuses

A Backrooms level is a loaded map, and so is a colony. The game keeps a limited number at once.

Your allowance is **your own colony limit** from Options, so the default is five and a player who
lowers it gets fewer. A start may set its own figure. It is never below two, because a branch needs
somewhere to live and somewhere to go.

At your allowance, the next way onward is refused before anything is generated, and the Places pane
reads *Holding 4 of 5*.

Three gates each holding a place, plus home, is four of five, which leaves one spare for a place
you walk into without planning to.

## Boarding one up

A way through you did not build can be closed permanently: **board it up for 25 wood**.

A colonist walks over and nails the boards on. The place behind it closes and that frees a place
against your allowance. It needs wood on the map and somebody who can reach both.

---

## Damage matters

Below **half condition** a gate loses calibration and will not hold a connection until repaired.

Gunfire, fire and mortars all count — a gate is an ordinary building with hit points.

## A gate remembers

Each gate keeps a record of what its openings did: completed returns against emergency cutoffs.

That is history, not a dice roll. Nothing here is randomly unreliable.

## Addresses

Every gate keeps its own list of everywhere it has connected. Rename them, pin the ones that
matter, clear the rest.

---

## Free ways through run out

Early on you will find ways through you did not build. These reach **through depth 6 and no
further** — or depth 7, once the company has earned **Deep Reach**, the project at the very top of
the research tree.

Past that, the only way deeper is a gate you built, powered and calibrated yourself. **No project
changes that**, and none ever will: seven is the last level the place hands over for free.

The cap applies to going deeper, never to coming out: a crew at the deepest band can always find a
way that leads home.

## There is always a way home

Every coordinate is generated with a guaranteed exit. Building a wall beside a gate does not brick
it — a gate is its own door cell.

---

## The kill switch

Wire a power switch to a gate and it becomes a kill switch. Flicking it is ordinary colonist work,
so somebody at home can cut a connection while a crew is still inside.

A cut connection gives the crew their return window.
