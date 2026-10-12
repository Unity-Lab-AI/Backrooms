<#
Upload the voice delivery packet to an EXISTING RunPod network volume over RunPod's S3-compatible API.
No pod runs during this, so no GPU time is spent on the transfer. It does not create a volume, a pod or a
key, and it starts nothing: the pod is created separately, after the owner's go, with start_template.sh as
its start command.

  powershell -File training/voice/pod/upload_volume_s3.ps1 -PacketDirectory <dir with delivery.tar + packet.json> `
      -VolumeId <network volume id> -DataCenter US-MO-1 [-DryRun]

Needs: AWS CLI v2 (aws.exe), and RunPod S3 credentials in the environment or ~/.aws/credentials:
  AWS_ACCESS_KEY_ID     = the RunPod user id (user_...)   -- console: Settings > S3 API Keys
  AWS_SECRET_ACCESS_KEY = an S3 API key (rps_...)         -- created there, shown once
These are NOT the RunPod API key and cannot be created through the API; the owner makes them in the console.

Lands on the volume as /workspace/incoming/delivery.tar, packet.json and start_template.sh.
After the copy it reads back each object's size and compares it with the local file.
#>
param(
    [Parameter(Mandatory=$true)][string]$PacketDirectory,
    [Parameter(Mandatory=$true)][ValidatePattern('^[a-z0-9]+$')][string]$VolumeId,
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Z]{2,3}-[A-Z]{2}-[0-9]+$')][string]$DataCenter,
    [switch]$DryRun
)
$ErrorActionPreference = 'Stop'
$aws = (Get-Command aws -ErrorAction SilentlyContinue).Source
if (-not $aws) { $aws = 'C:\Program Files\Amazon\AWSCLIV2\aws.exe' }
if (-not (Test-Path $aws)) { throw 'AWS CLI v2 not found (winget install Amazon.AWSCLI).' }

$packetRoot = (Resolve-Path -LiteralPath $PacketDirectory).Path
$packet = Get-Content -LiteralPath (Join-Path $packetRoot 'packet.json') -Raw | ConvertFrom-Json
$archive = Join-Path $packetRoot 'delivery.tar'
$actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $archive).Hash.ToLowerInvariant()
if ($packet.schema -ne 'unity-voice-delivery-v1' -or $packet.archive_sha256 -cne $actual) {
    throw "Delivery packet/archive hash differs ($actual). Nothing uploaded."
}
$starter = Join-Path $PSScriptRoot 'start_template.sh'
$endpoint = 'https://s3api-' + $DataCenter.ToLowerInvariant() + '.runpod.io/'
$common = @('--region', $DataCenter, '--endpoint-url', $endpoint)
$env:AWS_RETRY_MODE = 'standard'; $env:AWS_MAX_ATTEMPTS = '10'

$items = @(
    @{ Local = $archive; Key = 'incoming/delivery.tar' },
    @{ Local = (Join-Path $packetRoot 'packet.json'); Key = 'incoming/packet.json' },
    @{ Local = $starter; Key = 'incoming/start_template.sh' }
)
Write-Output "delivery.tar sha256 $actual  ->  s3://$VolumeId/incoming/  ($DataCenter)"
foreach ($i in $items) {
    $size = (Get-Item -LiteralPath $i.Local).Length
    Write-Output ("  {0}  ({1:N0} bytes)" -f $i.Key, $size)
    if ($DryRun) { continue }
    & $aws s3 cp $i.Local ("s3://$VolumeId/" + $i.Key) @common --cli-read-timeout 7200 --only-show-errors
    if ($LASTEXITCODE -ne 0) { throw "Upload failed for $($i.Key) (exit $LASTEXITCODE)." }
    $listed = & $aws s3api head-object --bucket $VolumeId --key $i.Key @common --query ContentLength --output text
    if ([int64]$listed -ne $size) { throw "Read-back size for $($i.Key) is $listed, local is $size." }
    Write-Output "    read back: $listed bytes OK"
}
if ($DryRun) { Write-Output 'DRY RUN: nothing was uploaded.' }
else {
    Write-Output ''
    Write-Output 'Uploaded and read back. Pod env for start_template.sh:'
    Write-Output "  VOICE_DELIVERY_SHA256=$actual"
    Write-Output "  VOICE_DATASET_ID=$($packet.dataset_id)"
    Write-Output "  VOICE_VOLUME_ID=$VolumeId"
}
