"""Prepare expansion-only A2 recordings with explicitly versioned source optimizations.

This is a different immutable renderer, never a replacement for the running v3
single-recording source batch. It skips unchanged jobs from the two base corpora,
renders only new jobs, and preserves pending listening/acting status. Teachers
remain sequential. No student training, downloads, pod rental or deployment.
"""
import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import subprocess
import time
import uuid

from dataset_contract import FEATURES, canonical_hash, file_hash, load_dataset, split_for
from make_dataset import (ROOT, TEACHERS, OwnedTimeout, approved_policy, approved_profiles,
                          bounded_seconds, corpus_rows, expected_rows, lexical_group,
                          load_recipe, owned_process, pilot_rows, read_metadata,
                          route_for, teacher_inputs, word_count, write_new_json)
from speech_text import EVENT_MARKERS

DIRECTORY = Path(__file__).resolve().parent
WORKER = DIRECTORY / "source_workers_optimized.py"
LIBRARY = DIRECTORY / "make_dataset.py"
WORKER_LIBRARY = DIRECTORY / "source_workers.py"
ALGORITHM = "a2-fixed-source-groups-v1"
BASE_SPEECH = DIRECTORY / "SPEECH_CORPUS.jsonl"
BASE_EVENTS = DIRECTORY / "SPEECH_EVENT_CORPUS.jsonl"


def expansion_rows(speech, events, base_speech, base_events):
    """Expanded inputs may contain unchanged base records; those are never rendered."""
    complete = corpus_rows(speech) + corpus_rows(events, require_events=True)
    base = corpus_rows(base_speech) + corpus_rows(base_events, require_events=True)
    if len({r["id"] for r in complete}) != len(complete) or len({r["id"] for r in base}) != len(base):
        raise ValueError("Corpus IDs overlap; preserve the drafts")
    base_by_id = {r["id"]: r for r in base}
    base_groups = {lexical_group(r["text"]) for r in base}
    jobs, skipped, new_groups = [], [], set()
    for row in complete:
        if row["id"] in base_by_id:
            if row != base_by_id[row["id"]]:
                raise ValueError("Expanded input changed an existing base job: " + row["id"])
            skipped.append(row["id"])
            continue
        group = lexical_group(row["text"])
        if group in base_groups or group in new_groups:
            raise ValueError("New expansion job repeats an existing lexical group: " + row["id"])
        new_groups.add(group); jobs.append(row)
    if not jobs:
        raise ValueError("No new expansion jobs; existing WAVs must be reused through a separate merge")
    receipt = {"base_speech_sha256": file_hash(base_speech), "base_events_sha256": file_hash(base_events),
               "base_job_count": len(base), "expanded_input_count": len(complete),
               "skipped_base_ids": skipped, "new_job_count": len(jobs),
               "skip_rule": "base ID plus exact unchanged six fields; new lexical groups must be unique",
               "old_audio_rebranded": False}
    return jobs, receipt


def schedule_jobs(jobs, routes, batch_size):
    """Homogeneous Qwen references and length ordering reduce avoidable batch padding."""
    schedule = []
    profiles = sorted({r["profile"] for r in routes.values() if r["teacher"] == "qwen"})
    for profile in profiles:
        matching = [j for j in jobs if routes[j["id"]] == {"teacher": "qwen", "profile": profile}]
        matching.sort(key=lambda j: (word_count(j), len(j["text"]), j["id"]))
        for start in range(0, len(matching), batch_size):
            schedule.append({"teacher": "qwen", "profile": profile,
                             "job_ids": [j["id"] for j in matching[start:start + batch_size]]})
    # Cosy remains serial. Exact-reference/instruction caching changes preprocessing only.
    for job in jobs:
        route = routes[job["id"]]
        if route["teacher"] == "cosy":
            schedule.append({**route, "job_ids": [job["id"]]})
    return schedule


def bound_groups(source_id, schedule):
    groups = []
    for ordinal, item in enumerate(schedule):
        identity = canonical_hash({"source_id": source_id, "ordinal": ordinal, **item})
        groups.append({**item, "group_id": identity,
                       "seed": int(canonical_hash({"batch_group": identity})[:8], 16)})
    return groups


