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
   def this package declares, or a keyed string it declares -- a def may legitimately name a
   keyed letter label or body. This is what catches a rename that updated the declaration
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
10. **The staged copy is this build.** The version in RimSort's local mods folder must match
   the version just built, because **that is the copy a launch actually loads.** Caught at
   0.12.99-dev with the staged copy a whole version behind, minutes before a launch: staging
   was in neither publication procedure, so it had been skipped batch after batch while every
   instrument stayed green. A stale staged copy sends the owner to report defects that were
   already fixed, and nothing downstream can tell -- the log is a true record of the wrong code.
   Skipped with a note where RimSort is not installed.

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
import struct
import sys
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries")
ABOUT = os.path.join(MOD, "About", "About.xml")
ALLOWLIST = os.path.join(REPO, "tools", "package-files.json")
CSPROJ = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "RimroomsAsyncIndustries.csproj")
GAME_DATA = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data"

# The owner's 294-entry profile as it is actually installed. Used only to verify an **optional**
# compatibility patch target, never to resolve anything this package needs: nothing here is a
# dependency and the absence of this folder changes no verdict about the package itself.
WORKSHOP = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\294100"

DEFNAME_TAG = re.compile(r"<defName>([^<]+)</defName>")
GAME_MANAGED = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed"

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
# An abstract inheritance parent, addressed by its Name attribute. Verified against
# the game's own abstract defs, so a patch on a parent that does not exist still fails.
XPATH_ABSTRACT = re.compile(r"@Name\s*=\s*[\"']([^\"']+)[\"']")


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


def strings_heap(path):
    """Every name in one managed assembly's CLI metadata `#Strings` heap.

    Read straight from the PE: section table -> CLI header -> metadata root -> stream headers.
    No reflection and no DLL load, so it works off any copy of the game on any platform and
    cannot execute anything it reads.

    Returned as the raw blob rather than a set of entries, because the heap permits SUFFIX
    SHARING: a name may be stored only as the tail of a longer one and referenced by pointing
    partway into it. `Building` is exactly that, so splitting on NUL finds every obvious name
    and silently misses real types -- the first draft of this check failed
    `<thingClass>Building</thingClass>`, which is correct code. Membership is therefore a
    search for `name + NUL`, which finds whole entries and shared suffixes alike.

    The heap holds every metadata name -- types, fields, methods, parameters -- so a hit proves
    a name EXISTS somewhere in the assembly rather than proving it is a type. That makes this an
    over-approximation: it can let an unusual mis-spelling through, and it can never reject a
    name that really is there. Deliberate in that direction, because a check that rejects
    correct code gets deleted and a check that is merely generous keeps catching this.
    """
    try:
        data = io.open(path, "rb").read()
    except IOError:
        return None
    try:
        pe = struct.unpack_from("<I", data, 0x3C)[0]
        if data[pe:pe + 4] != b"PE\0\0":
            return None
        coff = pe + 4
        section_count = struct.unpack_from("<H", data, coff + 2)[0]
        optional_size = struct.unpack_from("<H", data, coff + 16)[0]
        optional = coff + 20
        magic = struct.unpack_from("<H", data, optional)[0]
        directories = optional + (96 if magic == 0x10B else 112)
        cli_rva = struct.unpack_from("<I", data, directories + 14 * 8)[0]

        sections = []
        table = optional + optional_size
        for index in range(section_count):
            base = table + index * 40
            virtual_size, virtual_address, _, raw = struct.unpack_from("<IIII", data, base + 8)
            sections.append((virtual_address, max(virtual_size, 1), raw))

        def file_offset(rva):
            for virtual_address, virtual_size, raw in sections:
                if virtual_address <= rva < virtual_address + virtual_size:
                    return raw + (rva - virtual_address)
            return None

        cli = file_offset(cli_rva)
        if cli is None:
            return None
        metadata = file_offset(struct.unpack_from("<I", data, cli + 8)[0])
        if metadata is None or data[metadata:metadata + 4] != b"BSJB":
            return None
        version_length = struct.unpack_from("<I", data, metadata + 12)[0]
        cursor = metadata + 16 + version_length + ((-version_length) % 4) + 2
        stream_count = struct.unpack_from("<H", data, cursor)[0]
        cursor += 2
        for index in range(stream_count):
            offset, size = struct.unpack_from("<II", data, cursor)
            cursor += 8
            end = data.index(b"\0", cursor)
            name = data[cursor:end].decode("ascii", "replace")
            cursor = end + 1
            cursor += (-(cursor - metadata)) % 4
            if name == "#Strings":
                return data[metadata + offset:metadata + offset + size]
    except (struct.error, ValueError, IndexError):
        return None
    return None


