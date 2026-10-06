# How the PNGs became game assets

Written 2026-10-06, for Rev, at the owner's request.

## First, the part that matters most: I did not draw them

**The thirteen master images were not made in this session and not made by me.** They were already on disk when this work started, under `assets/source/phase2/`, with file timestamps of **2026-09-28** — the same day the owner's existing-content-only direction landed and retired them. Seven of them had already shipped once, in version 0.2.0, and were pulled back out across three later versions.

So the honest answer to *how did you make those PNGs* is: **I didn't. I cut them.** What follows is how 13 source images at 1254×1254 became the 15 textures the game actually loads, and every number below is measured rather than estimated.

| | |
|---|---|
| Masters in | 13 files, **1254×1254**, 8-bit RGBA — except the carpet, correctly 8-bit RGB with no alpha, because terrain is opaque |
| Total master size | **11,468 KB** |
| Textures out | **15 files**, 128×128 to 384×128 |
| Total shipped size | **532 KB** |

## The tool, not the hand

Everything is done by `tools/cut-phase2-art.py`. **Nothing was hand-edited**, and that is deliberate rather than lazy: re-running the tool reproduces every shipped texture from its master, so a master can be re-drawn and the package re-cut without anybody hand-matching thirteen crops. Run it with no arguments and it reports; `--apply` writes.

## Step 1 — measure the object, not its halo

The first pass used the image library's own bounding box, which treats an alpha value of 1 as present. On art with a soft drop shadow that measures the shadow.

It reported the **field analysis bench as 966×1130** — taller than wide, for an object that is visibly a long counter. At an alpha threshold of **32** the same image is **876×396**.

| Asset | Box at alpha > 0 | Box at alpha > 32 | Aspect used |
|---|---|---|---|
| field analysis bench | 966×1130 | **876×396** | **2.21 : 1** |
| site fluorescent | 1111×886 | **1089×221** | **4.96 : 1** |
| survey tag | 1000×1159 | **472×1004** | **0.47 : 1** |
| emergency cutoff | 691×812 | **546×804** | **0.68 : 1** |

Those corrected aspects are what assign each object's footprint in cells. The first numbers would have produced a bench shaped like a cupboard.

## Step 2 — size to the game, not to the master

RimWorld draws roughly **128 pixels per tile**. A 1254×1254 master is about ten times the size it is ever rendered at, and a master copied into a package instead of cut costs a player video memory for detail no camera shows.

So the output size is simply `tiles × 128`:

| Footprint | Texture |
|---|---|
| 1×1 | 128×128 |
| 2×1 | 256×128 |
| 2×2 | 256×256 |
| 3×1 | 384×128 |

A build-time check refuses any shipped gameplay texture larger than **1024 px on an axis**, which is the rule that catches a master pasted in by mistake.

## Step 3 — the actual cut

For each image, in this order:

1. **Crop** to the thresholded box from step 1, so the canvas is the object rather than the object plus empty space.
2. **Scale** to fit inside the target with a **4% bleed** kept on every edge, so nothing touches its own border.
3. **Resample** with Lanczos, which keeps the chunky outlines readable at a tenth of the original size where a cheaper filter turns them to mush.
4. **Letterbox** onto a fully transparent canvas of the exact target size, centred. The aspect is never stretched — an object that is 2.21 : 1 stays 2.21 : 1 and gets transparent space above and below it.

## Step 4 — rotation, which is where most of the thinking went

The owner's direction was blunt: **"remember things rotate"**.

RimWorld resolves a rotatable building's texture path as four frames — `_north`, `_east`, `_south`, `_west` — and **mirrors `_west` from `_east` for free. Nothing else is free.** A rotatable building shipping one unsuffixed frame is a missing-texture square on three of its four facings, and a player who never rotates it while placing would never find out.

So the tool has one strategy per asset, and each one is a claim about the drawing:

| Strategy | What it does | Used for | Why it is honest |
|---|---|---|---|
| `uniform` | Writes `_north`, `_east`, `_south` from the one master | emergency cutoff, site marker beacon | A button on a box and a lamp on a tripod genuinely look the same from every side |
| `flat` | `_south` and `_north` from the master, **`_east` is the master turned 90°** and drawn at the swapped size — a 3×1 strip at 384×128 becomes **128×384** | site fluorescent | A flat fixture read from above really does turn with its footprint. This is geometry, not a trick |
| `single` | One frame, and the def is marked **not rotatable** | machine gate, gate console, utility generator, field analysis bench | These are drawn as front elevations with a clear face. **There is no back view and no side view in existence**, so they ship honestly non-rotatable rather than showing one frame four times |
| `terrain` | Made seamless, no rotation | institutional carpet | Terrain tiles rather than turns |

