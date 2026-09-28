param(
    [string] $SteamApps = 'C:\Program Files (x86)\Steam\steamapps',
    [string] $ServerRoot = 'C:\Users\gfour\Desktop\RimWorld Server\Server-win-x64-new',
    [string] $ClientConfig = 'C:\Users\gfour\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml'
)

# Read-only local snapshot check. Never starts a process or changes a profile.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$metadata = @(Import-Csv -LiteralPath (Join-Path $repoRoot 'docs/research/installed-mod-metadata-2026-09-27.csv'))
if ($metadata.Count -ne 294) { throw 'Expected 294 historical metadata records' }
$pinText = [IO.File]::ReadAllText((Join-Path $repoRoot 'docs/research/RWT_AND_GRAVSHIP_FEASIBILITY.md'))
$issues = [Collections.Generic.List[string]]::new()
$checked = 0
$deltaPath = Join-Path $repoRoot 'docs/research/profile-deltas-2026-09-28.json'
$deltas = @(([IO.File]::ReadAllText($deltaPath) | ConvertFrom-Json).deltas)
$appliedDeltas = 0

function Check-Hash([string] $Label, [string] $Path, [string] $Expected) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        $issues.Add("Missing: $Label")
        return
    }
    $actual = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
    if ($actual -ne $Expected) { $issues.Add("Hash differs: $Label (observed $actual)") }
}

foreach ($row in $metadata) {
    $relative = $row.MetadataRelativePath
    if ($relative.StartsWith('game/')) {
        $path = Join-Path (Join-Path $SteamApps 'common/RimWorld') $relative.Substring(5)
    } elseif ($relative.StartsWith('workshop/')) {
        $path = Join-Path (Join-Path $SteamApps 'workshop/content') $relative.Substring(9)
    } else {
        $issues.Add("Unknown metadata path type: row $($row.LoadOrder)")
        continue
    }
    $expected = $row.AboutXmlSHA256
    $delta = @($deltas | Where-Object { $_.load_order -eq $row.LoadOrder })
    if ($delta.Count -gt 1) { throw "Duplicate delta for row $($row.LoadOrder)" }
    if ($delta.Count -eq 1) {
        $record = $delta[0]
        if ($record.package_id -cne $row.PackageID -or $record.old_about_sha256 -ne $expected -or $record.old_version -ne $row.LocalModVersion) {
            throw "Delta does not identify historical row $($row.LoadOrder)"
        }
        if (-not (Test-Path -LiteralPath (Join-Path $repoRoot $record.review_record))) { throw 'Delta review record is missing' }
        $expected = $record.new_about_sha256
        [xml] $currentAbout = [IO.File]::ReadAllText($path)
        if ($currentAbout.ModMetaData.modVersion.InnerText -ne $record.new_version) { $issues.Add("Delta version differs: row $($row.LoadOrder)") }
        $selectors = @{
            PackageID = '/ModMetaData/packageId'
            SupportedVersions = '/ModMetaData/supportedVersions/li'
            HardDependencies = '/ModMetaData/modDependencies/li/packageId'
            LoadAfter = '/ModMetaData/loadAfter/li'
            LoadBefore = '/ModMetaData/loadBefore/li'
            IncompatibleWith = '/ModMetaData/incompatibleWith/li'
        }
        foreach ($field in $selectors.Keys) {
            $values = @($currentAbout.SelectNodes($selectors[$field]) | ForEach-Object { $_.InnerText.Trim() } | Select-Object -Unique)
            if (($values -join '; ') -cne $row.$field) { $issues.Add("Delta changes unreviewed field $field at row $($row.LoadOrder)") }
        }
        foreach ($payload in $record.payload_pins) {
            $payloadPath = Join-Path (Join-Path $SteamApps "workshop/content/294100/$($record.workshop_id)") $payload.path
            Check-Hash "row $($row.LoadOrder) $($payload.path)" $payloadPath $payload.sha256
            $checked++
        }
        $appliedDeltas++
    }
    Check-Hash "row $($row.LoadOrder) $($row.PackageID) About.xml" $path $expected
    $checked++
}

$gameRoot = Join-Path $SteamApps 'common/RimWorld'
$workshop = Join-Path $SteamApps 'workshop/content/294100'
$pins = @(
    @{ Label = 'RimWorld game version file'; Path = (Join-Path $gameRoot 'Version.txt') },
    @{ Label = 'RimWorld runtime executable'; Path = (Join-Path $gameRoot 'RimWorldWin64.exe') },
    @{ Label = 'Core game assembly'; Path = (Join-Path $gameRoot 'RimWorldWin64_Data/Managed/Assembly-CSharp.dll') },
    @{ Label = 'Harmony active assembly'; Path = (Join-Path $workshop '2009463077/Current/Assemblies/0Harmony.dll') },
    @{ Label = 'Client mod profile'; Path = $ClientConfig },
    @{ Label = 'Server mod profile'; Path = (Join-Path $ServerRoot 'Configs/ModConfig.json') },
    @{ Label = 'RWT client assembly'; Match = 'RTClient.dll'; Path = (Join-Path $workshop '3005289691/1.6/Assemblies/RTClient.dll') },
    @{ Label = 'RWT client assembly'; Match = 'RTNetwork.dll'; Path = (Join-Path $workshop '3005289691/1.6/Assemblies/RTNetwork.dll') },
    @{ Label = 'RWT client assembly'; Match = 'RTShared.dll'; Path = (Join-Path $workshop '3005289691/1.6/Assemblies/RTShared.dll') },
    @{ Label = 'RWT server executable'; Path = (Join-Path $ServerRoot 'RTServer.exe') }
)
foreach ($pin in $pins) {
    $lines = @($pinText -split '\r?\n' | Where-Object { $_.StartsWith("| $($pin.Label) |") })
    if ($pin.ContainsKey('Match')) { $lines = @($lines | Where-Object { $_.Contains($pin.Match) }) }
    if ($lines.Count -ne 1 -or $lines[0] -notmatch '[A-F0-9]{64}') {
        $issues.Add("Expected one documented digest: $($pin.Label)")
        continue
    }
    $expected = $Matches[0]
    Check-Hash $pin.Label $pin.Path $expected
    $checked++
}
$manifest = [IO.File]::ReadAllText((Join-Path $SteamApps 'appmanifest_294100.acf'))
if ($appliedDeltas -ne $deltas.Count) { $issues.Add('One or more recorded deltas did not identify a metadata row') }
if ($manifest -notmatch '"buildid"\s+"23969874"') { $issues.Add('Steam build ID differs from 23969874') }
[ordered]@{
    Scope = 'Read-only local metadata, binary and profile hashes; no gameplay or remote-release recheck'
    CheckedHashes = $checked
    MetadataRows = $metadata.Count
    ReviewedMetadataDeltas = $appliedDeltas
    SteamBuildIDMatches = ($manifest -match '"buildid"\s+"23969874"')
    Issues = @($issues)
    Result = $(if ($issues.Count -eq 0) { 'PASS' } else { 'FAIL' })
} | ConvertTo-Json -Depth 4
if ($issues.Count) { exit 1 }