def optimization_contract(jobs, routes, batch_size):
    return {"algorithm": ALGORITHM, "qwen_batch_size": batch_size,
            "schedule": schedule_jobs(jobs, routes, batch_size),
            "qwen_grouping": "same approved reference; ascending lexical word count, characters, ID",
            "seed_policy": "one SHA-derived seed per entire immutable group, never an independent clip seed",
            "qwen_prompt_cache": "in-memory approved original/soft VoiceClonePromptItem reuse",
            "cosy_prompt_cache": "in-memory add_zero_shot_spk keyed by source ID, original reference SHA and exact instruction",
            "cosy_disk_cache_written": False, "adaptive_batch_fallback": False,
            "partial_group_resume": "refused; preserve all group outputs for explicit recovery",
            "qwen_eos_guard": "observe pinned talker.generate hidden-state first-codebook EOS before publishing any group member",
            "quality_claim": "none; fresh outputs need transcript, identity and acting review"}


def validate_optimized_plan(plan):
    renderer = plan["renderer"]
    optimization = renderer.get("optimization")
    if not isinstance(optimization, dict) or optimization.get("algorithm") != ALGORITHM:
        raise ValueError("Not this immutable optimized renderer")
    size = optimization.get("qwen_batch_size")
    if type(size) is not int or size not in (1, 2, 4):
        raise ValueError("Unsupported fixed Qwen batch size")
    if optimization != optimization_contract(plan["jobs"], plan["routes"], size):
        raise ValueError("Optimized job schedule or parameters changed")
    if plan.get("batch_groups") != bound_groups(plan["source_id"], optimization["schedule"]):
        raise ValueError("Batch group identities/seeds changed")
    actual = [job for group in plan["batch_groups"] for job in group["job_ids"]]
    if len(actual) != len(set(actual)) or set(actual) != {j["id"] for j in plan["jobs"]}:
        raise ValueError("Batch schedule omits or repeats a source job")


