"""Prepare a fresh, identity-bound v2 labeled voice dataset. Old CSV data is refused.

python training/voice/prep.py <dataset_dir> <new_feature_dir>
The destination is immutable. Failed preparation remains in its temporary sibling for inspection;
no previous features or recordings are removed. Pitch has a separate voiced/unvoiced mask.
"""
import json
import math
import os
import sys
import uuid
from pathlib import Path

import numpy as np
import pyworld
import soundfile as sf
import torch
import torch.nn.functional as F
import torchaudio
from misaki import en, espeak

from dataset_contract import (EMOTIONS, SPEECH_ACTS, FEATURES, FEATURE_SCHEMA, MAX_PHONEMES, MAX_FRAMES,
                              canonical_hash, file_hash, frontend_identity, load_dataset, load_features,
                              local_path, normalize_transcript, split_for)
from speech_text import EVENT_NAMES, event_counts, event_only_group, speech_tokens
from feature_arrays import read_feature

SR, N_FFT, HOP, N_MELS = (FEATURES[k] for k in ("sample_rate", "n_fft", "hop", "n_mels"))
MEL = torchaudio.transforms.MelSpectrogram(sample_rate=SR, n_fft=N_FFT, win_length=N_FFT, hop_length=HOP,
                                           f_min=FEATURES["f_min"], f_max=FEATURES["f_max"], n_mels=N_MELS,
                                           power=1.0, center=False, norm=None, mel_scale="htk")


def log_mel(wav):
    """Pad centered windows explicitly; one frame per HOP samples, with no extra end frame."""
    tensor = torch.from_numpy(wav)[None, None]
    tensor = F.pad(tensor, (FEATURES["reflect_pad"], FEATURES["reflect_pad"]), mode="reflect").squeeze(0)
    return torch.log(MEL(tensor).clamp(min=FEATURES["log_floor"])).squeeze(0).numpy()


def frame_pitch(wav, frames):
    f0, times = pyworld.dio(wav.astype(np.float64), SR, frame_period=HOP / SR * 1000)
    f0 = pyworld.stonemask(wav.astype(np.float64), f0, times, SR)
    # With the explicit 384-sample pad, window centers are at (frame + .5) * HOP.
    nearest = np.floor(np.arange(frames) + 1.0).astype(np.int64)
    nearest = np.clip(nearest, 0, len(f0) - 1)
    return f0[nearest].astype(np.float32)


