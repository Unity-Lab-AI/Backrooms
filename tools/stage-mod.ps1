param(
    [string] $LocalModsPath,
    [string] $RimSortSettingsPath = (Join-Path $env:LOCALAPPDATA 'RimSort/settings.json'),
    [switch] $UpdateExisting
)
. (Join-Path $PSScriptRoot 'BuildCommon.ps1')
$repoRoot = Get-RimroomsRoot
if (-not $LocalModsPath) { $LocalModsPath = (Get-RimSortInstancePaths $RimSortSettingsPath).LocalModsPath }
if (-not $LocalModsPath -or -not (Test-Path -LiteralPath $LocalModsPath -PathType Container)) {
    throw 'The configured RimSort Local Mods directory is missing. Correct it in RimSort or supply its confirmed path.'
}
if (@(Get-Process -Name RimWorldWin64, RimWorld -ErrorAction SilentlyContinue).Count -gt 0) {
    throw 'Close RimWorld before staging a new DLL. The script will not stop or start it.'
}
$LocalModsPath = [IO.Path]::GetFullPath($LocalModsPath)
$destination = Assert-RimroomsChildPath (Join-Path $LocalModsPath 'Rimrooms - Async Industries') $LocalModsPath
$source = Join-Path $repoRoot 'Mod/Rimrooms - Async Industries'
$manifest = Get-RimroomsPackageManifest $source
$builtManifestPath = Join-Path $repoRoot 'artifacts/build/package-manifest.json'
if (-not (Test-Path -LiteralPath $builtManifestPath)) { throw 'Build first: no successful build manifest exists.' }
$builtManifest = [IO.File]::ReadAllText($builtManifestPath) | ConvertFrom-Json
if ($builtManifest.PackageId -ne $manifest.PackageId -or $builtManifest.Version -ne $manifest.Version -or $builtManifest.Files.Count -ne $manifest.Files.Count) {
    throw 'Package changed after its successful build. Build again before staging.'
}
foreach ($file in $manifest.Files) {
    $built = @($builtManifest.Files | Where-Object Path -ceq $file.Path)
    if ($built.Count -ne 1 -or $built[0].SHA256 -ne $file.SHA256) { throw "Package changed after build: $($file.Path)" }
}
$backup = $null
if (Test-Path -LiteralPath $destination) {
    if (-not $UpdateExisting) { throw 'An installed Rimrooms folder exists. Inspect it, then use -UpdateExisting to back it up and replace only this mod.' }
    [xml] $existingAbout = [IO.File]::ReadAllText((Join-Path $destination 'About/About.xml'))
    if ($existingAbout.ModMetaData.packageId -cne 'Rimrooms.AsyncIndustries') { throw 'Existing folder belongs to another package; refusing to move it.' }
    $backup = Assert-RimroomsChildPath (Join-Path $repoRoot ('artifacts/staging-backups/' + [Guid]::NewGuid().ToString('N'))) $repoRoot
    $null = New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($backup)) -Force
    # Both resolved absolute targets were checked above; keep the old mod recoverable.
    Move-Item -LiteralPath $destination -Destination $backup
}
try {
    Copy-Item -LiteralPath $source -Destination $destination -Recurse
    $installed = Get-RimroomsPackageManifest $destination
    foreach ($file in $manifest.Files) {
        $copy = @($installed.Files | Where-Object Path -ceq $file.Path)
        if ($copy.Count -ne 1 -or $copy[0].SHA256 -ne $file.SHA256) { throw "Staged file differs: $($file.Path)" }
    }
} catch {
    # Preserve a failed copy rather than deleting files. Restore a previous installation.
    if (Test-Path -LiteralPath $destination) {
        $failed = Assert-RimroomsChildPath (Join-Path $repoRoot ('artifacts/staging-failed/' + [Guid]::NewGuid().ToString('N'))) $repoRoot
        $null = New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($failed)) -Force
        Move-Item -LiteralPath $destination -Destination $failed
    }
    if ($backup) { Move-Item -LiteralPath $backup -Destination $destination }
    throw
}
$receipt = [ordered]@{ PackageId = $manifest.PackageId; Version = $manifest.Version; Destination = $destination; Backup = $backup; Files = $manifest.Files; ProfileChanged = $false; GameLaunched = $false }
$receipt | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $repoRoot 'artifacts/build/staging-receipt.json') -Encoding UTF8
Write-Output "Staged and hash-checked $($manifest.Files.Count) package files at $destination"
Write-Output 'Refresh local mods in RimSort. The owner reviews the 295-entry target, adds the separate QA overlay, sorts and launches.'
