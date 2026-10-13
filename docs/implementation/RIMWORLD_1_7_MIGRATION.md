# RimWorld 1.7 migration — Rimrooms and RimPLC

**Owner direction recorded 2026-10-12.** This is the current game-version target record for both mods. It separates a declared loading target from observed runtime compatibility. Existing dated research, save results and compiled reference hashes remain evidence of the game version actually used.

## Owner instructions

> the preview image for the mod i need to read this and set the mod version to 1.7 for our mod and remake the mod preview image exactly as it is just change the 1.6 to a 1.6 and then fix the mod to use 1.7 as per: https://store.steampowered.com/news/app/294100/view/672882362547178633

Preview correction confirmed:

> Yes — change it to 1.7

> need all docs and wiki updated too

Expanded package/repository scope:

> rimroom rimPLC and all support documents and may need to add a github rim PLC and add it to it and here is the git to use for Rim PLC: https://git.unityailab.com/GFourteen/RimPLC

Follow-up on the visible `1.6` directory name:

> might need to fix that all around the backrooms folder

**Package layout update — 2026-10-12:** the current shared payload is now named `1.7/` in both packages. The earlier same-day layout used `1.6/`; dated build/research/evidence records preserve that path as recorded. This rename does not change the compiled API baseline, a save identity or the compatibility evidence boundary. Both retained game 1.6 and target game 1.7 select the one current `1.7/` directory through `LoadFolders.xml`.

The requested `1.7` is the RimWorld target. No separate new release number was specified for either mod: Rimrooms remains `0.13.0-dev`, RimPLC remains `0.1.0`. Metadata, project version, prior release records and main-menu release display must agree on that distinction.

## Official announcement and evidence boundary

[Ludeon announcement, 2026-10-12](https://store.steampowered.com/news/app/294100/view/672882362547178633), read in the browser directly after the search reader could not retrieve it:

- RimWorld 1.7 uses Ludeon's Waylith engine and is available through Steam's unstable branch. The normal Steam branch remains 1.6 at this announcement.
- Ludeon expects most existing mods to work without code changes. Its guidance is to test a mod before publishing it as compatible; changing a version label alone is not runtime evidence.
- New C# features are available to modders; adopting a new compiler/runtime is optional, not a requirement inferred for these packages.

Local installed target at inspection: **RimWorld 1.6.4871 rev590**, Steam build **23969874**. Core assembly SHA256: `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`. No 1.7 references, startup, saved-game observation or full-profile compatibility result was obtained in this task. The installation/profile is not switched to unstable by these package edits.

## Package and source treatment

| Package | Declared game versions | Load mapping | Own release |
| --- | --- | --- | --- |
| `Mod/Rimrooms - Async Industries` | 1.6, 1.7 | `v1.6` and `v1.7` both select `1.7` | 0.13.0-dev |
| `RimPLC` | 1.6, 1.7 | Each selects `/` and `1.7`, retaining root language/preset content | 0.1.0 |

The physical `1.7/` directory is a shared payload, not an instruction to load only in game 1.7. `LoadFolders.xml` chooses it for each declared game target. Keep one copy of the Defs, images and DLLs; do not recreate a duplicate `1.6/` payload. Current build destinations, package allowlists, public exports and install guides must point to `1.7/`. Older dated records use the original paths as evidence of their checkpoint, not as current copy instructions.

Both projects retain the reviewed .NET Framework 4.7.2/C# 7.3 assembly path and native references. The existing build pin remains the actual 1.6 pin. No game binary is imported into the repository and no invented 1.7 assembly hash is introduced. Later inspected 1.7 references/API changes may justify a distinct build, but require their own saved evidence.

`check-compliance.py` now checks both declared targets and shared load mappings. `check-package-integrity.py` resolves the declared mappings rather than requiring a same-named physical directory per version. Static package structure and compile evidence are distinct from runtime acceptance. See [package-migration.md](evidence/rimworld17-2026-10-12/package-migration.md).

## Preview and documentation

The original charcoal/gold preview was edited with the built-in image tool. Only the upper-left game label was requested to become `RIMWORLD 1.7`; title, subtitle, tagline, Operator credit, layout and door art remain in the approved composition. No development-build text was added.

- Final: `Mod/Rimrooms - Async Industries/About/Preview.png`.
- Backup, delivered copy and prompt: `outputs/preview-touchup-2026-10-12/`.
- Final PNG SHA256: `2a9fff02da22c4a08feae8d1813fd58e3c2779d59df533a666d2213b46024a5e`.

Current agent guides, design/build/support contracts and wiki describe the 1.7 target and retained baseline. Dated 1.6 per-mod reviews, collection titles, play observations, API comments, arithmetic and evidence hashes are not relabelled. Generated register/wiki/site pages must carry the same boundary and keep their relative links valid.

## RimPLC repositories and completion record

The supplied [Forgejo RimPLC repository](https://git.unityailab.com/GFourteen/RimPLC) was verified as accessible and empty. The matching GitHub repository was initially absent. Automatic approval review rejected public creation from the conditional wording; preparation continued without circumventing that rejection. After reviewing the prepared export, the owner explicitly answered **"Yes — create public GitHub and publish to both"**. [GitHub RimPLC](https://github.com/G-Fourteen/RimPLC) was then actually created and read back as public. This approval covers the reviewed standalone RimPLC export and the two named repositories, not unrelated model/job changes.

The standalone export must contain RimPLC's actual mod files, original source, optional original bridge companion/source, license and usable support documentation. It must exclude the Backrooms work ledger, voice/brain jobs, credentials, tool caches, game/provider assemblies and `.claude/` workflow. Source lives in this workspace; an export is a reviewed distribution copy, not a branch checkout of the running workspace.

Build and generated-doc receipts for this checkpoint are recorded under `docs/implementation/evidence/rimworld17-2026-10-12/`. Rimrooms, RimPLC core and the optional RimPLC bridge each compiled with **zero warnings/errors** against the reviewed installed 1.6 references. Rimrooms' compiled DLL retains SHA256 `AF7BB486CA3BF71FFCC49586BCAD54428F754E87C85209FB7517F20C8B0FA129`. The package manifest covers 200 Rimrooms files; the standalone RimPLC export contains 33 files, including seven package/companion files, 16 own source/project files, six schemas, license, README, user guide and ignore rules. The wiki renderer regenerated 17 pages and a stylesheet. Remote publication is proved by the final tool read-back, not by a local intention. No 1.7 release tag or compatibility pass is implied by this migration.

## Remaining acceptance

1. Obtain an official owned 1.7 installation/reference target without overwriting the current profile/save/session; record executable/layout, assemblies, game build and provider versions.
2. Inspect any API/engine differences affecting native/reflected UI, rendering, portal routing and work, saved state, multiplayer and the optional RimPLC bridge.
3. Perform separately authorized 1.7 startup/gameplay/save/co-op checks, recording the actual game version and profile. Old 1.6 results do not close these items.
4. After those results, promote verified 1.7 compatibility and publish a release under the existing distribution procedure.

The active voice/brain training belongs to another task. These changes must not alter its sources, manifests, models, pod jobs or launch configuration. Preserve its current `NOW.md` context when adding this migration handoff.
