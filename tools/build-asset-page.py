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

# **ONE FULL TABLE, NOT SIX GROUPED ONES, AND THE MOD LIST ALREADY LEARNED THIS LESSON.**
#
# Owner direction, 2026-10-06, verbatim: *"there is a asset gallery organizable just like the mod
# registry with their images listing there details"*. The register page had been five grouped tables
# and the owner's words then were *"this is not correct in the wiki and not the full 296 mods"* --
# grouping without one complete list hides the thing a reader came for.
#
# It is also what makes the page *organizable* at all: `render-wiki-html.py` attaches its search box
# and sortable headings to **any table with at least twenty body rows**, by size rather than by a
# flag. Six tables of twelve, thirty-four, six, one and seventeen rows got the tooling on exactly
# one of them. One table of sixty-nine gets it on the whole gallery, and the `Kind` column below
# does the grouping's job without costing the full list.
GROUPS = [
    ("Main menu backgrounds", "1.6/Textures/UI/"),
    ("Buildings", "1.6/Textures/Things/Building/"),
    ("Items", "1.6/Textures/Things/Item/"),
    ("Creatures", "1.6/Textures/Things/Pawn/"),
    ("Floors", "1.6/Textures/Terrain/"),
    ("Sound cues", "1.6/Sounds/"),
]

# Where the gallery's pictures live, **relative to the page that references them**, with no leading
# `..` -- the rule `export-public-repo.check_images_resolve` enforces on every published page.
#
# ## THE SAME RELATIVE PATH HAS TO RESOLVE FROM TWO DIFFERENT PLACES, AND THE FIRST VERSION ONLY
# ## SERVED ONE OF THEM
#
# Owner, 2026-10-06: *"im not seeing the pictures of the assets in the wiki"*. They were not there to
# see. The published site is **flat** -- `docs/wiki/assets.md` renders to `docs/assets.html` -- so
# `assets/art/gallery/X.png` resolves to `docs/assets/art/gallery/X.png`, which the exporter writes.
# **The repository is nested**, and the same string read from `docs/wiki/assets.md` resolves to
# `docs/wiki/assets/art/gallery/X.png`, which existed nowhere at all.
#
# So the gallery was built for the published site and never for the tree the owner actually reads,
# and every picture on the page was broken in the only place it was being looked at. One relative
# path cannot serve both layouts, so the pictures are written to **both** locations: the exporter
# puts them beside the flat HTML, and `--apply` puts them under `docs/wiki/` for the markdown.
GALLERY_DIRECTORY = "assets/art/gallery"

# The repository-side copy, which is what makes the markdown render on GitHub and in any editor.
REPO_GALLERY = os.path.join(REPO, "docs", "wiki", "assets", "art", "gallery")

# A thumbnail's longest edge, and the size below which the original is simply copied.
#
# **The twelve menu slides are 1672x941 and about 1.6 MB each.** Serving them full size into a
# ninety-six-pixel table cell would make a single page pull twenty megabytes, so those are resampled.
# A 128 or 256 pixel texture is already smaller than the resample target and copying it keeps it
# crisp, which matters more here than anywhere: half these textures are mostly transparent and the
# reader is looking at them to judge the alpha.
THUMB_MAX = 192
COPY_AT_OR_BELOW = 256

