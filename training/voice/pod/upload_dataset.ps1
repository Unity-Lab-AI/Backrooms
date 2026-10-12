<#
Print a transfer command for a previously authorized existing direct-SSH pod.
No command is executed. No key/API secret is printed or provider queried.
Runpod's basic SSH proxy does not support SCP; use the separately observed public
TCP SSH host/port. Review the host key through an independently checked channel.
#>
param(
    [Parameter(Mandatory=$true)][string]$PacketDirectory,
    [Parameter(Mandatory=$true)][string]$SshHost,
    [Parameter(Mandatory=$true)][ValidateRange(1,65535)][int]$SshPort
)
$ErrorActionPreference = 'Stop'
if ($SshHost -notmatch '^[A-Za-z0-9][A-Za-z0-9.-]{0,252}$') {
    throw 'Use the actual observed public SSH DNS name or IPv4 address; no proxy or shell text.'
}
$packetRoot = (Resolve-Path -LiteralPath $PacketDirectory).Path
$packetPath = Join-Path $packetRoot 'packet.json'
$packet = Get-Content -LiteralPath $packetPath -Raw | ConvertFrom-Json
$archive = Join-Path $packetRoot 'delivery.tar'
$actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $archive).Hash.ToLowerInvariant()
if ($packet.schema -ne 'unity-voice-delivery-v1' -or $packet.archive_sha256 -cne $actual) {
    throw 'Delivery packet/archive hash differs.'
}
if ($archive.Contains("'")) { throw 'Packet path contains a quote; choose a simple packet path.' }
Write-Output 'PREVIEW ONLY. This script does not connect, transfer, rent, start or train.'
Write-Output "Verified local archive SHA256: $actual"
Write-Output "scp -o StrictHostKeyChecking=yes -P $SshPort '$archive' 'root@$($SshHost):/workspace/incoming/'"
Write-Output 'Create /workspace/incoming and verify provider volume identity on the separately authorized existing pod first.'
Write-Output 'Use accept_delivery.py after transfer; never tar-extract an unchecked archive or launch training as an upload side effect.'
