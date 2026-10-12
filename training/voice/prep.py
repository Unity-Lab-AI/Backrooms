"""Turn the voice dataset into training features: phoneme ids, log-mel, frame pitch and frame energy.

    python training/voice/prep.py <dataset_dir> <out_dir> [limit]

<dataset_dir> holds metadata.csv (key|text|speed|seconds) and wavs/<key>.wav at 24 kHz (LJSpeech layout,
written by .local/voice-lab/make_dataset.py). <out_dir> gets one <key>.npz per clip, vocab.json (phoneme
symbol -> id, built from this data) and stats.json (log-pitch and energy mean/std over voiced frames).
Text becomes phonemes with misaki's dictionary G2P -- a pronunciation lookup, no voice in it.
"""
import json, os, sys
import numpy as np, pyworld, soundfile as sf, torch, torchaudio
from misaki import en, espeak

SR, N_FFT, HOP, N_MELS = 24000, 1024, 256, 80
MEL = torchaudio.transforms.MelSpectrogram(sample_rate=SR, n_fft=N_FFT, win_length=N_FFT, hop_length=HOP,
                                           f_min=0, f_max=SR // 2, n_mels=N_MELS, power=1.0, center=True)


def log_mel(wav):
    """wav: float32 numpy at SR -> [N_MELS, T] float32."""
    return torch.log(torch.clamp(MEL(torch.from_numpy(wav)), min=1e-5)).numpy()


def frame_pitch(wav, frames):
    """Hz per mel frame, 0 where unvoiced (WORLD dio + stonemask)."""
    x = wav.astype(np.float64)
    f0, t = pyworld.dio(x, SR, frame_period=HOP / SR * 1000)
    f0 = pyworld.stonemask(x, f0, t, SR)
    out = np.zeros(frames, dtype=np.float32)
    n = min(frames, len(f0))
    out[:n] = f0[:n]
    return out


def main():
    src, dst = sys.argv[1], sys.argv[2]
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else None
    os.makedirs(dst, exist_ok=True)
    g2p = en.G2P(trf=False, british=False, fallback=espeak.EspeakFallback(british=False))
    rows = [l.rstrip("\n").split("|") for l in open(os.path.join(src, "metadata.csv"), encoding="utf-8")][:limit]
    vocab = {"<pad>": 0, " ": 1}
    pitches, energies, kept = [], [], 0
    for key, text, _speed, _secs in rows:
        phon = g2p(text)[0]
        if not phon or "❓" in phon:
            continue
        for ch in phon:
            vocab.setdefault(ch, len(vocab))
        wav, sr = sf.read(os.path.join(src, "wavs", key + ".wav"), dtype="float32")
        assert sr == SR, "%s is %d Hz, expected %d" % (key, sr, SR)
        mel = log_mel(wav)
        f0 = frame_pitch(wav, mel.shape[1])
        energy = np.exp(mel).mean(0).astype(np.float32)
        np.savez(os.path.join(dst, key + ".npz"), phon=phon, mel=mel, f0=f0, energy=energy)
        pitches.append(np.log(f0[f0 > 0]))
        energies.append(energy)
        kept += 1
    lp, e = np.concatenate(pitches), np.concatenate(energies)
    json.dump(vocab, open(os.path.join(dst, "vocab.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump({"lf0_mean": float(lp.mean()), "lf0_std": float(lp.std()), "e_mean": float(e.mean()), "e_std": float(e.std()),
               "clips": kept}, open(os.path.join(dst, "stats.json"), "w"), indent=1)
    print("prep: %d of %d clips, %d symbols, pitch %.0f Hz median" % (kept, len(rows), len(vocab), float(np.exp(np.median(lp)))))


if __name__ == "__main__":
    main()
