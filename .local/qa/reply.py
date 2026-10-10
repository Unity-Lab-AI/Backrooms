"""Answer a chat message on stream: python .local/qa/reply.py <inbox id> "text"
Writes the reply to the studio outbox (replyTo = id) and speaks it."""
import importlib.util, json, os, subprocess, sys, time
# her own words, stream-filtered (unity-voice.py); --raw skips it
raw = "--raw" in sys.argv
if raw: sys.argv.remove("--raw")
if not raw:
    spec = importlib.util.spec_from_file_location("uv", ".claude/tools/unity-voice.py")
    uv = importlib.util.module_from_spec(spec); spec.loader.exec_module(uv)
    sys.argv[2] = uv.voice(sys.argv[2])
p = ".claude/.studio-outbox.jsonl"
mid = max(json.loads(l)["id"] for l in open(p, encoding="utf-8") if l.strip()) + 1
open(p, "a", encoding="utf-8").write(json.dumps({"id": mid, "replyTo": int(sys.argv[1]), "ts": int(time.time() * 1000),
                                                 "persona": "unity", "text": sys.argv[2]}) + "\n")
subprocess.Popen([sys.executable, ".claude/tools/unity-speak.py", "--bg", sys.argv[2]],
                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
