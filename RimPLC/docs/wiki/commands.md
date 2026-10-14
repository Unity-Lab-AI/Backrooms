---
title: Commands and the AI API
summary: "The command file for an external assistant, and the same commands as RimBridgeServer tools."
---

# Commands and the AI API

Everything the window can do, an external program can do too -- the same `Api` answers both.
There are two routes; the commands and their results are identical on each.

## The command file

With no bridge installed, RimPLC reads commands from a file in the game's configuration folder
and answers in a file beside it:

```
<RimWorld config folder>/RimPLC/inbox.jsonl    one JSON object per line, written by the client
<RimWorld config folder>/RimPLC/outbox.jsonl   {"id":..,"cmd":..,"result":{..}} per line, appended
```

The inbox is claimed by an atomic rename, a bounded number of lines run per pass and the rest
stay queued. It runs once a real second, so it works while the game is paused.

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

## The commands

| Command | Args | Result |
|---|---|---|
| `read_ladder` | `top` (default 4), `all` | the live rungs with the measured values that made them fire, plus tags, marks, player rungs, unknown keys, unresolved conditions, disabled rungs, not-applicable rungs, the scan tick |
| `read_state` | `keys` (optional filter) | the sensor values measured this scan; absent keys are unmeasured |
| `set_tag` | `name`, `value` (empty clears), `owner` | override a variable within its bounds; a constant needs the owner flag |
| `set_mark` | `name`, `value` | set a boolean or numeric mark |
| `set_host` | a dictionary of readings | push host inputs (readings measured outside the game) before a scan; merged first, a game reading of the same name wins, dropped after 120 s |
| `upsert_rung` | `rung` | add or replace a player rung; validated like the editor |
| `remove_rung` | `id` | remove a player rung, or drop the player copy of a preset rung |
| `enable_rung` | `id`, `enabled`, `owner` | switch a rung on or off; switching a preset rung off needs the owner flag |
| `letters_seen` | -- | mark every letter on the stack as read |
| `export` | `name` | write the ladder to `RimPLC/exports/<name>.json` |
| `import` | `json`, `dry_run` | merge a ladder; `dry_run` returns the diff without applying it |

A refusal is a result with `ok: false` and a reason in plain words. The shapes of every command,
rung, sensor, tag and mark are frozen in the repository's `docs/schema/` JSON schemas.

### The owner flag

`"owner": true` unlocks the owner-only changes -- a constant, a preset rung switched off. It is
meant to be set only by the owner's own client, never by anything that relays chat or another
user's input; the flag is the whole guard, so the client that sets it is the one being trusted.

## The RimBridgeServer tools

With RimBridgeServer installed, the companion
`BridgeTools/RimPLC.BridgeTools.dll` exposes the same commands as bridge tools:

```
rimplc/read_ladder   rimplc/read_state    rimplc/set_tag       rimplc/set_mark
rimplc/upsert_rung   rimplc/remove_rung   rimplc/enable_rung   rimplc/letters_seen
rimplc/export        rimplc/import
```

Each call hops to the game's main thread and runs the shared `Api`, so a tool and its file
command return the same text. Install exactly one copy of the companion -- the one inside the
mod folder -- as [Install](install.md) explains.

## Host inputs

`set_host` lets a program outside the game contribute readings the game cannot know: whether a
person is at the keyboard, how long since the last spoken line, whether a chat question is
waiting. They appear in the Sensors tab under **Stream**, are merged before the game's own
readings (a game reading of the same name wins), and are dropped after 120 seconds so a client
that stops pushing does not leave stale truth in the ladder.
