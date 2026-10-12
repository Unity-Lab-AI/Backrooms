"""Render original voice candidates locally using an explicitly downloaded teacher.

No model download, paid training, stream playback, runtime replacement or approval occurs.
Use the isolated qwen-tts environment and --model-dir pointing to the pinned snapshot.
Raw WAVs and modest equal-level listening copies are saved with provenance receipts.
"""
import argparse
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import time


def file_hash(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--candidates", default="A,B,C")
    parser.add_argument("--brief", type=Path, default=Path(__file__).with_name("AUDITION_BRIEF.json"))
    args = parser.parse_args()
    brief = json.loads(args.brief.read_text(encoding="utf-8"))
    model_dir = args.model_dir.resolve()
    source = json.loads((model_dir / "audition-source.json").read_text(encoding="utf-8"))
    if source["repo"] != brief["source_repo"] or source["revision"] != brief["source_revision"]:
        raise SystemExit("Model snapshot differs from the audition brief")
    config = json.loads((model_dir / "config.json").read_text(encoding="utf-8"))
    if config.get("tts_model_type") != "voice_design":
        raise SystemExit("This audition requires the reviewed VoiceDesign variant")
    wanted = args.candidates.split(",")
    candidates = [c for c in brief["candidates"] if c["id"] in wanted]
    if len(candidates) != len(set(wanted)):
        raise SystemExit("Unknown or repeated candidate ID")
    args.out.mkdir(parents=True, exist_ok=True)
    for candidate in candidates:
        if (args.out / (candidate["id"] + ".wav")).exists():
            raise SystemExit("Refusing to overwrite an existing audition; choose a fresh output directory")

    # Existing local models only. Inference cannot implicitly fetch another model.
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    import numpy as np
    import soundfile as sf
    import torch
    from qwen_tts import Qwen3TTSModel
    if not torch.cuda.is_available():
        raise SystemExit("CUDA unavailable; no CPU or paid fallback was selected")
    free, _total = torch.cuda.mem_get_info()
    if free < 8 * 1024 ** 3:
        raise SystemExit("Less than 8GiB GPU memory free; leave the active rig alone and retry later")
    print("Loading pinned local audition model", flush=True)
    model = Qwen3TTSModel.from_pretrained(
        str(model_dir), device_map="cuda:0", dtype=torch.bfloat16,
        attn_implementation="sdpa", local_files_only=True,
    )
    receipt = {
        "schema_version": 1, "source": source,
        "brief_sha256": file_hash(args.brief),
        "script_sha256": file_hash(Path(__file__)),
        "text": brief["text"], "device": torch.cuda.get_device_name(),
        "versions": {p: importlib.metadata.version(p) for p in
                     ("qwen-tts", "torch", "transformers", "accelerate", "soundfile")},
        "generation": {"max_new_tokens": 900, "temperature": 0.8, "top_p": 0.9},
        "owner_approval": None, "candidates": [],
    }
    for candidate in candidates:
        torch.manual_seed(brief["seed"])
        torch.cuda.manual_seed_all(brief["seed"])
        torch.cuda.reset_peak_memory_stats()
        started = time.monotonic()
        instruction = candidate["identity"] + " " + brief["delivery"]
        print("Rendering", candidate["id"], candidate["label"], flush=True)
        wavs, sr = model.generate_voice_design(
            text=brief["text"], language="English", instruct=instruction,
            non_streaming_mode=True, do_sample=True, temperature=0.8,
            top_p=0.9, max_new_tokens=900,
        )
        audio = np.asarray(wavs[0], dtype=np.float32).reshape(-1)
        if not audio.size or not np.isfinite(audio).all():
            raise RuntimeError("Empty or non-finite teacher output")
        duration = len(audio) / sr
        if duration > 65:
            raise RuntimeError("Audition exceeded its duration bound; keep it out of the candidate set")
        peak = float(np.max(np.abs(audio)))
        rms = float(np.sqrt(np.mean(audio.astype(np.float64) ** 2)))
        if peak <= 0 or peak >= 1 or rms <= 1e-5:
            raise RuntimeError("Silence or saturated teacher output; needs review")
        raw = args.out / (candidate["id"] + "-raw.wav")
        sf.write(raw, audio, sr, subtype="PCM_16")
        # Match broad RMS level with a safe peak ceiling; no pitch/time/effect changes.
        gain = min(10 ** (-22 / 20) / rms, 0.89 / peak)
        listen = args.out / (candidate["id"] + ".wav")
        sf.write(listen, audio * gain, sr, subtype="PCM_16")
        row = {
            **candidate, "instruction": instruction, "seed": brief["seed"],
            "sample_rate": sr, "seconds": duration,
            "render_seconds": time.monotonic() - started,
            "gpu_peak_allocated_mib": torch.cuda.max_memory_allocated() / 1024 ** 2,
            "raw_peak": peak, "raw_rms": rms, "listening_gain": gain,
            "raw_wav": raw.name, "raw_sha256": file_hash(raw),
            "wav": listen.name, "sha256": file_hash(listen),
        }
        receipt["candidates"].append(row)
        (args.out / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
        print("READY", candidate["id"], str(listen.resolve()),
              "seconds=%.2f" % duration, flush=True)
    del model
    torch.cuda.empty_cache()
    print("Audition pack complete. Listening approval is still pending.", flush=True)


if __name__ == "__main__":
    main()
