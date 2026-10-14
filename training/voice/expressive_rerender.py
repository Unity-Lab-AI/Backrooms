"""The expressive source set for unity-voice-v2: every emotional clip re-performed with the owner-approved pilot recipe.

Owner, 2026-10-13: "i reviewed all expressive-pilot-2026-10-13 they are good to go" -> "lets do that for all wee need
for the 2nd pass". From the accepted 4,845-clip dataset:
  * neutral rows stay the original A2 recordings (A2's ordinary voice is never replaced -- SOURCE_DELIVERY_POLICY);
  * every other row is re-performed by Cosy with the original A2 reference, the pilot's emotion description, one of
    three intensity tiers (picked from the clip id, so a third each) and the emotion's pace; its labels become the
    REAL delivery: intensity 0.25 / 0.55 / 0.85 and pace = the speed it was rendered at;
  * a take is kept only if CAM++ says it is still HER (the pilot's floor, calibrated on the approved A2 clips); a second
    seed is tried, and if neither is her the original clip stays with its original labels.
Renders only, resumable (re-run continues), never trains. Output: a dataset in the same v2 schema.

  .local/voice-lab/.venv-cosy/Scripts/python.exe training/voice/expressive_rerender.py
"""
import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from expressive_pilot import CODE, MODEL, REF, ROOT, APPROVED, EMOTIONS as PILOT, TIERS, instruction, f0_spread  # noqa: E402

SRC = Path(r"D:\voice-lab\pod-results\voice-2026-10-12\gen\dataset")
OUT = Path(r"D:\voice-lab\dataset-v2-expressive-2026-10-13")
INTENSITY = {"light": 0.25, "medium": 0.55, "strong": 0.85}
SEEDS = [11032, 2711]
SOURCE_ID = "cosy3-a2-expressive-pilot-recipe-2026-10-13"
# the dataset's 9 labels; "concerned" is the pilot's worried read; flirty is not a voice label (the model has 9)
FEEL = {e: PILOT[e][:2] for e in ("happy", "excited", "amused", "sad", "frustrated", "concerned", "surprised", "warm")}


def tier_of(row_id):
    return list(INTENSITY)[int(hashlib.sha256(row_id.encode()).hexdigest(), 16) % 3]


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


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
    rows = [json.loads(l) for l in (SRC / "metadata.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    (OUT / "wavs").mkdir(parents=True, exist_ok=True)
    done_path = OUT / "progress.jsonl"
    done = {}
    if done_path.exists():
        for l in done_path.read_text(encoding="utf-8").splitlines():
            r = json.loads(l)
            done[r["id"]] = r
    model = AutoModel(model_dir=str(MODEL), fp16=True, load_trt=False, load_vllm=False)
    model.frontend.speech_tokenizer_session.set_providers(["CPUExecutionProvider"])

    def emb(path):
        e = model.frontend._extract_spk_embedding(str(path)).float().reshape(-1)
        return e / e.norm()

    a2 = emb(REF)
    floor = min(float(emb(ROOT / "training/voice/reference" / n) @ a2) for n in APPROVED
                if (ROOT / "training/voice/reference" / n).exists()) - 0.05
    todo = [r for r in rows if r["id"] not in done]
    print("%d rows, %d done, %d to go; A2 floor %.3f" % (len(rows), len(done), len(todo), floor), flush=True)
    started = time.monotonic()
    with open(done_path, "a", encoding="utf-8") as log:
        for n, row in enumerate(todo, 1):
            dst = OUT / "wavs" / (row["id"] + ".wav")
            out_row = dict(row)
            result = {"id": row["id"], "kept": "original"}
            if row["emotion"] in FEEL:
                feel, speed = FEEL[row["emotion"]]
                tier = tier_of(row["id"])
                for seed in SEEDS:
                    set_all_random_seed(seed)
                    chunks = [o["tts_speech"].float().cpu().numpy().reshape(-1) for o in
                              model.inference_instruct2(row["text"], instruction(feel, tier), str(REF), stream=False,
                                                        speed=speed, text_frontend=False)]
                    if not chunks:
                        continue
                    audio = np.concatenate(chunks)
                    peak = float(np.max(np.abs(audio)))
                    if not (0.25 <= len(audio) / 24000 <= 30) or peak >= 1 or not np.isfinite(audio).all():
                        continue
                    sf.write(dst, audio, 24000, subtype="PCM_16")
                    sim = float(emb(dst) @ a2)
                    if sim >= floor:
                        out_row.update(intensity=INTENSITY[tier], pace=speed, source_id=SOURCE_ID)
                        result = {"id": row["id"], "kept": "expressive", "tier": tier, "seed": seed, "a2_similarity": sim,
                                  "f0_spread_st": f0_spread(audio, 24000)}
                        break
            if result["kept"] == "original":
                shutil.copy2(SRC / row["audio"], dst)
            out_row["audio"] = "wavs/" + dst.name
            out_row["sha256"] = sha(dst)
            result["row"] = out_row
            log.write(json.dumps(result) + "\n"); log.flush()
            if n % 25 == 0:
                rate = n / (time.monotonic() - started)
                print("%d/%d  (%.2f rows/s, ~%.1f h left)" % (n, len(todo), rate, (len(todo) - n) / rate / 3600), flush=True)
    # the dataset: every row, in the original order, same v2 schema
    done = {}
    for l in done_path.read_text(encoding="utf-8").splitlines():
        r = json.loads(l)
        done[r["id"]] = r
    with open(OUT / "metadata.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(done[row["id"]]["row"], ensure_ascii=False) + "\n")
    kept = [r for r in done.values() if r["kept"] == "expressive"]
    summary = {"rows": len(rows), "expressive": len(kept), "original_kept": len(rows) - len(kept),
               "mean_f0_spread_st": float(np.mean([r["f0_spread_st"] for r in kept])) if kept else None,
               "a2_floor": floor, "training_started": False}
    (OUT / "rerender-report.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("DONE", json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
