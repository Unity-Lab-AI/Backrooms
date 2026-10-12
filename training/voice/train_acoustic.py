"""Train Unity's own-weight v2 acoustic student on an exact labeled feature manifest.

Oracle reconstruction metrics are labeled ORACLE, not speech-quality claims. Heldout inference
is exported separately with predicted durations/F0/energy. Legacy smoke checkpoints are refused.
No train is started by importing this module.
"""
import argparse
import json
import os
import random
import time
import uuid
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

from dataset_contract import (ACOUSTIC_CONFIG, CHECKPOINT_SCHEMA, EMOTIONS, SPEECH_ACTS, MAX_FRAMES,
                              ensure_voice_metadata, file_hash, load_features, local_path, pair_identity, require_checkpoint, voice_metadata)
from model import UnityVoice, forward_sum_loss, mask_from_lens, token_index
from feature_arrays import read_feature, require_prepared_frontend
from student_state import (capture_random_state, require_data_order, require_finite_state,
                           require_student_checkpoint, restore_random_state, student_source_identity)


def load_all(root):
    manifest = load_features(root, verify_files=True)
    require_prepared_frontend(manifest)
    st, items = manifest["stats"], []
    for entry in manifest["entries"]:
        feature = read_feature(local_path(root, entry["feature"]), entry, manifest["vocab"])
        phon, mel, f0, voiced, energy = (torch.from_numpy(feature[key]) for key in ("phon", "mel", "f0", "voiced", "energy"))
        if (phon.ndim != 1 or len(phon) != entry["phonemes"] or mel.shape != (80, entry["frames"])
                or not len(phon) <= mel.size(1) <= MAX_FRAMES or (phon <= 0).any() or (phon >= len(manifest["vocab"])).any()
                or any(curve.shape != (entry["frames"],) for curve in (f0, voiced, energy))):
            raise ValueError("Invalid feature shapes/phonemes: " + entry["id"])
        if not all(torch.isfinite(value).all().item() for value in (mel, f0, voiced, energy)):
            raise ValueError("Nonfinite feature: " + entry["id"])
        if not ((voiced == 0) | (voiced == 1)).all().item() or (f0 < 0).any().item():
            raise ValueError("Invalid voiced mask/pitch: " + entry["id"])
        f0n = torch.where(voiced > 0, (torch.log(f0.clamp(min=1)) - st["lf0_mean"]) / st["lf0_std"], torch.zeros_like(f0))
        items.append(dict(entry, phon=phon, mel=mel, f0n=f0n, voiced=voiced,
                          en=(energy - st["e_mean"]) / st["e_std"]))
    return manifest, items


def batches(items, max_frames, shuffle=True):
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


def condition_for(entries, dev):
    return {"emotion": torch.tensor([EMOTIONS.index(x["emotion"]) for x in entries], device=dev, dtype=torch.long),
            "speech_act": torch.tensor([SPEECH_ACTS.index(x["speech_act"]) for x in entries], device=dev, dtype=torch.long),
            "intensity": torch.tensor([x["intensity"] for x in entries], device=dev, dtype=torch.float32),
            "pace": torch.tensor([x["pace"] for x in entries], device=dev, dtype=torch.float32)}


def collate(items, idx, dev):
    pad = torch.nn.utils.rnn.pad_sequence
    batch = [items[i] for i in idx]
    tl = torch.tensor([x["phon"].size(0) for x in batch])
    ml = torch.tensor([x["mel"].size(1) for x in batch])
    mel = pad([x["mel"].T for x in batch], batch_first=True).transpose(1, 2)
    values = (pad([x["phon"] for x in batch], batch_first=True), tl, mel, ml,
              pad([x["f0n"] for x in batch], batch_first=True), pad([x["en"] for x in batch], batch_first=True),
              pad([x["voiced"] for x in batch], batch_first=True))
    return tuple(value.to(dev, non_blocking=True) for value in values) + (condition_for(batch, dev),)


