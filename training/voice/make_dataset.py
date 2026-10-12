"""Render a fresh, pending-review v2 source dataset with the approved mixed A2 recipe.

The orchestrator uses only the standard library. Separate --qwen-python and
--cosy-python workers preserve the reviewed environments and run sequentially.
Default: balanced 32-clip pilot including performed-event requests; --all is explicit.
No training, deployment, automatic download, pitch shift or time stretch is performed.
Historical batches, reports, orphan WAVs and torn metadata are never replaced.
"""
import argparse
import collections
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time
import uuid

from dataset_contract import (DATASET_SCHEMA, EMOTIONS, SPEECH_ACTS, FEATURES, canonical_hash,
                              delivery, file_hash, load_dataset, local_path, normalize_transcript, split_for)
from speech_text import EVENT_MARKERS, event_counts, event_only_group

ROOT = Path(__file__).resolve().parents[2]
FIELDS = {"id", "text", "emotion", "intensity", "pace", "speech_act"}
QUESTIONS = {"yes_no_question", "wh_question"}
TEACHERS = {
    "qwen": {"repo": "Qwen/Qwen3-TTS-12Hz-1.7B-Base", "revision": "fd4b254389122332181a7c3db7f27e918eec64e3"},
    "cosy": {"repo": "FunAudioLLM/Fun-CosyVoice3-0.5B-2512", "revision": "29e01c4e8d000f4bcd70751be16fa94bf3d85a18",
             "code_commit": "074ca6dc9e80a2f424f1f74b48bdd7d3fea531cc"},
}
WORKER = Path(__file__).with_name("source_workers.py")


class OwnedTimeout(RuntimeError):
    def __init__(self, pid, seconds, termination):
        super().__init__("Owned source subprocess timed out after %ds (PID %d; %s); preserve the batch" % (seconds, pid, termination))
        self.pid, self.seconds, self.termination = pid, seconds, termination


def bounded_seconds(name, default, maximum):
    text = os.environ.get(name, str(default))
    if not re.fullmatch(r"[0-9]+", text) or not 1 <= int(text) <= maximum:
        raise ValueError("%s must be whole seconds in 1..%d" % (name, maximum))
    return int(text)


def owned_process(command, seconds, capture=False):
    """A bounded, shell-free child; timeout terminates only its owned process tree/group."""
    environment = dict(os.environ, HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1",
                       PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    options = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
    process = subprocess.Popen(command, cwd=str(ROOT), env=environment, text=True, encoding="utf-8",
        stdout=subprocess.PIPE if capture else None, stderr=subprocess.PIPE if capture else None, **options)
    try:
        stdout, stderr = process.communicate(timeout=seconds)
    except subprocess.TimeoutExpired:
        termination = "termination requested"
        try:
            if os.name == "nt":
                result = subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                                        capture_output=True, timeout=20, check=False)
                termination = "owned Windows tree killed" if result.returncode == 0 else "tree kill failed; direct kill requested"
                if result.returncode != 0 and process.poll() is None:
                    process.kill()
            else:
                os.killpg(process.pid, signal.SIGKILL)
                termination = "owned process group killed"
            process.communicate(timeout=20)
        except (OSError, subprocess.TimeoutExpired):
            if process.poll() is None:
                process.kill()
            termination += "; confirm exit before another source render"
        raise OwnedTimeout(process.pid, seconds, termination) from None
    if process.returncode:
        raise subprocess.CalledProcessError(process.returncode, command, output=stdout, stderr=stderr)
    return stdout


def lexical_group(text):
    return normalize_transcript(text) or event_only_group(text)


def word_count(row):
    return len(normalize_transcript(row["text"]).split())


