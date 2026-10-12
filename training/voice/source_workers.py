"""Isolated sequential source workers; never a deployed speaking path.

--describe inspects installed distributions only (no Torch/model import or GPU load).
Rendering reads the builder's immutable schema-3 recipe, validates its exact inputs,
and publishes only pending-review WAV/metadata. No downloads or student training.
Qwen and Cosy must use their own reviewed Python environments.
"""
import argparse
import gc
import importlib.metadata
import json
import os
from pathlib import Path
import re
import sys

from dataset_contract import FEATURES, canonical_hash, file_hash, local_path
from make_dataset import (ROOT, FIELDS, WORKER, expected_rows, load_recipe, read_metadata,
                          route_for, teacher_inputs, write_new_json)
from speech_text import event_counts


PACKAGES = {
    "qwen": ("qwen-tts", "torch", "torchaudio", "numpy", "transformers", "accelerate", "soundfile"),
    "cosy": ("torch", "torchaudio", "numpy", "transformers", "diffusers", "onnxruntime", "soundfile"),
}


def _version(name):
    # On the Linux pod Cosy runs the CUDA build, which registers as onnxruntime-gpu; the recorded key stays "onnxruntime".
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        if name == "onnxruntime":
            return importlib.metadata.version("onnxruntime-gpu")
        raise


def environment_descriptor(teacher):
    versions = {name: _version(name) for name in PACKAGES[teacher]}
    if teacher == "qwen" and (versions["qwen-tts"] != "0.1.1" or versions["transformers"] != "4.57.3"):
        raise ValueError("Qwen worker requires the reviewed qwen-tts0.1.1 / Transformers4.57.3 environment")
    if teacher == "cosy" and (versions["torch"] != "2.7.1+cu118" or versions["transformers"] != "4.51.3"):
        raise ValueError("Cosy worker must preserve the reviewed Torch2.7.1cu118 / Transformers4.51.3 environment")
    # System-site-enabled venvs expose shadowed global distributions too. Resolve
    # each normalized name once through the same sys.path lookup used above.
    installed = {}
    for dist in importlib.metadata.distributions():
        name = dist.metadata.get("Name")
        if name:
            key = re.sub(r"[-_.]+", "-", name).lower()
            if key not in installed:
                installed[key] = importlib.metadata.version(name)
    result = {"schema_version": 1, "teacher": teacher, "python_version": sys.version.split()[0],
              "python_executable_sha256": file_hash(Path(sys.executable)), "platform": sys.platform,
              "versions": versions, "installed_versions": dict(sorted(installed.items()))}
    if teacher == "qwen":
        dist = importlib.metadata.distribution("qwen-tts")
        result["qwen_package_files_sha256"] = {str(name).replace("\\", "/"): file_hash(dist.locate_file(name))
            for name in sorted(dist.files or [], key=str) if str(name).replace("\\", "/").startswith("qwen_tts/")
            and Path(name).suffix in (".py", ".json", ".txt")}
        if not result["qwen_package_files_sha256"]:
            raise ValueError("Qwen installed source inventory is missing")
    return result


def verify_recipe_inputs(plan, recipe_id, teacher, model_dir, code_dir):
    renderer = plan["renderer"]
    checks = {
        "builder_sha256": Path(__file__).with_name("make_dataset.py"), "worker_sha256": WORKER,
        "contract_sha256": Path(__file__).with_name("dataset_contract.py"),
        "speech_text_sha256": Path(__file__).with_name("speech_text.py"),
        "selected_config_sha256": Path(__file__).with_name("SELECTED_VOICE.json"),
        "reference_profiles_sha256": local_path(ROOT, renderer["selected_config"]["delivery_profiles"]),
        "source_delivery_policy_sha256": Path(__file__).with_name("SOURCE_DELIVERY_POLICY.json"),
        "approval_receipt_sha256": Path(__file__).parent / "receipts/source-auditions.json",
    }
    if any(file_hash(path) != renderer[key] for key, path in checks.items()):
        raise ValueError("Source/config/frontend/approval changed during rendering; preserve this batch")
    actual = {"inputs": teacher_inputs(teacher, model_dir, code_dir), "environment": environment_descriptor(teacher)}
    if actual != renderer["teachers"].get(teacher):
        raise ValueError("Worker model/code/environment differs from the immutable source recipe")
    ids = [job["id"] for job in plan["jobs"]]
    if len(ids) != len(set(ids)) or set(plan["routes"]) != set(ids):
        raise ValueError("Recipe has duplicate jobs or mismatched route inventory")
    for job in plan["jobs"]:
        if set(job) != FIELDS or plan["routes"][job["id"]] != route_for(job, renderer["source_delivery_policy"], renderer["reference_profiles"]):
            raise ValueError("Recipe job differs from the explicit approved routing policy")
    return actual


