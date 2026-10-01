# Install

## Requirements

| | |
|---|---|
| **RimWorld** | 1.6 |
| **Expansions** | Royalty, Ideology, Biotech, Anomaly, Odyssey |
| **Other mods** | The full collection this build is authored against |
| **Harmony** | Required by the collection |

This build **declares every one of its requirements**, so your mod manager will tell you what is
missing before the game loads rather than failing later.

Content from another mod is looked up by name. A missing one degrades what depends on it instead of
throwing an error.

---

## With a mod manager (recommended)

1. Subscribe to the **collection** — see [Links](links.md).
2. Open your mod manager and let it import the collection.
3. **Sort.** Rimrooms declares its load order, so the sorter places it correctly on its own.
4. Check for missing requirements. The manager lists any by name with a link.
5. Launch.

**Rimrooms must load last**, after every mod it is authored against. A patch cannot see content
from a mod that loads after it. The declared load order handles this — you do not need to drag it.

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
deeper.

---

## Load order in one line

```
Harmony → frameworks → expansions → everything else → Rimrooms
```

---

## Verifying it loaded

- A **Rimrooms** background appears on the main menu with the version beside RimWorld's own.
- A new scenario appears in the new-game list — see [The three starts](scenarios.md).
- Once in game, the **Operations** tab sits first on the bottom bar.

If the menu background is there but Operations is not, you are in the world view. Return to a
colony map.

---

## Removing it

Rimrooms writes its own save data. **Removing it from a save in progress will lose that data** —
the company account, coordinates, records and contracts.

Finish or abandon the colony first. Existing saves without Rimrooms are unaffected.
