"""Build Unity's voice dataset: #5 (round2/05.pt) reads her own lines + knowledge sentences, LJSpeech layout.
Resumable: a line whose wav exists is skipped. Two paces per line (her own lines) so duration varies.
python .local/voice-lab/make_dataset.py [max_hours]  ->  .local/voice-lab/dataset/{wavs/*.wav, metadata.csv}"""
import json, os, re, sys, random, hashlib, torch, soundfile as sf
from kokoro import KPipeline
LAB = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(LAB, "..", ".."))
OUT = os.path.join(LAB, "dataset"); WAVS = os.path.join(OUT, "wavs"); os.makedirs(WAVS, exist_ok=True)
MAX_S = float(sys.argv[1] if len(sys.argv) > 1 else 12) * 3600
own, know = [], []
for l in open(os.path.join(ROOT, "training/data/brain/train.jsonl"), encoding="utf-8"):
    r = json.loads(l); k = r.get("kind")
    for m in r["messages"]:
        if m["role"] != "assistant" or not isinstance(m.get("content"), str): continue
        t = " ".join(m["content"].split())
        if k in ("voice", "chat", "writeup") and 3 < len(t.split()) < 40: own.append(t)
        elif k == "knowledge":
            know += [s for s in re.split(r"(?<=[.!?])\s+", t) if 5 <= len(s.split()) <= 30 and re.fullmatch(r"[A-Za-z0-9 ,.'!?;:()\-]+", s)]
own, know = sorted(set(own)), sorted(set(know)); random.seed(5); random.shuffle(know)
jobs = [(t, sp) for t in own for sp in (0.92, 1.1)] + [(t, round(random.uniform(0.9, 1.12), 2)) for t in know]
voice = torch.load(os.path.join(LAB, "round2", "05.pt"))
pipe = KPipeline(lang_code="a", device="cuda", repo_id="hexgrad/Kokoro-82M")
meta = os.path.join(OUT, "metadata.csv"); done = {}
if os.path.exists(meta):
    for row in open(meta, encoding="utf-8"):
        p = row.rstrip("\n").split("|"); done[p[0]] = float(p[3])
total = sum(done.values()); f = open(meta, "a", encoding="utf-8")
for t, sp in jobs:
    if total >= MAX_S: break
    key = hashlib.sha1(("%s|%s" % (t, sp)).encode()).hexdigest()[:12]
    if key in done: continue
    a = torch.cat([torch.as_tensor(x) for _, _, x in pipe(t, voice=voice, speed=sp)]).numpy()
    sf.write(os.path.join(WAVS, key + ".wav"), a, 24000); secs = len(a) / 24000; total += secs
    f.write("%s|%s|%s|%.2f\n" % (key, t, sp, secs)); f.flush()
    if len(done) % 500 == 0: print("%.2f h" % (total / 3600), flush=True)
    done[key] = secs
print("DONE %.2f h, %d clips (own lines %d, knowledge pool %d)" % (total / 3600, len(done), len(own), len(know)))