def index_game_type_names():
    """Type names the installed game can resolve: Core plus every installed DLC.

    DLC code lives in `Data/<Dlc>/Assemblies`, so a def naming an Anomaly or Odyssey type
    resolves here exactly as the game resolves it -- and if the DLC is absent, so is the name,
    which is the honest answer rather than a pass.

    Returns the concatenated `#Strings` heaps. Ask it a question with `type_name_exists`.
    """
    paths = []
    for name in ("Assembly-CSharp.dll", "Assembly-CSharp-firstpass.dll"):
        paths.append(os.path.join(GAME_MANAGED, name))
    paths += sorted(glob.glob(os.path.join(GAME_DATA, "*", "Assemblies", "*.dll")))

    blobs = []
    for path in paths:
        found = strings_heap(path)
        if found:
            blobs.append(found)
    return b"\0".join(blobs) or None


def type_name_exists(heaps, simple):
    """Whether the installed game holds a metadata name equal to `simple`.

    `name + NUL` rather than equality against split entries, so a suffix-shared name such as
    `Building` resolves. See `strings_heap` for why that matters.
    """
    try:
        needle = simple.encode("utf-8") + b"\0"
    except UnicodeEncodeError:
        return False
    return needle in heaps


def index_game_defs():
    """Every def name the installed game ships, Core and DLC alike.

    Two kinds of name, because patches legitimately target both:

      * `defName` -- a concrete def.
      * the `Name` attribute of an **abstract** def, which is an inheritance parent rather than a
        def the game instantiates. Patching one is the only way to reach a property of every
        building in the game at once, including buildings belonging to mods this project has never
        seen. Until 0.12.27-dev this indexer knew nothing about them, so **every patch on an
        abstract parent was unverifiable and therefore refused** -- which ruled the technique out
        rather than checking it.

    An abstract name is indexed only when the def really declares itself abstract. A `Name` on a
    concrete def is an alias, and matching one would prove nothing about what a patch reaches.
    """
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
        for node in root.iter():
            name = node.get("Name")
            if name and (node.get("Abstract") or "").strip().lower() == "true":
                names[name.strip()] = True
    return names


def mod_xml_files():
    return sorted(glob.glob(os.path.join(MOD, "**", "*.xml"), recursive=True))


def source_cs_files():
    """Hand-written C# only. Anything under obj/ or bin/ is generated by the build and
    would otherwise reappear in the results the moment somebody compiles."""
    found = glob.glob(os.path.join(REPO, "src", "**", "*.cs"), recursive=True)
    return sorted(
        path for path in found
        if os.sep + "obj" + os.sep not in path and os.sep + "bin" + os.sep not in path
    )


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


def collect_keyed(problems):
    """Every keyed string name the package declares.

    Needed because a def may legitimately *name a keyed string* -- a letter label, a letter
    body -- and those are not defs. Without this, every such reference reads as a broken def
    reference, which is a false failure that would push somebody toward "fixing" a correct
    package.
    """
    keys = set()
    pattern = os.path.join(MOD, "*", "Languages", "*", "Keyed", "*.xml")
    for path in sorted(glob.glob(pattern)):
        root = parse(path, problems)
        if root is None:
            continue
        for node in list(root):
            if node.tag:
                keys.add(node.tag)
    return keys