def corpus_rows(path, require_events=False):
    rows, ids = [], set()
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        row = json.loads(line)
        if (not isinstance(row, dict) or set(row) != FIELDS or not isinstance(row["id"], str)
                or not re.fullmatch(r"[A-Za-z0-9_-]{1,96}", row["id"]) or row["id"] in ids
                or not isinstance(row["text"], str) or len(row["text"]) > 4000 or not lexical_group(row["text"])):
            raise ValueError("Invalid/duplicate exact six-field corpus entry: %s:%d" % (path, number))
        delivery(row["emotion"], row["intensity"], row["pace"], row["speech_act"])
        if row["pace"] != 1.0:
            raise ValueError("This source recipe uses natural speed 1.0; unverified pace labels are refused")
        if require_events and not any(event_counts(row["text"]).values()):
            raise ValueError("Event corpus row has no supported performed-event request: " + row["id"])
        ids.add(row["id"]); rows.append(row)
    if not rows:
        raise ValueError("Empty speech corpus: " + str(path))
    return rows


def pilot_rows(rows, limit):
    """Nine connected states, questions, all acts, both lexical splits, short turns and events."""
    chosen, seen = [], set()
    order = {row["id"]: index for index, row in enumerate(rows)}
    nonquestions = [act for act in SPEECH_ACTS if act not in QUESTIONS]

    def choose(candidates, preferred_act=None):
        available = [row for row in candidates if row["id"] not in seen]
        if not available:
            return None
        have_heldout = any(split_for(row["text"]) == "heldout" for row in chosen)
        represented = {row["speech_act"] for row in chosen}
        available.sort(key=lambda row: (
            not have_heldout and split_for(row["text"]) != "heldout",
            preferred_act is not None and row["speech_act"] != preferred_act,
            row["speech_act"] in represented, order[row["id"]]))
        row = available[0]
        chosen.append(row); seen.add(row["id"])
        return row

    # Two distinct TRAIN lexical groups give the event embedding actual training inputs.
    # The labels are requests until listening confirms audible laughter in each clip.
    event_groups = set()
    for _ in range(2):
        event = choose([row for row in rows if event_counts(row["text"])["laughter"] > 0
                        and split_for(row["text"]) == "train" and lexical_group(row["text"]) not in event_groups])
        if event is None:
            raise ValueError("Corpus needs two distinct TRAIN laughter-marked utterances")
        event_groups.add(lexical_group(event["text"]))
    held_events = [row for row in rows if any(event_counts(row["text"]).values()) and split_for(row["text"]) == "heldout"]
    if held_events:
        choose(held_events)
    for index, emotion in enumerate(EMOTIONS):
        candidates = [row for row in rows if row["emotion"] == emotion and word_count(row) >= 6]
        if not candidates:
            raise ValueError("Corpus lacks connected speech for " + emotion)
        plain = [row for row in candidates if not any(event_counts(row["text"]).values())]
        candidates = plain or candidates
        choose([row for row in candidates if row["speech_act"] not in QUESTIONS] or candidates,
               nonquestions[index % len(nonquestions)])
    for index, emotion in enumerate(EMOTIONS):
        candidates = [row for row in rows if row["emotion"] == emotion and row["speech_act"] in QUESTIONS]
        if candidates and not any(row["emotion"] == emotion and row["speech_act"] in QUESTIONS for row in chosen):
            connected = [row for row in candidates if word_count(row) >= 6]
            choose(connected or candidates, "yes_no_question" if index % 2 == 0 else "wh_question")
    for act in SPEECH_ACTS:
        if not any(row["speech_act"] == act for row in chosen):
            if choose([row for row in rows if row["speech_act"] == act]) is None:
                raise ValueError("Corpus lacks speech act " + act)
    for partition in ("train", "heldout"):
        if not any(split_for(row["text"]) == partition for row in chosen):
            if choose([row for row in rows if split_for(row["text"]) == partition]) is None:
                raise ValueError("Corpus lacks " + partition + " transcript groups")
    while sum(0 < word_count(row) <= 3 and row["speech_act"] not in QUESTIONS for row in chosen) < 2:
        short = [row for row in rows if 0 < word_count(row) <= 3 and row["speech_act"] not in QUESTIONS]
        familiar = [row for row in short if row["emotion"] in ("neutral", "warm")]
        if choose(familiar or short) is None:
            raise ValueError("Corpus lacks two distinct short lexical turns")
    if len(chosen) > limit:
        raise ValueError("Pilot limit too small for event/state/question/act/split/short-turn coverage")
    while len(chosen) < limit:
        counts = collections.Counter(row["emotion"] for row in chosen)
        candidates = [row for row in rows if row["id"] not in seen]
        if not candidates:
            break
        least = min(counts[row["emotion"]] for row in candidates)
        balanced = [row for row in candidates if counts[row["emotion"]] == least]
        connected = [row for row in balanced if word_count(row) >= 6]
        choose(connected or balanced)
    return chosen


