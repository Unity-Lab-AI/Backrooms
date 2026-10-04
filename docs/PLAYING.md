# Playing Rimrooms — Async Industries

> **The player documentation is the [wiki](wiki/index.md).** Start there — it is shorter, it is
> organised for reading, and it is what the published site serves.
>
> This page is kept as the long-form working version behind it.

[`HOWTO.md`](HOWTO.md) is the other document: it covers how the mod is *built*, not how it is
played.

## Read this part first

**The mod has been launched, and it has not been played through.** Those are different claims and
this page needs both. Twelve launches by the owner from 2026-09-30 onward got as far as walking a
Backrooms level: a coordinate generated, a gate held a connection, and a colonist crossed. What has
never happened is a campaign played end to end, so nothing below is a report of how any of it felt
over time, or whether it is balanced.

That distinction is not modesty, it changes how to use the page. Where this document and the game
disagree, **the game's own readouts are right and this page is wrong** — the panes read live state,
and a sentence here was written from source at a particular checkpoint. Numbers are given only where
the code fixes them; anything the game computes is described rather than quoted.

**Every launch so far found defects, and every one of them was ours** — never a conflict with another
mod. That record is the reason the refusal messages below are worth reading rather than guessing past.

## What the mod is

You run a branch office of a company that does contract work in the Backrooms. Ordinary RimWorld
colony play is untouched: pawns still eat, sleep, build, fight and hold grudges, and every base
game control still works the way it always did. What the mod adds is an employer, a machine that
opens a way into somewhere else, and paperwork about both.

The company is not a faction you befriend. It is an account, a queue of requests, and a bill.

## Three ways to start

Each is a scenario in the ordinary new-game list.

- **Async Industries** — the intended opening. A branch with staff, an account, and a survey
  already accepted. Most of this page is written about this start.
- **The Store** — you begin in a shop with a way through in the back. Less money, more improvisation.
- **Lone survivor** — you are already inside. The map you start on *is* a coordinate, and getting
  anywhere else is the first problem.

All three establish a branch, and all three use the same systems. The opening decides what you have
on day one, not what you can eventually do.

## The first session

The Operations tab is the company's own surface. It is the leftmost button on the bottom bar; its
keyboard shortcut is under *Keyboard, colour and scale* below.

1. **Restore power.** The gate needs a real supply and a real reserve. Ordinary generation and
   batteries; nothing special is required and nothing special is provided.
2. **Build the gate.** Designate the door, the communications console, the battery and a machining
   table on Operations' Machine pane, then complete the **assemble gate** bill on it: **100 steel
   and 8 industrial components**, worked by a crafter. The table keeps all of its normal recipes.
3. **Keep an operator at the console.** A qualified staff member stays at headquarters while the
   crossing is open. This is a job, not a checkbox.
4. **Pick a crew.** Ready field staff, checked for skill, health and what they are carrying.
5. **Open a connection and go.** Operations will refuse an opening it cannot complete, and it
   always says which requirement failed. Fix the named one.

**Read the refusal.** Every stop has a written reason: the assembly is unfinished, the reserve is
below what a return needs, no qualified operator is at the controls, no crew is ready, no validated
way home, the gate is out of calibration, or the connection was cut deliberately. The reason is the
instruction.

## The gate, the connection, the threshold

Three different things, and the mod is strict about the words.

A **gate** is the built machine. There is one kind of it, in sizes from one by one up to two by
three; a wider gate lets larger things through, and animals can cross a gate wide enough for them.
A **connection** is what an opened gate holds: it costs power to open, draws while it stands, and
holds a reserve back so that one return is always paid for. A **threshold** is the arrival cell on
the far side.

A gate is a door and nothing else. It does not teleport, it does not scan, it does not think.

**Damage matters.** Below half condition a gate loses calibration and will not hold a connection
until it is repaired. Shooting, fire and mortar hits all count, because a gate is an ordinary
building with hit points.

**A gate remembers.** Each one keeps a record of what its openings did — completed returns against
emergency cutoffs. That record is a history, not a dice roll; nothing is randomly unreliable.

