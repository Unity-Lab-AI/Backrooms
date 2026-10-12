"""Train the acoustic model from random weights.

    python training/voice/train_acoustic.py <features_dir> <ckpt_dir> [--steps N] [--batch B] [--smoke]

Resumes from <ckpt_dir>/acoustic.pt. Losses: mel L1, forward-sum alignment, binarization (after the
aligner warms up), and MSE on log-duration, pitch and energy against the aligned targets.
"""
import argparse, glob, json, os, random, time
import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from model import UnityVoice, forward_sum_loss, mask_from_lens


class Feats(Dataset):
    def __init__(self, root):
        self.files = sorted(glob.glob(os.path.join(root, "*.npz")))
        self.vocab = json.load(open(os.path.join(root, "vocab.json"), encoding="utf-8"))
        self.stats = json.load(open(os.path.join(root, "stats.json")))

    def __len__(self):
        return len(self.files)

    def __getitem__(self, i):
        z = np.load(self.files[i])
        phon = torch.tensor([self.vocab[c] for c in str(z["phon"])], dtype=torch.long)
        f0 = torch.from_numpy(z["f0"])
        f0n = torch.where(f0 > 0, (torch.log(f0.clamp(min=1)) - self.stats["lf0_mean"]) / self.stats["lf0_std"],
                          torch.zeros_like(f0))
        en = (torch.from_numpy(z["energy"]) - self.stats["e_mean"]) / self.stats["e_std"]
        return phon, torch.from_numpy(z["mel"]), f0n, en


def collate(batch):
    phon, mel, f0n, en = zip(*batch)
    tl = torch.tensor([p.size(0) for p in phon])
    ml = torch.tensor([m.size(1) for m in mel])
    pad = torch.nn.utils.rnn.pad_sequence
    mel = pad([m.T for m in mel], batch_first=True).transpose(1, 2)
    return pad(phon, batch_first=True), tl, mel, ml, pad(f0n, batch_first=True), pad(en, batch_first=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("feats"); ap.add_argument("ckpt")
    ap.add_argument("--steps", type=int, default=120000); ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.ckpt, exist_ok=True)
    dev = "cuda"
    data = Feats(a.feats)
    model = UnityVoice(len(data.vocab)).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, betas=(0.9, 0.98), weight_decay=1e-6)
    warm = 4000
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min((s + 1) / warm, (warm / (s + 1)) ** 0.5))
    step, path = 0, os.path.join(a.ckpt, "acoustic.pt")
    if os.path.exists(path):
        ck = torch.load(path, map_location=dev)
        model.load_state_dict(ck["model"]); opt.load_state_dict(ck["opt"]); sched.load_state_dict(ck["sched"])
        step = ck["step"]
        print("resumed at step", step)
    json.dump({"vocab": data.vocab, "stats": data.stats}, open(os.path.join(a.ckpt, "voice-meta.json"), "w",
              encoding="utf-8"), ensure_ascii=False)
    loader = DataLoader(data, batch_size=a.batch, shuffle=True, collate_fn=collate, num_workers=0 if a.smoke else 4,
                        drop_last=not a.smoke, persistent_workers=not a.smoke)
    t0 = time.time()
    while step < a.steps:
        for phon, tl, mel, ml, f0n, en in loader:
            phon, tl, mel, ml, f0n, en = [x.to(dev) for x in (phon, tl, mel, ml, f0n, en)]
            o = model(phon, tl, mel, ml, f0n, en)
            fm = mask_from_lens(ml, mel.size(2))[:, None, :].float()
            T = min(o["mel_hat"].size(2), mel.size(2))
            l_mel = (F.l1_loss(o["mel_hat"][..., :T], mel[..., :T], reduction="none") * fm[..., :T]).sum() / (fm.sum() * 80)
            l_align = forward_sum_loss(o["logp"], tl, ml)
            tr = o["text_real"].float()
            soft = torch.softmax(o["logp"], dim=-1)
            hard = torch.zeros_like(soft)
            for b in range(soft.size(0)):
                idx = torch.repeat_interleave(torch.arange(int(tl[b]), device=dev), o["dur"][b, : int(tl[b])])
                hard[b, torch.arange(idx.size(0), device=dev), idx] = 1
            l_bin = -(torch.log(soft.clamp(min=1e-12)) * hard).sum() / hard.sum()
            bin_w = 0.0 if step < 6000 else min(1.0, (step - 6000) / 6000)
            l_dur = (F.mse_loss(o["d_hat"], torch.log(o["dur"].float() + 1), reduction="none") * tr).sum() / tr.sum()
            l_p = (F.mse_loss(o["p_hat"], o["p_tgt"], reduction="none") * tr).sum() / tr.sum()
            l_e = (F.mse_loss(o["e_hat"], o["e_tgt"], reduction="none") * tr).sum() / tr.sum()
            loss = l_mel + l_align + bin_w * l_bin + 0.1 * (l_dur + l_p + l_e)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step(); sched.step(); step += 1
            if step % 100 == 0 or a.smoke:
                print("step %d  mel %.3f  align %.3f  bin %.3f  dur %.3f  pitch %.3f  energy %.3f  (%.1f s)" % (
                    step, l_mel.item(), l_align.item(), l_bin.item(), l_dur.item(), l_p.item(), l_e.item(),
                    time.time() - t0), flush=True)
            if step % 2000 == 0 or step >= a.steps:
                torch.save({"model": model.state_dict(), "opt": opt.state_dict(), "sched": sched.state_dict(),
                            "step": step, "n_symbols": len(data.vocab)}, path + ".tmp")
                os.replace(path + ".tmp", path)
            if step >= a.steps:
                break
    print("acoustic: done at step", step)


if __name__ == "__main__":
    main()