def approved_profiles(selected, acceptance):
    profile_path = local_path(ROOT, selected["delivery_profiles"])
    if file_hash(profile_path) != selected["delivery_profiles_sha256"]:
        raise ValueError("Approved reference profile configuration changed")
    config = json.loads(profile_path.read_text(encoding="utf-8"))
    if config.get("schema_version") != 1 or config.get("voice_id") != selected["voice_id"]:
        raise ValueError("Reference profile schema or voice identity mismatch")
    profiles = config["profiles"]
    if set(profiles) != {"original", "everyday", "playful", "soft", "questions"}:
        raise ValueError("Expected the five reviewed A2 reference performances")
    evidence = {}
    for entry in acceptance["evidence"]:
        if entry["path"] in evidence and evidence[entry["path"]] != entry["sha256"]:
            raise ValueError("Conflicting reference approval evidence")
        evidence[entry["path"]] = entry["sha256"]
    for name, profile in profiles.items():
        if not isinstance(profile.get("text"), str) or not profile["text"].strip():
            raise ValueError("Missing exact reference transcript: " + name)
        for audio, digest in (("audio", "sha256"), ("listening_audio", "listening_sha256")):
            relative, expected = profile[audio], profile[digest]
            if evidence.get(relative) != expected or file_hash(local_path(ROOT, relative)) != expected:
                raise ValueError("Reference does not match owner-accepted receipt evidence: " + name)
    original = profiles["original"]
    if (original["audio"], original["sha256"], original["text"]) != (selected["reference_audio"], selected["reference_sha256"], selected["reference_text"]):
        raise ValueError("Original A2 profile differs from selected identity")
    return config, profile_path


def approved_policy(selected, acceptance):
    path = Path(__file__).with_name("SOURCE_DELIVERY_POLICY.json")
    policy = json.loads(path.read_text(encoding="utf-8"))
    if policy.get("schema_version") != 1 or policy.get("voice_id") != selected["voice_id"]:
        raise ValueError("Delivery policy schema/voice identity mismatch")
    if policy["qwen_source"] != TEACHERS["qwen"] or policy["cosy_source"] != TEACHERS["cosy"]:
        raise ValueError("Delivery policy must bind the reviewed pinned teacher revisions")
    reference = policy["speaker_reference"]
    if reference != {"audio": selected["reference_audio"], "sha256": selected["reference_sha256"], "text": selected["reference_text"]}:
        raise ValueError("Cosy speaker reference must be the unchanged original A2")
    later = acceptance.get("later_acting_acceptance", {})
    if (set(later.get("accepted_clips", [])) != {"2-natural-happy", "4-little-chuckle"}
            or "1-neutral" not in later.get("rejected_clips", [])):
        raise ValueError("Missing owner happy/chuckle acceptance and explicit Cosy neutral rejection")
    selected_examples = {entry["id"]: entry for entry in selected["emotional_source_acceptance"]["evidence"]}
    evidence = {entry["path"]: entry["sha256"] for entry in acceptance["evidence"]}
    examples = policy["approved_examples"]
    if len(examples) != 2 or {entry["id"] for entry in examples} != {"2-natural-happy", "4-little-chuckle"}:
        raise ValueError("Only the two actually heard positive Cosy examples may guide this recipe")
    for example in examples:
        if example != selected_examples.get(example["id"]):
            raise ValueError("Policy acting example differs from selected owner evidence")
        for audio, digest in (("audio", "sha256"), ("listening_audio", "listening_sha256")):
            if evidence.get(example[audio]) != example[digest] or file_hash(local_path(ROOT, example[audio])) != example[digest]:
                raise ValueError("Accepted acting example changed: " + example["id"])
    if set(policy["emotion_routes"]) != set(EMOTIONS) or set(policy["cosy_instructions"]) != {"natural_happy", "relaxed_smile"}:
        raise ValueError("Incomplete/unknown mixed delivery policy")
    if policy["event_route"] != {"teacher": "cosy", "instruction": "relaxed_smile"}:
        raise ValueError("Recorded events must use the accepted relaxed-smile route")
    selection = owner_delivery_selection(policy)
    for example, instruction in (("2-natural-happy", "natural_happy"), ("4-little-chuckle", "relaxed_smile")):
        heard = {selected_examples[example]["instruction"]} | ({selection["cosy_instruction"]} if selection else set())
        if policy["cosy_instructions"][instruction] not in heard:
            raise ValueError("Cosy instruction differs from every owner-heard performance")
    return policy, path


