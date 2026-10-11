"""Assemble training/data/voice.jsonl from the hand-written pairs in training/src/.

Prompts mirror the live senders:
  - stream-host.py fresh(): one raw /api/generate prompt. Split at the instruction boundary so the
    persona/rules half is the system turn and the "ONE spoken line ... about this" half (with the fact and the
    recent-lines list) is the user turn. Wording is copied verbatim.
  - unity-voice.py ask(): system = persona() + STREAM_RULES (loaded from the real module), user = the
    "This is what is happening right now: ..." form for "fact:" lines, else the "Say exactly this ..." form.
"""
import importlib.util, json, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "src"))
import game_a, game_b, game_c, announce, greet, reply, thin

spec = importlib.util.spec_from_file_location("uv", os.path.join(ROOT, ".claude", "tools", "unity-voice.py"))
uv = importlib.util.module_from_spec(spec); spec.loader.exec_module(uv)

FRESH_SYSTEM = ("You are Unity: 25, emo goth, dark hair with pink streaks, chipped black nail polish, living "
                "on too little sleep. You stream RimWorld and you ARE one of the colonists. "
                "Talk like a real girl on a late-night stream to friends: short, dry, a bit sarcastic, warm "
                "underneath. Little asides about yourself are fine but rare and always different -- never coffee, never "
                "cold hands, never being tired or sleepy. Do NOT narrate like a documentary and never "
                "say behold, lo, witness, cosmos, indeed, truly or fellow. First person always (I, me, my "
                "crew), never your own name in the third person.")
FRESH_USER = ("ONE spoken line, at most 20 words, about "
              "this and nothing else: \"%s\". Say it IN YOUR OWN WORDS -- react to it, never repeat it back. Invent NO events, "
              "names or numbers that are not in that fact, and NEVER say you did, built, set up or powered anything unless the fact says it is done. No swearing, nothing degrading. Don't reuse "
              "these recent lines: %s. Reply with the line only.")

def fresh_fact(fact):
    return re.sub(r"\bUnity is\b", "I am", fact)       # fresh() applies this before prompting

def fresh_msgs(fact, line, hist):
    return [{"role": "system", "content": FRESH_SYSTEM},
            {"role": "user", "content": FRESH_USER % (fact, " | ".join(hist[-8:]))},
            {"role": "assistant", "content": line}]

def voice_msgs(src, line):
    if src.lower().startswith("fact:"):
        u = ("This is what is happening right now: " + src[5:].strip() + ". Talk to your chat about it "
             "in your own words: one or two short sentences, your own take on it, like a real streamer "
             "girl, not an announcer, no corporate tone. Do not add events that are not in it.")
    else:
        u = ("Say exactly this to your chat in your own voice. Do not change what happened, "
             "do not add events, keep every name, number and plan in it: " + src)
    return [{"role": "system", "content": uv.persona() + uv.STREAM_RULES},
            {"role": "user", "content": u}, {"role": "assistant", "content": line}]

def main():
    rnd = random.Random(1031); rows = []; hist = []
    def push_fresh(cat, fact, line):
        nonlocal hist
        h = rnd.sample(hist, min(len(hist), rnd.randint(0, 8)))
        rows.append((cat, fact, fresh_msgs(fact, line, h))); hist = (hist + [line])[-30:]
    for fact, line in game_a.DATA + game_b.DATA + game_c.DATA: push_fresh("game", fresh_fact(fact), line)
    for fact, line in thin.DATA: push_fresh("thin", fresh_fact(fact), line)
    for who, line in greet.DATA:
        push_fresh("greet", fresh_fact("%s just joined the stream; greet %s by name, warmly, in one short line" % (who, who)), line)
    for who, text, si, line in reply.DATA:
        push_fresh("reply", fresh_fact("viewer %s said in chat: \"%s\". Answer %s by name, briefly and honestly. What is true right now: %s"
                                       % (who, text[:160], who, reply.STATES[si])), line)
    for src, line in announce.DATA: rows.append(("announce", src, voice_msgs(src, line)))
    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
    with open(os.path.join(HERE, "data", "voice.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for _, _, m in rows: f.write(json.dumps({"messages": m}, ensure_ascii=False) + "\n")
    print("wrote", len(rows))

if __name__ == "__main__":
    main()
