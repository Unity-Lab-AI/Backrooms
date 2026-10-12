"""Round 2+: breed two picked voices, exaggerate away from the average voice, render with emotional pacing.
python .local/voice-lab/breed.py <from_round> <a> <b> <to_round>"""
import json, os, sys, torch, soundfile as sf
from kokoro import KPipeline
from huggingface_hub import hf_hub_download
LAB = os.path.dirname(os.path.abspath(__file__)); src, a, b, dst = sys.argv[1:5]
OUT = os.path.join(LAB, dst); os.makedirs(OUT, exist_ok=True)
A = torch.load(os.path.join(LAB, src, a + ".pt")); B = torch.load(os.path.join(LAB, src, b + ".pt"))
POOL = ["af_heart", "af_bella", "af_nicole", "af_sky", "af_sarah", "af_nova", "af_jessica", "af_river", "af_aoede", "af_kore", "af_alloy"]
MEAN = sum(torch.load(hf_hub_download("hexgrad/Kokoro-82M", "voices/%s.pt" % v, repo_id="hexgrad/Kokoro-82M") if False else hf_hub_download(repo_id="hexgrad/Kokoro-82M", filename="voices/%s.pt" % v), weights_only=True) for v in POOL) / len(POOL)
# (text, speed): the greeting bright and quick, the aside slower and warm
LINES = [("Hey, [welcome](+2) in!", 1.12), ("Grab a seat.", 1.02),
         ("Scar's out planting crops, and [honestly](+2)?", 1.0), ("Watching her work is [weirdly](+2) relaxing.", 0.9),
         ("Oh my god, a [raid](+2)! Okay, okay, everybody inside!", 1.15)]
pipe = KPipeline(lang_code="a", device="cuda", repo_id="hexgrad/Kokoro-82M")
GRID = [(0.5, 1.0), (0.5, 1.35), (0.65, 1.35), (0.35, 1.35), (0.5, 1.7), (0.6, 1.6)]
recipes = {}; gap = torch.zeros(int(24000 * 0.28))
for i, (wa, ex) in enumerate(GRID, 1):
    mix = A * wa + B * (1 - wa); mix = MEAN + (mix - MEAN) * ex
    parts = []
    for text, sp in LINES:
        parts += [torch.as_tensor(x) for _, _, x in pipe(text, voice=mix, speed=sp)] + [gap]
    name = "%02d" % i; sf.write(os.path.join(OUT, name + ".wav"), torch.cat(parts).numpy(), 24000)
    torch.save(mix, os.path.join(OUT, name + ".pt"))
    recipes[name] = {"parents": "%s/%s %.2f + %s/%s %.2f" % (src, a, wa, src, b, 1 - wa), "exaggerate": ex}
    print(name, recipes[name])
json.dump(recipes, open(os.path.join(OUT, "recipes.json"), "w"), indent=1)
