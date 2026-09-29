"""Refuse to ship a package whose own pieces do not agree with each other.

Why this exists
---------------
Phase 6 opens with one row: *"Validate Def references, language keys, patch targets,
load folders, package metadata, missing textures/audio, logs, build output, and clean-
install folder structure."* Three of those were already covered -- `check-keyed-strings.py`
owns language keys, `check-dlc-gating.py` owns DLC cross-references, and `audit-gate0.py`
owns the documentation graph. **The rest was covered by nothing at all**, and the first
run of this script found it: `About.xml` declared `<modVersion>0.7.1-dev</modVersion>`
while its own player-facing description still opened "Development build 0.6.4-dev",
seven checkpoints stale. Nobody reads a description against a version field by hand.

Every check here is a cross-reference *inside the shipped package*, so it runs without
the game and without a launch. That is the whole point: this is the part of Phase 6
that never needed the owner.

What it checks
--------------
1. **Package metadata.** `About.xml` parses; `packageId` matches the allowlist; the
   declared `modVersion` matches the csproj `<Version>`; the description does not quote
   a *different* version; `supportedVersions` is non-empty and every entry has a real
   load folder; no attribution strings anywhere in the package.
2. **Allowlist against disk, both directions.** Every allowlisted file exists, and every
   game-loadable file on disk is allowlisted. A def that is present but unlisted ships
   by accident; a listed file that is missing breaks the staging script.
3. **Load-folder structure.** Every loadable file sits under a declared version folder in
   a directory RimWorld actually reads. A `Defs/` folder one level too high loads nothing
   and reports nothing.
4. **Our own def references resolve.** Every `RR_` token referenced from a def must be a
   def this package declares. This is what catches a rename that updated the declaration
   and missed a reference -- an unresolved cross-reference at load, in a mod whose whole
   claim is that it needs nothing but Core.
5. **Patch targets exist.** Each `PatchOperation`'s xpath is resolved down to the defName
   it selects, and that def must exist in the game's own `Data/` or in this package. A
   patch against a def that was renamed by the game is silent: it simply never applies.
6. **Textures.** Every `texPath` naming an `RR_` asset resolves to a real `.png` in the
   package, and every `.png` in the package is referenced by something. Core texture
   paths cannot be verified from disk (they live in asset bundles) and are reported as
   unverifiable rather than passed.
7. **Sounds.** Every `RR_` sound reference resolves to a `SoundDef` this package declares.
8. **Class references.** Every `RimroomsAsyncIndustries` type named by a `workerClass`,
   `compClass`, `giverClass`, `thingClass`, `driverClass` or `Class="..."` attribute must exist
   in the C# source. A def naming a class that is not there fails at load with a red error.
9. **DefInjected.** Every DefInjected key's leading defName must be a def this package
   declares, and its folder must name that def's own type. A DefInjected entry aimed at a
   def that no longer exists is dead text that never reaches a player.

Exit code is non-zero on any failure, so it drops into the checkpoint ritual beside the
other checkers.

Usage
-----
    python tools/check-package-integrity.py
"""

import glob
import io
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries")
ABOUT = os.path.join(MOD, "About", "About.xml")
ALLOWLIST = os.path.join(REPO, "tools", "package-files.json")
CSPROJ = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "RimroomsAsyncIndustries.csproj")
GAME_DATA = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data"

# Directories RimWorld reads inside a version folder. Anything else is inert.
LOADABLE_DIRS = ("Defs", "Patches", "Languages", "Assemblies", "Textures", "Sounds")

# Strings that must never appear in a shipped artifact.
BANNED = ("Co-Authored-By: Claude", "Generated with [Claude", "Made with Claude",
          "noreply@anthropic.com", "claude.ai/code")

# A defName-shaped token belonging to this mod.
RR_TOKEN = re.compile(r"\bRR_[A-Za-z0-9_]+\b")

# XML comments, stripped before reference scanning.
COMMENT = re.compile(r"<!--.*?-->", re.S)

# Files RimWorld reads from the mod root rather than from a version folder.
ROOT_FILES = ("LoadFolders.xml",)

# defName( = 'X' ) or defName="X" inside a patch xpath.
XPATH_DEFNAME = re.compile(r"defName\s*=\s*[\"']([^\"']+)[\"']")


def fail(problems, message):
    problems.append(message)


def read_text(path):
    with io.open(path, encoding="utf-8-sig") as handle:
        return handle.read()


def parse(path, problems):
    try:
        return ET.parse(path).getroot()
    except ET.ParseError as error:
        fail(problems, "XML does not parse: %s (%s)" % (rel(path), error))
        return None


