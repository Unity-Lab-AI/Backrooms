# -*- coding: utf-8 -*-
"""Record the map-layers question verbatim, with what was measured before answering it."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

SECTION = NL.join([
"",
"## Owner question — do RimWorld's map layers change the five-map limit? (2026-10-05)",
"",
"**Verbatim owner question (2026-10-05):** *\"and somthing someone told me is that with rimworld updates there are now map layers? is that usable in any way as per our 5 mcolony limit we use to propigate and sustain our entire gameplay limitations\"*",
"",
"### Measured from the installed game before answering",
"",
"**Layers are real, and they are extensible.** `PlanetLayerDef` is a def type. Core ships one, `Surface`. **Odyssey** ships `Orbit`, and leaves a **commented-out `Moon` layer** in `Odyssey/Defs/PlanetLayerDefs/PlanetLayers.xml` — Ludeon documenting, in data, exactly how a modder adds a surface layer of their own.",
"",
"**A layer carries real behaviour, not just a camera position:** `canFormCaravans`, `onlyAllowWhitelistedIncidents`, `onlyAllowWhitelistedGameConditions`, `onlyAllowWhitelistedArrivals`, `onlyAllowWhitelistedArrivalModes`, `isSpace`, `ignoreNoBuildArea`, `defaultBiome`, `settlementWorldObjectDef`, `raidPointsFactor`, and its own `worldGenSteps`, `worldDrawLayers` and `worldTabs`.",
"",
"**And layers CONNECT.** `PlanetLayer.HasConnectionFromTo(PlanetLayer)` and `TryGetConnectionFromTo(...)` with a `PlanetLayerConnection`. That is this mod's central idea written in Core's own vocabulary.",
"",
"### THE ANSWER: layers do not raise the cap, and our coordinate maps were never counted by it",
"",
"**Read out of `RimWorld.Planet.SettleUtility.PlayerSettlementsCountLimitReached`, not inferred:** it walks `Find.Maps` and counts a map when `map.IsPlayerHome && map.Parent is Settlement`, **or** when `map.wasSpawnedViaGravShipLanding`, then compares against `Prefs.MaxNumberOfPlayerSettlements`.",
"",
"- **It is NOT layer-aware.** An orbital colony counts against the same number as a surface one. **A layer buys zero extra colonies.**",
"- **But it only counts settlement-parented homes and gravship landings.** `RimroomsDestinationMapParent` derives `MapParent`, **not** `Settlement`, so **every Backrooms coordinate map is already invisible to the player's settlement cap.** The only thing counting them is ours.",
"- **Our five is the owner's own direction, not an engine limit** — *\"lets have that 5 map count be universal max for back rooms main map and claiming maps where u pop out and anything over 5 maps defaults to caravans\"* — and `WorldExit.MaximumBranchMaps` counts headquarters, loaded coordinates, registered sites and claimed tiles together, with the stricter of ours and the player's preference winning.",
"- **The real cost of a map is simulation, and a layer does not make one cheaper.** Eight loaded maps is eight maps of pathfinding, temperature, weather and pawn ticking whichever layer their world object sits on. Raising the cap is a performance decision, and performance is the one thing this project cannot measure for itself.",
"",
"### What layers would actually be worth using for",
"",
"Not more maps. **Expressing our rules in Core's data instead of our C#**, which is cheaper to maintain and automatically correct as the game changes.",
"",
"- [ ] **A `Backrooms` PlanetLayer as a design question, not a capacity one.** `canFormCaravans: false` is our no-caravan rule; `onlyAllowWhitelistedArrivals` and `onlyAllowWhitelistedIncidents` are `PortalTraversalPolicy` and the incident gate expressed as data; a `defaultBiome` and `raidPointsFactor` of its own replace tuning we currently carry in code. **It would also make `PlanetLayerConnection` the engine's own word for a gate.** Needs an owner decision because it is a visible change: a layer gets its own world-view gizmo and its own tab, so the Backrooms would become somewhere the player can look at from the planet view — which may be exactly right or exactly wrong for a space that is meant to be found through a door.",
"- [ ] **Measure before any of it:** whether a `MapParent` on a non-surface layer still generates and saves identically, and whether `onlyAllowWhitelistedIncidents` would silence the unnerving register rather than shape it. **This is `[T]`-shaped work** — it needs a launch, and the owner is the only one who launches.",
"- [ ] **The cap itself stays five until the owner says otherwise.** It is their number, and the measurement above does not argue for changing it: nothing found gives a free map, and the thing that would — raising the number — is a performance trade nobody has measured yet.",
"",
])

text = io.open(TODO, encoding="utf-8").read()
if "do RimWorld's map layers change" in text:
    print("section already present; nothing written")
    sys.exit(1)
if not text.endswith(NL):
    text += NL
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text + SECTION)
print("recorded the question with the measurement, %d open rows added"
      % SECTION.count("- [ ] "))
