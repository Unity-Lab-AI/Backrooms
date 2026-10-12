"""Combine complete parent source QA without clearing flags or inventing listening.

python training/voice/merge_source_qa.py MERGED_DATASET NEW_OUT \
  --parent-qa DATASET BASE_SCREEN SOURCE_SUMMARY SECOND_ASR [--parent-qa ...]
Only JSON/file validation and unchanged evidence copies; no ASR/model execution.
"""
import argparse
import collections
import datetime
import math
from pathlib import Path
import shutil

from dataset_contract import canonical_hash, file_hash, local_path
from merge_source_datasets import (VOICE, indexed, load_merged, new_work, read_json,
                                   unchanged, verify_parent, write_json, write_lines)
from pod.atomic_publish import publish_directory
from recheck_source_words import inputs as recheck_inputs, json_lines
from speech_text import event_counts
from summarize_source_screen import comparison_tokens, lexical, owner_records, word_error

QA_SCHEMA = "unity-merged-source-qa-v1"


def artifact(path):
    path = Path(path).resolve()
    if not path.is_file():
        raise ValueError("Required QA artifact missing: " + str(path))
    return {"path": str(path), "sha256": file_hash(path)}


def snapshot(snapshot, path, count):
    path = Path(path).resolve()
    raw = path.read_bytes()
    if (Path(snapshot["path"]).resolve() != path or snapshot.get("exists") is not True
            or snapshot.get("snapshot_bytes") != len(raw) or snapshot.get("complete_prefix_bytes") != len(raw)
            or snapshot.get("snapshot_sha256") != file_hash(path)
            or snapshot.get("complete_prefix_sha256") != file_hash(path)
            or snapshot.get("ignored_unpublished_tail_bytes") != 0 or snapshot.get("rows") != count):
        raise ValueError("QA snapshot is partial, stale or bound to a different file")
    return indexed(json_lines(raw, str(path)), str(path))


def number(value, label, low=0, high=None):
    if (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value)
            or value < low or (high is not None and value > high)):
        raise ValueError("Invalid QA numeric field: " + label)


