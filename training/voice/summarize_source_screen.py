"""Summarize exact source/ASR snapshots without loading a model or accepting a corpus.

python training/voice/summarize_source_screen.py <dataset> <screen_dir> <new_out_dir>
Add --partial to inspect an explicitly incomplete writer/screen snapshot.
Original flags, ASR text, WAVs, labels and approval records are never changed.
"""
import argparse
import collections
import ctypes
import datetime
import decimal
import hashlib
import json
import math
import os
from pathlib import Path
import re
import statistics
import sys
import unicodedata
import uuid

ROOT = Path(__file__).resolve().parents[2]
OWNER_RECEIPT = ROOT / "training/voice/receipts/pilot32-owner-listening.json"
APPROVAL_RECEIPT = ROOT / "training/voice/receipts/pilot32-corpus-acceptance.json"
EMOTIONS = {"neutral", "warm", "happy", "amused", "excited", "sad", "concerned", "frustrated", "surprised"}
ACTS = {"statement", "yes_no_question", "wh_question", "exclamation", "instruction", "reassurance", "aside"}
EVENTS = re.compile(r"\[laughter\]|\[breath\]")
HASH = re.compile(r"[0-9a-f]{64}")
SAFE_ID = re.compile(r"[A-Za-z0-9_-]{1,96}")
ONES = {word: n for n, word in enumerate(("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"))}
TENS = dict(zip(("twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"), range(20, 100, 10)))
ORDINALS = dict(zip(("first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth",
    "eleventh", "twelfth", "thirteenth", "fourteenth", "fifteenth", "sixteenth", "seventeenth", "eighteenth", "nineteenth"), range(1, 20)))
ORDINAL_TENS = dict(zip(("twentieth", "thirtieth", "fortieth", "fiftieth", "sixtieth", "seventieth", "eightieth", "ninetieth"), range(20, 100, 10)))
COMPOUNDS = {("note", "book"): "notebook", ("note", "books"): "notebooks", ("key", "board"): "keyboard",
    ("key", "boards"): "keyboards", ("door", "way"): "doorway", ("walk", "way"): "walkway",
    ("screw", "driver"): "screwdriver", ("window", "sill"): "windowsill", ("book", "shop"): "bookshop",
    ("rim", "world"): "rimworld", ("rim", "rooms"): "rimrooms"}


def digest(value):
    data = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(data.encode()).hexdigest()


