# Origin completeness, and the weight of being somewhere wrong (0.7.4-dev)

**Baseline:** `3a4571b` (0.7.3-dev, 123 C# files, 78 package files).

**This checkpoint — 0.7.4-dev:** **125 C# source files** (two new), **79 approved package files** (one new ThoughtDef). Zero warnings, zero errors, `TreatWarningsAsErrors` on. Assembly SHA-256 `67843DA1A84F9B609B7BA4FBFADC29FA8E2C3C3F279919A4588E125E188A0716`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The request

> *"above market for (odd) resources as everything in it entirety that comes out of the backrooms get marked odd(im not sure the best way of doing it maybe mark it at the gate but idk it should be odd when in the backrooms too and all pawns in the backrooms get a -1 to -10 mood debuff -1 first enter and -10 after being in for long time like 1hr real game time and you can do things to lower it like security useing real materials not (odd) in theri surroundings ect ect expound on this too"*

Two things in one: **finish the origin model**, and **add the psychological layer**.

## Marking at the gate would have been the wrong answer, and the owner's doubt was right

The owner floated gate-marking and immediately doubted it — *"maybe mark it at the gate but idk"*. The doubt was correct. **Gate-marking is a laundering route**: carry ordinary cotton in, carry it back out, and it is now odd. It also fails the owner's own follow-on requirement in the same sentence — *"it should be odd when in the backrooms too"* — because nothing would be odd until it crossed.

The existing generation-time marking already satisfied "odd while still down there". What it did **not** cover is everything the owner meant by *"everything in it entirety"*: rock mined out of a coordinate's walls, material from a deconstructed partition, a plant cut in one of its rooms, meat butchered from something found in it. None of that is generated content.

## The fix: three states, stamped at first spawn

`ThingOrigin` replaces the boolean.

| State | Meaning |
|---|---|
| `Unknown` | never stamped — treated as ordinary, but not *proven* ordinary |
| `Backrooms` | came into existence inside a coordinate. **Odd** |
| `Outside` | came into existence anywhere else. **Permanently ordinary, wherever it later goes** |

A thing is stamped in `PostSpawnSetup` the first time it exists: `Outside` if the map is not a ready coordinate, `Backrooms` if it is.

**That closes the laundering route by construction rather than by a rule.** By the time a colonist hauls cotton through a gate, that cotton was stamped `Outside` back in the colony and can never become odd. Which means **anything appearing on a Backrooms map still carrying `Unknown` genuinely came into existence there** — so mined rock, deconstruction returns, cut plants and butchered meat are all correctly odd, with no special case for any of them.

One acknowledged seam: haul ordinary steel in, build a wall, deconstruct it, and the returns are odd. Deconstruction refunds roughly half, so the exploit **loses material every cycle** and is economically irrational. Named rather than fought.

## The pressure, and why it is the piece that ties the mod together

Until now odd/ordinary was purely economic. This makes it **psychological**, and that gives the player a reason to carry ordinary material *into* a coordinate rather than only carrying odd material out. The tension is real: **every ordinary thing hauled in to make the place bearable is a thing that was not sold**, and every odd fixture left in place is comfort that was not built.

It is also what finally gives the forward base a purpose. Thirty-one work families can already work across a gate; this is what makes it worth building somewhere for them to do it from.

### The curve

Pressure is a **saved tick count per person**, not a thought with a timer. Ticks are what let it **decay on leaving rather than snapping back** — an hour down there follows somebody home, which is better drama and better play, because it forces shift rotation instead of one colonist living down there forever.

- **−1 the moment they arrive.** The floor. Nothing removes it, because the place is wrong even when it is comfortable.
- **−10 after one real hour of continuous presence** — 216,000 ticks at normal speed. The gate's base opening window is 108,000 ticks for exactly thirty real minutes, so the two systems measure time in the same unit.
- **Recovery at 2× the accumulation rate**, so a rotation works and a single long shift does not.

### What a player builds to hold it off

The owner's lever — *"security useing real materials not (odd) in theri surroundings"* — is scored from the pawn's **actual surroundings**, not from a research unlock or a stat. A stat would have been easier and would have meant nothing; the only honest reading of "in their surroundings" is to go and look.

| Read | Weight |
|---|---|
| Ordinary-origin construction around them — walls, floors, furniture stamped `Outside` | **0.45** |
| A real enclosed room rather than a stretch of corridor | 0.25 |
| Somewhere ordinary-origin to sit or lie down | 0.15 |
| Light | 0.15 |

A full score slows accumulation to **20%** — never to zero. A perfectly appointed room in a coordinate is still a room in a coordinate.

**Odd fixtures found in place score nothing.** That is the entire point of the mechanic.

### Who it applies to

The owner said *"all pawns"*. The honest reading is everybody who **does not belong there**: a generated inhabitant is not unsettled by its own home, and applying it to natives would be both wrong and invisible since nothing reads their mood. So: humanlike, mood-bearing, player-faction — the player's colonists, and prisoners, slaves and guests they carried in.

## A checker gap closed in the same change

This checkpoint introduced the first `workerClass` reference in the package, and **nothing verified that such a class exists**. A def naming a missing type fails at load with a red error. `check-package-integrity.py` now resolves every `RimroomsAsyncIndustries` type named by `workerClass`, `compClass`, `giverClass`, `thingClass`, `driverClass` or a `Class="..."` attribute against the C# source. Verified by deliberately corrupting the name, confirming the failure, and restoring.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled **twice** from clean; identical SHA-256.
- `check-package-integrity.py` PASS (including the new class check, sanity-tested by breaking it).
- `check-keyed-strings.py`: 1,111 references all resolving, 0 duplicates, 0 argument mismatches.
- `check-dlc-gating.py` passes. `audit-gate0.py` PASS, zero errors.
- Compliance: one ThoughtDef added — a mechanics definition, anticipated by owner decision 18 which names *"pawn hediffs"* explicitly. **No new gameplay ThingDef, no asset, no patch operation, no new work type.**

## Not done, and named in `TODO.md`

- **The exchange paying above market for odd resources.** The owner's answer set that rate; the exchange itself is the next checkpoint alongside bonds and denominations.
- **Bonds, the 10–1,000,000 denomination ladder, the bench bills, greedy highest-denomination payout, and the credit beacon.**

## For the post-completion test phase

Confirming mined rock, deconstruction returns and cut plants inside a coordinate all read odd; confirming goods hauled in read ordinary and still read ordinary on the way back out; watching mood fall to −1 on entry and approach −10 across a real hour; building a lit, enclosed, ordinary-material room and confirming accumulation visibly slows but never stops; confirming pressure decays after leaving rather than vanishing; and confirming generated inhabitants are unaffected.