def benchmark_jobs(jobs, routes, teacher, count):
    """Bounded representative authoring, including both lexical splits when available."""
    matching = [j for j in jobs if routes[j["id"]]["teacher"] == teacher]
    if count > len(matching):
        raise ValueError("Benchmark limit exceeds available new jobs")
    matching.sort(key=lambda j: (word_count(j), len(j["text"]), j["id"]))
    selected, seen = [], set()
    def add(row):
        if row["id"] not in seen:
            selected.append(row); seen.add(row["id"])
    for partition in ("train", "heldout"):
        candidates = [j for j in matching if split_for(j["text"]) == partition]
        if not candidates:
            raise ValueError("Benchmark teacher lacks " + partition + " lexical groups")
        add(candidates[len(candidates) // 2])
    for route_name in sorted({routes[j["id"]].get("profile", routes[j["id"]].get("instruction")) for j in matching}):
        group = [j for j in matching if routes[j["id"]].get("profile", routes[j["id"]].get("instruction")) == route_name]
        add(group[len(group) // 2])
    if len(selected) > count:
        raise ValueError("Benchmark limit too small for route/split coverage")
    for fraction in (0, .25, .5, .75, 1):
        if len(selected) < count:
            add(matching[round((len(matching) - 1) * fraction)])
    for row in matching:
        if len(selected) == count:
            break
        add(row)
    return selected


def worker_environment(python, teacher):
    if python is None or not python.is_file():
        raise ValueError("Supply the existing isolated --%s-python" % teacher)
    output = owned_process([str(python.resolve()), str(WORKER), "--describe", teacher],
                           bounded_seconds("VOICE_SOURCE_PROBE_SECONDS", 180, 600), capture=True)
    descriptor = json.loads(output)
    if descriptor.get("schema_version") != 1 or descriptor.get("teacher") != teacher:
        raise ValueError("Wrong isolated worker descriptor")
    return descriptor


@contextmanager
def output_owner(output, recipe_id):
    """Only this invocation's lock is removed; stale locks require explicit review."""
    path = output / "source-owner.lock"
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    payload = json.dumps({"pid": os.getpid(), "recipe_id": recipe_id}, sort_keys=True)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(payload + "\n"); stream.flush(); os.fsync(stream.fileno())
        yield
    finally:
        if path.read_text(encoding="utf-8") != payload + "\n":
            raise ValueError("Owned render lock changed; preserve it")
        path.unlink()


def finish_report(output, identity, recipe_id, plan, render_seconds=None, recovered=False):
    runtime = {}
    for teacher in sorted(plan["renderer"]["teachers"]):
        path = output / ("source-" + teacher + "-runtime.json")
        receipt = json.loads(path.read_text(encoding="utf-8"))
        if receipt.get("recipe_id") != recipe_id or receipt.get("teacher") != teacher:
            raise ValueError("Missing exact worker runtime provenance")
        runtime[path.name] = file_hash(path)
    timing = output / "source-timing.jsonl"
    raw = timing.read_text(encoding="utf-8")
    if not raw.endswith("\n"):
        raise ValueError("Torn source timing; preserve for explicit recovery")
    records = [json.loads(line) for line in raw.splitlines()]
    if ([r.get("group_id") for r in records] != [g["group_id"] for g in plan["batch_groups"]]
            or any(r.get("recipe_id") != recipe_id for r in records)):
        raise ValueError("Incomplete/mismatched optimization timing inventory")
    body = {"schema_version": 3, "dataset": identity, "recipe_id": recipe_id, "scope": plan["scope"],
            "runtime_sha256": runtime, "optimization_id": canonical_hash(plan["renderer"]["optimization"]),
            "timing_sha256": file_hash(timing), "render_seconds": render_seconds,
            "completion": "recovered_exact_complete_metadata" if recovered else "rendered_complete",
            "audio_acceptance": "pending", "event_performance_acceptance": "pending",
            "student_training_started": False, "old_audio_rebranded": False}
    path = output / "source-build.json"
    if path.exists():
        saved = json.loads(path.read_text(encoding="utf-8"))
        for key in body.keys() - {"render_seconds", "completion"}:
            if saved.get(key) != body[key]:
                raise ValueError("Existing source-build report differs; preserve it")
    else:
        write_new_json(path, body)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out", type=Path)
    parser.add_argument("--corpus", type=Path, default=DIRECTORY / "SPEECH_CORPUS_EXPANDED.jsonl")
    parser.add_argument("--event-corpus", type=Path, default=DIRECTORY / "SPEECH_EVENT_CORPUS_EXPANDED.jsonl")
    parser.add_argument("--base-corpus", type=Path, default=BASE_SPEECH)
    parser.add_argument("--base-event-corpus", type=Path, default=BASE_EVENTS)
    parser.add_argument("--model-dir", type=Path)
    parser.add_argument("--qwen-python", type=Path)
    parser.add_argument("--cosy-python", type=Path)
    parser.add_argument("--cosy-code-dir", type=Path)
    parser.add_argument("--cosy-model-dir", type=Path)
    parser.add_argument("--qwen-batch-size", type=int, choices=(1, 2, 4), default=2)
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--all", action="store_true")
    scope.add_argument("--limit", type=int, default=32)
    scope.add_argument("--benchmark-limit", type=int)
    parser.add_argument("--benchmark-teacher", choices=("qwen", "cosy"))
    parser.add_argument("--plan-only", action="store_true", help="Freeze recipe after metadata/model-file inspection; no GPU/model load")
    args = parser.parse_args()
    args.out = args.out.resolve()
    if not args.out.is_relative_to((ROOT / ".local/voice-lab").resolve()):
        raise ValueError("Local authoring output must remain inside .local/voice-lab")
    if args.out.exists() and (any(args.out.glob("source-*-timeout.json")) or any(args.out.glob("source-*-failure-*.json"))):
        raise ValueError("Failed batch requires explicit review; preserve it and choose a fresh directory")
    if args.benchmark_limit is not None and (args.benchmark_teacher is None or not 4 <= args.benchmark_limit <= 64):
        raise ValueError("Bounded benchmark needs --benchmark-teacher and --benchmark-limit 4..64")
    if args.benchmark_teacher and args.benchmark_limit is None:
        raise ValueError("--benchmark-teacher requires the explicit bounded limit")
    if not args.all and args.benchmark_limit is None and not 24 <= args.limit <= 5000:
        raise ValueError("Pilot limit must be 24..5000")
    selection_path = DIRECTORY / "SELECTED_VOICE.json"
    acceptance_path = DIRECTORY / "receipts/source-auditions.json"
    selected = json.loads(selection_path.read_text(encoding="utf-8"))
    acceptance = json.loads(acceptance_path.read_text(encoding="utf-8"))
    gate = json.loads((DIRECTORY / "VOICE_QUALITY_GATE.json").read_text(encoding="utf-8"))
    source_check = gate["checks"]["source_auditions"]
    if (acceptance.get("decision") != "accepted" or acceptance.get("accepted_by") != "owner"
            or acceptance.get("voice_id") != selected["voice_id"] or source_check.get("accepted") is not True
            or source_check.get("receipt") != "training/voice/receipts/source-auditions.json"
            or source_check.get("receipt_sha256") != file_hash(acceptance_path)):
        raise ValueError("Original A2 source approval is not the accepted identity-bound receipt")
    profiles, profile_path = approved_profiles(selected, acceptance)
    policy, policy_path = approved_policy(selected, acceptance)
    additions, excluded = expansion_rows(args.corpus, args.event_corpus, args.base_corpus, args.base_event_corpus)
    routes_all = {j["id"]: route_for(j, policy, profiles) for j in additions}
    jobs = (benchmark_jobs(additions, routes_all, args.benchmark_teacher, args.benchmark_limit)
            if args.benchmark_limit is not None else additions if args.all else pilot_rows(additions, args.limit))
    routes = {j["id"]: routes_all[j["id"]] for j in jobs}
    used = {r["teacher"] for r in routes.values()}
    directories = {"qwen": args.model_dir, "cosy": args.cosy_model_dir}
    interpreters = {"qwen": args.qwen_python, "cosy": args.cosy_python}
    if any(directories[name] is None for name in used) or ("cosy" in used and args.cosy_code_dir is None):
        raise ValueError("Each used teacher needs its pinned local model/code directories")
    teachers = {name: {"inputs": teacher_inputs(name, directories[name], args.cosy_code_dir if name == "cosy" else None),
                       "environment": worker_environment(interpreters[name], name)} for name in sorted(used)}
    renderer = {"schema_version": 3, "teachers": teachers, "voice_id": selected["voice_id"],
                "selected_config": selected, "selected_config_sha256": file_hash(selection_path),
                "reference_profiles": profiles, "reference_profiles_sha256": file_hash(profile_path),
                "source_delivery_policy": policy, "source_delivery_policy_sha256": file_hash(policy_path),
                "approval_receipt": acceptance, "approval_receipt_sha256": file_hash(acceptance_path),
                "builder_sha256": file_hash(Path(__file__)), "worker_sha256": file_hash(WORKER),
                "builder_library_sha256": file_hash(LIBRARY), "worker_library_sha256": file_hash(WORKER_LIBRARY),
                "contract_sha256": file_hash(DIRECTORY / "dataset_contract.py"),
                "speech_text_sha256": file_hash(DIRECTORY / "speech_text.py"),
                "event_vocabulary": EVENT_MARKERS,
                "features": FEATURES,
                "seed_policy": "one fixed seed per entire recorded batch group; sequential teacher processes",
                "generation": {"qwen": {"max_new_tokens": 600, "temperature": .75, "top_p": .9,
                                           "do_sample": True, "language": "English", "non_streaming_mode": True,
                                           "x_vector_only_mode": False, "dtype": "bfloat16", "attention": "sdpa"},
                               "cosy": {"fp16": True, "load_trt": False, "load_vllm": False, "stream": False,
                                        "speed": 1.0, "text_frontend": False, "onnx_providers": ["CPUExecutionProvider"]}},
                "optimization": optimization_contract(jobs, routes, args.qwen_batch_size),
                "delivery_status": "intended labels and events remain pending audible performance/transcript review"}
    plan = {"renderer": renderer, "source_id": canonical_hash(renderer),
            "corpora_sha256": {"speech": file_hash(args.corpus), "events": file_hash(args.event_corpus)},
            "excluded_base": excluded, "scope": "optimization-benchmark" if args.benchmark_limit is not None else "expansion-full-draft" if args.all else "expansion-pilot",
            "jobs": jobs, "routes": routes, "audio_acceptance": "pending", "training_authorized": False}
    plan["batch_groups"] = bound_groups(plan["source_id"], renderer["optimization"]["schedule"])
    validate_optimized_plan(plan)
    recipe_id = canonical_hash(plan)
    args.out.mkdir(parents=True, exist_ok=True)
    recipe_file = args.out / "render-recipe.json"
    if recipe_file.exists():
        if json.loads(recipe_file.read_text(encoding="utf-8")) != dict(plan, recipe_id=recipe_id):
            raise ValueError("Output belongs to another immutable optimized recipe")
    elif any(args.out.iterdir()):
        raise ValueError("Nonempty unbound output is preserved")
    else:
        write_new_json(recipe_file, dict(plan, recipe_id=recipe_id))
    (args.out / "wavs").mkdir(exist_ok=True)
    if args.plan_only:
        print(json.dumps({"recipe_id": recipe_id, "source_id": plan["source_id"], "jobs": len(jobs),
                          "skipped_base": len(excluded["skipped_base_ids"]), "model_loaded": False}), flush=True)
        return
    with output_owner(args.out, recipe_id):
        expected = expected_rows(plan)
        done = read_metadata(args.out, expected)
        if set(done) == set(expected):
            _, identity = load_dataset(args.out)
            finish_report(args.out, identity, recipe_id, plan, recovered=True)
            return
        started = time.monotonic()
        for teacher in ("qwen", "cosy"):
            remaining = [job for job in jobs if routes[job["id"]]["teacher"] == teacher
                         and ("a2-" + canonical_hash({"source": plan["source_id"], "job": job,
                                                     "route": routes[job["id"]]})[:24]) not in done]
            if teacher not in used or not remaining:
                continue
            command = [str(interpreters[teacher].resolve()), str(WORKER), "--teacher", teacher,
                       "--recipe", str(recipe_file), "--model-dir", str(directories[teacher].resolve())]
            if teacher == "cosy":
                command += ["--code-dir", str(args.cosy_code_dir.resolve())]
            seconds = bounded_seconds("VOICE_SOURCE_SETUP_SECONDS", 180, 1800) + bounded_seconds("VOICE_SOURCE_CLIP_SECONDS", 300, 1800) * len(remaining)
            if seconds > 7 * 24 * 3600:
                raise ValueError("Worker walltime exceeds seven days; reduce limits/scope")
            try:
                owned_process(command, seconds)
            except OwnedTimeout as error:
                write_new_json(args.out / ("source-" + teacher + "-timeout.json"),
                               {"schema_version": 1, "recipe_id": recipe_id, "teacher": teacher,
                                "owned_child_pid": error.pid, "wall_timeout_seconds": error.seconds,
                                "termination": error.termination, "student_training_started": False,
                                "recovery": "preserve partial group; explicit review and fresh folder"})
                raise
            except subprocess.CalledProcessError as error:
                write_new_json(args.out / ("source-" + teacher + "-failure-" + uuid.uuid4().hex + ".json"),
                               {"schema_version": 1, "recipe_id": recipe_id, "teacher": teacher,
                                "worker_exit_code": error.returncode, "student_training_started": False,
                                "recovery": "preserve outputs and console diagnostic; explicit review and fresh folder"})
                raise
            done = read_metadata(args.out, expected)
        exact, identity = load_dataset(args.out)
        if set(done) != set(expected) or len(exact) != len(jobs):
            raise ValueError("Incomplete/extra source records; preserve batch")
        finish_report(args.out, identity, recipe_id, plan, time.monotonic() - started)
    print("Expansion source built; transcript/acting acceptance pending, student training prohibited.", flush=True)


if __name__ == "__main__":
    main()
