#!/usr/bin/env python3
"""Export the standalone RimPLC repository locally; never run Git or contact a remote.

The build manifest owns the loadable file list. This exporter adds only RimPLC's
own source, the root license and a standalone reader-facing README. Fresh staging
and hash checks precede publication. Unknown or locally changed output is refused
and preserved; nothing is recursively deleted.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
import uuid
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / "RimPLC"
EXPORT_PARENT = ROOT / ".local" / "export"
DEFAULT_MANIFEST = ROOT / "artifacts/build/rimplc-package-manifest.json"
REQUIRED = {
    "About/About.xml", "LoadFolders.xml", "1.7/Assemblies/RimPLC.dll",
    "1.7/Defs/MainButtonDefs/RimPLC_MainButtons.xml",
    "Languages/English/Keyed/RimPLC.xml", "Presets/LadderV2.json",
    "About/Preview.png", "About/RimPLC_Badge.png",
}
OPTIONAL = {"BridgeTools/RimPLC.BridgeTools.dll"}
SOURCE_PROJECTS = ("Source/RimPLC", "Source/RimPLC.BridgeTools")
SOURCE_SUFFIXES = {".cs", ".csproj", ".props", ".targets"}
SCHEMAS = ("ladder", "mark", "rung", "sensor", "tag", "tools")
SKIP_DIRECTORIES = {"bin", "obj", ".git", ".vs", "packages", "__pycache__"}
SECRET_MARKERS = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|"
    r"\bgh[pousr]_[A-Za-z0-9]{20,}\b|\bAKIA[0-9A-Z]{16}\b|"
    r"https?://[^\s/:]+:[^\s/@]+@")


class Refusal(Exception):
    pass


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def relative(value):
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise Refusal("invalid relative path: %r" % value)
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in ("", ".", "..") for part in value.split("/")):
        raise Refusal("unsafe relative path: %r" % value)
    return path


def checked(path, boundary=ROOT, must_exist=True):
    """Reject symlinks/reparse points in every ancestor, including existing parents."""
    path = Path(os.path.abspath(str(path)))
    boundary = Path(os.path.abspath(str(boundary)))
    try:
        path.relative_to(boundary)
    except ValueError:
        raise Refusal("path is outside its allowed root: %s" % path)
    for item in (path,) + tuple(path.parents):
        if item.exists() or item.is_symlink():
            info = item.lstat()
            if stat.S_ISLNK(info.st_mode) or (
                    getattr(info, "st_file_attributes", 0) &
                    getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)):
                raise Refusal("symlink or reparse-point path refused: %s" % item)
        if item == boundary:
            break
    if must_exist and not path.exists():
        raise Refusal("required input does not exist: %s" % path)
    if not path.resolve(strict=must_exist).is_relative_to(boundary.resolve()):
        raise Refusal("resolved path escapes its allowed root: %s" % path)
    return path


def file_record(path, rel, role):
    checked(path)
    if not path.is_file():
        raise Refusal("expected a regular file: %s" % path)
    return {"path": rel, "bytes": path.stat().st_size,
            "sha256": digest(path), "role": role}


def read_json(path):
    checked(path)
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (ValueError, UnicodeError) as exc:
        raise Refusal("invalid JSON in %s: %s" % (path, exc))


def validate_manifest(path):
    data = read_json(path)
    if not isinstance(data, dict):
        raise Refusal("package manifest must be an object")
    about = ET.parse(checked(PACKAGE / "About/About.xml")).getroot()
    name = about.findtext("name")
    version = about.findtext("modVersion")
    versions = [node.text for node in about.findall("supportedVersions/li")]
    if (about.findtext("packageId") != "Operator.RimPLC" or name != "RimPLC" or
            about.findtext("author") != "Operator" or not version):
        raise Refusal("RimPLC About.xml identity does not match this exporter")
    if about.find("modDependencies") is not None:
        raise Refusal("the standalone package unexpectedly declares dependencies")
    if versions != ["1.6", "1.7"]:
        raise Refusal("expected the declared 1.6 and 1.7 game targets")
    if (data.get("packageId") != "Operator.RimPLC" or
            data.get("modVersion") != version or data.get("supportedVersions") != versions):
        raise Refusal("manifest identity/version does not match About.xml")
    entries = data.get("files")
    if not isinstance(entries, list) or not entries:
        raise Refusal("build manifest contains no file list")
    records, seen = [], set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise Refusal("manifest file entries must be objects")
        rel = str(relative(entry.get("path")))
        if rel.casefold() in seen:
            raise Refusal("duplicate or case-colliding manifest path: %s" % rel)
        seen.add(rel.casefold())
        if rel not in REQUIRED | OPTIONAL:
            raise Refusal("not an allowlisted loadable/companion file: %s" % rel)
        expected_size = entry.get("bytes", entry.get("length", entry.get("size")))
        expected_hash = entry.get("sha256")
        if (type(expected_size) is not int or expected_size < 0 or
                not isinstance(expected_hash, str) or
                re.fullmatch(r"[0-9a-fA-F]{64}", expected_hash) is None):
            raise Refusal("invalid size/hash for %s" % rel)
        actual = file_record(PACKAGE / rel, rel, "package")
        if actual["bytes"] != expected_size or actual["sha256"] != expected_hash.lower():
            raise Refusal("package file differs from the build manifest: %s" % rel)
        records.append(actual)
    missing = REQUIRED - {item["path"] for item in records}
    if missing:
        raise Refusal("build manifest omits required package files: %s" % ", ".join(sorted(missing)))
    load = ET.parse(checked(PACKAGE / "LoadFolders.xml")).getroot()
    if load.tag != "loadFolders" or [node.tag for node in load] != ["v1.6", "v1.7"]:
        raise Refusal("unexpected load-folder game-version mapping")
    for node in load:
        if [item.text for item in node] != ["/", "1.7"]:
            raise Refusal("each game target must select root and shared 1.7 content")
    for project, assembly in zip(SOURCE_PROJECTS, ("RimPLC", "RimPLC.BridgeTools")):
        project_file = checked(PACKAGE / project / (assembly + ".csproj"))
        tree = ET.parse(project_file).getroot()
        if (tree.findtext("PropertyGroup/AssemblyName") != assembly or
                tree.findtext("PropertyGroup/Version") != version):
            raise Refusal("source project identity/version differs from the package: %s" % project)
    return version, versions, sorted(records, key=lambda item: item["path"])


def own_sources():
    records = []
    for project in SOURCE_PROJECTS:
        start = checked(PACKAGE / project)
        for parent, directories, names in os.walk(start, followlinks=False):
            directories[:] = sorted(name for name in directories if name.casefold() not in SKIP_DIRECTORIES)
            for directory in directories:
                checked(Path(parent) / directory)
            for name in sorted(names):
                path = checked(Path(parent) / name)
                rel = path.relative_to(PACKAGE).as_posix()
                if path.suffix.lower() not in SOURCE_SUFFIXES:
                    raise Refusal("unreviewed source-project file refused: %s" % rel)
                if SECRET_MARKERS.search(path.read_text(encoding="utf-8-sig")):
                    raise Refusal("credential marker in source file: %s" % rel)
                records.append(file_record(path, rel, "source"))
    return records


def support_documents():
    result = []
    for name in SCHEMAS:
        source = checked(ROOT / ("docs/rimplc/schema/" + name + ".schema.json"))
        value = read_json(source)
        if not isinstance(value, dict):
            raise Refusal("schema is not an object: %s" % source)
        def inspect_refs(node):
            if isinstance(node, dict):
                ref = node.get("$ref")
                if ref and not ref.startswith("#"):
                    filename = ref.split("#", 1)[0]
                    if filename not in {item + ".schema.json" for item in SCHEMAS}:
                        raise Refusal("schema references an unexported document: %s" % ref)
                for child in node.values():
                    inspect_refs(child)
            elif isinstance(node, list):
                for child in node:
                    inspect_refs(child)
        inspect_refs(value)
        result.append((source, file_record(source, "docs/schema/" + source.name, "schema")))
    source = checked(ROOT / "docs/wiki/rimplc.md")
    original = source.read_text(encoding="utf-8-sig")
    text = re.sub(r"\A---\r?\n.*?\r?\n---\r?\n", "", original, count=1, flags=re.S).lstrip()
    text = text.replace("(install.md)", "(https://g-fourteen.github.io/Rimrooms-AsyncIndustries/install.html)")
    text = text.replace("(links.md)", "(https://g-fourteen.github.io/Rimrooms-AsyncIndustries/links.html)")
    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
        if not target.startswith(("https://", "http://", "#")):
            raise Refusal("standalone guide contains an unresolved relative link: %s" % target)
    if SECRET_MARKERS.search(text):
        raise Refusal("credential marker in the RimPLC guide")
    return result, file_record(source, "docs/wiki/rimplc.md", "guide-context"), text


def readme(version, has_bridge, github_url):
    bridge = """