def owner_delivery_selection(policy):
    """The owner's later A/B choice of delivery (receipts/delivery-ab-*.json), bound to the exact clips heard.

    Owner, 2026-10-12: the first acting instructions sounded "too happy"; the owner heard dry and midpoint
    renders and chose a dry Cosy instruction and the everyday A2 take. That choice may replace the earlier
    instructions only when every heard clip still hashes to its receipt.
    """
    ref = policy.get("owner_delivery_selection")
    if not ref:
        return None
    path = local_path(ROOT, ref["receipt"])
    receipt = json.loads(path.read_text(encoding="utf-8"))
    if (receipt.get("decision") != "accepted" or receipt.get("accepted_by") != "owner"
            or receipt.get("voice_id") != policy["voice_id"] or not receipt.get("owner_quotes") or not receipt.get("evidence")):
        raise ValueError("Delivery selection receipt is not an owner acceptance for this voice")
    for entry in receipt["evidence"]:
        if file_hash(local_path(ROOT, entry["path"])) != entry["sha256"]:
            raise ValueError("Owner-heard A/B clip changed: " + entry["path"])
    return receipt


def route_for(job, policy, profiles):
    route = policy["event_route"] if any(event_counts(job["text"]).values()) else policy["emotion_routes"][job["emotion"]]
    if route.get("teacher") == "qwen":
        if set(route) != {"teacher", "profile"} or route["profile"] not in profiles["profiles"] or any(event_counts(job["text"]).values()):
            raise ValueError("Qwen route cannot synthesize literal nonverbal labels or unknown references")
    elif route.get("teacher") == "cosy":
        if (job["emotion"] == "neutral" or set(route) != {"teacher", "instruction"}
                or route["instruction"] not in policy["cosy_instructions"]):
            raise ValueError("Cosy neutral/unknown instruction is prohibited")
    else:
        raise ValueError("Unknown source teacher route")
    return dict(route)


def git_read(directory, *args):
    return subprocess.check_output(["git", "-C", str(directory), *args], text=True, encoding="utf-8", timeout=180).strip()


def tracked_source(directory):
    if git_read(directory, "status", "--porcelain", "--untracked-files=all"):
        raise ValueError("Teacher source checkout is dirty; preserve it and review before rendering")
    files = subprocess.check_output(["git", "-C", str(directory), "ls-files", "-z"], timeout=180).decode("utf-8").split("\0")
    return {name: file_hash(directory / name) for name in sorted(files) if name and (directory / name).is_file()}


