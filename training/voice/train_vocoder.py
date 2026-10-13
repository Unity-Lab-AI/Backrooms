"""Train the own-weight v2 vocoder on exact, identity-bound waveform/mel pairs.

Uses the same explicit-pad mel definition as prep.py. GTA remains oracle reconstruction,
not live predicted prosody. Every legacy checkpoint and unmanifested leftover is refused.
"""
import argparse
import json
import os
import random
import time
import uuid
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
import torch.nn.functional as F
import torchaudio

from dataset_contract import (CHECKPOINT_SCHEMA, FEATURES, VOCODER_CONFIG, ensure_voice_metadata, file_hash, load_dataset,
                              load_features, local_path, pair_identity, require_checkpoint, voice_metadata)
from vocoder import Generator, Discriminators, d_loss, g_loss, fm_loss
from feature_arrays import read_feature, require_prepared_frontend
from student_state import (capture_random_state, require_finite_state, require_student_checkpoint,
                           restore_random_state, student_source_identity)

SR, HOP, SEG = FEATURES["sample_rate"], FEATURES["hop"], 8192
FR = SEG // HOP
SILENT = float(np.log(FEATURES["log_floor"]))


def load_all(dataset, feature_root, manifest, gta, acoustic_path):
    rows, identity = load_dataset(dataset, verify_audio=True)
    if identity != manifest["dataset"]:
        raise ValueError("Vocoder source dataset differs from its acoustic feature identity")
    row_by_id = {row["id"]: row for row in rows}
    gta_entries = {}
    if gta:
        record = json.loads((Path(gta) / "mel-manifest.json").read_text(encoding="utf-8"))
        if (record.get("schema") != CHECKPOINT_SCHEMA or record.get("mode") != "oracle-gta"
                or record.get("identity") != pair_identity(manifest) or record.get("student_source") != student_source_identity()):
            raise ValueError("GTA mel identity/mode differs; predicted unaligned mels are not waveform targets")
        if not Path(acoustic_path).is_file() or record.get("acoustic_sha256") != file_hash(acoustic_path):
            raise ValueError("GTA export belongs to another acoustic checkpoint")
        gta_entries = {entry["id"]: entry for entry in record["entries"]}
        if len(gta_entries) != len(record["entries"]) or set(gta_entries) != set(row_by_id):
            raise ValueError("GTA export is incomplete or contains duplicate/extra ids")
        if {p.name for p in Path(gta).glob("*.npy")} != {entry["file"] for entry in gta_entries.values()}:
            raise ValueError("GTA has unmanifested leftovers/missing entries")
    items = []
    for entry in manifest["entries"]:
        feature = read_feature(local_path(feature_root, entry["feature"]), entry, manifest["vocab"])
        row = row_by_id[entry["id"]]
        if row["sha256"] != entry["audio_sha256"] or row["audio"] != entry["audio"]:
            raise ValueError("Feature/source waveform binding changed")
        if gta:
            item = gta_entries[entry["id"]]
            source = local_path(gta, item["file"])
            if file_hash(source) != item["sha256"]:
                raise ValueError("GTA mel hash mismatch: " + entry["id"])
            mel = np.load(source, allow_pickle=False)
        else:
            mel = feature["mel"]
        wav, rate = sf.read(local_path(dataset, row["audio"]), dtype="float32")
        if (rate != SR or wav.ndim != 1 or len(wav) != entry["original_samples"]
                or mel.dtype != np.float32 or mel.shape != (80, entry["frames"])):
            raise ValueError("Waveform/mel shape mismatch: " + entry["id"])
        if not np.isfinite(wav).all() or not np.isfinite(mel).all() or entry["samples"] != entry["frames"] * HOP:
            raise ValueError("Nonfinite waveform/mel or mismatched feature hop")
        wav = np.pad(wav, (0, entry["samples"] - len(wav)))
        if mel.shape[1] < FR:
            mel = np.pad(mel, ((0, 0), (0, FR - mel.shape[1])), constant_values=SILENT)
            wav = np.pad(wav, (0, FR * HOP - len(wav)))
        items.append((entry["id"], entry["split"], mel.astype(np.float32), wav))
    return items