def read_audio(src, row):
    wav, rate = sf.read(local_path(src, row["audio"]), dtype="float32")
    if rate != SR or wav.ndim != 1 or not np.isfinite(wav).all():
        raise ValueError("Source must be finite mono 24000 Hz: " + row["id"])
    seconds = len(wav) / SR
    if not FEATURES["min_seconds"] <= seconds <= FEATURES["max_seconds"]:
        raise ValueError("Source duration outside v2 bounds: " + row["id"])
    if np.max(np.abs(wav)) > 1.0 or np.mean(np.abs(wav) >= 0.999) > 0.001 or np.sqrt(np.mean(wav.astype(np.float64) ** 2)) < 1e-5:
        raise ValueError("Source is silent or excessively clipped: " + row["id"])
    original = len(wav)
    samples = math.ceil(original / HOP) * HOP
    return np.pad(wav, (0, samples - original)), original


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: prep.py <v2_dataset_dir> <new_feature_dir>")
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    rows, dataset = load_dataset(src, verify_audio=True)
    frontend = frontend_identity()
    frontend["config"].update(prep_sha256=file_hash(Path(__file__)),
                              feature_arrays_sha256=file_hash(Path(__file__).with_name("feature_arrays.py")))
    frontend["frontend_id"] = canonical_hash(frontend["config"])
    if dst.exists():
        previous = load_features(dst)
        if previous["dataset"] != dataset or previous["frontend"] != frontend:
            raise ValueError("Destination contains a different immutable dataset/frontend; choose a new directory")
        print("prep: existing exact v2 features verified; nothing changed")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    work = dst.with_name(dst.name + ".preparing-" + uuid.uuid4().hex[:12])
    work.mkdir(exist_ok=False)
    g2p = en.G2P(trf=False, british=False, fallback=espeak.EspeakFallback(british=False))
    phonemes = {}
    for row in rows:
        try:
            phonemes[row["id"]] = speech_tokens(row["text"], g2p, MAX_PHONEMES)
        except ValueError as error:
            raise ValueError("Invalid speech frontend input: " + row["id"]) from error
    # Preserve ordinary character/stress ordering; append only manifest-present events.
    # Heldout events may be representable, but inference also requires TRAIN support.
    all_tokens = {token for phon in phonemes.values() for token in phon}
    symbols = sorted(all_tokens - {" "} - set(EVENT_NAMES))
    symbols += sorted(all_tokens.intersection(EVENT_NAMES))
    vocab = {"<pad>": 0, " ": 1, **{char: index + 2 for index, char in enumerate(symbols)}}
    entries, pitches, energies = [], [], []
    for row in rows:
        phon = phonemes[row["id"]]
        wav, original = read_audio(src, row)
        mel = log_mel(wav)
        if not len(phon) <= mel.shape[1] <= MAX_FRAMES or mel.shape[1] * HOP != len(wav):
            raise ValueError("Impossible/overlong monotonic alignment or mel/audio mismatch: " + row["id"])
        f0 = frame_pitch(wav, mel.shape[1])
        voiced = (f0 > 0).astype(np.float32)
        energy = np.exp(mel).mean(0).astype(np.float32)
        if not all(np.isfinite(value).all() for value in (mel, f0, energy)):
            raise ValueError("Nonfinite features: " + row["id"])
        relative = row["id"] + ".npz"
        np.savez(work / relative, phon=np.asarray([vocab[c] for c in phon], dtype=np.int64),
                 mel=mel, f0=f0, energy=energy, voiced=voiced)
        split = split_for(row["text"])
        if split == "train":
            pitches.append(np.log(f0[voiced > 0])); energies.append(energy)
        entry = {key: row[key] for key in ("id", "text", "audio", "voice_id", "source_id", "emotion", "intensity", "pace", "speech_act")}
        entry.update(feature=relative, sha256=file_hash(work / relative), audio_sha256=row["sha256"],
                     split=split, text_group=normalize_transcript(row["text"]) or event_only_group(row["text"]),
                     events=event_counts(row["text"]), samples=len(wav),
                     original_samples=original, frames=mel.shape[1], phonemes=len(phon))
        read_feature(work / relative, entry, vocab)  # verify exact dtype/event/sample contracts before publication
        entries.append(entry)
    lp, energy = np.concatenate(pitches), np.concatenate(energies)
    if not len(lp) or lp.std() < 1e-6 or energy.std() < 1e-6:
        raise ValueError("Training split has no usable voiced pitch/energy variance")
    stats = {"lf0_mean": float(lp.mean()), "lf0_std": float(lp.std()), "e_mean": float(energy.mean()),
             "e_std": float(energy.std()), "normalization_split": "train"}
    body = {"schema": FEATURE_SCHEMA, "dataset": dataset, "frontend": frontend, "vocab": vocab,
            "stats": stats, "emotions": list(EMOTIONS), "speech_acts": list(SPEECH_ACTS), "entries": entries}
    manifest = dict(body, feature_id=canonical_hash(body))
    (work / "features-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    load_features(work)  # verify the exact output before its one atomic publication
    if dst.exists():
        raise ValueError("Feature destination appeared during preparation; preserve both directories")
    os.replace(work, dst)
    print("prep: %d clips, %d symbols; v2 feature_id %s" % (len(rows), len(vocab), manifest["feature_id"]))


if __name__ == "__main__":
    main()
