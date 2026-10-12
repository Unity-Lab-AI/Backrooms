"""Isolated A2 expansion authoring: fixed Qwen groups and exact Cosy prompt caching.

--describe imports installed metadata only. Rendering loads one pinned teacher,
preserves all failures/orphans, and never imports or trains a student model.
Optimized audio remains pending source review, even if an earlier recipe was heard.
"""
import argparse
import gc
import json
import os
from pathlib import Path
import sys
import time
import uuid

from dataset_contract import FEATURES, canonical_hash, file_hash, local_path
from make_dataset_optimized import (DIRECTORY, ROOT, WORKER, LIBRARY, WORKER_LIBRARY,
                                    expected_rows, load_recipe, read_metadata,
                                    route_for, teacher_inputs, validate_optimized_plan,
                                    write_new_json)
from source_workers import PACKAGES, audio_bounds, environment_descriptor
from speech_text import event_counts


def verify_recipe_inputs(plan, teacher, model_dir, code_dir):
    validate_optimized_plan(plan)
    renderer = plan["renderer"]
    checks = {"builder_sha256": DIRECTORY / "make_dataset_optimized.py", "worker_sha256": WORKER,
              "builder_library_sha256": LIBRARY, "worker_library_sha256": WORKER_LIBRARY,
              "contract_sha256": DIRECTORY / "dataset_contract.py",
              "speech_text_sha256": DIRECTORY / "speech_text.py",
              "selected_config_sha256": DIRECTORY / "SELECTED_VOICE.json",
              "reference_profiles_sha256": local_path(ROOT, renderer["selected_config"]["delivery_profiles"]),
              "source_delivery_policy_sha256": DIRECTORY / "SOURCE_DELIVERY_POLICY.json",
              "approval_receipt_sha256": DIRECTORY / "receipts/source-auditions.json"}
    if any(file_hash(path) != renderer.get(key) for key, path in checks.items()):
        raise ValueError("Immutable renderer/config/helper changed; preserve this batch")
    descriptor = {"inputs": teacher_inputs(teacher, model_dir, code_dir),
                  "environment": environment_descriptor(teacher)}
    if descriptor != renderer["teachers"].get(teacher):
        raise ValueError("Actual source model/code/environment differs from the recipe")
    jobs = plan["jobs"]
    if len({j["id"] for j in jobs}) != len(jobs) or set(plan["routes"]) != {j["id"] for j in jobs}:
        raise ValueError("Duplicate or missing source routes")
    from make_dataset import FIELDS
    for job in jobs:
        if set(job) != FIELDS or plan["routes"][job["id"]] != route_for(job, renderer["source_delivery_policy"], renderer["reference_profiles"]):
            raise ValueError("Job/route differs from approved A2 policy")
    return descriptor


def clip_key(plan, job):
    return "a2-" + canonical_hash({"source": plan["source_id"], "job": job,
                                  "route": plan["routes"][job["id"]]})[:24]


def read_timing(output, plan, recipe_id):
    path = output / "source-timing.jsonl"
    groups = {g["group_id"]: g for g in plan["batch_groups"]}
    done = {}
    if not path.exists():
        return done
    raw = path.read_text(encoding="utf-8")
    if raw and not raw.endswith("\n"):
        raise ValueError("Torn timing journal; preserve for explicit recovery")
    for line in raw.splitlines():
        row = json.loads(line)
        group = groups.get(row.get("group_id"))
        if (not group or row.get("recipe_id") != recipe_id or row.get("job_ids") != group["job_ids"]
                or row.get("seed") != group["seed"] or row.get("teacher") != group["teacher"]
                or row["group_id"] in done):
            raise ValueError("Invalid timing journal provenance")
        done[row["group_id"]] = row
    return done


def publish_wav(temporary, path):
    """No-replace publication, same-directory filesystem primitives only."""
    if temporary.parent.resolve() != path.parent.resolve() or temporary.is_symlink():
        raise ValueError("Unsafe WAV publication")
    if os.name == "nt":
        os.rename(temporary, path)  # Windows refuses an existing destination.
    else:
        os.link(temporary, path)  # Atomic no-replace; fail on unsupported filesystems.
        temporary.unlink()       # Only the owned, now-published temporary is removed.


