"""Create an immutable, per-clip human-curated v2 source dataset.

Export a review form, listen, and fill it in manually:
    python training/voice/curate_dataset.py template <draft_dir> <new_review.json>
    python training/voice/curate_dataset.py apply <draft_dir> <review.json> <new_dataset_dir>

No default accepts a clip. Every decision requires a named human reviewer and an
explicit listening acknowledgment. This validates an attestation; software cannot
prove that listening occurred. It never edits the draft, global quality gate or
training/deployment authorization. Wrong words must be rejected and re-rendered;
relabeling changes delivery controls only, not the spoken transcript or WAV bytes.

Fill reviewer with the real reviewing person's identity, reviewer_kind="human",
and reviewed_at with a timezone-qualified ISO8601 timestamp. For each clip, set
listened=true only after listening and choose accepted/rejected/relabel. Accepted
clips need actual_delivery explicitly equal to intended_delivery; relabel needs
valid different controls. Rejection/relabel requires a comment explaining why.
"""
import argparse
import ctypes
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import uuid

from dataset_contract import canonical_hash, delivery, file_hash, load_dataset, local_path, split_for

REVIEW_SCHEMA = "unity-voice-curation-review-v1"
RECEIPT_SCHEMA = "unity-voice-curation-receipt-v1"
RESULT_SCHEMA = "unity-voice-curation-result-v1"
CONTROLS = {"emotion", "intensity", "pace", "speech_act"}
REVIEW_FIELDS = {"schema", "draft_dataset", "reviewer", "reviewer_kind", "reviewed_at", "comment", "clips"}
CLIP_FIELDS = {"id", "text", "audio", "wav_sha256", "voice_id", "original_source_id",
               "intended_delivery", "decision", "listened", "actual_delivery", "comment"}


def text_field(value, name, maximum=8000, required=False):
    if not isinstance(value, str) or len(value) > maximum or (required and not value.strip()):
        raise ValueError("Missing/invalid " + name)
    return value


def reviewed_time(value):
    text_field(value, "reviewed_at", 128, required=True)
    try:
        parsed = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("reviewed_at must be an ISO8601 timestamp with a timezone") from error
    if parsed.tzinfo is None:
        raise ValueError("reviewed_at must include a timezone")
    return value


def intended(row):
    return {key: row[key] for key in ("emotion", "intensity", "pace", "speech_act")}


def controls(value):
    if not isinstance(value, dict) or set(value) != CONTROLS:
        raise ValueError("actual_delivery must contain exactly emotion/intensity/pace/speech_act")
    return delivery(**value)


def review_binding(row):
    return {"id": row["id"], "text": row["text"], "audio": row["audio"],
            "wav_sha256": row["sha256"], "voice_id": row["voice_id"],
            "original_source_id": row["source_id"], "intended_delivery": intended(row)}


def outside_source(path, source):
    if Path(path).is_symlink():
        raise ValueError("Output is an existing symlink; no replacement is permitted")
    path, source = Path(path).resolve(), Path(source).resolve()
    if path == source or path.is_relative_to(source):
        raise ValueError("New review/output must be outside the immutable source directory")
    return path


def write_new_json(path, value):
    """Atomic no-replace file publication; never replace an existing review."""
    path = Path(path)
    if path.exists() or path.is_symlink():
        raise ValueError("Output already exists; choose a new review path")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".writing-" + uuid.uuid4().hex)
    payload = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    with temporary.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    # Both names are in the same directory. Windows rename is atomic and refuses
    # an existing destination; unlike hard links it works in the local sandbox.
    if os.name == "nt":
        os.rename(temporary, path)
    else:
        # An existing destination makes the exclusive POSIX hard link fail.
        os.link(temporary, path)
        temporary.unlink()