def check_def_references(problems, declared, keyed):
    for path in mod_xml_files():
        if os.sep + "About" + os.sep in path:
            continue
        # Comments name files and defs that were deliberately moved elsewhere, so
        # scanning them reports prose as a broken reference.
        text = COMMENT.sub(" ", read_text(path))
        for token in sorted(set(RR_TOKEN.findall(text))):
            if token in declared or token in keyed:
                continue
            # A capability is neither a def nor a keyed string: it is an internal name a
            # project grants and a source file asks for. proof-research-branches.py asserts
            # both directions of that relationship, including the case this checker cannot
            # see -- a capability granted that no code reads.
            if token.startswith("RR_Cap_"):
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


def check_class_references(problems, notes):
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

    game_types = index_game_type_names()
    if game_types is None:
        notes.append("game assemblies not found, so Core and DLC type names in defs were not "
                     "resolved; that part is skipped, not passed")

    for value, reason in unresolved_class_names(referenced, declared_types, game_types):
        fail(problems, "a def names %s, %s" % (value, reason))


def unresolved_class_names(referenced, declared_types, game_types):
    """The type names in `referenced` the game will not be able to resolve, with the reason.

    A PURE FUNCTION ON PURPOSE, AND THIS IS THE LESSON OF THE SEVENTH LAUNCH TWICE OVER.

    The first lesson was the defect: `<li Class="CompProperties_Colorable" />` names a type that
    does not exist, and a `Class` the game cannot resolve throws out of `DirectXmlToObjectNew`,
    which discards the WHOLE ThingDef rather than the one node. `Door` and `Autodoor` left the
    game and 587 red lines followed from one line.

    The second lesson was how nearly the fix shipped unguarded. A plant that restored the old
    exemption as `if True: continue` walked past the proof, because the proof asserted that a
    COMMENT was absent rather than that a bad name is reported. So the verdict lives here, where
    a proof can hand it a crafted set of names and demand the right answer -- blinding it,
    exempting it or short-circuiting it all change the OUTPUT, which is the only thing the proof
    now accepts as evidence.

    Ours are matched against declared type names in the C# source rather than by reflecting over
    the built assembly, so that half stays honest even when the DLL is stale. Core and DLC names
    are matched against the installed game's own metadata, because a Core-shaped typo is the
    likeliest typo there is and taking those on trust was the wrong half to trust.
    """
    verdicts = []
    for value in sorted(referenced):
        simple = value.split(".")[-1]
        if value.startswith("RimroomsAsyncIndustries"):
            if simple not in declared_types:
                verdicts.append((value, "which no C# source file declares"))
            continue
        if game_types is None:
            continue
        if not type_name_exists(game_types, simple):
            verdicts.append((value, "and no type of that name exists in the installed game's "
                                    "assemblies. A Class the game cannot resolve discards the "
                                    "entire def being parsed, not just that one node"))
    return verdicts


def optional_compat_xpaths(root):
    """Every <xpath> that sits inside a PatchOperationFindMod.

    Such an operation applies only when the named mod is installed, so its target def
    legitimately does not exist in Core, in a DLC, or in this package. Demanding that it
    resolve would make supporting another mod impossible -- but the exemption is deliberately
    narrow: it is granted by being wrapped in FindMod, not by the def merely being unknown.
    """
    exempt = set()
    for node in root.iter():
        if node.get("Class") != "PatchOperationFindMod":
            continue
        for xpath_node in node.iter("xpath"):
            exempt.add(id(xpath_node))
    return exempt


def remedy():
    """The fix, and whether the operator can perform it right now.

    **Staging refuses while RimWorld is open and it is right to**, so a reader seeing this failure
    needs to know whether they are one command away or two. Said rather than left to be discovered:
    the stager's own refusal is `Close RimWorld before staging a new DLL`, and a guard that demands
    an action the operator cannot currently take without saying so is a guard people learn to
    ignore.
    """
    running = False
    try:
        import subprocess
        output = subprocess.run(["tasklist", "/FI", "IMAGENAME eq RimWorldWin64.exe"],
                                capture_output=True, text=True, timeout=20).stdout
        running = "RimWorldWin64" in output
    except Exception:
        pass
    if running:
        return (" RIMWORLD IS RUNNING, and the stager refuses while it is -- close the game first, "
                "then run `powershell -File tools/stage-mod.ps1 -UpdateExisting`. Until then the "
                "running game is loading the previous build.")
    return " Run `powershell -File tools/stage-mod.ps1 -UpdateExisting`."