## Free doors run out

Early on you will find ways through that you did not build. These reach **through depth 3** and no
further. Past that, the only way deeper is a gate you built, powered and calibrated yourself. The
found doors are a tutorial, not a strategy.

There is always a way home. A coordinate is generated with a guaranteed exit, and a wall built
beside a gate does not brick it — a gate is its own door cell.

## Coordinates

A **coordinate** is an address, and the map it opens onto. You visit one. You do not settle one,
and the game will tell you so if you try to put one on the books as a site.

Each coordinate is a set of rooms with links between them. Rooms you have **surveyed** appear on the
Atlas pane with what connects to what; rooms you have not are blank. Route telemetry has to be
unlocked before the link list shows at all.

**Things move between visits.** Come back and something will not be where you left it. This is
deliberate and is not a bug report.

**Every coordinate has a band** — how hostile it currently is. The band rises with depth and with
what your colony is worth, and it decides what comes looking for your crew. The Atlas pane prints
it. Before 0.12.33-dev it did not, and the only way to learn a coordinate's band was to be hurt by
it, which is the opposite of how this mod is meant to teach.

## What is out there

Wanderers, survivors, anomalies, and echoes of colonists. At the hostile band an inhabitant will
hunt your crew as far as the threshold — and only that far, with one bounded, named exception where
something crosses with them.

Inhabitants are drawn from this mod's own roster. Nothing installed elsewhere leaks into Backrooms
generation, and that is asserted by a proof rather than intended.

## Bringing something back

The point of a crossing is a record.

1. **Record in the field.** A recording wants a route, a distortion reading and an entity
   observation. The Investigation pane shows which of the three each recording still lacks.
2. **Analyse it at home.** Bind a laboratory, then analyse. Analysis is work, done by a pawn, over
   time.
3. **Spend the insight.** Finished analysis becomes insight. Company projects spend insight, and a
   completed project is what lets the branch do the next thing.

The research ladder has seven branches and four tiers, and every unlock grants a capability that
real code honours. Nothing on it is a number that quietly does nothing — unlocks that changed
nothing observable were deleted rather than shipped.

## The money

Two kinds, deliberately.

The **company account** is a ledger in dollars. It pays quoted company costs: staff, site fees,
procurement, obligations. It is never spawned as silver for somebody to haul. The **physical stock**
— silver, steel, food, gear, salvage — is ordinary RimWorld goods and behaves exactly as it always
has.

The Ledger pane lists recent movements with the reason for each. Outstanding obligations can be paid
from the Overview pane, and unpaid ones do not quietly vanish.

## Requests and contracts

A **request** is what the corporation asks for next. Requests are the campaign: finish one and the
following one opens. The corporation asks for six things and then stops asking, which is the hinge
of the opening arc rather than the end of the mod.

A **contract** is a priced job with terms, a base payment and a bonus. Survey and odd-supply work
arrives this way. Contracts and requests are separate systems and the Contracts pane shows both,
requests first, because a player looking at that pane is looking for what to do next.

## Facilities, equipment and sites

A **facility** is a contiguous run of space the branch treats as one place. **Equipment links** wire
shelves, analysers and cabinets into a gate the way furniture links to a bed — except these reach
across distance and through walls, and are made by hand. Nothing about a link is automatic.

A **site** is somewhere beyond headquarters that the branch has put on its books. It is billed every
day, it needs people present to receive anything, and it stops being billed while it is out of
reach. A gate may stand at a registered site, with its own facility around it.

## Work across a connection

Colonists will travel through an open connection to do work on the other side. That is the mod's
largest system and most of it is invisible when it is working.

Two things are worth knowing as a player. **Work you started keeps going** — a pawn that crossed to
finish a job finishes it rather than turning around at the threshold. And **work you have not
started yet waits its turn** — planning a job on the far side sits below every local job of the same
type, so nobody walks through a gate while there is the same work to do at home.

The Activity and Connected Work panes report what crossed and why.

## Containment

