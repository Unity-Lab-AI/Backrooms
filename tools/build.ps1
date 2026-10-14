param(
    [string] $RimWorldPath,
    [ValidateSet('Release', 'Debug')] [string] $Configuration = 'Release',
    [switch] $NoRestore
)
. (Join-Path $PSScriptRoot 'BuildCommon.ps1')
$repoRoot = Get-RimroomsRoot
if (-not $RimWorldPath) {
    if ($env:RIMWORLD_PATH) { $RimWorldPath = $env:RIMWORLD_PATH }
    else { $RimWorldPath = (Get-RimSortInstancePaths).GamePath }
}
$RimWorldPath = [IO.Path]::GetFullPath($RimWorldPath)
$managed = Join-Path $RimWorldPath 'RimWorldWin64_Data/Managed'
# RimWorld 1.7 (the Waylith engine) keeps no RimWorldWin64_Data/Managed: the reviewed reference assemblies live in the
# krafs reference set instead. RIMWORLD_MANAGED_PATH names that folder; the 1.6 core-assembly hash check is then skipped
# (2026-10-14: the run-5 DLL was built by hand and the stager copied the stale package because this script refused 1.7).
if ($env:RIMWORLD_MANAGED_PATH -and (Test-Path -LiteralPath (Join-Path $env:RIMWORLD_MANAGED_PATH 'Assembly-CSharp.dll') -PathType Leaf)) {
    $managed = [IO.Path]::GetFullPath($env:RIMWORLD_MANAGED_PATH)
    Write-Warning "Building against the reference assemblies at $managed (RIMWORLD_MANAGED_PATH); the 1.6 core hash check is skipped."
} else {
    $coreAssembly = Join-Path $managed 'Assembly-CSharp.dll'
    if (-not (Test-Path -LiteralPath $coreAssembly -PathType Leaf)) { throw 'Installed RimWorld managed assembly is missing (on 1.7 set RIMWORLD_MANAGED_PATH to the reference set).' }
    $expectedCoreHash = '5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A'
    if ((Get-FileHash -LiteralPath $coreAssembly -Algorithm SHA256).Hash -ne $expectedCoreHash) {
        throw 'Core assembly changed from the reviewed target. Review and record the new source/API target before rebuilding.'
    }
}
$project = Join-Path $repoRoot 'src/RimroomsAsyncIndustries/RimroomsAsyncIndustries.csproj'
[xml] $projectXml = [IO.File]::ReadAllText($project)
$package = Join-Path $repoRoot 'Mod/Rimrooms - Async Industries'
[xml] $about = [IO.File]::ReadAllText((Join-Path $package 'About/About.xml'))
if ($projectXml.Project.PropertyGroup.Version -ne $about.ModMetaData.modVersion) { throw 'Project and About.xml versions differ.' }
$env:DOTNET_CLI_HOME = Join-Path $repoRoot '.local/dotnet'
$env:NUGET_PACKAGES = Join-Path $repoRoot '.local/nuget'
$env:DOTNET_CLI_TELEMETRY_OPTOUT = '1'
$env:DOTNET_GENERATE_ASPNET_CERTIFICATE = 'false'
$env:DOTNET_ADD_GLOBAL_TOOLS_TO_PATH = 'false'
$solution = Join-Path $repoRoot 'src/RimroomsAsyncIndustries.sln'
Push-Location $repoRoot
try {
    if (-not $NoRestore) {
        & dotnet restore $solution --locked-mode "-p:RimWorldPath=$RimWorldPath" --verbosity minimal
        if ($LASTEXITCODE -ne 0) { throw 'Package restore failed. No new DLL was staged.' }
    }
    & dotnet build $solution --configuration $Configuration --no-restore "-p:RimWorldPath=$RimWorldPath" "-p:RimWorldManagedPath=$managed" --verbosity minimal
    if ($LASTEXITCODE -ne 0) { throw 'Compilation failed. The previous packaged DLL has not been replaced.' }
    $builtDll = Join-Path $repoRoot "src/RimroomsAsyncIndustries/bin/$Configuration/net472/RimroomsAsyncIndustries.dll"
    $assemblyDirectory = Join-Path $package '1.7/Assemblies'
    $null = New-Item -ItemType Directory -Path $assemblyDirectory -Force
    Copy-Item -LiteralPath $builtDll -Destination (Join-Path $assemblyDirectory 'RimroomsAsyncIndustries.dll') -Force
    Copy-Item -LiteralPath (Join-Path $repoRoot 'LICENSE') -Destination (Join-Path $package 'About/License.txt') -Force
    $manifest = Get-RimroomsPackageManifest $package
    $evidenceDirectory = Join-Path $repoRoot 'artifacts/build'
    $null = New-Item -ItemType Directory -Path $evidenceDirectory -Force
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $evidenceDirectory 'package-manifest.json') -Encoding UTF8
    $references = foreach ($name in @('Assembly-CSharp.dll', 'UnityEngine.CoreModule.dll', 'UnityEngine.IMGUIModule.dll', 'UnityEngine.TextRenderingModule.dll', 'mscorlib.dll')) {
        $path = Join-Path $managed $name
        [ordered]@{ Name = $name; AssemblyVersion = [Reflection.AssemblyName]::GetAssemblyName($path).Version.ToString(); SHA256 = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash }
    }
    [ordered]@{ SDK = (& dotnet --version); Configuration = $Configuration; TargetFramework = 'net472'; References = @($references); GameplayVerified = $false } |
        ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $evidenceDirectory 'reference-manifest.json') -Encoding UTF8
    Write-Output "Built $($manifest.PackageId) $($manifest.Version): $package"
    Write-Output "Package contains $($manifest.Files.Count) approved files. No game was launched."
} finally { Pop-Location }
