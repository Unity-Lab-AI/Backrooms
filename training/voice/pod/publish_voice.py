"""Atomically publish a complete configured pair, or verify/reuse that exact pair.

Invoked only inside the authorized bounded runner. Optimizers are excluded.
Interrupted sibling directories remain intact; existing releases are never removed.
Publishing model files is not owner listening/deployment acceptance.
"""
import argparse
import json
import os
import uuid
from pathlib import Path
import sys

VOICE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(VOICE))
from dataset_contract import file_hash, load_features, require_checkpoint, voice_metadata
from atomic_publish import publish_directory

FILES = ("acoustic.pt", "vocoder.pt", "voice-meta.json")


def validate_existing(output, record):
    receipt = json.loads((output / "publication.json").read_text(encoding="utf-8"))
    if ({key: receipt.get(key) for key in record} != record
            or set(path.name for path in output.iterdir()) != {*FILES, "SHA256SUMS", "publication.json"}
            or set(receipt.get("files", {})) != set(FILES)):
        raise ValueError("Existing completed publication identity/inventory differs; preserve it")
    for name, wanted in receipt["files"].items():
        if file_hash(output / name) != wanted:
            raise ValueError("Existing publication file differs: " + name)
    sums = "".join("%s  %s\n" % (receipt["files"][name], name) for name in FILES)
    if (output / "SHA256SUMS").read_text(encoding="utf-8") != sums:
        raise ValueError("Existing publication checksums differ")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("features", type=Path)
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    features = load_features(args.features)
    metadata = voice_metadata(features)
    if json.loads((args.checkpoint / "voice-meta.json").read_text(encoding="utf-8")) != metadata:
        raise ValueError("Working checkpoint metadata differs")
    import torch
    from student_state import require_student_checkpoint
    acoustic_path, vocoder_path = args.checkpoint / "acoustic.pt", args.checkpoint / "vocoder.pt"
    a = torch.load(acoustic_path, map_location="cpu", weights_only=True)
    v = torch.load(vocoder_path, map_location="cpu", weights_only=True)
    require_checkpoint(a, metadata["identity"], "acoustic")
    require_checkpoint(v, metadata["identity"], "vocoder")
    require_student_checkpoint(a); require_student_checkpoint(v)
    if (a["n_symbols"] != len(metadata["vocab"]) or a["step"] < int(os.environ["ACOUSTIC_STEPS"])
            or v["step"] < int(os.environ["VOCODER_STEPS"])):
        raise ValueError("Configured steps/symbols are incomplete")
    working_sha = file_hash(acoustic_path)
    provenance = v.get("input_provenance", {})
    if (provenance.get("mode") != "oracle-gta" or provenance.get("feature_id") != features["feature_id"]
            or provenance.get("acoustic_sha256") != working_sha
            or provenance.get("mel_manifest_sha256") != file_hash(args.checkpoint.parent / "oracle-gta/mel-manifest.json")):
        raise ValueError("Final vocoder lacks exact oracle GTA/checkpoint provenance")
    if not a.get("student_source") or a.get("student_source") != v.get("student_source"):
        raise ValueError("Paired checkpoint student source identity is missing/different")
    record = {"schema": "unity-voice-publication-v1", "identity": metadata["identity"],
              "working_acoustic_sha256": working_sha, "working_vocoder_sha256": file_hash(vocoder_path),
              "student_source": a["student_source"], "source_digest": os.environ["VOICE_DIGEST"],
              "training_steps": {"acoustic": a["step"], "vocoder": v["step"]},
              "deployment_accepted": False}
    if args.output.exists():
        validate_existing(args.output, record)
        print("Verified exact completed publication; no overwrite:", args.output)
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(args.output.name + ".publishing-" + uuid.uuid4().hex)
    temporary.mkdir()
    thin_a = {key: a[key] for key in ("schema", "kind", "identity", "model", "n_symbols", "step", "seed", "student_source")}
    thin_a["working_checkpoint_sha256"] = working_sha
    thin_v = {key: v[key] for key in ("schema", "kind", "identity", "G", "step", "seed", "input_mode",
                                    "input_provenance", "student_source")}
    for name, value in (("acoustic.pt", thin_a), ("vocoder.pt", thin_v)):
        with (temporary / name).open("xb") as stream:
            torch.save(value, stream); stream.flush(); os.fsync(stream.fileno())
    with (temporary / "voice-meta.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(metadata, stream, indent=2); stream.flush(); os.fsync(stream.fileno())
    record["files"] = {name: file_hash(temporary / name) for name in FILES}
    with (temporary / "SHA256SUMS").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write("".join("%s  %s\n" % (record["files"][name], name) for name in FILES))
        stream.flush(); os.fsync(stream.fileno())
    with (temporary / "publication.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(record, stream, indent=2); stream.flush(); os.fsync(stream.fileno())
    validate_existing(temporary, {key: value for key, value in record.items() if key != "files"})
    if file_hash(acoustic_path) != working_sha or file_hash(vocoder_path) != record["working_vocoder_sha256"]:
        raise ValueError("Working checkpoint changed during publication; preserve temporary")
    publish_directory(temporary, args.output)
    print("Complete atomic publication; listening/deployment unaccepted:", args.output)


if __name__ == "__main__":
    main()
