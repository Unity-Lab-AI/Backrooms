"""Expressive source pilot: real emotional range in HER voice (original A2 reference), measured, for the owner to hear.

Owner, 2026-10-13: "are we srue the adio voice retrain is properly set up ... we dont even have clips so how are we
training the human speech mechanics of emotional and in the moment reangess of human english speech?" -> option 2,
"2 but we keep our voice". The 4,845 source clips carry emotion mostly as labels (one intensity 0.35, one pace 1.0,
and the Cosy happy/amused instructions told it to stay restrained), so this re-performs lines with Cosy's instruction
path, three real intensities, emotion-fitting pace, the original A2 recording as the only speaker reference, and keeps
only takes that measure as HER (CAM++ speaker embedding vs A2, calibrated on the approved A2 clips) with the widest
pitch movement. Renders only -- no training, nothing deployed; the owner listens first.

Run with the reviewed Cosy environment, from a %TEMP% folder:
  .local/voice-lab/.venv-cosy/Scripts/python.exe training/voice/expressive_pilot.py
"""
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CODE = ROOT / ".local/voice-lab/models/cosyvoice-code"
MODEL = ROOT / ".local/voice-lab/models/cosyvoice3"
REF = ROOT / "training/voice/reference/A2-reference-raw.wav"
APPROVED = ["A2-everyday-raw.wav", "A2-natural-happy-raw.wav", "A2-chuckle-raw.wav", "A2-playful-raw.wav",
            "A2-questions-raw.wav", "A2-soft-raw.wav"]
OUT = Path(r"D:\voice-lab\expressive-pilot-2026-10-13")
SEEDS = [11032, 2711]
TIERS = {"light": "a little", "medium": "clearly", "strong": "very strongly, fully letting it show"}
# what each emotion sounds like in a real young woman's voice; pace fits the feeling
EMOTIONS = {
    "happy": ("happy and bright, smiling while she talks", 1.05,
              "We actually made it through winter, and nobody ate anybody."),
    "excited": ("excited and hyped, energy rising, a little breathless", 1.12,
                "Oh my gosh, there is a thrumbo out there. It is huge."),
    "amused": ("amused, laughing as she talks, a real giggle in her voice", 1.0,
               "I had a plan. [laughter] Okay, that was not the plan."),
    "sad": ("sad and quiet, voice heavy, close to tears", 0.9,
            "Gee is gone. The man who grew every meal we ate."),
    "frustrated": ("frustrated and exasperated, sighing, sharp on the key words", 1.05,
                   "The kitchen caught fire. Again. Who keeps doing this?"),
    "concerned": ("worried and tense, urgent but controlled", 1.05,
                  "Six pirates on the east edge, and they look fast."),
    "surprised": ("genuinely surprised, pitch jumping up in disbelief", 1.05,
                  "Wait, what is that thing doing in our freezer?"),
    "warm": ("warm and friendly, soft and welcoming, a smile in her voice", 0.98,
             "Hi, welcome in. Grab a seat near the fire."),
    "flirty": ("playful and teasing, a little flirty, smiling", 1.0,
               "Oh, you missed me? That is so sweet of you."),
}


def instruction(feel, tier):
    return ("You are a helpful assistant. Speak English as a real young woman, natural and human, with real pitch "
            "movement: %s %s.<|endofprompt|>" % (TIERS[tier], feel))


def f0_spread(wav, rate):
    import numpy as np
    import pyworld
    w = wav.astype("float64")
    f0, t = pyworld.dio(w, rate, frame_period=10)
    f0 = pyworld.stonemask(w, f0, t, rate)
    s = 12 * np.log2(f0[f0 > 0] / 195.0)
    return float(s.std()) if len(s) > 25 else 0.0


