"""Verify/extract an explicitly chosen delivery archive on an existing volume.

Local files only: no SSH/cloud call, installs, service or training. Directory is
published atomically after exact source/dataset checks; interrupted temps remain.
"""
import argparse
import hashlib
import json
import os
import tarfile
import uuid
from pathlib import Path, PurePosixPath
from atomic_publish import publish_directory


def file_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("output", type=Path, help="NEW directory on verified /workspace volume")
    parser.add_argument("--archive-sha256", required=True)
    parser.add_argument("--source-digest", required=True)
    parser.add_argument("--dataset-id", required=True)
    args = parser.parse_args()
    if file_hash(args.archive) != args.archive_sha256:
        raise ValueError("Uploaded archive hash differs")
    if args.output.exists():
        raise ValueError("Delivery destination exists; preserve it")
    with tarfile.open(args.archive, "r:") as archive:
        members = archive.getmembers()
        names = [member.name for member in members]
        if len(names) != len(set(names)) or "delivery.json" not in names:
            raise ValueError("Duplicate/incomplete delivery archive")
        for member in members:
            path = PurePosixPath(member.name)
            if (not member.isfile() or path.is_absolute() or "\\" in member.name or ":" in member.name
                    or any(part in (".", "..") for part in path.parts) or str(path) != member.name):
                raise ValueError("Unsafe archive member: " + member.name)
        receipt = json.load(archive.extractfile("delivery.json"))
        inventory = receipt["files"]
        if (receipt.get("schema") != "unity-voice-delivery-v1"
                or receipt.get("source_digest") != args.source_digest
                or receipt["dataset"]["dataset_id"] != args.dataset_id
                or set(inventory) | {"delivery.json"} != set(names)):
            raise ValueError("Delivery identity/inventory differs")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.output.with_name(args.output.name + ".receiving-" + uuid.uuid4().hex)
        temporary.mkdir()
        for member in members:
            raw = archive.extractfile(member).read()
            if member.name != "delivery.json" and hashlib.sha256(raw).hexdigest() != inventory[member.name]:
                raise ValueError("Delivery member hash differs: " + member.name)
            target = temporary / member.name
            if temporary.resolve() not in target.resolve().parents:
                raise ValueError("Archive target escapes fresh delivery directory")
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                stream.write(raw)
        import sys
        sys.path.insert(0, str(temporary / "source/training/voice"))
        from dataset_contract import load_dataset
        _, identity = load_dataset(temporary / "dataset", verify_audio=True)
        if identity != receipt["dataset"]:
            raise ValueError("Received dataset structure/identity differs")
        from importlib.util import module_from_spec, spec_from_file_location
        spec = spec_from_file_location("delivery_preflight", temporary / "source/training/voice/pod/preflight_voice.py")
        module = module_from_spec(spec); spec.loader.exec_module(module)
        module.source_identity(args.source_digest)
    publish_directory(temporary, args.output)
    print(json.dumps({"status": "received-verified-no-training", "directory": str(args.output),
                      "dataset_id": identity["dataset_id"], "source_digest": args.source_digest}))


if __name__ == "__main__":
    main()