def validate_packet(dataset, screen, packet, second):
    parent = verify_parent(dataset)
    descriptor = parent["descriptor"]
    identity, recipe_id = descriptor["dataset"], descriptor["recipe_id"]
    row_map = indexed(parent["rows"], "QA parent source rows")
    summary = read_json(packet / "summary.json")
    base_summary = read_json(screen / "summary.json")
    inspection = read_json(screen / "inspection-recipe.json")
    tasks = read_json(packet / "listening-tasks.json")
    count = len(row_map)
    if (summary.get("schema") != "unity-source-screen-curation-summary-v1"
            or summary.get("status") != "complete_inventory_screen_summary"
            or summary.get("partial_requested") is not False
            or summary.get("source_recipe_id") != recipe_id
            or summary.get("source_recipe_sha256") != descriptor["artifacts_sha256"]["render-recipe.json"]
            or summary.get("source_dataset_identity") != identity
            or summary.get("source_build_sha256") != descriptor["artifacts_sha256"]["source-build.json"]
            or summary.get("source_build_matches_snapshot") is not True
            or summary.get("original_qa_summary_matches_snapshot") is not True
            or summary.get("full_corpus_human_listening_inferred") is not False
            or summary.get("training_authorized") is not False
            or summary.get("original_qa_summary_sha256") != file_hash(screen / "summary.json")
            or tasks.get("schema") != "unity-source-listening-shortlist-v1"):
        raise ValueError("Parent source-summary packet is not an exact complete inventory")
    inventory = summary["inventory"]
    if (any(inventory.get(key) != count for key in ("expected", "rendered", "screened"))
            or inventory.get("not_rendered_ids") != [] or inventory.get("not_screened_ids") != []
            or inventory.get("complete_rendered_inventory") is not True
            or inventory.get("complete_screened_inventory") is not True):
        raise ValueError("Parent source-summary inventory is incomplete")
    source = snapshot(summary["source_metadata_snapshot"], dataset / "metadata.jsonl", count)
    scans = snapshot(summary["screening_snapshot"], screen / "screening.jsonl", count)
    clips = indexed(json_lines((packet / "clips.jsonl").read_bytes(), "source summary clips"), "source summary clips")
    if source != row_map or set(scans) != set(row_map) or set(clips) != set(row_map):
        raise ValueError("Source/base-screen/summary row inventories differ")
    if (base_summary.get("schema") != "unity-source-audio-screen-summary-v1"
            or base_summary.get("recipe_id") != recipe_id or base_summary.get("complete_expected_inventory") is not True
            or base_summary.get("expected") != count or base_summary.get("screened") != count
            or base_summary.get("screening_sha256") != file_hash(screen / "screening.jsonl")
            or base_summary.get("source_metadata_sha256") != identity["metadata_sha256"]
            or inspection.get("schema") != "unity-source-audio-screen-v1"
            or inspection.get("recipe_id") != recipe_id
            or inspection.get("recipe_sha256") != descriptor["artifacts_sha256"]["render-recipe.json"]
            or summary.get("inspection_recipe") != inspection
            or summary.get("inspection_recipe_sha256") != file_hash(screen / "inspection-recipe.json")):
        raise ValueError("Original complete base screening/inspection hashes differ")
    owner_binding = summary["owner_receipts"]
    owner_path, approval_path = Path(owner_binding["owner_receipt"]), Path(owner_binding["approval_receipt"])
    owner, known, actual_owner_binding = owner_records(owner_path, approval_path)
    if owner_binding != actual_owner_binding:
        raise ValueError("Parent summary prior-heard receipt binding differs")
    for key, row in row_map.items():
        scan, clip = scans[key], clips[key]
        if (scan.get("audio_sha256") != row["sha256"] or scan.get("text") != row["text"]
                or scan.get("audio") != row["audio"] or not isinstance(scan.get("recognized_text"), str)
                or scan.get("human_listening_acceptance") != "not_inferred"
                or scan.get("event_audibility") != "not_inferred"
                or not isinstance(scan.get("flags"), list) or any(not isinstance(flag, str) for flag in scan["flags"])
                or clip.get("intended_source_row") != row or clip.get("route") != parent["routes"][key]
                or clip.get("original_screening") != scan or clip.get("inventory_status") != "screened"
                or not isinstance(clip.get("supplemental_flags"), list)
                or any(not isinstance(flag, str) for flag in clip["supplemental_flags"])):
            raise ValueError("Parent raw QA/source row/text/delivery binding differs: " + key)
        for metric in ("seconds", "rms", "peak", "word_error_rate", "leading_quiet_seconds", "trailing_quiet_seconds"):
            number(scan[metric], metric)
        number(scan["clipped_fraction"], "clipped_fraction", high=1)
        if scan["seconds"] <= 0:
            raise ValueError("Screened duration must be positive")
        if not math.isclose(scan["seconds"], parent["durations"][key], rel_tol=0, abs_tol=1e-8):
            raise ValueError("Screened duration differs from actual unchanged WAV frames")
        target, target_rules = comparison_tokens(row["text"])
        heard, heard_rules = comparison_tokens(scan["recognized_text"])
        comparison = {"classification": "exact_lexical_match" if lexical(row["text"]) == lexical(scan["recognized_text"])
                      else "narrow_segmentation_or_number_equivalent" if target == heard else "unresolved_asr_disagreement",
                      "expected_tokens": target, "recognized_tokens": heard,
                      "applied_rules": sorted(set(target_rules + heard_rules)),
                      "comparison_word_error_rate": word_error(target, heard), "original_flags_preserved": True}
        if clip.get("transcript_comparison") != comparison:
            raise ValueError("Parent normalized transcript comparison differs from retained raw text")
        found = known.get(row["sha256"], [])
        delivery = {field: row[field] for field in ("emotion", "intensity", "pace", "speech_act")}
        exact = [record for record in found if record["text"] == row["text"] and record["actual_delivery"] == delivery
                 and owner["draft_dataset"]["voice_id"] == row["voice_id"]]
        status = "exact_previously_heard_binding" if exact else "hash_known_but_binding_differs" if found else "not_previously_heard"
        laughter = event_counts(row["text"])["laughter"]
        event_status = "no_event_requested" if not laughter else "prior_exact_owner_acceptance" if exact else "pending_audible_review"
        if (clip.get("previous_owner_acceptance") != status or clip.get("previous_owner_ids") != [r["id"] for r in exact]
                or clip.get("laughter_markers") != laughter or clip.get("event_audibility") != event_status):
            raise ValueError("Prior hearing/event claims are not exact owner WAV/text/style bindings")
    for group in tasks.get("groups", {}).values():
        if not isinstance(group, list):
            raise ValueError("Malformed source listening task group")
        seen = set()
        for task in group:
            key = task.get("id")
            row = row_map.get(key)
            if (row is None or key in seen or task.get("wav_sha256") != row["sha256"]
                    or task.get("text") != row["text"]
                    or Path(task["audio"]).resolve() != local_path(dataset, row["audio"])
                    or task.get("intended_delivery") != {field: row[field] for field in ("emotion", "intensity", "pace", "speech_act")}):
                raise ValueError("Parent listening task has a duplicate/unbound path/hash/text/delivery")
            seen.add(key)
    jobs, binding = recheck_inputs(dataset, packet)
    recipe = read_json(second / "recheck-recipe.json")
    second_summary = read_json(second / "summary.json")
    recipe_body = {key: value for key, value in recipe.items() if key != "recipe_id"}
    wanted = {job["id"]: job for job in jobs}
    raw_path = second / "rechecks.jsonl"
    checks = indexed(json_lines(raw_path.read_bytes(), "second ASR") if raw_path.is_file() else [], "second ASR")
    if (recipe.get("schema") != "unity-source-word-recheck-recipe-v1"
            or recipe.get("recipe_id") != canonical_hash(recipe_body) or recipe.get("inputs") != binding
            or recipe.get("requested_ids") != list(wanted)
            or recipe.get("requested_wav_sha256") != {key: job["source_row"]["sha256"] for key, job in wanted.items()}
            or second_summary.get("schema") != "unity-source-word-recheck-summary-v1"
            or second_summary.get("recipe_id") != recipe["recipe_id"]
            or second_summary.get("status") != "complete_requested_subset"
            or second_summary.get("complete_requested_subset") is not True
            or second_summary.get("source_packet_status") != "complete_inventory_screen_summary"
            or second_summary.get("requested_ids") != list(wanted)
            or set(second_summary.get("completed_ids", [])) != set(wanted)
            or len(second_summary.get("completed_ids", [])) != len(wanted)
            or second_summary.get("missing_ids") != [] or set(checks) != set(wanted)
            or second_summary.get("recheck_recipe_sha256") != file_hash(second / "recheck-recipe.json")
            or second_summary.get("rechecks_sha256") != (file_hash(raw_path) if raw_path.is_file() else None)
            or second_summary.get("ignored_unpublished_tail_bytes") != 0
            or second_summary.get("deadline_reached") is not False or second_summary.get("worker_exit_code") != 0):
        raise ValueError("Second-ASR report/recipe is incomplete or bound to different inputs")
    for key, check in checks.items():
        row, scan, clip = row_map[key], scans[key], clips[key]
        target, _ = comparison_tokens(row["text"])
        transcript = check.get("second_recognized_text")
        if not isinstance(transcript, str):
            raise ValueError("Second-ASR transcript must be retained")
        actual, _ = comparison_tokens(transcript)
        previous, _ = comparison_tokens(scan["recognized_text"])
        relation = "second_matches_intended" if actual == target else "two_recognizers_agree_against_intended" if actual == previous else "recognizers_disagree_unresolved"
        if (check.get("source_row") != row or check.get("base_screening") != scan
                or check.get("audio_sha256") != row["sha256"] or check.get("audio") != row["audio"]
                or check.get("second_comparison_tokens") != actual or check.get("expected_comparison_tokens") != target
                or check.get("relation") != relation or check.get("second_word_error_rate") != word_error(target, actual)
                or any(check.get(field) != clip[field] for field in ("previous_owner_acceptance", "previous_owner_ids", "event_audibility"))
                or check.get("human_listening_acceptance") != "not_inferred"):
            raise ValueError("Second-ASR row/transcripts/source binding differs: " + key)
    if second_summary.get("relations") != dict(collections.Counter(check["relation"] for check in checks.values())):
        raise ValueError("Second-ASR relation counts differ from retained results")
    actual_flags = dict(collections.Counter(flag for scan in scans.values() for flag in scan["flags"]))
    if base_summary.get("flag_counts") != actual_flags or summary.get("original_flag_counts") != actual_flags:
        raise ValueError("Original flag inventory/counts differ from raw screening; flags are never cleared")
    artifacts = {}
    for prefix, root, names in (("base", screen, ("inspection-recipe.json", "screening.jsonl", "summary.json")),
                              ("summary", packet, ("summary.json", "clips.jsonl", "listening-tasks.json")),
                              ("second", second, ("recheck-recipe.json", "summary.json"))):
        for name in names:
            artifacts[prefix + "/" + name] = artifact(root / name)
    if raw_path.is_file():
        artifacts["second/rechecks.jsonl"] = artifact(raw_path)
    artifacts["owner/listening.json"] = artifact(owner_path)
    artifacts["owner/corpus-receipt.json"] = artifact(approval_path)
    return {"parent": parent, "clips": clips, "scans": scans, "second": checks, "tasks": tasks,
            "artifacts": artifacts, "source_summary": summary, "second_summary": second_summary}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path); parser.add_argument("out", type=Path)
    parser.add_argument("--parent-qa", nargs=4, action="append", required=True, type=Path,
                        metavar=("DATASET", "BASE_SCREEN", "SOURCE_SUMMARY", "SECOND_ASR"))
    args = parser.parse_args()
    dataset = args.dataset.resolve()
    rows, identity, provenance, mapping = load_merged(dataset)
    wanted_parents = {parent["dataset"]["dataset_id"]: parent for parent in provenance["parents"]}
    packets = {}
    for paths in args.parent_qa:
        packet = validate_packet(*[path.resolve() for path in paths])
        descriptor = packet["parent"]["descriptor"]
        key = descriptor["dataset"]["dataset_id"]
        if key not in wanted_parents or key in packets or descriptor != wanted_parents[key]:
            raise ValueError("QA must bind each exact merged parent once; no missing/extra/replaced parent")
        packets[key] = packet
    if set(packets) != set(wanted_parents):
        raise ValueError("QA lacks all merged parents")
    output, work = new_work(args.out, [dataset, *[path for paths in args.parent_qa for path in paths]], "qa-merging")
    artifacts = {}
    for number, descriptor in enumerate(provenance["parents"]):
        packet = packets[descriptor["dataset"]["dataset_id"]]
        for name, entry in packet["artifacts"].items():
            relative = "parent-qa/%03d/" % number + name
            destination = work / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(entry["path"], destination)
            if file_hash(destination) != entry["sha256"]:
                raise ValueError("Parent QA artifact changed during copy; work preserved")
            artifacts[relative] = entry["sha256"]
    records, tasks = [], collections.defaultdict(list)
    for row in rows:
        link = mapping[row["id"]]
        packet = packets[link["parent_dataset_id"]]
        clip, scan, second = packet["clips"][row["id"]], packet["scans"][row["id"]], packet["second"].get(row["id"])
        if clip["intended_source_row"] != link["source_row"] or clip["route"] != link["route"]:
            raise ValueError("Merged row provenance differs from complete parent QA")
        events = event_counts(row["text"])
        prior = clip["previous_owner_acceptance"] == "exact_previously_heard_binding"
        record = {"id": row["id"], "parent_index": link["parent_index"], "parent_dataset_id": link["parent_dataset_id"],
                  "source_row": row, "route": link["route"], "source_summary_record": clip,
                  "original_screening": scan, "second_asr": second, "events": events,
                  "original_flags": list(scan["flags"]), "supplemental_flags": list(clip["supplemental_flags"]),
                  "previous_owner_acceptance": clip["previous_owner_acceptance"], "previous_owner_ids": clip["previous_owner_ids"],
                  "event_audibility": "prior_exact_owner_acceptance" if any(events.values()) and prior else
                                      "pending_audible_review" if any(events.values()) else "no_event_requested",
                  "human_listening_inferred": False, "training_authorized": False}
        records.append(record)
        task = {"id": row["id"], "audio": str(local_path(dataset, row["audio"])), "wav_sha256": row["sha256"],
                "text": row["text"], "intended_delivery": {field: row[field] for field in ("emotion", "intensity", "pace", "speech_act")},
                "parent_dataset_id": link["parent_dataset_id"], "route": link["route"],
                "original_flags": record["original_flags"], "supplemental_flags": record["supplemental_flags"],
                "previous_owner_acceptance": record["previous_owner_acceptance"], "event_audibility": record["event_audibility"],
                "second_asr_relation": second["relation"] if second else "not_requested"}
        if scan["flags"] or clip["supplemental_flags"]:
            tasks["all_flags_preserved"].append(task)
        if second and second["relation"] != "second_matches_intended":
            tasks["second_asr_unresolved_or_agreed_against_target"].append(task)
        if any(events.values()) and not prior:
            tasks["event_audibility"].append(task)
        for group in ("asr_and_signal_outliers", "stratified_candidates"):
            if any(entry["id"] == row["id"] for entry in packet["tasks"]["groups"][group]):
                tasks[group].append(task)
    if len(records) != identity["clips"] or len({record["id"] for record in records}) != identity["clips"]:
        raise ValueError("Merged QA row inventory is incomplete")
    write_lines(work / "clips.jsonl", records)
    listening = {"schema": "unity-merged-source-listening-tasks-v1", "groups": dict(tasks),
                 "unique_ids": list(dict.fromkeys(task["id"] for group in tasks.values() for task in group)),
                 "acceptance": "not_granted; exact candidate paths/hashes only"}
    write_json(work / "listening-tasks.json", listening)
    summary = {"schema": QA_SCHEMA, "status": "complete_multi_source_qa_unaccepted",
               "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "dataset": identity,
               "merge_id": provenance["merge_id"], "merge_provenance_sha256": file_hash(dataset / "merge-provenance.json"),
               "merge_rows_sha256": file_hash(dataset / "merge-rows.jsonl"), "parents": provenance["parents"],
               "complete_parent_inventory": True, "complete_row_inventory": True, "rows": len(records),
               "original_flag_counts": dict(collections.Counter(flag for record in records for flag in record["original_flags"])),
               "supplemental_flag_counts": dict(collections.Counter(flag for record in records for flag in record["supplemental_flags"])),
               "second_asr_relations": dict(collections.Counter(record["second_asr"]["relation"] for record in records if record["second_asr"])),
               "actual_second_asr_ids": [record["id"] for record in records if record["second_asr"]],
               "previous_owner_exact_match_ids": [record["id"] for record in records if record["previous_owner_acceptance"] == "exact_previously_heard_binding"],
               "event_requested_ids": [record["id"] for record in records if any(record["events"].values())],
               "event_pending_ids": [record["id"] for record in records if record["event_audibility"] == "pending_audible_review"],
               "measured_source_hours": sum(record["original_screening"]["seconds"] for record in records) / 3600,
               "clips_sha256": file_hash(work / "clips.jsonl"), "listening_tasks_sha256": file_hash(work / "listening-tasks.json"),
               "parent_qa_evidence_sha256": artifacts,
               "code_sha256": {name: file_hash(VOICE / name) for name in
                               ("merge_source_qa.py", "merge_source_datasets.py", "summarize_source_screen.py", "recheck_source_words.py", "dataset_contract.py", "speech_text.py", "pod/atomic_publish.py")},
               "full_corpus_human_listening_inferred": False, "corpus_acceptance_granted": False,
               "source_performance_acceptance": "pending", "training_authorized": False,
               "student_training_started": False, "pod_rental_authorized": False, "deployment_authorized": False}
    write_json(work / "summary.json", dict(summary, qa_id=canonical_hash(summary)))
    for packet in packets.values():
        unchanged(packet["parent"])
        if any(file_hash(entry["path"]) != entry["sha256"] for entry in packet["artifacts"].values()):
            raise ValueError("Parent QA changed during merge; work preserved")
    if load_merged(dataset)[1] != identity:
        raise ValueError("Merged dataset changed during QA merge; work preserved")
    publish_directory(work, output)
    print(str(output / "summary.json") + " -- complete inventory, acceptance remains pending")


if __name__ == "__main__":
    main()