def teacher_inputs(teacher, model_dir, code_dir=None):
    model_dir = model_dir.resolve()
    if not model_dir.is_dir():
        raise ValueError("Missing local teacher model directory: " + str(model_dir))
    source = json.loads((model_dir / "audition-source.json").read_text(encoding="utf-8"))
    if (source.get("repo"), source.get("revision")) != (TEACHERS[teacher]["repo"], TEACHERS[teacher]["revision"]):
        raise ValueError("Wrong/mutable teacher source: " + teacher)
    files = {path.relative_to(model_dir).as_posix(): file_hash(path) for path in sorted(model_dir.rglob("*"))
             if path.is_file() and ".cache" not in path.parts and "__pycache__" not in path.parts}
    required = ("config.json", "model.safetensors") if teacher == "qwen" else ("cosyvoice3.yaml", "llm.pt", "flow.pt", "hift.pt", "speech_tokenizer_v3.onnx", "campplus.onnx")
    if any(name not in files for name in required):
        raise ValueError("Required pinned teacher files missing: " + teacher)
    downloaded = {}
    for name in files:
        receipt = model_dir / ".cache/huggingface/download" / (name + ".metadata")
        if receipt.is_file():
            lines = receipt.read_text(encoding="utf-8").splitlines()
            if not lines or lines[0] != TEACHERS[teacher]["revision"]:
                raise ValueError("Local HF file revision differs from the pinned source: " + name)
            downloaded[name] = lines[0]
    if any(name not in downloaded for name in required):
        raise ValueError("Required teacher files lack the matching local HF revision receipts")
    result = {**TEACHERS[teacher], "source_record": source, "model_files_sha256": files,
              "hf_file_revisions": downloaded}
    if teacher == "qwen":
        if json.loads((model_dir / "config.json").read_text(encoding="utf-8")).get("tts_model_type") != "base":
            raise ValueError("Qwen must use the reviewed reference-anchored Base variant")
    else:
        if code_dir is None:
            raise ValueError("Cosy routes require --cosy-code-dir")
        code_dir = code_dir.resolve()
        if git_read(code_dir, "rev-parse", "HEAD") != TEACHERS[teacher]["code_commit"]:
            raise ValueError("Unexpected Cosy source code revision")
        result["code_files_sha256"] = tracked_source(code_dir)
        matcha = code_dir / "third_party/Matcha-TTS"
        link = git_read(code_dir, "ls-tree", "HEAD", "third_party/Matcha-TTS").split()
        if len(link) < 4 or link[0:2] != ["160000", "commit"] or git_read(matcha, "rev-parse", "HEAD") != link[2]:
            raise ValueError("Matcha submodule does not match the pinned Cosy gitlink")
        result["matcha_commit"] = link[2]
        result["matcha_files_sha256"] = tracked_source(matcha)
    return result


def worker_environment(python, teacher):
    if python is None or not python.is_file():
        raise ValueError("Supply an existing isolated --%s-python executable" % teacher)
    try:
        stdout = owned_process([str(python.resolve()), str(WORKER), "--describe", teacher],
                               bounded_seconds("VOICE_SOURCE_PROBE_SECONDS", 180, 600), capture=True)
    except subprocess.CalledProcessError as error:
        detail = (error.stderr or error.output or "No captured diagnostic").strip()
        raise ValueError("%s metadata probe failed with exit %d:\n%s" %
                         (teacher, error.returncode, detail[-4000:])) from error
    descriptor = json.loads(stdout)
    if descriptor.get("teacher") != teacher or descriptor.get("schema_version") != 1:
        raise ValueError("Invalid teacher environment descriptor")
    return descriptor


def expected_rows(plan):
    expected = {}
    for job in plan["jobs"]:
        key = "a2-" + canonical_hash({"source": plan["source_id"], "job": job, "route": plan["routes"][job["id"]]})[:24]
        if key in expected:
            raise ValueError("Duplicate rendered clip identity")
        expected[key] = {"schema": DATASET_SCHEMA, "id": key, "text": job["text"],
                         "audio": "wavs/" + key + ".wav", "sample_rate": FEATURES["sample_rate"],
                         "voice_id": plan["renderer"]["voice_id"], "source_id": plan["source_id"],
                         "emotion": job["emotion"], "intensity": job["intensity"],
                         "pace": job["pace"], "speech_act": job["speech_act"]}
    return expected


