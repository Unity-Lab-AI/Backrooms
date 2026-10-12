"""Speak with Unity's own voice: text -> phonemes -> acoustic model (emotion knobs) -> vocoder -> 24 kHz wav.

    python training/voice/infer.py <ckpt_dir> "text" out.wav [--emotion warm]

<ckpt_dir> holds acoustic.pt, vocoder.pt and voice-meta.json. Pitch and energy are in normalized units
(1.0 = one standard deviation of her own range), pace multiplies phoneme durations.
"""
import argparse, json, os, sys
import soundfile as sf, torch
from misaki import en, espeak

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model import UnityVoice
from vocoder import Generator

# Each preset: pitch shift, pitch range (how far each phoneme strays from her mean), pitch contour over the
# line (position 0..1 -> offset), energy shift and range, pace (duration multiplier, <1 faster) and an end
# drag (the last part of the line slowed, for weight).
PRESETS = {
    "neutral": dict(shift=0.0, rng=1.0, contour=lambda x: 0 * x, e=0.0, erng=1.0, pace=1.0, drag=1.0),
    "warm":    dict(shift=-0.2, rng=1.2, contour=lambda x: -0.3 * x, e=-0.3, erng=0.8, pace=1.08, drag=1.15),
    "hype":    dict(shift=0.7, rng=1.7, contour=lambda x: 0.3 * torch.sin(x * 6.28), e=0.8, erng=1.4, pace=0.86, drag=1.0),
    "panic":   dict(shift=1.1, rng=1.9, contour=lambda x: 0.6 * x, e=1.0, erng=1.6, pace=0.78, drag=0.9),
    "laugh":   dict(shift=0.8, rng=2.1, contour=lambda x: 0.5 * torch.sin(x * 18.0), e=0.6, erng=1.8, pace=0.9, drag=1.0),
    "choked":  dict(shift=-0.4, rng=1.6, contour=lambda x: -0.9 * x + 0.25 * torch.sin(x * 25.0), e=-0.7, erng=1.5, pace=1.25, drag=1.5),
}


class Voice:
    def __init__(self, ckpt, dev="cuda" if torch.cuda.is_available() else "cpu"):
        meta = json.load(open(os.path.join(ckpt, "voice-meta.json"), encoding="utf-8"))
        self.vocab, self.dev = meta["vocab"], dev
        a = torch.load(os.path.join(ckpt, "acoustic.pt"), map_location=dev)
        self.am = UnityVoice(a["n_symbols"]).to(dev).eval()
        self.am.load_state_dict(a["model"])
        self.voc = Generator().to(dev).eval()
        self.voc.load_state_dict(torch.load(os.path.join(ckpt, "vocoder.pt"), map_location=dev)["G"])
        self.g2p = en.G2P(trf=False, british=False, fallback=espeak.EspeakFallback(british=False))

    @torch.no_grad()
    def say(self, text, emotion="neutral"):
        p = PRESETS[emotion]
        phon = [self.vocab[c] for c in self.g2p(text)[0] if c in self.vocab]
        ids = torch.tensor([phon], device=self.dev)
        mel = self.am.infer(
            ids,
            pitch_fn=lambda v, x: v * p["rng"] + p["shift"] + p["contour"](x),
            energy_fn=lambda v, x: v * p["erng"] + p["e"],
            pace_fn=lambda d, x: d * p["pace"] * torch.where(x > 0.75, torch.full_like(x, p["drag"]), torch.ones_like(x)))
        return self.voc(mel).squeeze().cpu().numpy()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("ckpt"); ap.add_argument("text"); ap.add_argument("out")
    ap.add_argument("--emotion", default="neutral", choices=sorted(PRESETS))
    a = ap.parse_args()
    sf.write(a.out, Voice(a.ckpt).say(a.text, a.emotion), 24000)
    print("wrote", a.out)
