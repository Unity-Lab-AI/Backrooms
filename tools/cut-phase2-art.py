# -*- coding: utf-8 -*-
"""Cut the phase 2 and company-journal masters into textures RimWorld can actually load.

Why this is a tool and not thirteen hand edits
----------------------------------------------
Owner direction, 2026-10-06, verbatim: *"are we making our own items and benches and gates?
becasue if so i fucking love it!"*, answered as a full reversal of the existing-content-only
direction of 2026-09-28, and *"remember things rotate"*.

The thirteen masters under `assets/source/phase2/` are 1254x1254. RimWorld draws roughly 128 px
per tile, so every one of them is about ten times the size it is ever rendered at, and a master
copied into the package instead of cut costs a player VRAM for detail no camera shows.
`check-register-compliance.py` rule 6c refuses a shipped texture over 1024 px on an axis for
exactly that reason.

**A derivation, never a copy.** Re-running this tool reproduces every shipped texture from its
master, so a master can be re-authored and the package re-cut without anybody hand-matching
thirteen crops. The same reason the research mirror is generated rather than maintained.

Three facts the masters do not carry, and what is done about each
----------------------------------------------------------------
1. **A soft drop shadow is not the object.** The first measurement of these masters used a
   zero alpha threshold and reported the field analysis bench as 966x1130 -- taller than wide,
   for a bench that is visibly a long counter. At a real threshold it is **876x396**, an aspect
   of 2.21, and the site fluorescent goes from 1.25 to **4.96**. Footprints are assigned from
   the thresholded box, because the other number is the size of the halo.

2. **Things rotate, and three of four frames are not free.** `Graphic_Multi` resolves `_north`,
   `_east` and `_south`; RimWorld mirrors `_west` from `_east` and nothing else. So a master with
   one frame may ship as `Graphic_Multi` **only** when the object genuinely reads the same from
   every side -- a tripod beacon does, a counter does not. Everything else ships `Graphic_Single`
   and non-rotatable, which is honest and is a shape vanilla uses constantly, and this tool
   prints what would have to be drawn to upgrade it. **A Graphic_Multi with one frame is a
   missing-texture square on three facings**, and a player who never rotates it on placement
   would never find out.

3. **The carpet does not tile.** Measured seam error on the master is 18.3 left/right and 17.8
   top/bottom, where anything over 6 shows a grid. Terrain is drawn once per cell, so that is one
   hard edge per tile across an entire room, and it is invisible until somebody plays. It is made
   seamless by quad mirroring -- the one method available here that is **provably** seamless
   rather than approximately so, since mirrored edges are equal by construction. The cost is
   stated rather than hidden: a quad mirror is symmetric about both axes, which on a fine weave
   reads as texture and on a bold pattern would read as a kaleidoscope. The seam error is
   re-measured after cutting and printed, so the claim is a measurement and not a hope.

Usage
-----
    python tools/cut-phase2-art.py            report what would be cut, write nothing
    python tools/cut-phase2-art.py --apply    cut and write into the package

Authored building rotations use <name>_north.png and <name>_east.png beside the existing
<name>.png south/front master. They are only exported after the shipped graphicData selects
Graphic_Multi. Change that Def and the package allowlist together; this tool does not enable
rotation or ship draft facings for a Graphic_Single. Missing, unreadable or empty active authored
facings refuse the cut before any package texture is written. Icons need no world-space rotation.
The source destinations and integration checklist are in
docs/implementation/AUTHORED_ROTATION_PIPELINE.md.
"""
import io
import os
import sys
import xml.etree.ElementTree as ET

from PIL import Image, ImageChops

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(REPO, "assets", "source", "phase2")
JOURNAL_SOURCE = os.path.join(REPO, "assets", "source", "journal")
TEXTURES = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Textures")

# RimWorld draws about this many pixels per tile. Everything below is a multiple of it.
PIXELS_PER_TILE = 128

# Alpha at or below this is a shadow, a glow or a stray pixel, and is not the object.
ALPHA_FLOOR = 32

# Margin kept inside the texture so an object does not touch its own edge, as a fraction.
BLEED = 0.04

