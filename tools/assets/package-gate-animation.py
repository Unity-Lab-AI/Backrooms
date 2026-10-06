"""Package authored transparent energy sheets; never generates art or edits runtime.

The fixed uniform grid is preserved, so no frame gets its own scale/center transform.
Run --apply only after visually inspecting the generated sheets. Source masters
are retained outside the RimWorld mod. Default report mode writes nothing.
Applying requires --family; --family RR_GateOpen preserves the earlier deliveries.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "outputs/gate-cycle-assets-2026-10-06"
MASTER = ROOT / "assets/source/phase2"
PACKAGE = ROOT / "Mod/Rimrooms - Async Industries/1.6/Textures/Things/Building/Rimrooms/Gates"
FAMILIES = (
    ("RR_GateCharge", "gate-charge-sheet.png", 4, 2),
    ("RR_GateActivation", "gate-activation-sheet.png", 3, 2),
    ("RR_GateOpen", "gate-open-sheet.png", 4, 2),
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transparent_copy(image):
    # Alpha-composite on clear RGBA to discard hidden RGB before downsampling.
    clear = Image.new("RGBA", image.size)
    clear.alpha_composite(image)
    return clear


def extract(image, column, row, columns, rows, size):
    box = (column * image.width / columns, row * image.height / rows,
           (column + 1) * image.width / columns,
           (row + 1) * image.height / rows)
    return transparent_copy(image.resize((size, size), Image.Resampling.LANCZOS, box=box))


def metrics(image):
    alpha = np.asarray(image.getchannel("A"))
    center = alpha[96:160, 96:160]
    edges = np.concatenate((alpha[:8].ravel(), alpha[-8:].ravel(),
                            alpha[:, :8].ravel(), alpha[:, -8:].ravel()))
    return {
        "size": list(image.size), "mode": image.mode,
        "alphaRange": [int(alpha.min()), int(alpha.max())],
        "coverageAbove8": round(float((alpha > 8).mean()), 6),
        "center64MaxAlpha": int(center.max()),
        "center64CoverageAbove8": round(float((center > 8).mean()), 6),
        "center16MaxAlpha": int(alpha[120:136, 120:136].max()),
        "outer8MaxAlpha": int(edges.max()),
        "alphaEnergy": round(float(alpha.sum() / 255), 3),
    }


def transition(left, right):
    a, b = np.asarray(left).astype(float) / 255, np.asarray(right).astype(float) / 255
    a[:, :, :3] *= a[:, :, 3:4]
    b[:, :, :3] *= b[:, :, 3:4]
    delta = np.abs(a - b).mean(axis=2)
    union = np.maximum(a[:, :, 3], b[:, :, 3]) > (8 / 255)
    return {"meanPremultipliedRgbaDifference": round(float(delta.mean()), 6),
            "activePixelDifference": round(float(delta[union].mean()), 6)}


def checker_cell(size):
    image = Image.new("RGBA", (size, size), (74, 74, 74, 255))
    draw = ImageDraw.Draw(image)
    for y in range(0, size, 16):
        for x in range(0, size, 16):
            if (x // 16 + y // 16) % 2:
                draw.rectangle((x, y, x + 15, y + 15), fill=(98, 98, 98, 255))
    return image


def contact(frames, stem, columns, rows):
    cell, label = 256, 24
    sheet = Image.new("RGB", (columns * cell, rows * (cell + label)), (36, 36, 36))
    draw = ImageDraw.Draw(sheet)
    for index, frame in enumerate(frames):
        tile = checker_cell(cell)
        tile.alpha_composite(frame)
        x, y = (index % columns) * cell, (index // columns) * (cell + label)
        sheet.paste(tile.convert("RGB"), (x, y))
        draw.text((x + 8, y + cell + 5), f"{stem}_{index + 1:02d}", fill=(235, 235, 235))
    return sheet


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--family", choices=("all", *(x[0] for x in FAMILIES)))
    args = parser.parse_args()
    if args.apply and not args.family:
        parser.error("--apply requires an explicit --family; use RR_GateOpen to preserve finished charge/activation files")
    prepared = []
    for stem, filename, columns, rows in FAMILIES:
        if args.family and args.family != "all" and stem != args.family:
            continue
        source = OUTPUT / filename
        image = Image.open(source)
        if image.mode != "RGBA" or image.getchannel("A").getextrema()[0] != 0:
            raise ValueError(f"{filename}: source needs true RGBA transparency")
        if abs(image.width / columns - image.height / rows) > 0.01:
            raise ValueError(f"{filename}: source grid cells must be square")
        image = transparent_copy(image)
        master_size = round(image.width / columns)
        masters, frames, records = [], [], []
        for index in range(columns * rows):
            col, row = index % columns, index // columns
            master = extract(image, col, row, columns, rows, master_size)
            frame = transparent_copy(master.resize((256, 256), Image.Resampling.LANCZOS))
            record = metrics(frame)
            # Activation has two brief inward branches, never an opaque aperture.
            center_bad = (record["center64MaxAlpha"] > 8 if stem != "RR_GateActivation"
                          else record["center16MaxAlpha"] > 8 or
                          record["center64CoverageAbove8"] > 0.10)
            if center_bad or record["outer8MaxAlpha"] > 8:
                raise ValueError(f"{stem}_{index + 1:02d}: center/edge must stay clear")
            if not 0 < record["coverageAbove8"] < 0.20:
                raise ValueError(f"{stem}_{index + 1:02d}: sparse energy expected")
            name = f"{stem}_{index + 1:02d}.png"
            records.append({"name": name, "metrics": record,
                            "master": (MASTER / name).relative_to(ROOT).as_posix(),
                            "package": (PACKAGE / name).relative_to(ROOT).as_posix()})
            masters.append(master)
            frames.append(frame)
        report = {"stem": stem, "sourceSheet": source.relative_to(ROOT).as_posix(),
                  "sourceSha256": digest(source), "sheetSize": list(image.size),
                  "grid": [columns, rows], "masterSize": master_size,
                  "frames": records}
        if stem != "RR_GateActivation":
            report["loopTransitions"] = [
                {"from": index + 1, "to": ((index + 1) % len(frames)) + 1,
                 **transition(frame, frames[(index + 1) % len(frames)])}
                for index, frame in enumerate(frames)
            ]
            report["loopLimit"] = "Authored electrical flicker, not mathematically interpolated motion. The 8-to-1 boundary is compared with every normal step; final in-game pacing belongs to runtime QA."
            if stem == "RR_GateOpen":
                report["playback"] = "Quiet live company-portal presence after activation finishes. Eight-frame loop at a slower rate than charge; 300ms per frame in the outside-package APNG preview. Stop on closure; never draw on natural doors. Runtime state/lifecycle handling belongs to Claude."
        else:
            report["playback"] = "Nonlooping six-frame activation burst; stop drawing after frame 6."
        prepared.append((stem, columns, rows, masters, frames, report))
    if args.apply:
        MASTER.mkdir(parents=True, exist_ok=True)
        PACKAGE.mkdir(parents=True, exist_ok=True)
        for stem, columns, rows, masters, frames, report in prepared:
            for index, (master, frame) in enumerate(zip(masters, frames)):
                name = f"{stem}_{index + 1:02d}.png"
                master.save(MASTER / name)
                frame.save(PACKAGE / name)
                report["frames"][index]["masterSha256"] = digest(MASTER / name)
                report["frames"][index]["packageSha256"] = digest(PACKAGE / name)
            contact(frames, stem, columns, rows).save(OUTPUT / f"{stem}-contact.png")
            # Transparent APNG is an outside-package inspection aid, not game content.
            duration = 300 if stem == "RR_GateOpen" else 110 if stem == "RR_GateCharge" else 70
            frames[0].save(OUTPUT / f"{stem}-preview.png", save_all=True,
                           append_images=frames[1:], duration=duration,
                           loop=1 if stem == "RR_GateActivation" else 0,
                           disposal=1, blend=0)
        # Keep the completed original two-family manifest as its delivery receipt.
        manifest = "gate-open-manifest.json" if args.family == "RR_GateOpen" else (
            "animation-manifest-all.json" if args.family == "all" else f"{args.family}-manifest.json")
        (OUTPUT / manifest).write_text(
            json.dumps({"families": [x[-1] for x in prepared]}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"applied": args.apply, "families": [x[-1] for x in prepared]}, indent=2))


if __name__ == "__main__":
    main()