def audio_bounds(audio, rate, np, label):
    if (rate != FEATURES["sample_rate"] or audio.ndim != 1 or not audio.size or not np.isfinite(audio).all()
            or not FEATURES["min_seconds"] <= len(audio) / rate <= FEATURES["max_seconds"]):
        raise ValueError("Source duration/format outside preparation bounds: " + label)
    if (np.max(np.abs(audio)) > 1.0 or np.mean(np.abs(audio) >= 0.999) > .001
            or np.sqrt(np.mean(audio.astype(np.float64) ** 2)) < 1e-5):
        raise ValueError("Source is silent or excessively clipped: " + label)


def render(teacher, recipe, model_dir, code_dir):
    if any(recipe.parent.glob("source-*-timeout.json")):
        raise ValueError("Timed-out source batch requires explicit review; preserve it and use a fresh directory")
    plan, recipe_id = load_recipe(recipe)
    descriptor = verify_recipe_inputs(plan, recipe_id, teacher, model_dir, code_dir)
    output = recipe.parent
    expected = expected_rows(plan)
    done = read_metadata(output, expected)
    pending = []
    for job in plan["jobs"]:
        route = plan["routes"][job["id"]]
        key = "a2-" + canonical_hash({"source": plan["source_id"], "job": job, "route": route})[:24]
        if route["teacher"] == teacher and key not in done:
            path = local_path(output, expected[key]["audio"])
            if path.exists() or path.with_name(key + ".writing.wav").exists():
                raise ValueError("Orphan/torn WAV is preserved; explicit recovery review required")
            pending.append((job, route, key, path))
    if not pending:
        return
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    if teacher == "cosy":
        if code_dir is None:
            raise ValueError("Cosy worker requires its pinned local code directory")
        sys.path[:0] = [str(code_dir.resolve()), str(code_dir.resolve() / "third_party/Matcha-TTS")]
        cache = ROOT / ".local/voice-lab/models/cosy-runtime-cache"
        cache.mkdir(exist_ok=True)
        os.environ["HF_HOME"] = str(cache / "huggingface")
        os.environ["MODELSCOPE_CACHE"] = str(cache / "modelscope")
        os.environ["MPLCONFIGDIR"] = str(cache / "matplotlib")
    import numpy as np
    import soundfile as sf
    import torch
    if not torch.cuda.is_available() or torch.cuda.mem_get_info()[0] < 8 * 1024 ** 3:
        raise ValueError("Insufficient free local GPU memory; do not disturb the active rig")
    model, prompts = None, {}
    try:
        if teacher == "qwen":
            from qwen_tts import Qwen3TTSModel
            model = Qwen3TTSModel.from_pretrained(str(model_dir.resolve()), device_map="cuda:0", dtype=torch.bfloat16,
                                                attn_implementation="sdpa", local_files_only=True)
            providers = None
        else:
            from cosyvoice.cli.cosyvoice import AutoModel
            from cosyvoice.utils.common import set_all_random_seed
            model = AutoModel(model_dir=str(model_dir.resolve()), fp16=True, load_trt=False, load_vllm=False)
            if model.__class__.__name__ != "CosyVoice3" or model.sample_rate != FEATURES["sample_rate"]:
                raise ValueError("Wrong Cosy model class/sample rate")
            # Torch synthesis is CUDA; the reviewed Windows ONNX components are CPU.
            model.frontend.speech_tokenizer_session.set_providers(["CPUExecutionProvider"])
            model.frontend.campplus_session.set_providers(["CPUExecutionProvider"])
            providers = {"tokenizer": model.frontend.speech_tokenizer_session.get_providers(),
                         "speaker": model.frontend.campplus_session.get_providers()}
            if any(value != ["CPUExecutionProvider"] for value in providers.values()):
                raise ValueError("Actual Cosy ONNX provider readback differs from the reviewed CPU route")
        runtime = {"schema_version": 1, "recipe_id": recipe_id, "teacher": teacher,
                   "descriptor_id": canonical_hash(descriptor), "model_class": model.__class__.__name__,
                   "torch_device": "cuda:0", "onnx_providers": providers,
                   "audio_acceptance": "pending", "student_training_started": False}
        receipt = output / ("source-" + teacher + "-runtime.json")
        if receipt.exists():
            if json.loads(receipt.read_text(encoding="utf-8")) != runtime:
                raise ValueError("Existing worker provenance differs; preserve both attempts")
        else:
            write_new_json(receipt, runtime)
        for job, route, key, path in pending:
            seed = int(canonical_hash({"clip": key})[:8], 16)
            if teacher == "qwen":
                if any(event_counts(job["text"]).values()):
                    raise ValueError("Qwen must never speak a literal nonverbal marker")
                torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
                name = route["profile"]
                if name not in prompts:
                    reference = plan["renderer"]["reference_profiles"]["profiles"][name]
                    if file_hash(local_path(ROOT, reference["audio"])) != reference["sha256"]:
                        raise ValueError("Approved Qwen reference changed")
                    prompts[name] = model.create_voice_clone_prompt(ref_audio=str(local_path(ROOT, reference["audio"])),
                        ref_text=reference["text"], x_vector_only_mode=False)
                wavs, rate = model.generate_voice_clone(text=job["text"], language="English", voice_clone_prompt=prompts[name],
                    non_streaming_mode=True, do_sample=True, temperature=.75, top_p=.9, max_new_tokens=600)
                if len(wavs) != 1:
                    raise ValueError("Qwen did not return exactly one utterance")
                audio = np.asarray(wavs[0], dtype=np.float32)
            else:
                if job["emotion"] == "neutral":
                    raise ValueError("Cosy neutral generation is expressly prohibited")
                reference = plan["renderer"]["source_delivery_policy"]["speaker_reference"]
                if file_hash(local_path(ROOT, reference["audio"])) != reference["sha256"]:
                    raise ValueError("Original A2 Cosy speaker reference changed")
                instruction = plan["renderer"]["source_delivery_policy"]["cosy_instructions"][route["instruction"]]
                set_all_random_seed(seed)
                chunks = [item["tts_speech"].detach().float().cpu().numpy().reshape(-1)
                    for item in model.inference_instruct2(job["text"], instruction, str(local_path(ROOT, reference["audio"])),
                        zero_shot_spk_id="", stream=False, speed=1.0, text_frontend=False)]
                if not chunks:
                    raise ValueError("Cosy returned no source audio")
                audio, rate = np.concatenate(chunks).astype(np.float32), model.sample_rate
            audio_bounds(audio, rate, np, job["id"])
            temporary = path.with_name(key + ".writing.wav")
            with temporary.open("xb") as stream:
                sf.write(stream, audio, rate, format="WAV", subtype="PCM_16")
                stream.flush(); os.fsync(stream.fileno())
            stored, stored_rate = sf.read(temporary, dtype="float32")
            audio_bounds(stored, stored_rate, np, job["id"] + " serialized PCM")
            if path.exists():
                raise ValueError("Clip appeared concurrently; preserve this new temporary WAV")
            temporary.rename(path)
            row = dict(expected[key], sha256=file_hash(path))
            with (output / "metadata.jsonl").open("a", encoding="utf-8", newline="\n") as stream:
                stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
                stream.flush(); os.fsync(stream.fileno())
            done[key] = row
            print("SOURCE %d/%d %s teacher=%s route=%s %.2fs (acting/events pending listening)" %
                  (len(done), len(expected), job["id"], teacher, route.get("profile", route.get("instruction")), len(audio) / rate), flush=True)
    finally:
        prompts.clear()
        del model
        gc.collect()
        torch.cuda.empty_cache()
    # Process exit also releases CUDA context before the orchestrator starts the next worker.


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
        raise ValueError("Rendering worker needs --recipe and --model-dir")
    render(args.teacher, args.recipe.resolve(), args.model_dir, args.code_dir)


if __name__ == "__main__":
    main()