def losses(model, batch, step):
    phon, tl, mel, ml, f0n, energy, voiced, condition = batch
    with torch.autocast("cuda", dtype=torch.bfloat16):
        out = model(phon, tl, mel, ml, f0n, energy, voiced, condition)
    frames = mask_from_lens(ml, mel.size(2))[:, None].float()
    if out["mel_hat"].shape != mel.shape:
        raise ValueError("Alignment regulator did not preserve the exact target mel length")
    l_mel = (F.l1_loss(out["mel_hat"].float(), mel, reduction="none") * frames).sum() / (frames.sum() * mel.size(1))
    logp = out["logp"].float()
    l_align = forward_sum_loss(logp, tl, ml)
    idx, real = token_index(out["dur"], logp.size(1))
    soft_on_path = torch.log_softmax(logp, dim=-1).gather(2, idx[..., None]).squeeze(-1)
    l_bin = -(soft_on_path * real).sum() / real.sum()
    tr = out["text_real"].float()
    l_dur = (F.mse_loss(out["d_hat"].float(), torch.log(out["dur"].float() + 1), reduction="none") * tr).sum() / tr.sum()
    pitched = tr * (out["v_tgt"] > 0).float()
    l_pitch = (F.mse_loss(out["p_hat"].float(), out["p_tgt"], reduction="none") * pitched).sum() / pitched.sum().clamp(min=1)
    l_energy = (F.mse_loss(out["e_hat"].float(), out["e_tgt"], reduction="none") * tr).sum() / tr.sum()
    l_voicing = (F.binary_cross_entropy_with_logits(out["v_hat"].float(), out["v_tgt"], reduction="none") * tr).sum() / tr.sum()
    bin_weight = 0.0 if step < 6000 else min(1.0, (step - 6000) / 6000)
    total = l_mel + l_align + bin_weight * l_bin + 0.1 * (l_dur + l_pitch + l_energy + l_voicing)
    if not torch.isfinite(total).item() or (out["dur"][out["text_real"]] < 1).any().item():
        raise ValueError("Nonfinite loss or invalid learned monotonic alignment; training stopped")
    return total, dict(oracle_mel=l_mel, align=l_align, bin=l_bin, dur=l_dur, pitch=l_pitch, energy=l_energy, voicing=l_voicing), out


