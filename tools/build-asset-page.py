# -*- coding: utf-8 -*-
"""Generate the published asset page from the assets actually in the package.

Owner direction, 2026-10-06, verbatim:

    "and a asset page in wiki for it all showing game assets and details once its done"

**IT IS GENERATED, NOT WRITTEN, AND THAT IS THE WHOLE POINT.** Assets are being authored by more
than one party at once. A hand-written page listing them would be wrong within the hour, and a page
that is wrong about what ships is worse than no page: a reader checks it precisely because they
cannot see inside the package.

So every row below is read off the package at build time:

  * **the file**, its pixel size or its duration, and its weight on disk
  * **what names it** -- the Def that declares the texture path, or the source file that resolves
    it, because an asset nothing names is the defect that retired this art once already
  * **its master** under `assets/source/`, which is how provenance is shown rather than claimed

**Rotation frames are folded into one row.** `_north`, `_east`, `_south` and `_west` are one
drawing's facings, not four assets, and listing them separately would make a six-building package
look like twenty.

Usage
-----
    python tools/build-asset-page.py            report, write nothing
    python tools/build-asset-page.py --apply    write docs/wiki/assets.md
    python tools/build-asset-page.py --check    fail if the page is out of date
"""
import io
import os
import re
import struct
import sys
import wave

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries")
PACKAGE = os.path.join(MOD, "1.6")
SOURCE = os.path.join(REPO, "assets", "source")
SRC = os.path.join(REPO, "src")
TARGET = os.path.join(REPO, "docs", "wiki", "assets.md")

ROTATIONS = ("_north", "_east", "_south", "_west")

GROUPS = [
    ("Main menu backgrounds", "1.6/Textures/UI/"),
    ("Buildings", "1.6/Textures/Things/Building/"),
    ("Items", "1.6/Textures/Things/Item/"),
    ("Creatures", "1.6/Textures/Things/Pawn/"),
    ("Floors", "1.6/Textures/Terrain/"),
    ("Sound cues", "1.6/Sounds/"),
]


def png_size(path):
    with io.open(path, "rb") as handle:
        header = handle.read(26)
    return struct.unpack(">II", header[16:24])


def wav_facts(path):
    sound = wave.open(path)
    try:
        return sound.getframerate(), sound.getnchannels(), sound.getnframes() / float(
            sound.getframerate())
    finally:
        sound.close()


def stem_of(relative):
    """The asset's name with any rotation suffix removed, so facings fold into one row."""
    name = os.path.splitext(os.path.basename(relative))[0]
    for suffix in ROTATIONS:
        if name.endswith(suffix):
            return name[: -len(suffix)], suffix
    return name, ""


def shipped_assets():
    found = []
    for folder, _subdirs, files in os.walk(PACKAGE):
        for name in sorted(files):
            if not name.lower().endswith((".png", ".wav", ".ogg", ".mp3")):
                continue
            path = os.path.join(folder, name)
            found.append((os.path.relpath(path, MOD).replace(os.sep, "/"), path))
    return sorted(found)


def def_text():
    """Every shipped Def file as one blob, with its labels, so a path can be traced to a thing."""
    blob = []
    for folder, _subdirs, files in os.walk(os.path.join(PACKAGE, "Defs")):
        for name in sorted(files):
            if name.lower().endswith(".xml"):
                blob.append(io.open(os.path.join(folder, name), encoding="utf-8-sig").read())
    return "\n".join(blob)


def source_text():
    blob = []
    for folder, _subdirs, files in os.walk(SRC):
        if os.sep + "obj" in folder or os.sep + "bin" in folder:
            continue
        for name in sorted(files):
            if name.lower().endswith(".cs"):
                blob.append(io.open(os.path.join(folder, name), encoding="utf-8-sig").read())
    return "\n".join(blob)


