"""Export observed installed distribution/OS/runtime-asset inventories.

For the future image build only. No model imports, CUDA tests or network calls.
The observation is pending engineering review, never automatic acceptance.
"""
import argparse
import hashlib
import importlib.metadata
import json
import platform
import re
import subprocess
from pathlib import Path


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            value.update(chunk)
    return value.hexdigest()


def installed_paths(package):
    output = subprocess.run(["dpkg-query", "-L", package], capture_output=True,
                            text=True, timeout=30, check=True).stdout
    return [Path(line) for line in output.splitlines() if line.startswith("/")]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="NEW directory")
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Observation directory exists; preserve it")
    normalize = lambda name: re.sub(r"[-_.]+", "-", name).lower()
    names = {normalize(dist.metadata["Name"]) for dist in importlib.metadata.distributions()}
    packages = {name: importlib.metadata.version(name) for name in sorted(names)}
    metadata_lock = Path(__file__).with_name("environment.lock.json")
    expected = json.loads(metadata_lock.read_text(encoding="utf-8"))
    if (expected.get("schema") != "unity-voice-linux-artifact-lock-v1"
            or platform.python_version() != expected["target"]["python_full_version"]
            or any(packages.get(name) != package["version"] for name, package in expected["packages"].items())):
        raise ValueError("Built interpreter/distributions differ from metadata-resolved pins")
    english = Path(importlib.metadata.distribution("en-core-web-sm").locate_file("en_core_web_sm"))
    loader = Path(importlib.metadata.distribution("espeakng-loader").locate_file("espeakng_loader"))
    espeak_libraries = [path for path in installed_paths("libespeak-ng1") if path.name.startswith("libespeak-ng.so")]
    sndfile_libraries = [path for path in installed_paths("libsndfile1") if path.name.startswith("libsndfile.so")]
    data_roots = set()
    for path in installed_paths("espeak-ng-data"):
        for candidate in (path, *path.parents):
            if candidate.name == "espeak-ng-data" and candidate.is_dir():
                data_roots.add(candidate)
    if not espeak_libraries or not sndfile_libraries or not data_roots:
        raise ValueError("Installed Debian runtime assets could not be located")
    roots = {"english_model": [english], "espeak_library": [*espeak_libraries, loader],
             "espeak_data": sorted(data_roots), "libsndfile": sndfile_libraries}
    assets, roles = {}, {}
    for role, sources in roots.items():
        paths = set()
        for source in sources:
            if not source.exists():
                raise ValueError("Expected built asset missing: " + str(source))
            files = source.rglob("*") if source.is_dir() else [source]
            paths.update(str(path.resolve()) for path in files if path.is_file() and path.suffix != ".pyc")
        if not paths:
            raise ValueError("Empty asset role: " + role)
        roles[role] = sorted(paths)
        assets.update({path: digest(Path(path)) for path in paths})
    query_format = "-f=" + "$" + "{Package}\t" + "$" + "{Version}\n"
    os_packages = subprocess.run(["dpkg-query", "-W", query_format],
                                 capture_output=True, text=True, timeout=30, check=True).stdout
    args.output.mkdir(parents=True)
    for name, body in {"package-lock.json": packages, "runtime-assets.json": assets}.items():
        (args.output / name).write_text(json.dumps(body, indent=2, sort_keys=True), encoding="utf-8")
    (args.output / "os-packages.tsv").write_text(os_packages, encoding="utf-8")
    observation = {"schema": "unity-voice-environment-observation-v1", "decision": "pending",
        "python": platform.python_version(), "platform": platform.platform(), "image_digest": None,
        "package_lock_path": str((args.output / "package-lock.json").resolve()),
        "package_lock_sha256": digest(args.output / "package-lock.json"),
        "runtime_assets_path": str((args.output / "runtime-assets.json").resolve()),
        "runtime_assets_sha256": digest(args.output / "runtime-assets.json"),
        "runtime_asset_roles": roles, "os_packages_sha256": digest(args.output / "os-packages.tsv"),
        "artifact_lock_sha256": digest(metadata_lock),
        "limitations": ["Inventory only; no H100, phoneme, inference, training, provider or spending acceptance."]}
    (args.output / "observation.json").write_text(json.dumps(observation, indent=2), encoding="utf-8")
    print("Pending environment inventory exported; no acceptance:", args.output)


if __name__ == "__main__":
    main()
