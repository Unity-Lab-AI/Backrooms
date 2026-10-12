"""Merge complete schema-3 source datasets without re-rendering or accepting audio.

python training/voice/merge_source_datasets.py NEW_OUT --parent SEED --parent EXTRAS --minimum-clips 5000
Standard library only. Parent WAV bytes, row IDs and source IDs are preserved.
No fabricated merged render-recipe, approvals, training, services or cleanup.
"""
import argparse
import collections
import datetime
import json
import os
from pathlib import Path
import re
import shutil
import uuid
import wave

from dataset_contract import (FEATURES, canonical_hash, delivery, file_hash, load_dataset,
                              local_path, normalize_transcript)
from make_dataset import FIELDS, TEACHERS, expected_rows, load_recipe, read_metadata, route_for
from pod.atomic_publish import publish_directory
from speech_text import event_only_group

VOICE = Path(__file__).resolve().parent
MERGE_SCHEMA = "unity-multi-source-merge-v1"
HASH = re.compile(r"[0-9a-f]{64}")
SEED_SOURCE = "8abb75d3e26e8036311731861e5333f1cdaf0fe5f4044385716e4cfe56473798"
SEED_DUPLICATE = {"speech_40b93d87ee480f529324", "event_c902830ce8352bb49922"}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
        stream.flush(); os.fsync(stream.fileno())


def write_lines(path, values):
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        for value in values:
            stream.write(json.dumps(value, ensure_ascii=False, allow_nan=False) + "\n")
        stream.flush(); os.fsync(stream.fileno())


def indexed(rows, label):
    result = {}
    for row in rows:
        key = row.get("id")
        if not isinstance(key, str) or key in result:
            raise ValueError("Duplicate/missing ID in " + label)
        result[key] = row
    return result


def hash_map(value, label):
    if (not isinstance(value, dict) or not value
            or any(not isinstance(name, str) or not name or not isinstance(sha, str)
                   or HASH.fullmatch(sha) is None for name, sha in value.items())):
        raise ValueError("Invalid recorded file hashes: " + label)


def code_bindings(renderer):
    optimized = "optimization" in renderer
    names = {"builder_sha256": "make_dataset_optimized.py" if optimized else "make_dataset.py",
             "worker_sha256": "source_workers_optimized.py" if optimized else "source_workers.py",
             "contract_sha256": "dataset_contract.py", "speech_text_sha256": "speech_text.py"}
    if optimized:
        names.update(builder_library_sha256="make_dataset.py", worker_library_sha256="source_workers.py")
    bindings = {}
    for field, name in names.items():
        path = VOICE / name
        if not path.is_file() or renderer.get(field) != file_hash(path):
            raise ValueError("Current recorded renderer code missing/changed: " + name + "; preserve source evidence")
        bindings[name] = file_hash(path)
    return bindings


