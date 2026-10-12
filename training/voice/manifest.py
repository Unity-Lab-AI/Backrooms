"""Hash every input of the voice training run into VOICE_MANIFEST.json; the pod refuses any other inputs.

    python training/voice/manifest.py          # write the manifest and print its digest
    python training/voice/manifest.py --check  # verify the files against the manifest, print the digest

The immutable digest is what the owner approves at launch (VOICE_DIGEST on the pod).
Gate status and priced/final approvals are intentionally excluded: those receipts
approve this digest and cannot also be its inputs without creating a circular hash.
"""
import hashlib, json, os, sys
from quality_gate import MUTABLE_RECEIPT_CHECKS, receipt_path
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
FILES = ["training/voice/" + f for f in ("make_dataset.py", "source_workers.py", "build_corpus.py", "SPEECH_CORPUS.jsonl", "curate_dataset.py",
         "build_event_corpus.py", "SPEECH_EVENT_CORPUS.jsonl", "SOURCE_DELIVERY_POLICY.json",
         "dataset_contract.py", "prep.py", "model.py", "train_acoustic.py", "vocoder.py",
         "feature_arrays.py", "student_state.py", "speech_turns.py", "inspect_source_audio.py",
         "LISTENING_EVAL_TEXT.jsonl", "EVALUATION_PLAN.md", "RUNTIME_INTEGRATION_PLAN.md",
         "summarize_source_screen.py", "recheck_source_words.py", "SOURCE_QA_POLICY.md",
         "finish_source_preparation.py", "run_expanded_preparation.py",
         "make_dataset_optimized.py", "source_workers_optimized.py", "OPTIMIZED_SOURCE_CONTRACT.md",
         "SOURCE_THROUGHPUT_PLAN.md", "EXPANDED_CORPUS_PLAN.md", "build_expanded_corpus.py",
         "SPEECH_CORPUS_EXPANDED.jsonl", "SPEECH_EVENT_CORPUS_EXPANDED.jsonl",
         "merge_source_datasets.py", "merge_source_qa.py", "MERGED_SOURCE_CONTRACT.md",
         "train_vocoder.py", "infer.py", "quality_gate.py", "speech_text.py", "cosy_audition.py",
         "SELECTED_VOICE.json", "REFERENCE_PROFILES.json",
         "receipts/pilot32-owner-listening.json", "receipts/pilot32-corpus-acceptance.json",
         "receipts/local-environment-build.json", "receipts/environment-2026-10-11-v2/observation.json",
         "receipts/environment-2026-10-11-v2/package-lock.json", "receipts/environment-2026-10-11-v2/runtime-assets.json",
         "receipts/environment-2026-10-11-v2/os-packages.tsv",
         "audition.py", "AUDITION_BRIEF_LOW_REGISTER.json", "variations.py", "A2_VARIATIONS.json", "happy_audition.py",
         "manifest.py", "pod/bootstrap_voice.sh", "pod/run_voice.sh", "pod/atomic_publish.py",
         "pod/preflight_voice.py", "pod/prepare_launch.py", "pod/accept_delivery.py", "pod/publish_voice.py",
         "pod/render_eval.py", "pod/upload_dataset.ps1", "pod/ENVIRONMENT_SPEC.json",
         "pod/Dockerfile", "pod/DEBIAN_SNAPSHOT.json", "pod/create_build_context.py",
         "pod/export_environment.py", "pod/start_no_training.sh",
         "pod/environment.lock.json", "pod/resolve_environment.py", "pod/LAUNCH_CONFIG.template.json")]
PATH = os.path.join(HERE, "VOICE_MANIFEST.json")
profiles = json.load(open(os.path.join(HERE, "REFERENCE_PROFILES.json"), encoding="utf-8"))
for profile in profiles["profiles"].values():
    FILES.extend((profile["audio"], profile["listening_audio"]))
policy = json.load(open(os.path.join(HERE, "SOURCE_DELIVERY_POLICY.json"), encoding="utf-8"))
for example in policy["approved_examples"]:
    FILES.extend((example["audio"], example["listening_audio"]))
# Source/preparation receipts are inputs too. Their supporting listening artifacts may remain local;
# the receipt records their identities rather than shipping an audition library to the pod.
# Mutable gate state, owner paid authorization and final deployment receipts are
# validated separately by quality_gate.py and never alter the approved source digest.
gate = json.load(open(os.path.join(HERE, "VOICE_QUALITY_GATE.json"), encoding="utf-8"))
for check_id, check in gate["checks"].items():
    if check_id not in MUTABLE_RECEIPT_CHECKS and check.get("receipt"):
        FILES.append(os.path.relpath(receipt_path(check["receipt"]), ROOT).replace(os.sep, "/"))
# RunPod-template launch path and on-pod generation (2026-10-12).
FILES.extend("training/voice/pod/" + f for f in ("start_template.sh", "generate_on_pod.sh", "auto_screen.py",
             "requirements-template.txt", "requirements-teacher-qwen.txt", "requirements-teacher-cosy.txt",
             "constraints-teacher.txt", "upload_volume_s3.ps1", "pull_results_s3.ps1"))
# Unity's stream-voice script (5,000 lines, 2026-10-12), recorded on the pod by generate_on_pod.sh.
FILES.extend(("training/voice/STREAM_CORPUS.jsonl", "training/voice/STREAM_EVENT_CORPUS.jsonl"))
# The owner's later delivery choice (A/B, 2026-10-12) and every clip it was heard on.
policy = json.load(open(os.path.join(HERE, "SOURCE_DELIVERY_POLICY.json"), encoding="utf-8"))
if policy.get("owner_delivery_selection"):
    FILES.append(policy["owner_delivery_selection"]["receipt"])
    selection = json.load(open(os.path.join(ROOT, policy["owner_delivery_selection"]["receipt"]), encoding="utf-8"))
    FILES.extend(entry["path"] for entry in selection["evidence"])
FILES = sorted(set(FILES))


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def digest(files):
    return hashlib.sha256("".join("%s  %s\n" % (files[k], k) for k in sorted(files)).encode()).hexdigest()


if "--check" in sys.argv:
    m = json.load(open(PATH))
    if set(m["files"]) != set(FILES):
        print("MISMATCH:manifest input set differs; regenerate after reviewing the gate and receipts"); sys.exit(1)
    bad = [rel for rel, want in m["files"].items() if sha(rel) != want]
    if bad:
        print("MISMATCH:" + ",".join(bad)); sys.exit(1)
    print(digest(m["files"]))
else:
    files = {rel: sha(rel) for rel in FILES}
    with open(PATH, "w", newline="\n") as f:                                # LF, as git stores it
        json.dump({"files": files, "digest": digest(files)}, f, indent=1)
    print(digest(files))
