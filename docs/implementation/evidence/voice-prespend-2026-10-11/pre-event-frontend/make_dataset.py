"""Render a fresh v2 conversational source dataset using approved A2 performances.

Use the isolated qwen-tts environment, an already downloaded pinned Base model,
and a NEW output directory. Default is a balanced 24-clip pilot; --all is explicit.
This generates source audio only: no student training, cloud work or deployment.
References bias delivery; intended emotion labels still need audible performance review.
Historical source batches, reports, orphan WAVs and torn metadata are never replaced.
"""
import argparse
import collections
import importlib.metadata
import json
import os
from pathlib import Path
import time
import uuid

from dataset_contract import (DATASET_SCHEMA, EMOTIONS, SPEECH_ACTS, FEATURES, canonical_hash,
                              delivery, file_hash, load_dataset, local_path, split_for)

ROOT = Path(__file__).resolve().parents[2]
TEACHER = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
REVISION = "fd4b254389122332181a7c3db7f27e918eec64e3"
FIELDS = {"id", "text", "emotion", "intensity", "pace", "speech_act"}
QUESTIONS = {"yes_no_question", "wh_question"}


def corpus_rows(path):
    rows, ids = [], set()
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if not isinstance(row, dict) or set(row) != FIELDS or not isinstance(row["text"], str) or not row["text"].strip() or row["id"] in ids:
            raise ValueError("Invalid or duplicate speech corpus entry")
        delivery(row["emotion"], row["intensity"], row["pace"], row["speech_act"])
        if row["pace"] != 1.0:
            raise ValueError("This teacher has no explicit pace control; unverified pace labels are refused")
        ids.add(row["id"]); rows.append(row)
    if not rows:
        raise ValueError("Empty speech corpus")
    return rows


def pilot_rows(rows, limit):
    """Connected speech in every state, questions across states, all acts, two short turns."""
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
            row["speech_act"] in represented,
            order[row["id"]]))
        row = available[0]
        chosen.append(row); seen.add(row["id"])
        return row

    for index, emotion in enumerate(EMOTIONS):
        candidates = [row for row in rows if row["emotion"] == emotion and len(row["text"].split()) >= 6]
        if not candidates:
            raise ValueError("Corpus lacks connected speech for " + emotion)
        choose([row for row in candidates if row["speech_act"] not in QUESTIONS] or candidates,
               nonquestions[index % len(nonquestions)])
    for index, emotion in enumerate(EMOTIONS):
        candidates = [row for row in rows if row["emotion"] == emotion and row["speech_act"] in QUESTIONS]
        if candidates and not any(row["emotion"] == emotion and row["speech_act"] in QUESTIONS for row in chosen):
            choose(candidates, "yes_no_question" if index % 2 == 0 else "wh_question")
    for act in SPEECH_ACTS:
        if not any(row["speech_act"] == act for row in chosen):
            if choose([row for row in rows if row["speech_act"] == act]) is None:
                raise ValueError("Corpus lacks speech act " + act)
    for partition in ("train", "heldout"):
        if not any(split_for(row["text"]) == partition for row in chosen):
            if choose([row for row in rows if split_for(row["text"]) == partition]) is None:
                raise ValueError("Corpus lacks " + partition + " transcript groups")
    for emotion in ("neutral", "warm"):
        if sum(len(row["text"].split()) <= 3 and row["speech_act"] not in QUESTIONS for row in chosen) >= 2:
            break
        short = [row for row in rows if len(row["text"].split()) <= 3 and row["speech_act"] not in QUESTIONS]
        if choose([row for row in short if row["emotion"] == emotion] or short) is None:
            raise ValueError("Corpus lacks two distinct short turns")
    if len(chosen) > limit:
        raise ValueError("Pilot limit too small for connected/style/question/act/split/short-turn coverage")
    while len(chosen) < limit:
        counts = collections.Counter(row["emotion"] for row in chosen)
        candidates = [row for row in rows if row["id"] not in seen]
        if not candidates:
            break
        least = min(counts[row["emotion"]] for row in candidates)
        balanced = [row for row in candidates if counts[row["emotion"]] == least]
        connected = [row for row in balanced if len(row["text"].split()) >= 6]
        choose(connected or balanced)
    if sum(len(row["text"].split()) <= 3 and row["speech_act"] not in QUESTIONS for row in chosen) < 2:
        raise ValueError("Pilot must contain two distinct short turns")
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
    mapping = config["emotion_references"]
    if set(mapping) != set(EMOTIONS) or not set(mapping.values()) <= set(profiles):
        raise ValueError("Reference emotion mapping is incomplete")
    if config["question_reference"] not in profiles or not set(config["question_override_emotions"]) <= set(EMOTIONS):
        raise ValueError("Invalid question reference mapping")
    return config, profile_path


def reference_for(job, config):
    if job["speech_act"] in QUESTIONS and job["emotion"] in config["question_override_emotions"]:
        return config["question_reference"]
    return config["emotion_references"][job["emotion"]]


