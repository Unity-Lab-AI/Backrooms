# Current asset package paths — 2026-10-12

Current Rimrooms and RimPLC content folders are named **`1.7/`**. Both declared game-version
loaders use that folder. This owner-directed naming correction preserves the original asset bytes.

Older generation/provenance records retain their actual dated `1.6/` destinations. To locate
those same assets now, replace only the package-folder segment:

| Historical package path | Current package path |
|---|---|
| `Mod/Rimrooms - Async Industries/1.6/<relative asset>` | `Mod/Rimrooms - Async Industries/1.7/<relative asset>` |
| `RimPLC/1.6/<relative asset>` | `RimPLC/1.7/<relative asset>` |

Original source masters, filenames, prompts, hashes and `About/Preview.png` paths are unchanged.
Current cutters/build/export utilities write to `1.7/`. Do not rename an installed provider's
folders or relabel past game-version/API observations.

See [the layout record](../../docs/implementation/CONTENT_FOLDER_1_7_LAYOUT.md) for evidence.
