"""Lines for Unity's voice that are NOT about RimWorld, written by her own brain, with nothing repeating.

Owner, 2026-10-13: "what the fuck we want her to say more than just rimworld" / "and nothing should ever repeat" /
"we dont want her remmebring repitiions". The accepted 4,845 lines are all stream-and-colony talk (template-authored:
161 share an opening with another line). This writes NEW lines across life topics -- talking to a viewer, food, music,
pets, weather, feelings, teasing, jokes, plans, memories, goodbyes -- every emotion x speech act, in her voice
(the loaded unity-brain), and keeps a line only if:
  * it is stream-clean (guards.clean_for_stream leaves it unchanged), no game words, 4-24 words;
  * NO 5 words in a row appear in ANY other line, old corpus or new (the no-repeat rule);
  * every phoneme is in the live voice's vocabulary (the fine-tune refuses a new vocabulary).
Text only: renders nothing, trains nothing. Output: training/voice/OFFGAME_CORPUS.jsonl (+ .report.json).

  python training/voice/build_offgame_corpus.py [--target 1500]
"""
import argparse
import hashlib
import json
import random
import re
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path[:0] = [str(HERE), str(ROOT / ".local" / "autopilot")]
from dataset_contract import EMOTIONS, SPEECH_ACTS, MAX_PHONEMES, normalize_transcript  # noqa: E402
from speech_text import speech_tokens  # noqa: E402
import guards  # noqa: E402

OLLAMA = "http://127.0.0.1:11434"
MODEL = "unity-brain"
OUT = HERE / "OFFGAME_CORPUS.jsonl"
ACCEPTED = Path(r"D:\voice-lab\pod-results\voice-2026-10-12\gen\dataset\metadata.jsonl")
TOPICS = [
    "greeting a viewer who just arrived and asking how their day went",
    "replying to a viewer's question about what she had for dinner or what she's snacking on",
    "talking about coffee, tea, soda or an energy drink she's drinking right now",
    "music she's into, a song stuck in her head, or what she listens to while driving",
    "a movie or show she watched and what she thought of it",
    "her cat or a pet, or a viewer's pet",
    "the weather, the season, being too hot or too cold in her room",
    "how tired, sleepy, hyped or stressed she feels tonight",
    "playfully teasing a viewer or flirting a little, clean and sweet",
    "a self-deprecating joke about herself",
    "her PC, headset, chair, webcam or stream setup acting up",
    "plans for the weekend, a trip, or something she wants to try",
    "a childhood memory or a story from school",
    "encouraging a viewer who is having a rough day",
    "asking the chat a question about themselves",
    "reacting with shock to something a viewer typed",
    "saying goodnight or signing off the stream",
    "thanking someone for a follow, a gift or a kind message, in a fresh way each time",
    "apologising for spacing out, mis-clicking or losing her train of thought",
    "a small win in real life: a package arriving, a good hair day, cleaning her room",
    "missing someone, a sad thought, feeling a bit low tonight",
    "being worried about a friend, an exam, a bill or a doctor's visit",
    "being annoyed by traffic, a neighbour, a slow internet connection",
    "laughing at a dumb joke, a typo in chat, or something she just did",
    "food cravings, pizza, ramen, candy, cooking disasters",
    "gym, walks, stretching, sitting too long",
    "dreams, sleep schedule, naps, staying up too late",
    "phones, notifications, texting, forgetting to charge things",
    "books, podcasts, something she learned recently",
    "birthdays, holidays, gifts and small celebrations",
]
# which topics a feeling can honestly sit on (indices into TOPICS); neutral and warm fit anything
FITS = {
    "happy": [0, 1, 2, 3, 4, 5, 8, 11, 12, 14, 17, 19, 24, 25, 28, 29],
    "amused": [0, 1, 4, 5, 8, 9, 10, 12, 15, 23, 24, 27, 28],
    "excited": [3, 4, 11, 14, 16, 17, 19, 24, 28, 29],
    "sad": [7, 12, 13, 16, 20, 21, 26, 29],
    "concerned": [7, 13, 20, 21, 25, 26, 27],
    "frustrated": [6, 7, 10, 18, 22, 24, 25, 27],
    "surprised": [1, 5, 10, 15, 19, 23, 24, 27, 29],
}
GAME = re.compile(r"\b(colon|pawn|raid|haul|stockpile|rimworld|turret|mortar|thrumbo|muffalo|pirate|tribal|persona core|"
                  r"killbox|embrasure|mech|insect|toxic fallout|drop pod|caravan|trader|quest|ritual|ideolog|prisoner|"
                  r"recruit|tame|geyser|chemfuel|smokeleaf|psychite|pemmican|nutrient paste|lavish|butcher|sandbag|"
                  r"scar|juno|tamsin|gee|biscuit|base|map|zone|bill|research|freezer|battery|solar)\b", re.I)
BANNED = re.compile(r"\b(beer|wine|vodka|drunk|weed|joint|high|stoned|blunt|vape|smoke|cigarette|drugs?)\b", re.I)


def ngrams(words, n=5):
    return {" ".join(words[i:i + n]) for i in range(len(words) - n + 1)}


