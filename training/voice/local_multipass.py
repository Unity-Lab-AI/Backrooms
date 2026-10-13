"""Unity's voice -- the local multi-pass re-train, one command, resumable, never touching models/unity-voice/.

Owner, 2026-10-13: "the prep for the vocie repase multipass run" (and: never start training without his "start").

  pass 1  prosody   local_prosody_retrain.py to --steps (resumes its own work checkpoint; step 3917 exists)
  pass 2  gta       ground-truth-aligned mels from the NEW acoustic model (train_acoustic.export_mels), bound by hash
                    to a copy of that model inside the vocoder folder
  pass 3  vocoder   train_vocoder.py --gta, warm-started from the LIVE vocoder's weights (it was saved weights-only;
                    the only full checkpoint is step 25000), a fresh discriminator trained alone first
  pass 4  ab        the same preview lines through live (old acoustic + old vocoder) and new (new + new), F0/accent
                    metrics side by side -> <out>/ab/ + ab-report.json. Nothing goes live: the owner listens first.

  python local_multipass.py --check          verify every input/identity/hash/VRAM; trains nothing
  python local_multipass.py                  run passes 1-4 (each skipped when already complete)
  python local_multipass.py --from vocoder   start at a later pass

Python must run from a %TEMP% folder (the repo's .local/qa shadows 'inspect'); local_multipass.ps1 does that.
"""
import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
LIVE = HERE.parent.parent / "models" / "unity-voice"
PASSES = ["prosody", "gta", "vocoder", "ab"]


