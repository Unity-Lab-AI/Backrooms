# A2 student: no-start pod preparation

This contract is preparation, not permission to rent or train. The accepted
32-clip dataset is separate from newly generated full-corpus recordings. Use the
final accepted dataset identity and literal listening receipt; never substitute
unreviewed full recordings because there are more of them.

## Implemented source

- ENVIRONMENT_SPEC.json: locally built Linux x86_64 / Python 3.10.18 / Torch and
  Torchaudio 2.7.1+cu126, Misaki 0.9.4 and recorded installed version inventories.
  Registry/H100/training/runtime acceptance remains separate.
- LAUNCH_CONFIG.template.json: locked; price, budget, retention, source/data/image,
  provider IDs and engineering receipts remain null.
- preflight_voice.py: local source/data hashes and optional environment metadata,
  complete distribution lock, assets and CLI checks. No provider API or training.
- prepare_launch.py: fresh local delivery archive with manifest source inputs,
  current gate/receipts, metadata and exact referenced WAVs only.
- upload_dataset.ps1: verifies local archive hash and PRINTS an SCP command.
  accept_delivery.py verifies/extracts into a fresh directory and validates the
  source/data identity before publishing it. Neither starts training.
- Bootstrap/runner: no live apt/pip install, moving branch clone or automatic HTTP
  server. They require an already prepared environment and explicit data.
- publish_voice.py: one complete atomic model pair under
  /workspace/out/models/<run-id>/. Exact completed sets are checked/reused;
  interrupted .publishing-* siblings remain. Thin models keep student_source,
  working-checkpoint and exact GTA provenance. No deployment is implied.
- Atomic directory publication uses Linux renameat2 NOREPLACE or Windows
  no-replace rename. Unsupported filesystems fail without deleting partial work.
- render_eval.py uses all 38 reserved independent listening texts, literal
  requested controls and bounded long-turn chunking. Unsupported requests are
  recorded as not_rendered. Each evaluation retains the exact loaded checkpoint
  snapshot, SHA, steps and shared student_source; quality remains unaccepted.

## Build the environment before paying

