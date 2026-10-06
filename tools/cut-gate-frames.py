"""Convert authored gate trims to cardinal world textures without changing native doors.

Report mode writes nothing. --apply preflights all twelve drawings before exporting.
North/south use the wide gate face; east uses the swapped physical rectangle.
Masters stay under assets/source/gates; no front icon is reused as a world frame.
"""
import argparse
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/source/gates"
DESTINATION = ROOT / "Mod/Rimrooms - Async Industries/1.6/Textures/Things/Building/Rimrooms/Gates"
CONSUMER = ROOT / "src/RimroomsAsyncIndustries/Gate/GateWorldFrames.cs"
FOOTPRINTS = ((1, 1), (1, 2), (1, 3), (2, 3))
FACINGS = ("north", "east", "south")
PIXELS_PER_CELL = 128


def fit_frame(image, dimensions):
    # Preserve source masters, but clear RGB hidden under alpha zero before filtering.
    cleaned = Image.new("RGBA", image.size)
    cleaned.alpha_composite(image)
    image = cleaned
    alpha = image.getchannel("A")
    bounds = alpha.point(lambda value: 255 if value > 32 else 0).getbbox()
    if bounds is None:
        raise ValueError("empty frame")
    cropped = image.crop(bounds)
    # A frame must leave the physical doorway visible, never fill it with an opaque slab.
    cx, cy = cropped.width // 2, cropped.height // 2
    if cropped.getchannel("A").getpixel((cx, cy)) > 8:
        raise ValueError("gate aperture center must be transparent")
    scale = min(dimensions[0] * 0.96 / cropped.width,
                dimensions[1] * 0.96 / cropped.height)
    resized = cropped.resize((max(1, round(cropped.width * scale)),
                              max(1, round(cropped.height * scale))), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", dimensions)
    canvas.alpha_composite(resized, ((dimensions[0] - resized.width) // 2,
                                    (dimensions[1] - resized.height) // 2))
    return canvas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    consumer = CONSUMER.read_text(encoding="utf-8-sig") if CONSUMER.is_file() else ""
    outputs, failures = [], []
    for short, long in FOOTPRINTS:
        stem = "RR_GateFrame_%dx%d" % (short, long)
        path = "Things/Building/Rimrooms/Gates/" + stem
        if '"' + path + '"' not in consumer:
            failures.append("no exact runtime consumer for " + path)
        for facing in FACINGS:
            name = stem + "_" + facing + ".png"
            dimensions = ((short, long) if facing == "east" else (long, short))
            dimensions = tuple(axis * PIXELS_PER_CELL for axis in dimensions)
            try:
                with Image.open(SOURCE / name) as master:
                    frame = fit_frame(master.convert("RGBA"), dimensions)
                outputs.append((name, frame))
            except (OSError, ValueError) as error:
                failures.append(name + ": " + str(error))
    if failures:
        print("REFUSED: no gate textures written")
        for failure in failures:
            print("  " + failure)
        return 1
    if args.apply:
        DESTINATION.mkdir(parents=True, exist_ok=True)
    for name, frame in outputs:
        print("%s -> %dx%d" % (name, frame.width, frame.height))
        if args.apply:
            frame.save(DESTINATION / name, optimize=True)
    print("wrote %d gate textures" % len(outputs) if args.apply else "nothing written; use --apply")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
