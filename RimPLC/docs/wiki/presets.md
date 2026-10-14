---
title: Presets and building
summary: "The shipped ladder, player overrides, export and import, what the save holds, and building from source."
---

# Presets and building

## The shipped ladder

`Presets/LadderV2.json` is the book: every rung RimPLC ships with, in the ladder shape, with the
sensor catalogue, the tags and the marks it needs. It loads with the mod and is **not** saved in
the colony, so updating the mod updates the book in every save.

Editing a preset rung in the window (or with `upsert_rung` under its id) makes a **player copy**
under the same id; the ladder uses the copy and the window's **Revert** drops it. Your own rungs,
your switches, your advise/auto modes, your tag overrides, your marks, the instruction memory and
the letters you have marked seen **are** saved with the colony.

## Export and import

**Export** writes the ladder -- the book plus your layer -- to
`<RimWorld config folder>/RimPLC/exports/<name>.json`, in the same shape as the preset plus an
`rimplc_state` block with the memory.

**Import** reads one of those files (or any ladder in the shape) and shows the difference before
anything changes:

| Mark | Meaning |
|---|---|
| `+` | a rung the import adds |
| `~` | a rung it changes |
| `=` | a rung it leaves as is |
| `!` | a rung it cannot take -- the reason is beside it |

Apply merges it. A dry run through the command file (`"dry_run": true`) returns the same diff as
text. Back up a colony before importing into it or switching game versions.

## Clean notices

A rung's notice is text the game will show. Notices and messages from the external-assistant
rungs pass a clean-word filter before they are shown; a line the filter rejects is not shown, and
a rung whose notice would be rejected is refused at save time.

## Building from source

```
dotnet build -c Release Source/RimPLC/RimPLC.csproj -p:RimWorldPath="C:/path/to/RimWorld"
dotnet build -c Release Source/RimPLC.BridgeTools/RimPLC.BridgeTools.csproj
```

`RIMWORLD_PATH` in the environment is also accepted. Both projects target .NET Framework 4.7.2 and
C# 7.3, treat warnings as errors, and reference the game's `Managed` assemblies (and, for the
companion, the installed `RimBridgeServer.Sdk.dll`) read-only with `Private=false` -- nothing of
the game's is copied into the output. The core writes `1.7/Assemblies/RimPLC.dll`; the companion
writes `BridgeTools/RimPLC.BridgeTools.dll`. Neither build stages or launches the game.

The shipped preset is self-contained: nothing else is needed to build or run the mod. In the
working repository it is generated from the playbook by a checker that enforces unique ids,
numeric priorities, known keys, type-correct comparisons, a prompt for every rung and no
priority ties; the window's editor applies the same rules to a rung you save.

## Versions

The package declares RimWorld 1.6 and 1.7 and loads one `1.7/` folder for both. The compiler
and API baseline is 1.6; a 1.7 running session has not yet been recorded as passing.
