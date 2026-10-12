"""Train the vocoder from random weights on (mel, waveform) pairs, built to keep the GPU busy.

    python training/voice/train_vocoder.py <dataset_dir> <features_dir> <ckpt_dir> [--steps N] [--batch B]
                                           [--gta <gta_dir>] [--smoke]

- Every waveform and mel is loaded into RAM once; batches are random 8192-sample windows cut in memory.
- TF32 matmuls and cuDNN autotuning are on. The GAN itself stays in fp32: half precision destabilises it.
- Clips held out by model.is_heldout are never trained on; every 5000 steps the generator renders them whole
  and the mel L1 against the real audio is logged.
- --gta <dir>: train on the acoustic model's ground-truth-aligned mels (train_acoustic.py --export-gta) instead of
  the real ones, so the vocoder finishes on what it will actually be fed. The audio target stays the real clip.
Losses: LSGAN adversarial, feature matching x2, mel L1 x45. Resumes from <ckpt_dir>/vocoder.pt (every 5000 steps).
"""
import argparse, glob, os, random, sys, time
import numpy as np, soundfile as sf, torch, torchaudio
import torch.nn.functional as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vocoder import Generator, Discriminators, d_loss, g_loss, fm_loss
from model import is_heldout

SR, HOP, SEG = 24000, 256, 8192
FR = SEG // HOP
SILENT = float(np.log(1e-5))


def load_all(dataset, feats, gta):
    items = []
    for f in sorted(glob.glob(os.path.join(feats, "*.npz"))):
        name = os.path.basename(f)[:-4]
        mel = np.load(os.path.join(gta, name + ".npy")) if gta else np.load(f)["mel"]
        wav, sr = sf.read(os.path.join(dataset, "wavs", name + ".wav"), dtype="float32")
        assert sr == SR
        if mel.shape[1] <= FR:
            mel = np.pad(mel, ((0, 0), (0, FR - mel.shape[1] + 1)), constant_values=SILENT)
        wav = np.pad(wav, (0, max(0, mel.shape[1] * HOP - len(wav))))
        items.append((name, mel.astype(np.float32), wav))
    return items


def batch(items, n):
    mels, wavs = [], []
    for name, mel, wav in random.sample(items, n):
        s = random.randint(0, mel.shape[1] - FR - 1)
        mels.append(mel[:, s: s + FR]); wavs.append(wav[s * HOP: s * HOP + SEG])
    return torch.from_numpy(np.stack(mels)), torch.from_numpy(np.stack(wavs))[:, None]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset"); ap.add_argument("feats"); ap.add_argument("ckpt")
    ap.add_argument("--steps", type=int, default=200000); ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--gta"); ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.ckpt, exist_ok=True)
    dev = "cuda"
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    torch.backends.cudnn.benchmark = True
    G, D = Generator().to(dev), Discriminators().to(dev)
    og = torch.optim.AdamW(G.parameters(), 2e-4, betas=(0.8, 0.99), fused=True)
    od = torch.optim.AdamW(D.parameters(), 2e-4, betas=(0.8, 0.99), fused=True)
    sg = torch.optim.lr_scheduler.ExponentialLR(og, 0.999)
    sd = torch.optim.lr_scheduler.ExponentialLR(od, 0.999)
    mel_fn = torchaudio.transforms.MelSpectrogram(SR, n_fft=1024, win_length=1024, hop_length=HOP, f_min=0, f_max=SR // 2,
                                                  n_mels=80, power=1.0, center=True).to(dev)
    logmel = lambda x: torch.log(mel_fn(x).clamp(min=1e-5))
    step, path = 0, os.path.join(a.ckpt, "vocoder.pt")
    if os.path.exists(path):
        ck = torch.load(path, map_location=dev)
        G.load_state_dict(ck["G"]); D.load_state_dict(ck["D"]); og.load_state_dict(ck["og"]); od.load_state_dict(ck["od"])
        sg.load_state_dict(ck["sg"]); sd.load_state_dict(ck["sd"]); step = ck["step"]
        print("resumed at step", step, flush=True)
    items = load_all(a.dataset, a.feats, a.gta)
    train = [x for x in items if not is_heldout(x[0])]
    held = [x for x in items if is_heldout(x[0])][:24]
    print("vocoder: %d train clips, %d held out, mels from %s, %.1f M generator params" % (
        len(train), len(held), "GTA " + a.gta if a.gta else "real audio", sum(p.numel() for p in G.parameters()) / 1e6), flush=True)
    t0 = time.time(); start = step
    while step < a.steps:
        mel, wav = batch(train, a.batch)
        mel, wav = mel.to(dev, non_blocking=True), wav.to(dev, non_blocking=True)
        fake = G(mel)[..., : wav.size(-1)]
        ld = d_loss(D(wav), D(fake.detach()))
        od.zero_grad(set_to_none=True); ld.backward(); od.step()
        real_o, fake_o = D(wav), D(fake)
        l_mel = F.l1_loss(logmel(fake.squeeze(1)), logmel(wav.squeeze(1)))
        lg = g_loss(fake_o) + 2 * fm_loss(real_o, fake_o) + 45 * l_mel
        og.zero_grad(set_to_none=True); lg.backward(); og.step()
        step += 1
        if step % 1000 == 0:
            sg.step(); sd.step()
        if step % 200 == 0 or a.smoke:
            print("step %d  gen %.3f  disc %.3f  mel %.3f  (%.2f steps/s)" % (
                step, lg.item(), ld.item(), l_mel.item(), (step - start) / (time.time() - t0)), flush=True)
        if (step % 5000 == 0 or step >= a.steps) and held:
            G.eval()
            with torch.no_grad():
                errs = []
                for _, m, w in held:
                    y = G(torch.from_numpy(m)[None].to(dev)).squeeze()
                    n = min(len(y), len(w))
                    errs.append(F.l1_loss(logmel(y[:n]), logmel(torch.from_numpy(w[:n]).to(dev))).item())
            print("HELDOUT step %d  mel %.4f  (train mel %.4f)" % (step, sum(errs) / len(errs), l_mel.item()), flush=True)
            G.train()
        if step % 5000 == 0 or step >= a.steps:
            torch.save({"G": G.state_dict(), "D": D.state_dict(), "og": og.state_dict(), "od": od.state_dict(),
                        "sg": sg.state_dict(), "sd": sd.state_dict(), "step": step}, path + ".tmp")
            os.replace(path + ".tmp", path)
    print("vocoder: done at step", step, flush=True)


if __name__ == "__main__":
    main()
