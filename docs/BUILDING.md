# Building Rimrooms - Async Industries

**Current deliverable:** private `0.2.0` development slice. See the [current build record](implementation/PHASE_2_BUILD_RECORD.md) for actual scenario, gate, destination, expedition, evidence, research and interface implementation. Gameplay acceptance and the complete campaign remain in the [master TODO](PREPRODUCTION_AND_IMPLEMENTATION_TODO.md).

## Requirements and references

- Windows PowerShell and .NET SDK **9.0.308**, selected by [global.json](../global.json). A later patch in this SDK feature band is allowed by the resolver; record the actual SDK on each build.
- A locally installed, owned RimWorld 1.6. The script uses `-RimWorldPath`, then `RIMWORLD_PATH`, then the current instance's game folder in RimSort settings. It never loads or starts the game.
- [The project](../src/RimroomsAsyncIndustries/RimroomsAsyncIndustries.csproj) uses C# 7.3, deterministic Release/Debug builds, .NET Framework **4.7.2**, and treats compiler warnings as errors. `net472` is our selected compiler baseline; Core has no `TargetFrameworkAttribute`, so it is not a claim about an official runtime target. Runtime acceptance is still required.
- Restore uses the exact `Microsoft.NETFramework.ReferenceAssemblies.net472` **1.0.3** package and the committed [lock file](../src/RimroomsAsyncIndustries/packages.lock.json). [NuGet.Config](../NuGet.Config) selects nuget.org. Caches and CLI state stay in ignored `.local/`; internet access is needed on the first restore.
- References resolve under `<game>/RimWorldWin64_Data/Managed`: `Assembly-CSharp.dll`, `UnityEngine.CoreModule.dll`, `UnityEngine.IMGUIModule.dll`, `UnityEngine.TextRenderingModule.dll`. They have `Private=false` and never enter the mod package. The manifest also records installed `mscorlib.dll` as runtime context; compilation uses the reference package's framework assemblies.
- The build refuses a Core DLL whose SHA-256 differs from the [inspected target](implementation/PHASE_1_CORE_SOURCE_REVIEW.md). Review source drift and update the pin with evidence before accepting a different game build. The historical rev590/rev591 label discrepancy remains recorded in the [target audit](research/RWT_AND_GRAVSHIP_FEASIBILITY.md#pinned-local-rimworld-test-target).

## Build

From the repository root:

```powershell
./tools/build.ps1
# If RimSort settings are unavailable:
./tools/build.ps1 -RimWorldPath 'C:\Path\To\RimWorld'
# Optional compiler configuration:
./tools/build.ps1 -Configuration Debug
```

Normal builds restore in locked mode, compile, then package only our DLL and original content. `-NoRestore` is for an already restored, unchanged project. A dependency change must deliberately regenerate and review the lock file with `dotnet restore` before returning to locked builds. Do not commit proprietary references or downloaded inspection output.

| Output | Purpose |
| --- | --- |
| `src/RimroomsAsyncIndustries/bin/<configuration>/net472/` | Local compiler output and debug symbols; ignored |
| `Mod/Rimrooms - Async Industries/` | Sole copyable mod directory; built DLL is ignored by Git |
| `artifacts/build/package-manifest.json` | Exact approved package files, size and SHA-256 |
| `artifacts/build/reference-manifest.json` | Compiler configuration and locally used reference identities |

A clone contains package sources and original assets, but **must be built before copying**: Git does not carry generated DLLs. [package-files.json](../tools/package-files.json) owns the explicit package allowlist, enforced by [BuildCommon.ps1](../tools/BuildCommon.ps1). Add reviewed files to that contract as features enter development. It rejects extra files and malformed XML. It does not prove Def behavior or compatibility. The original card is maintained by [render-preview.ps1](../tools/render-preview.ps1); regenerate it only when its design/version changes, then review and rebuild the manifest.

## Stage for RimSort discovery

```powershell
./tools/stage-mod.ps1
# Only after inspecting an existing Rimrooms installation:
./tools/stage-mod.ps1 -UpdateExisting
```

The default destination is the **Local Mods folder of RimSort's current instance**, read from `%LOCALAPPDATA%/RimSort/settings.json`. An explicit `-LocalModsPath` must be the path confirmed in RimSort. Paths are resolved and reparse points rejected. Staging refuses while RimWorld is running, requires an unchanged successful-build manifest, copies this one package, and verifies every copied hash. It neither selects nor sorts mods. A protected Local Mods directory may require an elevated shell.

An existing installation is never silently overwritten. `-UpdateExisting` first preserves it in `artifacts/staging-backups/<unique-id>/`. A failed copy is preserved separately and the prior package restored when possible; if filesystem access prevents recovery, keep the backup and resolve the reported error before another attempt. The receipt records both paths. Keep these local backups until the replacement is accepted.

On this workstation the inspected Default instance points to `C:\Program Files (x86)\Steam\steamapps\common\Rimworld\Mods`. This is an observation, not a portable default; the tool re-reads settings each time. Refresh local discovery in RimSort. The owner alone reviews/sorts/saves the **295 target entries** and launches. A separately recorded RimBridgeServer QA overlay normally makes **296 loaded entries**. Follow the [launch plan](research/RIMSORT_PACKAGE_AND_LAUNCH_PLAN.md) and [attach-only bridge plan](research/RIMBRIDGE_TEST_HARNESS.md). No test session or active profile is created by these scripts.

## Build failures and evidence

Missing game files, changed Core pin, mismatched versions, failed restore/compilation, missing package files, or stale staging hashes produce a terminating error. Compilation failure does not replace the previous DLL. Package validation can fail after a new DLL is copied; that output must not be staged until a subsequent successful build creates a matching manifest. The installed mod is changed only by the separate staging command.

For each published build, preserve the compiler outcome and manifest in its phase evidence record. The code source, source/API review and feature IDs must be linked together. Actual save/load, UI sizing, native tab navigation, full-profile behavior, and performance are owner-launched acceptance work; no compilation result substitutes for them.