Published artifact availability was actually resolved from public metadata:
environment.lock.json contains 103 exact version/URL/SHA entries, official CUDA
Torch/Torchaudio wheel metadata and the official small English language wheel.
Numba 0.68.0 and llvmlite 0.50.0 publish compatible CP310 manylinux wheels and
require Python >=3.10. Two dependencies (docopt and pyworld) supply source archives;
their built wheel hashes are not invented. Actual Linux installation and dependency
checks completed in V2; native-library execution/phonemes/H100 remain unverified. The
[official PyTorch versions](https://pytorch.org/get-started/previous-versions/)
list the 2.7.1 CUDA 12.6 pair. Keep corresponding
[TorchAudio versions](https://docs.pytorch.org/audio/main/installation.html).
The [CUDA compatibility table](https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html)
gives the CUDA 12.x driver minimum; 525 is only a screening floor, not actual
image/GPU/driver acceptance.

1. Resolve every Linux dependency in a clean isolated image: direct candidates,
   transitive packages, exact versions and wheel/source hashes. Preserve the
   resolved installation lock as evidence. Never copy Windows wheels or the
   source-teacher environments.
2. Bake en_core_web_sm, espeak library/data and libsndfile into that image.
   Misaki must not download language assets during rented preprocessing.
   Qwen/Cosy teachers and the old Kokoro vector are not required on the pod.
3. Save package-lock.json as a normalized distribution-name to exact-version
   mapping covering ALL installed distributions, including build tooling.
4. Save runtime-assets.json as an absolute file-path to SHA256 mapping covering
   language model and library/data bytes. Bind nonempty inventoried path lists
   under roles english_model, espeak_library, espeak_data and libsndfile.
5. Save the actual registry image reference registry/name@sha256:<64 hex> in
   ENVIRONMENT_SPEC.json, regenerate the manifest and include it in the concrete
   source recipe approval. Preflight requires that exact reference, not any image
   with matching package names. A tag is not a digest; none is invented here.
6. Prepare the reviewed CLI. The
   [official v2.15.0 release](https://github.com/runpod/runpodctl/releases/tag/v2.15.0)
   publishes Linux-amd64 binary SHA256
   51c6f5a7e6f6c7cd4a52373f2262b9aeb0f16084e39595d25f71bc0cf5bc826b.
   Its [current stop command](https://docs.runpod.io/runpodctl/reference/runpodctl-pod)
   is runpodctl pod stop <id>. Its hash-checked binary was installed during the
   actual local V2 image build; credentials/provider stopping remain unverified.

The actual Linux-amd64 Python 3.10.18 base manifest was fetched and content-hash
verified through the public Docker registry:

    python@sha256:b4d66d07136c546f1765eae2bfcce9a64fa95f37c717c02bedd06d0476d1dbbd

This is a published BASE image, distinct from the locally built custom image. DEBIAN_SNAPSHOT.json
records actual small Release metadata hashes for fixed Debian/security snapshots.
Dockerfile checks those bytes and uses signed frozen package indexes during build.
The Python packages were installed in the isolated V2 image with exact artifact
hashes, followed by successful pip check. No package
was installed into the live Windows speech environments.

create_build_context.py creates a fresh allowlisted context with explicit COPY
and restrictive .dockerignore. No broad repo, .git, game, old voice vector, references
or teacher weights/environments enter it. A context has actually been created at:

    .local/voice-lab/pod-build-context-2026-10-11-v1

The separately owner-authorized LOCAL image build command is:

    docker build --platform linux/amd64 --tag unity-a2-prep:20261011-v2 .local/voice-lab/pod-build-context-2026-10-11-v2

V1 is retained as failed-build evidence. Root observed its installs complete, then
pip check exit 1 because smart-open 7.1.0 required missing wrapt. PyPI version-level
JSON had an empty dependency summary; the actual selected wheel's METADATA has
unconditional wrapt. This was not a Python 3.10 environment-marker exclusion.
The resolver now reads selected wheel core metadata and small source PKG-INFO,
records their hashes and version-summary differences, and uses a complete explicit
Linux/CPython 3.10.18 marker environment. Comparison across the selected artifacts
found only smart-open differed from its summary. Corrected V2 adds the published
CP310 Linux wrapt 1.17.2 wheel and is a NEW context; V1 is not mutated. Current
environment.lock.v2.json preserves that exact corrected resolution beside the
canonical environment.lock.json. Root's V2 Docker build completed with exit 0;
pip check reported "No broken requirements found." The missing dependency was
resolved rather than bypassed. Frozen V1/V2 contexts remain unchanged.

### Actual V2 local image and inventory

Saved evidence is under .local/voice-lab/pod-build-artifacts-2026-10-11-v2.
image-inspect.json and build-metadata.json agree on the local OCI index/image ID:

    sha256:3786ba627ace02b521b97f5aa9ef0f647fcad2133e73b1d69c7d0ced0e9ffd3f

Image tag unity-a2-prep:20261011-v2, Linux amd64, 3,429,124,586 bytes. The local
Docker RepoDigest and build metadata image.name are not evidence of a registry
push or remote pullability. image_digest therefore stays null.

Root copied exporter records using a created inspection container that was never
started. The copied Python package inventory contains exactly all 103 pinned
distributions, no extras, missing versions or mismatches. Python is 3.10.18;
the build exporter recorded WSL2 Linux/glibc 2.36. SHA readback matches:

| Inventory | SHA256 |
| --- | --- |
| package-lock.json | bdf2d5bb1ac1e09f0b3a69668e7bb54f343313ca1613890c617fad848fa6f3e4 |
| runtime-assets.json | c25d8adfd29d25e1501c41f8bbfd04861bde01ebedf739d92bdfe0d3397db9d3 |
| os-packages.tsv | 6a0ca30410bb5f2a1aedbf62626477855cb24e45e8677a748d3340617021c852 |
| artifact lock | 5081be03f5025ce38e4c2f0162f5337c9f85162101335741f74d140702478f9d |

There are 887 inventoried runtime paths: English model 28, espeak library plus
loader/bundled assets 369, Debian espeak data 489, libsndfile 1. Every role points
to inventoried SHA entries. Debian data is in its actual multiarch directory.
The 188-package OS inventory includes libc6 2.36-9+deb12u14,
libespeak-ng1/espeak-ng-data 1.51+dfsg-10+deb12u2, libsndfile1 1.2.0-1+deb12u1,
OpenSSH server 1:9.2p1-2+deb12u10 and GCC12 12.2.0-14+deb12u1.

These are build/export and copied-inventory observations. Raw asset bytes were
hashed by the actual build exporter; this review did not independently recopy
all 887 assets or execute their frontend/libraries. No trained model, phoneme
inference, H100 CUDA run, SSH startup, provider operation or registry push passed.
Root records the completed archive hash/size separately after its save finishes.
The root-owned local build receipt is training/voice/receipts/local-environment-build.json;
its local scope must bind frozen build-context inputs and actual observations,
not recursively hash the updated current specification or approve a registry.

Docker CLI 28.2.2 exists; the initial read-only observation found its Linux engine
unavailable and WSL docker-desktop stopped. Root subsequently reported a healthy
28.2.2 engine after the owner's explicit local-build approval. This reviewer
did not start either service.
Root owns the approved service start/build and later actual build results.
Building an image does not start any student training or rent/publish anything.
export_environment.py discovers Debian runtime paths through dpkg-query, verifies
installed distribution versions against the corrected artifact lock, and writes complete
package/assets/OS inventories plus a PENDING observation under /opt/unity-environment.
It imports no model and performs no phoneme/GPU/training test. In particular the
[Debian espeak data path is a multiarch library directory](https://packages.debian.org/bookworm/amd64/espeak-ng-data/filelist),
and no /usr/share assumption is used.

Record actual local image config/OCI manifest/archive identities as local build
evidence. They are not registry-pullable references. No registry push is authorized.
The future pullable image reference and its source-bound receipt remain separate;
never fill image_digest with a guessed registry reference or an unrelated ImageID.

Required named engineering environment receipt fields:

    schema: unity-voice-environment-receipt-v1
    decision: accepted
    scope: immutable-environment-preflight
    verified_by, recorded_at, evidence
    image_digest, python, environment_spec_sha256
    package_lock_path, package_lock_sha256
    runtime_assets_path, runtime_assets_sha256
    runtime_asset_roles: {english_model: [...], espeak_library: [...],
                         espeak_data: [...], libsndfile: [...]}

No receipt is manufactured here. These are engineering deliverables, not another
owner questionnaire. Pin changes require re-review and a new source manifest.

## Assemble local delivery

After all helpers are integrated and the root manifest regenerated/checked:

    python training/voice/pod/preflight_voice.py --offline --dataset <accepted-local-directory> --dataset-id <actual-id> --source-digest <actual-digest>
    python training/voice/pod/prepare_launch.py <accepted-local-directory> <NEW-packet-directory> --dataset-id <actual-id> --source-digest <actual-digest>

These are instructions, not observed execution. They perform local data/hash
checks and packing only. Mutable gate/final receipts are transported outside the
immutable source digest, avoiding circular approval. Prepare a NEW packet if any
receipt changes after packing. Archive SHA is a transport identity, not new spending
authorization. Features, teachers, game files and broad repository contents are excluded.

## Separately authorized future launch

Do not rent now. Finish image/data/recipe and concrete price/budget proposal first.
The owner approves that actual run. Initial pod entry must be a no-training
sleep/SSH environment. These utilities contain no create/start/delete action.

1. Choose a network volume. Record its provider ID and verify actual attachment
   and /workspace mount evidence before training. Ordinary volume disks use the
   same path but die when their pod is deleted; a
   [network volume exists independently](https://docs.runpod.io/pods/storage/types).
   This cannot guarantee safety from volume deletion/provider outages.
2. Save actual launch/billing epoch as VOICE_BILLING_STARTED_EPOCH. Budget clock
   starts there, including upload/preflight elapsed time, never at trainer start.
   Saved budgets/deadlines cannot silently reset.
3. Use observed direct public SSH host/port and verified host key. Runpod
   [basic SSH proxy does not support SCP/SFTP](https://docs.runpod.io/pods/configuration/use-ssh).
   The preview never disables host-key checking. Secrets never go in source/config
   or output. Upload delivery.tar to a fresh /workspace/incoming path.
4. Verify the explicit archive hash and extract into a NEW destination:

    python3 <trusted-copy>/accept_delivery.py /workspace/incoming/delivery.tar /workspace/deliveries/<packet-id> --archive-sha256 <actual-sha> --source-digest <actual-digest> --dataset-id <actual-id>

5. Set VOICE_DATASET_DIR to that delivery's dataset directory. Run its
   source/training/voice/pod/bootstrap_voice.sh only when closed quality receipts
   and priced owner approval have actually been completed. Dataset structure
   checks alone do not establish listening quality or training permission.
6. Environment and actual single-H100/CUDA checks precede work. Prepare new Linux
   features: CUDA/package/frontend identities differ from Windows cu118 caches.
7. Confirm stop credentials/provider state separately. Five bounded pinned-CLI
   requests record acknowledgments, not proof billing ended. Failure leaves
   STOP_UNCONFIRMED.txt and needs owner-console intervention.
8. Retrieve complete model run directory and SHA256SUMS via SSH; verify locally.
   Preserve working checkpoints. Final student listening/coexistence/playback
   acceptance and deployment remain independent decisions.

The proposed compute cap does not guarantee provider billing control or stop
ongoing storage charges. Source syntax checks do not verify environment execution,
resume/interruption/RNG, stop/billing, actual durability or final audible quality.

## Readiness

Config/delivery/preflight/publication and a concrete isolated build recipe are
implemented. A published-artifact lock, verified base digest, successful local
Linux build/dependency check and audited exported inventories exist. A future
pullable registry digest, actual runtime/H100/provider evidence and priced owner
approval remain separate. The local package can be assembled after integration.
It stays locked until accepted data, audited image and concrete priced approval
exist. No rental, training or provider mutation was performed.
