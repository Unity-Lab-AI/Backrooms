# Unity's voice -- the local multi-pass re-train (prosody -> GTA export -> vocoder polish -> A/B), one command.
#   powershell -ExecutionPolicy Bypass -File training\voice\local_multipass.ps1 -Check    (verify only, trains nothing)
#   powershell -ExecutionPolicy Bypass -File training\voice\local_multipass.ps1           (the real run -- owner's "start" only)
#   powershell -ExecutionPolicy Bypass -File training\voice\local_multipass.ps1 -From vocoder
# Resumable: run it again after a stop. Never writes into models\unity-voice\. Close the game, Ollama and the face
# service first (the check refuses with less than 8 GB of GPU memory free).
param(
    [switch]$Check,
    [string]$From = "prosody",
    [int]$Steps = 30000,
    [int]$VocoderSteps = 20000,
    [string]$Out = "D:\voice-lab\local-retrain-2026-10-13"
)
$ErrorActionPreference = "Stop"
$Repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$Run = Join-Path $env:TEMP "unity-voice-retrain"
New-Item -ItemType Directory -Force $Run | Out-Null
Set-Location $Run
$env:PYTHONIOENCODING = "utf-8"
$pyArgs = @((Join-Path $Repo "training\voice\local_multipass.py"), "--out", $Out, "--steps", $Steps, "--vocoder-steps", $VocoderSteps, "--from", $From)
if ($Check) { $pyArgs += "--check" }
python @pyArgs
if ($LASTEXITCODE) { throw "multipass exited with $LASTEXITCODE" }
