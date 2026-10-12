<#
Bring EVERYTHING a voice pod run made home to the owner's USB drive, over RunPod's S3 API (no pod needs to run).
Owner, 2026-10-12: "why would i make them if they are only therei while its rented" -- the generated clips are an
asset, not scratch. This copies, from the network volume:
  gen/dataset/           every screened clip kept for training + metadata.jsonl + screen-report.json
  gen/screening-all.jsonl, gen/merged/metadata.jsonl, gen/logs/   what was generated, what was screened out, why
  out/                   trained models, samples, progress samples, logs, gpu.txt
to D:\voice-lab\pod-results\<RunName>\ and then verifies every file's size against the volume listing.
Delete the volume only after this reports VERIFIED.

  powershell -File training/voice/pod/pull_results_s3.ps1 -VolumeId <id> -DataCenter US-MO-1 -RunName <name>
#>
param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[a-z0-9]+$')][string]$VolumeId,
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Z]{2,3}-[A-Z]{2}-[0-9]+$')][string]$DataCenter,
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9._-]+$')][string]$RunName,
    [string]$Destination = 'D:\voice-lab\pod-results'
)
$ErrorActionPreference = 'Stop'
$aws = (Get-Command aws -ErrorAction SilentlyContinue).Source
if (-not $aws) { $aws = 'C:\Program Files\Amazon\AWSCLIV2\aws.exe' }
$endpoint = 'https://s3api-' + $DataCenter.ToLowerInvariant() + '.runpod.io/'
$common = @('--region', $DataCenter, '--endpoint-url', $endpoint)
$env:AWS_RETRY_MODE = 'standard'; $env:AWS_MAX_ATTEMPTS = '10'
$root = Join-Path $Destination $RunName
New-Item -ItemType Directory -Force -Path $root | Out-Null
$prefixes = @('gen/dataset/', 'gen/logs/', 'out/')
$files = @('gen/screening-all.jsonl', 'gen/merged/metadata.jsonl', 'launch.log', 'bootstrap.log', 'voice.log', 'acoustic.log', 'vocoder.log')
foreach ($p in $prefixes) {
    Write-Output "sync s3://$VolumeId/$p"
    & $aws s3 sync ("s3://$VolumeId/" + $p) (Join-Path $root $p) @common --only-show-errors
    if ($LASTEXITCODE -ne 0) { throw "sync failed for $p" }
}
foreach ($f in $files) {
    & $aws s3 cp ("s3://$VolumeId/" + $f) (Join-Path $root $f) @common --only-show-errors 2>$null
}
# Verify: every object under the synced prefixes exists locally with the same size.
$bad = 0; $count = 0; $bytes = 0
foreach ($p in $prefixes) {
    $listing = & $aws s3api list-objects-v2 --bucket $VolumeId --prefix $p @common --query 'Contents[].[Key,Size]' --output text
    foreach ($line in ($listing -split "`n")) {
        if (-not $line.Trim() -or $line -eq 'None') { continue }
        $key, $size = $line -split "`t"
        $local = Join-Path $root ($key -replace '/', '\')
        $count++; $bytes += [int64]$size
        if (-not (Test-Path $local) -or (Get-Item $local).Length -ne [int64]$size) { $bad++; Write-Output "MISSING/SHORT: $key" }
    }
}
if ($bad) { throw "$bad of $count files did not verify; do NOT delete the volume" }
Write-Output ("VERIFIED: {0} files, {1:N2} GB in {2}. The volume may be deleted now." -f $count, ($bytes / 1GB), $root)