def rel(path):
    return os.path.relpath(path, REPO).replace(os.sep, "/")


def package_version():
    text = read_text(CSPROJ)
    match = re.search(r"<Version>([^<]+)</Version>", text)
    return match.group(1).strip() if match else None


def index_game_defs():
    """defName -> True for every def the installed game ships, Core and DLC alike."""
    names = {}
    if not os.path.isdir(GAME_DATA):
        return None
    pattern = os.path.join(GAME_DATA, "*", "Defs", "**", "*.xml")
    for path in glob.glob(pattern, recursive=True):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        for node in root.iter("defName"):
            if node.text:
                names[node.text.strip()] = True
    return names


def mod_xml_files():
    return sorted(glob.glob(os.path.join(MOD, "**", "*.xml"), recursive=True))


# --------------------------------------------------------------------------- #
# 1. Package metadata
# --------------------------------------------------------------------------- #

def check_metadata(problems, allowlist, versions):
    if not os.path.isfile(ABOUT):
        fail(problems, "About.xml is missing")
        return
    root = parse(ABOUT, problems)
    if root is None:
        return

    def value(tag):
        node = root.find(tag)
        return (node.text or "").strip() if node is not None else None

    package_id = value("packageId")
    if package_id != allowlist.get("packageId"):
        fail(problems, "About.xml packageId %r disagrees with package-files.json %r"
             % (package_id, allowlist.get("packageId")))

    declared = value("modVersion")
    built = package_version()
    if built and declared != built:
        fail(problems, "About.xml modVersion %r disagrees with csproj Version %r"
             % (declared, built))

    # The description is player-facing text that quotes its own build number, and
    # nothing has ever checked it against the field two lines above it.
    description = value("description") or ""
    quoted = set(re.findall(r"\b\d+\.\d+\.\d+-dev\b", description))
    stale = sorted(v for v in quoted if v != declared)
    if stale:
        fail(problems, "About.xml description quotes version(s) %s but modVersion is %r"
             % (", ".join(stale), declared))

    if not versions:
        fail(problems, "About.xml declares no supportedVersions")
    for version in versions:
        if not os.path.isdir(os.path.join(MOD, version)):
            fail(problems, "supportedVersions lists %r with no matching load folder" % version)


def check_no_attribution(problems):
    for path in glob.glob(os.path.join(MOD, "**", "*"), recursive=True):
        if not os.path.isfile(path) or path.lower().endswith((".png", ".dll", ".ogg", ".wav")):
            continue
        try:
            text = read_text(path)
        except (UnicodeDecodeError, OSError):
            continue
        for banned in BANNED:
            if banned in text:
                fail(problems, "attribution string %r found in %s" % (banned, rel(path)))


# --------------------------------------------------------------------------- #
# 2 + 3. Allowlist against disk, and load-folder structure
# --------------------------------------------------------------------------- #

def check_files(problems, allowlist, versions):
    listed = set(allowlist.get("files", []))

    for entry in sorted(listed):
        if not os.path.isfile(os.path.join(MOD, entry.replace("/", os.sep))):
            fail(problems, "package-files.json lists a file that is not on disk: %s" % entry)

    on_disk = set()
    for path in glob.glob(os.path.join(MOD, "**", "*"), recursive=True):
        if not os.path.isfile(path):
            continue
        entry = os.path.relpath(path, MOD).replace(os.sep, "/")
        # About/ is package identity, not loadable content, and is intentionally unlisted.
        if entry.startswith("About/"):
            continue
        on_disk.add(entry)

    for entry in sorted(on_disk - listed):
        fail(problems, "file ships but is not in package-files.json: %s" % entry)

    for entry in sorted(on_disk):
        # LoadFolders.xml is read from the mod root by design -- it is the file that
        # tells RimWorld which version folders exist, so it cannot live inside one.
        if entry in ROOT_FILES:
            continue
        head = entry.split("/")[0]
        if head not in versions:
            fail(problems, "file sits outside every declared version folder: %s" % entry)
            continue
        parts = entry.split("/")
        if len(parts) < 3 or parts[1] not in LOADABLE_DIRS:
            fail(problems, "file is not inside a directory RimWorld loads: %s" % entry)


# --------------------------------------------------------------------------- #
# 4. Our own def references
# --------------------------------------------------------------------------- #

