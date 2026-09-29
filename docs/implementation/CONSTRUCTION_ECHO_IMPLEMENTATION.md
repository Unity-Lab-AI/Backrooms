# The place starts copying you (0.8.1-dev)

**Baseline:** `988e109` (0.8.0-dev, 141 C# files, 86 package files).

**This checkpoint — 0.8.1-dev:** **142 C# source files** (one new), **86 approved package files** (unchanged). Zero warnings, zero errors, `TreatWarningsAsErrors` on. Assembly SHA-256 `8614901316F1935047963BC054CE0F87FCB630FFF40E0959097913956FA89675`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The request

> *"we need a dynamic procederually gernation of BAckrroms so that new equipement and rooms and shit going into the backrooms and build there or in the real world can start appearing in lower levels of back rooms seeds"*

## Why this is the strongest idea the generator has had

Until now a deep coordinate drew furniture from the whole def database — broad, but **impersonal**. This makes it draw from **the player**. Push far enough in and the rooms start containing the things *you* build: your benches, your beds, your machines, arranged by something that has clearly seen them.

That is precisely the feeling the setting runs on. A Backrooms space reads as wrong because it is *almost* somewhere real — and nothing is more almost-real to a player than a copy of their own colony.

It also means **the generator gets more interesting the longer a save runs, with no new content authored for it.**

## Sampled, never hooked

Nothing intercepts construction. A **rotating window** of one map's cells is sampled on an interval — the same bounded-scan rule the work layer uses everywhere: fixed cost however large the colony grows, and **no region of any map can be starved**, because the cursor advances whether or not anything was found.

That also makes it free to be correct about *where* something was built. A bench in the colony and a bench a colonist assembled inside a coordinate are both simply things the branch built — the owner's *"build there or in the real world"*.

## Three rules that stop it degenerating

**Generated fixtures are excluded.** Faction ownership is the test, and Backrooms furniture is not player-faction. Without that, the place would echo its own furniture back at itself and every deep coordinate would slowly converge on the same room.

**Structure is excluded.** Walls, doors and conduits are not contents. Echoing them would put a wall in the middle of a generated room — changing the layout rather than dressing it, which is the same rule the archetype placer already holds.

**Only 40% of slots echo.** The place copying you is unsettling **because the rest of the room is still strange**. If every fixture were something the player built, a deep coordinate would read as a badly laid-out copy of their colony and the effect would collapse into a joke.

## Bounded, and it forgets

The register caps at 96 definitions. When full, the **least recently seen** entry is dropped, so a branch that stops building a thing eventually stops seeing it echoed back. A register that only grew would turn a long save into an ever-lengthening list saved, loaded and scanned forever.

Sorted ordinally on read, for the same reason the archetype candidate lists are: unsorted it would follow the order things happened to be sampled in, which differs between machines, and **the same seed would then produce different rooms**.

## It only appears deep

`EchoFromDepth = 3`, deliberately not 2. The first couple of spaces should still feel like somewhere that existed before the player did. **The place copying you is something you discover by pushing in, not something that greets you.**

A young branch that has built almost nothing still gets fully dressed rooms: the echo falls straight through to the ordinary pool whenever the register holds nothing that fits the slot.

## A reading I made that the owner may want to correct

*"lower levels"* is read as **deeper** coordinates. In Backrooms lore a lower *number* is usually shallower, so this is genuinely ambiguous — but the owner has consistently said *"further in"* for depth, and the mechanic is far stronger as a progression reveal than as something present at the entrance. **Stated here rather than buried**, because flipping it is a one-constant change.

## Not done, and named in `TODO.md`

- **Echoed *rooms*, not just fixtures.** The owner said *"new equipement and rooms"*. Fixtures echo; room shapes do not.
- **Pawns found in coordinates** — the direction that arrived while this was building, captured verbatim.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled **twice** from clean; identical SHA-256.
- All four checkers pass.
- Compliance: **no new def of any kind**, no asset, no patch operation, no new work type.

## For the post-completion test phase

Confirming a depth-1 or depth-2 coordinate never echoes; confirming a deep coordinate contains recognisable player-built furniture once the branch has built some; confirming a brand-new branch still gets fully dressed deep rooms; confirming generated Backrooms furniture is never echoed; confirming no wall or door is ever echoed into a room interior; confirming the register stops at 96 and drops the least recently seen; and confirming the same seed produces the same rooms after a reload.