def verify_parent(directory):
    """Read exact completed parent source contracts; never loads teachers or imports them."""
    directory = Path(directory).resolve()
    if (not directory.is_dir() or any(directory.glob("source-*-timeout.json"))
            or any(directory.glob("source-*-failure-*.json"))):
        raise ValueError("Parent must be a completed source directory without timeout evidence")
    plan, recipe_id = load_recipe(directory / "render-recipe.json")
    renderer = plan["renderer"]
    bindings = code_bindings(renderer)
    if renderer.get("features") != FEATURES:
        raise ValueError("Parent recorded a different shared source/audio frontend")
    jobs = indexed(plan["jobs"], "parent jobs")
    if not jobs or set(plan["routes"]) != set(jobs):
        raise ValueError("Parent jobs/routes differ")
    used = set()
    for job in jobs.values():
        if set(job) != FIELDS:
            raise ValueError("Parent jobs require the exact six corpus fields")
        delivery(job["emotion"], job["intensity"], job["pace"], job["speech_act"])
        route = plan["routes"][job["id"]]
        if route != route_for(job, renderer["source_delivery_policy"], renderer["reference_profiles"]):
            raise ValueError("Parent job route differs from its recorded approved source policy")
        used.add(route["teacher"])
    if set(renderer["teachers"]) != used:
        raise ValueError("Parent teacher inventory differs from actual job routes")
    for teacher, item in renderer["teachers"].items():
        inputs = item["inputs"]
        if any(inputs.get(key) != value for key, value in TEACHERS[teacher].items()):
            raise ValueError("Parent teacher repo/revision differs from the reviewed source")
        hash_map(inputs.get("model_files_sha256"), teacher + " model")
        if (inputs.get("source_record", {}).get("repo"), inputs.get("source_record", {}).get("revision")) != (inputs["repo"], inputs["revision"]):
            raise ValueError("Parent teacher source record differs")
        if not isinstance(item.get("environment"), dict) or item["environment"].get("teacher") != teacher:
            raise ValueError("Parent lacks teacher environment provenance")
        if teacher == "cosy":
            hash_map(inputs.get("code_files_sha256"), "Cosy code")
            hash_map(inputs.get("matcha_files_sha256"), "Matcha code")
    expected = expected_rows(plan)
    done = read_metadata(directory, expected)
    rows, identity = load_dataset(directory)
    if set(done) != set(expected) or indexed(rows, "parent metadata") != done:
        raise ValueError("Parent source metadata is incomplete or differs from exact planned jobs")
    actual_wavs = {path.relative_to(directory).as_posix() for path in (directory / "wavs").rglob("*.wav")}
    if actual_wavs != {row["audio"] for row in rows}:
        raise ValueError("Parent WAV inventory has orphan/missing files; no cleanup is performed")
    wav_durations = {}
    for row in rows:
        with wave.open(str(local_path(directory, row["audio"])), "rb") as audio:
            if (audio.getnchannels(), audio.getsampwidth(), audio.getframerate(), audio.getcomptype()) != (1, 2, 24000, "NONE"):
                raise ValueError("Parent WAV is not mono PCM16/24000Hz: " + row["id"])
            if not FEATURES["min_seconds"] <= audio.getnframes() / 24000 <= FEATURES["max_seconds"]:
                raise ValueError("Parent WAV duration is outside source bounds: " + row["id"])
            wav_durations[row["id"]] = audio.getnframes() / 24000
    build = read_json(directory / "source-build.json")
    if (build.get("schema_version") != 3 or build.get("dataset") != identity
            or build.get("recipe_id") != recipe_id or build.get("scope") != plan["scope"]
            or build.get("completion") not in ("rendered_complete", "recovered_exact_complete_metadata")
            or build.get("student_training_started") is not False):
        raise ValueError("Parent source-build report is not an exact complete source-only result")
    artifacts = {name: file_hash(directory / name) for name in ("metadata.jsonl", "render-recipe.json", "source-build.json")}
    runtime, runtime_records = {}, {}
    for teacher in sorted(used):
        name = "source-" + teacher + "-runtime.json"
        receipt = read_json(directory / name)
        # Both pinned workers return the full teacher inputs/environment record.
        # The existing 8abb runtime receipt confirms this exact binding.
        descriptor_input = renderer["teachers"][teacher]
        if (receipt.get("schema_version") != 1 or receipt.get("recipe_id") != recipe_id
                or receipt.get("teacher") != teacher
                or receipt.get("descriptor_id") != canonical_hash(descriptor_input)
                or receipt.get("student_training_started") is not False):
            raise ValueError("Parent runtime receipt differs from its exact teacher/recipe/environment")
        runtime[name] = file_hash(directory / name)
        runtime_records[teacher] = receipt
    if build.get("runtime_sha256") != runtime:
        raise ValueError("Parent source-build runtime inventory/hash differs")
    artifacts.update(runtime)
    if "optimization" in renderer:
        from make_dataset_optimized import validate_optimized_plan
        from source_workers_optimized import read_timing
        validate_optimized_plan(plan)
        optimization_id = canonical_hash(renderer["optimization"])
        if (build.get("optimization_id") != optimization_id or build.get("old_audio_rebranded") is not False
                or any(receipt.get("optimization_id") != optimization_id
                       or receipt.get("cosy_model_directory_written") is not False
                       for receipt in runtime_records.values())):
            raise ValueError("Optimized report differs from recorded optimization identity")
        timing = directory / "source-timing.jsonl"
        if not timing.is_file() or build.get("timing_sha256") != file_hash(timing):
            raise ValueError("Optimized timing artifact is missing/changed")
        artifacts[timing.name] = file_hash(timing)
        timings = read_timing(directory, plan, recipe_id)
        if list(timings) != [group["group_id"] for group in plan["batch_groups"]]:
            raise ValueError("Optimized timing journal lacks exact ordered complete batch groups")
        for group in plan["batch_groups"]:
            record = timings[group["group_id"]]
            if any(record.get(field) != value for field, value in group.items()):
                raise ValueError("Optimized timing route/profile differs from its group")
            duration_values = record.get("audio_seconds")
            if (not isinstance(duration_values, list) or len(duration_values) != len(group["job_ids"])
                    or any(isinstance(value, bool) or not isinstance(value, (int, float))
                           or not FEATURES["min_seconds"] <= value <= FEATURES["max_seconds"] for value in duration_values)):
                raise ValueError("Optimized timing audio inventory differs")
            if group["teacher"] == "qwen":
                if record.get("qwen_completion", {}).get("eos_present") != [True] * len(group["job_ids"]):
                    raise ValueError("Optimized Qwen timing lacks per-item EOS completion evidence")
    routes = {key: plan["routes"][job["id"]] for job in jobs.values()
              for key in ["a2-" + canonical_hash({"source": plan["source_id"], "job": job,
                                                "route": plan["routes"][job["id"]]})[:24]]}
    job_ids = {key: job["id"] for job in jobs.values()
               for key in ["a2-" + canonical_hash({"source": plan["source_id"], "job": job,
                                                 "route": plan["routes"][job["id"]]})[:24]]}
    descriptor = {"directory": str(directory), "dataset": identity, "source_id": plan["source_id"],
                  "recipe_id": recipe_id, "artifacts_sha256": artifacts, "renderer_code_sha256": bindings}
    return {"descriptor": descriptor, "rows": rows, "routes": routes, "job_ids": job_ids, "durations": wav_durations}