def file_hash(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def read_json(path):
    data = Path(path).read_bytes()
    return json.loads(data), hashlib.sha256(data).hexdigest()


def snapshot_lines(path, partial):
    path = Path(path)
    data = path.read_bytes() if path.exists() else b""
    complete = data if not data or data.endswith(b"\n") else data[:data.rfind(b"\n") + 1]
    if complete != data and not partial:
        raise ValueError("Torn/appending JSONL needs explicit --partial: " + str(path))
    rows = []
    for number, line in enumerate(complete.decode("utf-8").splitlines(), 1):
        if not line.strip():
            raise ValueError("Blank JSONL row %d: %s" % (number, path))
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError("Expected a JSON object: " + str(path))
        rows.append(row)
    return rows, {"path": str(path), "exists": path.exists(), "snapshot_bytes": len(data),
                  "snapshot_sha256": hashlib.sha256(data).hexdigest(), "complete_prefix_bytes": len(complete),
                  "complete_prefix_sha256": hashlib.sha256(complete).hexdigest(),
                  "ignored_unpublished_tail_bytes": len(data) - len(complete), "rows": len(rows)}


def lexical(text):
    text = unicodedata.normalize("NFKC", EVENTS.sub(" ", text)).casefold().replace("’", "'")
    return " ".join(re.sub(r"[^\w']+", " ", text).split())


def below_hundred(words, start):
    if start >= len(words):
        return None
    word = words[start]
    if word in ONES:
        return ONES[word], start + 1
    if word in TENS:
        end, value = start + 1, TENS[word]
        if end < len(words) and words[end] in ONES and 1 <= ONES[words[end]] <= 9:
            value += ONES[words[end]]; end += 1
        return value, end
    return None


def under_thousand(words, start):
    if start + 1 < len(words) and words[start] in ONES and 1 <= ONES[words[start]] <= 9 and words[start + 1] == "hundred":
        value, end = ONES[words[start]] * 100, start + 2
        rest_start = end + 1 if end < len(words) and words[end] == "and" else end
        rest = below_hundred(words, rest_start)
        if rest:
            value += rest[0]; end = rest[1]
        return value, end
    return below_hundred(words, start)


def integer_words(words, start):
    part = under_thousand(words, start)
    if not part:
        return None
    value, end = part
    total, previous_scale = 0, 10 ** 12
    scales = {"thousand": 1000, "million": 1000000, "billion": 1000000000}
    while end < len(words) and words[end] in scales and scales[words[end]] < previous_scale:
        scale = scales[words[end]]
        total += value * scale; previous_scale = scale; end += 1
        rest = under_thousand(words, end)
        if not rest:
            return total, end
        value, end = rest
    return total + value, end


def decimal_text(text):
    value = format(decimal.Decimal(text), "f")
    return value.rstrip("0").rstrip(".") if "." in value else value


def comparison_tokens(text):
    """Narrow spelling/segmentation and numeric equivalents; never broad paraphrase matching."""
    text = unicodedata.normalize("NFKC", EVENTS.sub(" ", text)).casefold().replace("’", "'")
    words = re.findall(r"[-+]?\d[\d,]*(?:\.\d+)?(?:st|nd|rd|th)?|[^\W\d_]+(?:'[^\W\d_]+)*", text)
    merged, rules = [], []
    i = 0
    while i < len(words):
        pair = tuple(words[i:i + 2])
        if pair in COMPOUNDS:
            merged.append(COMPOUNDS[pair]); rules.append("compound:" + " ".join(pair)); i += 2
        else:
            merged.append(words[i]); i += 1
    words, out, i = merged, [], 0
    while i < len(words):
        word = words[i]
        match = re.fullmatch(r"([-+]?\d[\d,]*(?:\.\d+)?)(st|nd|rd|th)?", word)
        if match:
            literal = match[1]
            if "," not in literal or re.fullmatch(r"[-+]?\d{1,3}(?:,\d{3})+(?:\.\d+)?", literal):
                out.append(("ordinal:" if match[2] else "number:") + decimal_text(literal.replace(",", "")))
                rules.append("digit_number"); i += 1; continue
        if word in ORDINALS or word in ORDINAL_TENS:
            out.append("ordinal:" + str(ORDINALS.get(word, ORDINAL_TENS.get(word))))
            rules.append("ordinal_word"); i += 1; continue
        if word in TENS and i + 1 < len(words) and words[i + 1] in ORDINALS and 1 <= ORDINALS[words[i + 1]] <= 9:
            out.append("ordinal:" + str(TENS[word] + ORDINALS[words[i + 1]]))
            rules.append("ordinal_word"); i += 2; continue
        negative = word == "minus"
        parsed = integer_words(words, i + 1 if negative else i)
        if parsed:
            number, end = parsed
            value = str(number)
            if end + 1 < len(words) and words[end] == "point":
                last = end + 1
                fraction = []
                while last < len(words) and words[last] in ONES and ONES[words[last]] < 10:
                    fraction.append(str(ONES[words[last]])); last += 1
                if fraction:
                    value += "." + "".join(fraction); end = last
            out.append("number:" + decimal_text(("-" if negative else "") + value))
            rules.append("number_words"); i = end; continue
        out.append(word); i += 1
    return out, sorted(set(rules))


def word_error(left, right):
    previous = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        current = [i]
        for j, b in enumerate(right, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (a != b)))
        previous = current
    return previous[-1] / max(1, len(left))


def safe_child(directory, relative):
    if not isinstance(relative, str) or not relative or "\\" in relative or ":" in relative:
        raise ValueError("Unsafe source path")
    fragment = Path(relative)
    root = Path(directory).resolve()
    path = (root / fragment).resolve()
    if fragment.is_absolute() or ".." in fragment.parts or not path.is_relative_to(root):
        raise ValueError("Source path escapes its dataset")
    return path


