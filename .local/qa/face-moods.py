"""Expressions that actually change, hair that does not (owner, 2026-10-13: "u need to mix up the emotions im going crazy
looking at 100 woman with the sdame smirk" / "and exact hair"). Only the face (eyes to chin, inside the hairline) is
repainted; hair, top and room stay pixel-identical. Also cut-out tops ("put exotic cuts in the shirt so more skin bleed
through") repainted below the choker.

    python face-moods.py <reference.png> <out_dir> moods|cutouts
"""
import os
import sys

import torch
from diffusers import StableDiffusionInpaintPipeline, DPMSolverMultistepScheduler
from PIL import Image, ImageDraw, ImageFilter

CKPT = os.path.expanduser(r"~\Desktop\Unity 3D Equational Model\Unity 18+\models\realistic-vision-v51.safetensors")
WHO = ("amateur webcam photo, real human, natural skin texture with visible pores and small imperfections, her own grey-green eyes, slight webcam grain, natural lighting, unretouched, the same young woman, light caucasian skin with a warm glow, soft dark eyeliner, natural lips, realistic face, ")
MOODS = {
    "laughing": "laughing out loud, mouth wide open, eyes squeezed shut, big laugh",
    "shocked": "shocked, mouth open in surprise, eyebrows raised high, wide eyes",
    "angry": "angry, furrowed brows, glaring, gritted teeth, scowl",
    "pouting": "pouting, lower lip pushed out, sad puppy eyes",
    "wink": "playful wink, one eye closed, tongue slightly out, teasing",
    "excited": "excited, huge open-mouth grin, bright wide eyes",
    "bored": "bored, half-closed eyes, flat unimpressed expression",
    "smug": "smug, one eyebrow raised, lopsided smirk",
}
CUTOUTS = {
    "keyhole-halter": "very short black halter crop top with a large keyhole cutout over the cleavage, bare stomach and navel",
    "lattice-crop": "very short black crop top with a criss-cross strappy lattice neckline showing skin between the straps, bare stomach",
    "cutout-shoulders": "very short black crop top with cutouts at the shoulders and a cutout under the collarbone, bare stomach and navel",
    "ring-cutout": "very short black crop top with an o-ring cutout in the center of the chest and thin straps, bare stomach and navel",
}
NEG = ("airbrushed, plastic skin, smooth skin, doll, cgi, render, glowing eyes, bright blue eyes, oversaturated, beauty filter, perfect skin, uncanny, nipples, nude, topless, nsfw, see-through, bra, lingerie, tattoo, dark skin, pale skin, black lipstick, "
       "different person, deformed face, cross-eyed, extra teeth, cartoon, anime, blurry, watermark, text, child, old")


def main():
    src, out, kind = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(out, exist_ok=True)
    img = Image.open(src).convert("RGB").resize((512, 640))
    mask = Image.new("L", img.size, 0)
    if kind == "moods":
        # the face only: inside the bangs and the side hair, down to the chin
        ImageDraw.Draw(mask).ellipse([168, 118, 344, 300], fill=255)
        items, strength, base = MOODS, 0.7, WHO + "face close up, "
    else:
        ImageDraw.Draw(mask).rectangle([20, 262, 492, 640], fill=255)
        items, strength, base = CUTOUTS, 0.95, WHO + "busty, lifted cleavage, sitting at her desk, warm lamp light, wearing a "
    mask = mask.filter(ImageFilter.GaussianBlur(10))
    pipe = StableDiffusionInpaintPipeline.from_single_file(CKPT, torch_dtype=torch.float16, safety_checker=None)
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    pipe.enable_model_cpu_offload()
    for name, what in items.items():
        g = torch.Generator("cuda").manual_seed(4445)
        r = pipe(prompt=(what + ", " + base) if kind == "moods" else base + what, negative_prompt=NEG, image=img, mask_image=mask, strength=strength,
                 num_inference_steps=30, guidance_scale=7.5, width=512, height=640, generator=g).images[0]
        r.save(os.path.join(out, name + ".png"))
        print("ok", name, flush=True)
    W, H, cols = 256, 320, 4
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (W * cols, (H + 24) * rows), "black")
    d = ImageDraw.Draw(sheet)
    for i, name in enumerate(items):
        x, y = (i % cols) * W, (i // cols) * (H + 24)
        sheet.paste(Image.open(os.path.join(out, name + ".png")).resize((W, H)), (x, y))
        d.text((x + 6, y + H + 4), "%d: %s" % (i + 1, name), fill="white")
    sheet.save(os.path.join(out, "sheet.png"))
    print("sheet", flush=True)


if __name__ == "__main__":
    main()
