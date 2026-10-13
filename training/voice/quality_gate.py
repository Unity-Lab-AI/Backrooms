"""Refuse voice training/deployment until recorded quality and safety checks are accepted.

This is an attestation gate, not a substitute for listening or engineering validation.
Training requires approved source audio, a corpus and a preparation/evaluation plan;
it does NOT require an already trained final voice. Deployment adds final listening
and device/playback acceptance. No receipt or approval is manufactured by this tool.

Usage: python training/voice/quality_gate.py --stage train|deploy
Receipts live under training/voice/, are SHA256-bound in VOICE_QUALITY_GATE.json,
and contain: schema_version=1, check_id, decision="accepted", accepted_by,
recorded_at, scope="training-preflight"|"deployment", evidence (nonempty list).
Owner checks require accepted_by="owner" and an actual recorded owner decision.
Evidence may refer to local listening artifacts not copied to the training pod.
Corpus acceptance also binds approved_dataset_id to the supplied VOICE_DATASET_ID;
accepting a heard pilot never approves a different, unheard full dataset.
Paid authorization additionally binds approved_source_digest, approved_dataset_id,
owner_quote, approved_hourly_price, approved_budget_usd and approved_config. Config
uses the exact environment keys in RUN_CONFIG_FIELDS. These are concrete values,
not templates. Local deploy checks bind source/dataset identity without pod prices.
"""
import argparse
import hashlib
import json
import os
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

HERE = Path(__file__).resolve().parent
GATE_PATH = HERE / "VOICE_QUALITY_GATE.json"
TRAIN_CHECKS = (
    "source_auditions", "corpus_acceptance", "emotion_conditioning",
    "leakage_free_evaluation", "free_running_evaluation", "resume_integrity",
    "budget_stop_integrity", "immutable_run_inputs", "owner_training_authorization",
)
DEPLOY_CHECKS = ("trained_voice_acceptance", "local_playback_acceptance")
OWNER_CHECKS = {
    "source_auditions", "corpus_acceptance", "owner_training_authorization",
    "trained_voice_acceptance",
}
MUTABLE_RECEIPT_CHECKS = {"owner_training_authorization", *DEPLOY_CHECKS}
WORK_DEFAULTS = {
    "ACOUSTIC_STEPS": 20000, "ACOUSTIC_FRAMES": 96000,
    "VOCODER_STEPS": 120000, "VOCODER_BATCH": 32, "GTA_STEPS": 20000, "VOICE_SEED": 17,
}
RUN_CONFIG_FIELDS = {*WORK_DEFAULTS, "VOICE_VOLUME_ID", "VOICE_VOLUME_RECEIPT_SHA256", "KEEP_HOURS"}


def sha_identity(value, name):
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ValueError(name + " must be an exact lowercase SHA256 identity")
    return value


def number(value, name, nonnegative=False, receipt=False):
    if isinstance(value, bool) or (receipt and not isinstance(value, (int, float))):
        raise ValueError(name + " must be a concrete JSON number")
    try:
        parsed = Decimal(str(value))
    except InvalidOperation:
        raise ValueError(name + " must be numeric") from None
    if not parsed.is_finite() or (parsed < 0 if nonnegative else parsed <= 0):
        raise ValueError(name + " must be finite and " + ("nonnegative" if nonnegative else "positive"))
    return parsed


def owner_quote(receipt):
    quote = receipt.get("owner_quote")
    if (not isinstance(quote, str) or not quote.strip() or not any(char.isalnum() for char in quote)
            or quote.strip().casefold() in {"todo", "tbd", "pending", "placeholder", "replace me", "not approved"}):
        raise ValueError("owner_quote must contain the actual recorded owner decision, not a placeholder")


GENERATED = "generated-on-pod"


def bind_run_identity(receipt):
    # On-pod generation: the dataset does not exist when the owner says go. The paid authorization then binds the
    # source exactly and leaves the dataset to corpus_acceptance (generated-on-pod), which binds VOICE_DATASET_ID to
    # the screened corpus made from the approved script. Only the owner's training authorization may use this mode.
    if receipt.get("mode") == GENERATED and receipt.get("check_id") == "owner_training_authorization":
        if receipt.get("approved_dataset_id") != GENERATED:
            raise ValueError("a generated-on-pod authorization must set approved_dataset_id to " + GENERATED)
        expected = sha_identity(receipt.get("approved_source_digest"), "approved_source_digest")
        if expected != sha_identity(os.environ.get("VOICE_DIGEST"), "VOICE_DIGEST"):
            raise ValueError("approved_source_digest differs from the explicit VOICE_DIGEST")
        sha_identity(os.environ.get("VOICE_DATASET_ID"), "VOICE_DATASET_ID")
        return
    for field, environment in (("approved_source_digest", "VOICE_DIGEST"), ("approved_dataset_id", "VOICE_DATASET_ID")):
        expected = sha_identity(receipt.get(field), field)
        actual = sha_identity(os.environ.get(environment), environment)
        if expected != actual:
            raise ValueError(field + " differs from the explicit " + environment)


