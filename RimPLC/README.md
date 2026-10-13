# RimPLC

A standalone RimWorld 1.6 mod: the colony's whole "if this, then this" logic laid out as a PLC ladder and scanned in game. Package id `Operator.RimPLC`. No dependencies, no Harmony.

Design: `docs/RIMPLC_DESIGN.md`. Frozen shapes: `docs/rimplc/schema/`. Book preset: `Presets/LadderV2.json` (made from `docs/playbook.gates.json`).

## What it does (P0 + P1 + P2)

- **Sensors** read straight from the game every scan (fast), every 4th (normal) or every 16th (slow): clock, crew, health (bleed rate, tendable injuries, overall health percent), hostiles (Core threat API), letters, stores (`ResourceCounter`), zones, buildings, designations, animals, loose and junk weapons, alerts, temperature, research, mood, wealth, damaged buildings. Names match the Ladder v2 keys, so the book's 127 rungs load unchanged. A key that cannot be read is absent, never a fake 0.
- **Logic** is a port of `.local/autopilot/gates.py` (`tags`, `_holds`, `_bound`, latches, grace, `decide`): exact, `<`, `>`, `<=`, `>=`, `!=`, `{TAG}` bounds, numeric marks, done-latches, "a missing key never fires", first live rung plus `always`.
- **Instructions** (both engines, same rules): an object as a condition value is `any` (OR), `not`, `ton` / `tof` (on / off delay in `ticks` or `hours`), `ctu` (counter with `preset`, `reset`) or `ons` (one-shot). Memory moves on tick scans only and is saved with the game.
- **Def keys on demand**: `count_<thingdef>` (items: stack total; buildings: how many) and `alert_<class>` are measured when a rung names them. `research_<def>` is measured for every project. A sensor that replaced a mark names it as `fallback`, read while the sensor is unmeasured.
- **Advise only.** On a rung's rising edge RimPLC posts its `notice` as a game message (Unity's only when clean). Coils `message`, `set_mark` and `set_tag` run only on rungs the player switched to `auto`. Nothing that changes the game world is executed.
- **Window** (main tab "RimPLC"): Ladder (every rung live, each contact green true / dark false / amber unmeasured / red unresolved; switch on/off; advise/auto; New rung / Edit / Remove or Revert; Export / Import), Tags (override setpoints), Marks (set, clear, add), Sensors, Log.
- **Rung editor**: key + operator + value rows with searchable pickers (sensors, marks, tags, and runtime defs: items, buildings, research, alert classes; a DLC or mod def adds its `requires`). Instructions are edited as JSON, from templates. Saving runs the same rules as `tools/rimplc-check.py` (`Validate.cs`). Editing a book rung makes a player copy under the book id, and Revert drops it.
- **Export / import**: `<RimWorld config folder>/RimPLC/exports/*.json`, in the ladder shape plus `rimplc_state`. Import is a merge, shown as a diff (+ ~ = !) before Apply.
- **Clean notices**: Unity rungs' notices and messages go through `CleanText.cs`, a port of the stream's clean-word filter. A line it rejects is not shown, and a Unity rung with such a notice is refused.
- **Save**: marks, tag overrides, player/Unity rungs, switches, modes, edge memory and seen letters live in the save file (`ExposeData`). The book is not saved; updating the mod updates it.
- **AI API**: `RimPLC.BridgeTools.dll`, a RimBridgeServer companion with `rimplc/read_ladder`, `read_state`, `set_tag`, `set_mark`, `upsert_rung`, `remove_rung`, `enable_rung`, `letters_seen`, `export`, `import`. `read_ladder` keeps the field names of the `ladder` tool. Without the bridge, the same commands work through `<RimWorld config folder>/RimPLC/inbox.jsonl` -> `outbox.jsonl`.
- **Thin client**: the autopilot's `ladder` / `ladder_set` (`.local/autopilot/gates.py` + `tools.py`) ask RimPLC when it answers, with the same result text, and fall back to the Python engine when it does not. The mapping is in `docs/RIMPLC_DESIGN.md` under "Built status", P2.

## Layout

```
RimPLC/
  About/About.xml                      Operator.RimPLC, no dependencies
  LoadFolders.xml
  1.6/Assemblies/RimPLC.dll            build output (in this folder only)
  1.6/Defs/MainButtonDefs/             the RimPLC tab
  Languages/English/Keyed/
  Presets/LadderV2.json                the book (tools/rimplc-check.py --emit)
  BridgeTools/RimPLC.BridgeTools.dll   companion build output
  Source/RimPLC/                       core source + csproj
  Source/RimPLC.BridgeTools/           companion source + csproj
```

## Build

```
python tools/rimplc-check.py --emit                      # validate the playbook, write Presets/LadderV2.json
dotnet build -c Release RimPLC/Source/RimPLC              # -> RimPLC/1.6/Assemblies/RimPLC.dll
dotnet build -c Release RimPLC/Source/RimPLC.BridgeTools  # -> RimPLC/BridgeTools/RimPLC.BridgeTools.dll
```

Both projects reference the game's `Managed` assemblies (and the installed `RimBridgeServer.Sdk.dll`) read only, with `Private=false`. `RimWorldPath` / `RIMWORLD_PATH` override the default Steam path. Output never leaves this folder.

**Staging is the owner's step.** To try it: copy `RimPLC/` (without `Source/` and `BridgeTools/`) into the Mods folder as `RimPLC`, and `BridgeTools/RimPLC.BridgeTools.dll` into `<RimWorld>/BridgeTools/RimPLC/`. Not done by any build or agent.

## Command file

One JSON object per line in `inbox.jsonl`; the result lands in `outbox.jsonl` with the `id` echoed.

```
{"id":"1","cmd":"read_ladder","top":4}
{"id":"2","cmd":"set_mark","name":"combat_paused","value":true}
{"id":"3","cmd":"set_tag","name":"STEEL_RESERVE","value":600}
{"id":"4","cmd":"upsert_rung","rung":{"id":"check-beer","priority":30,"when":{"colonists":">3"},"then":["brew beer"]}}
{"id":"5","cmd":"enable_rung","id":"unity-check-beer","enabled":false}
{"id":"6","cmd":"upsert_rung","rung":{"id":"cold-hold","priority":12,"when":{"cold":{"ton":{"outdoor_temp":"<-10"},"hours":2}},"then":["build a heater in the barracks"]}}
{"id":"7","cmd":"export","name":"my-ladder"}
{"id":"8","cmd":"import","json":{"version":2,"gates":[],"tags":{"constants":{},"variables":{}}},"dry_run":true}
```

Owner-only edits (a constant, switching a book rung off) need `"owner": true`, which only the owner's CLI side sets, never chat.
