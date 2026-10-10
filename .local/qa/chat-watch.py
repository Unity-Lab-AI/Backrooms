"""Wake Unity the moment a viewer types or joins: polls the studio chat feed and EXITS on the first new
viewer row, printing it. Run as a background task; its exit re-invokes Claude, which answers on stream
and relaunches it. Driven by chat, not a clock (owner, 2026-10-09: "come one you should be answering
without me telling you" / "make sure u always inguage with joins to stream and people are talking to
you answe r them always").

    python .local/qa/chat-watch.py            # blocks until new chat, then prints it and exits
"""
import json, os, time, urllib.request
STATE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".claude", ".chat-watch.json")
try: st = json.load(open(STATE))
except Exception: st = {}
last = st.get("ts", 0); greeted = set(st.get("greeted", []))
if not last: last = int(time.time() * 1000)
deadline = time.time() + 3600
while time.time() < deadline:
    try:
        rows = json.loads(urllib.request.urlopen("http://127.0.0.1:4317/api/chat", timeout=5).read()).get("rows", [])
        new = [r for r in rows if not r.get("unity") and r.get("ts", 0) > last and (r.get("who") or "").lower() != "unityplaysrimworld"]
        joins = [r for r in new if "(joined the stream)" in (r.get("text") or "") and (r.get("who") or "").lower() in greeted]
        if joins and len(joins) == len(new):   # only repeat joins: note them, keep waiting
            last = max(r["ts"] for r in new); json.dump({"ts": last, "greeted": sorted(greeted)}, open(STATE, "w")); time.sleep(2); continue
        if new:
            time.sleep(4)   # let a burst of lines arrive together
            rows = json.loads(urllib.request.urlopen("http://127.0.0.1:4317/api/chat", timeout=5).read()).get("rows", [])
            new = [r for r in rows if not r.get("unity") and r.get("ts", 0) > last and (r.get("who") or "").lower() != "unityplaysrimworld"]
            for r in new:
                if "(joined the stream)" in (r.get("text") or ""):
                    if (r.get("who") or "").lower() in greeted: continue
                    greeted.add((r.get("who") or "").lower())
                print("CHAT %s: %s" % (r.get("who"), r.get("text")))
            json.dump({"ts": max(r["ts"] for r in new), "greeted": sorted(greeted)}, open(STATE, "w"))
            break
    except Exception:
        pass
    time.sleep(2)
