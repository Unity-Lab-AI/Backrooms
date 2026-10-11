"""Keep the training sources on disk (owner: "alot of this stuff u need to source and get available").

    python training/fetch_sources.py            # everything below, resumable (skips files already saved)

training/sources/rimworld-wiki/<Title>.wiki   raw wikitext of every main-namespace page of the official RimWorld wiki
training/sources/rimworld-wiki/_index.json    title -> file, with the page URL
training/sources/twitch/<slug>.html           Twitch's own creator/help/guidelines pages listed in TWITCH below
Polite: one request at a time, a pause between requests, an identifying User-Agent.
"""
import json, os, re, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "sources")
UA = {"User-Agent": "UnityAILab-training-corpus/1.0 (contact@unityailab.com)"}
WIKI = "https://rimworldwiki.com"
TWITCH = [
    "https://safety.twitch.tv/s/article/Community-Guidelines",
    "https://help.twitch.tv/s/article/how-to-use-raids",
    "https://help.twitch.tv/s/article/channel-points-guide",
    "https://help.twitch.tv/s/article/twitch-chat-badges-guide",
    "https://help.twitch.tv/s/article/how-to-manage-harassment-in-chat",
    "https://help.twitch.tv/s/article/subscription-guide",
    "https://help.twitch.tv/s/article/guide-to-cheering-with-bits",
    "https://help.twitch.tv/s/article/how-to-use-automod",
    "https://www.twitch.tv/creatorcamp/en/learn-the-basics/",
    "https://www.twitch.tv/creatorcamp/en/connect-and-engage/",
    "https://www.twitch.tv/creatorcamp/en/grow-your-community/",
]


def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read()
        except Exception as e:
            if i == tries - 1:
                print("  failed:", url, e)
                return None
            time.sleep(3 * (i + 1))


def safe(name):
    return re.sub(r"[^A-Za-z0-9 ._()\-]+", "_", name).strip()[:150]


def wiki():
    d = os.path.join(OUT, "rimworld-wiki"); os.makedirs(d, exist_ok=True)
    idx_path = os.path.join(d, "_index.json")
    idx = json.load(open(idx_path, encoding="utf-8")) if os.path.exists(idx_path) else {}
    titles, cont = [], {}
    while True:
        q = {"action": "query", "list": "allpages", "apnamespace": "0", "aplimit": "500", "apfilterredir": "nonredirects",
             "format": "json", **cont}
        raw = get(WIKI + "/api.php?" + urllib.parse.urlencode(q))
        if not raw:
            break
        j = json.loads(raw)
        titles += [p["title"] for p in j["query"]["allpages"]]
        if "continue" not in j:
            break
        cont = j["continue"]
        time.sleep(0.5)
    print("wiki pages:", len(titles), flush=True)
    for n, t in enumerate(titles, 1):
        f = safe(t) + ".wiki"
        if os.path.exists(os.path.join(d, f)):
            continue
        raw = get(WIKI + "/index.php?" + urllib.parse.urlencode({"title": t, "action": "raw"}))
        if raw:
            open(os.path.join(d, f), "wb").write(raw)
            idx[t] = {"file": f, "url": WIKI + "/wiki/" + urllib.parse.quote(t.replace(" ", "_"))}
        if n % 100 == 0:
            json.dump(idx, open(idx_path, "w", encoding="utf-8"), indent=0)
            print("  %d / %d" % (n, len(titles)), flush=True)
        time.sleep(0.35)
    json.dump(idx, open(idx_path, "w", encoding="utf-8"), indent=0)


def twitch():
    d = os.path.join(OUT, "twitch"); os.makedirs(d, exist_ok=True)
    for u in TWITCH:
        f = os.path.join(d, safe(u.rstrip("/").split("/")[-1]) + ".html")
        if not os.path.exists(f):
            raw = get(u)
            if raw:
                open(f, "wb").write(raw)
        time.sleep(1)


if __name__ == "__main__":
    twitch()
    wiki()
    print("sources saved under", OUT)