## Optional RimBridgeServer tools

The core mod does not require RimBridgeServer. Its file API works at
`<RimWorld config folder>/RimPLC/inbox.jsonl`, returning results in `outbox.jsonl`.

To build the optional companion after building the core:

```powershell
dotnet build Source/RimPLC.BridgeTools/RimPLC.BridgeTools.csproj -c Release -p:RimWorldPath="C:/path/to/RimWorld" -p:RimBridgeSdkPath="C:/path/to/RimBridgeServer.Sdk.dll"
```

With RimBridgeServer installed, copy **only** `BridgeTools/RimPLC.BridgeTools.dll`
to `<RimWorld>/BridgeTools/RimPLC/`. The SDK and bridge are supplied by their own
project; neither is bundled here. The companion exposes `rimplc/read_ladder`,
`read_state`, `set_tag`, `set_mark`, `upsert_rung`, `remove_rung`, `enable_rung`,
`letters_seen`, `export` and `import`.
"""
    if not has_bridge:
        bridge += "\nThe companion source is included; its DLL was not present in this exported build.\n"
    github = ("- [GitHub](%s)\n" % github_url) if github_url else (
        "\nThe GitHub mirror is pending creation. This export does not create or update it.\n")
    return """# RimPLC

![RimPLC — colony logic and control](About/Preview.png)

