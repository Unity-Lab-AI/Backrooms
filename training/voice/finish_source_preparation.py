"""Complete a frozen full source candidate locally, without training or cloud work.

python training/voice/finish_source_preparation.py DATASET SCREEN NEW_OUT \
    --source-digest EXACT_SHA256 --max-seconds 28800

Waits for existing writers; it neither launches nor stops those processes. Every
invoked preparation CLI uses this interpreter, argument lists and a bounded owned
child. New output/logs are preserved on failure. No approvals or gate are changed.
"""
import argparse
import collections
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import signal
import subprocess
import sys
import tarfile
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
VOICE = ROOT / "training/voice"
LOCAL = ROOT / ".local"
HASH = re.compile(r"[0-9a-f]{64}")
INVOKED = ("summarize_source_screen.py", "recheck_source_words.py", "curate_dataset.py", "prep.py",
           "pod/preflight_voice.py", "pod/prepare_launch.py")
REQUIRED = INVOKED + ("finish_source_preparation.py", "SOURCE_QA_POLICY.md", "dataset_contract.py",
                      "speech_text.py", "feature_arrays.py", "pod/LAUNCH_CONFIG.template.json")


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
        separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def file_hash(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            result.update(block)
    return result.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_new(path, value):
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
        stream.flush(); os.fsync(stream.fileno())


def artifact(path):
    path = Path(path)
    return {"path": str(path.resolve()), "sha256": file_hash(path), "bytes": path.stat().st_size}


def child_path(root, relative):
    if not isinstance(relative, str) or not relative or "\\" in relative or ":" in relative:
        raise ValueError("Invalid relative artifact path")
    fragment = Path(relative)
    path = (root / fragment).resolve()
    if fragment.is_absolute() or ".." in fragment.parts or not path.is_relative_to(root.resolve()):
        raise ValueError("Artifact escapes its declared directory")
    return path


def rows_at(path, partial=False):
    raw = Path(path).read_bytes() if Path(path).is_file() else b""
    if raw and not raw.endswith(b"\n"):
        if not partial:
            raise ValueError("Unpublished JSONL tail: " + str(path))
        raw = raw[:raw.rfind(b"\n") + 1]
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines()]
    if any(not isinstance(row, dict) for row in rows):
        raise ValueError("Expected JSONL objects: " + str(path))
    return rows


def index_rows(rows):
    indexed = {}
    for row in rows:
        key = row.get("id")
        if not isinstance(key, str) or key in indexed:
            raise ValueError("Invalid/duplicate artifact ID")
        indexed[key] = row
    return indexed