def _file_sha256(path):
    """A file's SHA256, read in chunks so a 20 MB texture is not held in memory."""
    import hashlib
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_staged_copy_is_current(problems, notes):
    """The copy the owner launches must be the build that was just made.

    **Caught at 0.12.99-dev minutes before a launch: the staged copy was `0.12.98-dev` while the
    build was `0.12.99-dev`.** `tools/stage-mod.ps1` was in neither the publication sequence in
    `NOW.md` nor the one-screen version in `PUBLISHING.md`, so it was simply skipped, batch after
    batch, while every instrument stayed green and every ref stayed level.

    **A stale staged copy is the most expensive failure in this project's whole loop.** The owner
    launches, meets a defect that was fixed two versions ago, and spends their session reporting
    it. Nothing downstream can detect that -- the log is from a real launch of a real build, and
    every word in it is true about the wrong code.

    Degrades rather than failing where RimSort is not installed: the path is read from RimSort's
    own `settings.json` and the whole check is skipped with a note when that is absent, because a
    rule that fails on somebody else's machine for a reason that is not a defect is a rule people
    switch off.
    """
    settings = os.path.join(os.environ.get("LOCALAPPDATA", ""), "RimSort", "settings.json")
    if not os.path.isfile(settings):
        notes.append("RimSort settings not present; the staged copy is unchecked rather than "
                     "confirmed current")
        return
    try:
        data = json.loads(io.open(settings, encoding="utf-8-sig").read())
        instance = data["instances"][data["current_instance"]]
        local = instance.get("local_folder") or ""
    except (ValueError, KeyError, TypeError, OSError):
        notes.append("RimSort settings could not be read; the staged copy is unchecked rather "
                     "than confirmed current")
        return
    staged = os.path.join(local, "Rimrooms - Async Industries", "About", "About.xml")
    if not local or not os.path.isfile(staged):
        notes.append("no staged copy in the RimSort local mods folder; nothing to compare")
        return
    built = read_text(os.path.join(MOD, "About", "About.xml"))
    live = read_text(staged)
    want = re.search(r"<modVersion>([^<]+)</modVersion>", built)
    have = re.search(r"<modVersion>([^<]+)</modVersion>", live)
    if want is None or have is None:
        fail(problems, "a modVersion could not be read from the built or the staged About.xml")
        return
    # **COMPARING VERSIONS ALONE WAS NOT ENOUGH, and this guard's own first run proved it.**
    # A fix landed without a version bump -- the same 0.12.99-dev -- so the version matched while
    # the staged assembly was the previous build. The check reported the staged copy current and it
    # was not. **The version is a label; the bytes are the thing that runs.**
    #
    # So every staged file is compared by content against the package that was just built. Cheap:
    # 103 files, and it is the difference between knowing and assuming.
    root = os.path.dirname(os.path.dirname(staged))
    stale = []
    missing = []
    for base, _, names in os.walk(MOD):
        for name in names:
            source = os.path.join(base, name)
            relative = os.path.relpath(source, MOD)
            mirror = os.path.join(root, relative)
            if not os.path.isfile(mirror):
                missing.append(relative.replace(os.sep, "/"))
            elif _file_sha256(source) != _file_sha256(mirror):
                stale.append(relative.replace(os.sep, "/"))
    if missing or stale:
        fail(problems,
             "THE STAGED COPY IS NOT THIS BUILD: %d file(s) differ and %d are absent, even though "
             "both declare %r. The version is a label; the bytes are what runs, so a fix without a "
             "version bump would otherwise stage as current. First differing: %s.%s"
             % (len(stale), len(missing), want.group(1).strip(),
                ", ".join((stale + missing)[:4]), remedy()))
        return
    if want.group(1).strip() != have.group(1).strip():
        fail(problems,
             "THE STAGED COPY IS NOT THIS BUILD: the game's Mods folder holds %r and the build is "
             "%r. That is the copy a launch actually loads, so the next Player.log would describe "
             "code that is already superseded. Run "
             "`powershell -File tools/stage-mod.ps1 -UpdateExisting`."
             % (have.group(1).strip(), want.group(1).strip()))
    else:
        notes.append("staged copy matches the build at %s, every file compared by content"
                     % want.group(1).strip())


