"""Render reserved listening text with its literal controls; never invent support.

Runs only inside the authorized deadline-bound runner. Unsupported delivery/event
requests are recorded as not_rendered, never relabelled or pitch-adjusted.
The suite does not enter the training dataset; sample files are not acceptance.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

VOICE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(VOICE))
from dataset_contract import FEATURES, delivery, file_hash, load_features, normalize_transcript, voice_metadata

FIELDS = {"id", "text", "emotion", "intensity", "pace", "speech_act"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("features", type=Path)
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("output", type=Path, help="NEW output directory; no overwrite")
    args = parser.parse_args()
    path = VOICE / "LISTENING_EVAL_TEXT.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    features = load_features(args.features)
    training_texts = {normalize_transcript(row["text"]) for row in features["entries"]}
    ids = set()
    for row in rows:
        if (set(row) != FIELDS or not isinstance(row["id"], str) or row["id"] in ids
                or not isinstance(row["text"], str) or not row["text"].strip()
                or normalize_transcript(row["text"]) in training_texts):
            raise ValueError("Reserved evaluation schema/ID/text separation differs")
        delivery(row["emotion"], row["intensity"], row["pace"], row["speech_act"])
        ids.add(row["id"])
    if not rows:
        raise ValueError("Reserved evaluation suite is empty")
    import soundfile as sf
    from infer import Voice
    args.output.mkdir(parents=True, exist_ok=False)
    snapshot = args.output / "loaded-checkpoint"
    snapshot.mkdir()
    for name in ("acoustic.pt", "vocoder.pt", "voice-meta.json"):
        shutil.copyfile(args.checkpoint / name, snapshot / name)
    if json.loads((snapshot / "voice-meta.json").read_text(encoding="utf-8")) != voice_metadata(features):
        raise ValueError("Snapshotted voice pair belongs to different features; no evaluation attribution is permitted")
    # Trainers replace checkpoint files atomically. Copies retain the exact pair
    # this evaluation loaded even while later working checkpoints advance.
    voice = Voice(snapshot)
    import torch
    loaded = {"voice_metadata_sha256": file_hash(snapshot / "voice-meta.json")}
    for kind in ("acoustic", "vocoder"):
        filename = kind + ".pt"
        state = torch.load(snapshot / filename, map_location="cpu", weights_only=True)
        loaded[kind] = {"sha256": file_hash(snapshot / filename), "step": state["step"],
                        "student_source": state["student_source"], "snapshot": "loaded-checkpoint/" + filename}
        del state
    results = []
    for index, row in enumerate(rows):
        entry = dict(row)
        try:
            # Voice.say internally chunks long turns; each chunk retains the same
            # requested controls and matching training/event/length checks.
            wav = voice.say(row["text"], row["emotion"], row["intensity"], row["pace"], row["speech_act"])
            name = "%03d.wav" % index
            sf.write(args.output / name, wav, FEATURES["sample_rate"], subtype="PCM_16")
            entry.update(status="rendered", audio=name, sha256=file_hash(args.output / name))
        except (ValueError, RuntimeError) as error:
            entry.update(status="not_rendered", reason=str(error))
        results.append(entry)
    receipt = {"kind": "reserved-unseen-listening-suite", "quality_accepted": False,
               "suite_sha256": file_hash(path), "feature_id": features["feature_id"],
               "loaded_pair": loaded,
               "results": results}
    with (args.output / "samples.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(receipt, stream, indent=2)
    print("Reserved listening probes:", args.output, "-- no acceptance implied")


if __name__ == "__main__":
    main()
