"""Write a fresh allowlisted Docker context and hash-locked install files.

No Docker command, install, service, training or cloud call is executed.
Only metadata-resolved artifacts are used; source archives build later.
"""
import argparse
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = {"pip", "setuptools", "wheel", "cython", "numpy", "packaging"}
COPY = ("Dockerfile", "DEBIAN_SNAPSHOT.json", "export_environment.py", "start_no_training.sh",
        "environment.lock.json", "ENVIRONMENT_SPEC.json")


def line(name, package):
    artifact = package["artifact"]
    return "%s @ %s --hash=sha256:%s\n" % (name, artifact["url"], artifact["sha256"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="NEW directory; no overwrite")
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Build context exists; preserve it")
    lock = json.loads((HERE / "environment.lock.json").read_text(encoding="utf-8"))
    if lock.get("schema") != "unity-voice-linux-artifact-lock-v1" or not BUILD <= set(lock["packages"]):
        raise ValueError("Metadata lock/build tools missing")
    if lock["base_image"]["reference"] not in (HERE / "Dockerfile").read_text(encoding="utf-8"):
        raise ValueError("Dockerfile and published base identity differ")
    args.output.mkdir(parents=True)
    for name in COPY:
        shutil.copyfile(HERE / name, args.output / name)
    (args.output / "requirements-build.lock.txt").write_text(
        "".join(line(name, lock["packages"][name]) for name in sorted(BUILD)), encoding="utf-8")
    (args.output / "requirements-runtime.lock.txt").write_text(
        "".join(line(name, package) for name, package in sorted(lock["packages"].items()) if name not in BUILD),
        encoding="utf-8")
    (args.output / ".dockerignore").write_text("*\n" + "".join("!" + name + "\n" for name in
        (*COPY, "requirements-build.lock.txt", "requirements-runtime.lock.txt")), encoding="utf-8")
    print("Prepared local context; no build started:", args.output)
    print("Later authorized Linux build: docker build --platform linux/amd64 --tag unity-voice-prepared:local " + str(args.output))


if __name__ == "__main__":
    main()