def main():
    sys.path[:0] = [str(CODE), str(CODE / "third_party/Matcha-TTS")]
    os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1")
    cache = ROOT / ".local/voice-lab/models/cosy-runtime-cache"
    os.environ.update(HF_HOME=str(cache / "huggingface"), MODELSCOPE_CACHE=str(cache / "modelscope"),
                      MPLCONFIGDIR=str(cache / "matplotlib"))
    import numpy as np
    import soundfile as sf
    import torch
    from cosyvoice.cli.cosyvoice import AutoModel
    from cosyvoice.utils.common import set_all_random_seed
    if not torch.cuda.is_available() or torch.cuda.mem_get_info()[0] < 6 * 1024 ** 3:
        raise SystemExit("needs ~6 GB of free GPU memory")
    model = AutoModel(model_dir=str(MODEL), fp16=True, load_trt=False, load_vllm=False)
    model.frontend.speech_tokenizer_session.set_providers(["CPUExecutionProvider"])

    def emb(path):
        e = model.frontend._extract_spk_embedding(str(path)).float().reshape(-1)
        return e / e.norm()

    a2 = emb(REF)
    approved = {n: float(emb(ROOT / "training/voice/reference" / n) @ a2) for n in APPROVED
                if (ROOT / "training/voice/reference" / n).exists()}
    floor = min(approved.values()) - 0.05   # as close to A2 as her own approved clips are, minus a small margin
    print("A2 similarity of the approved clips:", approved, "-> keep takes >= %.3f" % floor, flush=True)
    (OUT / "takes").mkdir(parents=True, exist_ok=True)
    (OUT / "listen").mkdir(parents=True, exist_ok=True)
    report = {"owner_request": "2 but we keep our voice", "a2_reference": str(REF), "approved_similarity": approved,
              "similarity_floor": floor, "training_started": False, "cells": []}
    for emo, (feel, speed, text) in EMOTIONS.items():
        for tier in TIERS:
            takes = []
            for seed in SEEDS:
                set_all_random_seed(seed)
                t0 = time.monotonic()
                chunks = [o["tts_speech"].float().cpu().numpy().reshape(-1) for o in
                          model.inference_instruct2(text, instruction(feel, tier), str(REF), stream=False,
                                                    speed=speed, text_frontend=False)]
                audio = np.concatenate(chunks) if chunks else np.zeros(1, "float32")
                rate = model.sample_rate
                path = OUT / "takes" / ("%s-%s-%d.wav" % (emo, tier, seed))
                sf.write(path, audio, rate, subtype="PCM_16")
                sim = float(emb(path) @ a2)
                spread = f0_spread(audio, rate)
                takes.append({"file": path.name, "seed": seed, "a2_similarity": sim, "f0_spread_st": spread,
                              "seconds": len(audio) / rate, "render_s": time.monotonic() - t0})
                print("%-10s %-6s seed %d: A2 sim %.3f, pitch spread %.2f st" % (emo, tier, seed, sim, spread), flush=True)
            hers = [t for t in takes if t["a2_similarity"] >= floor]
            best = max(hers, key=lambda t: t["f0_spread_st"]) if hers else None
            if best:
                src = OUT / "takes" / best["file"]
                wav, rate = sf.read(src)
                peak, rms = float(np.max(np.abs(wav))), float(np.sqrt(np.mean(wav ** 2)))
                gain = min(10 ** (-22 / 20) / max(rms, 1e-6), .89 / max(peak, 1e-6))
                sf.write(OUT / "listen" / ("%s-%s.wav" % (emo, tier)), wav * gain, rate, subtype="PCM_16")
            report["cells"].append({"emotion": emo, "tier": tier, "text": text, "speed": speed,
                                    "instruction": instruction(feel, tier), "takes": takes,
                                    "kept": best["file"] if best else None})
            (OUT / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    kept = [c for c in report["cells"] if c["kept"]]
    spreads = [max(t["f0_spread_st"] for t in c["takes"] if t["file"] == c["kept"]) for c in kept]
    print("kept %d of %d cells as HER voice; mean pitch spread %.2f st (current source clips 3.48, live model 3.12)" % (
        len(kept), len(report["cells"]), float(np.mean(spreads)) if spreads else 0.0), flush=True)
    print("listen:", OUT / "listen", flush=True)


if __name__ == "__main__":
    main()