def ask(prompt):
    body = {"model": MODEL, "prompt": prompt, "stream": False, "think": False,
            "options": {"num_ctx": 4096, "temperature": 1.0, "top_p": 0.95, "repeat_penalty": 1.15}}
    req = urllib.request.Request(OLLAMA + "/api/generate", json.dumps(body).encode(), {"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=180).read()).get("response", "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=1500)
    args = ap.parse_args()
    from misaki import en, espeak
    g2p = en.G2P(trf=False, british=False, fallback=espeak.EspeakFallback(british=False))
    vocab = set(json.load(open(ROOT / "models" / "unity-voice" / "voice-meta.json", encoding="utf-8"))["vocab"])
    seen_norm, seen_grams = set(), set()
    for line in ACCEPTED.read_text(encoding="utf-8").splitlines():
        if line.strip():
            t = normalize_transcript(json.loads(line)["text"])
            seen_norm.add(t); seen_grams |= ngrams(t.split())
    kept = []
    if OUT.exists():
        for line in OUT.read_text(encoding="utf-8").splitlines():
            r = json.loads(line); kept.append(r)
            t = normalize_transcript(r["text"]); seen_norm.add(t); seen_grams |= ngrams(t.split())
    print("accepted corpus: %d lines; off-game so far: %d" % (len(seen_norm) - len(kept), len(kept)), flush=True)
    rejected = {"dirty": 0, "game": 0, "length": 0, "repeat": 0, "phoneme": 0, "dup": 0}
    rnd = random.Random(20261013 + len(kept))
    out = open(OUT, "a", encoding="utf-8")
    started = time.monotonic()
    while len(kept) < args.target:
        emotion, act = rnd.choice(EMOTIONS), rnd.choice(SPEECH_ACTS)
        topic = rnd.choice([TOPICS[i] for i in FITS.get(emotion, range(len(TOPICS)))])   # the feeling must fit the topic
        want_laugh = emotion in ("amused", "happy") and rnd.random() < 0.35
        prompt = ("You are Unity, a 24-year-old woman streaming to a small friendly chat. Write 10 different things you "
                  "might say out loud, each on its own line, no numbering, no quotes. Topic: %s. Feeling: %s. Kind of line: %s "
                  "(%s). Rules: 6 to 20 words each; natural spoken English; nothing about video games or RimWorld; no real "
                  "people's names; no swearing, no alcohol, no drugs; each line must be a completely different sentence from "
                  "the others, different opening words, different wording.%s" % (
                      topic, emotion, act,
                      {"statement": "a plain statement", "yes_no_question": "a yes/no question to the viewer",
                       "wh_question": "a who/what/where/why/how question", "exclamation": "an exclamation",
                       "instruction": "telling the viewer to do something, friendly", "reassurance": "reassuring someone",
                       "aside": "a quiet aside to herself"}[act],
                      " Put the token [laughter] where she actually laughs, in about half of the lines." if want_laugh else ""))
        try:
            text = ask(prompt)
        except Exception as e:
            print("brain error:", e, flush=True); time.sleep(5); continue
        for raw in text.splitlines():
            line = raw.strip().strip('"').lstrip("-*•0123456789.) ").strip().strip('"')
            if not line or ":" in line[:14]:
                continue
            plain = line.replace("[laughter]", " ")
            try:
                words = normalize_transcript(plain).split()
            except ValueError:            # stage directions / other markup the voice does not take
                rejected["phoneme"] += 1; continue
            if not 4 <= len(words) <= 24 or not re.search(r"[.!?]$", line):
                rejected["length"] += 1; continue
            if guards.clean_for_stream(plain, max_len=400) != re.sub(r"\s+", " ", plain).strip() or BANNED.search(plain):
                rejected["dirty"] += 1; continue
            if GAME.search(plain):
                rejected["game"] += 1; continue
            try:
                norm = normalize_transcript(line)
            except ValueError:
                rejected["phoneme"] += 1; continue
            if norm in seen_norm:
                rejected["dup"] += 1; continue
            grams = ngrams(words)
            if grams & seen_grams:
                rejected["repeat"] += 1; continue
            try:
                phon = speech_tokens(line, g2p, MAX_PHONEMES)
            except ValueError:
                rejected["phoneme"] += 1; continue
            if set(phon) - vocab:
                rejected["phoneme"] += 1; continue
            row = {"id": "og-" + hashlib.sha256((norm + "|" + emotion + "|" + act).encode()).hexdigest()[:24],
                   "text": line, "emotion": emotion, "intensity": 0.0 if emotion == "neutral" else 0.35, "pace": 1.0,
                   "speech_act": act, "topic": topic}
            kept.append(row); seen_norm.add(norm); seen_grams |= grams
            out.write(json.dumps(row, ensure_ascii=False) + "\n"); out.flush()
            if len(kept) >= args.target:
                break
        if len(kept) % 50 < 10:
            print("%d/%d kept  rejected %s  (%.0f s)" % (len(kept), args.target, rejected, time.monotonic() - started), flush=True)
    report = {"lines": len(kept), "rejected": rejected, "topics": len(TOPICS), "rule": "no 5 words in a row shared with any other line",
              "by_emotion": {e: sum(r["emotion"] == e for r in kept) for e in EMOTIONS},
              "by_act": {a: sum(r["speech_act"] == a for r in kept) for a in SPEECH_ACTS},
              "laughter_lines": sum("[laughter]" in r["text"] for r in kept)}
    (HERE / "OFFGAME_CORPUS.report.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print("DONE", json.dumps(report), flush=True)


if __name__ == "__main__":
    main()