def source_recipe(directory):
    saved, sha = read_json(directory / "render-recipe.json")
    plan = {key: value for key, value in saved.items() if key != "recipe_id"}
    if (saved.get("recipe_id") != digest(plan) or plan["renderer"].get("schema_version") != 3
            or plan.get("source_id") != digest(plan["renderer"])):
        raise ValueError("Source recipe is not a valid immutable schema-3 recipe")
    expected, routes = {}, {}
    for job in plan["jobs"]:
        if job["emotion"] not in EMOTIONS or job["speech_act"] not in ACTS:
            raise ValueError("Unknown planned delivery")
        route = plan["routes"][job["id"]]
        key = "a2-" + digest({"source": plan["source_id"], "job": job, "route": route})[:24]
        if key in expected:
            raise ValueError("Duplicate expected clip")
        expected[key] = {"schema": "unity-voice-dataset-v2", "id": key, "text": job["text"],
            "audio": "wavs/" + key + ".wav", "sample_rate": 24000, "voice_id": plan["renderer"]["voice_id"],
            "source_id": plan["source_id"], "emotion": job["emotion"], "intensity": job["intensity"],
            "pace": job["pace"], "speech_act": job["speech_act"]}
        routes[key] = route
    return plan, saved["recipe_id"], sha, expected, routes


def owner_records(owner_path, approval_path):
    owner, owner_sha = read_json(owner_path)
    approval, approval_sha = read_json(approval_path)
    if (owner.get("schema") != "unity-a2-pilot-owner-acceptance-v1" or owner.get("accepted_by") != "owner"
            or owner.get("decision") != "accepted" or not owner.get("owner_quote")
            or approval.get("accepted_by") != "owner" or approval.get("decision") != "accepted"):
        raise ValueError("Expected the actual recorded pilot-owner acceptance, not a generated assumption")
    relative = owner_path.resolve().relative_to(ROOT).as_posix()
    if not any(entry.get("path") == relative and entry.get("sha256") == owner_sha for entry in approval.get("evidence", [])):
        raise ValueError("Pilot corpus receipt does not bind the exact owner listening receipt")
    by_hash = collections.defaultdict(list)
    seen = set()
    for clip in owner["clips"]:
        if clip["id"] in seen or not HASH.fullmatch(clip["wav_sha256"]):
            raise ValueError("Invalid/duplicate accepted pilot record")
        seen.add(clip["id"]); by_hash[clip["wav_sha256"]].append(clip)
    if len(seen) != owner["draft_dataset"]["clips"]:
        raise ValueError("Pilot owner receipt has incomplete clip coverage")
    return owner, by_hash, {"owner_receipt": str(owner_path), "owner_receipt_sha256": owner_sha,
                           "approval_receipt": str(approval_path), "approval_receipt_sha256": approval_sha,
                           "accepted_pilot_ids": sorted(seen)}


def numeric(entry, name, low=0, high=None):
    value = entry[name]
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < low or (high is not None and value > high):
        raise ValueError("Invalid screening metric: " + name)
    return value


def metrics(values):
    values = sorted(values)
    if not values:
        return None
    def percentile(fraction):
        position = (len(values) - 1) * fraction
        lo, hi = math.floor(position), math.ceil(position)
        return values[lo] + (values[hi] - values[lo]) * (position - lo)
    return {"count": len(values), "min": values[0], "p10": percentile(.1), "median": statistics.median(values),
            "p90": percentile(.9), "max": values[-1]}


