# Authorized local Docker preparation

Owner authorization: **"Yes — local Docker build only"**. This does not authorize
student training, a pod rental, a registry push, or changing the live voice.

## Startup recovery observed

Docker Desktop 4.42.0 failed while binding its inference-manager endpoint:

```text
remove C:\Users\gfour\AppData\Local\Docker\run\dockerInference:
The file cannot be accessed by the system.
```

The same error was present in local Docker logs. The endpoint dated from
2026-08-28; the containing `run` directory was ordinary, not a reparse point.
Docker processes were stopped and WSL reported no running distributions before
recovery. Checked absolute paths were confined to the explicitly named Docker
application-data directory. Only the transient socket directory was renamed:

```text
C:\Users\gfour\AppData\Local\Docker\run
    -> C:\Users\gfour\AppData\Local\Docker\run.quarantined-20261011-A2-prep
```

The backup remains available. No recursive deletion, factory reset, prune,
image/volume removal, diagnostics upload, or VHDX change was performed. Docker
was restarted through `docker desktop start --detach --timeout 30`; subsequent
`docker info` returned a functioning Linux engine, version **28.2.2**. The
existing container listing was empty. This records the observed recovery, not
a claim about NTFS corruption or a universal fix for Docker failures.

Related primary troubleshooting records:
[Docker troubleshooting](https://docs.docker.com/desktop/troubleshoot-and-support/troubleshoot/)
and [the reported endpoint failure](https://github.com/docker/desktop-feedback/issues/625).

## First image build: preserved failure

Context: `.local/voice-lab/pod-build-context-2026-10-11-v1/`.
Intended local tag: `unity-a2-prep:20261011-v1`.
Artifacts: `.local/voice-lab/pod-build-artifacts-2026-10-11-v1/`.

The build successfully pulled the pinned Python base, verified frozen Debian
Release metadata and installed the pinned Python artifacts. It then exited 1
at the actual installation-consistency check:

```text
smart-open 7.1.0 requires wrapt, which is not installed.
```

This build was not accepted or loaded as the completed environment. Package
metadata investigation identified that PyPI's version summary listed no
requirements for this wheel, whereas the selected wheel's own METADATA requires
`wrapt`. The resolver is being corrected to use selected-artifact metadata and
inspect the remaining packages for the same problem. The v1 context is preserved;
the corrected build must use a new context/version.

The build started no model/container training, rented no pod and published no
registry image. Local dependency installation inside the build is preparation;
it is separate from functional GPU, inference, student-learning or recovery
acceptance. Final build/inventory results will be recorded separately.

## Corrected image: observed local success

Fresh context: `.local/voice-lab/pod-build-context-2026-10-11-v2/`.
Local tag: `unity-a2-prep:20261011-v2`.
Build exit code: **0**. The actual dependency check printed **"No broken
requirements found."** The build exporter verified all selected version pins.

The selected-artifact lock has **103 packages**, including `wrapt==1.17.2`.
Its SHA256 is
`5081be03f5025ce38e4c2f0162f5337c9f85162101335741f74d140702478f9d`.
Across the reviewed package summaries only smart-open differed from its selected
artifact requirements. No dependency check was bypassed.

Actual Linux/amd64 image identity returned by this Docker engine, also matching
the build's OCI index digest:

```text
sha256:3786ba627ace02b521b97f5aa9ef0f647fcad2133e73b1d69c7d0ced0e9ffd3f
```

Image size: **3,429,124,586 bytes**. Python: **3.10.18**. A stopped inspection
container was created with `/bin/false` as its entrypoint; its state was
`created`, and it was never started. `docker cp` retrieved the build-produced
inventories. Independent metadata reconciliation found **103 observed packages,
103 expected**, no extra/missing/version differences. The four asset roles bind
**887 actual inventoried files**: English 28, espeak library/bundled files 369,
Debian espeak data 489, and libsndfile 1. The OS inventory contains 188 packages.

Permanent inventory copies and the actual local build receipt are under:

```text
training/voice/receipts/local-environment-build.json
training/voice/receipts/environment-2026-10-11-v2/
```

The saved Docker archive is:

```text
.local/voice-lab/pod-build-artifacts-2026-10-11-v2/unity-a2-environment.docker.tar
3,429,147,136 bytes
SHA256 bb7630a5dfdcd9b7354921161baf32d22de66a3ca47a871412410f41c47f7faa
```

The complete package inventory SHA256 is
`bdf2d5bb1ac1e09f0b3a69668e7bb54f343313ca1613890c617fad848fa6f3e4`;
runtime asset inventory SHA256 is
`c25d8adfd29d25e1501c41f8bbfd04861bde01ebedf739d92bdfe0d3397db9d3`.
The raw asset hashes were collected by the actual build exporter, not by a later
G2P, CUDA, model or ABI execution test.

These are **local build/installation/inventory observations**. No registry image
was published, and no pullable registry reference is claimed. `image_digest`
remains null until separately authorized publication supplies a real reference.
No student model was imported/trained/evaluated, no pod was rented, and no live
voice/service was changed. H100/driver, provider storage/credentials/stop/billing,
student recovery and final voice quality remain future observations.
