"""Synthesize with a matching own-weight v2 acoustic/vocoder pair.

python training/voice/infer.py <ckpt_dir> "text" <new_out.wav> --emotion warm --intensity .35
--speech-act yes_no_question --pace 1.0

These are learned spoken styles, not fabricated laugh/sob modes. A completed checkpoint
is not an accepted stream voice; deployment is governed by the separate quality gate.
"""
import argparse
import importlib.metadata
import json
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from misaki import en, espeak

from dataset_contract import (ACOUSTIC_CONFIG, CHECKPOINT_SCHEMA, EMOTIONS, FEATURES, MAX_PHONEMES,
                              SPEECH_ACTS, VOCODER_CONFIG, canonical_hash, delivery, file_hash, require_checkpoint)
from model import UnityVoice
from vocoder import Generator


def inferred_speech_act(text):
    """Minimal punctuation fallback; callers should supply intent for ambiguous/rhetorical speech."""
    if text.rstrip().endswith("?"):
        first = text.lower().lstrip().split(maxsplit=1)[0].strip(".,?!:;")
        return "wh_question" if first in ("what", "who", "where", "when", "why", "how", "which", "whose") else "yes_no_question"
    return "exclamation" if text.rstrip().endswith("!") else "statement"


def validate_metadata(meta):
    identity = meta.get("identity", {})
    if (meta.get("schema") != CHECKPOINT_SCHEMA or identity.get("schema") != CHECKPOINT_SCHEMA
            or meta.get("pair_id") != canonical_hash(identity) or identity.get("acoustic_config") != ACOUSTIC_CONFIG
            or identity.get("vocoder_config") != VOCODER_CONFIG or identity.get("emotions") != list(EMOTIONS)
            or identity.get("speech_acts") != list(SPEECH_ACTS)):
        raise ValueError("Legacy/mismatched voice metadata; v2 needs an identity-bound trained model pair")
    vocab = meta["vocab"]
    if (vocab.get("<pad>") != 0 or set(vocab.values()) != set(range(len(vocab)))
            or identity.get("vocab_id") != canonical_hash(vocab)):
        raise ValueError("Phoneme vocabulary identity is invalid")
    frontend = meta["frontend"]
    if (frontend["config"]["features"] != FEATURES or canonical_hash(frontend["config"]) != frontend["frontend_id"]
            or frontend["frontend_id"] != identity.get("frontend_id")):
        raise ValueError("Frontend/feature configuration mismatch")
    if importlib.metadata.version("misaki") != FEATURES["misaki_version"]:
        raise ValueError("Runtime requires the same misaki==0.9.4 phoneme frontend")
    if (meta["stats"].get("normalization_split") != "train" or canonical_hash(meta["stats"]) != identity.get("stats_id")
            or canonical_hash(meta.get("delivery_support")) != identity.get("support_id")):
        raise ValueError("Voice normalization lacks the v2 train-only identity")
    return identity


