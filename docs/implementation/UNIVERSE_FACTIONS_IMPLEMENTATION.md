# The universe has factions in it — 0.12.15-dev, 2026-09-29

**Dated record.** Never rewritten. Closes the owner's universe direction of 2026-09-28 — the
largest completely unbuilt direction in the project, found by the 0.12.14-dev backlog audit.

---

## What was missing, and how long

The owner named the universe's factions on **2026-09-28**. Thirteen rows were recorded verbatim.
**No `FactionDef` existed anywhere in the package**, and nothing had been started. The rows sat
open through fourteen checkpoints because the queue they sat in was never re-measured — which is
what 0.12.14-dev was about.

---

## Why a `FactionDef` is allowed at all

The founding rule is **invariant 10**: no new gameplay ThingDef, PawnKindDef, art or audio. The
owner answered the question directly:

> A `FactionDef` is **world configuration, not a physical gameplay Def**, so it sits inside the
> content policy — provided its `pawnGroupMakers` point at **existing** `PawnKindDef`s and its
> `factionIconPath` is an **existing** faction icon path.

That permission is narrow, and the proof exists because two things would quietly widen it:

| Widening | Why it would not be noticed |
|---|---|
| a `kindDef` option naming a pawn kind this mod authored | loads clean; the exemption silently stops being about world configuration |
| a `factionIconPath` Core does not ship | **loads clean and fails at runtime** — `ContentFinder` returns null and the faction simply has no icon |

So `proof-universe-factions.py` **enumerates the installed game** for both — invariant 19, never
trust a remembered list against shipped game data — and planting either one makes it exit 1.

---

## The seven

Six the owner named, plus one *"in the same vein"*. Descriptions are written fresh: the recorded
row asked explicitly that the owner's own wording stay in `TODO.md` and **not** be paraphrased into
def descriptions, and the proof searches the descriptions for the owner's phrasings to enforce it.

| Def | Label | What it wants |
|---|---|---|
| `RR_Faction_Government` | federal oversight office | your paperwork, patiently, for ever |
| `RR_Faction_RivalCorporations` | competing interests | your figures and whoever produced them |
| `RR_Faction_FormerStaff` | former staff association | **the only group that has stood where your crews stand** |
| `RR_Faction_TechThieves` | acquisition crew | a calibrated assembly, on a truck |
| `RR_Faction_Espionage` | industrial intelligence | to read your reports before the parent corporation does |
| `RR_Faction_ConcernedCitizens` | concerned citizens | to know what happened to the Hendersons' boy |
| `RR_Faction_Press` | independent press | **to publish all of it**, which is what the other six are preventing |

The seventh is the one whose purpose is *disclosure*, which is the single thing every other faction
on the list is working against. That is why it belongs.

---

## The decision that keeps this non-invasive

**`settlementGenerationWeight` is 0 for all seven.** Also `canMakeRandomly` false and
`requiredCountAtGameStart` 1.

This mod exists to work alongside **294 others**, several of which add their own factions and world
content. **Seven settlement-generating factions would change every world map every player
generates, for everyone, for ever.** These are conspiratorial and institutional interest groups:
they have people and intentions, not towns. World generation is exactly as it was.

They can still raid — a faction needs no settlement to arrive, which is how Core's mechanoids
work — so earning their hostility means something.

---

## All seven begin neutral, by not setting a field

`FactionDef` was decompiled rather than remembered, and it has **no starting-goodwill field at
all**. A faction that is not `permanentEnemy` starts neutral through Core's own relation logic.

So the owner's answer — *all neutral, escalating from play* — is achieved by **not setting
something**, which is the kind of correctness that decays silently: nothing looks wrong when a flag
quietly appears later. The proof therefore **asserts the absence**, and planting
`permanentEnemy>true` on any one of them fails it.

---

## Two more claims worth the proof's time

**Every faction can field both a peaceful and a combat group.** A faction that cannot arrive either
way is a name on a list, and earning its hostility would change nothing observable — the same test
invariant 136 applies to a research unlock.

**The period is prose, not a field.** RimWorld has no year; `techLevel` Industrial is the 1990s in
its vocabulary. The measurable half of the owner's answer that the framing *"also constrains
starting grants"* is that **no start grants spacer-tier content** — no Glitterworld medicine,
bionics, archotech, charge weapons, power armour, personas or luciferium. Research may still climb
anywhere, so **no start is dead-ended**, which was the other half of the same answer.

---

## Fault-planted five ways

| Planted fault | Exit | Caught |
|---|---|---|
| a pawn kind this mod authored | 1 | ✓ |
| an icon path Core does not ship | 1 | ✓ |
| a faction that generates settlements | 1 | ✓ |
| a faction that starts hostile | 1 | ✓ |
| the file dropped from the package allowlist | 1 | ✓ |
| *restored* | **0** | — |

The allowlist one was not hypothetical: `check-package-integrity.py` **caught the new file
shipping unauthorised** on its first run, before the proof existed.

---

## Receipts

| | |
|---|---|
| Version | 0.12.15-dev |
| Build | 173 C# files, **87 package files**, **0 warnings, 0 errors** |
| C# changed | **none** |
| New `FactionDef`s | **7**, plus one abstract base |
| New ThingDef, PawnKindDef, art or audio | **none** |
| Settlements added to world generation | **zero** |
| Owner rows closed | **13** |
| Checkers | **eight**, all passing |
| Proofs | **eighteen**, all exiting zero |
| Planted faults caught | **5 of 5** |
| Game launched | **no**, and nothing in this mod has ever been played |