A standalone ladder-logic advisor for RimWorld. Sensors read the colony, tags set
thresholds, marks hold recorded values, and rungs describe **if this, then this**.
The main tab shows each rung's live contacts and lets you edit, enable, import and
export a ladder. Advice is the default; this version's automatic coils are limited
to messages, marks and tags. It does not build, spawn or destroy world objects.

**Version {version}.** Package ID `Operator.RimPLC`; author `Operator`.
RimWorld **1.6 and 1.7** are declared targets and share the current `1.7/` content
folder. A declaration is not a compatibility result: a running 1.7 session has
not yet been verified. The core requires no other mod, Harmony or expansion.
Rimrooms-specific preset rungs remain inactive without Rimrooms.

Read the [user guide](docs/USER_GUIDE.md). JSON formats for rules, tags, sensors,
marks, ladders and commands are included under [docs/schema](docs/schema/).

## Install

Copy this repository's mod files to a local Mods folder as `RimPLC`, keeping
`About/` and `LoadFolders.xml` directly inside it. The loadable files are
`About/`, `LoadFolders.xml`, `1.7/`, `Languages/` and `Presets/`; `Source/` is for
developers and `BridgeTools/` is the separate optional companion below.
Enable RimPLC through your mod manager. Back up a save before changing its mod
list; removal from an existing save has not been checked.

## Build the core

Install a .NET SDK and use your own local RimWorld installation:

```powershell
dotnet build Source/RimPLC/RimPLC.csproj -c Release -p:RimWorldPath="C:/path/to/RimWorld"
```

`RIMWORLD_PATH` is also accepted. The project targets .NET Framework 4.7.2 and
C# 7.3, treats warnings as errors, and writes `1.7/Assemblies/RimPLC.dll`.
Game assemblies are read from `RimWorldWin64_Data/Managed` with `Private=false`
and are never copied into the output. Build commands do not stage or launch the
game. The shipped `Presets/LadderV2.json` is self-contained; no parent repository,
Python generator or training dataset is needed to build or run this mod.
{bridge}
## License and repositories

