"""Render a fresh v2 conversational dataset from the owner-approved synthetic A2 reference.

Use the isolated qwen-tts environment, an already downloaded pinned Base model,
and a NEW output directory. Default is a small coverage pilot; --all is explicit.
This generates source audio only: no student training, cloud work or deployment.
Intent labels still require audible corpus review before paid training acceptance.
The old Kokoro/CSV factory is preserved in the dated preparation evidence folder.
"""
import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import time

from dataset_contract import (DATASET_SCHEMA, EMOTIONS, SPEECH_ACTS, canonical_hash,
                              delivery, file_hash, load_dataset, split_for)

ROOT = Path(__file__).resolve().parents[2]
TEACHER = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
REVISION = "fd4b254389122332181a7c3db7f27e918eec64e3"
FIELDS = {"id", "text", "emotion", "intensity", "pace", "speech_act"}


def corpus_rows(path):
    rows, ids = [], set()
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if set(row) != FIELDS or not row["text"].strip() or row["id"] in ids:
            raise ValueError("Invalid or duplicate speech corpus entry")
        delivery(row["emotion"], row["intensity"], row["pace"], row["speech_act"])
        if row["pace"] != 1.0:
            raise ValueError("This teacher has no explicit pace control; unverified pace labels are refused")
        ids.add(row["id"]); rows.append(row)
    if not rows:
        raise ValueError("Empty speech corpus")
    return rows


