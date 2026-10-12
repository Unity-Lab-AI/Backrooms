"""Train the acoustic model from random weights, built to keep the GPU busy.

    python training/voice/train_acoustic.py <features_dir> <ckpt_dir> [--steps N] [--frames F] [--smoke]
    python training/voice/train_acoustic.py <features_dir> <ckpt_dir> --export-gta <out_dir>

- Every feature is loaded into RAM once; no disk reads during training.
- Batches are built from clips of similar length up to F mel frames each, so almost nothing is padding.
- The model runs under bf16 autocast; the aligner's distances, the alignment search and the losses stay fp32.
- Alignment search and the forward-sum loss run batched on the GPU (model.py), no per-clip CPU work.
- 2% of clips (by name hash, the same rule the vocoder uses) are held out; every 2000 steps the held-out mel
  loss is logged, so memorizing instead of learning shows up while it trains.
- --export-gta writes, for every clip, the mel the trained model makes with the clip's own alignment, pitch and
  energy (ground-truth aligned). The vocoder finishes on those, so it learns the mels it will really be fed.
Losses: mel L1, forward-sum alignment, binarization (from step 6k), MSE on log-duration, pitch and energy.
Resumes from <ckpt_dir>/acoustic.pt (checkpoint every 2000 steps).
"""
import argparse, glob, json, os, random, time
import numpy as np
import torch
import torch.nn.functional as F
from model import UnityVoice, forward_sum_loss, mask_from_lens, token_index, is_heldout


def load_all(root):
    vocab = json.load(open(os.path.join(root, "vocab.json"), encoding="utf-8"))
    st = json.load(open(os.path.join(root, "stats.json")))
    items = []
    for f in sorted(glob.glob(os.path.join(root, "*.npz"))):
        z = np.load(f)
        f0 = torch.from_numpy(z["f0"])
        f0n = torch.where(f0 > 0, (torch.log(f0.clamp(min=1)) - st["lf0_mean"]) / st["lf0_std"], torch.zeros_like(f0))
        items.append(dict(name=os.path.basename(f)[:-4],
                          phon=torch.tensor([vocab[c] for c in str(z["phon"])], dtype=torch.long),
                          mel=torch.from_numpy(z["mel"]), f0n=f0n,
                          en=(torch.from_numpy(z["energy"]) - st["e_mean"]) / st["e_std"]))
    return vocab, st, items


def batches(items, max_frames, shuffle=True):
    """Clips sorted by length, cut into batches holding at most max_frames mel frames (longest x count)."""
    order = sorted(range(len(items)), key=lambda i: items[i]["mel"].size(1))
    out, cur = [], []
    for i in order:
        longest = max([items[k]["mel"].size(1) for k in cur] + [items[i]["mel"].size(1)])
        if cur and longest * (len(cur) + 1) > max_frames:
            out.append(cur); cur = []
        cur.append(i)
    if cur:
        out.append(cur)
    if shuffle:
        random.shuffle(out)
    return out


def collate(items, idx, dev):
    pad = torch.nn.utils.rnn.pad_sequence
    b = [items[i] for i in idx]
    tl = torch.tensor([x["phon"].size(0) for x in b])
    ml = torch.tensor([x["mel"].size(1) for x in b])
    mel = pad([x["mel"].T for x in b], batch_first=True).transpose(1, 2)
    out = (pad([x["phon"] for x in b], batch_first=True), tl, mel, ml,
           pad([x["f0n"] for x in b], batch_first=True), pad([x["en"] for x in b], batch_first=True))
    return [t.to(dev, non_blocking=True) for t in out]


def losses(model, batch, step):
    phon, tl, mel, ml, f0n, en = batch
    with torch.autocast("cuda", dtype=torch.bfloat16):
        o = model(phon, tl, mel, ml, f0n, en)
    mel_hat = o["mel_hat"].float()
    fm = mask_from_lens(ml, mel.size(2))[:, None, :].float()
    T = min(mel_hat.size(2), mel.size(2))
    l_mel = (F.l1_loss(mel_hat[..., :T], mel[..., :T], reduction="none") * fm[..., :T]).sum() / (fm.sum() * mel.size(1))
    logp = o["logp"].float()
    l_align = forward_sum_loss(logp, tl, ml)
    # binarization: pull the soft alignment onto the hard path found by the search
    idx, real = token_index(o["dur"], logp.size(1))
    soft_on_path = torch.log_softmax(logp, dim=-1).gather(2, idx[..., None]).squeeze(-1)
    l_bin = -(soft_on_path * real).sum() / real.sum()
    tr = o["text_real"].float()
    l_dur = (F.mse_loss(o["d_hat"].float(), torch.log(o["dur"].float() + 1), reduction="none") * tr).sum() / tr.sum()
    l_p = (F.mse_loss(o["p_hat"].float(), o["p_tgt"], reduction="none") * tr).sum() / tr.sum()
    l_e = (F.mse_loss(o["e_hat"].float(), o["e_tgt"], reduction="none") * tr).sum() / tr.sum()
    bin_w = 0.0 if step < 6000 else min(1.0, (step - 6000) / 6000)
    total = l_mel + l_align + bin_w * l_bin + 0.1 * (l_dur + l_p + l_e)
    return total, dict(mel=l_mel, align=l_align, bin=l_bin, dur=l_dur, pitch=l_p, energy=l_e), o


