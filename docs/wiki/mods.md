# Mods and expansions

## What is required

This build is authored against a **specific collection** and declares every member of it.

| | |
|---|---|
| **RimWorld 1.6** | |
| **All five expansions** | Royalty, Ideology, Biotech, Anomaly, Odyssey |
| **The collection** | Every mod it is built alongside — see [Links](links.md) |

Your mod manager reads those declarations and will **name anything missing, with a link**, before
the game loads.

## Load order

Rimrooms declares its own ordering as well as its requirements, so a sorting manager puts it in the
right place without being told.

**It loads last.** A patch cannot see content from a mod that loads after it.

---

## How it treats other mods

| | |
|---|---|
| **Nothing is edited** | No other mod's files are changed, read into this one, or copied |
| **Content is looked up by name** | A missing one degrades what depends on it rather than throwing |
| **Expansion content is gated** | Anything from an expansion is marked as needing it |
| **Nothing leaks inward** | No content from any other mod appears in Backrooms generation |

The company panel lists the optional mods this one has a stated position on, whether each is
loaded, and in plain words what will and will not happen with it.

## Doors from other mods

Wider doors work as wider gates — that is the one place another mod's content changes what you can
do. A 2-cell door passes pack animals; 3 cells or more passes anything.

## What is not claimed

**No compatibility report exists.** Declaring a requirement is not the same as testing against it,
and no conflict testing has been published.

If you hit a conflict, it is worth reporting — see [Links](links.md).

---

## Running a smaller list

The requirements are declared as hard. A manager will warn you if you drop one.

The mod is written so that **missing content degrades rather than crashes**, but a reduced list is
untested and unsupported.
