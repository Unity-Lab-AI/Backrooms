"""Train the vocoder from random weights on (mel, waveform) pairs.

    python training/voice/train_vocoder.py <dataset_dir> <features_dir> <ckpt_dir> [--steps N] [--batch B] [--smoke]

Random 8192-sample windows (32 mel frames). Losses: LSGAN adversarial, feature matching x2, mel L1 x45.
Resumes from <ckpt_dir>/vocoder.pt.
"""
import argparse, glob, os, random, time
import numpy as np, soundfile as sf, torch, torchaudio
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from vocoder import Generator, Discriminators, d_loss, g_loss, fm_loss

SR, HOP, SEG = 24000, 256, 8192


class Pairs(Dataset):
    def __init__(self, wavs, feats):
        self.items = [(os.path.join(wavs, os.path.basename(f)[:-4] + ".wav"), f) for f in sorted(glob.glob(os.path.join(feats, "*.npz")))]

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        wav_path, npz = self.items[i]
        mel = np.load(npz)["mel"]
        wav, _ = sf.read(wav_path, dtype="float32")
        frames = SEG // HOP
        if mel.shape[1] <= frames:
            mel = np.pad(mel, ((0, 0), (0, frames - mel.shape[1] + 1)), constant_values=np.log(1e-5))
        s = random.randint(0, mel.shape[1] - frames - 1)
        seg = wav[s * HOP: s * HOP + SEG]
        seg = np.pad(seg, (0, SEG - len(seg)))
        return torch.from_numpy(mel[:, s: s + frames].copy()), torch.from_numpy(seg)[None]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset"); ap.add_argument("feats"); ap.add_argument("ckpt")
    ap.add_argument("--steps", type=int, default=250000); ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.ckpt, exist_ok=True)
    dev = "cuda"
    G, D = Generator().to(dev), Discriminators().to(dev)
    og = torch.optim.AdamW(G.parameters(), 2e-4, betas=(0.8, 0.99))
    od = torch.optim.AdamW(D.parameters(), 2e-4, betas=(0.8, 0.99))
    sg = torch.optim.lr_scheduler.ExponentialLR(og, 0.999)
    sd = torch.optim.lr_scheduler.ExponentialLR(od, 0.999)
    mel_fn = torchaudio.transforms.MelSpectrogram(SR, n_fft=1024, win_length=1024, hop_length=HOP, f_min=0, f_max=SR // 2,
                                                  n_mels=80, power=1.0, center=True).to(dev)
    step, path = 0, os.path.join(a.ckpt, "vocoder.pt")
    if os.path.exists(path):
        ck = torch.load(path, map_location=dev)
        G.load_state_dict(ck["G"]); D.load_state_dict(ck["D"]); og.load_state_dict(ck["og"]); od.load_state_dict(ck["od"])
        sg.load_state_dict(ck["sg"]); sd.load_state_dict(ck["sd"]); step = ck["step"]
        print("resumed at step", step)
    loader = DataLoader(Pairs(os.path.join(a.dataset, "wavs"), a.feats), batch_size=a.batch, shuffle=True,
                        num_workers=0 if a.smoke else 6, drop_last=not a.smoke, persistent_workers=not a.smoke)
    t0 = time.time()
    while step < a.steps:
        for mel, wav in loader:
            mel, wav = mel.to(dev), wav.to(dev)
            fake = G(mel)[..., : wav.size(-1)]
            ld = d_loss(D(wav), D(fake.detach()))
            od.zero_grad(set_to_none=True); ld.backward(); od.step()
            real_o, fake_o = D(wav), D(fake)
            l_mel = F.l1_loss(torch.log(mel_fn(fake.squeeze(1)).clamp(min=1e-5)), torch.log(mel_fn(wav.squeeze(1)).clamp(min=1e-5)))
            lg = g_loss(fake_o) + 2 * fm_loss(real_o, fake_o) + 45 * l_mel
            og.zero_grad(set_to_none=True); lg.backward(); og.step()
            step += 1
            if step % 1000 == 0:
                sg.step(); sd.step()
            if step % 200 == 0 or a.smoke:
                print("step %d  gen %.3f  disc %.3f  mel %.3f  (%.1f s)" % (step, lg.item(), ld.item(), l_mel.item(), time.time() - t0), flush=True)
            if step % 5000 == 0 or step >= a.steps:
                torch.save({"G": G.state_dict(), "D": D.state_dict(), "og": og.state_dict(), "od": od.state_dict(),
                            "sg": sg.state_dict(), "sd": sd.state_dict(), "step": step}, path + ".tmp")
                os.replace(path + ".tmp", path)
            if step >= a.steps:
                break
    print("vocoder: done at step", step)


if __name__ == "__main__":
    main()
