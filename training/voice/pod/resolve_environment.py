"""Resolve published CP310 Linux artifacts from small public metadata only.

No install, containers, cloud calls, Torch imports or model generation. CUDA
Torch wheel METADATA is fetched, not its multi-GB wheel. The small official spaCy
language wheel is read only to obtain authoritative dependencies/hash. Results
are metadata resolution, not observed Linux installation or functional acceptance.
Requires the existing packaging library; never installs it.
"""
import argparse
import email
import hashlib
import html.parser
import importlib.metadata
import io
import json
import re
import sys
import tarfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

from packaging.markers import default_environment
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.utils import canonicalize_name, parse_wheel_filename
from packaging.version import InvalidVersion, Version

HERE = Path(__file__).resolve().parent
CACHE = {}
TARGET = dict(default_environment(), python_version="3.10", python_full_version="3.10.18",
              implementation_version="3.10.18", platform_system="Linux", sys_platform="linux",
              os_name="posix", platform_machine="x86_64", platform_release="", platform_version="")


def request(url, headers=None, maximum=20000000):
    req = urllib.request.Request(url, headers={"User-Agent": "Unity-source-preparation/1", **(headers or {})})
    with urllib.request.urlopen(req, timeout=45) as response:
        raw = response.read(maximum + 1)
        if len(raw) > maximum:
            raise ValueError("Metadata/allowed small artifact exceeded limit: " + url)
        return raw, dict(response.headers)


def get_json(url, headers=None):
    return json.loads(request(url, headers)[0])


def compatible(filename):
    if not filename.endswith(".whl"):
        return False
    _, _, _, tags = parse_wheel_filename(filename)
    for tag in tags:
        interpreter = tag.interpreter
        python = interpreter in ("cp310", "py3", "py310") or (
            tag.abi == "abi3" and interpreter.startswith("cp") and int(interpreter[2:]) <= 310)
        if not python or tag.abi not in ("cp310", "abi3", "none"):
            continue
        platform = tag.platform
        if platform == "any":
            return True
        if not platform.endswith("_x86_64") or not platform.startswith(("manylinux", "linux")):
            continue
        match = re.match(r"manylinux_(\d+)_(\d+)_", platform)
        if match and (int(match[1]), int(match[2])) > (2, 36):
            continue
        return True
    return False


def cuda_package(name):
    class Links(html.parser.HTMLParser):
        def __init__(self):
            super().__init__(); self.urls = []
        def handle_starttag(self, tag, attrs):
            if tag == "a":
                value = dict(attrs).get("href")
                if value:
                    self.urls.append(value)
    index = "https://download.pytorch.org/whl/cu126/" + name + "/"
    parser = Links(); parser.feed(request(index)[0].decode())
    choices = []
    for link in parser.urls:
        url = urllib.parse.urljoin(index, link)
        filename = urllib.parse.unquote(urllib.parse.urlsplit(url).path.rsplit("/", 1)[-1])
        if filename.startswith(name + "-2.7.1+cu126-") and compatible(filename):
            choices.append((filename, url))
    if len(choices) != 1:
        raise ValueError("Expected one CUDA CP310 Linux wheel: " + name)
    filename, url = choices[0]
    fragment = urllib.parse.parse_qs(urllib.parse.urlsplit(url).fragment)
    digest = fragment.get("sha256", [None])[0]
    if not digest or not re.fullmatch("[0-9a-f]{64}", digest):
        raise ValueError("Official CUDA index omitted wheel digest")
    url = urllib.parse.urldefrag(url)[0]
    raw = request(url + ".metadata", maximum=1000000)[0]
    metadata = email.message_from_bytes(raw)
    return {"name": name, "version": metadata["Version"], "requires_python": metadata["Requires-Python"],
            "requires_dist": metadata.get_all("Requires-Dist", []),
            "artifact": {"filename": filename, "url": url, "sha256": digest, "kind": "wheel"},
            "metadata_url": url + ".metadata", "metadata_sha256": hashlib.sha256(raw).hexdigest()}


def language_model():
    release = get_json("https://api.github.com/repos/explosion/spacy-models/releases/tags/en_core_web_sm-3.8.0")
    asset = next(asset for asset in release["assets"] if asset["name"] == "en_core_web_sm-3.8.0-py3-none-any.whl")
    raw = request(asset["browser_download_url"])[0]
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        name = next(name for name in archive.namelist() if name.endswith(".dist-info/METADATA"))
        metadata_raw = archive.read(name)
    metadata = email.message_from_bytes(metadata_raw)
    return {"name": "en-core-web-sm", "version": metadata["Version"], "requires_python": metadata["Requires-Python"],
            "requires_dist": metadata.get_all("Requires-Dist", []),
            "artifact": {"filename": asset["name"], "url": asset["browser_download_url"],
                         "sha256": hashlib.sha256(raw).hexdigest(), "kind": "wheel"},
            "metadata_url": asset["browser_download_url"] + "#METADATA",
            "metadata_sha256": hashlib.sha256(metadata_raw).hexdigest()}


