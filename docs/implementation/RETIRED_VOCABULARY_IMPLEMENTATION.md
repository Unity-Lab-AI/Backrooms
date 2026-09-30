# The in-game text stops naming things that do not exist — 0.12.26-dev, 2026-09-29

**Dated record.** Never rewritten. A shipped, player-visible defect set, and the **tenth checker**.

---

## Fourteen strings told the player to use equipment this mod had retired

Found while writing an event string for the disagreement feature at 0.12.25-dev: I grepped the
language files for the name of everything this mod has ever retired, expecting nothing.

| Retired | When | What the text still said |
|---|---|---|
| **return beacon** | 0.9.9-dev | *"a tag and return beacon there identify the safe route"* · *"Bring a return beacon for a stable comparison"* |
| **survey tag** | 0.10.7-dev → `GlowPod` | *"Place a numbered survey tag at a verified junction"* |
| **sealed evidence case** | 0.10.9-dev → designated `Shelf` | *"return it with the evidence case"* · *"its expedition evidence case"* |
| **field recorder** | 0.12.24-dev → `TextBook` | *"Carry the field recorder through each required room"* |
| **route recording** | legacy only since the book | *"recover the route recording and analyze it"* |

**This is the worst kind of stale.** A stale document misleads somebody reading the repository; a
stale tutorial string tells a player to go and do something the game will not let them do. The
objectives panel, the contract terms, three room clues and the *"what to do next"* readouts were all
naming gear that has not existed for up to fifteen checkpoints.

Nothing caught it, and it is worth being exact about why: `check-keyed-strings.py` verifies that
every key **resolves** and that every used key **exists**. Both were true. The text was well-formed,
translated, referenced, and wrong.

---

## What I found by eye was nine. The check found fourteen, plus two more

I spotted nine by reading. The check then found **five more** keyed strings — every one of them a
`route recording` mention, which I had not thought to look for because the phrase still *sounds*
current — and after being widened to def descriptions, **two more**:

- `RR_RouteRecording`'s own description still said *"return it with the field evidence case"*.
- `RR_GateTelemetry`, a live research project, described *"Compare recovered route recordings"*.

That second one only appeared after fixing a hole in my own check: the def-block pattern listed Core
def types and **not this mod's own namespaced ones**, so it was blind to `RimroomsProjectDef`,
`RimroomsRequestDef`, the procurement catalogue — most of what this mod actually authors.

**My first version of the check would have passed while the defect it exists for sat in a research
project description.**

---

## The rule is derived, because a list of four names would go stale next time

Invariant 214: check a rule as a **shape**, not a count. A checker holding *"return beacon, survey
tag, evidence case, field recorder"* is stale the next time something is retired — which is exactly
the failure it exists to prevent.

So the names come out of the repository:

- **Retired** = a def with a label in `docs/implementation/historical-content/` that the package no
  longer declares. **Invariant 37 already requires retired content to be archived**, so this list
  maintains itself.
- **Superseded but still loadable** = a live item def that is *unobtainable*: `tradeability` is
  `None`, no live recipe produces it, no scenario grants it. That derivation catches
  `RR_FieldRecorder` — retired at 0.12.24-dev **by making it unobtainable rather than by deleting
  it** — with no rule mentioning it, and `RR_RouteRecording`, which only legacy saves contain.

### The archive had a hole, so the archive was repaired first

`RR_ReturnBeacon` was retired at 0.9.9-dev and **never archived**. There is no `0.9.9-dev` folder,
which is an invariant 37 breach sitting in history — and it meant the derivation missed the very
item whose stale text started this.

Recovered from `578df5d^` and archived, along with the recipe file retired at 0.12.24-dev. Derived
retired defs went from **12 to 15**.

**A derived list is only as complete as what it derives from.** The check would have been quietly
partial, and passed.

---

## The one judgement that cannot be derived

Whether the **concept survived the item**:

> *"emergency return cutoff"* is retired, but **an emergency return is a live mechanic** with its own
> window, energy reserve and alerts.
> *"legacy field analysis bench"* is retired, but **the analysis bench is live** — a designated Core
> bench.
> *"gate control console"* is retired, but **a gate console is live** — a designated Core comms
> console.

A purely derived phrase rule flagged all three. It produced **25 hits of which most were false
positives** of precisely this kind, because sub-phrases of a retired label are very often live
vocabulary.

So `tools/retired-vocabulary.json` holds **decisions with reasons**, and the check enforces the shape
around them:

1. **Every derived phrase must be dispositioned** `stale` or `live`. A new retirement therefore
   **fails the build** until somebody says whether its words survived it.
2. Every disposition must carry a **reason** — *"a disposition without one is a guess somebody will
   trust"*.
3. Every `stale` phrase must appear in **no** keyed string and **no** live def description.
4. Every entry must still be a derived phrase, **so the file cannot rot either.**

A def may name **itself**: `RR_FieldRecorder` is labelled *"field recorder and radio"* and has to be
able to say so. What it may not do is instruct somebody to use some *other* retired thing.

The file is also the only place this knowledge has ever been written down — **which concepts outlived
their items** is exactly what a new reader gets wrong.

---

## Two substitutions are not rewords

Called out because getting either wrong ships an instruction that cannot be followed:

- **Custody is a place now.** *"return it with the evidence case"* → *"bring it to the shelf
  designated as the records archive"*. The player does something **different**, not something
  differently worded.
- **A marker is still numbered.** `CompRimroomsMarker.Number` is live, so the numbering survived the
  survey tag. *"numbered tag"* → *"numbered marker"*, never nothing.

The replacement vocabulary was taken from strings **already shipped**, not invented:
`RR_Event_CorridorUnmarked` (*"Set a glow pod down at that junction and mark it as the route home"*)
is already the modern voice for the same situation that `RR_Event_CorridorMismatch` was describing in
retired words.

### And three keys were simply dead

`RR_Generation_ClimateUnitLabel`, `RR_Generation_FluorescentLabel` and
`RR_Generation_FluorescentDescription` labelled `RR_SiteClimateUnit` and `RR_SiteFluorescent`, both
long retired. Grep confirms **nothing references them**. Deleted rather than reworded: there is
nothing left for them to describe.

---

## Fault-planted four ways

| Planted fault | Exit | Caught |
|---|---|---|
| a retired item reappears in a keyed string | 1 | ✓ |
| a derived phrase has no disposition (a future retirement nobody dispositioned) | 1 | ✓ |
| a disposition no longer derived from any label (the file rotting the other way) | 1 | ✓ |
| a disposition carries no reason | 1 | ✓ |
| *restored* | **0** | — |

The second and third are the ones that make this durable rather than a one-off cleanup: the check
fails **both** when the repository outgrows the data and when the data outgrows the repository.

---

## Receipts

| | |
|---|---|
| Version | 0.12.26-dev |
| Build | **174 C# files, 86 package files**, **0 warnings, 0 errors** |
| Assembly | `0E265705F23D1CC907E25CF48C767B5548ED99F8EB3588FD992DD9488DD68EA5`, identical across two clean rebuilds |
| C# changed | **none** |
| Player-facing strings rewritten | **12** |
| Dead keys deleted | **3** |
| Def descriptions corrected | **2** |
| Retired defs now archived | **15**, up from 12 — a 0.9.9-dev retirement that was never archived |
| Checkers | **TEN**, all passing |
| Proofs | **twenty-three**, all exiting zero |
| Planted faults caught | **4 of 4** |
| Game launched | **no.** Nobody has read one of these strings on a screen |