def publish(work, output):
    work, output = work.resolve(), output.resolve()
    if work.parent != output.parent or not work.name.startswith(output.name + ".summarizing-") or output.exists():
        raise ValueError("Publication target appeared/changed; preserve the work sibling")
    if os.name == "nt":
        os.rename(work, output)
    elif sys.platform.startswith("linux"):
        library = ctypes.CDLL(None, use_errno=True)
        rename = getattr(library, "renameat2", None)
        if rename is None:
            raise ValueError("Atomic no-replace publication unavailable; preserve the work sibling")
        rename.argtypes = (ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint)
        rename.restype = ctypes.c_int
        if rename(-100, os.fsencode(work), -100, os.fsencode(output), 1) != 0:
            code = ctypes.get_errno()
            raise OSError(code, os.strerror(code), str(output))
    else:
        raise ValueError("Atomic no-replace publication is not implemented on this platform; work preserved")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path); parser.add_argument("screen", type=Path); parser.add_argument("out", type=Path)
    parser.add_argument("--partial", action="store_true")
    parser.add_argument("--owner-receipt", type=Path, default=OWNER_RECEIPT)
    parser.add_argument("--approval-receipt", type=Path, default=APPROVAL_RECEIPT)
    args = parser.parse_args()
    source, screen, output = args.dataset.resolve(), args.screen.resolve(), args.out.resolve()
    if output.exists() or args.out.is_symlink() or output.is_relative_to(source) or output == screen or output.is_relative_to(screen):
        raise ValueError("Choose a new output directory outside both immutable source and original screening directories")
    plan, recipe_id, recipe_sha, expected, routes = source_recipe(source)
    inspection, inspection_sha = read_json(screen / "inspection-recipe.json")
    if (inspection.get("schema") != "unity-source-audio-screen-v1" or inspection.get("recipe_id") != recipe_id
            or inspection.get("recipe_sha256") != recipe_sha):
        raise ValueError("Screening recipe belongs to different source inputs")
    # Screen first: every complete screen row already depended on a published
    # source row. Reading source second permits an active writer to append safely.
    scans, screen_snapshot = snapshot_lines(screen / "screening.jsonl", args.partial)
    rows, metadata_snapshot = snapshot_lines(source / "metadata.jsonl", args.partial)
    available, screened = {}, {}
    for row in rows:
        key, sha = row.get("id"), row.get("sha256")
        if (key not in expected or key in available or {k: v for k, v in row.items() if k != "sha256"} != expected[key]
                or not isinstance(sha, str) or not HASH.fullmatch(sha)):
            raise ValueError("Invalid exact source metadata row")
        path = safe_child(source, row["audio"])
        if not path.is_file() or file_hash(path) != sha:
            raise ValueError("Source WAV missing/changed: " + key)
        available[key] = row
    for entry in scans:
        key = entry.get("id")
        row = available.get(key)
        if (row is None or key in screened or entry.get("audio_sha256") != row["sha256"]
                or entry.get("text") != row["text"] or entry.get("audio") != row["audio"]):
            raise ValueError("Screened clip is duplicate, unpublished or bound to different audio/text")
        if not isinstance(entry.get("recognized_text"), str) or not isinstance(entry.get("flags"), list) or any(not isinstance(flag, str) for flag in entry["flags"]):
            raise ValueError("Screen transcript/flags are malformed")
        for name in ("seconds", "rms", "peak", "word_error_rate", "leading_quiet_seconds", "trailing_quiet_seconds"):
            numeric(entry, name)
        numeric(entry, "clipped_fraction", high=1)
        if entry["seconds"] <= 0:
            raise ValueError("Screened audio has no duration")
        screened[key] = entry
    owner, known, owner_binding = owner_records(args.owner_receipt, args.approval_receipt)
    all_ids = set(expected)
    published = set(available) == all_ids
    screened_all = set(screened) == all_ids
    source_report, source_report_sha = (read_json(source / "source-build.json") if (source / "source-build.json").is_file() else (None, None))
    qa_report, qa_report_sha = (read_json(screen / "summary.json") if (screen / "summary.json").is_file() else (None, None))
    source_identity = {"schema": "unity-voice-dataset-v2", "dataset_id": digest(rows),
        "metadata_sha256": metadata_snapshot["snapshot_sha256"], "voice_id": plan["renderer"]["voice_id"],
        "source_ids": sorted({row["source_id"] for row in rows}), "clips": len(rows)}
    if source_report is not None and source_report.get("recipe_id") != recipe_id:
        raise ValueError("Final source report belongs to another recipe")
    if qa_report is not None and qa_report.get("recipe_id") != recipe_id:
        raise ValueError("Final QA report belongs to another recipe")
    source_report_matches = source_report is not None and source_report.get("dataset") == source_identity
    qa_report_matches = (qa_report is not None and qa_report.get("screening_sha256") == screen_snapshot["snapshot_sha256"]
                         and qa_report.get("source_metadata_sha256") == metadata_snapshot["snapshot_sha256"])
    if not args.partial and ((source_report is not None and not source_report_matches) or (qa_report is not None and not qa_report_matches)):
        raise ValueError("Final reports differ from observed metadata/screen snapshots")
    complete = (published and screened_all and source_report_matches and qa_report_matches
                and qa_report.get("complete_expected_inventory") is True
                and not metadata_snapshot["ignored_unpublished_tail_bytes"] and not screen_snapshot["ignored_unpublished_tail_bytes"])
    if not complete and not args.partial:
        raise ValueError("Full source/screen/receipts are not complete; use explicit --partial to publish a labeled snapshot")
    bucket_levels = collections.defaultdict(list)
    for key, entry in screened.items():
        bucket_levels[(routes[key]["teacher"], expected[key]["emotion"])].append(20 * math.log10(max(1e-12, entry["rms"])))
    records, tasks = [], {"asr_and_signal_outliers": [], "event_audibility": [], "stratified_candidates": []}
    seen_buckets = collections.Counter()
    for key, wanted in expected.items():
        row, entry = available.get(key), screened.get(key)
        event_count = wanted["text"].count("[laughter]")
        found = known.get(row["sha256"], []) if row else []
        style = {field: wanted[field] for field in ("emotion", "intensity", "pace", "speech_act")}
        exact = [clip for clip in found if clip["text"] == wanted["text"] and clip["actual_delivery"] == style
                 and owner["draft_dataset"]["voice_id"] == wanted["voice_id"]]
        receipt_status = "exact_previously_heard_binding" if exact else "hash_known_but_binding_differs" if found else "not_previously_heard"
        event_status = "no_event_requested" if not event_count else "prior_exact_owner_acceptance" if exact else "pending_audible_review"
        record = {"id": key, "intended_source_row": row or wanted, "route": routes[key],
            "inventory_status": "screened" if entry else "rendered_not_screened" if row else "not_rendered",
            "original_screening": entry, "previous_owner_acceptance": receipt_status,
            "previous_owner_ids": [clip["id"] for clip in exact], "laughter_markers": event_count,
            "event_audibility": event_status, "supplemental_flags": [], "training_authorized": False}
        task = ({"id": key, "audio": str(safe_child(source, wanted["audio"])), "wav_sha256": row["sha256"],
                 "text": wanted["text"], "intended_delivery": style, "route": routes[key],
                 "original_flags": entry["flags"] if entry else [], "supplemental_flags": record["supplemental_flags"],
                 "previous_owner_acceptance": receipt_status, "event_audibility": event_status,
                 "screening_status": record["inventory_status"]} if row else None)
        if event_count and row and not exact:
            tasks["event_audibility"].append(task)
        if entry:
            left, left_rules = comparison_tokens(wanted["text"])
            right, right_rules = comparison_tokens(entry["recognized_text"])
            equality = lexical(wanted["text"]) == lexical(entry["recognized_text"])
            equivalent = left == right
            record["transcript_comparison"] = {"classification": "exact_lexical_match" if equality else "narrow_segmentation_or_number_equivalent" if equivalent else "unresolved_asr_disagreement",
                "expected_tokens": left, "recognized_tokens": right, "applied_rules": sorted(set(left_rules + right_rules)),
                "comparison_word_error_rate": word_error(left, right), "original_flags_preserved": True}
            if not equivalent:
                record["supplemental_flags"].append("unresolved_asr_disagreement")
            if found and not exact:
                record["supplemental_flags"].append("known_audio_binding_differs")
            seconds = entry["seconds"]
            quiet_fraction = min(1.0, (entry["leading_quiet_seconds"] + entry["trailing_quiet_seconds"]) / seconds)
            if seconds >= 2 and quiet_fraction > .5:
                record["supplemental_flags"].append("large_boundary_quiet_fraction")
            levels = bucket_levels[(routes[key]["teacher"], wanted["emotion"])]
            level = 20 * math.log10(max(1e-12, entry["rms"]))
            if len(levels) >= 8 and abs(level - statistics.median(levels)) > 12:
                record["supplemental_flags"].append("level_outlier_within_teacher_state")
            original_actionable = [flag for flag in entry["flags"] if flag != "possible_transcript_mismatch" or not equivalent]
            task["comparison_word_error_rate"] = record["transcript_comparison"]["comparison_word_error_rate"]
            if original_actionable or record["supplemental_flags"]:
                task["priority"] = (0 if "source_format_or_level_outlier" in original_actionable else
                                    1 if original_actionable or task["comparison_word_error_rate"] > .25 else 2)
                tasks["asr_and_signal_outliers"].append(task)
            bucket = (routes[key]["teacher"], wanted["emotion"], wanted["speech_act"])
            if not exact and seen_buckets[bucket] < 2:
                tasks["stratified_candidates"].append(task); seen_buckets[bucket] += 1
        records.append(record)
    tasks["asr_and_signal_outliers"].sort(key=lambda task: (task["priority"], -task["comparison_word_error_rate"], task["id"]))
    flag_counts = collections.Counter(flag for entry in scans for flag in entry["flags"])
    comparison_counts = collections.Counter(record["transcript_comparison"]["classification"] for record in records if "transcript_comparison" in record)
    shortlist_ids = list(dict.fromkeys(task["id"] for group in tasks.values() for task in group))
    summary = {"schema": "unity-source-screen-curation-summary-v1", "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "complete_inventory_screen_summary" if complete else "explicit_partial_snapshot", "partial_requested": args.partial,
        "source_recipe_id": recipe_id, "source_recipe_sha256": recipe_sha, "inspection_recipe": inspection,
        "inspection_recipe_sha256": inspection_sha, "inspection_code_sha256": inspection["script_sha256"],
        "summary_code_sha256": file_hash(Path(__file__)), "qa_policy_sha256": file_hash(Path(__file__).with_name("SOURCE_QA_POLICY.md")),
        "source_metadata_snapshot": metadata_snapshot, "screening_snapshot": screen_snapshot,
        "source_build_sha256": source_report_sha, "original_qa_summary_sha256": qa_report_sha,
        "source_build_matches_snapshot": source_report_matches, "original_qa_summary_matches_snapshot": qa_report_matches,
        "source_scope": plan["scope"], "full1378_preparation_inventory": complete and len(expected) == 1378 and plan["scope"] == "full-draft",
        "owner_receipts": owner_binding,
        "inventory": {"expected": len(expected), "target1378": len(expected) == 1378, "rendered": len(available), "screened": len(screened),
            "not_rendered_ids": sorted(all_ids - set(available)), "not_screened_ids": sorted(all_ids - set(screened)),
            "complete_rendered_inventory": published, "complete_screened_inventory": screened_all},
        "source_dataset_identity": source_identity if published else None, "original_flag_counts": dict(flag_counts),
        "transcript_comparison_counts": dict(comparison_counts),
        "previous_owner_exact_match_ids": [record["id"] for record in records if record["previous_owner_acceptance"] == "exact_previously_heard_binding"],
        "all_laughter_ids": [record["id"] for record in records if record["laughter_markers"]],
        "laughter_still_pending_ids": [record["id"] for record in records if record["event_audibility"] == "pending_audible_review"],
        "shortlist_ids": shortlist_ids, "measured_screened_hours": sum(entry["seconds"] for entry in scans) / 3600,
        "screen_metrics": {name: metrics([entry[name] for entry in scans]) for name in
            ("seconds", "rms", "peak", "clipped_fraction", "leading_quiet_seconds", "trailing_quiet_seconds", "word_error_rate")},
        "acceptance": "not_granted; technical comparison and listening tasks only",
        "full_corpus_human_listening_inferred": False, "training_authorized": False, "pod_rental_authorized": False}
    if file_hash(source / "render-recipe.json") != recipe_sha:
        raise ValueError("Source recipe changed during summary")
    output.parent.mkdir(parents=True, exist_ok=True)
    work = output.with_name(output.name + ".summarizing-" + uuid.uuid4().hex)
    work.mkdir(exist_ok=False)
    (work / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    (work / "clips.jsonl").write_text("".join(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n" for record in records), encoding="utf-8", newline="\n")
    (work / "listening-tasks.json").write_text(json.dumps({"schema": "unity-source-listening-shortlist-v1", "groups": tasks,
        "unique_ids": shortlist_ids, "note": "Candidate listening tasks, not audio generation or listening acceptance."}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    if output.exists():
        raise ValueError("Output appeared concurrently; preserve the summary work directory")
    publish(work, output)
    print(json.dumps({"status": summary["status"], "expected": len(expected), "rendered": len(available), "screened": len(screened),
        "comparisons": dict(comparison_counts), "exact_prior_owner_matches": len(summary["previous_owner_exact_match_ids"]),
        "listening_shortlist": len(shortlist_ids), "out": str(output)}, indent=2))


if __name__ == "__main__":
    main()
