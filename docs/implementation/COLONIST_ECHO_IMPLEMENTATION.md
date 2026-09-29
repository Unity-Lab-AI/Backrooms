# The place copies your people, and holds them until you find them (0.8.5-dev)

**Baseline:** `d1a70e5` (0.8.4-dev, 149 C# files, 91 package files).

**This checkpoint — 0.8.5-dev:** **151 C# source files** (two new), **91 approved package files** (unchanged; one def and two keyed strings added to existing files). Zero warnings, zero errors, `TreatWarningsAsErrors` on. Assembly SHA-256 `1314BF625F45C04F9F64BB8AC18F88B5705F9ED253563AA4BBEE9E8C8983BE28`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The request

> *"not just room shape echoes but echos of thier inhabitance in weird ways and items and equipment and production benches"*

Items and benches shipped in 0.8.4-dev. This is *"echos of thier inhabitance"* — and it is a different thing entirely from echoing objects.

## The echo is of somebody who is alive right now

**Deliberately not somebody you lost.** That is the Missing family, and it is a different and sadder feeling: a body with a familiar name is grief.

An echo is **uncanny**, and it is uncanny precisely because **the real one is standing in your base at the same moment you are looking at this one.**

That constraint is enforced rather than assumed. A colonist must be:

- **alive**, not downed;
- **on a player home map** — not in another coordinate, because somebody standing in the Backrooms is not "at home" and echoing them loses the whole point;
- **not on the coordinate map itself** — meeting your own echo while you are standing there is a sillier effect than meeting it while you know they are at home.

If nobody qualifies, **the echo is not placed at all.** A generic stranger under an echo family would be a worse encounter than none, because the whole effect is the recognition.

## What is copied, and what deliberately is not

| Copied | Not copied |
|---|---|
| the **name** | skills, traits, backstory |
| the **apparel** | health, relationships, interior anything |

Those two are what a player recognises at a glance, and together they are enough to land.

**An echo is a surface** — something that has *seen* your colonist, rather than something that *is* them. Copying the interior would make it a duplicate, which is a weaker and much more confusing idea, and would hand the player a free second copy of their best worker if they ever recruited one. **Echoes cannot be recruited at all** — the survivor mark is never applied to them.

**Copies of apparel, never the originals.** Taking the real clothes would strip a living colonist from across a gate: a bug wearing a feature's clothes. Each piece is made fresh from the same def and stuff, so quality and damage differ — fitting, since an echo is a likeness rather than a duplicate. Whatever the generator already dressed it in is removed first, or the echo wears two shirts and reads as a mess rather than as a copy.

## Never hostile

An echo is unsettling, not dangerous. Hostility would also **break the warning-first rule**, because a thing wearing a friendly name that attacks is the definition of an unreadable threat. The existing `ConfigErrors` check already refuses any hostile family that is not Psychotic, so this is enforced by the same guard.

## Determinism took a specific fix

Candidates are sorted by `thingIDNumber` rather than taken in list order. List order varies with spawn and load order, so without the sort **the same seed would echo a different colonist after a reload** — and the entire effect depends on it being the same person every time.

## Inhabitants are held until they are found — a defect caught by the owner mid-build

> *"and we cant have backrooms npc pawns all dying off if a person is slow to explore so something needs to be done about like stat or need freezing until discovered with the fog of war"*

**This was a real defect in what had just been built, not a refinement.** Everything placed in a coordinate is a live pawn on a live map, so its needs tick from the moment it exists. A survivor placed three rooms away would **starve to death before a cautious player ever reached them** — the rescue would be impossible for the exact player most likely to want it, and it would read as a broken feature rather than as somebody having died.

The same applies to a hostile freezing to death in a cold band's coordinate, and to a body rotting to bones behind a door nobody opened.

**Fog of war is the right discovery signal, and the owner named it.** RimWorld already tracks per cell whether the player has seen it, so nothing has to be invented, saved or kept in sync — and it is already the exact question a player experiences as *"have I been there yet"*.

Needs cannot be stopped from ticking without Harmony, so they are **topped back up** on a bounded sweep instead. The observable result is identical, and it needs no patch to a Core method. Malnutrition, hypothermia and heatstroke are cleared, and corpse rot is held at zero.

Clearing hediffs is safe **precisely because this only ever runs on somebody nobody has seen**: no player decision is being undone and nothing observable is being reversed.

**Mood is deliberately left alone.** A held pawn is being kept alive, not made happy, and a forced mood would produce somebody who reads as uncannily content in a place designed to be unbearable.

The moment their cell is uncovered they are released. **Discovery is what starts their clock.**

## Not done, and named in `TODO.md`

- **Echoed room shapes.** The last one. Room dimensions feed the **saved layout fingerprint**, so changing them touches generation's validation path and wants its own careful checkpoint.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled **twice** from clean; identical SHA-256.
- All four checkers pass; 1,183 keyed references all resolving.
- Compliance: one inhabitant def and two keyed strings added to existing files. **No new PawnKindDef, no new gameplay ThingDef, no asset, no patch operation, no new work type.**

## For the post-completion test phase

Confirming an echo carries a living colonist's exact name and clothes; confirming the real colonist is unaffected and keeps their own apparel; confirming no echo appears when every colonist is inside the coordinate, downed or dead; confirming an echo is never hostile and never offers the survivor option; confirming the same coordinate echoes the same colonist after a reload; confirming an echo appears only at depth 3 and deeper; and confirming apparel from a mod that refuses to be worn degrades to a partially dressed echo rather than an error; **and, for the preservation fix:** leaving a coordinate unexplored for a long stretch and confirming a survivor three rooms away is still alive and unstarved, a hostile has not frozen, and a body has not rotted; confirming that all three resume normal behaviour the moment their cell is uncovered; and confirming the player's own people are never held.