class Preparation:
    def __init__(self, args):
        self.dataset, self.screen, self.output = [path.resolve() for path in (args.dataset, args.screen, args.out)]
        self.expected_digest = args.source_digest
        self.started = time.monotonic()
        self.deadline = self.started + args.max_seconds
        self.seconds = args.max_seconds
        self.stages, self.artifacts = [], {}
        self.identity = None
        self.feature_identity = None
        self.active = None
        self.cleanup = []
        self.manifest_sha = file_hash(VOICE / "VOICE_MANIFEST.json")
        self.gate_sha = file_hash(VOICE / "VOICE_QUALITY_GATE.json")
        self.recipe_sha = file_hash(self.dataset / "render-recipe.json")
        self.recipe = read_json(self.dataset / "render-recipe.json")
        body = {key: value for key, value in self.recipe.items() if key != "recipe_id"}
        if (self.recipe.get("recipe_id") != canonical(body) or self.recipe.get("scope") != "full-draft"
                or self.recipe["renderer"].get("schema_version") != 3
                or self.recipe.get("source_id") != canonical(self.recipe["renderer"])):
            raise ValueError("An exact frozen schema-3 full-draft source recipe is required")
        self.expected = {}
        for job in self.recipe["jobs"]:
            key = "a2-" + canonical({"source": self.recipe["source_id"], "job": job,
                                      "route": self.recipe["routes"][job["id"]]})[:24]
            if key in self.expected:
                raise ValueError("Duplicate planned source clip")
            self.expected[key] = {"schema": "unity-voice-dataset-v2", "id": key, "text": job["text"],
                "audio": "wavs/" + key + ".wav", "sample_rate": 24000,
                "voice_id": self.recipe["renderer"]["voice_id"], "source_id": self.recipe["source_id"],
                **{field: job[field] for field in ("emotion", "intensity", "pace", "speech_act")}}
        if not self.expected:
            raise ValueError("Empty full source recipe")

    def remaining(self):
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("Full candidate preparation deadline reached; preserve all outputs")
        return remaining

    def guard(self):
        self.remaining()
        if file_hash(VOICE / "VOICE_MANIFEST.json") != self.manifest_sha:
            raise ValueError("Frozen source manifest changed during preparation")
        manifest = read_json(VOICE / "VOICE_MANIFEST.json")
        files = manifest["files"]
        required = {"training/voice/" + name for name in REQUIRED}
        if not required.issubset(files):
            raise ValueError("Freeze every driver/helper/template in manifest first: " + ",".join(sorted(required - set(files))))
        digest = hashlib.sha256("".join("%s  %s\n" % (files[name], name) for name in sorted(files)).encode()).hexdigest()
        if digest != manifest.get("digest") or digest != self.expected_digest:
            raise ValueError("Explicit source digest differs from frozen manifest")
        for relative, wanted in files.items():
            path = child_path(ROOT, relative)
            if not isinstance(wanted, str) or not HASH.fullmatch(wanted) or not path.is_file() or file_hash(path) != wanted:
                raise ValueError("Frozen source file changed: " + relative)
        if file_hash(self.dataset / "render-recipe.json") != self.recipe_sha:
            raise ValueError("Source recipe changed during preparation")
        renderer = self.recipe["renderer"]
        bindings = {"builder_sha256": "make_dataset.py", "worker_sha256": "source_workers.py",
            "contract_sha256": "dataset_contract.py", "speech_text_sha256": "speech_text.py",
            "selected_config_sha256": "SELECTED_VOICE.json", "reference_profiles_sha256": "REFERENCE_PROFILES.json",
            "source_delivery_policy_sha256": "SOURCE_DELIVERY_POLICY.json", "approval_receipt_sha256": "receipts/source-auditions.json"}
        if any(renderer.get(field) != file_hash(VOICE / relative) for field, relative in bindings.items()):
            raise ValueError("Completed source recipe and current teacher-input source bindings differ")
        if (self.recipe["corpora_sha256"] != {"speech": file_hash(VOICE / "SPEECH_CORPUS.jsonl"),
                                               "events": file_hash(VOICE / "SPEECH_EVENT_CORPUS.jsonl")}):
            raise ValueError("Frozen source corpora differ from the completed recipe")
        if file_hash(VOICE / "VOICE_QUALITY_GATE.json") != self.gate_sha:
            raise ValueError("Quality gate changed during this locked preparation")
        gate = read_json(VOICE / "VOICE_QUALITY_GATE.json")
        if gate.get("training_allowed") is not False or gate.get("deployment_allowed") is not False:
            raise ValueError("This driver requires the actual no-training/no-deployment gate")
        if gate["checks"]["owner_training_authorization"].get("accepted") is not False:
            raise ValueError("This preparation invocation must remain unpriced and unapproved")
        if gate["checks"]["corpus_acceptance"].get("accepted") is not False:
            raise ValueError("This driver prepares the still-unaccepted full candidate only")
        if self.identity is not None:
            if file_hash(self.dataset / "metadata.jsonl") != self.identity["metadata_sha256"]:
                raise ValueError("Completed source metadata changed during preparation")
            for key, row in self.source_rows.items():
                if file_hash(child_path(self.dataset, row["audio"])) != row["sha256"]:
                    raise ValueError("Completed source WAV changed during preparation: " + key)
            for name in ("source_build", "base_screen_summary", "base_screening", "base_inspection_recipe"):
                saved = self.artifacts[name]
                if file_hash(saved["path"]) != saved["sha256"]:
                    raise ValueError("Completed source/QA receipt changed during preparation: " + name)
        self.remaining()

    def complete_writers(self):
        while True:
            self.guard()
            timeouts = list(self.dataset.glob("source-*-timeout.json"))
            if timeouts:
                raise ValueError("Source worker timeout receipts need explicit recovery: " + ",".join(path.name for path in timeouts))
            rendered = rows_at(self.dataset / "metadata.jsonl", partial=True)
            screened = rows_at(self.screen / "screening.jsonl", partial=True)
            print(json.dumps({"stage": "waiting_for_existing_writers", "rendered": len(rendered),
                "screened": len(screened), "expected": len(self.expected),
                "remaining_seconds": math.floor(self.remaining())}), flush=True)
            source_path, screen_path = self.dataset / "source-build.json", self.screen / "summary.json"
            if source_path.is_file() and screen_path.is_file():
                source, screen = read_json(source_path), read_json(screen_path)
                if (source.get("schema_version") != 3 or source.get("recipe_id") != self.recipe["recipe_id"]
                        or source.get("scope") != "full-draft"
                        or source.get("completion") not in ("rendered_complete", "recovered_exact_complete_metadata")):
                    raise ValueError("Final source receipt is invalid or belongs to another recipe")
                if (screen.get("schema") != "unity-source-audio-screen-summary-v1"
                        or screen.get("recipe_id") != self.recipe["recipe_id"]):
                    raise ValueError("Final screen receipt belongs to another recipe")
                if screen.get("complete_expected_inventory") is not True:
                    raise ValueError("Screen writer ended with an explicitly partial report; no false completion")
                rows = rows_at(self.dataset / "metadata.jsonl")
                row_map = index_rows(rows)
                scans = index_rows(rows_at(self.screen / "screening.jsonl"))
                if set(row_map) != set(self.expected) or set(scans) != set(self.expected):
                    raise ValueError("Final receipts lack complete exact rendered/screened IDs")
                for key, row in row_map.items():
                    if ({field: value for field, value in row.items() if field != "sha256"} != self.expected[key]
                            or not isinstance(row.get("sha256"), str) or not HASH.fullmatch(row["sha256"])
                            or scans[key].get("audio_sha256") != row["sha256"] or scans[key].get("text") != row["text"]):
                        raise ValueError("Final source/screen row binding differs: " + key)
                identity = {"schema": "unity-voice-dataset-v2", "dataset_id": canonical(rows),
                    "metadata_sha256": file_hash(self.dataset / "metadata.jsonl"), "voice_id": rows[0]["voice_id"],
                    "source_ids": sorted({row["source_id"] for row in rows}), "clips": len(rows)}
                if (source.get("dataset") != identity or screen.get("source_metadata_sha256") != identity["metadata_sha256"]
                        or screen.get("screening_sha256") != file_hash(self.screen / "screening.jsonl")
                        or screen.get("screened") != len(rows) or screen.get("expected") != len(rows)):
                    raise ValueError("Final source/screen receipt hashes or counts differ")
                runtime = source.get("runtime_sha256", {})
                wanted_runtime = {"source-" + teacher + "-runtime.json" for teacher in self.recipe["renderer"]["teachers"]}
                if set(runtime) != wanted_runtime:
                    raise ValueError("Source worker provenance coverage differs")
                for name, sha in runtime.items():
                    path = child_path(self.dataset, name)
                    receipt = read_json(path)
                    if file_hash(path) != sha or receipt.get("recipe_id") != self.recipe["recipe_id"]:
                        raise ValueError("Source worker receipt hash/recipe differs")
                    self.artifacts[name] = artifact(path)
                inspection = read_json(self.screen / "inspection-recipe.json")
                if (inspection.get("recipe_id") != self.recipe["recipe_id"] or inspection.get("recipe_sha256") != self.recipe_sha
                        or inspection.get("script_sha256") != file_hash(VOICE / "inspect_source_audio.py")):
                    raise ValueError("Completed ASR inspection input/code hash differs")
                self.identity = identity
                self.source_rows = row_map
                for name, path in (("render_recipe", self.dataset / "render-recipe.json"), ("source_build", source_path),
                        ("source_metadata", self.dataset / "metadata.jsonl"), ("base_screen_summary", screen_path),
                        ("base_screening", self.screen / "screening.jsonl"), ("base_inspection_recipe", self.screen / "inspection-recipe.json")):
                    self.artifacts[name] = artifact(path)
                return
            time.sleep(min(30, self.remaining()))

    def stop_owned(self, process):
        """Only this invocation's tracked live child/tree; never either source writer."""
        if process.poll() is not None:
            return
        record = {"pid": process.pid, "scope": "owned preparation child only"}
        try:
            if os.name == "nt":
                result = subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10, check=False,
                    creationflags=subprocess.CREATE_NO_WINDOW)
                record.update(method="taskkill owned PID tree", returncode=result.returncode,
                    output=(result.stdout + result.stderr).decode(errors="replace")[-4000:])
                if result.returncode != 0 and process.poll() is None:
                    process.kill(); record["tree_cleanup_confirmed"] = False
                else:
                    record["tree_cleanup_confirmed"] = result.returncode == 0
            else:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    pass
                # The leader may exit before its ASR child. Still signal this
                # invocation's own session group, never an external writer PID.
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                record.update(method="owned POSIX process group", tree_cleanup_confirmed=True)
            process.wait(timeout=5)
            record["child_exited"] = True
        except (OSError, subprocess.TimeoutExpired) as error:
            record.update(cleanup_error=str(error), tree_cleanup_confirmed=False)
            if process.poll() is None:
                process.kill()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
            record["child_exited"] = process.poll() is not None
        self.cleanup.append(record)

    def step(self, name, arguments):
        self.guard()
        command = [sys.executable, *[str(value) for value in arguments]]
        stdout_path, stderr_path = self.output / "logs" / (name + ".stdout.txt"), self.output / "logs" / (name + ".stderr.txt")
        stage = {"name": name, "command": command, "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 "stdout": str(stdout_path), "stderr": str(stderr_path), "status": "running"}
        self.stages.append(stage)
        started = time.monotonic()
        environment = dict(os.environ, HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", CUDA_VISIBLE_DEVICES="",
                           PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        options = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {"start_new_session": True}
        try:
            with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
                process = subprocess.Popen(command, cwd=str(ROOT), env=environment, stdout=stdout, stderr=stderr, **options)
                self.active = process
                while process.poll() is None:
                    try:
                        process.wait(timeout=min(30, self.remaining()))
                    except subprocess.TimeoutExpired:
                        self.guard()
                        print(json.dumps({"stage": name, "elapsed_seconds": math.floor(time.monotonic() - started),
                            "remaining_seconds": math.floor(self.remaining())}), flush=True)
                if process.returncode:
                    raise RuntimeError("Preparation child %s exited %d; inspect its preserved logs" % (name, process.returncode))
            self.guard()
            stage.update(status="completed", returncode=process.returncode)
        except BaseException:
            stage["status"] = "failed"
            if self.active is not None:
                self.stop_owned(self.active)
                stage["returncode"] = self.active.returncode
            raise
        finally:
            self.active = None
            stage["elapsed_seconds"] = time.monotonic() - started
            write_new(self.output / (name + "-stage.json"), stage)
        return stdout_path

    def validate_features(self, directory):
        path = directory / "features-manifest.json"
        manifest = read_json(path)
        body = {key: value for key, value in manifest.items() if key != "feature_id"}
        if (manifest.get("schema") != "unity-voice-features-v2" or manifest.get("dataset") != self.identity
                or manifest.get("feature_id") != canonical(body)
                or manifest["frontend"].get("frontend_id") != canonical(manifest["frontend"]["config"])):
            raise ValueError("Fresh local features differ from exact full candidate identity")
        entries = index_rows(manifest["entries"])
        if set(entries) != set(self.source_rows) or {row["split"] for row in entries.values()} != {"train", "heldout"}:
            raise ValueError("Fresh features lack complete IDs or grouped splits")
        inventory = {}
        for key, entry in entries.items():
            row = self.source_rows[key]
            if (entry["audio_sha256"] != row["sha256"] or any(entry[field] != row[field]
                    for field in ("text", "audio", "voice_id", "source_id", "emotion", "intensity", "pace", "speech_act"))):
                raise ValueError("Feature/source labels differ: " + key)
            feature = child_path(directory, entry["feature"])
            if file_hash(feature) != entry["sha256"]:
                raise ValueError("Fresh feature file changed: " + key)
            inventory[entry["feature"]] = entry["sha256"]
        self.feature_identity = {"feature_id": manifest["feature_id"], "frontend_id": manifest["frontend"]["frontend_id"],
            "dataset_id": self.identity["dataset_id"], "clips": len(entries),
            "splits": dict(collections.Counter(entry["split"] for entry in entries.values())),
            "feature_inventory_id": canonical(inventory), "host_os": platform.system(),
            "host_python": platform.python_version(), "linux_fresh_repreparation_required": True,
            "uploaded_features": False, "source_performance_acceptance": "pending"}
        self.artifacts["local_feature_manifest"] = artifact(path)

    def pipeline(self):
        self.complete_writers()
        summary_dir = self.output / "source-summary"
        self.step("01-source-summary", [VOICE / "summarize_source_screen.py", self.dataset, self.screen, summary_dir])
        summary = read_json(summary_dir / "summary.json")
        if summary.get("status") != "complete_inventory_screen_summary" or summary.get("source_dataset_identity") != self.identity:
            raise ValueError("Full summary did not establish the exact completed inventory")
        for name in ("summary.json", "clips.jsonl", "listening-tasks.json"):
            self.artifacts["source_summary_" + name] = artifact(summary_dir / name)
        if self.remaining() < 60:
            raise TimeoutError("Insufficient remaining deadline for bounded second-ASR preparation")
        recheck_dir = self.output / "word-recheck"
        self.step("02-word-recheck", [VOICE / "recheck_source_words.py", self.dataset, summary_dir, recheck_dir,
            "--threads", "4", "--max-seconds", str(min(3600, math.floor(self.remaining())))])
        recheck = read_json(recheck_dir / "summary.json")
        if recheck.get("complete_requested_subset") is not True or recheck.get("source_packet_status") != "complete_inventory_screen_summary":
            raise ValueError("Second-ASR requested queue did not finish; preserve partial evidence")
        for name in ("recheck-recipe.json", "summary.json"):
            self.artifacts["word_recheck_" + name] = artifact(recheck_dir / name)
        if (recheck_dir / "rechecks.jsonl").is_file():
            self.artifacts["word_recheck_results"] = artifact(recheck_dir / "rechecks.jsonl")
        review_path = self.output / "full-candidate-review.pending.json"
        self.step("03-pending-review", [VOICE / "curate_dataset.py", "template", self.dataset, review_path])
        review = read_json(review_path)
        if (review.get("draft_dataset") != self.identity or len(review["clips"]) != self.identity["clips"]
                or any(row["decision"] != "pending" or row["listened"] is not False or row["actual_delivery"] is not None
                       for row in review["clips"]) or review.get("reviewer") is not None
                or review.get("reviewer_kind") is not None or review.get("reviewed_at") is not None):
            raise ValueError("Review template must remain complete and entirely pending")
        reviews = index_rows(review["clips"])
        if set(reviews) != set(self.source_rows):
            raise ValueError("Pending review does not cover every source ID exactly once")
        for key, row in self.source_rows.items():
            entry = reviews[key]
            delivery = {field: row[field] for field in ("emotion", "intensity", "pace", "speech_act")}
            if (entry["wav_sha256"] != row["sha256"] or entry["text"] != row["text"]
                    or entry["audio"] != row["audio"] or entry["voice_id"] != row["voice_id"]
                    or entry["original_source_id"] != row["source_id"] or entry["intended_delivery"] != delivery):
                raise ValueError("Pending review differs from source hash/text/labels: " + key)
        self.artifacts["pending_human_review"] = artifact(review_path)
        features = self.output / "local-candidate-features"
        self.step("04-local-preprocessing", [VOICE / "prep.py", self.dataset, features])
        self.validate_features(features)
        preflight_log = self.step("05-offline-preflight", [VOICE / "pod/preflight_voice.py", "--offline",
            "--dataset", self.dataset, "--dataset-id", self.identity["dataset_id"], "--source-digest", self.expected_digest])
        preflight = read_json(preflight_log)
        if preflight.get("source_digest") != self.expected_digest or preflight.get("dataset") != self.identity or preflight.get("training_authorized") is not False:
            raise ValueError("Offline preflight did not bind exact full candidate/source")
        self.artifacts["offline_preflight"] = artifact(preflight_log)
        delivery_dir = self.output / "delivery"
        self.step("06-delivery", [VOICE / "pod/prepare_launch.py", self.dataset, delivery_dir,
            "--dataset-id", self.identity["dataset_id"], "--source-digest", self.expected_digest])
        packet = read_json(delivery_dir / "packet.json")
        if (packet.get("schema") != "unity-voice-delivery-v1" or packet.get("dataset") != self.identity
                or packet.get("source_digest") != self.expected_digest or packet.get("training_authorized") is not False
                or packet.get("status") != "locked-preparation-only" or packet.get("archive") != "delivery.tar"
                or packet.get("archive_sha256") != file_hash(delivery_dir / "delivery.tar")):
            raise ValueError("Delivery identity/archive differs from locked candidate")
        if any(not key.startswith(("source/training/voice/", "dataset/")) for key in packet["files"]):
            raise ValueError("Delivery unexpectedly contains local features or unrelated inputs")
        wanted_audio = {"dataset/" + row["audio"]: row["sha256"] for row in self.source_rows.values()}
        wanted_audio["dataset/metadata.jsonl"] = self.identity["metadata_sha256"]
        if {key: sha for key, sha in packet["files"].items() if key.startswith("dataset/")} != wanted_audio:
            raise ValueError("Delivery dataset inventory differs")
        with tarfile.open(delivery_dir / "delivery.tar", "r:") as archive:
            members = archive.getmembers()
            if (len(members) != len(packet["files"]) + 1
                    or {member.name for member in members} != set(packet["files"]) | {"delivery.json"}
                    or any(not member.isfile() for member in members)):
                raise ValueError("Actual delivery archive contains unexpected/missing files")
        self.artifacts["delivery_packet"] = artifact(delivery_dir / "packet.json")
        self.artifacts["delivery_archive"] = artifact(delivery_dir / "delivery.tar")
        template = read_json(VOICE / "pod/LAUNCH_CONFIG.template.json")
        populated = dict(template, VOICE_DIGEST=self.expected_digest,
                         VOICE_DATASET_ID=self.identity["dataset_id"], VOICE_DATASET_DIR=str(self.dataset))
        if template.get("status") != "locked-no-rental-no-training":
            raise ValueError("Launch template no longer represents locked preparation")
        for field, value in populated.items():
            if field not in {"schema", "status", "VOICE_DIGEST", "VOICE_DATASET_ID", "VOICE_DATASET_DIR", "candidate_work", "notes"} and value is not None:
                raise ValueError("Unobserved price/provider/registry/durability/approval must remain null: " + field)
        populated["notes"] = list(template["notes"]) + [
            "This exact full source dataset is a candidate, not an accepted corpus or approved training run.",
            "VOICE_DATASET_DIR is its actual local path, not a future cloud mount attestation.",
            "Local Windows/host features are excluded from delivery; reprepare freshly in the actual pinned Linux environment."]
        launch_path = self.output / "launch-config.locked.json"
        write_new(launch_path, populated)
        self.artifacts["locked_launch_config"] = artifact(launch_path)
        self.guard()
        self.qa = {"base_summary": summary, "second_asr_summary": recheck,
            "pending_review_rows": len(review["clips"]), "all_review_decisions_pending": True}

    def report(self, status, error=None):
        result = {"schema": "unity-full-source-preparation-result-v1", "status": status,
            "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "source_digest": self.expected_digest, "source_manifest_sha256": self.manifest_sha,
            "quality_gate_sha256": self.gate_sha, "render_recipe_sha256": self.recipe_sha,
            "dataset": self.identity, "local_features": self.feature_identity, "artifacts": self.artifacts,
            "stages": self.stages, "owned_child_cleanup": self.cleanup,
            "deadline_seconds": self.seconds, "elapsed_seconds": time.monotonic() - self.started,
            "source_dataset": str(self.dataset), "base_screen": str(self.screen),
            "source_performance_acceptance": "pending", "full_corpus_human_listening_inferred": False,
            "corpus_acceptance_granted": False, "training_authorized": False, "student_training_started": False,
            "pod_rental_authorized": False, "deployment_authorized": False,
            "unobserved_launch": {"price": None, "budget": None, "provider": None, "registry": None,
                                  "durability": None, "owner_paid_approval": None},
            "future_linux_features": "Fresh preprocessing required after exact delivery/environment verification; no feature files uploaded.",
            "error": error}
        if hasattr(self, "qa"):
            result["qa"] = self.qa
        write_new(self.output / "preparation-result.json", result)
        print(json.dumps({"status": status, "dataset_id": self.identity["dataset_id"] if self.identity else None,
            "feature_id": self.feature_identity["feature_id"] if self.feature_identity else None,
            "result": str(self.output / "preparation-result.json"), "training_authorized": False,
            "pod_rental_authorized": False}, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path); parser.add_argument("screen", type=Path); parser.add_argument("out", type=Path)
    parser.add_argument("--source-digest", required=True)
    parser.add_argument("--max-seconds", type=int, required=True)
    args = parser.parse_args()
    if not HASH.fullmatch(args.source_digest) or not 60 <= args.max_seconds <= 28800:
        raise ValueError("Provide exact source digest and explicit 60..28800-second preparation deadline")
    dataset, screen, output = [path.resolve() for path in (args.dataset, args.screen, args.out)]
    if (output.exists() or args.out.is_symlink() or not output.is_relative_to(LOCAL.resolve())
            or not output.is_relative_to(ROOT.resolve())
            or output.is_relative_to(dataset) or output.is_relative_to(screen) or output.is_relative_to(VOICE.resolve())
            or dataset == screen or not dataset.is_dir() or not screen.is_dir()):
        raise ValueError("Source/screen must exist separately; use a NEW .local output outside immutable inputs and voice code")
    prep = Preparation(args)
    prep.guard()  # Refuse stale/unfrozen inputs before creating any preparation directory.
    output.mkdir(parents=True, exist_ok=False)
    (output / "logs").mkdir()
    write_new(output / "preparation-request.json", {"schema": "unity-full-source-preparation-request-v1",
        "source_digest": args.source_digest, "source_manifest_sha256": prep.manifest_sha,
        "dataset": str(dataset), "screen": str(screen), "deadline_seconds": args.max_seconds,
        "python": sys.executable, "driver_sha256": file_hash(Path(__file__)),
        "scope": "local preparation only; no source writers launched/stopped; no approvals, training, rental or uploads"})
    try:
        prep.pipeline()
        prep.report("complete_full_candidate_preparation_unaccepted")
    except BaseException as error:
        if prep.active is not None:
            prep.stop_owned(prep.active)
        prep.report("failed_or_partial_preparation", {"type": type(error).__name__, "message": str(error),
                    "traceback": traceback.format_exc()})
        raise SystemExit(2) from error


if __name__ == "__main__":
    main()