def unchanged(parent):
    descriptor = parent["descriptor"]
    root = Path(descriptor["directory"])
    if any(file_hash(root / name) != sha for name, sha in descriptor["artifacts_sha256"].items()):
        raise ValueError("Parent artifact changed during merge; partial work preserved")


def new_work(output, inputs, label):
    if Path(output).is_symlink():
        raise ValueError("Output must not be a symlink")
    output = Path(output).resolve()
    if output.exists() or any(output.is_relative_to(Path(root).resolve()) for root in inputs):
        raise ValueError("Use a NEW output outside immutable inputs")
    output.parent.mkdir(parents=True, exist_ok=True)
    work = output.with_name(output.name + "." + label + "-" + uuid.uuid4().hex)
    work.mkdir(exist_ok=False)
    return output, work


def load_merged(directory):
    directory = Path(directory).resolve()
    provenance = read_json(directory / "merge-provenance.json")
    body = {key: value for key, value in provenance.items() if key != "merge_id"}
    rows, identity = load_dataset(directory)
    if (provenance.get("schema") != MERGE_SCHEMA or provenance.get("merge_id") != canonical_hash(body)
            or provenance.get("dataset") != identity or provenance.get("audio_bytes_changed") is not False
            or provenance.get("training_authorized") is not False):
        raise ValueError("Merged dataset/provenance identity differs")
    records = [json.loads(line) for line in (directory / "merge-rows.jsonl").read_text(encoding="utf-8").splitlines()]
    if file_hash(directory / "merge-rows.jsonl") != provenance.get("rows_sha256"):
        raise ValueError("Merged source-row provenance changed")
    mapping = indexed(records, "merged provenance rows")
    if set(mapping) != {row["id"] for row in rows}:
        raise ValueError("Merged source-row provenance lacks complete inventory")
    parents = provenance["parents"]
    if len({parent["dataset"]["dataset_id"] for parent in parents}) != len(parents):
        raise ValueError("Merged parents are duplicated")
    for row in rows:
        record = mapping[row["id"]]
        number = record.get("parent_index")
        if (type(number) is not int or not 0 <= number < len(parents) or record.get("source_row") != row
                or record.get("parent_dataset_id") != parents[number]["dataset"]["dataset_id"]):
            raise ValueError("Merged row differs from original source binding")
    for name, sha in provenance["evidence_sha256"].items():
        if file_hash(local_path(directory, name)) != sha:
            raise ValueError("Merged parent evidence missing/changed")
    return rows, identity, provenance, mapping


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out", type=Path)
    parser.add_argument("--parent", type=Path, action="append", required=True)
    parser.add_argument("--minimum-clips", type=int, default=5000)
    args = parser.parse_args()
    if len(args.parent) < 2 or not 1 <= args.minimum_clips <= 100000:
        raise ValueError("Provide at least two distinct complete parents and minimum-clips 1..100000")
    if len({path.resolve() for path in args.parent}) != len(args.parent):
        raise ValueError("Repeated parent directory")
    parents = [verify_parent(path) for path in args.parent]
    if len({parent["descriptor"]["dataset"]["voice_id"] for parent in parents}) != 1:
        raise ValueError("All parents must preserve one selected voice identity")
    rows, records, ids, job_ids, groups = [], [], set(), set(), {}
    allowed = []
    for number, parent in enumerate(parents):
        own_groups = collections.defaultdict(list)
        for row in parent["rows"]:
            key, job_id = row["id"], parent["job_ids"][row["id"]]
            group = normalize_transcript(row["text"]) or event_only_group(row["text"])
            if key in ids or job_id in job_ids or group in groups:
                raise ValueError("Added source duplicates an existing ID/job/lexical group: " + key)
            ids.add(key); job_ids.add(job_id); own_groups[group].append(job_id)
            rows.append(row)
            records.append({"id": key, "parent_index": number, "parent_dataset_id": parent["descriptor"]["dataset"]["dataset_id"],
                            "job_id": job_id, "source_row": row, "route": parent["routes"][key]})
        for group, members in own_groups.items():
            if len(members) > 1:
                if not (number == 0 and parent["descriptor"]["source_id"] == SEED_SOURCE and set(members) == SEED_DUPLICATE):
                    raise ValueError("Unapproved duplicate lexical group inside parent")
                allowed.append({"parent_index": number, "lexical_group": group, "job_ids": sorted(members),
                                "reason": "Historical seed question and explicit laughter variant remain one grouped split"})
            groups[group] = number
    if len(rows) < args.minimum_clips:
        raise ValueError("Complete merged inventory is below explicit minimum-clips")
    output, work = new_work(args.out, args.parent, "merging")
    evidence = {}
    for number, parent in enumerate(parents):
        root = Path(parent["descriptor"]["directory"])
        for name, sha in parent["descriptor"]["artifacts_sha256"].items():
            relative = "parent-evidence/%03d/" % number + name
            target = work / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / name, target)
            if file_hash(target) != sha:
                raise ValueError("Copied parent artifact changed; work preserved")
            evidence[relative] = sha
        for row in parent["rows"]:
            target = local_path(work, row["audio"])
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                raise ValueError("Merged WAV path appeared concurrently")
            with local_path(root, row["audio"]).open("rb") as source, target.open("xb") as destination:
                shutil.copyfileobj(source, destination)
                destination.flush(); os.fsync(destination.fileno())
            if file_hash(target) != row["sha256"]:
                raise ValueError("Copied WAV differs from unchanged parent bytes; work preserved")
        unchanged(parent)
    write_lines(work / "metadata.jsonl", rows)
    write_lines(work / "merge-rows.jsonl", records)
    _, identity = load_dataset(work)
    body = {"schema": MERGE_SCHEMA, "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "dataset": identity, "parents": [parent["descriptor"] for parent in parents],
            "rows_sha256": file_hash(work / "merge-rows.jsonl"), "evidence_sha256": evidence,
            "allowed_seed_lexical_duplicates": allowed, "minimum_clips": args.minimum_clips,
            "merge_code_sha256": file_hash(Path(__file__)), "atomic_publish_sha256": file_hash(VOICE / "pod/atomic_publish.py"),
            "audio_bytes_changed": False, "original_source_ids_preserved": True,
            "audio_acceptance": "pending", "full_corpus_human_listening_inferred": False,
            "training_authorized": False, "student_training_started": False, "pod_rental_authorized": False}
    write_json(work / "merge-provenance.json", dict(body, merge_id=canonical_hash(body)))
    load_merged(work)
    for parent in parents:
        unchanged(parent)
    publish_directory(work, output)
    print(json.dumps({"status": "complete_unchanged_multi_source_candidate_unaccepted", "dataset": identity,
                      "out": str(output), "training_authorized": False}, indent=2))


if __name__ == "__main__":
    main()
