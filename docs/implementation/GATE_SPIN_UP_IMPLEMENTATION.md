# Bringing a gate up is work (0.8.9-dev)

**Baseline:** `ae0e65a` (0.8.8-dev, 154 C# files, 92 package files).

**This checkpoint — 0.8.9-dev:** **155 C# source files** (one new), **92 approved package files** (no new file; three existing keyed files extended). Zero warnings, zero errors, `TreatWarningsAsErrors` on. Assembly SHA-256 `9E0FA752A9DB00EB801A013FAFBC937D3723CC33D359A54B57A11E42083D8354`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The requests

> *"when u establish a backrooms portal connection the specific addresss should be connected and the gate opened but it neededs to be a ramp up process that takes a bit of time like with everything the pawns needs to do/maintaing/ operate to opening the gate process like a item build in a way"*

> *"yes the gates are just repurosed doors of the game with a bue tint and maybe a blue light glow hue around it like light through a glass wall does"*

## The ramp belongs to opening, not to one button

Three things could start an opening: dialling a remembered address, opening a session from the operations window, and opening straight after registering an address. All three now route through the same ramp.

That matters more than it looks. If dialling ramped and the operations window still opened instantly, **the ramp would be optional** — a player who learned the other button would never see it. Routing every entry point through one mechanism means there is **exactly one way a laboratory gate opens**, and `BeginPortalOpening` is simply no longer reachable without first doing the work.

## "like a item build in a way", taken literally

Work, not a timer. It accumulates at the assigned operator's own working speed — `ResearchSpeed`, the same stat calibrating the same machine already used, so a better technician genuinely brings a gate up faster and **choosing who operates the gate becomes a real decision**.

It is shown as a progress bar on the console, which is the one piece of interface every RimWorld player already reads without being taught.

**No new job def was needed.** `RR_OperateGate` already sat the operator at the console indefinitely, and its progress bar was a **binary one-or-zero indicator** that told nobody anything. It now shows the real ramp when one is running and falls back to the old indicator when none is. The operator also learns Intellectual while ramping — but only while ramping, because standing watch over an idle gate teaches nothing.

## "maintaing" is what makes it more than a delay

The ramp climbs **only while the gate is actually being held**: operator on station, power and headroom present, cutoff not thrown. These are deliberately *the same conditions a live opening is held by* — bringing a connection up must not require less than keeping one up, or a player could ramp under conditions that immediately drop the session.

Left alone it bleeds back down, and at zero it lapses with a message rather than sitting as a half-finished thing nobody can see.

### A defect the offline proof caught before it shipped

Decay was first written as a **flat 0.5 per tick**, with a code comment claiming decay is slower than progress.

**It was not.** RimWorld's research speed at low Intellectual is well under one, so a flat 0.5 would have bled a poor technician's ramp **faster than they could build it** — turning a slow operator's gate from slow into *impossible*, while the comment asserted the opposite.

`.local/register/proof-spinup.py` rejected it on that assertion. Decay is now a **fraction of the rate the ramp was observed climbing at**, checked across nine operator rates from 0.08 to 2.4. "Decay is slower than progress" is now true **by construction for every possible operator**, rather than true by luck within a stat range nobody checked.

The observed rate is saved, so decay stays tied to the crew that was actually running the machine even after that operator has been reassigned, downed or killed — which is precisely when a ramp starts bleeding.

## Why the address book now earns its keep

Required work falls with every previous connection this gate has made to that address: 1,800 for somewhere nobody has been, reaching a floor of 450 after nine runs. Proved monotonic, floored and bounded across sixty prior-connection counts.

That turns the 0.8.8 history from a convenience list into the gate's **learned routes**, and it is why pinning an entry now protects something real — the familiarity count lives on the entry, so evicting it costs the discount too.

**The discount never reaches zero.** A gate that opens instantly is a gate with no operating crew, which is the one thing this direction exists to prevent.

## A held ramp is not a lost ramp

When the work finishes and the machine still will not take it — stored energy below the opening threshold is the ordinary case — the ramp is **held at full rather than thrown away**, and the gate opens by itself the moment the reserve recovers. It still bleeds if the crew walks away, so a held ramp is not a free one.

The alternative, aborting on a refusal at the last tick, would have destroyed a long ramp over a momentary dip in a battery. That is the same "no unavoidable instant failure" rule every threat in this mod obeys.

## The blue door, and why it needed nothing new

`ThingWithComps.DrawColor` already consults **`ThingComp.ForceColor()`** on every component a thing carries, and the gate component is already on the door. Overriding that one hook tints a designated gate and leaves **every other door in the game untouched** — the same dormant-until-designated rule the rest of the native binding follows.

Verified by decompiling `Verse.ThingWithComps` and `Verse.ThingComp` rather than assumed. `Notify_ColorChanged()` drops Core's cached coloured graphic and redraws the cell, and is called at exactly the two moments designation changes.

**A player's own paint still wins**, because Core checks a painted colour *before* reaching this hook. That is the right outcome — an explicit choice beats an automatic tint — and the aura still marks the door as a gate.

The aura itself already existed but appeared **only while a connection was open**, which meant a gate was indistinguishable from any other door for almost all of its life. It is now the gate's permanent identity: a soft steady blue once designated, brighter and faster while live, and the existing amber when something has gone wrong. Still a native fleck at fixed colour and size, so **no new art or graphic resource** was introduced, and it still honours the aura and reduced-motion settings.

## Natural gates, again unchanged and again with no new guard

A natural threshold has no gate component behind it, never reaches `RegisterLaboratoryAddress`, and therefore cannot dial or ramp. Invariant #30 holds with nothing added, and the blue tint is likewise `IsDesignated`-only, so a natural doorway keeps looking like what it is.

## Not done, and named in `TODO.md`

- **Multi-cell gates** — 1x2, 1x3 and 2x3, by binding across a run of adjacent Core doors, and by accepting Doors Expanded's multi-cell doors when that mod is installed. Owner-answered, not yet built.
- **Pursuit and incursion** — inhabitants chasing a pawn to the threshold, and coming through a live opening at qualifying depth and technology. Owner-answered, not yet built.
- **Facilities**, the unknown-def-field checker, and the remaining milestones in the recorded order.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled **twice** from clean; identical SHA-256.
- All four checkers pass; 1,214 keyed references all resolving, up exactly twenty, matching the twenty keys added.
- `.local/register/proof-spinup.py`: the familiarity curve proved monotonic, floored and bounded over sixty counts, and the decay rule proved slower than progress across nine operator rates. **It rejected the first decay design.**
- Compliance: **no new def of any kind, no asset, no patch operation, no new job def, no new work type.**

## For the post-completion test phase

Confirming a dial registers the address and starts a ramp rather than opening immediately; that the ramp climbs only with the operator on station and powered, and bleeds otherwise; that it lapses at zero with a message and leaves the address remembered; that a second dial to the same address is measurably faster and a ninth is at the floor; that a fully charged ramp waits for a recovering battery and then opens by itself; that stopping a ramp keeps the address; that a ramp survives a save and reload with its observed rate intact; that a designated gate is visibly blue and an undesignated door is not; that releasing a gate restores the door immediately; and that a door the player painted keeps their paint.
