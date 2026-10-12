"""Create a local immutable delivery packet; never contacts or starts a pod.

Only exact manifest source inputs, current gate/receipts, metadata and its WAVs
are included. Teacher installations, game files and feature caches are excluded.
This packet is preparation, not listening, spending or training authorization.
"""
import argparse
import io
import json
import os
import tarfile
import uuid
from pathlib import Path

from preflight_voice import ROOT, VOICE, sha, source_identity
from dataset_contract import file_hash, load_dataset
from atomic_publish import publish_directory


def add_bytes(archive, relative, raw):
    info = tarfile.TarInfo(relative)
    info.size, info.mtime, info.mode = len(raw), 0, 0o644
    archive.addfile(info, io.BytesIO(raw))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("output", type=Path, help="NEW local directory; no overwrite")
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--source-digest", required=True)
    args = parser.parse_args()
    digest = source_identity(args.source_digest)
    rows, identity = load_dataset(args.dataset, verify_audio=True)
    if identity["dataset_id"] != sha(args.dataset_id, "dataset id"):
        raise ValueError("Dataset differs from explicitly chosen delivery identity")
    if args.output.exists():
        raise ValueError("Delivery directory exists; preserve it and use a new path")
    manifest = json.loads((VOICE / "VOICE_MANIFEST.json").read_text(encoding="utf-8"))
    paths = set(manifest["files"]) | {"training/voice/VOICE_MANIFEST.json", "training/voice/VOICE_QUALITY_GATE.json"}
    gate = json.loads((VOICE / "VOICE_QUALITY_GATE.json").read_text(encoding="utf-8"))
    paths.update(check["receipt"] for check in gate["checks"].values() if check.get("receipt"))
    for relative in paths:
        resolved = (ROOT / relative).resolve()
        if VOICE not in resolved.parents or not resolved.is_file():
            raise ValueError("Delivery source is missing/outside voice source: " + relative)
    inventory = {"source/" + relative: file_hash(ROOT / relative) for relative in sorted(paths)}
    inventory["dataset/metadata.jsonl"] = identity["metadata_sha256"]
    inventory.update({"dataset/" + row["audio"]: row["sha256"] for row in rows})
    body = {"schema": "unity-voice-delivery-v1", "status": "locked-preparation-only",
            "source_digest": digest, "dataset": identity, "files": inventory,
            "training_authorized": False, "deployment_authorized": False}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(args.output.name + ".packing-" + uuid.uuid4().hex)
    temporary.mkdir()
    archive_path = temporary / "delivery.tar"
    with tarfile.open(archive_path, "w", format=tarfile.PAX_FORMAT) as archive:
        for relative in sorted(paths):
            add_bytes(archive, "source/" + relative, (ROOT / relative).read_bytes())
        add_bytes(archive, "dataset/metadata.jsonl", (args.dataset / "metadata.jsonl").read_bytes())
        for row in sorted(rows, key=lambda row: row["audio"]):
            add_bytes(archive, "dataset/" + row["audio"], (args.dataset / row["audio"]).read_bytes())
        add_bytes(archive, "delivery.json", json.dumps(body, sort_keys=True, indent=2).encode("utf-8"))
    for relative, expected in inventory.items():
        origin = ROOT / relative[7:] if relative.startswith("source/") else args.dataset / relative[8:]
        if file_hash(origin) != expected:
            raise ValueError("Input changed while packing; preserve temporary: " + relative)
    packet = dict(body, archive="delivery.tar", archive_sha256=file_hash(archive_path),
                  archive_bytes=archive_path.stat().st_size)
    (temporary / "packet.json").write_text(json.dumps(packet, indent=2), encoding="utf-8")
    publish_directory(temporary, args.output)
    print(json.dumps({"directory": str(args.output.resolve()), "source_digest": digest,
                      "dataset_id": identity["dataset_id"], "archive_sha256": packet["archive_sha256"],
                      "status": "prepared-only-no-cloud-action"}, indent=2))


if __name__ == "__main__":
    main()
