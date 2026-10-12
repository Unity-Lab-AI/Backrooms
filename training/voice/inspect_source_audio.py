"""Offline source-audio inventory and transcript screening; never human acceptance.

Only existing local faster-whisper weights are allowed. CPU int8 transcription
flags possible wrong words for listening; ASR disagreement is not proof of a bad
recording. --watch may inspect complete published rows while the source builder
continues. It never edits WAVs, labels, review decisions or launch permissions.
"""
import argparse
import collections
import importlib.metadata
import json
import os
from pathlib import Path
import time

from dataset_contract import canonical_hash, file_hash, local_path, normalize_transcript
from make_dataset import expected_rows, load_recipe, read_metadata, write_new_json


def word_error(expected, actual):
    left, right = expected.split(), actual.split()
    previous = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        current = [i]
        for j, b in enumerate(right, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (a != b)))
        previous = current
    return previous[-1] / max(1, len(left))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--max-seconds", type=int, default=28800)
    parser.add_argument("--watch", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.threads <= 8:
        raise ValueError("CPU thread limit must be 1..8")
    if not 60 <= args.max_seconds <= 86400:
        raise ValueError("Screening walltime must be 60..86400 seconds")
    args.dataset, args.out, args.model_dir = args.dataset.resolve(), args.out.resolve(), args.model_dir.resolve()
    if args.out == args.dataset or args.out.is_relative_to(args.dataset):
        raise ValueError("QA output must be outside the immutable source dataset")
    required = [args.model_dir / name for name in ("config.json", "model.bin", "tokenizer.json", "vocabulary.txt")]
    if not all(p.is_file() for p in required):
        raise ValueError("Supply complete existing local ASR files; no download is allowed")
    plan, recipe_id = load_recipe(args.dataset / "render-recipe.json")
    expected = expected_rows(plan)
    source_recipe_sha256 = file_hash(args.dataset / "render-recipe.json")
    config = {"schema": "unity-source-audio-screen-v1", "recipe_id": recipe_id,
              "recipe_sha256": source_recipe_sha256, "script_sha256": file_hash(Path(__file__)),
              "asr_files_sha256": {p.name: file_hash(p) for p in required},
              "versions": {p: importlib.metadata.version(p) for p in ("faster-whisper", "ctranslate2", "numpy", "soundfile")},
              "asr": {"device": "cpu", "compute_type": "int8", "cpu_threads": args.threads,
                      "num_workers": 1, "language": "en", "beam_size": 3,
                      "condition_on_previous_text": False, "vad_filter": False},
              "scope": "format inventory plus fallible ASR screening; no voice/emotion/human acceptance"}
    args.out.mkdir(parents=True, exist_ok=True)
    config_path = args.out / "inspection-recipe.json"
    if config_path.exists():
        if json.loads(config_path.read_text(encoding="utf-8")) != config:
            raise ValueError("QA folder belongs to different source/ASR/code inputs")
    else:
        if any(args.out.iterdir()):
            raise ValueError("Preserve nonempty unbound QA folder")
        write_new_json(config_path, config)
    result_path = args.out / "screening.jsonl"
    done = {}
    if result_path.exists():
        raw = result_path.read_text(encoding="utf-8")
        if raw and not raw.endswith("\n"):
            raise ValueError("Preserve torn QA output for explicit recovery")
        for line in raw.splitlines():
            entry = json.loads(line)
            if entry["id"] in done or entry["id"] not in expected:
                raise ValueError("Invalid duplicate/unexpected QA entry")
            done[entry["id"]] = entry
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    import numpy as np
    import soundfile as sf
    from faster_whisper import WhisperModel
    model = WhisperModel(str(args.model_dir), device="cpu", compute_type="int8",
                         cpu_threads=args.threads, num_workers=1, local_files_only=True)
    started = time.monotonic()
    while True:
        if time.monotonic() - started > args.max_seconds:
            raise ValueError("Source screening deadline reached; preserve partial results")
        if file_hash(args.dataset / "render-recipe.json") != source_recipe_sha256:
            raise ValueError("Source recipe changed during screening")
        try:
            available = read_metadata(args.dataset, expected)
        except ValueError as error:
            if args.watch and "Torn/non-newline-complete" in str(error):
                time.sleep(.2)
                continue
            raise
        for clip_id, row in available.items():
            if clip_id in done:
                if done[clip_id]["audio_sha256"] != row["sha256"] or done[clip_id]["text"] != row["text"]:
                    raise ValueError("Previously screened audio/text changed")
                continue
            path = local_path(args.dataset, row["audio"])
            audio, rate = sf.read(path, dtype="float32")
            information = sf.info(path)
            if rate != 24000 or audio.ndim != 1 or not np.isfinite(audio).all() or information.subtype != "PCM_16":
                raise ValueError("Invalid source WAV format: " + clip_id)
            seconds = len(audio) / rate
            quiet = np.flatnonzero(np.abs(audio) > .001)
            leading = quiet[0] / rate if len(quiet) else seconds
            trailing = (len(audio) - quiet[-1] - 1) / rate if len(quiet) else seconds
            segments, info = model.transcribe(str(path), language="en", beam_size=3,
                condition_on_previous_text=False, vad_filter=False, word_timestamps=False)
            segments = list(segments)
            transcript = " ".join(s.text.strip() for s in segments).strip()
            target, heard = normalize_transcript(row["text"]), normalize_transcript(transcript)
            wer = word_error(target, heard)
            rms = float(np.sqrt(np.mean(audio.astype(np.float64) ** 2)))
            clipping = float(np.mean(np.abs(audio) >= .999))
            flags = []
            if not .25 <= seconds <= 30 or rms < 1e-5 or clipping > .001:
                flags.append("source_format_or_level_outlier")
            if not heard or wer > .25:
                flags.append("possible_transcript_mismatch")
            if leading > 1.5 or trailing > 1.5:
                flags.append("long_boundary_quiet")
            if len(target.split()) / max(.1, seconds - leading - trailing) > 6:
                flags.append("possibly_rushed")
            entry = {"id": clip_id, "audio": row["audio"], "audio_sha256": row["sha256"],
                     "text": row["text"], "recognized_text": transcript, "normalized_expected": target,
                     "normalized_recognized": heard, "word_error_rate": wer,
                     "seconds": seconds, "rms": rms, "peak": float(np.max(np.abs(audio))),
                     "clipped_fraction": clipping, "leading_quiet_seconds": leading,
                     "trailing_quiet_seconds": trailing, "flags": flags,
                     "human_listening_acceptance": "not_inferred", "event_audibility": "not_inferred"}
            if file_hash(path) != row["sha256"]:
                raise ValueError("Source changed during analysis")
            with result_path.open("a", encoding="utf-8", newline="\n") as stream:
                stream.write(json.dumps(entry, ensure_ascii=False, allow_nan=False) + "\n")
                stream.flush(); os.fsync(stream.fileno())
            done[clip_id] = entry
            if len(done) % 25 == 0 or flags:
                print("SOURCE SCREEN %d/%d %s %s" % (len(done), len(expected), clip_id, ",".join(flags) or "no heuristic flags"), flush=True)
        complete = set(done) == set(expected) and (args.dataset / "source-build.json").is_file()
        if complete or not args.watch:
            summary = {"schema": "unity-source-audio-screen-summary-v1", "recipe_id": recipe_id,
                       "complete_expected_inventory": complete, "screened": len(done), "expected": len(expected),
                       "seconds": sum(x["seconds"] for x in done.values()),
                       "flag_counts": dict(collections.Counter(flag for x in done.values() for flag in x["flags"])),
                       "flagged_ids": [x["id"] for x in done.values() if x["flags"]],
                       "screening_sha256": file_hash(result_path), "source_metadata_sha256": file_hash(args.dataset / "metadata.jsonl"),
                       "acceptance": "not_granted; ASR flags require review, and no flags do not prove voice or emotion",
                       "training_authorized": False, "pod_rental_authorized": False}
            write_new_json(args.out / "summary.json", summary)
            print(json.dumps(summary, ensure_ascii=False), flush=True)
            return
        if any(args.dataset.glob("source-*-timeout.json")):
            raise ValueError("Source renderer timed out; preserve partial screening")
        time.sleep(15)


if __name__ == "__main__":
    main()
