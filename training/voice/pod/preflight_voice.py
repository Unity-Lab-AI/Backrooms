"""Read-only preflight. No rental, training, installs, services or provider API calls.

--offline checks immutable source and supplied labeled dataset without model imports.
--environment additionally validates a prepared environment receipt and installed
distribution metadata. GPU/credential/provider observations remain separate evidence.
This tool never writes acceptance receipts or changes the quality gate.
"""
import argparse
import importlib.metadata
import json
import os
import platform
import re
import shutil
import sys
from pathlib import Path

VOICE = Path(__file__).resolve().parent.parent
ROOT = VOICE.parent.parent
sys.path.insert(0, str(VOICE))
from dataset_contract import file_hash, load_dataset


def sha(value, label):
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ValueError(label + " must be an exact SHA256")
    return value


def source_identity(expected):
    manifest = json.loads((VOICE / "VOICE_MANIFEST.json").read_text(encoding="utf-8"))
    files = manifest["files"]
    if not isinstance(files, dict) or not files:
        raise ValueError("Empty source manifest")
    for relative, wanted in files.items():
        path = (ROOT / relative).resolve()
        if ROOT not in path.parents or not path.is_file() or file_hash(path) != sha(wanted, relative):
            raise ValueError("Source manifest file differs: " + relative)
    import hashlib
    digest = hashlib.sha256("".join("%s  %s\n" % (files[k], k) for k in sorted(files)).encode()).hexdigest()
    if digest != manifest["digest"] or (expected and digest != sha(expected, "VOICE_DIGEST")):
        raise ValueError("Source manifest/expected digest differs")
    return digest


def environment_identity():
    """Validate a separately observed receipt; metadata is not functional acceptance."""
    spec = json.loads(Path(__file__).with_name("ENVIRONMENT_SPEC.json").read_text(encoding="utf-8"))
    receipt_path = Path(os.environ["VOICE_ENVIRONMENT_RECEIPT"])
    if file_hash(receipt_path) != sha(os.environ["VOICE_ENVIRONMENT_RECEIPT_SHA256"], "environment receipt"):
        raise ValueError("Environment receipt hash differs")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if (receipt.get("schema") != "unity-voice-environment-receipt-v1"
            or receipt.get("decision") != "accepted" or receipt.get("scope") != "immutable-environment-preflight"
            or not receipt.get("verified_by") or not receipt.get("recorded_at") or not receipt.get("evidence")):
        raise ValueError("Prepared environment needs named engineering evidence, not a template")
    image = os.environ["VOICE_IMAGE_DIGEST"]
    if (re.fullmatch(r"[A-Za-z0-9./:_-]+@sha256:[0-9a-f]{64}", image) is None
            or receipt.get("image_digest") != image or spec.get("image_digest") != image):
        raise ValueError("Exact registry image digest differs or is absent")
    if receipt.get("environment_spec_sha256") != file_hash(Path(__file__).with_name("ENVIRONMENT_SPEC.json")):
        raise ValueError("Environment specification changed")
    if platform.system() != "Linux" or platform.machine().lower() not in ("x86_64", "amd64"):
        raise ValueError("Prepared worker requires Linux x86_64")
    if platform.python_version() != spec["python"] or receipt.get("python") != spec["python"]:
        raise ValueError("Python build differs")
    for name, version in spec["packages"].items():
        if importlib.metadata.version(name) != version:
            raise ValueError("Installed package differs: " + name)
    # Full lock covers transitive packages too. Local receipt JSON paths are data,
    # never shell commands. No package manager or model is imported.
    lock_path = Path(receipt["package_lock_path"])
    if file_hash(lock_path) != sha(receipt.get("package_lock_sha256"), "package lock"):
        raise ValueError("Complete package lock differs")
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    normalize = lambda name: re.sub(r"[-_.]+", "-", name).lower()
    names = {normalize(dist.metadata["Name"]) for dist in importlib.metadata.distributions()}
    actual = {name: importlib.metadata.version(name) for name in names}
    if not isinstance(lock, dict) or lock != actual:
        raise ValueError("Installed distribution inventory differs from complete prepared lock")
    assets_path = Path(receipt["runtime_assets_path"])
    if file_hash(assets_path) != sha(receipt.get("runtime_assets_sha256"), "runtime assets"):
        raise ValueError("Runtime asset inventory differs")
    assets = json.loads(assets_path.read_text(encoding="utf-8"))
    if (not isinstance(assets, dict) or not assets
            or set(receipt.get("runtime_asset_roles", {})) != {"english_model", "espeak_library", "espeak_data", "libsndfile"}):
        raise ValueError("English/espeak/libsndfile runtime assets must be recorded")
    for relative, wanted in assets.items():
        path = Path(relative)
        if not path.is_absolute() or not path.is_file() or file_hash(path) != sha(wanted, "runtime asset"):
            raise ValueError("Runtime asset differs: " + relative)
    for paths in receipt["runtime_asset_roles"].values():
        if not isinstance(paths, list) or not paths or any(path not in assets for path in paths):
            raise ValueError("Every runtime asset role must bind inventoried files")
    binary = shutil.which("runpodctl")
    if binary is None or file_hash(binary) != spec["runpodctl"]["binary_sha256"]:
        raise ValueError("Prepared runpodctl binary differs from reviewed release")
    return {"image_digest": image, "python": spec["python"], "packages": spec["packages"],
            "package_lock_sha256": receipt["package_lock_sha256"],
            "runtime_assets_sha256": receipt["runtime_assets_sha256"],
            "runpodctl_sha256": spec["runpodctl"]["binary_sha256"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--environment", action="store_true")
    parser.add_argument("--dataset", type=Path)
    parser.add_argument("--dataset-id")
    parser.add_argument("--source-digest")
    args = parser.parse_args()
    if not args.offline and not args.environment:
        parser.error("Choose --offline or --environment; no start option exists")
    report = {"schema": "unity-voice-readonly-preflight-v1", "training_authorized": False,
              "provider_observed": False, "source_digest": source_identity(args.source_digest)}
    if args.dataset:
        _, identity = load_dataset(args.dataset, verify_audio=True)
        if args.dataset_id and identity["dataset_id"] != sha(args.dataset_id, "dataset id"):
            raise ValueError("Supplied dataset identity differs")
        report["dataset"] = identity
    elif args.dataset_id:
        raise ValueError("--dataset-id requires --dataset")
    if args.environment:
        report["environment"] = environment_identity()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, importlib.metadata.PackageNotFoundError) as error:
        print("PREFLIGHT REFUSED: " + str(error), file=sys.stderr)
        sys.exit(2)
