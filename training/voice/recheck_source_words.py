"""Bounded offline CPU second opinion for an existing source-screen packet.

python training/voice/recheck_source_words.py DATASET SUMMARY_DIR NEW_OUT_DIR
No downloads, recording/label changes, human acceptance, training or pod actions.
The parent enforces a walltime limit, including recognizer loading, and preserves
completed rows if it must stop the child. Every source ID retains its own target.
"""
import argparse
import collections
import datetime
import importlib.metadata
import json
import multiprocessing
import os
from pathlib import Path
import re
import time
import wave

from summarize_source_screen import comparison_tokens, digest, file_hash, lexical, read_json, safe_child, source_recipe, word_error

SMALL_CACHE = (Path.home() / ".cache/huggingface/hub/models--Systran--faster-whisper-small/snapshots/"
               "536b0662742c02347bc0e980a01041f333bce120")
HASH = re.compile(r"[0-9a-f]{64}")


def write_new(path, value):
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
        stream.flush(); os.fsync(stream.fileno())


def json_lines(data, label):
    if data and not data.endswith(b"\n"):
        raise ValueError("Non-newline-complete JSONL: " + label)
    rows = []
    for line in data.decode("utf-8").splitlines():
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError("Expected JSONL objects: " + label)
        rows.append(row)
    return rows


def observed_prefix(snapshot):
    """An active writer may append, but cannot rewrite this packet's bound prefix."""
    count = snapshot["complete_prefix_bytes"]
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise ValueError("Invalid snapshot prefix length")
    path = Path(snapshot["path"])
    with path.open("rb") as stream:
        data = stream.read(count)
    import hashlib
    if len(data) != count or hashlib.sha256(data).hexdigest() != snapshot["complete_prefix_sha256"]:
        raise ValueError("Source/screen prefix changed since the summary: " + str(path))
    return json_lines(data, str(path))


def index_rows(rows, label):
    indexed = {}
    for row in rows:
        key = row.get("id")
        if not isinstance(key, str) or key in indexed:
            raise ValueError("Duplicate/invalid ID: " + label)
        indexed[key] = row
    return indexed


def inputs(dataset, packet):
    summary, summary_sha = read_json(packet / "summary.json")
    tasks, tasks_sha = read_json(packet / "listening-tasks.json")
    clips_data = (packet / "clips.jsonl").read_bytes()
    clips = index_rows(json_lines(clips_data, "summary clips"), "summary clips")
    if (summary.get("schema") != "unity-source-screen-curation-summary-v1"
            or summary.get("status") not in ("complete_inventory_screen_summary", "explicit_partial_snapshot")
            or tasks.get("schema") != "unity-source-listening-shortlist-v1"):
        raise ValueError("Supply the existing source-screen summary/listening packet")
    plan, recipe_id, recipe_sha, expected, routes = source_recipe(dataset)
    if (summary.get("source_recipe_id") != recipe_id or summary.get("source_recipe_sha256") != recipe_sha
            or Path(summary["source_metadata_snapshot"]["path"]).resolve() != dataset / "metadata.jsonl"
            or set(clips) != set(expected)):
        raise ValueError("Summary does not bind the exact dataset recipe/inventory")
    source = index_rows(observed_prefix(summary["source_metadata_snapshot"]), "source prefix")
    scans = index_rows(observed_prefix(summary["screening_snapshot"]), "screen prefix")
    for key, record in clips.items():
        row = record["intended_source_row"]
        if ({field: value for field, value in row.items() if field != "sha256"} != expected[key]
                or record["route"] != routes[key] or record["original_screening"] != scans.get(key)
                or (key in source and row != source[key]) or (key not in source and "sha256" in row)):
            raise ValueError("Summary record differs from bound source/screen: " + key)
    if set(scans) - set(source) or set(source) - set(expected):
        raise ValueError("Invalid source/screen prefix inventory")
    candidates = []
    seen = set()
    for task in tasks["groups"]["asr_and_signal_outliers"]:
        key = task["id"]
        if key in seen or key not in clips:
            raise ValueError("Duplicate/unbound listening task")
        seen.add(key)
        record, row = clips[key], source.get(key)
        if row is None or row.get("sha256") != task.get("wav_sha256") or task.get("text") != row["text"]:
            raise ValueError("Listening task is not bound to the exact published WAV/text")
        base = record["original_screening"]
        delivery = {field: row[field] for field in ("emotion", "intensity", "pace", "speech_act")}
        if (base is None or base.get("audio_sha256") != row["sha256"] or base.get("text") != row["text"]
                or base.get("audio") != row["audio"] or task.get("intended_delivery") != delivery
                or task.get("route") != record["route"] or task.get("original_flags") != base["flags"]):
            raise ValueError("Base/listening source labels or audio hash differ: " + key)
        path = safe_child(dataset, row["audio"])
        if Path(task["audio"]).resolve() != path:
            raise ValueError("Listening task path differs from source")
        if record.get("transcript_comparison", {}).get("classification") == "unresolved_asr_disagreement":
            if not HASH.fullmatch(row["sha256"]) or file_hash(path) != row["sha256"]:
                raise ValueError("Source WAV changed: " + key)
            with wave.open(str(path), "rb") as audio:
                if (audio.getnchannels(), audio.getsampwidth(), audio.getframerate(), audio.getcomptype()) != (1, 2, 24000, "NONE"):
                    raise ValueError("Invalid source WAV format: " + key)
            candidates.append({"id": key, "source_row": row, "audio_path": str(path),
                               "base_screening": record["original_screening"], "source_summary_record": record})
    unresolved = {key for key, record in clips.items()
                  if record.get("transcript_comparison", {}).get("classification") == "unresolved_asr_disagreement"}
    if {job["id"] for job in candidates} != unresolved:
        raise ValueError("Listening queue lacks exact unresolved transcript coverage")
    binding = {"summary_path": str(packet / "summary.json"), "summary_sha256": summary_sha,
               "clips_sha256": file_hash(packet / "clips.jsonl"), "listening_tasks_sha256": tasks_sha,
               "summary_status": summary["status"], "source_recipe_id": recipe_id,
               "source_recipe_sha256": recipe_sha, "source_metadata_snapshot": summary["source_metadata_snapshot"],
               "base_screening_snapshot": summary["screening_snapshot"], "owner_receipts": summary["owner_receipts"],
               "source_scope": plan["scope"], "expected_source_clips": len(expected)}
    return candidates, binding