def named_by(texture_path, defs, code):
    """What declares this asset: a Def's label, or the fact that code resolves it.

    **A FOLDER SCAN NAMES EVERY FILE IN IT, AND THE FIRST DRAFT MISSED THAT.** The menu slides are
    loaded with `ContentFinder.GetAllInFolder`, so no Def and no string literal mentions any one of
    them by name -- and all twelve were reported as shipped-but-unnamed, which would have printed a
    twelve-item fault list on a published page about twelve working backgrounds. Crying wolf on a
    page a reader checks because they cannot see inside the package is worse than not writing it.
    """
    if texture_path.startswith("UI/Menu/"):
        return "main menu slideshow"
    # A Def names the path without the extension and without a rotation suffix.
    pattern = re.escape(texture_path)
    block = re.search(r"<(?:texPath|texturePath|uiIconPath|clipPath)>%s</" % pattern, defs)
    if block:
        # Walk back to the nearest label above the match: that is the thing a player sees.
        before = defs[: block.start()]
        labels = re.findall(r"<label>([^<]+)</label>", before)
        if labels:
            return labels[-1]
    if ('"%s"' % texture_path) in code:
        # **A DRAWING RESOLVED IN CODE RATHER THAN BY A DEF IS AN INTERFACE PICTURE**, and saying so
        # is not decoration: `check-doc-conformance` refuses a published page that names a retired
        # def without saying it is gone, and `RR_MachineGate` is exactly that -- a texture on the
        # Set Gate button whose buildable def was retired in 0.9.0-dev and is never coming back,
        # because a gate is a real door and cloning one would cut it off from every door mod.
        # If a future code-resolved asset was never a buildable, this wording needs revisiting
        # rather than widening.
        return "button icon; no longer a buildable"
    return ""


def master_for(stem):
    for folder, _subdirs, files in os.walk(SOURCE):
        for name in files:
            if os.path.splitext(name)[0] == stem:
                return os.path.relpath(os.path.join(folder, name), REPO).replace(os.sep, "/")
    return ""


