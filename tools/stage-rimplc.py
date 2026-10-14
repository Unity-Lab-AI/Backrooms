"""Stage the RimPLC package into the game's Mods folder, hash-checked against its manifest.

    python tools/stage-rimplc.py            # refresh artifacts/build/rimplc-package-manifest.json, then stage
    python tools/stage-rimplc.py --manifest # refresh the manifest only

Every file listed in the manifest is copied and read back; a mismatch rolls the folder back to the backup. The
companion DLL ships INSIDE the package (RimPLC/BridgeTools/RimPLC.BridgeTools.dll); a second copy in the game's
own BridgeTools/RimPLC/ root registers the same tools twice (RimBridgeServer: "Capability alias
'rimplc/enable_rung' is already registered"), so any copy found there is moved aside, never left in place.
"""
import datetime
import hashlib
import json
import pathlib
import shutil
import sys
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[1]
PKG = ROOT / "RimPLC"
MANIFEST = ROOT / "artifacts" / "build" / "rimplc-package-manifest.json"
RECEIPT = ROOT / "artifacts" / "build" / "rimplc-staging-receipt.json"
GAME = pathlib.Path(r"C:\Program Files (x86)\Steam\steamapps\common\Rimworld")
DEST = GAME / "Mods" / "RimPLC"
GLOBAL_COMPANION = GAME / "BridgeTools" / "RimPLC"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def refresh_manifest():
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    changed = []
    for f in m["files"]:
        p = PKG / f["path"]
        b = p.read_bytes()
        h = hashlib.sha256(b).hexdigest()
        if h != f["sha256"] or len(b) != f["bytes"]:
            changed.append(f["path"])
        f["bytes"], f["sha256"] = len(b), h
    m["recorded_at"] = now()
    MANIFEST.write_text(json.dumps(m, indent=2) + "\n", encoding="utf-8")
    print("rimplc manifest: %d files, changed: %s" % (len(m["files"]), ", ".join(changed) or "none"))
    return m


def move_global_companion():
    if not GLOBAL_COMPANION.exists():
        return None
    aside = ROOT / "artifacts" / "staging-backups" / ("rimplc-global-companion-" + uuid.uuid4().hex)
    aside.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(GLOBAL_COMPANION), str(aside))
    print("moved the second companion copy %s aside to %s" % (GLOBAL_COMPANION, aside))
    return str(aside)


def stage(m):
    for f in m["files"]:   # the package must still be the manifest's build
        assert sha(PKG / f["path"]) == f["sha256"], "package changed after its manifest: " + f["path"]
    backup = None
    if DEST.exists():
        about = (DEST / "About" / "About.xml").read_text(encoding="utf-8")
        assert "<packageId>Operator.RimPLC</packageId>" in about, "existing folder is another package"
        backup = ROOT / "artifacts" / "staging-backups" / ("rimplc-" + uuid.uuid4().hex)
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(DEST), str(backup))
    try:
        for f in m["files"]:
            t = DEST / f["path"]
            t.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(PKG / f["path"], t)
            assert sha(t) == f["sha256"], "staged file differs: " + f["path"]
    except Exception:
        failed = ROOT / "artifacts" / "staging-failed" / ("rimplc-" + uuid.uuid4().hex)
        failed.parent.mkdir(parents=True, exist_ok=True)
        if DEST.exists():
            shutil.move(str(DEST), str(failed))
        if backup:
            shutil.move(str(backup), str(DEST))
        raise
    aside = move_global_companion()
    receipt = {"PackageId": m["packageId"], "Version": m["modVersion"], "Destination": str(DEST),
               "Backup": str(backup) if backup else None, "GlobalCompanionMovedTo": aside, "Files": m["files"],
               "StagedAt": now(), "ProfileChanged": False, "GameLaunched": False}
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print("Staged and hash-checked %d RimPLC package files at %s (backup: %s)" % (len(m["files"]), DEST, backup))


if __name__ == "__main__":
    manifest = refresh_manifest()
    if "--manifest" not in sys.argv:
        stage(manifest)
