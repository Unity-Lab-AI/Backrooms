# RimWorld 1.7 package migration — source record

**Date:** 2026-10-12. **Scope:** package metadata, shared content loading and the two affected package validators. This record does not claim a 1.7 build or runtime result.

## Owner direction and source

The owner requested the mod target and preview be updated to RimWorld 1.7, confirmed the preview text should change from 1.6 to 1.7, and requested all documentation and wiki pages be updated. The owner extended the scope to RimPLC: *"rimroom rimPLC and all support documents and may need to add a github rim PLC and add it to it and here is the git to use for Rim PLC: https://git.unityailab.com/GFourteen/RimPLC"*. Repository/export changes are assigned to the lead. The lead read the [official Steam announcement](https://store.steampowered.com/news/app/294100/view/672882362547178633) in the browser: 1.7 is available on the unstable beta branch, uses the Waylith engine, and is intended to preserve existing mod compatibility. The publisher asks modders to verify their mods before publishing compatibility. The default game branch remains 1.6 at this checkpoint.

## Baseline and preserved behavior

- Package identity: `Rimrooms.AsyncIndustries`; author `Operator`; title `Rimrooms - Async Industries`.
- The package's own development version remains `0.13.0-dev` in this bounded assignment. The lead owns any later owner-directed package version change.
- RimPLC identity remains `Operator.RimPLC`, title `RimPLC`, author `Operator`, and package version `0.1.0`. Its ordinary assembly still builds directly to `RimPLC/1.6/Assemblies/RimPLC.dll`, and the optional companion still builds to `RimPLC/BridgeTools/RimPLC.BridgeTools.dll`.
- The real-user RimSort settings at `C:\Users\gfour\AppData\Local\RimSort\settings.json` select `C:\Program Files (x86)\Steam\steamapps\common\Rimworld`; its `Version.txt` reads `1.6.4871 rev590` and Steam app manifest build ID is `23969874`.
- The installed Core SHA-256 is `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`, matching the existing build pin.
- No Def names, C# class identities, saved fields, namespace, provider bindings, assets, dependencies or load-order entries changed.
- The reviewed `net472` / C# 7.3 compiler baseline, installed game assembly references and physical `1.6/Assemblies` build output remain unchanged. No new game hash has been invented.

## Changed files and callers

| File | Change |
|---|---|
| `Mod/Rimrooms - Async Industries/About/About.xml` | Declares game versions 1.6 and 1.7. Description explains that 1.7 is a development target whose runtime verification is pending. |
| `Mod/Rimrooms - Async Industries/LoadFolders.xml` | Explicit `v1.6` and `v1.7` mappings both select the existing physical `1.6` content folder. No files are duplicated or moved. |
| `tools/check-compliance.py` | Replaces the obsolete 1.6-only declaration rule with 1.6 plus 1.7; parses actual load mappings and requires both to select shared `1.6` content. Its existing asset, license, dependency, patching and reference checks stay intact. |
| `tools/check-package-integrity.py` | Resolves supported game versions through explicit `LoadFolders.xml` mappings. Refuses absent/duplicate/undeclared mappings, conditional entries, invalid paths, missing folders and package escapes. Package placement checks use mapped content folders rather than assuming the physical folder name equals the game version. Main is the only discovered caller of the modified internal check. |
| `src/RimroomsAsyncIndustries/RimroomsAsyncIndustries.csproj` | Missing-reference diagnostic points to the reviewed build target instead of hardcoding 1.6. Build settings and references stay intact. |
| `RimPLC/About/About.xml` | Declares 1.6 and 1.7 game targets, with an explicit pending 1.7 runtime verification statement. Package version stays `0.1.0`. |
| `RimPLC/LoadFolders.xml` | Both version mappings select `/` and `1.6`, preserving its existing root-content loading and assembly/Defs folder. |
| `RimPLC/Source/RimPLC/RimPLC.csproj` | Missing-reference diagnostic no longer hardcodes 1.6. Existing local references and output destination remain intact. |

The old 1.6-only literal in `.local/register/proof-housekeeping.py` is a dependent assertion for the lead to reconcile. This assignment does not own that file. `tools/build.ps1` requires no content destination change because both game versions deliberately share the existing folder and assembly; its reviewed Core pin remains enforced. RimPLC uses direct `dotnet build` on its two projects, not that Rimrooms packaging script. Its companion's default `RimBridgeSdkPath` still selects the actually installed provider's `1.6/Assemblies` folder; a future provider layout change needs an inspected SDK path, not a cosmetic number substitution.

## Evidence limits and remaining work

The edited Python files were parsed as source AST and the edited XML/project files were parsed as XML without importing or executing either checker. This is syntax evidence only. No tests, checkers, compilation, staging, game installation/update, game launch, settings/profile change, voice-model action or publication ran in this assignment.

The lead owns the preview edit, live documentation/wiki reconciliation, generated public output, any owner-directed package version change and later build/staging decisions. Verify 1.7 with its actual official install and the requested runtime cases before announcing observed compatibility. Existing 1.6 source and runtime evidence remains historical 1.6 evidence, not a 1.7 result.