@torch.no_grad()
def export_mels(model, manifest, items, out_dir, dev, max_frames, mode, checkpoint_path):
    """Immutable exact GTA or heldout text-only output; the two are distinct contracts."""
    destination = Path(out_dir)
    selected = items if mode == "oracle-gta" else [x for x in items if x["split"] == "heldout"]
    checkpoint_hash = file_hash(checkpoint_path)
    if destination.exists():
        record = json.loads((destination / "mel-manifest.json").read_text(encoding="utf-8"))
        if (record.get("schema") != CHECKPOINT_SCHEMA or record.get("identity") != pair_identity(manifest)
                or record.get("mode") != mode or record.get("acoustic_sha256") != checkpoint_hash
                or record.get("student_source") != student_source_identity()
                or {row["id"] for row in record["entries"]} != {row["id"] for row in selected}
                or len(record["entries"]) != len(selected)):
            raise ValueError("Export already exists with another identity/checkpoint; preserve it and choose a fresh path")
        if {path.name for path in destination.glob("*.npy")} != {row["file"] for row in record["entries"]}:
            raise ValueError("Export has unmanifested leftovers/missing files")
        for row in record["entries"]:
            if file_hash(local_path(destination, row["file"])) != row["sha256"]:
                raise ValueError("Existing immutable export hash mismatch")
        print("export: existing exact %s export verified; nothing changed" % mode)
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    work = destination.with_name(destination.name + ".exporting-" + uuid.uuid4().hex[:12])
    work.mkdir(exist_ok=False)
    model.eval()
    exported = []
    for idx in batches(selected, max_frames, shuffle=False):
        if mode == "oracle-gta":
            with torch.autocast("cuda", dtype=torch.bfloat16):
                predicted = model(*collate(selected, idx, dev))["mel_hat"].float()
            outputs = [(selected[i], predicted[k, :, :selected[i]["frames"]]) for k, i in enumerate(idx)]
        else:
            outputs = [(selected[i], model.infer(selected[i]["phon"][None].to(dev), condition_for([selected[i]], dev))[0]) for i in idx]
        for entry, mel in outputs:
            if mel.ndim != 2 or mel.size(0) != 80 or not 0 < mel.size(1) <= MAX_FRAMES or not torch.isfinite(mel).all().item():
                raise ValueError("Invalid/nonfinite exported mel; preserve the unfinished export")
            relative = entry["id"] + ".npy"
            np.save(work / relative, mel.float().cpu().numpy())
            exported.append({"id": entry["id"], "file": relative, "sha256": file_hash(work / relative)})
    record = {"schema": CHECKPOINT_SCHEMA, "identity": pair_identity(manifest), "mode": mode,
              "acoustic_sha256": checkpoint_hash, "student_source": student_source_identity(), "entries": exported}
    (work / "mel-manifest.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    if destination.exists():
        raise ValueError("Export destination appeared concurrently; preserve both directories")
    os.replace(work, destination)
    print("export: %s wrote %d identity-bound mels; listening acceptance remains open" % (mode, len(exported)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("feats"); parser.add_argument("ckpt")
    parser.add_argument("--steps", type=int, default=20000)
    parser.add_argument("--frames", type=int, default=48000)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--export-gta", dest="gta")
    parser.add_argument("--export-heldout-inference", dest="predicted")
    parser.add_argument("--smoke", action="store_true", help="logging only; smoke output is never quality acceptance")
    args = parser.parse_args()
    if args.steps < 1 or args.frames < MAX_FRAMES or not 0 <= args.seed < 2 ** 32 or (args.gta and args.predicted):
        raise ValueError("Invalid training/export configuration")
    dev = "cuda"
    if not torch.cuda.is_available():
        raise ValueError("Acoustic training requires an explicitly prepared CUDA environment")
    random.seed(args.seed); np.random.seed(args.seed); torch.manual_seed(args.seed)
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    torch.backends.cudnn.benchmark = True
    manifest, items = load_all(args.feats)
    identity, metadata = pair_identity(manifest), voice_metadata(manifest)
    train, held = [x for x in items if x["split"] == "train"], [x for x in items if x["split"] == "heldout"]
    model = UnityVoice(len(manifest["vocab"]), **ACOUSTIC_CONFIG).to(dev)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, betas=(0.9, 0.98), weight_decay=1e-6, fused=True)
    warm = 4000
    training_config = {"seed": args.seed, "frame_budget": args.frames, "optimizer": "AdamW-fused",
                       "learning_rate": 1e-3, "warmup": warm, "precision": "bf16-autocast-fp32-losses"}
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lambda s: min((s + 1) / warm, (warm / (s + 1)) ** 0.5))
    directory = Path(args.ckpt)
    directory.mkdir(parents=True, exist_ok=True)
    path, meta_path = directory / "acoustic.pt", directory / "voice-meta.json"
    if meta_path.exists() and json.loads(meta_path.read_text(encoding="utf-8")) != metadata:
        raise ValueError("Checkpoint directory metadata is legacy or belongs to another model pair")
    step, epoch_order, batch_cursor = 0, [], 0
    if path.exists():
        checkpoint = torch.load(path, map_location=dev, weights_only=True)
        require_checkpoint(checkpoint, identity, "acoustic")
        require_student_checkpoint(checkpoint)
        if not {"model", "opt", "sched", "step", "n_symbols", "seed", "rng", "data_order", "training_config"} <= set(checkpoint):
            raise ValueError("Deployment-only acoustic weights cannot resume training; keep the full working checkpoint")
        if checkpoint.get("seed") != args.seed:
            raise ValueError("Resume seed differs; use the original configuration")
        if checkpoint["training_config"] != training_config or checkpoint["n_symbols"] != len(manifest["vocab"]):
            raise ValueError("Resume batch/training configuration or vocabulary differs")
        require_finite_state({key: checkpoint[key] for key in ("model", "opt", "sched")}, "acoustic")
        model.load_state_dict(checkpoint["model"]); optimizer.load_state_dict(checkpoint["opt"]); scheduler.load_state_dict(checkpoint["sched"])
        step = checkpoint["step"]
        if type(step) is not int or step < 1:
            raise ValueError("Working acoustic checkpoint has no valid completed step")
        epoch_order, batch_cursor = checkpoint["data_order"]["batches"], checkpoint["data_order"]["cursor"]
        require_data_order(epoch_order, batch_cursor, len(train))
        restore_random_state(checkpoint["rng"])
        print("resumed v2 acoustic at step", step, flush=True)
    elif args.gta or args.predicted:
        raise ValueError("Cannot export untrained random weights")
    elif (directory / "vocoder.pt").exists() and not meta_path.exists():
        raise ValueError("Unidentified old vocoder checkpoint; use a fresh v2 checkpoint directory")
    if args.gta or args.predicted:
        export_mels(model, manifest, items, args.gta or args.predicted, dev, args.frames, "oracle-gta" if args.gta else "predicted-heldout", path)
        return
    ensure_voice_metadata(directory, manifest)
    print("acoustic v2: %d train clips, %d heldout transcript groups, %.1f M parameters; pair %s" % (
        len(train), len({x["text_group"] for x in held}), sum(p.numel() for p in model.parameters()) / 1e6, metadata["pair_id"]), flush=True)
    start, start_step, frames_seen = time.time(), step, 0
    while step < args.steps:
        model.train()
        if not epoch_order or batch_cursor == len(epoch_order):
            epoch_order, batch_cursor = batches(train, args.frames), 0
        for idx in epoch_order[batch_cursor:]:
            batch = collate(train, idx, dev)
            loss, parts, _ = losses(model, batch, step)
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0, error_if_nonfinite=True)
            optimizer.step(); scheduler.step(); step += 1
            batch_cursor += 1
            frames_seen += int(batch[3].sum())
            if step % 100 == 0 or args.smoke:
                elapsed = time.time() - start
                print("step %d  %s  (%.2f steps/s, %.0f k frames/s)" % (
                    step, "  ".join("%s %.3f" % (key, value.item()) for key, value in parts.items()),
                    (step - start_step) / elapsed, frames_seen / elapsed / 1000), flush=True)
            if step % 2000 == 0 or step >= args.steps:
                model.eval()
                weighted, weight = 0.0, 0
                with torch.no_grad():
                    for held_idx in batches(held, args.frames, False):
                        held_batch = collate(held, held_idx, dev)
                        frames = int(held_batch[3].sum())
                        weighted += losses(model, held_batch, step)[1]["oracle_mel"].item() * frames
                        weight += frames
                print("HELDOUT_ORACLE step %d mel %.4f; NOT a text-only quality score" % (step, weighted / weight), flush=True)
                model.train()
                temporary = path.with_name(path.name + ".writing-" + uuid.uuid4().hex)
                torch.save({"schema": CHECKPOINT_SCHEMA, "kind": "acoustic", "identity": identity,
                            "student_source": student_source_identity(), "training_config": training_config,
                            "model": model.state_dict(), "opt": optimizer.state_dict(), "sched": scheduler.state_dict(),
                            "step": step, "n_symbols": len(manifest["vocab"]), "seed": args.seed,
                            "rng": capture_random_state(), "data_order": {"batches": epoch_order, "cursor": batch_cursor}}, temporary)
                os.replace(temporary, path)
            if step >= args.steps:
                break
    print("acoustic: completed configured steps; spoken quality and deployment remain unverified", flush=True)


if __name__ == "__main__":
    main()
