<#
Bring EVERYTHING a voice pod run made home to the owner's USB drive, over RunPod's S3 API (no pod needs to run).
Owner, 2026-10-12: "why would i make them if they are only therei while its rented" -- the generated clips are an
asset, not scratch. Owner, same day: "make sure it sends home the data information and anxulliray details and info we need to monitor
and do checks". This copies EVERYTHING the run produced, from the network volume:
  gen/          every generated clip (kept AND screened-out), each shard's recipe, runtime receipt, completion
                receipt and metadata, per-shard screening + summaries, the merged set, the kept dataset with
                screen-report.json, the script shards, stage markers and every generation log
  out/          trained models, samples, progress samples, status, cost clock, gpu.txt, pip freeze, all mirrored logs
  state/        stage markers, budget record, volume receipt, stop attempts
  voice-runs/   each training run's run-config.json and stage markers (features and checkpoints excluded; the
                published models are already in out/)
  *.log         launch, bootstrap, voice, acoustic and vocoder logs
Skipped on purpose, all reinstallable: gen/venv-*, gen/cosyvoice-code, gen/asr-model, venv/, src-*/.
to D:\voice-lab\pod-results\<RunName>\ and then verifies every file's size against the volume listing.
Delete the volume only after this reports VERIFIED. It can also run WHILE the pod works, for a mid-run check from
home (S3 reads the volume live; repeated runs only fetch what is new).

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
$syncs = @(
    @{ Prefix = 'gen/';        Exclude = @('venv-qwen/*', 'venv-cosy/*', 'cosyvoice-code/*', 'asr-model/*') },
    @{ Prefix = 'out/';        Exclude = @() },
    @{ Prefix = 'state/';      Exclude = @() },
    @{ Prefix = 'voice-runs/'; Exclude = @('*/features/*', '*/ckpt/*', '*/oracle-gta/*', '*/predicted-heldout/*') }
)
foreach ($s in $syncs) {
    $ex = @(); foreach ($e in $s.Exclude) { $ex += @('--exclude', $e) }
    Write-Output "sync s3://$VolumeId/$($s.Prefix)"
    & $aws s3 sync ("s3://$VolumeId/" + $s.Prefix) (Join-Path $root $s.Prefix) @common @ex --only-show-errors
    if ($LASTEXITCODE -ne 0) { throw "sync failed for $($s.Prefix)" }
}
foreach ($f in @('launch.log', 'bootstrap.log', 'voice.log', 'acoustic.log', 'vocoder.log', 'runpod-start.log')) {
    & $aws s3 cp ("s3://$VolumeId/" + $f) (Join-Path $root $f) @common --only-show-errors 2>$null
}
# Verify: every object under the synced prefixes exists locally with the same size.
$bad = 0; $count = 0; $bytes = 0
$skip = '^(gen/(venv-qwen|venv-cosy|cosyvoice-code|asr-model)/|voice-runs/[^/]+/(features|ckpt|oracle-gta|predicted-heldout)/)'
foreach ($s in $syncs) {
    $listing = & $aws s3api list-objects-v2 --bucket $VolumeId --prefix $s.Prefix @common --query 'Contents[].[Key,Size]' --output text
    foreach ($line in ($listing -split "`n")) {
        if (-not $line.Trim() -or $line -eq 'None') { continue }
        $key, $size = $line -split "`t"
        if ($key -match $skip) { continue }
        $local = Join-Path $root ($key -replace '/', '\')
        $count++; $bytes += [int64]$size
        if (-not (Test-Path $local) -or (Get-Item $local).Length -ne [int64]$size) { $bad++; Write-Output "MISSING/SHORT: $key" }
    }
}
if ($bad) { throw "$bad of $count files did not verify; do NOT delete the volume" }
Write-Output ("VERIFIED: {0} files, {1:N2} GB in {2}. The volume may be deleted now." -f $count, ($bytes / 1GB), $root)