def publish_directory(work, destination):
    """One atomic no-replace publication, preserving work on any failure."""
    work, destination = Path(work).resolve(), Path(destination).resolve()
    if work.parent != destination.parent or not work.name.startswith(destination.name + ".curating-"):
        raise ValueError("Publication paths are not the checked sibling work/destination pair")
    if destination.exists() or destination.is_symlink():
        raise ValueError("Destination appeared concurrently; preserve the work directory")
    if os.name == "nt":
        # Windows rename refuses an existing destination, including an empty directory.
        os.rename(work, destination)
    elif sys.platform.startswith("linux"):
        # Ordinary POSIX rename may replace an empty directory. RENAME_NOREPLACE must
        # be supported by this filesystem; otherwise fail and keep the work sibling.
        library = ctypes.CDLL(None, use_errno=True)
        rename = getattr(library, "renameat2", None)
        if rename is None:
            raise ValueError("Atomic no-replace directory publication unavailable; work preserved")
        rename.argtypes = (ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint)
        rename.restype = ctypes.c_int
        if rename(-100, os.fsencode(work), -100, os.fsencode(destination), 1) != 0:
            code = ctypes.get_errno()
            raise OSError(code, os.strerror(code), str(destination))
    else:
        raise ValueError("This platform lacks the implemented atomic no-replace publication; work preserved")


def export_template(draft, output):
    rows, identity = load_dataset(draft, verify_audio=True)
    output = outside_source(output, draft)
    form = {"schema": REVIEW_SCHEMA, "draft_dataset": identity,
            "reviewer": None, "reviewer_kind": None, "reviewed_at": None,
            "comment": "", "clips": []}
    for row in rows:
        form["clips"].append(dict(review_binding(row), decision="pending", listened=False,
                                  actual_delivery=None, comment=""))
    write_new_json(output, form)
    print("Exported %d pending clip reviews to %s. Nothing accepted or authorized." % (len(rows), output))


def validate_review(review, rows, identity):
    if not isinstance(review, dict) or set(review) != REVIEW_FIELDS or review.get("schema") != REVIEW_SCHEMA:
        raise ValueError("Review must contain exactly the curation-review-v1 fields")
    if review["draft_dataset"] != identity:
        raise ValueError("Review belongs to a different draft dataset/metadata identity")
    text_field(review["reviewer"], "human reviewer identity", 256, required=True)
    if review["reviewer_kind"] != "human":
        raise ValueError("Review requires an explicitly identified human, not automated acceptance")
    reviewed_time(review["reviewed_at"])
    text_field(review["comment"], "review comment")
    clips = review["clips"]
    if not isinstance(clips, list) or len(clips) != len(rows):
        raise ValueError("Review must cover every draft clip exactly once")
    originals = {row["id"]: row for row in rows}
    decisions = {}
    for clip in clips:
        if not isinstance(clip, dict) or set(clip) != CLIP_FIELDS:
            raise ValueError("Clip review must contain exactly the template fields")
        clip_id = clip["id"]
        if not isinstance(clip_id, str) or clip_id not in originals or clip_id in decisions:
            raise ValueError("Unknown/duplicate review clip identity")
        row = originals[clip_id]
        if {key: clip[key] for key in review_binding(row)} != review_binding(row):
            raise ValueError("Original clip text/hash/source/labels changed in review: " + clip_id)
        decision = clip["decision"]
        if decision not in ("accepted", "rejected", "relabel"):
            raise ValueError("Every clip requires accepted/rejected/relabel; pending is refused: " + clip_id)
        if clip["listened"] is not True:
            raise ValueError("Explicit per-clip human listening acknowledgment missing: " + clip_id)
        comment = text_field(clip["comment"], "clip comment", required=decision != "accepted")
        actual = controls(clip["actual_delivery"]) if clip["actual_delivery"] is not None else None
        if decision == "accepted" and actual != intended(row):
            raise ValueError("Accepted clip needs its explicitly confirmed intended controls; use relabel for changes: " + clip_id)
        if decision == "relabel" and (actual is None or actual == intended(row)):
            raise ValueError("Relabel needs explicitly corrected delivery controls: " + clip_id)
        decisions[clip_id] = {"original_row": row, "decision": decision, "listened": True,
                              "actual_delivery": actual, "comment": comment}
    if set(decisions) != set(originals):
        raise ValueError("Review has missing or extra clips")
    retained = [row for row in rows if decisions[row["id"]]["decision"] != "rejected"]
    if not retained or {split_for(row["text"]) for row in retained} != {"train", "heldout"}:
        raise ValueError("Retained dataset needs at least one train and one heldout transcript group")
    return decisions, retained