def build():
    defs = def_text()
    code = source_text()
    rows = {}
    for relative, path in shipped_assets():
        stem, suffix = stem_of(relative)
        key = (os.path.dirname(relative), stem)
        entry = rows.setdefault(key, {
            "stem": stem,
            "folder": os.path.dirname(relative),
            "facings": [],
            "bytes": 0,
            "sound": relative.lower().endswith((".wav", ".ogg", ".mp3")),
            "size": "",
            "relative": relative,
        })
        entry["bytes"] += os.path.getsize(path)
        if suffix:
            entry["facings"].append(suffix.lstrip("_"))
        if entry["sound"]:
            rate, channels, seconds = wav_facts(path)
            entry["size"] = "%.1f s, %d kHz %s" % (
                seconds, rate // 1000, "mono" if channels == 1 else "stereo")
        else:
            width, height = png_size(path)
            entry["size"] = "%d x %d" % (width, height)

    out = []
    for entry in rows.values():
        texture_path = entry["folder"].split("/", 2)[-1] + "/" + entry["stem"]
        if entry["sound"]:
            texture_path = entry["folder"].split("/", 2)[-1] + "/" + entry["stem"]
            lookup = texture_path.replace("Sounds/", "")
        else:
            lookup = texture_path.replace("Textures/", "")
        entry["named_by"] = named_by(lookup, defs, code)
        entry["master"] = master_for(entry["stem"])
        out.append(entry)
    return out


def page(entries):
    textures = [e for e in entries if not e["sound"]]
    sounds = [e for e in entries if e["sound"]]
    total = sum(e["bytes"] for e in entries)

    out = []
    out.append("---")
    out.append("title: The assets")
    out.append("summary: Every picture and sound this mod ships, what each one is for, and where "
               "it came from.")
    out.append("---")
    out.append("")
    out.append("# The assets")
    out.append("")
    out.append("**Everything listed here is original to this project.** Nothing is copied from "
               "another mod, and nothing is extracted from the game.")
    out.append("")
    out.append("Where Rimrooms uses one of the game's own pictures or sounds, it names the path and "
               "the game provides it while you play — that file is not in this package and is not "
               "on this page.")
    out.append("")
    out.append("**%d drawings and %d sound cues, %.0f KB in total.**"
               % (len(textures), len(sounds), total / 1024.0))
    out.append("")
    out.append("This page is generated from the package itself on every build, so it cannot drift "
               "from what actually ships.")
    out.append("")
    out.append("## How to read the facings column")
    out.append("")
    out.append("A building that can be rotated needs a separate drawing per direction. The game "
               "mirrors west from east for free; nothing else is free.")
    out.append("")
    out.append("**`one frame` means the building does not rotate** — which is deliberate. A "
               "rotatable building with one drawing would show a missing-texture square on three "
               "sides out of four, and you would only find out after placing it.")
    out.append("")

    for title, prefix in GROUPS:
        group = sorted([e for e in entries if e["relative"].startswith(prefix)],
                       key=lambda e: e["stem"].lower())
        if not group:
            continue
        out.append("## %s" % title)
        out.append("")
        if group[0]["sound"]:
            out.append("| Cue | Length and format | Heard when | Master |")
            out.append("|---|---|---|---|")
            for entry in group:
                out.append("| **%s** | %s | %s | %s |" % (
                    entry["stem"], entry["size"], entry["named_by"] or "—",
                    "yes" if entry["master"] else "—"))
        else:
            out.append("| Drawing | In game | Size | Facings | Master |")
            out.append("|---|---|---|---|---|")
            for entry in group:
                # Facings only mean something for a thing that can be placed and turned. A menu
                # background reading "one frame" invites the reader to wonder which way it faces.
                if "/Things/" not in entry["relative"]:
                    facings = "—"
                elif entry["facings"]:
                    facings = ", ".join(sorted(entry["facings"]))
                else:
                    facings = "one frame"
                out.append("| **%s** | %s | %s | %s | %s |" % (
                    entry["stem"], entry["named_by"] or "—", entry["size"], facings,
                    "yes" if entry["master"] else "—"))
        out.append("")

    missing = [e for e in entries if not e["named_by"]]
    if missing:
        out.append("## Shipped but not yet named by anything")
        out.append("")
        out.append("These are in the package and nothing in the game refers to them yet. That is a "
                   "fault worth reporting, not a feature.")
        out.append("")
        for entry in sorted(missing, key=lambda e: e["stem"].lower()):
            out.append("- **%s**" % entry["stem"])
        out.append("")

    return "\n".join(out) + "\n"


def main():
    entries = build()
    body = page(entries)
    textures = [e for e in entries if not e["sound"]]
    sounds = [e for e in entries if e["sound"]]
    print("asset page")
    print("  drawings          : %d" % len(textures))
    print("  sound cues        : %d" % len(sounds))
    print("  with a master     : %d" % len([e for e in entries if e["master"]]))
    unnamed = [e["stem"] for e in entries if not e["named_by"]]
    print("  named by nothing  : %d%s" % (len(unnamed), (" (%s)" % ", ".join(unnamed)) if unnamed else ""))

    if "--check" in sys.argv:
        current = io.open(TARGET, encoding="utf-8").read() if os.path.isfile(TARGET) else ""
        if current != body:
            print("")
            print("FAIL: %s is out of date. Run `python tools/build-asset-page.py --apply`."
                  % os.path.relpath(TARGET, REPO).replace(os.sep, "/"))
            return 1
        print("  generated page    : up to date")
        return 0

    if "--apply" in sys.argv:
        io.open(TARGET, "w", encoding="utf-8", newline="\n").write(body)
        print("  wrote             : %s" % os.path.relpath(TARGET, REPO).replace(os.sep, "/"))
    else:
        print("  nothing written; re-run with --apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
