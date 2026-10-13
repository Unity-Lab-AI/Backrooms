"""Local prosody fine-tune of Unity's acoustic student on one 16 GB GPU.

Starts from the live acoustic weights (read-only copy of models/unity-voice/acoustic.pt) and keeps the
architecture, vocabulary and voice identity (unity-a2-low-warm-alto-v1) unchanged. What changes is the
training objective, aimed at the flat delivery the owner hears:

  * pitch/energy/duration predictor losses weighted 1.0/1.0/0.5 instead of 0.1 each, so the predictors
    stop settling on the average contour;
  * an utterance-level contour loss: the spread (std) and level (mean) of the predicted phoneme pitch and
    energy must match the recording, which pushes back on regression-to-the-mean and on the collapsed
    emotion register;
  * predictor dropout 0.5 -> 0.2 (weights untouched);
  * fresh AdamW at a fine-tune learning rate (2e-4, 500-step warmup, inverse-sqrt decay).

Never writes into models/unity-voice/. Output tree (default D:/voice-lab/local-retrain-<date>/):
  work/acoustic-work.pt       full resumable checkpoint, rewritten every --ckpt-minutes
  model/acoustic.pt           deployment-only weights, rewritten at every checkpoint
  samples/step-XXXXXX/*.wav   preview lines every --sample-minutes, vocoded with the live vocoder
  samples/metrics.jsonl       F0 std / syllable-accent / energy spread of the previews vs the recordings
  train.log.jsonl             loss every 100 steps

The live vocoder was polished on the OLD acoustic model's output (oracle-gta). Previews use it as-is; before
this model can go live the vocoder needs its short GTA polish on the new acoustic output (see the README).
"""
import argparse
import json
import math
import os
import random
import sys
import time
import uuid
from datetime import date
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from dataset_contract import ACOUSTIC_CONFIG, CHECKPOINT_SCHEMA, EMOTIONS, SPEECH_ACTS, VOCODER_CONFIG, MAX_PHONEMES, pair_identity  # noqa: E402
from model import UnityVoice, mask_from_lens  # noqa: E402
from train_acoustic import load_all, batches, collate, losses as base_losses  # noqa: E402
from vocoder import Generator  # noqa: E402
from speech_text import speech_tokens  # noqa: E402

LIVE = HERE.parent.parent / "models" / "unity-voice"
PREVIEW_LINES = [  # the owner's 2026-10-13 session lines ('!' spoken as '.', like the live voice)
    ("concerned", "instruction", "Six pirates on the east edge, and they look fast. Everyone shoots from behind sandbags."),
    ("warm", "statement", "Hi roomsidlehands, welcome in, grab a seat near the fire."),
    ("sad", "statement", "Gee is gone. The man who grew every meal we ate. I am so sorry, everyone."),
    ("excited", "exclamation", "There is a thrumbo out there. A huge white giant that eats three meals a day."),
    ("frustrated", "exclamation", "The kitchen caught fire, and our cook looked at me like I was the one who lit it."),
    ("amused", "statement", "It is a cardboard box, but it's our box. We're proud of it."),
    ("surprised", "wh_question", "Wait, what is that thing doing in our freezer?"),
    ("happy", "statement", "We actually made it through winter, and nobody ate anybody."),
]


def spread_loss(pred, tgt, mask):
    """Per-utterance |std(pred)-std(tgt)| + |mean(pred)-mean(tgt)| over masked phonemes."""
    n = mask.sum(1).clamp(min=2)
    mp, mt = (pred * mask).sum(1) / n, (tgt * mask).sum(1) / n
    sp = (((pred - mp[:, None]) ** 2 * mask).sum(1) / n + 1e-6).sqrt()
    st = (((tgt - mt[:, None]) ** 2 * mask).sum(1) / n + 1e-6).sqrt()
    keep = (mask.sum(1) >= 3).float()
    return (((sp - st).abs() + (mp - mt).abs()) * keep).sum() / keep.sum().clamp(min=1)


def prosody_losses(model, batch, step):
    _, parts, out = base_losses(model, batch, step + 12000)  # fine-tune: alignment binarization fully on
    tr = out["text_real"].float()
    pitched = tr * (out["v_tgt"] > 0.5).float()
    l_pspread = spread_loss(out["p_hat"].float(), out["p_tgt"].float(), pitched)
    l_espread = spread_loss(out["e_hat"].float(), out["e_tgt"].float(), tr)
    total = (parts["oracle_mel"] + parts["align"] + parts["bin"]
             + 1.0 * parts["pitch"] + 1.0 * parts["energy"] + 0.5 * parts["dur"] + 0.1 * parts["voicing"]
             + 0.5 * (l_pspread + l_espread))
    if not torch.isfinite(total).item():
        raise ValueError("Nonfinite loss; training stopped")
    parts.update(pitch_spread=l_pspread, energy_spread=l_espread)
    return total, parts