def artifact_metadata(item):
    """The selected artifact can differ from PyPI's version-level summary."""
    url = item["url"]
    if item["packagetype"] == "bdist_wheel":
        metadata_url = url + ".metadata"
        try:
            raw = request(metadata_url, maximum=1000000)[0]
        except urllib.error.HTTPError as error:
            if error.code != 404 or item["size"] > 20000000:
                raise
            wheel = request(url)[0]
            if hashlib.sha256(wheel).hexdigest() != item["digests"]["sha256"]:
                raise ValueError("Wheel differs from published artifact digest")
            with zipfile.ZipFile(io.BytesIO(wheel)) as archive:
                name = next(name for name in archive.namelist() if name.endswith(".dist-info/METADATA"))
                raw = archive.read(name)
            metadata_url = url + "#METADATA"
    else:
        # Small source archives are data only. Never execute setup.py/PEP517.
        archive_raw = request(url)[0]
        if hashlib.sha256(archive_raw).hexdigest() != item["digests"]["sha256"]:
            raise ValueError("Source archive differs from published digest")
        with tarfile.open(fileobj=io.BytesIO(archive_raw), mode="r:*") as archive:
            members = [member for member in archive.getmembers() if member.isfile()
                       and member.name.endswith("/PKG-INFO")]
            member = min(members, key=lambda member: len(member.name))
            raw = archive.extractfile(member).read()
        metadata_url = url + "#PKG-INFO"
    return email.message_from_bytes(raw), metadata_url, hashlib.sha256(raw).hexdigest()


def pypi_version(name, version):
    url = "https://pypi.org/pypi/" + name + "/" + version + "/json"
    if url not in CACHE:
        raw = request(url, maximum=3000000)[0]
        data = json.loads(raw)
        artifacts = [item for item in data["urls"] if not item.get("yanked") and compatible(item["filename"])]
        if not artifacts:
            artifacts = [item for item in data["urls"] if item["packagetype"] == "sdist"]
        if not artifacts or (data["info"].get("requires_python")
                and Version("3.10.18") not in SpecifierSet(data["info"]["requires_python"])):
            CACHE[url] = None
        else:
            item = sorted(artifacts, key=lambda item: item["filename"])[0]
            metadata, metadata_url, metadata_sha = artifact_metadata(item)
            if (canonicalize_name(metadata["Name"]) != name or Version(metadata["Version"]) != Version(version)):
                raise ValueError("Selected artifact METADATA name/version differs")
            python_requirement = metadata["Requires-Python"] or data["info"].get("requires_python")
            if python_requirement and Version("3.10.18") not in SpecifierSet(python_requirement):
                CACHE[url] = None
                return None
            CACHE[url] = {"name": name, "version": metadata["Version"],
                "requires_python": python_requirement,
                "requires_dist": metadata.get_all("Requires-Dist", []),
                "artifact": {"filename": item["filename"], "url": item["url"],
                             "sha256": item["digests"]["sha256"], "kind": item["packagetype"]},
                "metadata_url": metadata_url, "metadata_sha256": metadata_sha,
                "version_summary_url": url, "version_summary_sha256": hashlib.sha256(raw).hexdigest(),
                "version_summary_requires_dist": data["info"].get("requires_dist") or []}
    return CACHE[url]


def choose(name, requirements, special):
    specs = [requirement.specifier for requirement in requirements]
    accepted = lambda version: all(Version(version) in spec for spec in specs)
    if name in special:
        result = special[name]
        if not accepted(result["version"]):
            raise ValueError("Incompatible pinned special artifact: " + name)
        return result
    pinned = {str(spec.version) for requirement in requirements for spec in requirement.specifier if spec.operator == "==" and "*" not in spec.version}
    versions = list(pinned)
    if not versions:
        try:
            local = importlib.metadata.version(name)
            if accepted(local):
                versions.append(local)
        except importlib.metadata.PackageNotFoundError:
            pass
        project = get_json("https://pypi.org/pypi/" + name + "/json")
        valid_versions = []
        for value in project["releases"]:
            try:
                valid_versions.append(Version(value))
            except InvalidVersion:
                continue
        versions += [str(version) for version in sorted(valid_versions, reverse=True)
                     if not version.is_prerelease and accepted(str(version)) and str(version) not in versions]
    for version in versions:
        if accepted(version):
            result = pypi_version(name, version)
            if result:
                return result
    raise ValueError("No published CP310 Linux artifact satisfies " + name + ": " + ", ".join(map(str, specs)))


