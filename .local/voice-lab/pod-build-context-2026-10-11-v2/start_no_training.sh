#!/usr/bin/env bash
# Future authorized container startup only. No training/cloud mutation here.
set -euo pipefail
key="$AUTHORIZED_PUBLIC_KEY"
[[ "$key" != *$'\n'* && "$key" =~ ^(ssh-ed25519|ssh-rsa|ecdsa-sha2-nistp(256|384|521))\ [A-Za-z0-9+/=]+(\ .*)?$ ]] || {
  echo "REFUSED: provide one actual owner public SSH key; no password login or training" >&2
  exit 2
}
install -d -m 700 /root/.ssh
printf '%s\n' "$key" > /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys
install -d -m 755 /run/sshd
ssh-keygen -A
exec /usr/sbin/sshd -D -e