Original RimPLC source is MIT licensed; see [LICENSE](LICENSE). RimWorld and its
assemblies belong to Ludeon Studios and are not included.

The original [mod preview](About/Preview.png) and transparent
[branding badge](About/RimPLC_Badge.png) use a cream/brass ladder-circuit motif.
They are promotional artwork; the game's RimPLC controls remain text-based.

- [Forgejo](https://git.unityailab.com/GFourteen/RimPLC)
{github}

These are the owner's publication destinations. A local export does not confirm
that either remote has been created or updated.
""".format(version=version, bridge=bridge, github=github)


GITIGNORE = """# Build caches, symbols, IDE settings and local credentials never ship.
**/bin/
**/obj/
.vs/
*.pdb
*.user
*.suo
.env
.env.*
*.pem
*.key
"""


def tree_files(root):
    result = {}
    if not root.exists():
        return result
    checked(root)
    if not root.is_dir():
        raise Refusal("export path is not a directory: %s" % root)
    for parent, directories, names in os.walk(root, followlinks=False):
        if Path(parent) == root:
            directories[:] = [name for name in directories if name != ".git"]
            names = [name for name in names if name != ".git"]
        for name in directories:
            checked(Path(parent) / name)
        for name in names:
            path = checked(Path(parent) / name)
            rel = path.relative_to(root).as_posix()
            if rel.casefold() in {key.casefold() for key in result}:
                raise Refusal("case-colliding export path: %s" % rel)
            result[rel] = file_record(path, rel, "export")
    return result


def write_json(path, value):
    checked(path, must_exist=False)
    temp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    checked(temp, must_exist=False)
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temp, path)


def prepare_output(output, state_path, expected):
    existing = tree_files(output)
    old = read_json(state_path) if state_path.exists() else None
    if old is not None:
        if (old.get("schema") != 1 or old.get("output") != str(output) or
                old.get("exporter") != "export-rimplc-repo.py"):
            raise Refusal("previous export ownership receipt is invalid")
        owned = {item["path"]: item for item in old.get("files", [])}
    else:
        owned = {}
    unexpected = set(existing) - set(owned)
    stale = set(owned) - set(expected)
    if unexpected or stale:
        raise Refusal("existing files preserved; review them before export. Unmanaged: %s; retired: %s" %
                      (", ".join(sorted(unexpected)) or "none", ", ".join(sorted(stale)) or "none"))
    for rel, item in existing.items():
        if item["sha256"] != owned[rel].get("sha256") or item["bytes"] != owned[rel].get("bytes"):
            raise Refusal("locally changed export file preserved: %s" % rel)
    # A changed README/receipt is not silently treated as an authorised overwrite.
    return existing


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=EXPORT_PARENT / "RimPLC")
    parser.add_argument("--github-url", help="Confirmed mirror URL; omitted while repository creation is pending")
    args = parser.parse_args()
    if args.github_url not in (None, "https://github.com/G-Fourteen/RimPLC"):
        raise Refusal("the GitHub destination must be the owner's exact mirror URL")
    manifest = checked(args.manifest)
    output = checked(args.output, boundary=EXPORT_PARENT, must_exist=False)
    if output.parent != EXPORT_PARENT or not re.fullmatch(r"RimPLC(?:-[A-Za-z0-9_-]+)?", output.name):
        raise Refusal("output must be a managed .local/export/RimPLC or RimPLC-<suffix> directory")
    checked(EXPORT_PARENT, must_exist=False).mkdir(parents=True, exist_ok=True)
    state_path = EXPORT_PARENT / (output.name + "-export-state.json")
    checked(state_path, must_exist=False)
    version, versions, package_records = validate_manifest(manifest)
    inputs = [(PACKAGE / item["path"], item) for item in package_records + own_sources()]
    documents, guide_context, guide_text = support_documents()
    inputs += documents
    license_record = file_record(checked(ROOT / "LICENSE"), "LICENSE", "license")
    inputs.append((ROOT / "LICENSE", license_record))
    # Record the current project guide as context, without copying its parent-repo links.
    guide = file_record(checked(PACKAGE / "README.md"), "RimPLC/README.md", "context")
    manifest_record = file_record(manifest, manifest.relative_to(ROOT).as_posix(), "build-manifest")
    generated = {"README.md": readme(version, any(item["path"] in OPTIONAL for item in package_records), args.github_url),
                 ".gitignore": GITIGNORE, "docs/USER_GUIDE.md": guide_text}
    expected = {item["path"] for _, item in inputs} | set(generated)
    if len(expected) != len(inputs) + len(generated):
        raise Refusal("duplicate export paths")
    prepare_output(output, state_path, expected)
    staging = EXPORT_PARENT / (".RimPLC-stage-" + uuid.uuid4().hex)
    checked(staging, must_exist=False).mkdir()
    payload = staging / "payload"
    payload.mkdir()
    for source, item in inputs:
        target = checked(payload / str(relative(item["path"])), must_exist=False)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        if digest(target) != item["sha256"] or target.stat().st_size != item["bytes"]:
            raise Refusal("input changed while copying: %s" % item["path"])
    for rel, text in generated.items():
        (payload / rel).write_text(text, encoding="utf-8", newline="\n")
    snapshot = tree_files(payload)
    if set(snapshot) != expected:
        raise Refusal("staged file list differs from the explicit allowlist")
    for item in list(inputs) + [(PACKAGE / "README.md", guide),
                               (ROOT / "docs/wiki/rimplc.md", guide_context), (manifest, manifest_record)]:
        if digest(item[0]) != item[1]["sha256"]:
            raise Refusal("input changed before publication: %s" % item[0])
    receipt = {"schema": 1, "exporter": "export-rimplc-repo.py",
               "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "output": str(output), "packageId": "Operator.RimPLC", "modVersion": version,
               "supportedVersions": versions, "build_manifest": manifest_record,
               "project_readme_context": guide,
               "user_guide_context": guide_context, "confirmed_github_url": args.github_url,
               "inputs": [item for _, item in inputs], "files": list(snapshot.values()),
               "source_snapshot_sha256": hashlib.sha256(json.dumps(
                   [item for _, item in inputs if item["role"] == "source"],
                   sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest(),
               "staging": str(staging), "git_or_network_called": False,
               "runtime_17_verified": False}
    write_json(staging / "prepared-export.json", receipt)
    existing = prepare_output(output, state_path, expected)
    if not output.exists():
        os.replace(payload, output)
    else:
        # Replace only previously owned, unchanged files. Never sweep the checkout.
        for rel in sorted(expected):
            source = payload / rel
            target = checked(output / rel, must_exist=False)
            target.parent.mkdir(parents=True, exist_ok=True)
            temp = checked(target.with_name(target.name + "." + uuid.uuid4().hex + ".tmp"), must_exist=False)
            shutil.copyfile(source, temp)
            if target.exists():
                previous = existing.get(rel)
                if (previous is None or target.stat().st_size != previous["bytes"] or
                        digest(target) != previous["sha256"]):
                    raise Refusal("export file changed during publication; preserved: %s" % rel)
            elif rel in existing:
                raise Refusal("export file disappeared during publication: %s" % rel)
            os.replace(temp, target)
    actual = tree_files(output)
    if set(actual) != expected or any(actual[rel]["sha256"] != snapshot[rel]["sha256"] for rel in expected):
        raise Refusal("published local tree differs from the prepared snapshot; staging preserved")
    write_json(state_path, receipt)
    print(json.dumps({"output": str(output), "receipt": str(state_path), "files": len(actual),
                      "package_files": len(package_records),
                      "source_files": sum(item["role"] == "source" for _, item in inputs),
                      "modVersion": version, "supportedVersions": versions,
                      "source_snapshot_sha256": receipt["source_snapshot_sha256"],
                      "git_or_network_called": False}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (Refusal, OSError, ET.ParseError, UnicodeError) as exc:
        print("RimPLC export refused: %s" % exc, file=sys.stderr)
        sys.exit(1)
