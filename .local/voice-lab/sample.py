"""Voice lab: blend Kokoro American-female style vectors into new voices and render one line each.
python .local/voice-lab/sample.py <round> <n> [seed]   -> .local/voice-lab/<round>/NN.wav + recipes.json"""
import json, os, sys, random, torch, soundfile as sf
from kokoro import KPipeline
from huggingface_hub import hf_hub_download
rnd, n = sys.argv[1], int(sys.argv[2]); random.seed(int(sys.argv[3]) if len(sys.argv) > 3 else 11)
OUT = os.path.join(os.path.dirname(__file__), rnd); os.makedirs(OUT, exist_ok=True)
POOL = ["af_heart", "af_bella", "af_nicole", "af_sky", "af_sarah", "af_nova", "af_jessica", "af_river", "af_aoede", "af_kore", "af_alloy"]
LINE = "Hey, welcome in! Grab a seat. Scar's out planting crops, and honestly? Watching her work is weirdly relaxing."
pipe = KPipeline(lang_code="a", device="cuda" if torch.cuda.is_available() else "cpu")
vec = {v: torch.load(hf_hub_download("hexgrad/Kokoro-82M", "voices/%s.pt" % v), weights_only=True) for v in POOL}
recipes = {}
for i in range(1, n + 1):
    picks = random.sample(POOL, 3); w = [random.random() for _ in picks]; t = sum(w); w = [x / t for x in w]
    mix = sum(vec[v] * x for v, x in zip(picks, w))
    speed = round(random.uniform(0.95, 1.12), 2)
    audio = torch.cat([torch.as_tensor(a) for _, _, a in pipe(LINE, voice=mix, speed=speed)])
    name = "%02d" % i; sf.write(os.path.join(OUT, name + ".wav"), audio.numpy(), 24000)
    torch.save(mix, os.path.join(OUT, name + ".pt"))
    recipes[name] = {"mix": {v: round(x, 3) for v, x in zip(picks, w)}, "speed": speed}
    print(name, recipes[name])
json.dump(recipes, open(os.path.join(OUT, "recipes.json"), "w"), indent=1)