def base_image():
    token = get_json("https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/python:pull")["token"]
    headers = {"Authorization": "Bearer " + token,
               "Accept": "application/vnd.oci.image.index.v1+json,application/vnd.docker.distribution.manifest.list.v2+json"}
    base = "https://registry-1.docker.io/v2/library/python/"
    raw, response = request(base + "manifests/3.10.18-slim-bookworm", headers, maximum=1000000)
    index = json.loads(raw)
    child = next(entry for entry in index["manifests"] if entry["platform"].get("os") == "linux"
                 and entry["platform"].get("architecture") == "amd64")
    headers["Accept"] = "application/vnd.oci.image.manifest.v1+json,application/vnd.docker.distribution.manifest.v2+json"
    manifest_raw = request(base + "manifests/" + child["digest"], headers, maximum=1000000)[0]
    if "sha256:" + hashlib.sha256(manifest_raw).hexdigest() != child["digest"]:
        raise ValueError("Registry platform manifest digest differs")
    config = get_json(base + "blobs/" + json.loads(manifest_raw)["config"]["digest"], headers)
    if "PYTHON_VERSION=3.10.18" not in config["config"]["Env"]:
        raise ValueError("Published base Python differs")
    return {"tag": "python:3.10.18-slim-bookworm", "platform": "linux/amd64",
            "index_digest": "sha256:" + hashlib.sha256(raw).hexdigest(),
            "platform_digest": child["digest"], "reference": "python@" + child["digest"],
            "config_digest": json.loads(manifest_raw)["config"]["digest"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="NEW metadata lock JSON; never overwrites")
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Output exists; preserve previous metadata evidence")
    spec = json.loads((HERE / "ENVIRONMENT_SPEC.json").read_text(encoding="utf-8"))
    roots = [Requirement(name + ("[en]" if name == "misaki" else "") + "==" + version)
             for name, version in spec["packages"].items()]
    roots += [Requirement("pip==25.3"), Requirement("setuptools==80.9.0"),
              Requirement("wheel==0.45.1"), Requirement("Cython==3.0.12")]
    special = {"torch": cuda_package("torch"), "torchaudio": cuda_package("torchaudio"),
               "en-core-web-sm": language_model()}
    selected, extras = {}, {}
    for round_number in range(30):
        requirements, next_extras = {}, {}
        for requirement in roots:
            name = canonicalize_name(requirement.name)
            requirements.setdefault(name, []).append(requirement)
            next_extras.setdefault(name, set()).update(requirement.extras)
        for name, package in selected.items():
            for text in package["requires_dist"]:
                requirement = Requirement(text)
                if requirement.marker and not any(requirement.marker.evaluate(dict(TARGET, extra=extra))
                        for extra in {"", *extras.get(name, set())}):
                    continue
                target = canonicalize_name(requirement.name)
                if requirement.url:
                    raise ValueError("Review an explicit URL dependency separately: " + text)
                requirements.setdefault(target, []).append(requirement)
                next_extras.setdefault(target, set()).update(requirement.extras)
        next_selected = {name: choose(name, constraints, special) for name, constraints in sorted(requirements.items())}
        if next_selected == selected and next_extras == extras:
            break
        selected, extras = next_selected, next_extras
        print("Metadata resolution round", round_number + 1, "packages", len(selected), flush=True)
    else:
        raise ValueError("Metadata dependency graph did not converge; no complete lock claimed")
    lock = {"schema": "unity-voice-linux-artifact-lock-v1", "status": "metadata-resolved-not-built",
            "target": TARGET, "base_image": base_image(), "packages": selected,
            "root_requirements": list(map(str, roots)),
            "limitations": ["No Linux install, image build, ABI, phoneme or H100 execution verified.",
                            "Published sdists must build with pinned tooling; built wheel hashes are not claimed.",
                            "Actual custom image digest and OS package inventory remain future build observations."]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(lock, stream, indent=2, sort_keys=True)
    print("Published metadata only:", args.output, "packages", len(selected), "base", lock["base_image"]["reference"])


if __name__ == "__main__":
    main()