class QwenEosObserver:
    """Observe the pinned talker API used by its parent generate implementation."""
    def __init__(self, model, torch):
        self.talker, self.torch = model.model.talker, torch
        self.original = self.talker.generate
        self.eos = model.model.config.talker_config.codec_eos_token_id
        self.last = None
    def install(self):
        def generate(*args, **kwargs):
            result = self.original(*args, **kwargs)
            states = [hidden[-1] for hidden in result.hidden_states if hidden[-1] is not None]
            if not states:
                raise ValueError("Qwen returned no inspectable codec states")
            first = self.torch.stack(states, dim=1)[:, :, 0]
            stop = first == self.eos
            self.last = {"eos_present": stop.any(dim=1).detach().cpu().tolist(),
                         "codec_steps": int(first.shape[1]),
                         "first_eos_index": stop.int().argmax(dim=1).detach().cpu().tolist()}
            return result
        self.talker.generate = generate
    def restore(self):
        self.talker.generate = self.original


def cache_key(plan, instruction_name):
    policy = plan["renderer"]["source_delivery_policy"]
    reference = policy["speaker_reference"]
    return "a2-" + canonical_hash({"source_id": plan["source_id"], "reference_sha256": reference["sha256"],
                                  "reference_text": reference["text"], "instruction_name": instruction_name,
                                  "instruction": policy["cosy_instructions"][instruction_name]})