def f0_metrics(wav):
    import pyworld
    w = wav.astype(np.float64)
    f0, t = pyworld.dio(w, 24000, frame_period=256 / 24)
    f0 = pyworld.stonemask(w, f0, t, 24000)
    s = 12 * np.log2(f0[f0 > 0] / 195.0)
    if len(s) < 25:
        return None
    sm = np.convolve(s, np.ones(19) / 19, "valid")
    trend = np.polyval(np.polyfit(np.arange(len(sm)), sm, 1), np.arange(len(sm)))
    return {"f0_std_st": float(s.std()), "accent_st": float(np.std(sm - trend)), "median_st": float(np.median(s))}


@torch.no_grad()
def write_samples(model, voc, g2p, vocab, out_dir, step, dev, log):
    model.eval()
    folder = out_dir / ("step-%06d" % step)
    folder.mkdir(parents=True, exist_ok=True)
    rows = []
    for i, (emotion, act, text) in enumerate(PREVIEW_LINES):
        try:
            phon = speech_tokens(text, g2p, MAX_PHONEMES)
            if set(phon) - set(vocab):
                continue
            ids = torch.tensor([[vocab[t] for t in phon]], device=dev)
            cond = {"emotion": torch.tensor([EMOTIONS.index(emotion)], device=dev),
                    "speech_act": torch.tensor([SPEECH_ACTS.index(act)], device=dev),
                    "intensity": torch.tensor([0.0 if emotion == "neutral" else 0.35], device=dev),
                    "pace": torch.tensor([1.0], device=dev)}
            wav = voc(model.infer(ids, cond, 1.0)).squeeze().float().clamp(-1, 1).cpu().numpy()
        except ValueError as error:
            print("sample skipped:", error, flush=True)
            continue
        sf.write(folder / ("%02d-%s-%s.wav" % (i + 1, emotion, act)), wav, 24000)
        m = f0_metrics(wav)
        if m:
            rows.append(dict(m, emotion=emotion))
    if rows:
        summary = {"step": step, "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                   "f0_std_st": float(np.mean([r["f0_std_st"] for r in rows])),
                   "accent_st": float(np.mean([r["accent_st"] for r in rows])),
                   "emotion_register_spread_st": float(np.ptp([r["median_st"] for r in rows])),
                   "baseline_live_model": {"f0_std_st": 3.12, "accent_st": 1.64},
                   "baseline_recordings": {"f0_std_st": 3.48, "accent_st": 2.10}}
        with open(out_dir / "metrics.jsonl", "a", encoding="utf-8") as stream:
            stream.write(json.dumps(summary) + "\n")
        log("samples step %d: F0 std %.2f st, accent %.2f st, emotion spread %.2f st -> %s" % (
            step, summary["f0_std_st"], summary["accent_st"], summary["emotion_register_spread_st"], folder))
    model.train()
    for p in model.dur, model.pitch, model.energy, model.voicing:
        p.drop.p = 0.2


