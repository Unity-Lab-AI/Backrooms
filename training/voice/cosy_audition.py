"""Audition genuine delivery controls and laughter using ONLY the original A2 reference.

Pinned local CosyVoice3 source tool, no automatic download, training or deployment.
English target speech; a supported instruction path controls performance separately
from speaker/flow conditioning. Naturalness and A2 identity still need listening. The rejected neutral example is excluded.
The original A2 calm reference is never replaced by a Cosy neutral render.
"""
import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from dataset_contract import file_hash, local_path

ROOT = Path(__file__).resolve().parents[2]
REPO = "FunAudioLLM/Fun-CosyVoice3-0.5B-2512"
REVISION = "29e01c4e8d000f4bcd70751be16fa94bf3d85a18"
CODE = "074ca6dc9e80a2f424f1f74b48bdd7d3fea531cc"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--code-dir", type=Path, required=True)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists() and any(args.out.iterdir()):
        raise ValueError("Choose a new directory; existing auditions are preserved")
    selected = json.loads((ROOT / "training/voice/SELECTED_VOICE.json").read_text(encoding="utf-8"))
    reference = local_path(ROOT, selected["reference_audio"])
    if file_hash(reference) != selected["reference_sha256"]:
        raise ValueError("The original approved A2 recording changed")
    source = json.loads((args.model_dir / "audition-source.json").read_text(encoding="utf-8"))
    if (source["repo"], source["revision"]) != (REPO, REVISION):
        raise ValueError("Wrong pinned source model")
    code_dir = args.code_dir.resolve()
    commit = subprocess.check_output(["git", "-C", str(code_dir), "rev-parse", "HEAD"], text=True).strip()
    if commit != CODE:
        raise ValueError("Unexpected source code revision")
    sys.path[:0] = [str(code_dir), str(code_dir / "third_party/Matcha-TTS")]
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    cache = ROOT / ".local/voice-lab/models/cosy-runtime-cache"
    cache.mkdir(exist_ok=True)
    os.environ["HF_HOME"] = str(cache / "huggingface")
    os.environ["MODELSCOPE_CACHE"] = str(cache / "modelscope")
    os.environ["MPLCONFIGDIR"] = str(cache / "matplotlib")
    import numpy as np
    import soundfile as sf
    import torch
    from cosyvoice.cli.cosyvoice import AutoModel
    from cosyvoice.utils.common import set_all_random_seed
    if not torch.cuda.is_available() or torch.cuda.mem_get_info()[0] < 8 * 1024 ** 3:
        raise ValueError("Insufficient free local GPU memory")
    if torch.__version__ != "2.7.1+cu118":
        raise ValueError("Audition setup must preserve the existing rig's Torch version")
    model = AutoModel(model_dir=str(args.model_dir.resolve()), fp16=True, load_trt=False, load_vllm=False)
    # Official Windows wheel uses CPU ONNX. Be explicit about the actual provider;
    # Torch synthesis remains CUDA. No all-GPU or runtime coexistence claim.
    model.frontend.speech_tokenizer_session.set_providers(["CPUExecutionProvider"])
    providers = {"tokenizer": model.frontend.speech_tokenizer_session.get_providers(),
                 "speaker": model.frontend.campplus_session.get_providers()}
    jobs = [
        {"id": "2-natural-happy", "text": "I'm in a good mood now.",
         "instruction": "You are a helpful assistant. 请用自然、真诚、轻松开心的语气说话，不要夸张，不要尖叫，也不要讽刺。<|endofprompt|>",
         "control_status": "free-form restrained genuine happiness; audition experiment"},
        {"id": "4-little-chuckle", "text": "I had a plan. [laughter] Okay, that was not the plan.",
         "instruction": "You are a helpful assistant. 请用自然、轻松、带着微笑的语气说话。<|endofprompt|>",
         "control_status": "trained laughter token with free-form relaxed smiling delivery; check actual chuckle"},
    ]
    args.out.mkdir(parents=True, exist_ok=True)
    receipt = {"schema_version": 1, "source": source, "code_commit": commit,
               "script_sha256": file_hash(Path(__file__)), "voice_id": selected["voice_id"],
               "reference_audio": selected["reference_audio"], "reference_sha256": selected["reference_sha256"],
               "mode": "official instruction+reference API; original A2 only; mixed CPU ONNX/CUDA Torch",
               "providers": providers, "speaker_identity_preservation": "unverified until listening",
               "model_files_sha256": {p.relative_to(args.model_dir).as_posix(): file_hash(p)
                                      for p in sorted(args.model_dir.rglob("*")) if p.is_file() and ".cache" not in p.parts},
               "versions": {x: importlib.metadata.version(x) for x in
                            ("torch", "torchaudio", "numpy", "transformers", "diffusers", "onnxruntime", "soundfile")},
               "seed": 11032, "speed": 1.0, "text_frontend": False, "fp16": True,
               "owner_acceptance": None, "student_training_started": False, "clips": []}
    for job in jobs:
        set_all_random_seed(11032)
        torch.cuda.reset_peak_memory_stats()
        started = time.monotonic()
        chunks = []
        for output in model.inference_instruct2(job["text"], job["instruction"], str(reference),
                                               stream=False, speed=1.0, text_frontend=False):
            chunks.append(output["tts_speech"].detach().float().cpu().numpy().reshape(-1))
        if not chunks:
            raise ValueError("No source audio returned")
        audio = np.concatenate(chunks)
        rate = model.sample_rate
        peak, rms = float(np.max(np.abs(audio))), float(np.sqrt(np.mean(audio.astype(np.float64) ** 2)))
        if rate != 24000 or not np.isfinite(audio).all() or not .25 <= len(audio) / rate <= 30 or peak >= 1 or rms < 1e-5:
            raise ValueError("Invalid local source audio")
        raw = args.out / (job["id"] + "-raw.wav")
        listening = args.out / (job["id"] + ".wav")
        sf.write(raw, audio, rate, subtype="PCM_16")
        gain = min(10 ** (-22 / 20) / rms, .89 / peak)
        sf.write(listening, audio * gain, rate, subtype="PCM_16")
        receipt["clips"].append({**job, "seconds": len(audio) / rate, "render_seconds": time.monotonic() - started,
                                 "raw": raw.name, "raw_sha256": file_hash(raw),
                                 "listening": listening.name, "listening_sha256": file_hash(listening),
                                 "gain_only": gain, "gpu_peak_mib": torch.cuda.max_memory_allocated() / 1024 ** 2})
        with (args.out / "receipt.json").open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(receipt, stream, indent=2, ensure_ascii=False); stream.write("\n")
        print("ACTING AUDITION", job["id"], "%.2fs" % (len(audio) / rate), flush=True)
    del model; torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