def read_metadata(output, expected):
    path = output / "metadata.jsonl"
    done = {}
    if not path.exists():
        return done
    text = path.read_text(encoding="utf-8")
    if text and not text.endswith("\n"):
        raise ValueError("Torn/non-newline-complete metadata; preserve it for explicit recovery review")
    for line in text.splitlines():
        row = json.loads(line)
        wanted = expected.get(row.get("id")) if isinstance(row, dict) else None
        if (wanted is None or {key: value for key, value in row.items() if key != "sha256"} != wanted
                or not isinstance(row.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", row["sha256"])
                or file_hash(local_path(output, row["audio"])) != row["sha256"] or row["id"] in done):
            raise ValueError("Invalid existing exact source record; preserve and inspect")
        done[row["id"]] = row
    return done


def load_recipe(path):
    saved = json.loads(path.read_text(encoding="utf-8"))
    plan = {key: value for key, value in saved.items() if key != "recipe_id"}
    if (saved.get("recipe_id") != canonical_hash(plan) or plan["renderer"].get("schema_version") != 3
            or plan.get("source_id") != canonical_hash(plan["renderer"])):
        raise ValueError("Wrong/torn source recipe; schema 3 needs a fresh batch")
    return plan, saved["recipe_id"]


def write_new_json(path, value):
    temporary = path.with_name(path.name + ".writing-" + uuid.uuid4().hex)
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    if path.exists():
        raise ValueError("Output appeared concurrently; preserve both records: " + str(path))
    temporary.rename(path)


def finish_report(output, identity, recipe_id, plan, render_seconds=None, recovered=False):
    """Recover only a missing complete report; source-worker provenance already exists, no GPU load."""
    runtime = {}
    for teacher in sorted(plan["renderer"]["teachers"]):
        path = output / ("source-" + teacher + "-runtime.json")
        receipt = json.loads(path.read_text(encoding="utf-8"))
        if receipt.get("recipe_id") != recipe_id or receipt.get("teacher") != teacher:
            raise ValueError("Missing/mismatched worker provenance; preserve batch for review")
        runtime[path.name] = file_hash(path)
    path = output / "source-build.json"
    if path.exists():
        report = json.loads(path.read_text(encoding="utf-8"))
        if (report.get("schema_version") != 3 or report.get("dataset") != identity or report.get("recipe_id") != recipe_id
                or report.get("scope") != plan["scope"] or report.get("runtime_sha256") != runtime):
            raise ValueError("Existing source report belongs to another batch; preserve it")
        return
    report = {"schema_version": 3, "dataset": identity, "recipe_id": recipe_id, "scope": plan["scope"],
              "runtime_sha256": runtime, "render_seconds": render_seconds,
              "completion": "recovered_exact_complete_metadata" if recovered else "rendered_complete",
              "audio_acceptance": "pending", "event_performance_acceptance": "pending", "student_training_started": False}
    write_new_json(path, report)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out", type=Path)
    parser.add_argument("--model-dir", type=Path, help="Existing pinned Qwen Base directory")
    parser.add_argument("--qwen-python", type=Path)
    parser.add_argument("--cosy-python", type=Path)
    parser.add_argument("--cosy-code-dir", type=Path)
    parser.add_argument("--cosy-model-dir", type=Path)
    parser.add_argument("--corpus", type=Path, default=Path(__file__).with_name("SPEECH_CORPUS.jsonl"))
    parser.add_argument("--event-corpus", type=Path, default=Path(__file__).with_name("SPEECH_EVENT_CORPUS.jsonl"))
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--limit", type=int, default=32)
    scope.add_argument("--all", action="store_true")
    args = parser.parse_args()
    if args.out.exists() and any(args.out.glob("source-*-timeout.json")):
        raise ValueError("Prior source worker timed out; preserve/review this batch and choose a fresh directory")
    if not args.all and not 24 <= args.limit <= 5000:
        raise ValueError("Pilot limit must be 24..5000 and sufficient for required event/state coverage")
    selection_path = Path(__file__).with_name("SELECTED_VOICE.json")
    selected = json.loads(selection_path.read_text(encoding="utf-8"))
    acceptance_path = Path(__file__).parent / "receipts/source-auditions.json"
    acceptance = json.loads(acceptance_path.read_text(encoding="utf-8"))
    if acceptance.get("decision") != "accepted" or acceptance.get("accepted_by") != "owner" or acceptance.get("voice_id") != selected["voice_id"]:
        raise ValueError("No owner acceptance of this source identity")
    gate = json.loads(Path(__file__).with_name("VOICE_QUALITY_GATE.json").read_text(encoding="utf-8"))
    source_check = gate["checks"]["source_auditions"]
    if (source_check.get("accepted") is not True or source_check.get("receipt") != "training/voice/receipts/source-auditions.json"
            or source_check.get("receipt_sha256") != file_hash(acceptance_path)):
        raise ValueError("Source approval receipt is not the identity-bound accepted receipt")
    profiles, profile_path = approved_profiles(selected, acceptance)
    policy, policy_path = approved_policy(selected, acceptance)
    rows = corpus_rows(args.corpus) + corpus_rows(args.event_corpus, require_events=True)
    if len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Speech/event corpora have overlapping IDs; preserve and repair the source drafts")
    jobs = rows if args.all else pilot_rows(rows, args.limit)
    routes = {job["id"]: route_for(job, policy, profiles) for job in jobs}
    used = {route["teacher"] for route in routes.values()}
    directories = {"qwen": args.model_dir, "cosy": args.cosy_model_dir}
    interpreters = {"qwen": args.qwen_python, "cosy": args.cosy_python}
    if "cosy" in used and (args.cosy_code_dir is None or args.cosy_model_dir is None):
        raise ValueError("Any Cosy route requires --cosy-code-dir and --cosy-model-dir")
    if "qwen" in used and args.model_dir is None:
        raise ValueError("Any Qwen route requires --model-dir")
    teachers = {name: {"inputs": teacher_inputs(name, directories[name], args.cosy_code_dir if name == "cosy" else None),
                       "environment": worker_environment(interpreters[name], name)} for name in sorted(used)}
    renderer = {
        "schema_version": 3, "teachers": teachers, "voice_id": selected["voice_id"],
        "selected_config": selected, "selected_config_sha256": file_hash(selection_path),
        "reference_profiles": profiles, "reference_profiles_sha256": file_hash(profile_path),
        "source_delivery_policy": policy, "source_delivery_policy_sha256": file_hash(policy_path),
        "approval_receipt": acceptance, "approval_receipt_sha256": file_hash(acceptance_path),
        "builder_sha256": file_hash(Path(__file__)), "worker_sha256": file_hash(WORKER),
        "contract_sha256": file_hash(Path(__file__).with_name("dataset_contract.py")),
        "speech_text_sha256": file_hash(Path(__file__).with_name("speech_text.py")),
        "event_vocabulary": EVENT_MARKERS, "features": FEATURES,
        "seed_policy": "clip identity SHA256 prefix; teacher batches run sequentially",
        "generation": {
            "qwen": {"max_new_tokens": 600, "temperature": .75, "top_p": .9, "do_sample": True, "language": "English",
                     "non_streaming_mode": True, "x_vector_only_mode": False, "dtype": "bfloat16", "attention": "sdpa"},
            "cosy": {"fp16": True, "load_trt": False, "load_vllm": False, "stream": False, "speed": 1.0,
                     "text_frontend": False, "zero_shot_spk_id": "", "onnx_providers": ["CPUExecutionProvider"]},
        },
        "delivery_status": "intended labels and event markers remain pending audible performance/transcript review",
    }
    plan = {"renderer": renderer, "source_id": canonical_hash(renderer),
            "corpora_sha256": {"speech": file_hash(args.corpus), "events": file_hash(args.event_corpus)},
            "scope": "full-draft" if args.all else "pilot", "jobs": jobs, "routes": routes,
            "audio_acceptance": "pending", "training_authorized": False}
    recipe_id = canonical_hash(plan)
    args.out.mkdir(parents=True, exist_ok=True)
    recipe_file = args.out / "render-recipe.json"
    if recipe_file.exists():
        if json.loads(recipe_file.read_text(encoding="utf-8")) != dict(plan, recipe_id=recipe_id):
            raise ValueError("Output belongs to another immutable recipe; schema 3 needs a fresh directory")
    elif any(args.out.iterdir()):
        raise ValueError("Output is not empty or a matching schema 3 recipe; historical/torn data is preserved")
    else:
        write_new_json(recipe_file, dict(plan, recipe_id=recipe_id))
    (args.out / "wavs").mkdir(exist_ok=True)
    expected = expected_rows(plan)
    done = read_metadata(args.out, expected)
    if set(done) == set(expected):
        _, identity = load_dataset(args.out)
        finish_report(args.out, identity, recipe_id, plan, recovered=True)
        print("Exact mixed source batch complete; receipt verified without GPU load or audio replacement.", flush=True)
        return
    for key in set(expected) - set(done):
        path = local_path(args.out, expected[key]["audio"])
        if path.exists() or path.with_name(key + ".writing.wav").exists():
            raise ValueError("Orphan/interrupted WAV exists; preserve it for explicit recovery review")
    started = time.monotonic()
    # A process exits and releases all GPU state before the next teacher is loaded.
    for teacher in ("qwen", "cosy"):
        if teacher not in used:
            continue
        remaining = [job for job in jobs if routes[job["id"]]["teacher"] == teacher
                     and ("a2-" + canonical_hash({"source": plan["source_id"], "job": job, "route": routes[job["id"]]})[:24]) not in done]
        if not remaining:
            continue
        command = [str(interpreters[teacher].resolve()), str(WORKER), "--teacher", teacher,
                   "--recipe", str(recipe_file.resolve()), "--model-dir", str(directories[teacher].resolve())]
        if teacher == "cosy":
            command += ["--code-dir", str(args.cosy_code_dir.resolve())]
        setup = bounded_seconds("VOICE_SOURCE_SETUP_SECONDS", 180, 1800)
        per_clip = bounded_seconds("VOICE_SOURCE_CLIP_SECONDS", 300, 1800)
        seconds = setup + per_clip * len(remaining)
        if seconds > 7 * 24 * 3600:
            raise ValueError("Source worker walltime exceeds the seven-day absolute bound; reduce batch/limits")
        try:
            owned_process(command, seconds)
        except OwnedTimeout as error:
            write_new_json(args.out / ("source-" + teacher + "-timeout.json"), {
                "schema_version": 1, "recipe_id": recipe_id, "teacher": teacher,
                "owned_child_pid": error.pid, "wall_timeout_seconds": error.seconds,
                "termination": error.termination, "recovery": "explicit review; preserve batch and use a fresh directory",
                "audio_acceptance": "pending", "student_training_started": False})
            raise
        done = read_metadata(args.out, expected)
    exact, identity = load_dataset(args.out)
    if set(done) != set(expected) or len(exact) != len(jobs):
        raise ValueError("Incomplete or extra source records; preserve the batch")
    finish_report(args.out, identity, recipe_id, plan, render_seconds=time.monotonic() - started)
    print("Mixed source draft built; listening/event QA pending, no training permission.", flush=True)


if __name__ == "__main__":
    main()