class Voice:
    def __init__(self, ckpt, dev=None):
        self.dev = dev or ("cuda" if torch.cuda.is_available() else "cpu")
        path = Path(ckpt)
        meta = json.loads((path / "voice-meta.json").read_text(encoding="utf-8"))
        identity = validate_metadata(meta)
        acoustic = torch.load(path / "acoustic.pt", map_location=self.dev, weights_only=True)
        vocoder = torch.load(path / "vocoder.pt", map_location=self.dev, weights_only=True)
        require_checkpoint(acoustic, identity, "acoustic")
        require_checkpoint(vocoder, identity, "vocoder")
        if acoustic.get("n_symbols") != len(meta["vocab"]) or min(acoustic.get("step", 0), vocoder.get("step", 0)) < 1:
            raise ValueError("Model pair is untrained or has the wrong symbol count")
        mode = vocoder.get("input_mode")
        provenance = vocoder.get("input_provenance")
        if mode == "source":
            if provenance != {"mode": "source", "feature_id": identity["feature_id"]}:
                raise ValueError("Vocoder source provenance differs from this pair")
        elif mode == "oracle-gta":
            acoustic_sha = acoustic.get("working_checkpoint_sha256") or file_hash(path / "acoustic.pt")
            if (not isinstance(provenance, dict) or set(provenance) != {"mode", "feature_id", "acoustic_sha256", "mel_manifest_sha256"}
                    or provenance["mode"] != mode or provenance["feature_id"] != identity["feature_id"]
                    or provenance["acoustic_sha256"] != acoustic_sha):
                raise ValueError("GTA vocoder was trained for another exact acoustic checkpoint/export")
        else:
            raise ValueError("Vocoder lacks a supported exact input provenance")
        self.vocab = meta["vocab"]
        self.support = meta["delivery_support"]
        self.am = UnityVoice(len(self.vocab), **ACOUSTIC_CONFIG).to(self.dev).eval()
        self.am.load_state_dict(acoustic["model"])
        self.voc = Generator(**VOCODER_CONFIG).to(self.dev).eval()
        self.voc.load_state_dict(vocoder["G"])
        self.g2p = en.G2P(trf=False, british=False, fallback=espeak.EspeakFallback(british=False))

    @torch.no_grad()
    def say(self, text, emotion="neutral", intensity=None, pace=1.0, speech_act=None):
        if not isinstance(text, str) or not text.strip() or len(text) > 4000:
            raise ValueError("Speech text must be nonempty and bounded")
        chosen = delivery(emotion, (0.0 if emotion == "neutral" else 0.35) if intensity is None else intensity,
                          pace, speech_act or inferred_speech_act(text))
        support = next((row for row in self.support if row["emotion"] == chosen["emotion"] and row["speech_act"] == chosen["speech_act"]), None)
        if (support is None or not support["intensity_min"] <= chosen["intensity"] <= support["intensity_max"]
                or not support["pace_min"] <= chosen["pace"] <= support["pace_max"]):
            raise ValueError("Requested delivery is outside this pair's recorded training support; no unseen acting is promised")
        phon = self.g2p(text)[0]
        if not phon or len(phon) > MAX_PHONEMES:
            raise ValueError("No usable phonemes or utterance too long; split into sentences")
        unknown = sorted(set(phon) - set(self.vocab))
        if unknown:
            raise ValueError("Unknown phonemes must be repaired in the pronunciation/frontend data, not dropped: " + repr(unknown))
        ids = torch.tensor([[self.vocab[char] for char in phon]], device=self.dev, dtype=torch.long)
        condition = {"emotion": torch.tensor([EMOTIONS.index(chosen["emotion"])], device=self.dev, dtype=torch.long),
                     "speech_act": torch.tensor([SPEECH_ACTS.index(chosen["speech_act"])], device=self.dev, dtype=torch.long),
                     "intensity": torch.tensor([chosen["intensity"]], device=self.dev, dtype=torch.float32),
                     "pace": torch.tensor([chosen["pace"]], device=self.dev, dtype=torch.float32)}
        mel = self.am.infer(ids, condition)
        wav = self.voc(mel).squeeze().float().cpu().numpy()
        if wav.ndim != 1 or not len(wav) or not np.isfinite(wav).all():
            raise ValueError("Vocoder produced invalid audio")
        return wav


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ckpt"); parser.add_argument("text"); parser.add_argument("out")
    parser.add_argument("--emotion", default="neutral", choices=EMOTIONS)
    parser.add_argument("--intensity", type=float)
    parser.add_argument("--pace", type=float, default=1.0)
    parser.add_argument("--speech-act", choices=SPEECH_ACTS)
    args = parser.parse_args()
    destination = Path(args.out)
    if destination.exists():
        raise ValueError("Output already exists; preserve it and choose a new sample path")
    wav = Voice(args.ckpt).say(args.text, args.emotion, args.intensity, args.pace, args.speech_act)
    destination.parent.mkdir(parents=True, exist_ok=True)
    sf.write(destination, wav, FEATURES["sample_rate"], subtype="PCM_16")
    print("wrote", destination, "-- sample only; no quality acceptance implied")


if __name__ == "__main__":
    main()
