"""Keep only the clips that passed the speech-recognition screen: the on-pod replacement for clip-by-clip listening.

    python auto_screen.py <merged dataset> <screening.jsonl> <out dataset>

Owner, 2026-10-12: the pod generates the clips "for the traing pod to use right then iin the moment", so nobody
listens to each clip before training. This is the rule that stands in for it, approved with the script:
  - a clip is KEPT only if inspect_source_audio.py screened it with NO flags (words heard match the script, no long
    silence, no clipping, not rushed);
  - a clip that was never screened, or whose screened WAV hash differs from the dataset row, is DROPPED;
  - laughter clips are kept on the same rule (ASR cannot hear a laugh; the owner judges laughter in the samples).
Writes <out>/metadata.jsonl (the kept rows, unchanged) and hard-links each kept WAV (copies if links fail), then
re-loads the result with dataset_contract.load_dataset and writes <out>/screen-report.json.
"""
import json, os, shutil, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from dataset_contract import load_dataset


def main():
    merged, screening, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    if out.exists():
        raise SystemExit("output exists; preserve it: " + str(out))
    rows, identity = load_dataset(merged, verify_audio=True)
    screened = {}
    for line in screening.read_text(encoding="utf-8").splitlines():
        if line.strip():
            s = json.loads(line)
            screened[s["id"]] = s
    kept, dropped = [], Counter()
    for row in rows:
        s = screened.get(row["id"])
        if s is None:
            dropped["never_screened"] += 1
        elif s.get("audio_sha256") != row["sha256"]:
            dropped["screened_a_different_wav"] += 1
        elif s.get("flags"):
            for flag in s["flags"]:
                dropped[flag] += 1
        else:
            kept.append(row)
    tmp = out.with_name(out.name + ".building")
    if tmp.exists():
        shutil.rmtree(tmp)
    (tmp / "wavs").mkdir(parents=True)
    for row in kept:
        src, dst = merged / row["audio"], tmp / row["audio"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.link(src, dst)
        except OSError:
            shutil.copy2(src, dst)
    with open(tmp / "metadata.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for row in kept:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    _, kept_identity = load_dataset(tmp, verify_audio=True)
    report = {"schema": "unity-voice-auto-screen-v1", "merged": identity, "kept": kept_identity,
              "kept_clips": len(kept), "total_clips": len(rows), "dropped_by_reason": dict(dropped),
              "kept_by_emotion": dict(Counter(r["emotion"] for r in kept)),
              "kept_laughter": sum("[laughter]" in r["text"] for r in kept),
              "rule": "keep only rows screened with no flags and a matching WAV hash"}
    (tmp / "screen-report.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    tmp.rename(out)
    print(json.dumps({k: report[k] for k in ("kept_clips", "total_clips", "dropped_by_reason", "kept_laughter")}))


if __name__ == "__main__":
    main()
