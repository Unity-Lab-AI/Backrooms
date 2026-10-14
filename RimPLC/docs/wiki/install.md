---
title: Install
summary: "Where the files go, which game versions load it, and the one rule about the bridge companion."
---

# Install

## The package

Copy the mod to RimWorld's local Mods folder as `RimPLC`, with `About/` and `LoadFolders.xml`
directly inside it:

```
Mods/RimPLC/
  About/About.xml                      Operator.RimPLC, no dependencies
  About/Preview.png
  About/RimPLC_Badge.png
  LoadFolders.xml
  1.7/Assemblies/RimPLC.dll            the mod
  1.7/Defs/MainButtonDefs/             the RimPLC tab on the bottom bar
  Languages/English/Keyed/
  Presets/LadderV2.json                the shipped ladder (the book)
  BridgeTools/RimPLC.BridgeTools.dll   the optional bridge companion (see below)
```

`Source/` in the repository is for developers and is not needed in the Mods folder.

Enable RimPLC in your mod manager. It has no dependencies and no load-order requirement. Back up
a save before changing its mod list: removal from an existing save has not been checked.

## Game versions

`About.xml` declares `1.6` and `1.7`. `LoadFolders.xml` points both at the same `1.7/` folder,
so there is one payload whichever version the game reports. Leave the `1.7/` folder name as it is.

The inspected compiler and API baseline is 1.6. A session on 1.7 unstable / Waylith has not yet
been recorded as passing. Ludeon's
[announcement](https://store.steampowered.com/news/app/294100/view/672882362547178633) explains
the engine update and the unstable branch.

## The bridge companion -- one copy, inside the mod

`BridgeTools/RimPLC.BridgeTools.dll` exposes the same commands as the command file to
RimBridgeServer as `rimplc/*` tools
([Commands and the AI API](commands.md)). It loads only when RimBridgeServer is installed; without
it the file is simply never used.

**Keep exactly one copy.** RimBridgeServer also scans the game's own `BridgeTools/` root, and a
second copy at `<RimWorld>/BridgeTools/RimPLC/` registers the same tools twice:

```
[RimBridge] Failed to register annotated extension provider 'extension.mod/operator.rimplc/...':
Capability alias 'rimplc/enable_rung' is already registered
```

The copy that ships inside the mod folder is the one to keep. Delete any copy under the game's
root `BridgeTools/` folder.

## First look

Open the **RimPLC** tab on the bottom bar. The Ladder tab lists every rung of the shipped preset;
tick **Live rungs only** to see what holds right now. Read [The window](window.md) for what each
control does, and [The ladder](ladder.md) for what the rungs mean.
