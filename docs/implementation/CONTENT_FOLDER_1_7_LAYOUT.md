# Current package folders: 1.7 — 2026-10-12

Owner direction, verbatim:

> "might need to fix that all around the backrooms folder"
>
> "i doont want my 1.7 saying 1.6"

## Scope and preserved behavior

This is a package-layout correction to [the 1.7 migration](RIMWORLD_1_7_MIGRATION.md),
following [regression containment](../REGRESSION_CONTAINMENT.md). It changes physical content
folder names, build destinations, load mappings and paths in current documentation/tooling.
Package IDs, releases, Def names, saved IDs, gameplay code and original assets are unchanged.
Both declared game versions load the single current folder:

| Package | Current content | Game 1.6 loader | Game 1.7 loader |
|---|---|---|---|
| Rimrooms | `Mod/Rimrooms - Async Industries/1.7/` | `1.7` | `1.7` |
| RimPLC | `RimPLC/1.7/` | `/`, `1.7` | `/`, `1.7` |

The mod's own releases remain Rimrooms **0.13.0-dev** and RimPLC **0.1.0**.
The preview artwork already reads RimWorld 1.7. A folder name does not establish API/runtime compatibility.

## Completed work

- Moved the 196 Rimrooms content files and three RimPLC content files to `1.7/` with
  before/after byte and SHA256 comparisons. All original bytes are preserved, including symbols.
- Updated both `LoadFolders.xml` files and RimPLC's project output directory.
- Updated the 200-entry Rimrooms allowlist and both current package manifests.
- Updated 23 package/build/asset/site/export tool files and 221 operational `.local/register`
  and `.local/qa` scripts so future operations use the current folder.
- Updated current design/build/agent/wiki guidance. Repaired 40 navigation hrefs in 19 archived
  reports, preserving their historical labels, observed versions and hashes.
- Regenerated the asset gallery, site navigation, 17 wiki pages and readable documents.
- Refreshed both local distribution exports and the 200-file copyable Rimrooms ZIP.
- Preserved RimPLC's old export and ownership receipt in
  `.local/export/RimPLC-before-1-7-2026-10-12*`, prepared a new export through unchanged ownership
  guards, and retained its existing ordinary Git directory/history. No force push is used.

The old dated provenance, API inspection, build/play records and explicit backup snapshots remain
historical. Current content referenced by old `1.6/` package paths is now at the same relative
location under `1.7/`; see [the asset path note](../../assets/source/CONTENT_PATHS.md).
The installed RimBridgeServer SDK path remains the provider's actual `1.6/` path; it is not ours to rename.

## Evidence and limits

See [layout-results.json](evidence/content-folder-2026-10-12/layout-results.json),
the two package manifests in that folder, and the pre-move snapshot at
`artifacts/build/content-folder-migration-2026-10-12-before.json`.

Rimrooms, RimPLC core and its optional bridge compiled with zero warnings/errors against the
existing installed **1.6.4871 rev590** references. Their shipped DLL hashes remain unchanged:

| DLL | SHA256 |
|---|---|
| Rimrooms | `AF7BB486CA3BF71FFCC49586BCAD54428F754E87C85209FB7517F20C8B0FA129` |
| RimPLC | `89f2a33c56fc8cacca033a482a24bc5118b0f464aa3f7fd5ac928eeda8563666` |
| RimPLC bridge | `eb2482acc98ea8e89aab4973c873143d75a6aed489cf44c180067f4a272750bc` |

The normal Windows PowerShell build-script invocation was refused by its AuthorizationManager;
the equivalent direct `dotnet build --no-restore` commands succeeded without changing that policy.
Python/PowerShell parsing, file/hash inspection and diff checks are static evidence. No gameplay
tests were run; actual 1.7 API/runtime/profile acceptance remains pending.

The game install, Local Mods, RimSort profile, saves, live training/model jobs and pods are untouched.
The active parent checkout is not switched or published during those jobs. Its source/docs changes
remain here for the lead's normal source integration. The approved standalone distribution
checkpoints are published separately; actual remote read-backs in tool output are the receipts.
