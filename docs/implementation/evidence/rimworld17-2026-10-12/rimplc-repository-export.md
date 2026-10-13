# RimPLC standalone repository export — 2026-10-12

## Scope and result

The owner requested a standalone RimPLC repository at
`https://git.unityailab.com/GFourteen/RimPLC` and a matching GitHub mirror.
The lead confirmed the Forgejo repository exists and has no branches. Creation of
the public GitHub mirror remains a separate approval/publication step.

Implemented **`tools/export-rimplc-repo.py`**, which prepares a local publication
tree only. It contains no Git, network, game-launch, staging-to-game, training or
pod operation. The lead owns compilation, manifest capture, production execution,
repository creation, commits and remote pushes.

The exporter was parsed with Python 3.10 `ast.parse` successfully. This is syntax
evidence only. No exporter execution, unit test, fixture, compilation or game run
was performed by the export agent. The output and receipt paths below are
**planned until the lead's production command succeeds**.

## Inputs read

- `RimPLC/About/About.xml` and `LoadFolders.xml`: `Operator.RimPLC`, author
  `Operator`, version `0.1.0`, declared targets 1.6 and 1.7, shared root + `1.6/`
  loading, no hard dependencies.
- `RimPLC/README.md`: project context, recorded by hash rather than copied with
  parent-repository links.
- `RimPLC/Source/RimPLC/`: the mod's own C# source and project; local game
  references have `Private=false`, output is `1.6/Assemblies/RimPLC.dll`.
- `RimPLC/Source/RimPLC.BridgeTools/`: the optional companion's own source and
  project; SDK path is supplied through `RimBridgeSdkPath`, output is
  `BridgeTools/RimPLC.BridgeTools.dll`.
- `docs/wiki/rimplc.md`: current public user guide. The standalone copy removes
  front matter and changes the two Rimrooms wiki links to their live HTML URLs.
- `docs/rimplc/schema/`: six JSON schemas, with their mutual local references
  checked against the copied set.
- Root `LICENSE`: original MIT license, copied unchanged.
- `docs/RIMPLC_DESIGN.md` and `tools/export-public-repo.py`: inspected for project
  context and the existing public-export conventions; neither is copied.

## Build manifest contract

Default input: `artifacts/build/rimplc-package-manifest.json`.

Required shape:

```json
{
  "packageId": "Operator.RimPLC",
  "modVersion": "0.1.0",
  "supportedVersions": ["1.6", "1.7"],
  "files": [
    {"path": "About/About.xml", "bytes": 123, "sha256": "64 hexadecimal characters"}
  ]
}
```

The size key may also be `length` or `size`. Every file path is relative to
`RimPLC/`, uses `/`, and must exactly match the explicit allowlist below. The
example size/hash is illustrative, not a receipt. Actual bytes and SHA-256 values
must be captured after the successful build. Identity, version and game targets
must agree with `About.xml`; both project versions must agree with it as well.

Required manifest files:

1. `About/About.xml`
2. `LoadFolders.xml`
3. `1.6/Assemblies/RimPLC.dll`
4. `1.6/Defs/MainButtonDefs/RimPLC_MainButtons.xml`
5. `Languages/English/Keyed/RimPLC.xml`
6. `Presets/LadderV2.json`

Optional seventh file: `BridgeTools/RimPLC.BridgeTools.dll`, only when its owned
build output is included in the fresh manifest. PDBs and other DLLs are refused.
The manifest does not prove gameplay or 1.7 engine compatibility.

## Standalone tree

```text
.local/export/RimPLC/                 planned repository checkout
  About/About.xml
  LoadFolders.xml
  1.6/
    Assemblies/RimPLC.dll
    Defs/MainButtonDefs/RimPLC_MainButtons.xml
  Languages/English/Keyed/RimPLC.xml
  Presets/LadderV2.json
  BridgeTools/RimPLC.BridgeTools.dll   optional, separate installation destination
  Source/
    RimPLC/                          own .cs and .csproj
    RimPLC.BridgeTools/               own .cs and .csproj
  docs/
    USER_GUIDE.md
    schema/                          ladder, mark, rung, sensor, tag, tools schemas
  README.md                          generated standalone instructions
  LICENSE                            unchanged root license
  .gitignore
```

The generated README uses `Source/...` paths that actually exist in this tree.
It documents the core and optional companion builds, the loadable package subset,
the file API, and the companion's separate `<RimWorld>/BridgeTools/RimPLC/`
destination. The shipped preset is sufficient; no playbook generator, parent
repository, training dataset or private autopilot is needed.

The public tree excludes `bin/`, `obj/`, IDE/cache directories, PDBs, game and
provider DLLs, `.local/`, `.claude/`, training, credentials and the working ledger.
Only the two named owned DLL paths can enter through the manifest. Own source is
limited to `.cs`, `.csproj`, `.props` and `.targets`; unexpected files are refused.
Text inputs are checked for common embedded private-key/credential markers;
this is a bounded guard, not a claim to detect every possible secret.

## Production command and publication handoff

From the Backrooms root, after compilation and manifest capture:

```powershell
python tools/export-rimplc-repo.py
```

After the lead confirms that the requested public GitHub repository exists:

```powershell
python tools/export-rimplc-repo.py --github-url https://github.com/G-Fourteen/RimPLC
```

Without that flag the README links the existing Forgejo project and says the
GitHub mirror is pending, without advertising a nonexistent mirror as available.
The flag only changes README text; it never creates or contacts a repository.

The command reports the exact output, receipt, file counts, package version,
declared game targets and source snapshot SHA-256. Its ownership receipt is
planned at `.local/export/RimPLC-export-state.json`, outside the public tree.
The receipt records each input/exported file's size and SHA-256, the build
manifest, source snapshot, README/user-guide provenance, staging path and
`git_or_network_called: false`.

The lead should inspect that receipt and public tree before committing or
pushing, then record actual remote results separately. An exporter success
confirms a local file snapshot, never a repository creation or push.

## Preservation and recovery

- Paths must stay under the project and managed `.local/export/` boundary;
  absolute/traversing/colon/backslash file paths, duplicate case variants,
  symlinks and Windows reparse points are refused.
- Inputs are read again by hash before publication. A changed package, source,
  manifest or guide causes refusal.
- Every run builds a fresh `.RimPLC-stage-<UUID>/payload/` tree. Staging evidence
  is retained. A missing output is published with a directory rename; a managed
  checkout is updated only through replacements of previously owned, unchanged
  files. Its `.git` metadata is preserved.
- An unexpected/untracked file, locally changed owned file, or retired owned
  path causes refusal and remains untouched. The exporter never recursively
  deletes a directory or silently removes a stale file.
- If publication fails partway through an existing checkout, retain its receipt
  and staging tree, inspect old/new hashes, and resolve explicitly. Do not wipe
  the checkout to make the command pass. A fresh alternative may be selected
  with `--output .local/export/RimPLC-<suffix>`.
- The 1.7 claim remains a declared development target; no runtime acceptance was
  performed here. Source/export integrity and gameplay compatibility are separate.