def main():
    today = date.today().isoformat()
    ap = argparse.ArgumentParser()
    ap.add_argument("--feats", default=r"D:\voice-lab\local-retrain-2026-10-13\feats")
    ap.add_argument("--out", default=r"D:\voice-lab\local-retrain-" + today)
    ap.add_argument("--steps", type=int, default=30000)
    ap.add_argument("--frames", type=int, default=24000, help="mel frames per batch (VRAM knob)")
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--ckpt-minutes", type=float, default=15)
    ap.add_argument("--sample-minutes", type=float, default=30)
    ap.add_argument("--smoke", type=int, default=0, help="run this many steps, report speed/VRAM, write nothing but a smoke report")
    ap.add_argument("--seed", type=int, default=23)
    args = ap.parse_args()
    if not torch.cuda.is_available():
        raise SystemExit("CUDA GPU required")
    dev = "cuda"
    random.seed(args.seed); np.random.seed(args.seed); torch.manual_seed(args.seed)
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    logf = open(out / ("smoke.log" if args.smoke else "train.log"), "a", encoding="utf-8")

    def log(msg):
        line = time.strftime("%H:%M:%S ") + msg
        print(line, flush=True); logf.write(line + "\n"); logf.flush()

    manifest, items = load_all(args.feats)
    live_meta = json.loads((LIVE / "voice-meta.json").read_text(encoding="utf-8"))
    if manifest["vocab"] != live_meta["vocab"]:
        raise SystemExit("Re-prepared vocabulary differs from the live voice; refusing to fine-tune across vocabularies")
    if manifest["dataset"]["dataset_id"] != live_meta["identity"]["dataset_id"]:
        raise SystemExit("Feature dataset is not the live voice's dataset")
    train = [x for x in items if x["split"] == "train"]
    held = [x for x in items if x["split"] == "heldout"]
    model = UnityVoice(len(manifest["vocab"]), **ACOUSTIC_CONFIG).to(dev)
    for p in model.dur, model.pitch, model.energy, model.voicing:
        p.drop.p = 0.2
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, betas=(0.9, 0.98), weight_decay=1e-6, fused=True)
    warm = 500
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min((s + 1) / warm, (warm / (s + 1)) ** 0.5))
    work = out / "work" / "acoustic-work.pt"
    step, order, cursor = 0, [], 0
    if work.exists() and not args.smoke:
        ck = torch.load(work, map_location=dev, weights_only=True)
        model.load_state_dict(ck["model"]); opt.load_state_dict(ck["opt"]); sched.load_state_dict(ck["sched"])
        step, order, cursor = ck["step"], ck["order"], ck["cursor"]
        log("resumed at step %d" % step)
    else:
        live = torch.load(LIVE / "acoustic.pt", map_location=dev, weights_only=True)
        model.load_state_dict(live["model"])
        log("initialized from live acoustic step %d (read-only)" % live["step"])
    voc = Generator(**VOCODER_CONFIG).to(dev).eval()
    voc.load_state_dict(torch.load(LIVE / "vocoder.pt", map_location=dev, weights_only=True)["G"])
    from misaki import en, espeak
    g2p = en.G2P(trf=False, british=False, fallback=espeak.EspeakFallback(british=False))
    identity = pair_identity(manifest)

    def save():
        (out / "work").mkdir(exist_ok=True); (out / "model").mkdir(exist_ok=True)
        tmp = work.with_name("acoustic-work.pt.writing-" + uuid.uuid4().hex[:8])
        torch.save({"model": model.state_dict(), "opt": opt.state_dict(), "sched": sched.state_dict(),
                    "step": step, "order": order, "cursor": cursor, "args": vars(args)}, tmp)
        os.replace(tmp, work)
        tmp = out / "model" / "acoustic.pt.writing"
        torch.save({"schema": CHECKPOINT_SCHEMA, "kind": "acoustic", "identity": identity, "model": model.state_dict(),
                    "n_symbols": len(manifest["vocab"]), "step": step, "seed": args.seed,
                    "fine_tune": "local-prosody-v1 from live acoustic"}, tmp)
        os.replace(tmp, out / "model" / "acoustic.pt")
        log("checkpoint step %d" % step)

    total_steps = args.smoke or args.steps
    log("train %d clips, heldout %d; frames/batch %d; target step %d" % (len(train), len(held), args.frames, total_steps))
    torch.cuda.reset_peak_memory_stats()
    t0 = last_ck = last_sample = time.time()
    s0 = step
    if not args.smoke and step == 0:
        write_samples(model, voc, g2p, manifest["vocab"], out / "samples", 0, dev, log)
    model.train()
    while step < total_steps:
        if not order or cursor >= len(order):
            order, cursor = batches(train, args.frames), 0
        idx = order[cursor]
        loss, parts = prosody_losses(model, collate(train, idx, dev), step)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step(); sched.step(); step += 1; cursor += 1
        if step % 100 == 0 or (args.smoke and step % 20 == 0):
            el = time.time() - t0
            log("step %d  %s  %.2f steps/s  peak VRAM %.2f GB" % (step, " ".join("%s %.3f" % (k, v.item()) for k, v in parts.items()),
                (step - s0) / el, torch.cuda.max_memory_allocated() / 2 ** 30))
        if args.smoke:
            continue
        now = time.time()
        if now - last_ck >= args.ckpt_minutes * 60 or step >= total_steps:
            save(); last_ck = now
        if now - last_sample >= args.sample_minutes * 60 or step >= total_steps:
            write_samples(model, voc, g2p, manifest["vocab"], out / "samples", step, dev, log); last_sample = time.time()
    el = time.time() - t0
    rate = (step - s0) / el
    log("done %d steps in %.1f min, %.2f steps/s, peak VRAM allocated %.2f GB, reserved %.2f GB; 30k steps ~ %.1f h" % (
        step - s0, el / 60, rate, torch.cuda.max_memory_allocated() / 2 ** 30, torch.cuda.max_memory_reserved() / 2 ** 30,
        30000 / rate / 3600))
    if args.smoke:
        write_samples(model, voc, g2p, manifest["vocab"], out / "smoke-samples", step, dev, log)


if __name__ == "__main__":
    main()
