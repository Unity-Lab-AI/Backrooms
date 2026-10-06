---
title: Install
summary: "You need RimWorld 1.6 and nothing else. How to install it and how to tell it worked."
---

# Install

## Requirements

| | |
|---|---|
| **RimWorld** | 1.6 — the only requirement |
| **Expansions** | Royalty, Ideology, Biotech, Anomaly, Odyssey — every one **optional** |
| **Other mods** | All optional |
| **Harmony** | Not used and not needed |

**This build declares no dependencies at all.** Your mod manager will not ask you for anything,
because nothing is being asked for. Content from an expansion is marked as needing it, so without
that expansion it simply is not there.

Content from another mod is looked up by name. A missing one degrades what depends on it instead of
throwing an error.

---

## With RimSort (recommended)

**[RimSort](https://github.com/RimSort/RimSort) is the mod manager this was built and sorted with.**
It is free, open source, and runs on Windows, macOS and Linux.

| | |
|---|---|
| **The project** | <https://github.com/RimSort/RimSort> |
| **Downloads** | <https://github.com/RimSort/RimSort/releases> |
| **Its own documentation** | <https://github.com/RimSort/RimSort/wiki> |

Any manager that reads a mod's declared load order will do, and the game's own mod list works too.
RimSort is named here because it is the one in use on this side, so it is the one these steps can
honestly describe.

### Setting RimSort up

RimSort needs to be told where four things live. It finds most of them by itself; check them once
before your first sort.

| What it asks for | What to give it |
|---|---|
| **Game install** | The folder holding `RimWorldWin64.exe` — on a default Steam install, `steamapps/common/RimWorld` |
| **Config folder** | Where RimWorld keeps `ModsConfig.xml`. This is the file a sort actually writes |
| **Steam mods** | `steamapps/workshop/content/294100`, if you use Workshop mods |
| **Local mods** | The game's own `Mods` folder, which is where a manually installed copy of Rimrooms goes |

If a sort appears to do nothing, the config folder is almost always the one pointing somewhere
else — that is the only one of the four a sort writes to.

### Then

1. Install Rimrooms — subscribe on the Workshop, or drop the folder into **Local mods**. See
   [Links](links.md).
2. **Refresh** so RimSort picks it up.
3. **Sort.** Rimrooms publishes its own load order, so RimSort places it correctly on its own.
4. **Save**, then run the game.

**Rimrooms loads last.** A patch cannot see content from a mod that loads after it, and its
load-order list handles this — you do not need to drag it.

That list names other mods, and it is **advice about order, never a list of things you need**. Own
none of them and the mod runs.

> **Sort, then save.** Sorting arranges the list; saving is what writes `ModsConfig.xml`. Running
> the game without saving launches the order you had before.

---

## Manual install

1. Download the release.
2. Extract into:

   ```
   RimWorld/Mods/Rimrooms - Async Industries/
   ```

3. Enable it in the in-game mod list, **below everything else**.
4. Restart RimWorld.

That folder is also RimSort's **Local mods** location, so a manual install is picked up by a
refresh and can then be sorted like any other mod.

A correct install has `About/About.xml` directly inside the mod folder — not nested one level
deeper. The folder's name does not matter; the game identifies a mod by the `packageId` inside
that file.

---

## Load order in one line

```
frameworks → expansions → everything else → Rimrooms
```

---

## Verifying it loaded

- A **Rimrooms** background appears on the main menu with the version beside RimWorld's own.
- New scenarios appear in the new-game list — see [The three starts](scenarios.md).
- Once in game, the **Operations** tab sits first on the bottom bar.

If the menu background is there but Operations is not, you are in the world view. Return to a
colony map.

---

## Removing it

Rimrooms writes its own save data. **Removing it from a save in progress will lose that data** —
the company account, coordinates, records and contracts.

Finish or abandon the colony first. Existing saves without Rimrooms are unaffected.