def render(teacher, recipe, model_dir, code_dir):
    output = recipe.parent
    if any(output.glob("source-*-timeout.json")) or any(output.glob("source-*-failure-*.json")):
        raise ValueError("Failed source batch requires explicit review and a fresh directory")
    plan, recipe_id = load_recipe(recipe)
    descriptor = verify_recipe_inputs(plan, teacher, model_dir, code_dir)
    expected = expected_rows(plan)
    done = read_metadata(output, expected)
    timings = read_timing(output, plan, recipe_id)
    jobs = {j["id"]: j for j in plan["jobs"]}
    pending = []
    for group in plan["batch_groups"]:
        if group["teacher"] != teacher:
            continue
        keys = [clip_key(plan, jobs[job_id]) for job_id in group["job_ids"]]
        complete = [key in done for key in keys]
        if any(complete) and not all(complete):
            raise ValueError("Partial batch group is preserved; no reseeding/rerendering individual members")
        if all(complete):
            if group["group_id"] not in timings:
                raise ValueError("Published group lacks its timing receipt; explicit recovery needed")
            continue
        if group["group_id"] in timings:
            raise ValueError("Timing receipt has no complete corresponding audio group")
        for key in keys:
            path = local_path(output, expected[key]["audio"])
            if path.exists() or path.with_name(key + ".writing.wav").exists():
                raise ValueError("Interrupted/orphan WAV is preserved")
        pending.append(group)
    if not pending:
        return
    os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", PYTHONDONTWRITEBYTECODE="1")
    if teacher == "cosy":
        if code_dir is None:
            raise ValueError("Cosy needs its pinned source checkout")
        sys.path[:0] = [str(code_dir.resolve()), str(code_dir.resolve() / "third_party/Matcha-TTS")]
        cache = output / "runtime-cache"
        cache.mkdir(exist_ok=True)
        os.environ.update(HF_HOME=str(cache / "huggingface"), MODELSCOPE_CACHE=str(cache / "modelscope"),
                          MPLCONFIGDIR=str(cache / "matplotlib"))
    import numpy as np
    import soundfile as sf
    import torch
    if not torch.cuda.is_available() or torch.cuda.mem_get_info()[0] < 8 * 1024 ** 3:
        raise ValueError("Need eight GiB free on the local GPU; do not stop other applications")
    model, observer, current_group = None, None, None
    prompts, cosy_keys = {}, {}
    try:
        if teacher == "qwen":
            from qwen_tts import Qwen3TTSModel
            model = Qwen3TTSModel.from_pretrained(str(model_dir.resolve()), device_map="cuda:0",
                                                dtype=torch.bfloat16, attn_implementation="sdpa", local_files_only=True)
            observer = QwenEosObserver(model, torch); observer.install()
            providers = None
            for name in sorted({g["profile"] for g in pending}):
                reference = plan["renderer"]["reference_profiles"]["profiles"][name]
                if name not in ("original", "soft") or file_hash(local_path(ROOT, reference["audio"])) != reference["sha256"]:
                    raise ValueError("Only unchanged approved original/soft Qwen prompts are used")
                prompts[name] = model.create_voice_clone_prompt(ref_audio=str(local_path(ROOT, reference["audio"])),
                                                               ref_text=reference["text"], x_vector_only_mode=False)
                if len(prompts[name]) != 1:
                    raise ValueError("Expected exactly one approved Qwen reference item")
        else:
            from cosyvoice.cli.cosyvoice import AutoModel
            from cosyvoice.utils.common import set_all_random_seed
            model = AutoModel(model_dir=str(model_dir.resolve()), fp16=True, load_trt=False, load_vllm=False)
            if model.__class__.__name__ != "CosyVoice3" or model.sample_rate != FEATURES["sample_rate"]:
                raise ValueError("Wrong Cosy class/sample rate")
            model.frontend.speech_tokenizer_session.set_providers(["CPUExecutionProvider"])
            model.frontend.campplus_session.set_providers(["CPUExecutionProvider"])
            providers = {"tokenizer": model.frontend.speech_tokenizer_session.get_providers(),
                         "speaker": model.frontend.campplus_session.get_providers()}
            if any(value != ["CPUExecutionProvider"] for value in providers.values()):
                raise ValueError("Actual ONNX provider readback differs")
            policy = plan["renderer"]["source_delivery_policy"]
            reference = policy["speaker_reference"]
            if file_hash(local_path(ROOT, reference["audio"])) != reference["sha256"]:
                raise ValueError("Original A2 speaker reference changed")
            # Add separate instruction-specific entries; never save_spkinfo or write model_dir.
            for name in sorted({g["instruction"] for g in plan["batch_groups"] if g["teacher"] == "cosy"}):
                key, instruction = cache_key(plan, name), policy["cosy_instructions"][name]
                if key in model.frontend.spk2info:
                    raise ValueError("Instruction cache key unexpectedly existed before this invocation")
                if model.add_zero_shot_spk(instruction, str(local_path(ROOT, reference["audio"])), key) is not True:
                    raise ValueError("Cosy did not create the isolated in-memory reference cache")
                tokens, length = model.frontend._extract_text_token(instruction)
                saved = model.frontend.spk2info[key]
                if (not torch.equal(saved["prompt_text"], tokens) or not torch.equal(saved["prompt_text_len"], length)
                        or "text" in saved or "text_len" in saved):
                    raise ValueError("Cosy cache does not bind exactly the intended instruction tokens")
                cosy_keys[name] = key
        gpu = torch.cuda.get_device_properties(0)
        runtime = {"schema_version": 1, "recipe_id": recipe_id, "teacher": teacher,
                   "descriptor_id": canonical_hash(descriptor), "model_class": model.__class__.__name__,
                   "torch_device": "cuda:0", "onnx_providers": providers,
                   "optimization_id": canonical_hash(plan["renderer"]["optimization"]),
                   "gpu_name": gpu.name, "gpu_total_memory_bytes": gpu.total_memory,
                   "cuda_version": torch.version.cuda, "cudnn_version": torch.backends.cudnn.version(),
                   "qwen_eos_observer": teacher == "qwen", "cosy_cache_keys": cosy_keys,
                   "cosy_model_directory_written": False, "audio_acceptance": "pending", "student_training_started": False}
        receipt = output / ("source-" + teacher + "-runtime.json")
        if receipt.exists():
            if json.loads(receipt.read_text(encoding="utf-8")) != runtime:
                raise ValueError("Runtime provenance differs from the prior attempt")
        else:
            write_new_json(receipt, runtime)
        for group in pending:
            current_group = group
            group_jobs = [jobs[job_id] for job_id in group["job_ids"]]
            torch.cuda.synchronize(); torch.cuda.reset_peak_memory_stats()
            started = time.monotonic()
            if teacher == "qwen":
                if any(any(event_counts(j["text"]).values()) for j in group_jobs):
                    raise ValueError("Qwen cannot render a nonverbal event marker")
                reference = plan["renderer"]["reference_profiles"]["profiles"][group["profile"]]
                if file_hash(local_path(ROOT, reference["audio"])) != reference["sha256"]:
                    raise ValueError("Qwen reference changed mid-run")
                torch.manual_seed(group["seed"]); torch.cuda.manual_seed_all(group["seed"])
                observer.last = None
                wavs, rate = model.generate_voice_clone(text=[j["text"] for j in group_jobs], language="English",
                    voice_clone_prompt=prompts[group["profile"]], non_streaming_mode=True, do_sample=True,
                    temperature=.75, top_p=.9, max_new_tokens=600)
                eos = observer.last
                if len(wavs) != len(group_jobs) or eos is None or eos["eos_present"] != [True] * len(group_jobs):
                    raise ValueError("Qwen output inventory or EOS completion differs; capped audio is not published")
                arrays = [np.asarray(wav, dtype=np.float32) for wav in wavs]
            else:
                job = group_jobs[0]
                if len(group_jobs) != 1 or job["emotion"] == "neutral":
                    raise ValueError("Cosy must stay serial and may never generate rejected neutral")
                if file_hash(local_path(ROOT, reference["audio"])) != reference["sha256"]:
                    raise ValueError("Cosy original A2 reference changed mid-run")
                key = cosy_keys[group["instruction"]]
                if key != cache_key(plan, group["instruction"]) or key not in model.frontend.spk2info:
                    raise ValueError("Cosy cache identity changed")
                set_all_random_seed(group["seed"])
                chunks = [item["tts_speech"].detach().float().cpu().numpy().reshape(-1)
                          for item in model.inference_instruct2(job["text"], policy["cosy_instructions"][group["instruction"]],
                              str(local_path(ROOT, reference["audio"])), zero_shot_spk_id=key,
                              stream=False, speed=1.0, text_frontend=False)]
                if not chunks:
                    raise ValueError("Cosy returned no source audio")
                arrays, rate, eos = [np.concatenate(chunks).astype(np.float32)], model.sample_rate, None
            torch.cuda.synchronize()
            seconds = time.monotonic() - started
            # Validate every generated member before publishing any member of this group.
            for job, audio in zip(group_jobs, arrays):
                audio_bounds(audio, rate, np, job["id"])
            prepared = []
            for job, audio in zip(group_jobs, arrays):
                key = clip_key(plan, job)
                path = local_path(output, expected[key]["audio"])
                temporary = path.with_name(key + ".writing.wav")
                with temporary.open("xb") as stream:
                    sf.write(stream, audio, rate, format="WAV", subtype="PCM_16")
                    stream.flush(); os.fsync(stream.fileno())
                stored, stored_rate = sf.read(temporary, dtype="float32")
                audio_bounds(stored, stored_rate, np, job["id"] + " PCM")
                prepared.append((key, path, temporary))
            for key, path, temporary in prepared:
                publish_wav(temporary, path)
                row = dict(expected[key], sha256=file_hash(path))
                with (output / "metadata.jsonl").open("a", encoding="utf-8", newline="\n") as stream:
                    stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
                    stream.flush(); os.fsync(stream.fileno())
                done[key] = row
            timing = {"recipe_id": recipe_id, **group, "inference_seconds": seconds,
                      "audio_seconds": [len(a) / rate for a in arrays], "qwen_completion": eos,
                      "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
                      "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
                      "free_memory_bytes_after": torch.cuda.mem_get_info()[0],
                      "timing_scope": "GPU-synchronized inference only; excludes loading/prompt setup/publication",
                      "source_acceptance": "pending"}
            with (output / "source-timing.jsonl").open("a", encoding="utf-8", newline="\n") as stream:
                stream.write(json.dumps(timing, ensure_ascii=False, allow_nan=False) + "\n")
                stream.flush(); os.fsync(stream.fileno())
            print("OPTIMIZED SOURCE %d/%d teacher=%s group=%s jobs=%d render=%.2fs audio=%.2fs (pending review)" %
                  (len(done), len(expected), teacher, group["group_id"][:12], len(group_jobs), seconds,
                   sum(timing["audio_seconds"])), flush=True)
    except Exception as error:
        write_new_json(output / ("source-" + teacher + "-failure-" + uuid.uuid4().hex + ".json"),
                       {"schema_version": 1, "recipe_id": recipe_id, "teacher": teacher,
                        "group_id": current_group["group_id"] if current_group else None,
                        "error_type": type(error).__name__, "error": str(error),
                        "student_training_started": False,
                        "recovery": "preserve all outputs/temporaries; review explicitly; no automatic batch-size fallback"})
        raise
    finally:
        if observer is not None:
            observer.restore()
        if model is not None and teacher == "cosy":
            for key in cosy_keys.values():
                model.frontend.spk2info.pop(key, None)
        prompts.clear(); cosy_keys.clear()
        del model
        gc.collect(); torch.cuda.empty_cache()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--describe", choices=PACKAGES)
    mode.add_argument("--teacher", choices=PACKAGES)
    parser.add_argument("--recipe", type=Path)
    parser.add_argument("--model-dir", type=Path)
    parser.add_argument("--code-dir", type=Path)
    args = parser.parse_args()
    if args.describe:
        print(json.dumps(environment_descriptor(args.describe), ensure_ascii=False, sort_keys=True))
        return
    if args.recipe is None or args.model_dir is None:
        raise ValueError("Source authoring needs recipe and model directory")
    render(args.teacher, args.recipe.resolve(), args.model_dir, args.code_dir)


if __name__ == "__main__":
    main()
