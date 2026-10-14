"""Outfit swap that keeps Unity's face: inpaint only the torso of the reference (owner, 2026-10-13: "try differnt
clothing and push up bra appearance but no bra" / "those are all hug fabric dresses need less fabric" / "Unity is
caucasian not black"). Plain img2img kept the old top or drifted her face and skin; this repaints below the chin only.

    python .local/qa/outfit-inpaint.py <source.png> <out_dir>
"""
import os
import sys

import torch
from diffusers import StableDiffusionInpaintPipeline, DPMSolverMultistepScheduler
from PIL import Image, ImageDraw, ImageFilter

CKPT = os.path.expanduser(r"~\Desktop\Unity 3D Equational Model\Unity 18+\models\realistic-vision-v51.safetensors")
SKIN = "light caucasian skin with a warm healthy glow, not pale"
BASE = ("amateur webcam photo, real human, natural skin texture with visible pores and small imperfections, her own grey-green eyes, slight webcam grain, natural lighting, unretouched, candid gaming webcam photo, waist-up, young woman sitting at her desk gaming, facing the camera, cozy bedroom, " + SKIN +
        ", busty, lifted perky round cleavage, push-up shape, high firm bust, warm lamp light, realistic, wearing a ")
EVERYDAY = {
    "scoop-tee": "fitted black low scoop neck t-shirt, everyday casual",
    "wrap-top": "black wrap top with a deep v neckline, everyday casual",
    "henley": "fitted dark grey v neck henley with the top buttons open, everyday casual",
    "cardigan": "cropped black cardigan buttoned low over bare skin, everyday casual",
}
TOPS = {
    "scoop-tank": "fitted black scoop neck tank top, everyday casual",
    "vneck-tee": "fitted white low v-neck t-shirt, everyday casual",
    "band-tee": "fitted black cropped band t-shirt with a low scoop neck, everyday casual",
    "flannel": "open red plaid flannel shirt over a low cut black tank top, everyday casual",
    "offshoulder": "loose black off-shoulder knit sweater with a low neckline, everyday cozy",
    "hoodie": "unzipped black hoodie over a low cut grey tank top, everyday cozy",
}
CROPS = {
    "halter-crop": "very short black halter neck crop top ending just below the bust, deep v neckline, bare flat stomach and navel",
    "cami-crop": "very short black spaghetti strap crop cami ending just below the bust, low neckline, bare flat stomach and navel",
    "tiefront-crop": "very short black tie-front crop top ending just below the bust, low neckline, bare flat stomach and navel",
    "lace-cami-crop": "very short dark purple spaghetti strap crop cami with lace trim ending just below the bust, bare flat stomach and navel",
    "pink-halter-crop": "very short pink halter neck crop top ending just below the bust, deep v neckline, bare flat stomach and navel",
}
OUTFITS = {
    "bandeau": "black strapless bandeau tube top, cropped, bare shoulders and midriff",
    "crop-cami": "tiny black strappy cropped cami top with a plunging neckline, bare midriff",
    "crop-corset": "black cropped corset top with sweetheart neckline, bare midriff",
    "halter": "black cropped halter top with a deep v neckline, bare shoulders and midriff",
}
NEG = ("airbrushed, plastic skin, smooth skin, doll, cgi, render, glowing eyes, bright blue eyes, oversaturated, beauty filter, perfect skin, uncanny, visible bra, bra straps, lingerie, underwear, saggy breasts, droopy breasts, nipples, nipple outline, nude, topless, nsfw, "
       "see-through, sheer, wardrobe malfunction, dress, baggy, dark skin, black woman, pale skin, computer, monitor, "
       "keyboard, laptop, headset, cartoon, anime, blurry, deformed, extra fingers, child, teen, old, watermark, text")


def main():
    src, out = sys.argv[1], sys.argv[2]
    global OUTFITS
    if len(sys.argv) > 3 and sys.argv[3] == "everyday":
        OUTFITS = EVERYDAY
    if len(sys.argv) > 3 and sys.argv[3] == "tops":
        OUTFITS = TOPS
    if len(sys.argv) > 3 and sys.argv[3] == "crops":
        OUTFITS = CROPS
    os.makedirs(out, exist_ok=True)
    img = Image.open(src).convert("RGB").resize((512, 640))
    # below the chin and choker, inside the shoulders' width: face, hair and background above stay pixel-identical
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rectangle([20, 250, 492, 640], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(8))
    pipe = StableDiffusionInpaintPipeline.from_single_file(CKPT, torch_dtype=torch.float16, safety_checker=None)
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    pipe.enable_model_cpu_offload()
    for name, outfit in OUTFITS.items():
        g = torch.Generator("cuda").manual_seed(4445)
        r = pipe(prompt=BASE + outfit, negative_prompt=NEG, image=img, mask_image=mask, strength=float(os.environ.get('INPAINT_STRENGTH', '0.95')),
                 num_inference_steps=30, guidance_scale=7.0, width=512, height=640, generator=g).images[0]
        r.save(os.path.join(out, name + ".png"))
        print("ok", name, flush=True)
    W, H = 320, 400
    sheet = Image.new("RGB", (W * len(OUTFITS), H + 24), "black")
    d = ImageDraw.Draw(sheet)
    for i, name in enumerate(OUTFITS):
        sheet.paste(Image.open(os.path.join(out, name + ".png")).resize((W, H)), (i * W, 0))
        d.text((i * W + 6, H + 4), "%d: %s" % (i + 1, name), fill="white")
    sheet.save(os.path.join(out, "sheet.png"))
    print("sheet", flush=True)


if __name__ == "__main__":
    main()