# One line per kind, so the summary table says what a category *is* rather than only how big it is.
# Ordered as a reader meets them, not alphabetically. A kind with no assets is not printed, so this
# list can name a category before anything fills it without putting an empty row on the page.
KIND_BLURBS = [
    ("Menu background", "A painting behind the main menu. Twelve, shown in turn."),
    ("Building", "Something the company builds and you can place and rotate."),
    ("Gate frame", "The machine trim a designated door wears, one per supported footprint."),
    ("Animation frame", "One still of a sequence the code plays in order."),
    ("Item", "Something a colonist carries, hauls or reads."),
    ("Floor", "A terrain surface."),
    ("Interface icon", "A picture used by a button or panel rather than placed in the world."),
    ("Creature", "Something that lives out there."),
    ("Sound cue", "A company sound. Mono, 48 kHz, played at the thing that made it."),
    ("Other", "Shipped and not yet categorised, which is a fault worth reporting."),
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
    # **A SoundDef HAS NO LABEL, AND WALKING BACK FOR ONE FINDS SOMEBODY ELSE'S.** The first
    # version reported RR_GateWarning as "starting staff" -- the nearest <label> above the clip
    # path belonged to an unrelated def entirely. A cue is identified by its defName.
    clip = re.search(r"<clipPath>%s</clipPath>" % pattern, defs)
    if clip:
        names = re.findall(r"<defName>([^<]+)</defName>", defs[: clip.start()])
        return names[-1] if names else ""
    block = re.search(r"<(?:texPath|texturePath|uiIconPath)>%s</" % pattern, defs)
    if block:
        # Walk back to the nearest label above the match: that is the thing a player sees.
        before = defs[: block.start()]
        labels = re.findall(r"<label>([^<]+)</label>", before)
        if labels:
            return labels[-1]
    # **A NUMBERED SEQUENCE IS NAMED BY ITS PREFIX, NOT BY EACH FRAME.** The animation code holds
    # one literal -- "Things/.../RR_GateCharge_" -- and appends 01 through 08, which is the only
    # sane way to load a sequence. Matching whole paths alone reported all twenty-two frames as
    # shipped-but-unnamed while the code was drawing every one of them.
    frame = re.match(r"^(?P<stem>.*_)\d{2}$", texture_path)
    if frame and ('"%s"' % frame.group("stem")) in code:
        return "animation frame, drawn in sequence by code"
    if ('"%s"' % texture_path) in code:
        if texture_path == "Things/Building/Rimrooms/RR_MachineGate":
            return "button icon; no longer a buildable"
        if texture_path.startswith("Things/Building/Rimrooms/Gates/RR_GateFrame_"):
            return "cosmetic frame on designated native doors"
        return "graphic loaded by code"
    return ""


def descriptions():
    """What each asset actually depicts, hand-written because nothing can derive it.

    **Owner, 2026-10-06: *"that shit about asseet decriptions needs done and updated in wiki"*.**
    Every other column on the page is read off the package; a description is the one thing a file
    cannot tell you about itself. So it is authored here and merged in, and an asset with no
    description is **reported** rather than silently left blank -- an incomplete page that says it
    is incomplete is honest, and one that quietly shows a dash is not.
    """
    path = os.path.join(REPO, "tools", "asset-descriptions.json")
    if not os.path.isfile(path):
        return {}
    import json
    return json.load(io.open(path, encoding="utf-8")).get("assets", {})


def usages():
    """What a player DOES with each asset, which is a different question from what it depicts.

    **Owner, 2026-10-06: *"im not seeing the pictures of the assets in the wiki with theri right up
    details and how the are used in game play"*.** The page already carried two facts per asset --
    what the drawing shows, and the def that loads it -- and **neither of them is what a player does
    with the thing.** A reader looking at a picture of a sealed box wants to know that you build it
    on a conduit run and flicking it cuts an open connection.

    Authored for the same reason the descriptions are: nothing can derive it. Reported when absent,
    never left as a dash, because a dash on a column the owner asked for looks deliberate.
    """
    path = os.path.join(REPO, "tools", "asset-descriptions.json")
    if not os.path.isfile(path):
        return {}
    import json
    return json.load(io.open(path, encoding="utf-8")).get("usage", {})


def master_for(stem):
    # Preserve the original south master for older buildings; newer directional sets have
    # genuinely authored suffixed masters rather than an unsuffixed source that never existed.
    candidates = [stem] + [stem + suffix for suffix in ("_south", "_north", "_east", "_west")]
    sources = {}
    for folder, _subdirs, files in os.walk(SOURCE):
        for name in files:
            sources[os.path.splitext(name)[0]] = os.path.relpath(
                os.path.join(folder, name), REPO).replace(os.sep, "/")
    for candidate in candidates:
        if candidate in sources:
            return sources[candidate]
    return ""


def kind_of(entry):
    """The one-word category the gallery sorts and filters on.

    Derived from where the file sits and what it is named, never hand-listed: a new texture lands in
    the right category by being put in the right folder, which is the same reason the page itself is
    generated. The order of the tests matters -- a gate frame and an animation frame both live under
    `Things/Building/`, and both are more specific than "Building".
    """
    relative = entry["relative"]
    if entry["sound"]:
        return "Sound cue"
    if relative.startswith("1.6/Textures/UI/Menu/"):
        return "Menu background"
    if relative.startswith("1.6/Textures/UI/"):
        return "Interface icon"
    # **AN ICON THAT LIVES AMONG THE BUILDINGS, AND THE FOLDER WOULD HAVE LIED ABOUT IT.**
    # `RR_MachineGate` sits under `Things/Building/` because it once was a buildable and the path
    # never moved. It is now the Set Gate button's picture and **is never placed in the world**, so
    # a `Kind` of "Building" on a published page would invite a reader to look for it in the build
    # menu. The same path is special-cased in `named_by` for the same reason.
    if relative.endswith("/RR_MachineGate.png"):
        return "Interface icon"
    if relative.startswith("1.6/Textures/Terrain/"):
        return "Floor"
    if relative.startswith("1.6/Textures/Things/Item/"):
        return "Item"
    if relative.startswith("1.6/Textures/Things/Pawn/"):
        return "Creature"
    if "/Gates/RR_GateFrame_" in relative:
        return "Gate frame"
    # A two-digit tail is a sequence frame. `stem_of` has already removed any rotation suffix, so
    # nothing here can mistake `_south` for a frame number.
    if re.match(r"^.*_\d{2}$", entry["stem"]):
        return "Animation frame"
    if relative.startswith("1.6/Textures/Things/Building/"):
        return "Building"
    return "Other"


def preview_source(entry):
    """The file a thumbnail is made from, or "" for a cue.

    A rotatable set has three files and one gallery row, so one facing has to represent it.
    **South, because that is the view a building is authored in** -- it is the face a player sees
    when they place one, and `master_for` already prefers the south master for the same reason.
    """
    if entry["sound"]:
        return ""
    for suffix in ("_south", "", "_north", "_east", "_west"):
        candidate = os.path.join(PACKAGE, *(entry["folder"].split("/")[1:]))
        candidate = os.path.join(candidate, entry["stem"] + suffix + ".png")
        if os.path.isfile(candidate):
            return candidate
    return ""


def build():
    defs = def_text()
    code = source_text()
    written = descriptions()
    how_used = usages()
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
            "pixel_sizes": set(),
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
            entry["pixel_sizes"].add((width, height))
            entry["size"] = " / ".join("%d x %d" % dimensions
                                       for dimensions in sorted(entry["pixel_sizes"]))

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
        entry["description"] = written.get(entry["stem"], "")
        entry["usage"] = how_used.get(entry["stem"], "")
        entry["kind"] = kind_of(entry)
        entry["preview_source"] = preview_source(entry)
        out.append(entry)
    return out


def gallery_files(entries):
    """{gallery file name: the package file it is made from}, for every entry with a picture."""
    found = {}
    for entry in entries:
        source = entry.get("preview_source")
        if source:
            found[entry["stem"] + ".png"] = source
    return found


def write_gallery(target_directory, entries=None):
    """Write the gallery's thumbnails into a site directory. Returns (written, resampled, note).

    **Called by `export-public-repo.py` rather than at page-generation time**, because these are
    site bytes and not repository content: the published site is the only place they are served
    from, and the export tree is rebuilt from scratch on every run.

    **Pillow is used where it is present and its absence is reported, never fatal.** The same
    degradation rule the staged-copy check follows: a tool that fails on somebody else's machine for
    a reason that is not a defect is a tool people switch off. Without Pillow the originals are
    copied at full size to the same paths, so the markup, the page and the image-resolve guard are
    identical either way -- only the bytes differ, and the note says which happened.
    """
    import shutil
    if entries is None:
        entries = build()
    if not os.path.isdir(target_directory):
        os.makedirs(target_directory)
    try:
        from PIL import Image
    except ImportError:
        Image = None
    written = 0
    resampled = 0
    for name, source in sorted(gallery_files(entries).items()):
        destination = os.path.join(target_directory, name)
        width, height = png_size(source)
        if Image is None or max(width, height) <= COPY_AT_OR_BELOW:
            shutil.copyfile(source, destination)
        else:
            picture = Image.open(source)
            # RGBA throughout: most of these are mostly transparent, and flattening one would put a
            # black rectangle on the page where the reader is checking for a clear aperture.
            picture = picture.convert("RGBA")
            picture.thumbnail((THUMB_MAX, THUMB_MAX), Image.LANCZOS)
            picture.save(destination, "PNG", optimize=True)
            resampled += 1
        written += 1
    note = ("Pillow is not installed, so every gallery picture is a full-size copy"
            if Image is None else
            "%d picture(s) resampled to %d px, the rest copied at their own size"
            % (resampled, THUMB_MAX))
    return written, resampled, note


def page(entries):
    textures = [e for e in entries if not e["sound"]]
    sounds = [e for e in entries if e["sound"]]
    total = sum(e["bytes"] for e in entries)
    file_count = len(shipped_assets())

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
    # **FILES AND ENTRIES ARE DIFFERENT NUMBERS AND BOTH ARE STATED.** A rotatable set is three
    # files and one entry, so a single count has to pick one meaning and will be read as the other.
    # `NOW.md` published "59 shipped: 42 drawings" on 2026-10-06 -- 59 was the count of entries with
    # a master, printed as the total. Saying both is what stops that happening again.
    out.append("**%d drawings and %d sound cues — %d entries from %d files, %.0f KB in total.**"
               % (len(textures), len(sounds), len(entries), file_count, total / 1024.0))
    out.append("")
    out.append("This page is generated from the package itself on every build, so it cannot drift "
               "from what actually ships.")
    out.append("")
    out.append("## How to read this page")
    out.append("")
    out.append("**Search the table and sort it by any column.** Click a heading to sort, click it "
               "again to reverse. The search box filters every column at once, so typing *gate* "
               "finds the frames, the animation and the cues together.")
    out.append("")
    out.append("A building that can be rotated needs a separate drawing per direction. The game "
               "mirrors west from east for free; nothing else is free. A rotatable set is **one "
               "row with one picture**, because three facings are one drawing and not three assets.")
    out.append("")
    out.append("**`one frame` identifies a fixed pose or interface icon.** The closed journal and "
               "Set Gate button need one picture; the journal's reading poses and directional "
               "equipment have their own facing sets. Rectangular sets list both pixel sizes "
               "because turning them swaps their width and depth.")
    out.append("")
    out.append("**A sound cue has no picture, so its preview is a dash.** It is in the same table "
               "rather than a separate one, because a reader asking what this mod ships wants one "
               "list.")
    out.append("")
    out.append("**The pictures are checkerboarded behind** on the published site. Most of these "
               "textures are mostly transparent — a gate frame is an outline around a hole — so the "
               "squares are there to show you where the transparency is instead of hiding it "
               "against a flat colour.")
    out.append("")
    out.append("**What it is** describes the drawing. **How you use it** is what a player does with "
               "the thing, which is a different question and used to be missing. **In game** names "
               "the definition or the code that loads the file, so an asset nothing refers to shows "
               "up as a fault rather than hiding.")
    out.append("")

    out.append("## What is in here")
    out.append("")
    out.append("| Kind | How many | What it is |")
    out.append("|---|---|---|")
    for kind, blurb in KIND_BLURBS:
        count = len([e for e in entries if e["kind"] == kind])
        if count:
            out.append("| **%s** | %d | %s |" % (kind, count, blurb))
    out.append("")

    out.append("## The gallery")
    out.append("")
    out.append("| Preview | Asset | Kind | What it is | How you use it | In game | Size | Facings "
               "| Master |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for entry in sorted(entries, key=lambda e: e["stem"].lower()):
        # Facings only mean something for a thing that can be placed and turned. A menu
        # background reading "one frame" invites the reader to wonder which way it faces.
        if entry["sound"] or "/Things/" not in entry["relative"]:
            facings = "—"
        elif entry["facings"]:
            facings = ", ".join(sorted(entry["facings"]))
        else:
            facings = "one frame"
        if entry.get("preview_source"):
            preview = "![%s](%s/%s.png)" % (entry["stem"], GALLERY_DIRECTORY, entry["stem"])
        else:
            preview = "—"
        master = os.path.basename(entry["master"]) if entry["master"] else "—"
        out.append("| %s | **%s** | %s | %s | %s | %s | %s | %s | %s |" % (
            preview, entry["stem"], entry["kind"], entry["description"] or "—",
            entry["usage"] or "—", entry["named_by"] or "—", entry["size"], facings, master))
    out.append("")

    out.append("## Where a master is a dash")
    out.append("")
    masterless = sorted(e["kind"] for e in entries if not e["master"])
    kinds = sorted(set(masterless))
    out.append("Every drawing of a game object is cut from a larger master kept outside the "
               "package, and so is every cue; that master's filename is in the last column.")
    out.append("")
    out.append("**%d of the %d entries have no separate master, and every one of them is a %s.** "
               "There is nothing to cut: a background ships at the size it was drawn."
               % (len(masterless), len(entries),
                  " or ".join(k.lower() for k in kinds) if kinds else "—"))
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
    # **A BLANK DESCRIPTION IS REPORTED, NEVER SHRUGGED OFF.** The owner asked for descriptions on
    # this page; an asset that quietly shows a dash is the page failing at the one job it was asked
    # to do, and a dash looks deliberate.
    undescribed = sorted(e["stem"] for e in entries if not e.get("description"))
    print("  no description    : %d%s"
          % (len(undescribed), (" (%s)" % ", ".join(undescribed[:6])) if undescribed else ""))
    print("  gallery pictures  : %d" % len(gallery_files(entries)))
    # **A KIND OF "Other" IS A FAULT AND IS NAMED HERE.** It means a file landed somewhere
    # `kind_of` does not recognise, and an uncategorised row would still sort and still read as
    # deliberate on the published page.
    uncategorised = sorted(e["stem"] for e in entries if e["kind"] == "Other")
    print("  uncategorised     : %d%s"
          % (len(uncategorised), (" (%s)" % ", ".join(uncategorised)) if uncategorised else ""))
    # **A BLANK USAGE LINE IS REPORTED FOR THE SAME REASON A BLANK DESCRIPTION IS.** The owner asked
    # for *"how the are used in game play"* as a column, so a dash in it is the page failing at a
    # job it was given rather than an asset that happens to have nothing to say.
    unexplained = sorted(e["stem"] for e in entries if not e.get("usage"))
    print("  no usage line     : %d%s"
          % (len(unexplained), (" (%s)" % ", ".join(unexplained[:6])) if unexplained else ""))

    expected = set(gallery_files(entries))

    if "--check" in sys.argv:
        current = io.open(TARGET, encoding="utf-8").read() if os.path.isfile(TARGET) else ""
        if current != body:
            print("")
            print("FAIL: %s is out of date. Run `python tools/build-asset-page.py --apply`."
                  % os.path.relpath(TARGET, REPO).replace(os.sep, "/"))
            return 1
        print("  generated page    : up to date")
        # **AND THE PICTURES THE PAGE POINTS AT MUST BE THERE.** The page passed this check while
        # every image on it was broken in the repository, because the check only ever compared the
        # markdown with itself. A reference to a file that is not there is exactly as wrong as a
        # stale sentence, and it is the fault the owner actually hit.
        present = set(n for n in os.listdir(REPO_GALLERY)
                      if n.lower().endswith(".png")) if os.path.isdir(REPO_GALLERY) else set()
        absent = sorted(expected - present)
        stale = sorted(present - expected)
        if absent or stale:
            print("")
            print("FAIL: the repository gallery does not match the page. %d picture(s) the page "
                  "references are missing and %d picture(s) are left over. Every image on "
                  "docs/wiki/assets.md is broken without them. Run "
                  "`python tools/build-asset-page.py --apply`." % (len(absent), len(stale)))
            for name in (absent + stale)[:6]:
                print("  - %s" % name)
            return 1
        print("  repo gallery      : %d picture(s), matching the page" % len(present))
        return 0

    if "--apply" in sys.argv:
        io.open(TARGET, "w", encoding="utf-8", newline="\n").write(body)
        print("  wrote             : %s" % os.path.relpath(TARGET, REPO).replace(os.sep, "/"))
        # Written beside the markdown as well as into the export, because one relative path has to
        # resolve from a nested page and a flat one. See GALLERY_DIRECTORY.
        if os.path.isdir(REPO_GALLERY):
            for name in sorted(os.listdir(REPO_GALLERY)):
                if name.lower().endswith(".png") and name not in expected:
                    os.remove(os.path.join(REPO_GALLERY, name))
        written, _resampled, note = write_gallery(REPO_GALLERY, entries)
        print("  repo gallery      : %d picture(s) into %s; %s"
              % (written, os.path.relpath(REPO_GALLERY, REPO).replace(os.sep, "/"), note))
    else:
        print("  nothing written; re-run with --apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
