# Read-only. Reports every installed 0Harmony.dll with its real assembly version, plus the
# RimBridgeServer assembly's declared Harmony reference, so a version mismatch is measured
# rather than inferred. Starts nothing, changes nothing, writes nothing.

$roots = @(
  'C:\Program Files (x86)\Steam\steamapps\workshop\content\294100',
  'C:\Program Files (x86)\Steam\steamapps\common\Rimworld\Mods',
  "$env:USERPROFILE\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Mods"
)

$results = @()
foreach ($root in $roots) {
  if (-not (Test-Path $root)) { continue }
  $hits = Get-ChildItem -Path $root -Recurse -Filter '0Harmony.dll' -ErrorAction SilentlyContinue
  foreach ($hit in $hits) {
    try {
      $name = [System.Reflection.AssemblyName]::GetAssemblyName($hit.FullName)
      $results += [PSCustomObject]@{
        AssemblyVersion = $name.Version.ToString()
        Path            = $hit.FullName
      }
    } catch {
      $results += [PSCustomObject]@{ AssemblyVersion = 'UNREADABLE'; Path = $hit.FullName }
    }
  }
}

Write-Output '=== installed 0Harmony.dll ==='
if ($results.Count -eq 0) {
  Write-Output 'none found under the searched roots'
} else {
  $results | Sort-Object AssemblyVersion | Format-List | Out-String | Write-Output
}

Write-Output '=== RimBridgeServer assemblies and what they reference ==='
$bridges = @()
foreach ($root in $roots) {
  if (-not (Test-Path $root)) { continue }
  $bridges += Get-ChildItem -Path $root -Recurse -Filter 'RimBridgeServer*.dll' -ErrorAction SilentlyContinue
}
if ($bridges.Count -eq 0) {
  Write-Output 'no RimBridgeServer assembly found under the searched roots'
}
foreach ($bridge in $bridges) {
  Write-Output ('--- ' + $bridge.FullName)
  try {
    $asm = [System.Reflection.Assembly]::ReflectionOnlyLoadFrom($bridge.FullName)
    foreach ($ref in $asm.GetReferencedAssemblies()) {
      if ($ref.Name -like '*Harmony*') {
        Write-Output ('    references ' + $ref.Name + ' ' + $ref.Version.ToString())
      }
    }
  } catch {
    Write-Output ('    could not reflect: ' + $_.Exception.Message)
  }
}
