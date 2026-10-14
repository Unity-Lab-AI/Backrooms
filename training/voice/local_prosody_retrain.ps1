# One-command local prosody fine-tune of Unity's voice on this PC's GPU.
#   powershell -ExecutionPolicy Bypass -File training\voice\local_prosody_retrain.ps1            (real run, ~30k steps)
#   powershell -ExecutionPolicy Bypass -File training\voice\local_prosody_retrain.ps1 -Smoke 300 (speed/VRAM check only)
# Resumable: run the same command again after a stop and it continues from work\acoustic-work.pt.
# Never writes into models\unity-voice\. Python runs from a %TEMP% folder (the repo's .local\qa shadows 'inspect').
param(
    [int]$Steps = 30000,
    [int]$Frames = 24000,
    [int]$Smoke = 0,
    [string]$Out = "D:\voice-lab\local-retrain-2026-10-13",
    [string]$Dataset = "D:\voice-lab\pod-results\voice-2026-10-12\gen\dataset"
)
$ErrorActionPreference = "Stop"
$Repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$Voice = Join-Path $Repo "training\voice"
$Feats = Join-Path $Out "feats"
$Run = Join-Path $env:TEMP "unity-voice-retrain"
New-Item -ItemType Directory -Force $Run, $Out | Out-Null
Set-Location $Run
$env:PYTHONIOENCODING = "utf-8"

if (-not (Test-Path (Join-Path $Feats "features-manifest.json"))) {
    Write-Host "Preparing features from $Dataset (CPU, ~40 min, one time)..."
    python (Join-Path $Voice "prep.py") $Dataset $Feats
    if ($LASTEXITCODE) { throw "feature prep failed" }
}
$pyArgs = @((Join-Path $Voice "local_prosody_retrain.py"), "--feats", $Feats, "--out", $Out, "--steps", $Steps, "--frames", $Frames)
if ($Smoke -gt 0) { $pyArgs += @("--smoke", $Smoke) }
python @pyArgs
if ($LASTEXITCODE) { throw "training exited with $LASTEXITCODE" }
