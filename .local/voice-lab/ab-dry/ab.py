"""A/B: is the A2 voice too cheerful ("too happy, like Mary Ann") and does a drier delivery fix it?

    <cosy venv python> ab.py cosy <out>     # A current instruction, B dry instruction, C dry + "!" -> "."
    <qwen venv python> ab.py qwen <out>     # same lines cloned from the original / soft / everyday A2 references

Same calls and settings as training/voice/source_workers.py (fixed seed per line, speed 1.0, text_frontend off).
Writes <out>/<teacher>-<variant>-<n>.wav and index.json. Audition only: nothing here enters a dataset.
"""
import json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / ".local" / "voice-lab"
POLICY = json.load(open(ROOT / "training/voice/SOURCE_DELIVERY_POLICY.json", encoding="utf-8"))
PROFILES = json.load(open(ROOT / "training/voice/REFERENCE_PROFILES.json", encoding="utf-8"))["profiles"]
REF = POLICY["speaker_reference"]
MID = ("You are a helpful assistant. 请用自然、放松、平稳的语气说话，带一点干巴巴的幽默，温暖但不甜美，可以带一点笑意，"
       "但不要过分开心，不要夸张，不要尖叫。<|endofprompt|>")
DRY = ("You are a helpful assistant. 请用自然、偏低沉、略带慵懒的语气说话，语气平稳克制，带一点冷幽默和轻微的讽刺，"
       "内心是温暖的；不要甜美，不要过分开心，不要夸张，不要尖叫。<|endofprompt|>")
COSY_LINES = [
    "Everybody survived!",
    "Did that vending machine just talk to Mara?",
    "Nobody had a breakdown today, which might be a colony record.",
    "[laughter] Bram has just declared war on a turkey!",
    "Hollis wrote a poem for the event letter. It rhymes and everything, I'm so proud.",
    "I zoned the trash pile as a recreation area, and everyone's thrilled about it. [laughter]",
]
QWEN_LINES = [
    "Is it weird that I'm getting attached to a hallway?",
    "It's okay, Pip.",
    "Is anybody else having a slow, sleepy kind of evening?",
    "Our food stores are getting low and winter's coming. We need a plan, chat.",
]


def main():
    teacher, out = sys.argv[1], Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    import numpy as np, soundfile as sf, torch
    index = []
    if teacher == "cosy":
        code = LAB / "models" / "cosyvoice-code"
        sys.path[:0] = [str(code), str(code / "third_party" / "Matcha-TTS")]
        cache = LAB / "models" / "cosy-runtime-cache"
        os.environ.update(HF_HOME=str(cache / "huggingface"), MODELSCOPE_CACHE=str(cache / "modelscope"),
                          HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1")
        from cosyvoice.cli.cosyvoice import AutoModel
        from cosyvoice.utils.common import set_all_random_seed
        model = AutoModel(model_dir=str(LAB / "models" / "cosyvoice3"), fp16=True, load_trt=False, load_vllm=False)
        variants = ({"M1-mid": (MID, False), "M2-mid-no-exclaim": (MID, True)} if "--mid" in sys.argv else
                    {"A-current": (None, False), "B-dry": (DRY, False), "C-dry-no-exclaim": (DRY, True)})
        for name, (instr, calm) in variants.items():
            for n, text in enumerate(COSY_LINES, 1):
                current = POLICY["cosy_instructions"]["relaxed_smile" if "[laughter]" in text else "natural_happy"]
                line = text.replace("!", ".") if calm else text
                set_all_random_seed(1000 + n)
                audio = np.concatenate([item["tts_speech"].squeeze(0).cpu().numpy() for item in model.inference_instruct2(
                    line, instr or current, str(ROOT / REF["audio"]), zero_shot_spk_id="", stream=False, speed=1.0,
                    text_frontend=False)])
                path = out / ("cosy-%s-%d.wav" % (name, n))
                sf.write(path, audio, model.sample_rate)
                index.append({"file": path.name, "variant": name, "text": line})
                print(path.name, round(len(audio) / model.sample_rate, 2), flush=True)
    else:
        from qwen_tts import Qwen3TTSModel
        model = Qwen3TTSModel.from_pretrained(str(LAB / "models" / "qwen3-tts-base"), device_map="cuda:0",
                                              dtype=torch.bfloat16, attn_implementation="sdpa", local_files_only=True)
        names = ("mid",) if "--mid" in sys.argv else ("original", "soft", "everyday")
        for name in names:
            if name == "mid":                       # original + everyday A2 takes back to back as one reference
                a, ra = sf.read(str(ROOT / PROFILES["original"]["audio"]), dtype="float32")
                b, rb = sf.read(str(ROOT / PROFILES["everyday"]["audio"]), dtype="float32")
                assert ra == rb
                both = out / "mid-reference.wav"
                sf.write(both, np.concatenate([a, np.zeros(int(ra * .4), dtype=np.float32), b]), ra)
                prompt = model.create_voice_clone_prompt(ref_audio=str(both),
                                                         ref_text=PROFILES["original"]["text"] + " " + PROFILES["everyday"]["text"])
            else:
                prof = PROFILES[name]
                prompt = model.create_voice_clone_prompt(ref_audio=str(ROOT / prof["audio"]), ref_text=prof["text"])
            for n, text in enumerate(QWEN_LINES, 1):
                torch.manual_seed(2000 + n); torch.cuda.manual_seed_all(2000 + n)
                wavs, rate = model.generate_voice_clone(text=text, language="English", voice_clone_prompt=prompt,
                                                        non_streaming_mode=True, do_sample=True, temperature=.75, top_p=.9,
                                                        max_new_tokens=600)
                path = out / ("qwen-%s-%d.wav" % (name, n))
                sf.write(path, np.asarray(wavs[0], dtype=np.float32), rate)
                index.append({"file": path.name, "variant": name, "text": text})
                print(path.name, flush=True)
    json.dump(index, open(out / ("index-%s%s.json" % (teacher, "-mid" if "--mid" in sys.argv else "")), "w", encoding="utf-8"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
