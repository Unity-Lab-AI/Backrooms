"""Focused local acting auditions after the owner rejected a flat happy A2 line.

Base attempts preserve the approved speaker reference and use performed context.
VoiceDesign attempts are NEW reference candidates: identity continuity is unproven.
No source approval, training, deployment, automatic download or pitch effects.
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import time

from dataset_contract import file_hash, local_path

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("base", "design"), required=True)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists() and any(args.out.iterdir()):
        raise ValueError("Choose a fresh audition directory; previous audio is preserved")
    selected = json.loads((ROOT / "training/voice/SELECTED_VOICE.json").read_text(encoding="utf-8"))
    profiles = json.loads((ROOT / selected["delivery_profiles"]).read_text(encoding="utf-8"))
    source = json.loads((args.model_dir / "audition-source.json").read_text(encoding="utf-8"))
    expected = (("Qwen/Qwen3-TTS-12Hz-1.7B-Base", "fd4b254389122332181a7c3db7f27e918eec64e3")
                if args.mode == "base" else
                ("Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign", "5ecdb67327fd37bb2e042aab12ff7391903235d3"))
    if (source["repo"], source["revision"]) != expected:
        raise ValueError("Wrong pinned source model")
    ref = profiles["profiles"]["playful"]
    reference = local_path(ROOT, ref["audio"])
    if file_hash(reference) != ref["sha256"]:
        raise ValueError("Approved playful A2 reference changed")
    if args.mode == "base":
        jobs = [
            {"id": "B1-same-line", "text": "I'm in a good mood now!", "seed": 11101},
            {"id": "B2-happy-context", "text": "Oh, yes! I'm in a GOOD mood now! That just made my day. Come on, let's do it!", "seed": 11102},
        ]
        instruction = None
    else:
        jobs = [
            {"id": "D1-smiling-happy", "text": "I'm in a good mood now! That actually worked! Did you see it? Oh, I am so happy right now!", "seed": 11032},
            {"id": "D2-real-excitement", "text": "Oh, yes! We did it! I'm in a good mood now! That was amazing. Let's do that again!", "seed": 11032},
        ]
        instruction = (
            "An original young adult woman in her twenties speaking General American English. "
            "Her voice is a LOW warm alto with rich rounded chest resonance, slight natural huskiness, "
            "full vocal body and grounded friendly gamer-coder confidence. Keep an adult speaking "
            "identity, no girlish squeak or thin nasal voice. She is GENUINELY HAPPY about a real win "
            "and talking excitedly to a close friend. You can hear the smile and delight in her voice: "
            "bright living energy, expressive rhythm, clear emphasized happy words, varied phrase "
            "beginnings and endings, spontaneous connected speech and audible joyful pitch motion. "
            "Her low register remains the comfortable home while lively inflections move naturally. "
            "This must sound joyful and excited, not a calm report stating that she is happy. "
            "No shouting, shrieking, exaggerated baby voice, sing-song performance or forced laughter. "
            "Let energy and expressive phrasing convey genuine pleasure while retaining warm adult resonance."
        )
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    import numpy as np
    import soundfile as sf
    import torch
    from qwen_tts import Qwen3TTSModel
    if not torch.cuda.is_available() or torch.cuda.mem_get_info()[0] < 8 * 1024 ** 3:
        raise ValueError("Insufficient free local GPU memory")
    model = Qwen3TTSModel.from_pretrained(str(args.model_dir.resolve()), device_map="cuda:0",
                                        dtype=torch.bfloat16, attn_implementation="sdpa", local_files_only=True)
    prompt = (model.create_voice_clone_prompt(ref_audio=str(reference), ref_text=ref["text"],
                                             x_vector_only_mode=False) if args.mode == "base" else None)
    args.out.mkdir(parents=True, exist_ok=True)
    receipt = {"schema_version": 1, "purpose": "happy acting remedy; not source/training approval",
               "source": source, "mode": args.mode, "owner_correction": selected["corpus_preview_feedback"]["specific_correction"],
               "instruction": instruction, "reference": ref if args.mode == "base" else None,
               "identity_status": "approved A2 reference used" if args.mode == "base" else "new description-guided reference candidate; compare with A2",
               "script_sha256": file_hash(Path(__file__)),
               "versions": {name: importlib.metadata.version(name) for name in ("qwen-tts", "torch", "transformers", "soundfile")},
               "generation": {"max_new_tokens": 600, "temperature": .75, "top_p": .9},
               "owner_acceptance": None, "student_training_started": False, "clips": []}
    for job in jobs:
        torch.manual_seed(job["seed"]); torch.cuda.manual_seed_all(job["seed"])
        start = time.monotonic()
        kwargs = dict(text=job["text"], language="English", non_streaming_mode=True,
                      do_sample=True, temperature=.75, top_p=.9, max_new_tokens=600)
        if args.mode == "base":
            wavs, rate = model.generate_voice_clone(voice_clone_prompt=prompt, **kwargs)
        else:
            wavs, rate = model.generate_voice_design(instruct=instruction, **kwargs)
        audio = np.asarray(wavs[0], dtype=np.float32).reshape(-1)
        peak = float(np.max(np.abs(audio)))
        rms = float(np.sqrt(np.mean(audio.astype(np.float64) ** 2)))
        if rate != 24000 or not np.isfinite(audio).all() or not .25 <= len(audio) / rate <= 30 or peak >= 1 or rms < 1e-5:
            raise ValueError("Invalid source audition")
        raw = args.out / (job["id"] + "-raw.wav")
        listen = args.out / (job["id"] + ".wav")
        sf.write(raw, audio, rate, subtype="PCM_16")
        gain = min(10 ** (-22 / 20) / rms, .89 / peak)
        sf.write(listen, audio * gain, rate, subtype="PCM_16")
        receipt["clips"].append({**job, "raw": raw.name, "raw_sha256": file_hash(raw),
                                 "listening": listen.name, "listening_sha256": file_hash(listen),
                                 "seconds": len(audio) / rate, "render_seconds": time.monotonic() - start,
                                 "gain_only": gain})
        with (args.out / "receipt.json").open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(receipt, stream, indent=2); stream.write("\n")
        print("HAPPY AUDITION", job["id"], "%.2fs" % (len(audio) / rate), flush=True)
    del model; torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
