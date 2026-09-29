# A shop with a door in the back — 0.11.9-dev, 2026-09-29

**Dated record.** Describes the checkpoint as it was built, including three new-game crashes it
shipped into a proof and then fixed. Never rewritten.

---

## What this is

The **second selectable start**, from the `furniture_knickknack_store` card in
`docs/SCENARIOS.md`, and a correction to the first one.

Until now the mod had exactly one scenario. The chart names three.

---

## The register, checked first

`Interface, scenario setup, and quality of life` — 11 rows. The one that matters is **[85] EdB
Prepare Carefully**, *Optional*, traced `RR-FAC;RR-STA;RR-UI;RR-COMPAT`.

It applies, and the existing design already answers it: the Store's `ScenarioDef` puts a native
`ScenPart_ConfigPage_ConfigureStartingPawns` in front, and **every starting item is a native
`ScenPart_StartingThing_Defined`**. Both stay visible and editable, exactly as the Async
Industries start already does, so Prepare Carefully and Character Editor see an ordinary
scenario and can edit people and stock without the mod fighting them. The mod's own scen parts
are `visible=false` and carry only what those tools have no opinion about: the layout and the
branch.

Nothing else in the family applies.

---

## The correction: Async began with nothing

The Async start listed `<completedProjects />` — **nothing finished** — and its own comment said
so. That contradicted the direction it was written under:

> *"Async industries starts with this tech research and other basic gate techs it needs to
> operate and begin researching and gate operations at basic levels"*

**Asked rather than guessed**, because three readings were all defensible. The owner's answer was
the fullest one: **all seven tier-0 roots, plus the gate ladder's first rung.** Eight of
twenty-five projects.

So Async opens able to run a gate properly and with a foot in the door on every branch — which is
what an authorised branch of a company that has done this before would actually have.

**One consequence was named before the choice and taken knowingly:** `RR_GateTelemetry` puts
`PortalWindowTier` at 1, and tier 1 is the floor at which something may follow a crew out. Async
is exposed to incursion from its first opening. That is the price of starting equipped.

---

## The Store

| | |
|---|---|
| Map | 50×50 |
| People | **3** — owner/manager, employee, night guard, as operations / medical-logistics / security |
| Rooms | sales floor, stockroom, office, staff room, and a back room nobody uses |
| Money | **200 silver in the till** and a shop's stock. No corporate allocation |
| Wages and overhead | 300 and 1,500 a day — three people and a building, not a research branch |
| Corporation contact | **No** |
| Research finished | **None** |

**The last two rows are the whole point.** No clean-up team, no unsolicited courier, no
research. Nobody is watching this place and nothing is coming if it goes wrong, and as of 0.11.7
and 0.11.8 that absence is a **real mechanical difference** rather than a line in a design
document.

### The threshold is a door

The contract calls for *"a basement containing a narrow anomalous threshold"* that is *"not a
working machine gate"*.

It is an ordinary Core door in the back room, **because that is exactly what a gate is in this
mod before somebody designates it.** Nothing here claims a breach system that does not exist. The
shop has a door in the back that should not be there, and what it becomes is the player's
decision.

RimWorld has no basements, so the back room is a room. The fiction is in the description, where
it costs nothing and lies about nothing.

### Five roles was an Async rule written as a universal one

`ConfigErrors` demanded **exactly five** starting roles, with the message *"Async Industries
requires five distinct starting roles."* The Store opens with three, and the solo/group start
with as few as one. Relaxed to **one to five**, which is the real rule: at least somebody, and
no more than the company recognises.

---

## The proof caught three crashes in my own layout

`GenStep_Headquarters` throws on anything it dislikes, and **every one of those is a new-game
crash invisible to the compiler, to all eight checkers, and to reading the XML.** The numbers look
fine right up until a player picks the scenario.

So `proof-starts.py` rebuilds each layout offline. On its first run against a layout that built
clean and passed every checker:

| Found | Would have been |
|---|---|
| `WoodFiredGenerator` at (36,22) — it is **2×2**, so it occupies z=23, the stockroom's south wall | `"Headquarters wall intersects generated structure"` — hard crash at new game |
| `Battery` at (33,22) — same wall | same crash |
| a shelf then colliding with the moved generator | same crash |

**Three crashes, in a layout that built with zero warnings.** Building sizes are read from Core's
own `ThingDef`s, so a 1×1 assumption cannot hide a 2×2.

### And the claim it asserts that nothing else could

**A sealed room does not throw.** The map generates, the colony starts, and a third of the shop
simply cannot be entered — forever, silently. The proof flood-fills from the arrival cell through
doors and open ground and insists every room interior is reachable. Removing one door from the
stockroom fails it immediately.

---

## The assertion that was wrong, for the third time this session

The first wall rule said *a room's wall must not land inside another room's interior*. It failed
on the Store — **and it would have failed on Async, which has shipped and works.**

`GenStep_Headquarters` throws only when a wall lands where an **edifice** already is:

```csharp
if (cell.GetEdifice(map) != null) { throw ... "wall intersects generated structure" }
```

An interior cell has no edifice. Interior rooms sitting inside an outer shell is precisely how the
Async headquarters is built. **The assertion was wrong and the source was right** — invariant 130,
third instance today. Restated as the real rule: two rooms must not share a **wall cell**.

The pattern is now unmistakable. **An assertion written from what the code looks like is a guess;
an assertion written from what the code throws on is a fact.** All three of this session's wrong
assertions came from the first kind.

---

## The proof was fault-planted four ways

| Fault planted | Caught by |
|---|---|
| the stockroom's door removed | *"is reachable from the arrival cell — **SEALED**"* |
| a shelf moved onto a wall | *"clears the walls"* |
| the Store given corporation contact | *"exactly one start begins in corporation contact"* |
| `RR_GateTelemetryy` as a starting project | *"starting project exists — skipped at runtime, so the start silently grants less than it says"* |

All restored, proof holding over **both** starts.

---

## Receipts

| | |
|---|---|
| Version | 0.11.9-dev |
| Build | 167 C# files, 86 package files, **0 warnings, 0 errors** |
| New starts | **1** — the mod now ships two of the chart's three |
| New defs | 1 `RimroomsStartDef`, 1 `ScenarioDef` |
| New art, audio or texture | **none** |
| Harmony | **none** |
| New-game crashes found and fixed before shipping | **3** |
| Checkers | **eight**, all passing |
| Proofs | **seven**; the new one fault-planted four ways |
| Game launched | **no** |

Next: the **solo/group** start. Owner direction at the fork, verbatim: *"remember the other one is
solo/group start.. group have been known to end up together inside so leets use the in backrooms
start to be 1-5 pawns player settable with normal set up or edb prepare carefully mod and or
character editor"*. It begins **inside a generated coordinate**, which is structurally unlike
both surface starts and needs the coordinate created, seeded and registered at new-game.