def log(out, msg):
    line = time.strftime("%H:%M:%S ") + msg
    print(line, flush=True)
    with open(out / "multipass.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run(out, cmd):
    log(out, "run: " + " ".join(str(c) for c in cmd))
    code = subprocess.call([str(c) for c in cmd])
    if code:
        raise SystemExit("pass failed with exit code %d" % code)


def acoustic_step(out):
    import torch
    p = out / "model" / "acoustic.pt"
    return torch.load(p, map_location="cpu", weights_only=True)["step"] if p.exists() else 0


def load_new_acoustic(out, manifest, dev):
    import torch
    from dataset_contract import ACOUSTIC_CONFIG
    from model import UnityVoice
    ck = torch.load(out / "model" / "acoustic.pt", map_location=dev, weights_only=True)
    model = UnityVoice(len(manifest["vocab"]), **ACOUSTIC_CONFIG).to(dev)
    model.load_state_dict(ck["model"])
    return model.eval(), ck


def check(args, out):
    """Everything the four passes need, verified without a single training step."""
    import torch
    from dataset_contract import load_dataset, load_features, pair_identity
    problems = []
    feats, dataset = Path(args.feats), Path(args.dataset)
    for p in (feats / "features-manifest.json", LIVE / "acoustic.pt", LIVE / "vocoder.pt", LIVE / "voice-meta.json",
              out / "work" / "acoustic-work.pt", out / "model" / "acoustic.pt"):
        log(out, ("ok   " if p.exists() else "MISSING ") + str(p))
        if not p.exists():
            problems.append("missing " + str(p))
    manifest = load_features(str(feats), verify_files=False)
    rows, identity = load_dataset(str(dataset), verify_audio=False)
    if identity != manifest["dataset"]:
        problems.append("dataset folder is not the one the features were prepared from")
    live_meta = json.loads((LIVE / "voice-meta.json").read_text(encoding="utf-8"))
    if manifest["vocab"] != live_meta["vocab"]:
        problems.append("feature vocabulary differs from the live voice")
    voc = torch.load(LIVE / "vocoder.pt", map_location="cpu", weights_only=True)
    text_side = ("feature_id", "frontend_id")   # a re-prepared text frontend; the vocoder never sees text
    vi, fi = voc.get("identity") or {}, pair_identity(manifest)
    if {k: v for k, v in vi.items() if k not in text_side} != {k: v for k, v in fi.items() if k not in text_side}:
        problems.append("live vocoder belongs to another dataset/audio pair")
    elif vi != fi:
        log(out, "note: live vocoder was made with the pod's text frontend; the warm start records both identities")
    new = torch.load(out / "model" / "acoustic.pt", map_location="cpu", weights_only=True)
    if new.get("identity") != pair_identity(manifest):
        problems.append("retrained acoustic identity differs from the features")
    log(out, "prosody pass at step %d of %d; live vocoder step %d (%s); %d dataset rows" % (
        new.get("step", 0), args.steps, voc.get("step", 0), voc.get("input_mode"), len(rows)))
    if torch.cuda.is_available():
        free, total = torch.cuda.mem_get_info()
        log(out, "GPU %s: %.1f GB free of %.1f GB" % (torch.cuda.get_device_name(0), free / 1e9, total / 1e9))
        if free < 8e9:
            problems.append("less than 8 GB of GPU memory free (close the game/Ollama/the face service)")
    else:
        problems.append("no CUDA GPU")
    free_disk = shutil.disk_usage(out).free
    log(out, "disk free on %s: %.0f GB" % (out.anchor, free_disk / 1e9))
    if free_disk < 30e9:
        problems.append("less than 30 GB free disk for the GTA mels and checkpoints")
    for p in problems:
        log(out, "PROBLEM: " + p)
    log(out, "CHECK " + ("PASSED -- ready for the owner's start" if not problems else "FAILED"))
    return not problems


def pass_prosody(args, out):
    if acoustic_step(out) >= args.steps:
        log(out, "prosody: done (step %d)" % acoustic_step(out)); return
    run(out, [sys.executable, HERE / "local_prosody_retrain.py", "--feats", args.feats, "--out", out,
              "--steps", args.steps, "--frames", args.frames])


def pass_gta(args, out):
    import torch
    from train_acoustic import load_all, export_mels
    gta, vdir = out / "gta", out / "vocoder"
    if (gta / "mel-manifest.json").exists():
        log(out, "gta: export exists"); return
    vdir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(out / "model" / "acoustic.pt", vdir / "acoustic.pt")   # the vocoder binds its GTA to this exact file
    manifest, items = load_all(args.feats)
    model, ck = load_new_acoustic(out, manifest, "cuda")
    log(out, "gta: exporting %d mels from the new acoustic model (step %d)" % (len(items), ck["step"]))
    export_mels(model, manifest, items, str(gta), "cuda", args.frames, "oracle-gta", vdir / "acoustic.pt")


def pass_vocoder(args, out):
    import torch
    vdir = out / "vocoder"
    total = int(torch.load(LIVE / "vocoder.pt", map_location="cpu", weights_only=True)["step"]) + args.d_warmup + args.vocoder_steps
    if (vdir / "vocoder.pt").exists() and torch.load(vdir / "vocoder.pt", map_location="cpu", weights_only=True)["step"] >= total:
        log(out, "vocoder: done"); return
    cmd = [sys.executable, HERE / "train_vocoder.py", args.dataset, args.feats, vdir, "--gta", out / "gta",
           "--steps", total, "--batch", args.vocoder_batch, "--d-warmup", args.d_warmup]
    if not (vdir / "vocoder.pt").exists():
        cmd += ["--warm-generator", LIVE / "vocoder.pt"]
    run(out, cmd)


def pass_ab(args, out):
    import numpy as np
    import soundfile as sf
    import torch
    from dataset_contract import VOCODER_CONFIG, load_features
    from vocoder import Generator
    from local_prosody_retrain import PREVIEW_LINES, f0_metrics
    from model import UnityVoice
    from dataset_contract import ACOUSTIC_CONFIG, EMOTIONS, SPEECH_ACTS, MAX_PHONEMES
    from speech_text import speech_tokens
    from misaki import en, espeak
    dev = "cuda"
    manifest = load_features(args.feats, verify_files=False)
    vocab = {t: i for i, t in enumerate(manifest["vocab"])} if isinstance(manifest["vocab"], list) else manifest["vocab"]
    g2p = en.G2P(trf=False, british=False, fallback=espeak.EspeakFallback(british=False))
    pairs = {"live": (LIVE / "acoustic.pt", LIVE / "vocoder.pt"), "new": (out / "model" / "acoustic.pt", out / "vocoder" / "vocoder.pt")}
    report = {}
    for name, (ap, vp) in pairs.items():
        model = UnityVoice(len(manifest["vocab"]), **ACOUSTIC_CONFIG).to(dev).eval()
        model.load_state_dict(torch.load(ap, map_location=dev, weights_only=True)["model"])
        voc = Generator(**VOCODER_CONFIG).to(dev).eval()
        voc.load_state_dict(torch.load(vp, map_location=dev, weights_only=True)["G"])
        folder = out / "ab" / name
        folder.mkdir(parents=True, exist_ok=True)
        rows = []
        with torch.no_grad():
            for i, (emotion, act, text) in enumerate(PREVIEW_LINES):
                phon = speech_tokens(text, g2p, MAX_PHONEMES)
                if set(phon) - set(vocab):
                    continue
                ids = torch.tensor([[vocab[t] for t in phon]], device=dev)
                cond = {"emotion": torch.tensor([EMOTIONS.index(emotion)], device=dev),
                        "speech_act": torch.tensor([SPEECH_ACTS.index(act)], device=dev),
                        "intensity": torch.tensor([0.35], device=dev), "pace": torch.tensor([1.0], device=dev)}
                wav = voc(model.infer(ids, cond, 1.0)).squeeze().float().clamp(-1, 1).cpu().numpy()
                sf.write(folder / ("%02d-%s.wav" % (i + 1, emotion)), wav, 24000)
                m = f0_metrics(wav)
                if m:
                    rows.append(dict(m, emotion=emotion))
        report[name] = {"f0_std_st": float(np.mean([r["f0_std_st"] for r in rows])),
                        "accent_st": float(np.mean([r["accent_st"] for r in rows])),
                        "emotion_register_spread_st": float(np.ptp([r["median_st"] for r in rows]))} if rows else {}
    report["recordings"] = {"f0_std_st": 3.48, "accent_st": 2.10}
    (out / "ab-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    log(out, "ab: " + json.dumps(report) + " -> " + str(out / "ab") + " (owner listens; nothing deployed)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"D:\voice-lab\local-retrain-2026-10-13")
    ap.add_argument("--feats", default=r"D:\voice-lab\local-retrain-2026-10-13\feats")
    ap.add_argument("--dataset", default=r"D:\voice-lab\pod-results\voice-2026-10-12\gen\dataset")
    ap.add_argument("--steps", type=int, default=30000, help="prosody pass total steps")
    ap.add_argument("--frames", type=int, default=24000)
    ap.add_argument("--vocoder-steps", type=int, default=20000, help="joint GTA polish steps after the warm-up")
    ap.add_argument("--d-warmup", type=int, default=2000)
    ap.add_argument("--vocoder-batch", type=int, default=16)
    ap.add_argument("--from", dest="start", choices=PASSES, default="prosody")
    ap.add_argument("--check", action="store_true", help="verify inputs only; trains nothing")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if args.check:
        raise SystemExit(0 if check(args, out) else 1)
    if not check(args, out):
        raise SystemExit("check failed; nothing started")
    for name in PASSES[PASSES.index(args.start):]:
        log(out, "=== pass: " + name)
        globals()["pass_" + name](args, out)
    log(out, "all passes done -- listen to %s before anything goes live" % (out / "ab"))


if __name__ == "__main__":
    main()