def worker(jobs, model_dir, threads, output):
    """Child only: loading/transcription cannot outlive the parent deadline."""
    try:
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        for variable in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
            os.environ[variable] = str(threads)
        from faster_whisper import WhisperModel
        model = WhisperModel(model_dir, device="cpu", compute_type="int8", cpu_threads=threads,
                             num_workers=1, local_files_only=True)
        grouped = collections.defaultdict(list)
        for job in jobs:
            grouped[job["source_row"]["sha256"]].append(job)
        for sha, shared in grouped.items():
            for job in shared:
                if file_hash(job["audio_path"]) != sha:
                    raise ValueError("Source WAV changed before ASR: " + job["id"])
            started = time.monotonic()
            segments, _ = model.transcribe(shared[0]["audio_path"], language="en", beam_size=5,
                condition_on_previous_text=False, vad_filter=False, word_timestamps=False)
            segments = [{"start": part.start, "end": part.end, "text": part.text} for part in segments]
            transcript = " ".join(part["text"].strip() for part in segments).strip()
            elapsed = time.monotonic() - started
            for job in shared:
                row, base = job["source_row"], job["base_screening"]
                if file_hash(job["audio_path"]) != sha:
                    raise ValueError("Source WAV changed during ASR: " + job["id"])
                target, target_rules = comparison_tokens(row["text"])
                actual, actual_rules = comparison_tokens(transcript)
                previous, _ = comparison_tokens(base["recognized_text"])
                classification = ("second_matches_intended" if actual == target else
                                  "two_recognizers_agree_against_intended" if actual == previous else
                                  "recognizers_disagree_unresolved")
                entry = {"id": job["id"], "audio": row["audio"], "audio_sha256": sha,
                    "source_row": row, "base_screening": base, "second_recognized_text": transcript,
                    "second_segments": segments, "second_comparison_tokens": actual,
                    "expected_comparison_tokens": target, "second_word_error_rate": word_error(target, actual),
                    "second_exact_lexical_match": lexical(row["text"]) == lexical(transcript),
                    "comparison_rules": sorted(set(target_rules + actual_rules)), "relation": classification,
                    "shared_audio_ids": [item["id"] for item in shared], "asr_elapsed_seconds_for_shared_audio": elapsed,
                    "previous_owner_acceptance": job["source_summary_record"]["previous_owner_acceptance"],
                    "previous_owner_ids": job["source_summary_record"]["previous_owner_ids"],
                    "event_audibility": job["source_summary_record"]["event_audibility"],
                    "human_listening_acceptance": "not_inferred", "acceptance": "not_granted",
                    "training_authorized": False, "pod_rental_authorized": False}
                with (Path(output) / "rechecks.jsonl").open("a", encoding="utf-8", newline="\n") as stream:
                    stream.write(json.dumps(entry, ensure_ascii=False, allow_nan=False) + "\n")
                    stream.flush(); os.fsync(stream.fileno())
                print("SOURCE WORD RECHECK " + job["id"] + " " + classification, flush=True)
    except Exception as error:
        write_new(Path(output) / "worker-error.json", {"error_type": type(error).__name__, "message": str(error),
                  "scope": "second-ASR failure; completed rows preserved; no acceptance granted"})
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path); parser.add_argument("summary", type=Path); parser.add_argument("out", type=Path)
    parser.add_argument("--model-dir", type=Path, default=SMALL_CACHE)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--max-seconds", type=int, default=3600)
    args = parser.parse_args()
    if not 1 <= args.threads <= 4 or not 60 <= args.max_seconds <= 86400:
        raise ValueError("Use 1..4 CPU threads and a 60..86400-second deadline")
    dataset, packet, output, model_dir = [path.resolve() for path in (args.dataset, args.summary, args.out, args.model_dir)]
    if (output.exists() or args.out.is_symlink() or output.is_relative_to(dataset)
            or output.is_relative_to(packet) or output.is_relative_to(model_dir)):
        raise ValueError("Use a NEW output directory outside source, summary and cached weights")
    started = time.monotonic()
    jobs, binding = inputs(dataset, packet)
    required = [model_dir / name for name in ("config.json", "model.bin", "tokenizer.json", "vocabulary.txt")]
    if not all(path.is_file() for path in required):
        raise ValueError("Complete existing local faster-whisper-small weights are required; no download")
    config = {"schema": "unity-source-word-recheck-recipe-v1", "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "inputs": binding, "requested_ids": [job["id"] for job in jobs],
        "requested_wav_sha256": {job["id"]: job["source_row"]["sha256"] for job in jobs},
        "helper_sha256": file_hash(Path(__file__)),
        "comparison_code_sha256": file_hash(Path(__file__).with_name("summarize_source_screen.py")),
        "qa_policy_sha256": file_hash(Path(__file__).with_name("SOURCE_QA_POLICY.md")),
        "model_dir": str(model_dir), "model_files_sha256": {path.name: file_hash(path) for path in required},
        "versions": {name: importlib.metadata.version(name) for name in ("faster-whisper", "ctranslate2")},
        "asr": {"device": "cpu", "compute_type": "int8", "threads": args.threads, "num_workers": 1,
                "language": "en", "beam_size": 5, "local_files_only": True,
                "condition_on_previous_text": False, "vad_filter": False},
        "deadline_seconds": args.max_seconds, "scope": "fallible second transcript evidence only; no acceptance"}
    config["recipe_id"] = digest(config)
    output.mkdir(parents=True, exist_ok=False)
    write_new(output / "recheck-recipe.json", config)
    expired = False
    exit_code = 0
    if jobs:
        process = multiprocessing.get_context("spawn").Process(target=worker, args=(jobs, str(model_dir), args.threads, str(output)))
        process.start()
        process.join(timeout=max(0, args.max_seconds - (time.monotonic() - started)))
        if process.is_alive():
            expired = True
            process.terminate(); process.join(timeout=5)
            if process.is_alive():
                process.kill(); process.join(timeout=5)
        exit_code = process.exitcode
        process.close()
    path = output / "rechecks.jsonl"
    raw = path.read_bytes() if path.is_file() else b""
    complete_prefix = raw if not raw or raw.endswith(b"\n") else raw[:raw.rfind(b"\n") + 1]
    done = index_rows(json_lines(complete_prefix, "completed rechecks"), "completed rechecks")
    wanted = {job["id"]: job for job in jobs}
    for key, entry in done.items():
        if (key not in wanted or entry["source_row"] != wanted[key]["source_row"]
                or entry["base_screening"] != wanted[key]["base_screening"]
                or entry["audio_sha256"] != wanted[key]["source_row"]["sha256"]):
            raise ValueError("Completed second-ASR row is not bound to its exact source")
    complete = set(done) == set(wanted) and not expired and exit_code == 0 and complete_prefix == raw
    report = {"schema": "unity-source-word-recheck-summary-v1", "recipe_id": config["recipe_id"],
        "status": "complete_requested_subset" if complete else "partial_requested_subset",
        "complete_requested_subset": complete, "source_packet_status": binding["summary_status"],
        "requested_ids": list(wanted), "completed_ids": list(done), "missing_ids": sorted(set(wanted) - set(done)),
        "unique_requested_audio_hashes": len({job["source_row"]["sha256"] for job in jobs}),
        "relations": dict(collections.Counter(entry["relation"] for entry in done.values())),
        "deadline_reached": expired, "worker_exit_code": exit_code, "elapsed_seconds": time.monotonic() - started,
        "recheck_recipe_sha256": file_hash(output / "recheck-recipe.json"),
        "rechecks_sha256": file_hash(path) if path.is_file() else None,
        "ignored_unpublished_tail_bytes": len(raw) - len(complete_prefix),
        "acceptance": "not_granted; transcripts are evidence for triage, never human listening",
        "training_authorized": False, "pod_rental_authorized": False}
    write_new(output / "summary.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not complete:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