@torch.no_grad()
def export_gta(model, items, out_dir, dev, max_frames):
    """Ground-truth-aligned mels: the model's own output with each clip's real alignment, pitch and energy."""
    os.makedirs(out_dir, exist_ok=True)
    model.eval()
    for idx in batches(items, max_frames, shuffle=False):
        batch = collate(items, idx, dev)
        with torch.autocast("cuda", dtype=torch.bfloat16):
            o = model(*batch)
        mel_hat = o["mel_hat"].float().cpu().numpy()
        for k, i in enumerate(idx):
            n = items[i]["mel"].size(1)
            np.save(os.path.join(out_dir, items[i]["name"] + ".npy"), mel_hat[k, :, :n].astype(np.float32))
    print("gta: wrote %d mels to %s" % (len(items), out_dir))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("feats"); ap.add_argument("ckpt")
    ap.add_argument("--steps", type=int, default=120000)
    ap.add_argument("--frames", type=int, default=48000, help="mel frames per batch (longest clip x clips)")
    ap.add_argument("--export-gta", dest="gta")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.ckpt, exist_ok=True)
    dev = "cuda"
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    torch.backends.cudnn.benchmark = True
    vocab, st, items = load_all(a.feats)
    train = [x for x in items if not is_heldout(x["name"])]
    held = [x for x in items if is_heldout(x["name"])]
    model = UnityVoice(len(vocab)).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, betas=(0.9, 0.98), weight_decay=1e-6, fused=True)
    warm = 4000
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min((s + 1) / warm, (warm / (s + 1)) ** 0.5))
    step, path = 0, os.path.join(a.ckpt, "acoustic.pt")
    if os.path.exists(path):
        ck = torch.load(path, map_location=dev)
        model.load_state_dict(ck["model"]); opt.load_state_dict(ck["opt"]); sched.load_state_dict(ck["sched"])
        step = ck["step"]
        print("resumed at step", step, flush=True)
    if a.gta:
        export_gta(model, items, a.gta, dev, a.frames)
        return
    json.dump({"vocab": vocab, "stats": st}, open(os.path.join(a.ckpt, "voice-meta.json"), "w", encoding="utf-8"),
              ensure_ascii=False)
    print("acoustic: %d train clips, %d held out, %.1f M params" % (
        len(train), len(held), sum(p.numel() for p in model.parameters()) / 1e6), flush=True)
    t0, frames_seen = time.time(), 0
    while step < a.steps:
        model.train()
        for idx in batches(train, a.frames):
            batch = collate(train, idx, dev)
            loss, parts, _ = losses(model, batch, step)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step(); sched.step(); step += 1
            frames_seen += int(batch[3].sum())
            if step % 100 == 0 or a.smoke:
                dt = time.time() - t0
                print("step %d  %s  (%.2f steps/s, %.0f k frames/s)" % (
                    step, "  ".join("%s %.3f" % (k, v.item()) for k, v in parts.items()), step / dt if not a.smoke else 0,
                    frames_seen / dt / 1000), flush=True)
                if a.smoke:
                    t0, frames_seen = time.time(), 0
            if (step % 2000 == 0 or step >= a.steps) and held:
                model.eval()
                with torch.no_grad():
                    vals = [losses(model, collate(held, idx2, dev), step)[1]["mel"].item() for idx2 in batches(held, a.frames, False)]
                print("HELDOUT step %d  mel %.4f  (train mel %.4f)" % (step, sum(vals) / len(vals), parts["mel"].item()), flush=True)
                model.train()
            if step % 2000 == 0 or step >= a.steps:
                torch.save({"model": model.state_dict(), "opt": opt.state_dict(), "sched": sched.state_dict(),
                            "step": step, "n_symbols": len(vocab)}, path + ".tmp")
                os.replace(path + ".tmp", path)
            if step >= a.steps:
                break
    print("acoustic: done at step", step, flush=True)


if __name__ == "__main__":
    main()
