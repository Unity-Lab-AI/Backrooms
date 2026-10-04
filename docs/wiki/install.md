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

## With a mod manager (recommended)

1. Subscribe to the mod — see [Links](links.md).
2. Open your mod manager and let it import.
3. **Sort.** Rimrooms publishes its own load order, so the sorter places it correctly on its own.
4. Launch.

**Rimrooms loads last.** A patch cannot see content from a mod that loads after it, and its
load-order list handles this — you do not need to drag it.

That list names other mods, and it is **advice about order, never a list of things you need**. Own
none of them and the mod runs.

---

## Manual install

1. Download the release.
2. Extract into:

   ```
   RimWorld/Mods/Rimrooms - Async Industries/
   ```

3. Enable it in the in-game mod list, **below everything else**.
4. Restart RimWorld.

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
