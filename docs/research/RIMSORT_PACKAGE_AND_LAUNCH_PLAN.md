# RimSort package staging and launch plan

**Status:** the 0.1.0 foundation was built and staged into the Default RimSort instance's configured Local Mods directory on 2026-09-28; see the [build/staging evidence](../implementation/PHASE_1_BUILD_RECORD.md) and [commands](../BUILDING.md). The active mod list was not changed and no game was launched. The first owner-operated profile/launch steps below remain pending.

## Repository and copyable package boundary

Keep the documentation, research, workbook, and C# source in the repository. Keep the one loadable RimWorld package in its own folder:

```text
Backrooms/
  docs/                              project plans and research; never copied into the mod
  outputs/                           planning workbooks; never copied into the mod
  src/                               solution and C# source; never copied into the mod
  tools/                             build/staging utilities; never copied into the mod
  Mod/
    Rimrooms - Async Industries/     the complete, copyable RimWorld package
      About/
      LoadFolders.xml
      1.6/                            Defs, Assemblies, Languages, Patches, Textures, Sounds
```

`Mod/Rimrooms - Async Industries/` is the package root. The staging script copies only this folder into the `Local Mods` path shown in RimSort. RimSort's usual Local Mods path is `<RimWorld install>/Mods`, but installations and RimSort settings can differ; use the configured location shown in RimSort rather than assuming a hard-coded game path. Do not copy the repository root, `docs/`, `outputs/`, `src/`, or `tools/` into the game.

The package metadata must keep the displayed title `Rimrooms - Async Industries`, package ID `Rimrooms.AsyncIndustries`, and author/publisher `Operator`. RimSort reads the package's `About/About.xml` and load-order metadata to identify and place the mod. Declare only dependencies and ordering rules justified by the settled design and reviewed source; do not add optional mods just to silence a sorter warning.

## Owner-operated first launch

The product test target is the existing 294-entry profile plus Rimrooms: **295 target entries**. RimSort owns discovery, dependency checks, sorting, saving the active mod list, and launch. RimBridgeServer must also be enabled as a test-only in-game mod to provide its bridge; this creates a separate QA overlay, normally **296 loaded entries** (295 target entries plus RimBridgeServer, with any additional harness dependency recorded). Keep both counts explicit. Do not drop or replace one of the 295 target entries to make the bridge fit the count.

1. Build the Rimrooms package under `Mod/Rimrooms - Async Industries/` and copy only that folder into RimSort's configured Local Mods folder.
2. In RimSort, refresh the local mods, confirm the display title and package ID, add Rimrooms to the existing 294-entry profile, sort with RimSort, and save the resulting list. Confirm exactly 295 target entries and exactly one Rimrooms package.
3. For bridge-driven acceptance, add RimBridgeServer and only its documented harness dependencies to a disposable RimSort QA profile that preserves every one of those 295 target entries. Label this as the 295-entry target plus the test-only overlay; never present the overlay as a Rimrooms player dependency or a 295-total run.
4. Record both counts, both ordered package-ID/version lists, RimSort version, warnings, DLC set, RimWorld build, bridge build, and Rimrooms build/commit. Preserve the pre-Rimrooms 294-entry list and the sorted 295-entry target as comparison baselines.
5. The owner starts the first full-profile QA test from RimSort. Do not launch `RimWorld.exe` directly, have GABS start it, or use another manager to rewrite the list. A successful load is only a startup observation, not a compatibility pass.
6. After the initial full-profile startup is reviewed, prepare any focused Core-only, RWT, DLC, or optional-mod test variants in RimSort. Keep each ordered target profile and test overlay/result separately recorded; the owner continues to start each test session through RimSort.

## RimBridgeServer connection

Use [RimBridgeServer](RIMBRIDGE_TEST_HARNESS.md) after a Rimrooms build exists and after the owner has started the isolated test session through RimSort. Prefer RimBridgeServer's direct connection to that already-running process. Do not use GABS' launch action for this project; GABS may be considered only if its attach workflow is verified to connect to the existing RimSort-launched process without changing the profile. Keep RimSort authoritative for load order and settings, and do not ask the bridge to reorder or enable/disable mods during the 295-target-entry test.

Use disposable saves and a disposable RWT server configuration. Record RimBridgeServer and any harness-only dependencies separately from the mod's player-facing dependency list. Capture the bridge version, game/profile identity, saves, logs, screenshots, relevant before/after state, and actual result. No Rimsort launch, RimBridgeServer connection, or gameplay test occurs before the first Rimrooms package exists.

## Sources and scope

- RimSort's [Basic Usage guide](https://rimsort.github.io/RimSort/user-guide/basic-usage) documents the required game/config/Local Mods paths, list import/export, warnings, and sorting metadata.
- RimSort's [Downloading and Installing guide](https://rimsort.github.io/RimSort/user-guide/downloading-and-installing) documents game, configuration, and Workshop path variations and recommends checking paths in settings.
- RimWorld's [mod folder guide](https://rimworldwiki.com/wiki/Modding_Tutorials/Mod_Folder_Structure) describes the conventional per-mod subfolder inside the local `Mods` directory.
- RimBridgeServer's [direct and GABS modes](https://github.com/pardeike/RimBridgeServer) are separate from RimSort's role; for this project, the owner-operated RimSort launch is authoritative.

Recheck the installed RimSort version, configured Local Mods path, its detected Rimrooms package ID, and how the current build reads `About.xml` when staging the first actual package. This plan does not modify RimSort settings or the owner's active mod list.