# `single`  -- Graphic_Single, rotatable false. Items, and buildings awaiting authored rotations.
# `uniform` -- Graphic_Multi cut from one master, legitimate only where every side looks alike.
# `flat`    -- Graphic_Multi where `_east` is `_south` turned ninety degrees. **This is geometry,
#              not a fake.** A fixture drawn flat enough to read as seen from above really does
#              turn with its footprint, and its east frame is drawn for the swapped footprint:
#              a 3x1 strip at 384x128 becomes 128x384 facing east. Only legitimate where the
#              master has no perspective to be wrong about -- a strip light does, a generator
#              drawn in three quarter view does not, and turning that one would lay it on its side.
# `terrain` -- tiled, made seamless, no rotation.
# `pawn`    -- a creature presentation, square, no rotation.
#
# `tiles` is the footprint in cells and is assigned from the thresholded aspect, with the reason
# recorded beside it so a later change is an argument rather than a guess.
PLAN = [
    # name,                       kind,      tiles,  strategy,  folder,                     why
    ("RR_MachineGate",            "icon",     (2, 2), "single",  "Things/Building/Rimrooms",
     "a flat Set Gate gizmo icon; not a buildable, so no world-space rotation is required"),
    ("RR_GateConsole",            "building", (1, 1), "single",  "Things/Building/Rimrooms",
     "aspect 0.84, a console with a clearly front face"),
    ("RR_EmergencyCutoff",        "building", (1, 1), "uniform", "Things/Building/Rimrooms",
     "aspect 0.68, a button on a box that reads the same from every side"),
    ("RR_UtilityGenerator",       "building", (2, 2), "single",  "Things/Building/Rimrooms",
     "aspect 0.84, a three quarter view with a distinct front"),
    ("RR_FieldAnalysisBench",     "building", (2, 1), "single",  "Things/Building/Rimrooms",
     "aspect 2.21, a counter with an authored end view for its swapped footprint"),
    ("RR_SiteFluorescent",        "building", (3, 1), "flat",    "Things/Building/Rimrooms",
     "aspect 4.96, a flat strip fitting read from above; its east frame is its south turned"),
    ("RR_ReturnBeacon",           "building", (1, 1), "uniform", "Things/Building/Rimrooms",
     "aspect 0.86, a tripod lamp, radially alike"),
    # **THESE THREE BECAME BUILDINGS ON 2026-10-06** and the kind is corrected with them, because
    # the kind is what puts an entry in ROTATIONS WANTED. Leaving them as `item` would have had the
    # tool report a complete rotation set that does not exist. The owner's fork answer was "Build
    # the three items, hold the Pursuer"; each took a 1x1 minifiable building to get a real job.
    ("RR_FieldRecorder",          "building", (1, 1), "single",  "Things/Item/Rimrooms",
     "aspect 1.39, a desk unit with authored rear vents and an end view"),
    ("RR_SealedEvidenceCase",     "building", (1, 1), "single",  "Things/Item/Rimrooms",
     "aspect 1.59, a latched case with authored hinge-side and end views"),
    ("RR_SurveyTag",              "building", (1, 1), "single",  "Things/Item/Rimrooms",
     "aspect 0.47, a tag with authored plain reverse and edge views"),
    # The journal stays an item. Items genuinely do not rotate, so it is not a gap.
    ("RR_RouteRecording",         "item",     (1, 1), "single",  "Things/Item/Rimrooms",
     "items do not rotate"),
    ("RR_FadedInstitutionalCarpet", "terrain", (2, 2), "terrain", "Terrain/Rimrooms",
     "terrain tiles rather than rotates; 256 px keeps the weave at a readable density"),
    ("RR_QuietPursuer",           "pawn",     (2, 2), "pawn",    "Things/Pawn/Rimrooms",
     "a creature presentation, drawn square and never rotated by facing"),
    ("RR_CompanyJournal_Closed",  "item",     (1, 1), "single",  "Things/Item/Rimrooms/Journal",
     "the paper field journal's closed world sprite and inventory icon"),
    ("RR_CompanyJournal_Open",    "book",     (1, 1), "authored", "Things/Item/Rimrooms/Journal",
     "matching authored north/east/south reading views; west mirrors east"),
    ("RR_CompanyJournal_Vertical", "book",    (1, 1), "authored", "Things/Item/Rimrooms/Journal",
     "matching authored north/east/south upright views; west mirrors east"),
]

ROTATIONS = ("_north", "_east", "_south")
AUTHORED_FACINGS = ("_north", "_east")


def thresholded_box(image):
    """The object's box, with anything at or below the alpha floor treated as absent."""
    alpha = image.split()[3]
    mask = alpha.point(lambda v: 255 if v > ALPHA_FLOOR else 0)
    return mask.getbbox()


def _mean_difference(a, b):
    pixels = list(ImageChops.difference(a, b).getdata())
    return sum(sum(p) for p in pixels) / float(len(pixels) * 3)