def profile_defs():
    """Every defName declared by the installed profile mods, or None if they are unreachable.

    **Why this exists.** An optional compatibility patch target was reported as *"not installed
    here and cannot be verified"* seven times -- every one of them a `PH_` door from **Doors
    Expanded**. Both that mod (profile row 77, `jecrell.doorsexpanded`) and **ReBuild: Doors and
    Corners** (row 185) declare those defs, **both are in the owner's 294-entry profile, and both
    are installed on this machine.** So the seven were verifiable all along and the checker simply
    was not looking anywhere a profile mod lives.

    That matters because a renamed target is a **silent** compatibility break: the patch applies
    to nothing and the gate console never appears on the door. A note saying it cannot be checked
    reads as *checked and fine* after the third time somebody sees it.

    **Returns None rather than an empty set when the library is not reachable**, so a machine
    without the Steam workshop folder degrades to exactly the old behaviour -- seven notes -- and
    never to a silent pass. An absence rule over an empty set is satisfied by construction, which
    is this repository's most repeated finding about its own instruments.
    """
    if not os.path.isdir(WORKSHOP):
        return None
    names = set()
    for path in glob.iglob(os.path.join(WORKSHOP, "*", "**", "*.xml"), recursive=True):
        try:
            text = io.open(path, encoding="utf-8-sig", errors="replace").read()
        except OSError:
            continue
        if "<defName>" not in text:
            continue
        for name in DEFNAME_TAG.findall(text):
            names.add(name.strip())
    return names or None


