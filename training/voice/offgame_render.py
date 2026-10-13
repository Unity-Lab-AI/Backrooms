"""Render the off-game lines (OFFGAME_CORPUS.jsonl) in her voice with the owner-approved pilot recipe.

Owner, 2026-10-13: "we want her to say more than just rimworld". Same as expressive_rerender.py for the emotional
rows -- Cosy, the original A2 reference, the emotion description, an intensity tier from the id, the emotion's pace,
kept only if CAM++ says HER -- but these lines have no original recording to fall back to: a line neither seed
renders as her is DROPPED (listed in the report). Neutral lines are rendered too (Cosy "neutral" is NOT used for
A2's ordinary voice in the accepted set -- SOURCE_DELIVERY_POLICY -- so neutral off-game lines use the "warm"
description at the light tier and keep the neutral label with intensity 0.0).
Renders only, resumable, never trains. Output: D:/voice-lab/dataset-v2-offgame-2026-10-13/ (v2 schema rows).

  .local/voice-lab/.venv-cosy/Scripts/python.exe training/voice/offgame_render.py
"""
import hashlib
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from expressive_pilot import CODE, MODEL, REF, ROOT, APPROVED, instruction, f0_spread  # noqa: E402
from expressive_rerender import FEEL, INTENSITY, SEEDS, SOURCE_ID, tier_of, sha  # noqa: E402

CORPUS = HERE / "OFFGAME_CORPUS.jsonl"
OUT = Path(r"D:\voice-lab\dataset-v2-offgame-2026-10-13")
VOICE_ID = "unity-a2-low-warm-alto-v1"


def main():
    sys.path[:0] = [str(CODE), str(CODE / "third_party/Matcha-TTS")]
    os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1")
    cache = ROOT / ".local/voice-lab/models/cosy-runtime-cache"
    os.environ.update(HF_HOME=str(cache / "huggingface"), MODELSCOPE_CACHE=str(cache / "modelscope"),
                      MPLCONFIGDIR=str(cache / "matplotlib"))
    import numpy as np
    import soundfile as sf
    from cosyvoice.cli.cosyvoice import AutoModel
    from cosyvoice.utils.common import set_all_random_seed
    lines = [json.loads(l) for l in CORPUS.read_text(encoding="utf-8").splitlines() if l.strip()]
    (OUT / "wavs").mkdir(parents=True, exist_ok=True)
    done_path = OUT / "progress.jsonl"
    done = {}
    if done_path.exists():
        for l in done_path.read_text(encoding="utf-8").splitlines():
            r = json.loads(l); done[r["id"]] = r
    model = AutoModel(model_dir=str(MODEL), fp16=True, load_trt=False, load_vllm=False)
    model.frontend.speech_tokenizer_session.set_providers(["CPUExecutionProvider"])

    def emb(path):
        e = model.frontend._extract_spk_embedding(str(path)).float().reshape(-1)
        return e / e.norm()

    a2 = emb(REF)
    floor = min(float(emb(ROOT / "training/voice/reference" / n) @ a2) for n in APPROVED
                if (ROOT / "training/voice/reference" / n).exists()) - 0.05
    todo = [r for r in lines if r["id"] not in done]
    print("%d lines, %d done, %d to go; A2 floor %.3f" % (len(lines), len(done), len(todo), floor), flush=True)
    started = time.monotonic()
    with open(done_path, "a", encoding="utf-8") as log:
        for n, line in enumerate(todo, 1):
            emo = line["emotion"]
            feel, speed = FEEL.get(emo, FEEL["warm"])
            tier = tier_of(line["id"]) if emo in FEEL else "light"
            dst = OUT / "wavs" / (line["id"] + ".wav")
            result = {"id": line["id"], "kept": "dropped"}
            for seed in SEEDS:
                set_all_random_seed(seed)
                chunks = [o["tts_speech"].float().cpu().numpy().reshape(-1) for o in
                          model.inference_instruct2(line["text"], instruction(feel, tier), str(REF), stream=False,
                                                    speed=speed, text_frontend=False)]
                if not chunks:
                    continue
                audio = np.concatenate(chunks)
                if not (0.25 <= len(audio) / 24000 <= 30) or float(np.max(np.abs(audio))) >= 1 or not np.isfinite(audio).all():
                    continue
                sf.write(dst, audio, 24000, subtype="PCM_16")
                sim = float(emb(dst) @ a2)
                if sim >= floor:
                    row = {"schema": "unity-voice-dataset-v2", "id": line["id"], "text": line["text"], "audio": "wavs/" + dst.name,
                           "sample_rate": 24000, "voice_id": VOICE_ID, "source_id": SOURCE_ID, "emotion": emo,
                           "intensity": 0.0 if emo == "neutral" else INTENSITY[tier], "pace": speed,
                           "speech_act": line["speech_act"], "sha256": sha(dst)}
                    result = {"id": line["id"], "kept": "expressive", "tier": tier, "seed": seed, "a2_similarity": sim,
                              "f0_spread_st": f0_spread(audio, 24000), "row": row}
                    break
            if result["kept"] == "dropped" and dst.exists():
                dst.unlink()
            log.write(json.dumps(result, ensure_ascii=False) + "\n"); log.flush()
            if n % 25 == 0:
                rate = n / (time.monotonic() - started)
                print("%d/%d  (%.2f lines/s, ~%.1f h left)" % (n, len(todo), rate, (len(todo) - n) / rate / 3600), flush=True)
    done = {}
    for l in done_path.read_text(encoding="utf-8").splitlines():
        r = json.loads(l); done[r["id"]] = r
    with open(OUT / "metadata.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for line in lines:
            if done[line["id"]]["kept"] == "expressive":
                f.write(json.dumps(done[line["id"]]["row"], ensure_ascii=False) + "\n")
    kept = [r for r in done.values() if r["kept"] == "expressive"]
    summary = {"lines": len(lines), "rendered_as_her": len(kept), "dropped": [i for i, r in done.items() if r["kept"] == "dropped"],
               "mean_f0_spread_st": float(np.mean([r["f0_spread_st"] for r in kept])) if kept else None, "a2_floor": floor,
               "training_started": False}
    (OUT / "render-report.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("DONE", json.dumps({k: v for k, v in summary.items() if k != "dropped"}), "dropped:", len(summary["dropped"]), flush=True)


if __name__ == "__main__":
    main()