def seam_error(image, samples=24):
    """How much worse the wrap joint is than this texture's own ordinary adjacency.

    **THE FIRST VERSION OF THIS WAS WRONG AND IT REPORTED A FAILURE THAT DOES NOT EXIST.** It
    compared a sixteen pixel band on one edge against the band on the other, which asks *do these
    two regions look alike* rather than *do these two columns join*. A quad mirror makes column 0
    identical to column w-1 by construction, so its true seam is exactly zero -- and the band
    measure scored it 7.15 against a threshold of 6 and would have condemned a provably seamless
    tile.

    What tiles actually touch is column w-1 against column 0, so that is what is measured, in
    units of the mean difference between ordinary neighbouring columns of the same image. A ratio
    near 1 means the joint is no more visible than any other column boundary. A photographic
    texture that does not wrap scores many times that, because the join is between unrelated
    content while its neighbours are continuous.
    """
    flat = image.convert("RGB")
    w, h = flat.size
    out = []
    for axis in (0, 1):
        if axis == 0:
            edge = (flat.crop((w - 1, 0, w, h)), flat.crop((0, 0, 1, h)))
            interior = [(flat.crop((i, 0, i + 1, h)), flat.crop((i + 1, 0, i + 2, h)))
                        for i in range(1, w - 2, max(1, (w - 3) // samples))]
        else:
            edge = (flat.crop((0, h - 1, w, h)), flat.crop((0, 0, w, 1)))
            interior = [(flat.crop((0, i, w, i + 1)), flat.crop((0, i + 1, w, i + 2)))
                        for i in range(1, h - 2, max(1, (h - 3) // samples))]
        joint = _mean_difference(*edge)
        baseline = sum(_mean_difference(a, b) for a, b in interior) / float(len(interior))
        out.append(joint / baseline if baseline > 0.01 else 0.0)
    return out


def fit(image, size):
    """Trim to the object, then letterbox it into `size` without distorting its aspect."""
    box = thresholded_box(image)
    if box is None:
        raise ValueError("the master is empty above the alpha floor")
    cropped = image.crop(box)
    target_w, target_h = size
    inner_w = int(target_w * (1.0 - BLEED * 2))
    inner_h = int(target_h * (1.0 - BLEED * 2))
    scale = min(inner_w / float(cropped.size[0]), inner_h / float(cropped.size[1]))
    scaled = cropped.resize((max(1, int(round(cropped.size[0] * scale))),
                             max(1, int(round(cropped.size[1] * scale)))), Image.LANCZOS)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    canvas.paste(scaled, ((target_w - scaled.size[0]) // 2, (target_h - scaled.size[1]) // 2), scaled)
    return canvas


def quad_mirror(image, size):
    """A provably seamless tile: mirrored edges are equal to their opposites by construction."""
    half = (size[0] // 2, size[1] // 2)
    corner = image.convert("RGB").resize(half, Image.LANCZOS)
    tile = Image.new("RGB", size)
    tile.paste(corner, (0, 0))
    tile.paste(corner.transpose(Image.FLIP_LEFT_RIGHT), (half[0], 0))
    tile.paste(corner.transpose(Image.FLIP_TOP_BOTTOM), (0, half[1]))
    tile.paste(corner.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM), half)
    return tile


def outputs_for(name, kind, tiles, strategy, folder):
    """Every file this entry produces, as (relative path, how it is made)."""
    size = (tiles[0] * PIXELS_PER_TILE, tiles[1] * PIXELS_PER_TILE)
    base = "%s/%s" % (folder, name)
    if strategy == "authored":
        return size, [("%s%s.png" % (base, suffix), suffix) for suffix in ROTATIONS]
    if strategy == "uniform":
        return size, [("%s%s.png" % (base, suffix), "fit") for suffix in ROTATIONS]
    if strategy == "flat":
        # East is drawn for the swapped footprint, so it is the swapped size too.
        return size, [("%s_south.png" % base, "fit"),
                      ("%s_north.png" % base, "fit"),
                      ("%s_east.png" % base, "turned")]
    if strategy == "terrain":
        return size, [("%s.png" % base, "seamless")]
    return size, [("%s.png" % base, "fit")]


def source_text():
    """All C# source as one blob, so a texture named only in code still counts as named.

    **A DEF IS NOT THE ONLY THING THAT CAN NAME A TEXTURE.** The gate's designation icon is
    resolved by `ContentFinder` from a path in `GateArt.cs`, because a gate is a door the player
    already owns and has no def of its own to carry artwork. Deriving shipment from defs alone
    would have held that texture back and left the button showing a picture of the door.
    """
    source_root = os.path.join(REPO, "src")
    blob = []
    for folder, _subdirs, files in os.walk(source_root):
        if os.sep + "obj" in folder or os.sep + "bin" in folder:
            continue
        for name in files:
            if name.lower().endswith(".cs"):
                blob.append(io.open(os.path.join(folder, name), encoding="utf-8-sig").read())
    return "\n".join(blob)


def referenced_texture_paths():
    """Every texture path the shipped Defs actually name.

    **THIS IS WHY THE 0.2.0 ART WAS RIGHT TO BE RETIRED THE FIRST TIME**, in the retirement's own
    words: those defs *"had no C# consumer whatsoever and had been shipping textures nobody could
    see"*. A texture in the package that no def names is weight with no gameplay behind it, and the
    temptation to cut all thirteen and sort the defs out later is exactly how that happens again.

    So shipping is **derived** from the defs rather than listed here. Author a def that names a
    texture and the next cut ships it; nothing else reaches the package. One derivation, and it
    maintains itself.
    """
    defs_root = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs")
    found = set()
    for folder, _subdirs, files in os.walk(defs_root):
        for name in files:
            if not name.lower().endswith(".xml"):
                continue
            body = io.open(os.path.join(folder, name), encoding="utf-8-sig").read()
            for tag in ("texPath", "texturePath"):
                start = "<%s>" % tag
                end = "</%s>" % tag
                index = 0
                while True:
                    a = body.find(start, index)
                    if a < 0:
                        break
                    b = body.find(end, a)
                    if b < 0:
                        break
                    found.add(body[a + len(start):b].strip())
                    index = b
    return found


def directional_texture_paths():
    """Texture stems whose shipped graphicData explicitly selects Graphic_Multi."""
    defs_root = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs")
    found = set()
    for folder, _subdirs, files in os.walk(defs_root):
        for name in files:
            if not name.lower().endswith(".xml"):
                continue
            tree = ET.parse(os.path.join(folder, name))
            graphics = (element for element in tree.iter()
                        if element.tag in ("graphicData", "openGraphic", "verticalGraphic"))
            for graphic in graphics:
                if (graphic.findtext("graphicClass") or "").strip() == "Graphic_Multi":
                    stem = (graphic.findtext("texPath") or "").strip()
                    if stem:
                        found.add(stem)
    return found


def authored_paths(name):
    """Only real drawings count; south is the unchanged original front master."""
    directory = JOURNAL_SOURCE if name.startswith("RR_CompanyJournal_") else SOURCE
    return {suffix: os.path.join(directory, name + suffix + ".png")
            for suffix in AUTHORED_FACINGS}


def primary_master_path(name, strategy):
    directory = JOURNAL_SOURCE if name.startswith("RR_CompanyJournal_") else SOURCE
    # Books have a real south drawing; legacy fixed-facing buildings keep their original name.
    suffix = "_south" if strategy == "authored" else ""
    return os.path.join(directory, name + suffix + ".png")


def main():
    apply_changes = "--apply" in sys.argv
    if not os.path.isdir(SOURCE):
        print("REFUSED: no master folder at %s" % os.path.relpath(SOURCE, REPO))
        return 1
    referenced = referenced_texture_paths()
    directional = directional_texture_paths()
    code = source_text()
    held = []

    # Refuse an incomplete active set before writing even an unrelated texture. Single-facing
    # objects may have draft masters, but those frames are not package output until activated.
    incomplete = []
    invalid = []
    active_frames = {}
    for name, kind, tiles, strategy, folder, _why in PLAN:
        if not ((kind == "building" and strategy == "single") or strategy == "authored"):
            continue
        if "%s/%s" % (folder, name) not in directional:
            continue
        paths = authored_paths(name)
        paths["_south"] = primary_master_path(name, strategy)
        absent = [path for path in paths.values() if not os.path.isfile(path)]
        if absent:
            incomplete.extend(os.path.relpath(path, REPO) for path in absent)
            continue
        size = (tiles[0] * PIXELS_PER_TILE, tiles[1] * PIXELS_PER_TILE)
        frames = {}
        for suffix, path in paths.items():
            try:
                with Image.open(path) as authored:
                    facing_size = (size[1], size[0]) if suffix == "_east" else size
                    frames[suffix] = fit(authored.convert("RGBA"), facing_size)
            except (OSError, ValueError) as exception:
                invalid.append((os.path.relpath(path, REPO), str(exception)))
        active_frames[name] = frames
    if incomplete or invalid:
        print("REFUSED: Graphic_Multi needs valid authored masters; no package textures written.")
        for path in incomplete:
            print("  MISSING FACING  %s" % path)
        for path, reason in invalid:
            print("  INVALID FACING  %s: %s" % (path, reason))
        return 1

    written = 0
    wanted = []
    ready = []
    print("cut phase 2 art  (%s)" % ("APPLY" if apply_changes else "report only"))
    print("")
    for name, kind, tiles, strategy, folder, why in PLAN:
        stem = "%s/%s" % (folder, name)
        if strategy == "authored" and stem not in directional:
            held.append((name, stem))
            print("  %-30s HELD -- no explicit Graphic_Multi binding names %s" % (name, stem))
            continue
        master_path = primary_master_path(name, strategy)
        if not os.path.isfile(master_path):
            print("  MISSING MASTER  %s" % name)
            return 1
        master = Image.open(master_path).convert("RGBA")
        paths = (authored_paths(name)
                 if (kind == "building" and strategy == "single") or strategy == "authored" else {})
        missing = [suffix for suffix, path in paths.items() if not os.path.isfile(path)]
        if paths and stem in directional:
            strategy = "authored"
        size, targets = outputs_for(name, kind, tiles, strategy, folder)

        if strategy == "authored":
            # Preflight fitted every active facing before any output could be written. East uses
            # the swapped rectangular footprint, as for flat fixtures; no view is synthesized.
            frames = active_frames[name]
            produced = [(rel, frames[facing]) for rel, facing in targets]
            print("  %-30s %-8s %4dx%-4d %-8s rotates (authored north/east, original south)"
                  % (name, kind, size[0], size[1], "%dx%d" % tiles))
        elif strategy == "terrain":
            tile = quad_mirror(master, size)
            before = seam_error(master)
            after = seam_error(tile)
            print("  %-30s %-8s %4dx%-4d terrain   seam x%.1f/x%.1f -> x%.2f/x%.2f (1.0 = invisible)"
                  % (name, kind, size[0], size[1], before[0], before[1], after[0], after[1]))
            produced = [(targets[0][0], tile)]
        else:
            frame = fit(master, size)
            turned = fit(master.transpose(Image.ROTATE_90), (size[1], size[0]))
            produced = [(rel, turned if how == "turned" else frame) for rel, how in targets]
            note = {"uniform": "rotates (one master, all sides alike)",
                    "flat": "rotates (east is south turned ninety degrees)"}.get(strategy, "no rotation")
            print("  %-30s %-8s %4dx%-4d %-8s %s" % (name, kind, size[0], size[1],
                                                     "%dx%d" % tiles, note))

        print("        %s" % why)
        # A def names its texture without a rotation suffix, so that is what is matched.
        if stem not in referenced and ('"%s"' % stem) not in code:
            held.append((name, stem))
            print("        HELD -- no shipped def or source file names %s" % stem)
            continue
        if kind == "building" and paths and strategy == "single":
            if missing:
                wanted.append((name, why, missing))
            else:
                ready.append(name)
        for rel, image in produced:
            destination = os.path.join(TEXTURES, rel.replace("/", os.sep))
            print("        -> 1.6/Textures/%s" % rel)
            if apply_changes:
                folder_path = os.path.dirname(destination)
                if not os.path.isdir(folder_path):
                    os.makedirs(folder_path)
                image.save(destination, optimize=True)
                written += 1

    if held:
        print("")
        print("HELD OUT OF THE PACKAGE -- cut cleanly, but no shipped def names them yet. A texture")
        print("nobody can see is the exact defect that retired this art in 0.9.0-dev. Author the def")
        print("and the next run ships it; nothing here needs changing.")
        for name, stem in held:
            print("  %-30s %s" % (name, stem))

    if wanted:
        print("")
        print("ROTATIONS WANTED -- these ship Graphic_Single and non-rotatable until a back and a")
        print("side view exist. None of them is faked, and none ships Graphic_Multi with one frame.")
        print("Missing drawings are listed per object. _south is the master already here,")
        print("and RimWorld mirrors _west from _east at no cost.")
        for name, why, missing in wanted:
            print("  %-30s missing %s; %s" % (name, ", ".join(missing), why))
        print("")
        print("  TOTAL STILL TO DRAW: %d frames across %d buildings."
              % (sum(len(missing) for _name, _why, missing in wanted), len(wanted)))
        print("  Nothing in this tool can derive them. A back view and a side view are drawings.")

    if ready:
        print("")
        print("AUTHORED VIEWS READY -- still Graphic_Single; activate Graphic_Multi, rotation and")
        print("the package allowlist together before exporting these draft facings.")
        for name in ready:
            print("  %s" % name)

    print("")
    if apply_changes:
        print("wrote %d texture(s)" % written)
    else:
        print("nothing written; re-run with --apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