def check_patches(problems, declared, game_defs, notes):
    # Read once for the whole sweep: the library is thousands of files and the answer is the
    # same for every patch in the package.
    installed = profile_defs()
    verified = 0
    patch_dir = os.path.join(MOD, "*", "Patches", "*.xml")
    for path in sorted(glob.glob(patch_dir)):
        root = parse(path, problems)
        if root is None:
            continue
        exempt = optional_compat_xpaths(root)
        found_any = False
        for xpath_node in root.iter("xpath"):
            found_any = True
            xpath = (xpath_node.text or "").strip()
            targets = XPATH_DEFNAME.findall(xpath) + XPATH_ABSTRACT.findall(xpath)
            if not targets:
                fail(problems, "%s has an xpath selecting no named def, so what it "
                               "patches cannot be verified: %s" % (rel(path), xpath))
                continue
            optional = id(xpath_node) in exempt
            for target in targets:
                if target in declared:
                    continue
                if game_defs is None:
                    continue
                if target not in game_defs:
                    if not optional:
                        fail(problems, "%s patches %r, which exists neither in the game's "
                                       "Data nor in this package" % (rel(path), target))
                    elif installed is None:
                        notes.append("optional compatibility patch targets %r; the mod library "
                                     "is not reachable from here, so it cannot be verified"
                                     % target)
                    elif target in installed:
                        # Verified against the profile mod's own defs on disk, which is what the
                        # patch's own comment says the names were read from in the first place.
                        verified += 1
                    else:
                        # **A FAILURE, not a note.** The library IS reachable and the target is
                        # in none of it, so this is the silent break rather than the unknown:
                        # the patch would apply to nothing and the gate console would never
                        # appear on that door, with no error anywhere to say so.
                        fail(problems, "%s patches %r as optional compatibility, and no "
                                       "installed profile mod declares it. An optional patch "
                                       "whose target has been renamed applies to nothing and "
                                       "reports nothing -- read the mod's current defs and "
                                       "update the xpath, or drop the target" % (rel(path), target))
        if not found_any:
            fail(problems, "%s is in Patches/ but contains no xpath" % rel(path))
    if installed is None:
        notes.append("mod library not reachable; optional compatibility targets are unverified "
                     "rather than passed")
    else:
        notes.append("optional compatibility patch targets verified against the installed "
                     "profile mods: %d" % verified)


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

    # C# asks for textures too, and until 0.9.0-dev this check could not see it. Retiring
    # the legacy gate buildings deleted four textures that C# still named on a dead branch,
    # and the checker passed clean: it only ever looked at XML, and only ever checked the
    # "ships but unreferenced" direction from disk. A reference to a texture that does not
    # ship is the more serious of the two, because ContentFinder reports a missing path at
    # runtime, so it is checked in both directions now and from both kinds of source.
    scanned_folders = set()
    for path in source_cs_files():
        text = read_text(path)
        for value in re.findall(r"""ContentFinder<\s*Texture2D\s*>\s*\.\s*Get\s*\(\s*["']([^"']+)["']""", text):
            value = value.strip()
            if "RR_" in value:
                referenced.add(value)
            else:
                unverifiable.add(value)
        # GetAllInFolder references a WHOLE FOLDER, not one path, and this checker could not see
        # that. Both menu slides have been reported as "ships but nothing references it" for
        # every run since they were added -- the old code named them in a string array and then
        # called Get(variable), which this regex cannot follow either. A note nobody can act on
        # is noise, and noise is how a real finding gets scrolled past.
        #
        # This is not a widening. GetAllInFolder genuinely loads every image under the folder, so
        # treating them as referenced is what the API actually does. The "reference that does not
        # ship" direction is untouched and is still the more serious of the two.
        for value in re.findall(
                r"""ContentFinder<\s*Texture2D\s*>\s*\.\s*GetAllInFolder\s*\(\s*(\w+|["'][^"']+["'])""",
                text):
            token = value.strip()
            if token.startswith('"') or token.startswith("'"):
                folder = token.strip("\"'")
            else:
                # A bare identifier. Resolve the const it names, in this same file, or give up --
                # guessing a folder would be worse than reporting nothing.
                match = re.search(
                    r"""const\s+string\s+%s\s*=\s*["']([^"']+)["']""" % re.escape(token), text)
                folder = match.group(1) if match else None
            if folder:
                scanned_folders.add(folder.strip("/"))

    on_disk = set()
    for path in glob.glob(os.path.join(MOD, "*", "Textures", "**", "*.png"), recursive=True):
        parts = os.path.relpath(path, MOD).replace(os.sep, "/").split("/")
        on_disk.add("/".join(parts[2:])[: -len(".png")])

    for value in sorted(referenced):
        if value not in on_disk:
            fail(problems, "texture path %r is referenced but no matching .png ships" % value)

    for value in sorted(on_disk):
        if value in referenced:
            continue
        # A texture inside a folder some source scans with GetAllInFolder IS referenced, by the
        # folder rather than by name. That is the whole point of scanning: art can be added by
        # dropping a file in.
        if any(value.startswith(folder + "/") for folder in scanned_folders):
            continue
        notes.append("texture ships but nothing references it: %s.png" % value)

    if scanned_folders:
        for folder in sorted(scanned_folders):
            count = len([v for v in on_disk if v.startswith(folder + "/")])
            notes.append("folder scanned by GetAllInFolder, %d texture(s) covered: %s"
                         % (count, folder))

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
    keyed = collect_keyed(problems)
    check_def_references(problems, declared, keyed)
    check_class_references(problems, notes)
    check_patches(problems, declared, game_defs, notes)
    check_textures(problems, notes)
    check_staged_copy_is_current(problems, notes)
    check_sounds(problems, declared)
    check_definjected(problems, declared)

    print("package-integrity")
    print("  defs declared:      %d" % len(declared))
    print("  package files:      %d" % len(allowlist.get("files", [])))
    print("  supported versions: %s" % (", ".join(versions) or "none"))
    print("  game defs indexed:  %s" % ("%d" % len(game_defs) if game_defs else "skipped"))
    _heaps = index_game_type_names()
    print("  game name heap:     %s" % ("%d bytes" % len(_heaps) if _heaps else "skipped"))

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
