"""Reference-anchored variations of the owner-selected original A2 audition.

No paid work, training, runtime replacement, approval or automatic download.
The selected raw reference and source revision are verified before generation.
Intended delivery labels are not proof of successful emotion or identity preservation.
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import time


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    here = Path(__file__).resolve().parent
    root = here.parent.parent
    config_path = here / "A2_VARIATIONS.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    folder = root / config["reference_folder"]
    reference_receipt = json.loads((folder / "receipt.json").read_text(encoding="utf-8"))
    reference = next(c for c in reference_receipt["candidates"] if c["id"] == config["reference_candidate"])
    raw = folder / reference["raw_wav"]
    listen = folder / reference["wav"]
    selection = reference_receipt.get("owner_approval") or {}
    if selection.get("candidate") != config["reference_candidate"] or not selection.get("quote"):
        raise SystemExit("No recorded owner selection of the reference identity")
    if sha(raw) != config["reference_sha256"] or sha(raw) != reference["raw_sha256"] or sha(listen) != reference["sha256"]:
        raise SystemExit("Selected reference WAV no longer matches its recording")
    model_dir = args.model_dir.resolve()
    source = json.loads((model_dir / "audition-source.json").read_text(encoding="utf-8"))
    if source["repo"] != config["source_repo"] or source["revision"] != config["source_revision"]:
        raise SystemExit("Wrong source model revision")
    if json.loads((model_dir / "config.json").read_text(encoding="utf-8")).get("tts_model_type") != "base":
        raise SystemExit("Reference variants require the reviewed Base model")
    if args.out.exists() and any(args.out.iterdir()):
        raise SystemExit("Use a fresh variation output folder; existing auditions are preserved")
    args.out.mkdir(parents=True, exist_ok=True)
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    import numpy as np
    import soundfile as sf
    import torch
    from qwen_tts import Qwen3TTSModel
    if not torch.cuda.is_available() or torch.cuda.mem_get_info()[0] < 8 * 1024 ** 3:
        raise SystemExit("Insufficient free local CUDA memory; no fallback selected")
    model = Qwen3TTSModel.from_pretrained(str(model_dir), device_map="cuda:0", dtype=torch.bfloat16,
                                        attn_implementation="sdpa", local_files_only=True)
    print("Building reusable A2 reference prompt", flush=True)
    prompt = model.create_voice_clone_prompt(ref_audio=str(raw), ref_text=reference_receipt["text"],
                                             x_vector_only_mode=False)
    original = args.out / "0-original-A2.wav"
    shutil.copyfile(listen, original)
    receipt = {"schema_version": 1, "source": source, "config_sha256": sha(config_path),
               "script_sha256": sha(Path(__file__)), "reference_raw_sha256": sha(raw),
               "original_wav": original.name, "original_sha256": sha(original),
               "reference_selection": selection, "owner_variation_approval": None,
               "versions": {p: importlib.metadata.version(p) for p in
                            ("qwen-tts", "torch", "transformers", "accelerate", "soundfile")},
               "mode": "reference-anchored Base synthesis; intended emotions conveyed through text/context",
               "generation": {"max_new_tokens": 650, "temperature": 0.75, "top_p": 0.9},
               "profiles": []}
    for index, profile in enumerate(config["profiles"]):
        torch.manual_seed(config["seed"] + index)
        torch.cuda.manual_seed_all(config["seed"] + index)
        torch.cuda.reset_peak_memory_stats()
        start = time.monotonic()
        print("Rendering", profile["id"], flush=True)
        wavs, sr = model.generate_voice_clone(text=profile["text"], language="English",
                                             voice_clone_prompt=prompt, non_streaming_mode=True,
                                             do_sample=True, temperature=0.75, top_p=0.9, max_new_tokens=650)
        audio = np.asarray(wavs[0], dtype=np.float32).reshape(-1)
        if not audio.size or not np.isfinite(audio).all() or len(audio) / sr > 50:
            raise RuntimeError("Invalid or overlong source output")
        peak = float(np.max(np.abs(audio)))
        rms = float(np.sqrt(np.mean(audio.astype(np.float64) ** 2)))
        if peak <= 0 or peak >= 1 or rms <= 1e-5:
            raise RuntimeError("Silent or saturated source output")
        raw_out = args.out / (profile["id"] + "-raw.wav")
        sf.write(raw_out, audio, sr, subtype="PCM_16")
        gain = min(10 ** (-22 / 20) / rms, 0.89 / peak)
        out = args.out / (profile["id"] + ".wav")
        sf.write(out, audio * gain, sr, subtype="PCM_16")
        receipt["profiles"].append({**profile, "seed": config["seed"] + index,
                                   "sample_rate": sr, "seconds": len(audio) / sr,
                                   "render_seconds": time.monotonic() - start,
                                   "gpu_peak_allocated_mib": torch.cuda.max_memory_allocated() / 1024 ** 2,
                                   "listening_gain": gain, "wav": out.name, "sha256": sha(out),
                                   "raw_wav": raw_out.name, "raw_sha256": sha(raw_out)})
        (args.out / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
        print("READY", str(out.resolve()), "seconds=%.2f" % (len(audio) / sr), flush=True)
    del model
    torch.cuda.empty_cache()
    print("A2 variants rendered; listening approval remains pending.", flush=True)


if __name__ == "__main__":
    main()