def bind_corpus_identity(receipt):
    """A reviewed pilot receipt cannot approve a different, unheard training corpus."""
    if receipt.get("mode") == "generated-on-pod":
        return bind_generated_corpus(receipt)
    expected = sha_identity(receipt.get("approved_dataset_id"), "approved_dataset_id")
    actual = sha_identity(os.environ.get("VOICE_DATASET_ID"), "VOICE_DATASET_ID")
    if expected != actual:
        raise ValueError("Corpus acceptance differs from the explicit VOICE_DATASET_ID")


def bind_generated_corpus(receipt):
    """On-pod generation (owner, 2026-10-12: the pod makes the clips "for the traing pod to use right then iin the
    moment"): no clip exists before the run, so the owner approves the exact SCRIPT and the automatic screen rule.
    The corpus at VOICE_DATASET_DIR is accepted only if the script files still hash to the approval, every training
    row's id and text come from that script, the screen report applied the approved rule, and enough clips survived.
    """
    for name, wanted in receipt["approved_script_sha256"].items():
        if file_hash(HERE / name) != sha_identity(wanted, name):
            raise ValueError("Approved script changed: " + name)
    script = {}
    for name in receipt["approved_script_sha256"]:
        for line in (HERE / name).read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                script[row["id"]] = row["text"]
    if not os.environ.get("VOICE_DATASET_DIR"):
        raise ValueError("no VOICE_DATASET_DIR: the generated corpus is checked on the pod, after generation")
    root = Path(os.environ["VOICE_DATASET_DIR"])
    report = json.loads((root / "screen-report.json").read_text(encoding="utf-8"))
    if report.get("rule") != receipt["screen_rule"]:
        raise ValueError("Generated corpus was screened with a different rule than the approved one")
    rows = [json.loads(l) for l in (root / "metadata.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    lines = set(script.values())
    stray = [r["id"] for r in rows if r["text"] not in lines]
    if stray:
        raise ValueError("%d generated rows are not lines of the approved script" % len(stray))
    if len(rows) < int(receipt["minimum_clips"]):
        raise ValueError("Only %d screened clips survived; the approval needs at least %s" % (len(rows), receipt["minimum_clips"]))
    if report["kept"]["dataset_id"] != sha_identity(os.environ.get("VOICE_DATASET_ID"), "VOICE_DATASET_ID"):
        raise ValueError("VOICE_DATASET_ID is not the screened generated corpus")


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bind_training_configuration(receipt):
    """Compare numeric amounts exactly; 4.99 and 4.990 represent the same price."""
    for field, environment, default in (("approved_hourly_price", "PRICE_PER_HOUR", None),
                                        ("approved_budget_usd", "BUDGET_USD", "50")):
        expected = number(receipt.get(field), field, receipt=True)
        actual = number(os.environ.get(environment) or default, environment)
        if expected != actual:
            raise ValueError(field + " differs from the actual " + environment)
    approved = receipt.get("approved_config")
    if not isinstance(approved, dict) or set(approved) != RUN_CONFIG_FIELDS:
        raise ValueError("approved_config must contain exactly: " + ", ".join(sorted(RUN_CONFIG_FIELDS)))
    work = {}
    for field, default in WORK_DEFAULTS.items():
        supplied = os.environ.get(field) or str(default)
        if re.fullmatch(r"[0-9]+", supplied) is None:
            raise ValueError(field + " must be a concrete integer")
        actual = int(supplied)
        if actual < (0 if field == "VOICE_SEED" else 1) or type(approved[field]) is not int or approved[field] != actual:
            raise ValueError(field + " differs from its exact approved integer")
        work[field] = actual
    if work["ACOUSTIC_FRAMES"] < 3000 or work["GTA_STEPS"] >= work["VOCODER_STEPS"]:
        raise ValueError("approved work has an invalid frame budget or GTA/source split")
    if not 0 <= work["VOICE_SEED"] < 2 ** 32:
        raise ValueError("VOICE_SEED must be in the trainers' uint32 range 0..4294967295")
    volume = os.environ.get("VOICE_VOLUME_ID")
    if not isinstance(volume, str) or re.fullmatch(r"[A-Za-z0-9_-]{1,128}", volume) is None or approved["VOICE_VOLUME_ID"] != volume:
        raise ValueError("VOICE_VOLUME_ID must match the concrete approved provider volume")
    volume_receipt = sha_identity(os.environ.get("VOICE_VOLUME_RECEIPT_SHA256"), "VOICE_VOLUME_RECEIPT_SHA256")
    if receipt.get("mode") == GENERATED:
        # the pod writes and verifies its own volume receipt after mounting (start_template.sh); the volume id itself
        # is bound above
        if approved["VOICE_VOLUME_RECEIPT_SHA256"] != GENERATED:
            raise ValueError("a generated-on-pod authorization must set VOICE_VOLUME_RECEIPT_SHA256 to " + GENERATED)
    elif sha_identity(approved["VOICE_VOLUME_RECEIPT_SHA256"], "approved volume receipt") != volume_receipt:
        raise ValueError("volume verification receipt differs from the approved configuration")
    keep = number(os.environ.get("KEEP_HOURS") or "1", "KEEP_HOURS", nonnegative=True)
    if number(approved["KEEP_HOURS"], "approved KEEP_HOURS", nonnegative=True, receipt=True) != keep:
        raise ValueError("KEEP_HOURS differs from the approved retention")


def receipt_path(relative):
    """Only voice-preparation receipts travel with the pod's sparse checkout."""
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError("receipt must be a relative path under training/voice/")
    path = (HERE.parent.parent / relative).resolve()
    if HERE not in path.parents or not path.is_file():
        raise ValueError("receipt is missing or outside training/voice/")
    return path


def blockers(stage):
    gate = json.loads(GATE_PATH.read_text(encoding="utf-8"))
    if gate.get("schema_version") != 1:
        raise ValueError("unsupported quality-gate schema")
    checks = gate.get("checks")
    if not isinstance(checks, dict):
        raise ValueError("checks must be an object")
    missing = []
    if gate.get("training_allowed") is not True:
        missing.append("training_allowed is false; preparation is not permission to train")
    if stage == "deploy" and gate.get("deployment_allowed") is not True:
        missing.append("deployment_allowed is false; no final voice is approved")
    required = TRAIN_CHECKS + (DEPLOY_CHECKS if stage == "deploy" else ())
    for check_id in required:
        check = checks.get(check_id)
        if not isinstance(check, dict) or check.get("accepted") is not True:
            reason = check.get("reason", "no acceptance recorded") if isinstance(check, dict) else "check missing"
            missing.append("%s: %s" % (check_id, reason))
            continue
        try:
            raw = receipt_path(check.get("receipt")).read_bytes()
            if hashlib.sha256(raw).hexdigest() != check.get("receipt_sha256"):
                raise ValueError("receipt digest differs from the gate")
            receipt = json.loads(raw)
            if receipt.get("schema_version") != 1 or receipt.get("check_id") != check_id:
                raise ValueError("receipt schema or check identity differs")
            if receipt.get("decision") != "accepted":
                raise ValueError("receipt does not record acceptance")
            authority = receipt.get("accepted_by")
            if not isinstance(authority, str) or not authority.strip():
                raise ValueError("receipt has no named accepting authority")
            if check_id in OWNER_CHECKS and authority != "owner":
                raise ValueError("this check requires the owner's recorded acceptance")
            scope = "deployment" if check_id in DEPLOY_CHECKS else "training-preflight"
            if receipt.get("scope") != scope:
                raise ValueError("receipt has the wrong acceptance scope")
            if not receipt.get("recorded_at") or not isinstance(receipt.get("evidence"), list) or not receipt["evidence"]:
                raise ValueError("receipt lacks a date or supporting evidence references")
            if check_id == "corpus_acceptance":
                owner_quote(receipt)
                bind_corpus_identity(receipt)
            elif check_id == "owner_training_authorization":
                owner_quote(receipt)
                bind_run_identity(receipt)
                if stage == "train":
                    bind_training_configuration(receipt)
            elif check_id in DEPLOY_CHECKS:
                bind_run_identity(receipt)
                if check_id == "trained_voice_acceptance":
                    owner_quote(receipt)
        except (OSError, ValueError, TypeError, AttributeError) as error:
            missing.append("%s: %s" % (check_id, error))
    return missing


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("train", "deploy"), default="train")
    args = parser.parse_args()
    try:
        pending = blockers(args.stage)
    except (OSError, ValueError, TypeError, AttributeError) as error:
        pending = ["invalid or missing quality gate: %s" % error]
    if pending:
        print("VOICE QUALITY GATE CLOSED (%s)" % args.stage, file=sys.stderr)
        for reason in pending:
            print("- " + reason, file=sys.stderr)
        print("No training/deployment authorized. Keep the paid pod uncreated while this gate is closed.", file=sys.stderr)
        return 2
    print("VOICE QUALITY GATE ACCEPTED (%s); this does not provision a pod." % args.stage)
    return 0


if __name__ == "__main__":
    sys.exit(main())