**The four `single` buildings are printed under a heading called ROTATIONS WANTED on every run.** That list is the tool telling whoever reads it exactly which drawings are missing. Nobody has to remember.

A build check fails if any `Graphic_Multi` of ours is missing `_north`, `_east` or `_south`, so the dishonest version cannot be shipped by accident.

## Step 5 — the carpet, and a measurement that was wrong

Terrain is drawn once per cell, so a texture whose left edge does not match its right edge puts a visible joint at every tile boundary — a grid across an entire room, invisible until somebody plays.

**The first seam measurement was wrong by roughly an order of magnitude, and the number was published before it was checked.** It compared a 16-pixel band on one edge against the band on the other, which asks *do these two regions look alike*, not *do these two columns join*. It reported **18.3** against a threshold of 6 and called it a grid across every room.

It was caught because it scored a **provably seamless** image at 7.15.

The correct measure asks what tiles actually touch: the difference between **column w−1 and column 0**, expressed in units of the difference between ordinary neighbouring columns of the same image. A ratio near 1 means the joint is no more visible than any other column boundary.

| | Left/right | Top/bottom |
|---|---|---|
| Master, measured properly | **×1.4** | **×1.7** |
| After the fix | **×0.00** | **×0.00** |

So the real problem was a faint seam on a fine weave, not a grid. **The fix was still worth making; the alarm was not.**

The fix is a **quad mirror**: the top-left quarter is resized, then mirrored right, then that pair mirrored down. Mirrored edges are equal to their opposites **by construction**, so the result is seamless provably rather than approximately. The cost is stated rather than hidden — a quad mirror is symmetric about both axes, which on a fine fabric weave reads as texture and on a bold pattern would read as a kaleidoscope.

## Step 6 — what is allowed to ship

A rule earned the hard way. When this art was retired the first time, the reason recorded was that the defs *"had no C# consumer whatsoever and had been shipping textures nobody could see"*.

So the tool does not ship what it cuts. It **derives** what ships by reading which texture paths the shipped definitions and the C# source actually name. Author a definition that names a texture and the next run ships it; nothing else reaches the package, ever.

Four images are cut cleanly and deliberately held out on that rule, and the tool prints them with the reason.

## Is it enough? No — and here is the exact shortfall

**18 of the 19 cut textures ship.** One is held by decision: the Quiet Pursuer, which needs a race definition with body graphics rather than a texture, and a malformed race on a 296-mod profile breaks other mods' pawn rendering.

**Seven buildings are shipping non-rotatable because their other facings do not exist.** Each needs exactly **two** drawings — `_north` and `_east`. `_south` is the master already here, and the engine mirrors `_west` from `_east` free.

| Building | What is missing |
|---|---|
| machine gate | back and side of an arch drawn face on |
| gate console | back and side |
| utility generator | back and side of a three-quarter view |
| field analysis bench | the end-on view of a counter |
| field recorder | back and side of a desk unit |
| sealed evidence case | the case's other side; only the latch side is drawn |
| survey tag | the tag's reverse, which is blank and undrawn |

**14 frames.** The tool prints that count on every run, under a heading called ROTATIONS WANTED, so it is reported rather than remembered.

**Nothing in the pipeline can derive them.** A back view and a side view are drawings, not transforms — the one case where a transform is legitimate is the flat strip light, because a flat object genuinely turns with its footprint. Rotating a three-quarter drawing would lay the object on its side.

## What this does not cover

- **The four WAV files were not processed at all.** They were already 48 kHz, mono, 16-bit, between 0.6 and 2.0 seconds, which is correct for one-shot cues. They were copied in unchanged.
- **The four masters still needing rotations cannot be derived from what exists.** A back view and a side view are drawings, and no amount of tooling invents one.
- **Nothing here judges how the art looks in the game.** Only the owner launches it.

## Reproducing it

```
python tools/cut-phase2-art.py            # report what would be cut, write nothing
python tools/cut-phase2-art.py --apply    # cut and write into the package
```

The report names every output path, the footprint and strategy chosen for each master with the reason, the carpet's seam ratio before and after, every image held back and why, and the ROTATIONS WANTED list.
