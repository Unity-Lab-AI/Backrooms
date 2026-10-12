<#
Bring everything a BRAIN pod run made home to the owner's USB drive over RunPod's S3 API (no pod needs to run).
Owner: "make sure it sends home the data information and anxulliray details and info we need to monitor and do checks".
Copies from the brain pod's network volume:
  gguf/      unity-brain.gguf + .sha256, quant.txt, brain-eval.json, status/cost/state/log mirrors, versions.txt
  out/       LoRA adapter, both quants, eval outputs, calibration text
  state/     stage markers, inputs digest, first-start clock
  run.log    the whole run log
to D:\voice-lab\pod-results\<RunName>\ and verifies every file's size. Skipped (reinstallable or rebuilt): llama.cpp/,
the HF cache, ckpt/ (training checkpoints; pass -WithCheckpoints to include them). Delete the volume only after VERIFIED.

  powershell -File training/pod/pull_brain_s3.ps1 -VolumeId <id> -DataCenter US-MO-1 -RunName brain-<date>
#>
param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[a-z0-9]+$')][string]$VolumeId,
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Z]{2,3}-[A-Z]{2}-[0-9]+$')][string]$DataCenter,
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9._-]+$')][string]$RunName,
    [string]$Destination = 'D:\voice-lab\pod-results',
    [switch]$WithCheckpoints
)
$ErrorActionPreference = 'Stop'
$aws = (Get-Command aws -ErrorAction SilentlyContinue).Source
if (-not $aws) { $aws = 'C:\Program Files\Amazon\AWSCLIV2\aws.exe' }
$common = @('--region', $DataCenter, '--endpoint-url', ('https://s3api-' + $DataCenter.ToLowerInvariant() + '.runpod.io/'))
$env:AWS_RETRY_MODE = 'standard'; $env:AWS_MAX_ATTEMPTS = '10'
$root = Join-Path $Destination $RunName
New-Item -ItemType Directory -Force -Path $root | Out-Null
$prefixes = @('gguf/', 'out/', 'state/') + $(if ($WithCheckpoints) { @('ckpt/') } else { @() })
foreach ($p in $prefixes) {
    Write-Output "sync s3://$VolumeId/$p"
    & $aws s3 sync ("s3://$VolumeId/" + $p) (Join-Path $root $p) @common --only-show-errors
    if ($LASTEXITCODE -ne 0) { throw "sync failed for $p" }
}
& $aws s3 cp "s3://$VolumeId/run.log" (Join-Path $root 'run.log') @common --only-show-errors 2>$null
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
Write-Output ("VERIFIED: {0} files, {1:N2} GB in {2}. Copy unity-brain.gguf + .sha256 + brain-eval.json + quant.txt into training\models\ to apply." -f $count, ($bytes / 1GB), $root)
