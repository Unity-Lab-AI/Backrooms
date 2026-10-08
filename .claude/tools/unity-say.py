"""Streamer narration: speak a line in Unity's voice AND post it to the Persona Studio chat.

    python .claude/tools/unity-say.py "line"            # speaks in the background, returns at once
    python .claude/tools/unity-say.py --wait "line"     # speaks and waits until done

The line is appended to .claude/.studio-outbox.jsonl (replyTo null = unprompted narration), so
the studio window shows what Unity is saying while she plays.
"""
import json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
OUTBOX = os.path.join(HERE, "..", ".studio-outbox.jsonl")


def post(text, persona="unity"):
    last = 0
    if os.path.exists(OUTBOX):
        for line in open(OUTBOX, encoding="utf-8"):
            try: last = max(last, int(json.loads(line).get("id", 0)))
            except Exception: pass
    with open(OUTBOX, "a", encoding="utf-8") as f:
        f.write(json.dumps({"id": last + 1, "replyTo": None, "ts": int(time.time() * 1000),
                            "persona": persona, "text": text}) + "\n")


def main():
    args = sys.argv[1:]
    wait = bool(args) and args[0] == "--wait"
    if wait: args = args[1:]
    text = " ".join(args).strip()
    if not text: return
    post(text)
    speak = [sys.executable, os.path.join(HERE, "unity-speak.py")] + ([] if wait else ["--bg"]) + [text]
    subprocess.run(speak)


if __name__ == "__main__":
    main()
