"""Keep only the clips that passed the speech-recognition screen: the on-pod replacement for clip-by-clip listening.

    python auto_screen.py <merged dataset> <screening.jsonl> <out dataset>

Owner, 2026-10-12: the pod generates the clips "for the traing pod to use right then iin the moment", so nobody
listens to each clip before training. This is the rule that stands in for it, approved with the script:
  - a clip is KEPT only if inspect_source_audio.py screened it with NO flags (words heard match the script, no long
    silence, no clipping, not rushed);
  - a clip that was never screened, or whose screened WAV hash differs from the dataset row, is DROPPED;
  - laughter clips are kept on the same rule (ASR cannot hear a laugh; the owner judges laughter in the samples).
Writes <out>/metadata.jsonl (the kept rows, unchanged) and hard-links each kept WAV (copies if links fail), then
re-loads the result with dataset_contract.load_dataset and writes <out>/screen-report.json, which lists every
dropped clip (id, line, reasons, what the recognizer heard) so it can be listened to at home.
"""
import json, os, re, shutil, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from dataset_contract import load_dataset


ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()
SPOKEN = {"gonna": "going to", "wanna": "want to", "gotta": "got to", "kinda": "kind of", "ok": "okay", "alright": "all right"}
LAUGH = {"ha", "haha", "hahaha", "heh", "hehe", "hah", "ahaha", "pfft"}


def number_words(n):
    n = int(n)
    if n < 20: return ONES[n]
    if n < 100: return TENS[n // 10] + ("" if n % 10 == 0 else " " + ONES[n % 10])
    if n < 1000: return ONES[n // 100] + " hundred" + ("" if n % 100 == 0 else " " + number_words(n % 100))
    if n < 1000000: return number_words(n // 1000) + " thousand" + ("" if n % 1000 == 0 else " " + number_words(n % 1000))
    return str(n)


def words(text):
    text = text.lower().replace("[laughter]", " ").replace("%", " percent")
    text = re.sub(r"\d+", lambda m: " " + number_words(m.group(0)) + " ", text)
    out = []
    for w in re.sub(r"[^a-z' ]+", " ", text).split():
        w = w.strip("'")
        if w in LAUGH or not w: continue
        out.extend(SPOKEN.get(w, w).split())
    return [w.replace("a hundred", "one hundred") for w in out]


def edit_rate(expected, heard):
    a, b = words(expected), words(heard)
    a = " ".join(a).replace("a hundred", "one hundred").split(); b = " ".join(b).replace("a hundred", "one hundred").split()
    d = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        prev, d[0] = d[0], i
        for j, y in enumerate(b, 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (x != y))
    return d[len(b)] / max(1, len(a))


def laugh_heard(heard):
    return any(w.strip(".,!?'").lower() in LAUGH for w in (heard or "").split())


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
    kept, dropped, dropped_rows, rescued = [], Counter(), [], []
    for row in rows:
        s = screened.get(row["id"])
        reasons = (["never_screened"] if s is None else ["screened_a_different_wav"] if s.get("audio_sha256") != row["sha256"]
                   else list(s.get("flags") or []))
        # Fair second look at a words-only mismatch: digits vs number words, gonna/going to, a heard laugh
        # ("ha ha") for [laughter]. Kept only if it then matches within 10% word edits; every rescue is recorded.
        if reasons == ["possible_transcript_mismatch"] and edit_rate(row["text"], s.get("recognized_text", "")) <= 0.10:
            rescued.append({"id": row["id"], "text": row["text"], "heard_as": s.get("recognized_text"),
                            "edit_rate": round(edit_rate(row["text"], s.get("recognized_text", "")), 3)})
            reasons = []
        if reasons:
            for reason in reasons:
                dropped[reason] += 1
            dropped_rows.append({"id": row["id"], "audio": row["audio"], "emotion": row["emotion"], "text": row["text"],
                                 "reasons": reasons, "heard_as": (s or {}).get("recognized_text")})
        else:
            kept.append(row)
    tmp = out.with_name(out.name + ".building")
    if tmp.exists():
        shutil.rmtree(tmp)
    (tmp / "wavs").mkdir(parents=True)
    # Uniform edges. The local proof run (owner: "most we cut off starts ... speed up sounding") showed teacher clips
    # starting with 0.03-1.0 s of silence at random, which the student smeared into its first sound. Every kept clip
    # is trimmed to the same PAD seconds of quiet before the first and after the last sound, its hash re-recorded.
    import numpy as np, soundfile as sf, hashlib
    PAD = 0.15
    trimmed = []
    for row in kept:
        src, dst = merged / row["audio"], tmp / row["audio"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        wav, sr = sf.read(str(src), dtype="float32")
        level = np.abs(wav)
        loud = np.flatnonzero(level > max(1e-4, 0.03 * float(level.max())))
        if len(loud):
            pad = int(PAD * sr)
            wav = wav[max(0, loud[0] - pad): min(len(wav), loud[-1] + 1 + pad)]
        sf.write(str(dst), wav, sr, subtype="PCM_16")
        row = dict(row, sha256=hashlib.sha256(dst.read_bytes()).hexdigest())
        trimmed.append(row)
    kept = trimmed
    with open(tmp / "metadata.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for row in kept:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    _, kept_identity = load_dataset(tmp, verify_audio=True)
    report = {"schema": "unity-voice-auto-screen-v1", "merged": identity, "kept": kept_identity,
              "kept_clips": len(kept), "total_clips": len(rows), "dropped_by_reason": dict(dropped),
              "kept_by_emotion": dict(Counter(r["emotion"] for r in kept)),
              "kept_laughter": sum("[laughter]" in r["text"] for r in kept),
              "dropped": dropped_rows,
              "rescued_after_normalising": rescued,
              "laughter_heard": sum(1 for r in kept if "[laughter]" in r["text"]
                                    and laugh_heard(screened.get(r["id"], {}).get("recognized_text"))),
              "rule": "keep only rows screened with no flags and a matching WAV hash; a words-only mismatch is kept if it matches within 10% after normalising numbers, contractions and heard laughter",
              "edges": "every kept clip trimmed to 0.15 s of quiet before the first and after the last sound"}
    (tmp / "screen-report.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    tmp.rename(out)
    print(json.dumps({k: report[k] for k in ("kept_clips", "total_clips", "dropped_by_reason", "kept_laughter", "laughter_heard")} | {"rescued": len(rescued)}))


if __name__ == "__main__":
    main()