def finish_report(output, identity, recipe_id, scope, render_seconds=None, recovered=False):
    """Recreate a missing completed-batch receipt without loading the GPU; never replace a report."""
    path = output / "source-build.json"
    if path.exists():
        report = json.loads(path.read_text(encoding="utf-8"))
        if report.get("dataset") != identity or report.get("recipe_id") != recipe_id or report.get("scope") != scope:
            raise ValueError("Existing source report belongs to another batch; preserve it for inspection")
        return
    report = {"schema_version": 2, "dataset": identity, "recipe_id": recipe_id, "scope": scope,
              "render_seconds": render_seconds,
              "completion": "recovered_exact_complete_metadata" if recovered else "rendered_complete",
              "audio_acceptance": "pending", "student_training_started": False}
    temporary = path.with_name(path.name + ".writing-" + uuid.uuid4().hex)
    temporary.write_text(json.dumps(report, indent=2), encoding="utf-8")
    # The caller owns this output directory. A concurrent writer is a conflict, never a replacement.
    if path.exists():
        raise ValueError("Source report appeared concurrently; preserve both records")
    temporary.rename(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out", type=Path)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--corpus", type=Path, default=Path(__file__).with_name("SPEECH_CORPUS.jsonl"))
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--limit", type=int, default=24)
    scope.add_argument("--all", action="store_true")
    args = parser.parse_args()
    if not args.all and not 18 <= args.limit <= 5000:
        raise ValueError("Pilot limit must be 18..5000 and large enough for the required coverage")
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
    model_dir = args.model_dir.resolve()
    source = json.loads((model_dir / "audition-source.json").read_text(encoding="utf-8"))
    if source["repo"] != TEACHER or source["revision"] != REVISION:
        raise ValueError("Wrong or mutable teacher source")
    if json.loads((model_dir / "config.json").read_text(encoding="utf-8")).get("tts_model_type") != "base":
        raise ValueError("Expected the reviewed reference-anchored Base variant")
    rows = corpus_rows(args.corpus)
    jobs = rows if args.all else pilot_rows(rows, args.limit)
    versions = {name: importlib.metadata.version(name) for name in ("qwen-tts", "torch", "transformers", "accelerate", "soundfile")}
    if versions["qwen-tts"] != "0.1.1" or versions["transformers"] != "4.57.3":
        raise ValueError("Use the reviewed isolated teacher environment")
    suffixes = {".safetensors", ".json", ".txt", ".model", ".tiktoken", ".vocab", ".merges", ".bin", ".pt", ".onnx"}
    model_files = {path.relative_to(model_dir).as_posix(): file_hash(path)
                   for path in sorted(model_dir.rglob("*")) if path.is_file() and path.suffix.lower() in suffixes}
    if not any(name.endswith(".safetensors") for name in model_files):
        raise ValueError("Teacher weights missing")
    renderer = {
        "schema_version": 2, "teacher": TEACHER, "revision": REVISION, "model_files_sha256": model_files,
        "selected_config": selected, "selected_config_sha256": file_hash(selection_path),
        "reference_profiles": profiles, "reference_profiles_sha256": file_hash(profile_path),
        "approval_receipt": acceptance, "approval_receipt_sha256": file_hash(acceptance_path),
        "voice_id": selected["voice_id"], "versions": versions,
        "builder_sha256": file_hash(Path(__file__)),
        "contract_sha256": file_hash(Path(__file__).with_name("dataset_contract.py")),
        "seed_policy": "clip identity SHA256 prefix",
        "generation": {"max_new_tokens": 600, "temperature": 0.75, "top_p": 0.9, "do_sample": True,
                       "language": "English", "non_streaming_mode": True, "x_vector_only_mode": False,
                       "dtype": "bfloat16", "attention": "sdpa"},
        "delivery_policy": "approved reference performance plus authored text/context; intended labels need listening review",
    }
    source_id = canonical_hash(renderer)
    plan = {"renderer": renderer, "source_id": source_id, "corpus_sha256": file_hash(args.corpus),
            "scope": "full-draft" if args.all else "pilot", "jobs": jobs,
            "audio_acceptance": "pending", "training_authorized": False}
    recipe_id = canonical_hash(plan)
    args.out.mkdir(parents=True, exist_ok=True)
    recipe_file = args.out / "render-recipe.json"
    if recipe_file.exists():
        if json.loads(recipe_file.read_text(encoding="utf-8")) != dict(plan, recipe_id=recipe_id):
            raise ValueError("Output belongs to another immutable recipe; choose a fresh directory")
    elif any(args.out.iterdir()):
        raise ValueError("Output is not empty or a matching v2 recipe; old rejected data is preserved")
    else:
        recipe_file.write_text(json.dumps(dict(plan, recipe_id=recipe_id), indent=2), encoding="utf-8")
    wavdir = args.out / "wavs"; wavdir.mkdir(exist_ok=True)
    metadata = args.out / "metadata.jsonl"
    expected = {}
    for job in jobs:
        key = "a2-" + canonical_hash({"source": source_id, "job": job})[:24]
        expected[key] = {"schema": DATASET_SCHEMA, "id": key, "text": job["text"],
                         "audio": "wavs/" + key + ".wav", "sample_rate": 24000,
                         "voice_id": selected["voice_id"], "source_id": source_id,
                         "emotion": job["emotion"], "intensity": job["intensity"],
                         "pace": job["pace"], "speech_act": job["speech_act"]}
    done = {}
    if metadata.exists():
        for line in metadata.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            wanted = expected.get(row.get("id"))
            if (wanted is None or {key: value for key, value in row.items() if key != "sha256"} != wanted
                    or file_hash(local_path(args.out, row["audio"])) != row["sha256"] or row["id"] in done):
                raise ValueError("Invalid existing source record; preserve and inspect")
            done[row["id"]] = row
    if set(done) == set(expected):
        _, identity = load_dataset(args.out)
        finish_report(args.out, identity, recipe_id, plan["scope"], recovered=True)
        print("Exact source batch complete and receipt verified; no GPU load or audio replacement.", flush=True)
        return
    os.environ["HF_HUB_OFFLINE"] = "1"; os.environ["TRANSFORMERS_OFFLINE"] = "1"
    import numpy as np
    import soundfile as sf
    import torch
    from qwen_tts import Qwen3TTSModel
    if not torch.cuda.is_available() or torch.cuda.mem_get_info()[0] < 8 * 1024 ** 3:
        raise ValueError("Insufficient free local GPU memory; do not disturb the active rig")
    model = Qwen3TTSModel.from_pretrained(str(model_dir), device_map="cuda:0", dtype=torch.bfloat16,
                                        attn_implementation="sdpa", local_files_only=True)
    prompts = {}
    started = time.monotonic()
    for job in jobs:
        key = "a2-" + canonical_hash({"source": source_id, "job": job})[:24]
        if key in done:
            continue
        profile_name = reference_for(job, profiles)
        if profile_name not in prompts:
            reference = profiles["profiles"][profile_name]
            prompts[profile_name] = model.create_voice_clone_prompt(
                ref_audio=str(local_path(ROOT, reference["audio"])), ref_text=reference["text"],
                x_vector_only_mode=False)
        path = wavdir / (key + ".wav")
        if path.exists():
            raise ValueError("Orphan WAV exists without metadata; preserve it for recovery review")
        seed = int(canonical_hash({"clip": key})[:8], 16)
        torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
        wavs, rate = model.generate_voice_clone(
            text=job["text"], language="English", voice_clone_prompt=prompts[profile_name],
            non_streaming_mode=True, do_sample=True, temperature=0.75, top_p=0.9, max_new_tokens=600)
        if len(wavs) != 1:
            raise ValueError("Teacher did not return exactly one source utterance")
        audio = np.asarray(wavs[0], dtype=np.float32)
        if (rate != FEATURES["sample_rate"] or audio.ndim != 1 or not audio.size or not np.isfinite(audio).all()
                or not FEATURES["min_seconds"] <= len(audio) / rate <= FEATURES["max_seconds"]):
            raise ValueError("Invalid duration/format teacher clip: " + job["id"])
        if (np.max(np.abs(audio)) > 1.0 or np.mean(np.abs(audio) >= 0.999) > 0.001
                or np.sqrt(np.mean(audio.astype(np.float64) ** 2)) < 1e-5):
            raise ValueError("Silent or excessively clipped source audio: " + job["id"])
        temporary = wavdir / (key + ".writing.wav")
        if temporary.exists():
            raise ValueError("Interrupted source write exists; preserve for review")
        sf.write(temporary, audio, rate, subtype="PCM_16")
        temporary.rename(path)
        # Validate the serialized PCM too: it is what preparation will actually read.
        stored, stored_rate = sf.read(path, dtype="float32")
        if (stored_rate != rate or stored.ndim != 1 or not np.isfinite(stored).all()
                or np.max(np.abs(stored)) > 1.0 or np.mean(np.abs(stored) >= 0.999) > 0.001
                or np.sqrt(np.mean(stored.astype(np.float64) ** 2)) < 1e-5):
            raise ValueError("Serialized source failed preparation audio bounds; preserve it for inspection")
        row = dict(expected[key], sha256=file_hash(path))
        with metadata.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
            stream.flush()
        done[key] = row
        print("SOURCE %d/%d %s profile=%s %.2fs (performance label needs listening review)" % (
            len(done), len(jobs), job["id"], profile_name, len(audio) / rate), flush=True)
    exact, identity = load_dataset(args.out)
    if len(exact) != len(jobs):
        raise ValueError("Dataset contains rows outside the exact recipe")
    finish_report(args.out, identity, recipe_id, plan["scope"], render_seconds=time.monotonic() - started)
    del model; torch.cuda.empty_cache()
    print("Source audio built; not corpus acceptance or training permission.", flush=True)


if __name__ == "__main__":
    main()
