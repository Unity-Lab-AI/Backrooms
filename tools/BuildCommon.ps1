Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-RimroomsRoot {
    return [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
}

function Get-RimSortInstancePaths {
    param([string] $SettingsPath = (Join-Path $env:LOCALAPPDATA 'RimSort/settings.json'))
    if (-not (Test-Path -LiteralPath $SettingsPath -PathType Leaf)) {
        throw 'RimSort settings were not found. Pass the installed game or Local Mods path explicitly.'
    }
    $settings = [IO.File]::ReadAllText($SettingsPath) | ConvertFrom-Json
    $property = $settings.instances.PSObject.Properties[$settings.current_instance]
    if ($null -eq $property) { throw 'The current RimSort instance is not present in settings.' }
    return [PSCustomObject]@{
        Instance = $settings.current_instance
        GamePath = $property.Value.game_folder
        LocalModsPath = $property.Value.local_folder
        SettingsPath = [IO.Path]::GetFullPath($SettingsPath)
    }
}

function Assert-RimroomsChildPath {
    param([string] $Path, [string] $Parent)
    $full = [IO.Path]::GetFullPath($Path).TrimEnd('\', '/')
    $base = [IO.Path]::GetFullPath($Parent).TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
    if (-not $full.StartsWith($base, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Path is outside the intended directory: $full"
    }
    # Refuse links/junctions on existing path components; they can escape the lexical root.
    $current = $full
    while ($current) {
        if (Test-Path -LiteralPath $current) {
            if ((Get-Item -LiteralPath $current -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) {
                throw "Refusing a reparse point in a build/staging path: $current"
            }
        }
        $parentPath = [IO.Path]::GetDirectoryName($current)
        if ($parentPath -eq $current) { break }
        $current = $parentPath
    }
    return $full
}

function Get-RimroomsPackageManifest {
    param([string] $PackageRoot)
    $root = [IO.Path]::GetFullPath($PackageRoot)
    [xml] $about = [IO.File]::ReadAllText((Join-Path $root 'About/About.xml'))
    if ($about.ModMetaData.name -cne 'Rimrooms - Async Industries' -or
        $about.ModMetaData.author -cne 'Operator' -or
        $about.ModMetaData.packageId -cne 'UnityLabAI.RimroomsAsyncIndustries') {
        throw 'Package identity does not match the accepted project identity.'
    }
    $required = @('About/About.xml', 'About/Preview.png', 'About/License.txt', 'LoadFolders.xml',
        '1.6/Assemblies/RimroomsAsyncIndustries.dll', '1.6/Defs/MainButtonDefs/RR_MainButtons.xml',
        '1.6/Languages/English/Keyed/RR_Operations.xml', '1.6/Languages/English/DefInjected/MainButtonDef/RR_MainButtons.xml')
    foreach ($relative in $required) {
        if (-not (Test-Path -LiteralPath (Join-Path $root $relative) -PathType Leaf)) { throw "Package file missing: $relative" }
    }
    $entries = @()
    foreach ($file in Get-ChildItem -LiteralPath $root -File -Recurse | Sort-Object FullName) {
        $null = Assert-RimroomsChildPath $file.FullName $root
        $relative = $file.FullName.Substring($root.Length + 1).Replace('\', '/')
        if ($relative -notin $required) { throw "Unapproved foundation package file: $relative. Update the explicit package contract before adding content." }
        if ($file.Extension -eq '.xml') {
            $null = [xml] [IO.File]::ReadAllText($file.FullName)
        }
        $entries += [ordered]@{ Path = $relative; Bytes = $file.Length; SHA256 = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash }
    }
    return [ordered]@{
        PackageId = 'UnityLabAI.RimroomsAsyncIndustries'
        Version = [string] $about.ModMetaData.modVersion
        Files = $entries
    }
}
