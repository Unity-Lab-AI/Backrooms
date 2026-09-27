param(
    [Parameter(Mandatory = $true)]
    [string] $InventoryPath,

    [Parameter(Mandatory = $true)]
    [string] $WorkshopRoot,

    [Parameter(Mandatory = $true)]
    [string] $GameDataRoot,

    [Parameter(Mandatory = $true)]
    [string] $OutputPath

    ,

    [Parameter(Mandatory = $true)]
    [string] $EdgesOutputPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-NodeText {
    param(
        [xml] $Document,
        [string] $XPath
    )

    $node = $Document.SelectSingleNode($XPath)
    if ($null -eq $node) {
        return ''
    }
    return $node.InnerText.Trim()
}

function Get-NodeListText {
    param(
        [xml] $Document,
        [string] $XPath
    )

    $values = @(
        $Document.SelectNodes($XPath) |
            ForEach-Object { $_.InnerText.Trim() } |
            Where-Object { $_ -ne '' } |
            Select-Object -Unique
    )
    return ($values -join '; ')
}

$resolvedInventory = (Resolve-Path -LiteralPath $InventoryPath).Path
$rows = @(Import-Csv -LiteralPath $resolvedInventory)
if ($rows.Count -ne 294) {
    throw "Expected 294 profile rows but found $($rows.Count). Refusing to write a partial snapshot."
}

$seenOrders = @{}
$seenIds = @{}
$output = foreach ($row in $rows) {
    if ($seenOrders.ContainsKey($row.LoadOrder)) {
        throw "Duplicate load-order value: $($row.LoadOrder)"
    }
    $seenOrders[$row.LoadOrder] = $true

    $sourceKind = ''
    $modRoot = ''
    $aboutRelativePath = ''
    $loadFoldersPath = ''
    if ($row.ModID -match '^\d+$') {
        $sourceKind = 'Installed Steam Workshop copy'
        $modRoot = Join-Path $WorkshopRoot $row.ModID
        $aboutRelativePath = "workshop/294100/$($row.ModID)/About/About.xml"
        $loadFoldersPath = Join-Path $modRoot 'LoadFolders.xml'
    }
    else {
        $sourceKind = 'Installed RimWorld base game or DLC'
        $modRoot = Join-Path $GameDataRoot $row.ModID
        $aboutRelativePath = "game/Data/$($row.ModID)/About/About.xml"
        $loadFoldersPath = Join-Path $modRoot 'LoadFolders.xml'
    }

    $aboutPath = Join-Path $modRoot 'About\About.xml'
    $metadataStatus = ''
    $metadataName = ''
    $packageId = ''
    $modVersion = ''
    $supportedVersions = ''
    $dependencies = ''
    $loadAfter = ''
    $loadBefore = ''
    $incompatibleWith = ''
    $aboutSha256 = ''
    $loadFolderVersions = ''
    $loadFolderConditionTypes = ''
    $loadFolderPathCount = 0
    $missingLoadFolderPaths = ''
    $loadFoldersStatus = 'No LoadFolders.xml; default version-folder discovery applies'

    if (Test-Path -LiteralPath $aboutPath -PathType Leaf) {
        try {
            [xml] $about = Get-Content -LiteralPath $aboutPath -Raw
            $metadataName = Get-NodeText -Document $about -XPath '/ModMetaData/name'
            $packageId = Get-NodeText -Document $about -XPath '/ModMetaData/packageId'
            $modVersion = Get-NodeText -Document $about -XPath '/ModMetaData/modVersion'
            $supportedVersions = Get-NodeListText -Document $about -XPath '/ModMetaData/supportedVersions/li'
            $dependencies = Get-NodeListText -Document $about -XPath '/ModMetaData/modDependencies/li/packageId'
            $loadAfter = Get-NodeListText -Document $about -XPath '/ModMetaData/loadAfter/li'
            $loadBefore = Get-NodeListText -Document $about -XPath '/ModMetaData/loadBefore/li'
            $incompatibleWith = Get-NodeListText -Document $about -XPath '/ModMetaData/incompatibleWith/li'
            $aboutSha256 = (Get-FileHash -LiteralPath $aboutPath -Algorithm SHA256).Hash
            $metadataStatus = 'About.xml parsed'
        }
        catch {
            $metadataStatus = "About.xml parse error: $($_.Exception.Message)"
        }
    }
    else {
        $metadataStatus = 'About.xml missing from installed source'
    }

    if ($packageId -ne '') {
        if ($seenIds.ContainsKey($packageId)) {
            $seenIds[$packageId] = @($seenIds[$packageId]) + $row.LoadOrder
        }
        else {
            $seenIds[$packageId] = @($row.LoadOrder)
        }
    }

    if (Test-Path -LiteralPath $loadFoldersPath -PathType Leaf) {
        try {
            [xml] $loadFolders = Get-Content -LiteralPath $loadFoldersPath -Raw
            $loadFolderVersionNodes = @(
                $loadFolders.DocumentElement.ChildNodes |
                    Where-Object { $_.NodeType -eq [System.Xml.XmlNodeType]::Element } |
                    ForEach-Object { $_.Name }
            )
            $loadFolderVersions = $loadFolderVersionNodes -join '; '
            $conditionTypes = @(
                $loadFolders.SelectNodes('//li') |
                    ForEach-Object { $_.Attributes | ForEach-Object { $_.Name } } |
                    Where-Object { $_ -like 'IfMod*' } |
                    Select-Object -Unique
            )
            $loadFolderConditionTypes = $conditionTypes -join '; '

            $folderPaths = @(
                $loadFolders.SelectNodes('//li') |
                    ForEach-Object { $_.InnerText.Trim() } |
                    Where-Object { $_ -ne '' -and $_ -ne '/' } |
                    Select-Object -Unique
            )
            $loadFolderPathCount = $folderPaths.Count
            $missingPaths = @(
                $folderPaths |
                    Where-Object {
                        $relative = $_ -replace '/', [System.IO.Path]::DirectorySeparatorChar
                        -not (Test-Path -LiteralPath (Join-Path $modRoot $relative))
                    }
            )
            if ($missingPaths.Count -gt 0) {
                $missingLoadFolderPaths = $missingPaths -join '; '
                $loadFoldersStatus = 'Parsed; one or more listed folders are absent locally'
            }
            else {
                $loadFoldersStatus = 'Parsed; all listed folders exist locally'
            }
        }
        catch {
            $loadFoldersStatus = "LoadFolders.xml parse error: $($_.Exception.Message)"
        }
    }

    [pscustomobject]@{
        LoadOrder = $row.LoadOrder
        InventoryName = $row.ModName
        InventoryID = $row.ModID
        InventoryType = $row.Type
        WorkshopURL = $row.WorkshopURL
        SourceKind = $sourceKind
        MetadataName = $metadataName
        PackageID = $packageId
        LocalModVersion = $modVersion
        SupportedVersions = $supportedVersions
        HardDependencies = $dependencies
        LoadAfter = $loadAfter
        LoadBefore = $loadBefore
        IncompatibleWith = $incompatibleWith
        MetadataRelativePath = $aboutRelativePath
        AboutXmlSHA256 = $aboutSha256
        MetadataStatus = $metadataStatus
        LoadFolderVersions = $loadFolderVersions
        LoadFolderConditionTypes = $loadFolderConditionTypes
        LoadFolderPathCount = $loadFolderPathCount
        MissingLoadFolderPaths = $missingLoadFolderPaths
        LoadFoldersStatus = $loadFoldersStatus
    }
}

$duplicatePackageIds = @(
    $seenIds.GetEnumerator() |
        Where-Object { @($_.Value).Count -gt 1 } |
        ForEach-Object { $_.Key }
)
if ($duplicatePackageIds.Count -gt 0) {
    Write-Warning "Duplicate installed package IDs: $($duplicatePackageIds -join ', ')"
}

$outputDirectory = Split-Path -Parent $OutputPath
if ($outputDirectory -and -not (Test-Path -LiteralPath $outputDirectory)) {
    New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null
}
$output | Export-Csv -LiteralPath $OutputPath -NoTypeInformation -Encoding UTF8

$profileByPackageId = @{}
foreach ($record in $output) {
    if ($record.PackageID -ne '') {
        $profileByPackageId[$record.PackageID] = $record
    }
}

$edges = foreach ($record in $output) {
    foreach ($relation in @(
        @{ Name = 'Requires'; Values = $record.HardDependencies },
        @{ Name = 'LoadAfter'; Values = $record.LoadAfter },
        @{ Name = 'LoadBefore'; Values = $record.LoadBefore },
        @{ Name = 'IncompatibleWith'; Values = $record.IncompatibleWith }
    )) {
        foreach ($targetPackageId in ($relation.Values -split ';\s*' | Where-Object { $_ -ne '' })) {
            $target = $profileByPackageId[$targetPackageId]
            [pscustomobject]@{
                FromLoadOrder = $record.LoadOrder
                FromName = $record.InventoryName
                FromPackageID = $record.PackageID
                Relationship = $relation.Name
                ToLoadOrder = if ($null -ne $target) { $target.LoadOrder } else { '' }
                ToName = if ($null -ne $target) { $target.InventoryName } else { '' }
                ToPackageID = $targetPackageId
                TargetInProfile = ($null -ne $target)
                EvidenceRelativePath = $record.MetadataRelativePath
                EvidenceAboutXmlSHA256 = $record.AboutXmlSHA256
            }
        }
    }
}

$edgeOutputDirectory = Split-Path -Parent $EdgesOutputPath
if ($edgeOutputDirectory -and -not (Test-Path -LiteralPath $edgeOutputDirectory)) {
    New-Item -ItemType Directory -Path $edgeOutputDirectory -Force | Out-Null
}
$edges | Export-Csv -LiteralPath $EdgesOutputPath -NoTypeInformation -Encoding UTF8

$parsed = @($output | Where-Object { $_.MetadataStatus -eq 'About.xml parsed' }).Count
$workshopParsed = @($output | Where-Object { $_.SourceKind -eq 'Installed Steam Workshop copy' -and $_.MetadataStatus -eq 'About.xml parsed' }).Count
$loadFolderFiles = @($output | Where-Object { $_.LoadFolderVersions -ne '' }).Count
$missingFolders = @($output | Where-Object { $_.MissingLoadFolderPaths -ne '' }).Count
$requiresEdges = @($edges | Where-Object { $_.Relationship -eq 'Requires' }).Count
$incompatibleEdges = @($edges | Where-Object { $_.Relationship -eq 'IncompatibleWith' }).Count
$activeDeclaredIncompatibilities = @($edges | Where-Object { $_.Relationship -eq 'IncompatibleWith' -and $_.TargetInProfile }).Count
Write-Output "Rows=$($output.Count); parsed About.xml=$parsed; parsed Workshop About.xml=$workshopParsed; entries with LoadFolders.xml=$loadFolderFiles; entries with missing listed folders=$missingFolders; duplicate package IDs=$($duplicatePackageIds.Count); Requires edges=$requiresEdges; IncompatibleWith edges=$incompatibleEdges; active declared incompatibilities=$activeDeclaredIncompatibilities; metadata=$OutputPath; relationships=$EdgesOutputPath"