def collect_declared(problems):
    """name -> the set of XML tags declaring it, for every def this package declares.

    Two shapes count as "declared", and missing either produces a false failure:

    * a concrete def with a ``<defName>``;
    * an **abstract parent** carrying ``Name="..."`` and no defName at all. Five of
      this package's defs inherit from three such parents, and they are referenced
      by ``ParentName`` exactly like a real def.

    The value is a *set* because RimWorld namespaces defNames per def type, and this
    package genuinely relies on it: ``RR_CalibrateGate`` is both a `JobDef` and a
    `WorkGiverDef`. Keying one tag per name silently loses one of them.
    """
    declared = {}
    for path in mod_xml_files():
        if os.sep + "Languages" + os.sep in path or os.sep + "About" + os.sep in path:
            continue
        root = parse(path, problems)
        if root is None:
            continue
        for node in root.iter():
            name = node.find("defName")
            if name is not None and name.text:
                declared.setdefault(name.text.strip(), set()).add(node.tag)
            abstract = node.get("Name")
            if abstract:
                declared.setdefault(abstract.strip(), set()).add(node.tag)
    return declared


def check_def_references(problems, declared):
    for path in mod_xml_files():
        if os.sep + "About" + os.sep in path:
            continue
        # Comments name files and defs that were deliberately moved elsewhere, so
        # scanning them reports prose as a broken reference.
        text = COMMENT.sub(" ", read_text(path))
        for token in sorted(set(RR_TOKEN.findall(text))):
            if token in declared:
                continue
            # Keyed strings and DefInjected suffixes are owned by check-keyed-strings.py.
            if os.sep + "Languages" + os.sep in path:
                continue
            fail(problems, "%s references %s, which this package does not declare"
                 % (rel(path), token))


# --------------------------------------------------------------------------- #
# 5. Patch targets
# --------------------------------------------------------------------------- #

def check_comment_dashes(problems):
    """XML comments may not contain a double hyphen, and this keeps biting.

    The parser reports it as a generic "not well-formed (invalid token)" at a column, which
    tells you nothing about the actual rule. Prose in these files naturally wants an em-dash
    typed as `--`, so this is a trap the next person walks into too. Named explicitly here.
    """
    for path in mod_xml_files():
        text = read_text(path)
        for match in re.finditer(r"<!--(.*?)(?:-->|$)", text, re.S):
            if "--" in match.group(1):
                line = text[: match.start()].count(chr(10)) + 1
                fail(problems, "%s line %d: an XML comment contains '--', which is not legal "
                               "inside a comment. Use an em-dash or rephrase."
                     % (rel(path), line))


def check_class_references(problems):
    """Every RimroomsAsyncIndustries type named in XML must exist in the source.

    A def naming a class that is not there fails at load with a red error, and nothing was
    checking it. `workerClass`, `compClass`, `giverClass`, `thingClass`, `driverClass` and
    `Class="..."` attributes all reach the same reflection lookup, so all of them are read
    here rather than a list of the ones that have bitten so far.

    Matched against declared type names in the C# source rather than by reflecting over the
    built assembly, so the check is honest even when the DLL is stale.
    """
    declared_types = set()
    for path in glob.glob(os.path.join(REPO, "src", "**", "*.cs"), recursive=True):
        if os.sep + "obj" + os.sep in path or os.sep + "bin" + os.sep in path:
            continue
        text = read_text(path)
        for name in re.findall(r"\b(?:class|struct|enum|interface)\s+([A-Za-z_][A-Za-z0-9_]*)", text):
            declared_types.add(name)

    referenced = set()
    for path in mod_xml_files():
        text = COMMENT.sub(" ", read_text(path))
        for value in re.findall(r"<\w*[Cc]lass>([^<]+)</\w*[Cc]lass>", text):
            referenced.add(value.strip())
        for value in re.findall(r'Class="([^"]+)"', text):
            referenced.add(value.strip())

    for value in sorted(referenced):
        if not value.startswith("RimroomsAsyncIndustries"):
            continue                      # Core and DLC types; not ours to verify from source.
        simple = value.split(".")[-1]
        if simple not in declared_types:
            fail(problems, "a def names %s, which no C# source file declares" % value)


def check_patches(problems, declared, game_defs):
    patch_dir = os.path.join(MOD, "*", "Patches", "*.xml")
    for path in sorted(glob.glob(patch_dir)):
        root = parse(path, problems)
        if root is None:
            continue
        found_any = False
        for xpath_node in root.iter("xpath"):
            found_any = True
            xpath = (xpath_node.text or "").strip()
            targets = XPATH_DEFNAME.findall(xpath)
            if not targets:
                fail(problems, "%s has an xpath selecting no named def, so what it "
                               "patches cannot be verified: %s" % (rel(path), xpath))
                continue
            for target in targets:
                if target in declared:
                    continue
                if game_defs is None:
                    continue
                if target not in game_defs:
                    fail(problems, "%s patches %r, which exists neither in the game's "
                                   "Data nor in this package" % (rel(path), target))
        if not found_any:
            fail(problems, "%s is in Patches/ but contains no xpath" % rel(path))


