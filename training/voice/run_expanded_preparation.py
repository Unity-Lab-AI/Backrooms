"""Local background source preparation only; never trains, rents or uploads.

Wait for the existing 1,378-source run, render only the new expansion jobs,
screen each parent, merge unchanged recordings and produce features/delivery.
The immutable source digest is checked throughout. Existing writers are never
started or stopped here. Failure preserves all source, outputs and logs.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
VOICE = ROOT / "training/voice"
sys.path.insert(0, str(VOICE / "pod"))
from preflight_voice import source_identity
from dataset_contract import file_hash, load_dataset, load_features


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class Pipeline:
    def __init__(self, args):
        self.args = args
        self.out = args.output.resolve()
        self.started = time.monotonic()
        self.deadline = self.started + args.max_seconds
        self.children = {}
        self.stages = []
        self.stage = "initializing"
        self.manifest_sha = file_hash(VOICE / "VOICE_MANIFEST.json")
        self.gate_sha = file_hash(VOICE / "VOICE_QUALITY_GATE.json")
        self.last_guard = 0.0
        self.guard(force=True)
        if self.out.exists() or not self.out.is_relative_to((ROOT / ".local/voice-lab").resolve()):
            raise ValueError("Use a NEW output directory under this workspace's .local/voice-lab")
        for name in ("seed", "seed_screen", "qwen_model", "cosy_code", "cosy_model", "asr_model"):
            if not getattr(args, name).is_dir():
                raise ValueError("Required existing local directory is missing: " + name)
        for name in ("qwen_python", "cosy_python"):
            if not getattr(args, name).is_file():
                raise ValueError("Required source interpreter is missing: " + name)
        self.out.mkdir(parents=True)
        (self.out / "logs").mkdir()
        self.status()

    def remaining(self):
        value = self.deadline - time.monotonic()
        if value <= 0:
            raise TimeoutError("Local source preparation deadline reached; no training was started")
        return value

    def guard(self, force=False):
        self.remaining()
        if force or time.monotonic() - self.last_guard >= 30:
            if file_hash(VOICE / "VOICE_MANIFEST.json") != self.manifest_sha:
                raise ValueError("Frozen manifest changed; preserve this job and review before restarting")
            source_identity(self.args.source_digest)
            if file_hash(VOICE / "VOICE_QUALITY_GATE.json") != self.gate_sha:
                raise ValueError("Gate changed during this preparation-only job")
            gate = read(VOICE / "VOICE_QUALITY_GATE.json")
            if gate["training_allowed"] is not False or gate["deployment_allowed"] is not False:
                raise ValueError("Background source preparation requires closed training/deployment gates")
            if gate["checks"]["owner_training_authorization"]["accepted"] is not False:
                raise ValueError("This job does not operate under a paid training authorization")
            self.last_guard = time.monotonic()

    def status(self, **extra):
        data = {"schema": "unity-expanded-source-job-v1", "recorded_at": stamp(),
                "pid": os.getpid(), "stage": self.stage, "source_digest": self.args.source_digest,
                "deadline_seconds": self.args.max_seconds,
                "elapsed_seconds": round(time.monotonic() - self.started, 1),
                "owned_children": {name: process.pid for name, process in self.children.items() if process.poll() is None},
                "training_started": False, "pod_rented": False, "uploaded": False,
                "corpus_acceptance": "not_granted", **extra}
        temporary = self.out / "status.json.writing"
        temporary.write_text(json.dumps(data, indent=2), encoding="utf-8")
        os.replace(temporary, self.out / "status.json")
        print(json.dumps(data), flush=True)

    def start(self, name, arguments, cpu=False):
        self.guard(force=True)
        command = [sys.executable, "-B", "-u", *map(str, arguments)]
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
        if cpu:
            env.update(CUDA_VISIBLE_DEVICES="", HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1")
        else:
            env.update(VOICE_SOURCE_SETUP_SECONDS="600", VOICE_SOURCE_CLIP_SECONDS="300")
        options = ({"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW}
                   if os.name == "nt" else {"start_new_session": True})
        stdout = (self.out / "logs" / (name + ".stdout.log")).open("xb")
        stderr = (self.out / "logs" / (name + ".stderr.log")).open("xb")
        try:
            process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=stdout, stderr=stderr, **options)
        finally:
            stdout.close(); stderr.close()
        self.children[name] = process
        self.stages.append({"name": name, "command": command, "pid": process.pid, "started_at": stamp()})
        self.status()
        return process

    def wait(self, *names):
        while True:
            self.guard()
            for name in names:
                code = self.children[name].poll()
                if code is not None and code != 0:
                    raise RuntimeError(name + " failed (exit %d); inspect preserved logs" % code)
            if all(self.children[name].poll() is not None for name in names):
                for name in names:
                    self.children[name].wait()
                self.status(completed_stages=list(names))
                return
            self.status()
            time.sleep(min(30, self.remaining()))

    def run(self, name, arguments, cpu=True):
        self.stage = name
        self.start(name, arguments, cpu=cpu)
        self.wait(name)

    def stop_owned(self):
        for name, process in self.children.items():
            if process.poll() is not None:
                continue
            if os.name == "nt":
                result = subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                    capture_output=True, timeout=15, creationflags=subprocess.CREATE_NO_WINDOW)
                (self.out / "logs" / (name + ".cleanup.log")).write_bytes(result.stdout + result.stderr)
            else:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                    time.sleep(2)
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            if process.poll() is None:
                process.kill()
            process.wait(timeout=10)

    def summarize_parent(self, name, dataset, screen):
        summary, recheck = self.out / (name + "-summary"), self.out / (name + "-word-recheck")
        self.run(name + "-summary", [VOICE / "summarize_source_screen.py", dataset, screen, summary])
        self.run(name + "-word-recheck", [VOICE / "recheck_source_words.py", dataset, summary, recheck,
                  "--threads", "4", "--max-seconds", str(min(7200, int(self.remaining())))])
        return summary, recheck

    def execute(self):
        a = self.args
        self.stage = "waiting_existing_seed_and_screen"
        while not ((a.seed / "source-build.json").is_file() and (a.seed_screen / "summary.json").is_file()):
            self.guard()
            if list(a.seed.glob("source-*-timeout.json")):
                raise RuntimeError("Existing seed writer timed out; explicit recovery required")
            self.status(seed_dataset=str(a.seed), seed_screen=str(a.seed_screen))
            time.sleep(min(30, self.remaining()))
        seed_report = read(a.seed / "source-build.json")
        seed_scan = read(a.seed_screen / "summary.json")
        _, seed_identity = load_dataset(a.seed, verify_audio=True)
        if seed_report["dataset"] != seed_identity or seed_scan.get("complete_expected_inventory") is not True:
            raise ValueError("Seed source/screen receipt is partial or mismatched")
        seed_summary, seed_recheck = self.summarize_parent("seed", a.seed, a.seed_screen)
        extras, extra_screen = self.out / "expansion-source", self.out / "expansion-screen"
        self.stage = "rendering_expansion_only"
        self.start("expansion-render", [VOICE / "make_dataset_optimized.py", extras, "--all",
            "--qwen-batch-size", "2", "--model-dir", a.qwen_model, "--qwen-python", a.qwen_python,
            "--cosy-python", a.cosy_python, "--cosy-code-dir", a.cosy_code, "--cosy-model-dir", a.cosy_model])
        while not (extras / "render-recipe.json").is_file():
            self.guard()
            code = self.children["expansion-render"].poll()
            if code is not None:
                raise RuntimeError("Expansion exited before publishing its recipe (exit %s)" % code)
            self.status()
            time.sleep(min(5, self.remaining()))
        self.start("expansion-screen", [VOICE / "inspect_source_audio.py", extras, extra_screen,
            "--model-dir", a.asr_model, "--threads", "4", "--watch",
            "--max-seconds", str(min(86400, int(self.remaining())))], cpu=True)
        self.wait("expansion-render", "expansion-screen")
        extra_summary, extra_recheck = self.summarize_parent("expansion", extras, extra_screen)
        merged, qa = self.out / "merged-5000-candidate", self.out / "merged-source-qa"
        self.run("merge-dataset", [VOICE / "merge_source_datasets.py", merged,
            "--parent", a.seed, "--parent", extras, "--minimum-clips", "5000"])
        self.run("merge-qa", [VOICE / "merge_source_qa.py", merged, qa,
            "--parent-qa", a.seed, a.seed_screen, seed_summary, seed_recheck,
            "--parent-qa", extras, extra_screen, extra_summary, extra_recheck])
        pending = self.out / "candidate-listening.pending.json"
        self.run("pending-review", [VOICE / "curate_dataset.py", "template", merged, pending])
        features = self.out / "local-candidate-features"
        self.run("local-preprocessing", [VOICE / "prep.py", merged, features])
        _, identity = load_dataset(merged, verify_audio=True)
        feature_manifest = load_features(features)
        if feature_manifest["dataset"] != identity:
            raise ValueError("Finished feature manifest differs from the merged dataset")
        self.run("offline-preflight", [VOICE / "pod/preflight_voice.py", "--offline", "--dataset", merged,
            "--dataset-id", identity["dataset_id"], "--source-digest", a.source_digest])
        delivery = self.out / "delivery"
        self.run("delivery", [VOICE / "pod/prepare_launch.py", merged, delivery,
            "--dataset-id", identity["dataset_id"], "--source-digest", a.source_digest])
        packet = read(delivery / "packet.json")
        if (packet["archive_sha256"] != file_hash(delivery / "delivery.tar")
                or packet["dataset"] != identity or packet["source_digest"] != a.source_digest
                or packet["status"] != "locked-preparation-only"
                or packet["training_authorized"] is not False or packet["deployment_authorized"] is not False):
            raise ValueError("Finished delivery identity, archive or preparation-only scope differs")
        config = read(VOICE / "pod/LAUNCH_CONFIG.template.json")
        config.update(VOICE_DIGEST=a.source_digest, VOICE_DATASET_ID=identity["dataset_id"], VOICE_DATASET_DIR=str(merged))
        (self.out / "launch-config.locked.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
        self.guard(force=True)
        result = {"schema": "unity-expanded-source-result-v1", "status": "completed_candidate_not_accepted",
            "recorded_at": stamp(), "source_digest": a.source_digest, "dataset": identity,
            "local_feature_id": feature_manifest["feature_id"], "delivery": packet,
            "merged_source_qa": str(qa), "pending_review": str(pending), "stages": self.stages,
            "training_started": False, "pod_rented": False, "uploaded": False,
            "corpus_acceptance": "not_granted", "student_quality": "untrained-unverified",
            "future_linux_features": "Reprepare in the pinned Linux environment; local features are not uploaded"}
        (self.out / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        self.stage = "completed_candidate_not_accepted"
        self.status(dataset=identity, delivery_sha256=packet["archive_sha256"])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("seed", "seed-screen", "output", "qwen-model", "qwen-python", "cosy-python", "cosy-code", "cosy-model", "asr-model"):
        p.add_argument("--" + name, type=Path, required=True)
    p.add_argument("--source-digest", required=True)
    p.add_argument("--max-seconds", type=int, default=86400)
    args = p.parse_args()
    if not 3600 <= args.max_seconds <= 172800:
        raise ValueError("Local background preparation limit must be 1..48 hours")
    pipeline = Pipeline(args)
    try:
        pipeline.execute()
    except BaseException as error:
        pipeline.stage = "failed_preserved_for_lead_review"
        (pipeline.out / "failure.json").write_text(json.dumps({"recorded_at": stamp(),
            "type": type(error).__name__, "message": str(error), "traceback": traceback.format_exc()}, indent=2), encoding="utf-8")
        try:
            pipeline.stop_owned()
        finally:
            pipeline.status(error=str(error))
        raise SystemExit(2) from error


if __name__ == "__main__":
    main()