def pilot_rows(rows, limit):
    """Include distinct styles, acts and both transcript-group partitions, then fill."""
    chosen, seen = [], set()
    groups = [("emotion", x) for x in EMOTIONS] + [("speech_act", x) for x in SPEECH_ACTS]
    for field, value in groups + [("split", "train"), ("split", "heldout")]:
        match = next((r for r in rows if (split_for(r["text"]) if field == "split" else r[field]) == value), None)
        if match is None:
            raise ValueError("Corpus lacks required coverage: " + value)
        if match["id"] not in seen:
            chosen.append(match); seen.add(match["id"])
    if len(chosen) > limit:
        raise ValueError("Pilot limit too small for style/act/group coverage")
    for row in rows:
        if len(chosen) >= limit:
            break
        if row["id"] not in seen:
            chosen.append(row); seen.add(row["id"])
    return chosen


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("out", type=Path)
    ap.add_argument("--model-dir", type=Path, required=True)
    ap.add_argument("--corpus", type=Path, default=Path(__file__).with_name("SPEECH_CORPUS.jsonl"))
    scope = ap.add_mutually_exclusive_group()
    scope.add_argument("--limit", type=int, default=24)
    scope.add_argument("--all", action="store_true")
    args = ap.parse_args()
    if not args.all and not 18 <= args.limit <= 5000:
        raise ValueError("Pilot limit must be 18..5000")
    selection_path = Path(__file__).with_name("SELECTED_VOICE.json")
    selected = json.loads(selection_path.read_text(encoding="utf-8"))
    reference = ROOT / selected["reference_audio"]
    if file_hash(reference) != selected["reference_sha256"]:
        raise ValueError("The approved A2 reference audio changed")
    acceptance = json.loads((Path(__file__).parent / "receipts/source-auditions.json").read_text(encoding="utf-8"))
    if acceptance.get("decision") != "accepted" or acceptance.get("accepted_by") != "owner" or acceptance.get("voice_id") != selected["voice_id"]:
        raise ValueError("No owner acceptance of this source identity")
    gate = json.loads(Path(__file__).with_name("VOICE_QUALITY_GATE.json").read_text(encoding="utf-8"))
    source_check = gate["checks"]["source_auditions"]
    if source_check.get("accepted") is not True or source_check.get("receipt") != "training/voice/receipts/source-auditions.json" or source_check.get("receipt_sha256") != file_hash(Path(__file__).parent / "receipts/source-auditions.json"):
        raise ValueError("Source approval receipt is not the identity-bound accepted receipt")
    model_dir = args.model_dir.resolve()
    source = json.loads((model_dir / "audition-source.json").read_text(encoding="utf-8"))
    if source["repo"] != TEACHER or source["revision"] != REVISION:
        raise ValueError("Wrong or mutable teacher source")
    if json.loads((model_dir / "config.json").read_text(encoding="utf-8")).get("tts_model_type") != "base":
        raise ValueError("Expected the reviewed reference-anchored Base variant")
    rows = corpus_rows(args.corpus)
    jobs = rows if args.all else pilot_rows(rows, args.limit)
    versions = {name: importlib.metadata.version(name) for name in
                ("qwen-tts", "torch", "transformers", "accelerate", "soundfile")}
    if versions["qwen-tts"] != "0.1.1" or versions["transformers"] != "4.57.3":
        raise ValueError("Use the reviewed isolated teacher environment")
    model_hashes = {p.relative_to(model_dir).as_posix(): file_hash(p)
                    for p in sorted(model_dir.rglob("*.safetensors"))}
    if not model_hashes:
        raise ValueError("Teacher weights missing")
    renderer = {
        "schema_version": 1, "teacher": TEACHER, "revision": REVISION,
        "model_sha256": model_hashes, "reference_sha256": selected["reference_sha256"],
        "voice_id": selected["voice_id"], "versions": versions,
        "builder_sha256": file_hash(Path(__file__)),
        "contract_sha256": file_hash(Path(__file__).with_name("dataset_contract.py")),
        "seed_policy": "clip identity SHA256 prefix",
        "generation": {"max_new_tokens": 600, "temperature": 0.75, "top_p": 0.9},
        "delivery_policy": "reference identity plus authored text/context; intended labels need listening review",
    }
    source_id = canonical_hash(renderer)
    plan = {"renderer": renderer, "source_id": source_id, "corpus_sha256": file_hash(args.corpus),
            "scope": "full-draft" if args.all else "pilot", "jobs": jobs,
            "audio_acceptance": "pending", "training_authorized": False}
    recipe_id = canonical_hash(plan)
    args.out.mkdir(parents=True, exist_ok=True)
    recipe_file = args.out / "render-recipe.json"
    if recipe_file.exists():
        previous = json.loads(recipe_file.read_text(encoding="utf-8"))
        if previous != dict(plan, recipe_id=recipe_id):
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
        from dataset_contract import local_path
        for line in metadata.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            wanted = expected.get(row.get("id"))
            if wanted is None or {k: v for k, v in row.items() if k != "sha256"} != wanted or file_hash(local_path(args.out, row["audio"])) != row["sha256"] or row["id"] in done:
                raise ValueError("Invalid existing source record; preserve and inspect")
            done[row["id"]] = row
    if set(done) == set(expected):
        load_dataset(args.out)
        print("Exact source batch already complete; no GPU load or audio replacement.", flush=True)
        return
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    import numpy as np
    import soundfile as sf
    import torch
    from qwen_tts import Qwen3TTSModel
    if not torch.cuda.is_available() or torch.cuda.mem_get_info()[0] < 8 * 1024 ** 3:
        raise ValueError("Insufficient free local GPU memory; do not disturb the active rig")
    model = Qwen3TTSModel.from_pretrained(str(model_dir), device_map="cuda:0", dtype=torch.bfloat16,
                                        attn_implementation="sdpa", local_files_only=True)
    prompt = model.create_voice_clone_prompt(ref_audio=str(reference), ref_text=selected["reference_text"],
                                             x_vector_only_mode=False)
    started = time.monotonic()
    for job in jobs:
        key = "a2-" + canonical_hash({"source": source_id, "job": job})[:24]
        if key in done:
            continue
        path = wavdir / (key + ".wav")
        if path.exists():
            raise ValueError("Orphan WAV exists without metadata; preserve it for recovery review")
        seed = int(canonical_hash({"clip": key})[:8], 16)
        torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
        wavs, sr = model.generate_voice_clone(
            text=job["text"], language="English", voice_clone_prompt=prompt,
            non_streaming_mode=True, do_sample=True, temperature=0.75, top_p=0.9, max_new_tokens=600)
        audio = np.asarray(wavs[0], dtype=np.float32).reshape(-1)
        if sr != 24000 or not audio.size or not np.isfinite(audio).all() or not .25 <= len(audio) / sr <= 30:
            raise ValueError("Invalid duration/format teacher clip: " + job["id"])
        if np.max(np.abs(audio)) >= 1 or np.sqrt(np.mean(audio.astype(np.float64) ** 2)) < 1e-5:
            raise ValueError("Silent or saturated source audio: " + job["id"])
        temporary = wavdir / (key + ".writing.wav")
        if temporary.exists():
            raise ValueError("Interrupted source write exists; preserve for review")
        sf.write(temporary, audio, sr, subtype="PCM_16")
        temporary.rename(path)
        row = {"schema": DATASET_SCHEMA, "id": key, "text": job["text"],
               "audio": "wavs/" + path.name, "sha256": file_hash(path), "sample_rate": sr,
               "voice_id": selected["voice_id"], "source_id": source_id,
               "emotion": job["emotion"], "intensity": job["intensity"],
               "pace": job["pace"], "speech_act": job["speech_act"]}
        with metadata.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
            stream.flush()
        done[key] = row
        print("SOURCE %d/%d %s %.2fs (label needs listening review)" % (
            len(done), len(jobs), job["id"], len(audio) / sr), flush=True)
    exact, identity = load_dataset(args.out)
    if len(exact) != len(jobs):
        raise ValueError("Dataset contains rows outside the exact recipe")
    report = {"dataset": identity, "recipe_id": recipe_id, "scope": plan["scope"],
              "render_seconds": time.monotonic() - started,
              "audio_acceptance": "pending", "student_training_started": False}
    (args.out / "source-build.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    del model; torch.cuda.empty_cache()
    print("Source audio built; not corpus acceptance or training permission.", flush=True)


if __name__ == "__main__":
    main()