def apply_review(draft, review_path, output):
    draft, review_path = Path(draft).resolve(), Path(review_path).resolve()
    destination = outside_source(output, draft)
    if destination.exists() or destination.is_symlink():
        raise ValueError("Dataset destination already exists; no overwrite is permitted")
    rows, original_identity = load_dataset(draft, verify_audio=True)
    review_bytes = review_path.read_bytes()
    review = json.loads(review_bytes)
    decisions, retained = validate_review(review, rows, original_identity)
    # Record the literal review-file SHA256 as well as the normalized review identity.
    receipt = {"schema": RECEIPT_SCHEMA, "draft_dataset": original_identity,
               "review_file_sha256": hashlib.sha256(review_bytes).hexdigest(), "review_id": canonical_hash(review),
               "reviewer": review["reviewer"], "reviewer_kind": "human", "reviewed_at": review["reviewed_at"],
               "comment": review["comment"], "curator_code_sha256": file_hash(Path(__file__)),
               "decisions": [decisions[row["id"]] for row in rows],
               "limits": {"listening_is_a_human_attestation": True,
                          "global_corpus_acceptance_granted": False,
                          "training_authorized": False, "deployment_authorized": False}}
    receipt_payload = json.dumps(receipt, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    receipt_hash = hashlib.sha256(receipt_payload.encode("utf-8")).hexdigest()
    destination.parent.mkdir(parents=True, exist_ok=True)
    work = destination.with_name(destination.name + ".curating-" + uuid.uuid4().hex)
    work.mkdir(exist_ok=False)
    (work / "wavs").mkdir()
    (work / "curation-receipt.json").write_text(receipt_payload, encoding="utf-8", newline="\n")
    new_rows = []
    for row in retained:
        target = "wavs/" + row["id"] + ".wav"
        source = local_path(draft, row["audio"])
        copy = local_path(work, target)
        if copy.exists() or copy.is_symlink():
            raise ValueError("Unexpected existing WAV in fresh work directory; preserve it")
        shutil.copyfile(source, copy)
        if file_hash(copy) != row["sha256"]:
            raise ValueError("Source changed or copy failed; work preserved: " + row["id"])
        new_source = canonical_hash({"schema": "unity-voice-curated-source-v1",
                                     "original_source_id": row["source_id"],
                                     "curation_receipt_sha256": receipt_hash})
        accepted = dict(row, audio=target, source_id=new_source)
        accepted.update(decisions[row["id"]]["actual_delivery"])
        new_rows.append(accepted)
    metadata = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n" for row in new_rows)
    (work / "metadata.jsonl").write_text(metadata, encoding="utf-8", newline="\n")
    _, curated_identity = load_dataset(work, verify_audio=True)
    _, unchanged_identity = load_dataset(draft, verify_audio=True)
    if unchanged_identity != original_identity or review_path.read_bytes() != review_bytes:
        raise ValueError("Source/review changed during curation; work preserved, nothing published")
    result = {"schema": RESULT_SCHEMA, "dataset": curated_identity, "original_dataset": original_identity,
              "curation_receipt_sha256": receipt_hash, "retained_clip_ids": [row["id"] for row in retained],
              "rejected_clip_ids": [row["id"] for row in rows if decisions[row["id"]]["decision"] == "rejected"],
              "wav_bytes_unchanged": True, "global_corpus_acceptance": "not_granted",
              "student_training_started": False, "training_authorized": False, "deployment_authorized": False}
    (work / "curation-result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    publish_directory(work, destination)
    print("Published %d human-reviewed clips to %s; %d rejected recordings remain in the draft." % (
        len(retained), destination, len(rows) - len(retained)))
    print("Dataset identity:", curated_identity["dataset_id"])
    print("Global corpus acceptance and training/deployment permissions were not changed.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    template = commands.add_parser("template", help="write a new entirely pending human review form")
    template.add_argument("draft", type=Path)
    template.add_argument("out", type=Path)
    apply = commands.add_parser("apply", help="publish a new dataset from a complete human listening review")
    apply.add_argument("draft", type=Path)
    apply.add_argument("review", type=Path)
    apply.add_argument("out", type=Path)
    args = parser.parse_args()
    if args.command == "template":
        export_template(args.draft, args.out)
    else:
        apply_review(args.draft, args.review, args.out)


if __name__ == "__main__":
    main()