def batch(items, count):
    mels, wavs = [], []
    for _, _, mel, wav in random.sample(items, count):
        start = random.randint(0, mel.shape[1] - FR)
        mels.append(mel[:, start:start + FR]); wavs.append(wav[start * HOP:start * HOP + SEG])
    return torch.from_numpy(np.stack(mels)), torch.from_numpy(np.stack(wavs))[:, None]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset"); parser.add_argument("feats"); parser.add_argument("ckpt")
    parser.add_argument("--steps", type=int, default=120000); parser.add_argument("--batch", type=int, default=32)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--gta"); parser.add_argument("--smoke", action="store_true")
    # A GTA polish on a NEW acoustic model, started from deployed (weights-only) vocoder weights: the live vocoder was
    # saved without its discriminator/optimizers, and the only full checkpoint is far older. A fresh discriminator is
    # trained alone for --d-warmup steps first so it cannot tear the generator apart.
    parser.add_argument("--warm-generator", help="deployed vocoder.pt whose G starts a fresh --gta run")
    parser.add_argument("--d-warmup", type=int, default=2000)
    args = parser.parse_args()
    if args.warm_generator and not args.gta:
        raise ValueError("--warm-generator is only for a GTA polish (--gta)")
    if args.steps < 1 or args.batch < 1 or not 0 <= args.seed < 2 ** 32 or not torch.cuda.is_available():
        raise ValueError("Invalid vocoder configuration or CUDA unavailable")
    random.seed(args.seed); np.random.seed(args.seed); torch.manual_seed(args.seed)
    dev = "cuda"
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    torch.backends.cudnn.benchmark = True
    manifest = load_features(args.feats, verify_files=True)
    require_prepared_frontend(manifest)
    identity, metadata = pair_identity(manifest), voice_metadata(manifest)
    items = load_all(args.dataset, args.feats, manifest, args.gta, Path(args.ckpt) / "acoustic.pt")
    input_provenance = {"mode": "oracle-gta" if args.gta else "source", "feature_id": manifest["feature_id"]}
    if args.gta:
        gta_manifest = Path(args.gta) / "mel-manifest.json"
        gta_record = json.loads(gta_manifest.read_text(encoding="utf-8"))
        input_provenance.update(acoustic_sha256=gta_record["acoustic_sha256"],
                                mel_manifest_sha256=file_hash(gta_manifest))
    train = [item for item in items if item[1] == "train"]
    held = [item for item in items if item[1] == "heldout"][:24]
    if len(train) < args.batch:
        raise ValueError("Vocoder batch exceeds available train clips")
    generator, discriminator = Generator(**VOCODER_CONFIG).to(dev), Discriminators().to(dev)
    og = torch.optim.AdamW(generator.parameters(), 2e-4, betas=(0.8, 0.99), fused=True)
    od = torch.optim.AdamW(discriminator.parameters(), 2e-4, betas=(0.8, 0.99), fused=True)
    sg, sd = torch.optim.lr_scheduler.ExponentialLR(og, 0.999), torch.optim.lr_scheduler.ExponentialLR(od, 0.999)
    training_config = {"seed": args.seed, "batch": args.batch, "segment_samples": SEG, "optimizer": "AdamW-fused",
                       "learning_rate": 2e-4, "scheduler_gamma": .999, "scheduler_interval": 1000, "precision": "fp32"}
    mel_fn = torchaudio.transforms.MelSpectrogram(SR, n_fft=1024, win_length=1024, hop_length=HOP,
                                                  f_min=0, f_max=SR // 2, n_mels=80, power=1.0,
                                                  center=False, norm=None, mel_scale="htk").to(dev)

    def logmel(wav):
        padded = F.pad(wav.unsqueeze(1), (FEATURES["reflect_pad"], FEATURES["reflect_pad"]), mode="reflect").squeeze(1)
        return torch.log(mel_fn(padded).clamp(min=FEATURES["log_floor"]))

    directory = Path(args.ckpt)
    directory.mkdir(parents=True, exist_ok=True)
    path, meta_path = directory / "vocoder.pt", directory / "voice-meta.json"
    if meta_path.exists() and json.loads(meta_path.read_text(encoding="utf-8")) != metadata:
        raise ValueError("Checkpoint metadata is legacy or belongs to another pair")
    step = 0
    warm_start, d_only_until = None, 0
    if path.exists():
        checkpoint = torch.load(path, map_location=dev, weights_only=True)
        require_checkpoint(checkpoint, identity, "vocoder")
        require_student_checkpoint(checkpoint)
        if not {"G", "D", "og", "od", "sg", "sd", "step", "seed", "rng", "training_config"} <= set(checkpoint):
            raise ValueError("Deployment-only vocoder weights cannot resume training; keep the full working checkpoint")
        previous_mode = checkpoint.get("input_mode")
        previous_provenance = checkpoint.get("input_provenance")
        source_provenance = {"mode": "source", "feature_id": manifest["feature_id"]}
        if previous_mode == "source":
            if previous_provenance != source_provenance:
                raise ValueError("Source vocoder checkpoint lacks exact input provenance")
            # Explicit --gta is the one permitted source-to-GTA transition.
        elif previous_mode == "oracle-gta":
            if not args.gta or previous_provenance != input_provenance:
                raise ValueError("GTA checkpoint cannot resume another acoustic/export or source-only stage")
        else:
            raise ValueError("Unknown/unidentified vocoder input mode; use a fresh v2 run")
        if checkpoint.get("seed") != args.seed:
            raise ValueError("Resume seed differs from the original run")
        if checkpoint["training_config"] != training_config:
            raise ValueError("Resume vocoder batch/training configuration differs")
        require_finite_state({key: checkpoint[key] for key in ("G", "D", "og", "od", "sg", "sd")}, "vocoder")
        generator.load_state_dict(checkpoint["G"]); discriminator.load_state_dict(checkpoint["D"])
        og.load_state_dict(checkpoint["og"]); od.load_state_dict(checkpoint["od"])
        sg.load_state_dict(checkpoint["sg"]); sd.load_state_dict(checkpoint["sd"]); step = checkpoint["step"]
        if type(step) is not int or step < 1:
            raise ValueError("Working vocoder checkpoint has no valid completed step")
        restore_random_state(checkpoint["rng"])
        warm_start = checkpoint.get("warm_start")
        if warm_start:
            d_only_until = warm_start["d_only_until"]
        print("resumed v2 vocoder at step", step, flush=True)
    elif args.warm_generator:
        deployed = torch.load(args.warm_generator, map_location=dev, weights_only=True)
        # The vocoder only sees audio and mels: a re-prepared text frontend (feature_id/frontend_id) does not change
        # what its weights learned. Every other identity field must match; both identities are recorded.
        text_side = ("feature_id", "frontend_id")
        theirs = deployed.get("identity") or {}
        if deployed.get("kind") != "vocoder" or {k: v for k, v in theirs.items() if k not in text_side} != \
                {k: v for k, v in identity.items() if k not in text_side}:
            raise ValueError("Deployed vocoder belongs to another dataset/audio pair")
        require_finite_state({"G": deployed["G"]}, "vocoder")
        generator.load_state_dict(deployed["G"])
        step = int(deployed.get("step") or 0)
        if step < 1:
            raise ValueError("Deployed vocoder has no recorded step")
        d_only_until = step + max(0, args.d_warmup)
        warm_start = {"from": str(args.warm_generator), "sha256": file_hash(args.warm_generator), "from_step": step,
                      "from_mode": deployed.get("input_mode"), "d_only_until": d_only_until,
                      "from_identity": theirs}
        print("warm start from deployed G at step %d; discriminator alone until %d" % (step, d_only_until), flush=True)
    elif (directory / "acoustic.pt").exists() and not meta_path.exists():
        raise ValueError("Unidentified acoustic checkpoint; use a fresh v2 directory")
    ensure_voice_metadata(directory, manifest)
    print("vocoder v2: %d train clips, %d heldout clips; %s input; pair %s" % (
        len(train), len(held), "ORACLE GTA" if args.gta else "source waveform", metadata["pair_id"]), flush=True)
    started, start_step = time.time(), step
    while step < args.steps:
        mel, wav = batch(train, args.batch)
        mel, wav = mel.to(dev, non_blocking=True), wav.to(dev, non_blocking=True)
        fake = generator(mel)
        if fake.shape != wav.shape:
            raise ValueError("Vocoder output is not exactly one HOP per feature frame")
        ld = d_loss(discriminator(wav), discriminator(fake.detach()))
        if not torch.isfinite(ld).item():
            raise ValueError("Nonfinite discriminator loss; training stopped")
        od.zero_grad(set_to_none=True); ld.backward()
        torch.nn.utils.clip_grad_norm_(discriminator.parameters(), float("inf"), error_if_nonfinite=True)
        od.step()
        if step < d_only_until:   # warm start: the fresh discriminator learns the live voice before G moves
            step += 1
            if step % 200 == 0 or args.smoke:
                print("step %d disc-warmup disc %.3f" % (step, ld.item()), flush=True)
            continue
        for parameter in discriminator.parameters():
            parameter.requires_grad_(False)
        with torch.no_grad():
            real_out = discriminator(wav)
        fake_out = discriminator(fake)
        l_mel = F.l1_loss(logmel(fake.squeeze(1)), logmel(wav.squeeze(1)))
        lg = g_loss(fake_out) + 2 * fm_loss(real_out, fake_out) + 45 * l_mel
        if not torch.isfinite(lg).item():
            raise ValueError("Nonfinite generator loss; training stopped")
        og.zero_grad(set_to_none=True); lg.backward()
        torch.nn.utils.clip_grad_norm_(generator.parameters(), float("inf"), error_if_nonfinite=True)
        og.step()
        for parameter in discriminator.parameters():
            parameter.requires_grad_(True)
        step += 1
        if step % 1000 == 0:
            sg.step(); sd.step()
        if step % 200 == 0 or args.smoke:
            print("step %d gen %.3f disc %.3f reconstruction_mel %.3f (%.2f steps/s)" % (
                step, lg.item(), ld.item(), l_mel.item(), (step - start_step) / (time.time() - started)), flush=True)
        if step % 5000 == 0 or step >= args.steps:
            generator.eval()
            with torch.no_grad():
                errors = []
                for _, _, mel, wav in held:
                    out = generator(torch.from_numpy(mel)[None].to(dev)).squeeze(1)
                    target = torch.from_numpy(wav)[None].to(dev)
                    errors.append(F.l1_loss(logmel(out), logmel(target)).item())
            print("HELDOUT_RECONSTRUCTION step %d mel %.4f; NOT full TTS quality acceptance" % (step, sum(errors) / len(errors)), flush=True)
            generator.train()
            temporary = path.with_name(path.name + ".writing-" + uuid.uuid4().hex)
            torch.save({"schema": CHECKPOINT_SCHEMA, "kind": "vocoder", "identity": identity, "G": generator.state_dict(),
                        "student_source": student_source_identity(), "training_config": training_config,
                        "D": discriminator.state_dict(), "og": og.state_dict(), "od": od.state_dict(),
                        "sg": sg.state_dict(), "sd": sd.state_dict(), "step": step, "seed": args.seed,
                        "rng": capture_random_state(), "input_mode": input_provenance["mode"], "input_provenance": input_provenance,
                        "warm_start": warm_start}, temporary)
            os.replace(temporary, path)
    print("vocoder: completed configured steps; naturalness and deployment remain unverified", flush=True)


if __name__ == "__main__":
    main()