# --------------------------------------------------------------------------- #
# 6 + 7. Textures and sounds
# --------------------------------------------------------------------------- #

def check_textures(problems, notes):
    referenced = set()
    unverifiable = set()
    for path in mod_xml_files():
        text = read_text(path)
        for tag in ("texPath", "uiIconPath", "iconPath", "symbol"):
            for value in re.findall(r"<%s>([^<]+)</%s>" % (tag, tag), text):
                value = value.strip()
                if "RR_" in value:
                    referenced.add(value)
                else:
                    unverifiable.add(value)

    on_disk = set()
    for path in glob.glob(os.path.join(MOD, "*", "Textures", "**", "*.png"), recursive=True):
        parts = os.path.relpath(path, MOD).replace(os.sep, "/").split("/")
        on_disk.add("/".join(parts[2:])[: -len(".png")])

    for value in sorted(referenced):
        if value not in on_disk:
            fail(problems, "texture path %r is referenced but no matching .png ships" % value)

    for value in sorted(on_disk):
        if value not in referenced:
            notes.append("texture ships but nothing references it: %s.png" % value)

    if unverifiable:
        notes.append("%d non-RR texture path(s) point at game assets and cannot be "
                     "checked from disk; they live in asset bundles, not Data/"
                     % len(unverifiable))


def check_sounds(problems, declared):
    sound_defs = set(name for name, tags in declared.items() if "SoundDef" in tags)
    for path in mod_xml_files():
        if os.sep + "SoundDefs" + os.sep in path:
            continue
        text = read_text(path)
        for tag in ("soundDef", "soundDoor", "soundInteract", "soundClose", "soundOpen"):
            for value in re.findall(r"<%s>([^<]+)</%s>" % (tag, tag), text):
                value = value.strip()
                if value.startswith("RR_") and value not in sound_defs:
                    fail(problems, "%s references sound %r, which this package does not "
                                   "declare as a SoundDef" % (rel(path), value))


# --------------------------------------------------------------------------- #
# 8. DefInjected
# --------------------------------------------------------------------------- #

def check_definjected(problems, declared):
    pattern = os.path.join(MOD, "*", "Languages", "*", "DefInjected", "*", "*.xml")
    for path in sorted(glob.glob(pattern)):
        folder_type = os.path.basename(os.path.dirname(path))
        root = parse(path, problems)
        if root is None:
            continue
        for node in list(root):
            key = node.tag
            def_name = key.split(".")[0]
            if def_name not in declared:
                fail(problems, "%s injects into %r, which this package does not declare"
                     % (rel(path), def_name))
                continue
            actual = declared[def_name]
            if folder_type not in actual:
                fail(problems, "%s sits in DefInjected/%s but %r is declared only as %s"
                     % (rel(path), folder_type, def_name, "/".join(sorted(actual))))


# --------------------------------------------------------------------------- #

def main():
    problems = []
    notes = []

    if not os.path.isdir(MOD):
        sys.stderr.write("package-integrity: mod folder not found at %s\n" % MOD)
        return 2

    allowlist = json.loads(read_text(ALLOWLIST))

    versions = []
    if os.path.isfile(ABOUT):
        root = ET.parse(ABOUT).getroot()
        node = root.find("supportedVersions")
        if node is not None:
            versions = [(item.text or "").strip() for item in node.findall("li")]

    game_defs = index_game_defs()
    if game_defs is None:
        notes.append("game Data folder not found, so patch targets were not resolved "
                     "against it; that part is skipped, not passed")

    declared = collect_declared(problems)

    check_metadata(problems, allowlist, versions)
    check_no_attribution(problems)
    check_files(problems, allowlist, versions)
    check_comment_dashes(problems)
    check_def_references(problems, declared)
    check_class_references(problems)
    check_patches(problems, declared, game_defs)
    check_textures(problems, notes)
    check_sounds(problems, declared)
    check_definjected(problems, declared)

    print("package-integrity")
    print("  defs declared:      %d" % len(declared))
    print("  package files:      %d" % len(allowlist.get("files", [])))
    print("  supported versions: %s" % (", ".join(versions) or "none"))
    print("  game defs indexed:  %s" % ("%d" % len(game_defs) if game_defs else "skipped"))

    for note in notes:
        print("  note: %s" % note)

    if problems:
        print("")
        print("FAIL: %d problem(s)" % len(problems))
        for problem in problems:
            print("  - %s" % problem)
        return 1

    print("")
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