Some of what comes back has to be held. Holding platforms, the strength of what holds them, and the
consequences of failure are all the base game's — this mod adds warnings about **the maps you are
not looking at**, because RimWorld's own four containment alerts read the map on screen and this mod
assumes several live maps at once.

On a breach the branch cuts every open connection. That is a deliberate procedure, it is armed by
default, and it uses each gate's own emergency cutoff.

**Staff report in.** Anybody back from a crossing is not dispatched again until they have been
debriefed. Quarantine and debrief are one mechanism, not two: it is *you do not go back out until
you have reported in*. Walking a single colonist through a door by hand is not a company dispatch
and is not held to it.

## The Operations tab

Thirteen panes: Overview, Personnel, Contracts, Ledger, Atlas, Activity, Investigation, Machine,
Expedition, Facilities, Procurement, Sites, and Help.

The **Help** pane holds the glossary of every word this mod uses that RimWorld does not, the live
keyboard binding, and the readability position. It works with no game loaded, because a glossary you
need a running company to open is not help.

Below the panes, **Colony controls** opens the game's own tabs: Architect, Work, Assign, Research and
the world map. These are the game's own buttons pressed on your behalf. **Nothing about RimWorld's
tab bar is replaced, reordered or patched** — see the note on that below.

## Keyboard, colour and scale

The Operations tab is bound to **Backslash** by default, and the binding is generated by
RimWorld's own key-binding machinery so it appears in your Key Bindings dialog with everything
else. Rebind it freely; the Help pane reads your current binding rather than the shipped one.

**Why not a function key.** The base game leaves F12 free, so an earlier build took it — and
HugsLib, which a great many profiles load, binds F12 to *Publish log file*. Across the base game
and a large mod list, every one of F1 to F12 is bound by something. Backslash is not.

**These screens set no colour and no text size of their own.** Your Options — interface scale, font,
colourblind mode — apply here exactly as they apply to the base game. A checker refuses an authored
colour or an authored font in any readout file, so this stays true rather than being remembered.

Nothing required is carried by colour, sound or animation alone. Gate readiness, the return reserve,
route tags, distance, recall warnings and record status each have a written label.

## Two things this mod deliberately does not do

**It does not remap RimWorld's own menus.** An earlier plan was to rebuild the base game's tabs into
a company-first layout. That plan is not built, on purpose: remapping the base game's interface
would fight every interface mod anyone has installed, and reachability was the actual requirement.
The company tab is first on the bar and every surface it names is reachable from inside it, which
is the requirement met without taking anything over.

**It does not promise multiplayer.** There is no shared colony and no live shared map.
There is no synchronised research either.
[`MULTIPLAYER.md`](MULTIPLAYER.md) says what was actually inspected and nothing more.

## If something goes wrong

- **Operations says a company is not established.** The Overview pane offers to register
  headquarters again. Use it before anything else.
- **Operations says the save uses a different record version.** Keep the original save and use a
  matching build. Do not re-save it.
- **A coordinate failed to generate.** The Atlas pane says so, keeps the address, and offers to
  re-address the survey. Your crew and stock are accounted for.
- **A colony control is unavailable.** Return to a playable colony map. Some tabs do not exist in
  the world view.

## What this page is not

It is not a balance document, it is not a compatibility report, and it is not a play report.

The mod is developed against RimWorld 1.6 and **declares no dependencies at all** — not one mod and
not one expansion. All five expansions are optional, and expansion content is marked as needing its
expansion, so without it that content is simply absent. A 294-entry load-order list ships as sorting
advice, which is a different thing from a requirement: own none of those mods and this still runs.
Content from another mod is looked up by name, so a missing one degrades what depends on it rather
than throwing.

For what the systems are meant to achieve, read [`GAME_DESIGN.md`](GAME_DESIGN.md). For the opening
script in the company's own voice, read [`TUTORIAL_SCRIPT.md`](TUTORIAL_SCRIPT.md). For what is
known about running alongside other mods, read [`COMPATIBILITY.md`](COMPATIBILITY.md).
