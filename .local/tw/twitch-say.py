"""Type into the real Twitch chat as Unity, and set the stream's title and category.

Owner, 2026-10-10, verbatim: *"and Unity knows how to work twich and start new streams and talk in chat"*.

Before this, she could only READ Twitch chat (the bridge pipes it into her inbox) and speak out loud on the
broadcast. She could not put a word in the actual chat box, and could not name the stream. Both of those are
done here through the same logged-in browser `twitch-mod.py` already uses (CDP on 9333), so no API keys, no
extra login, nothing stored.

    python .local/tw/twitch-say.py say "hey, welcome in"
    python .local/tw/twitch-say.py reply RoomsIdleHands "good question -- the wall goes up first"
    python .local/tw/twitch-say.py title "Unity Plays RimWorld -- company start, fresh colony"
    python .local/tw/twitch-say.py category "RimWorld"
    python .local/tw/twitch-say.py golive "Unity Plays RimWorld -- company start"   (title + category + OBS)

THE STREAM IS CLEAN: every line is filtered the same way her spoken lines are -- no profanity, nothing
degrading, no links, no @everyone. A line that fails the filter is refused, not softened.
"""
import os, re, subprocess, sys, time

CHANNEL = os.environ.get("TWITCH_CHANNEL", "unityplaysrimworld")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIRTY = re.compile(r"\b(fuck|shit|bitch|damn|ass|hell|cunt|slut|whore|retard|stupid|dumb|ugly|kys)\b", re.I)
LINKY = re.compile(r"(https?://|www\.|\.com\b|\.gg\b|@everyone|@here)", re.I)

def clean(line):
    line = (line or "").strip()
    if not line: raise SystemExit("refused: empty line")
    if len(line) > 450: line = line[:447] + "..."
    if DIRTY.search(line): raise SystemExit("refused: the stream is clean -- %r" % line[:60])
    if LINKY.search(line): raise SystemExit("refused: no links in chat -- %r" % line[:60])
    return line

def page_for(ctx, url_part, url):
    pg = next((p for p in ctx.pages if url_part in p.url), None)
    if pg is None:
        pg = ctx.new_page(); pg.goto(url, wait_until="domcontentloaded"); time.sleep(6)
    return pg

def main():
    what = (sys.argv[1] if len(sys.argv) > 1 else "").lower()
    if what not in ("say", "reply", "title", "category", "golive"):
        raise SystemExit(__doc__)

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.connect_over_cdp("http://127.0.0.1:9333")
        ctx = br.contexts[0]

        if what in ("say", "reply"):
            text = clean(" ".join(sys.argv[2:]) if what == "say"
                         else "@%s %s" % (sys.argv[2], " ".join(sys.argv[3:])))
            pg = page_for(ctx, "twitch.tv/popout/%s/chat" % CHANNEL,
                          "https://www.twitch.tv/popout/%s/chat" % CHANNEL)
            box = pg.locator('[data-a-target="chat-input"]').first
            box.click(); box.type(text, delay=18); time.sleep(0.5)
            pg.keyboard.press("Enter"); time.sleep(1)
            print("said in chat:", text)
            return

        # title and category live on the creator dashboard's stream manager
        pg = page_for(ctx, "dashboard.twitch.tv", "https://dashboard.twitch.tv/u/%s/stream-manager" % CHANNEL)
        edit = pg.locator('button:has-text("Edit Stream Info"), [aria-label*="Edit Stream Info"]').first
        if edit.count(): edit.click(); time.sleep(2)

        if what in ("title", "golive"):
            title = clean(" ".join(sys.argv[2:]) or "Unity Plays RimWorld")
            box = pg.locator('#edit-broadcast-title-formgroup, [data-a-target="stream-title-field"]').first
            if box.count():
                box.click(); box.fill(""); box.type(title, delay=12); print("title set:", title)
            else:
                raise SystemExit("refused: the title box was not found -- nothing saved")

        if what in ("category", "golive"):
            cat = " ".join(sys.argv[2:]) if what == "category" else "RimWorld"
            box = pg.locator('#Category-Selector, [data-a-target="stream-game-field"]').first
            if box.count():
                box.click(); box.fill(""); box.type(cat, delay=12); time.sleep(2)
                pg.keyboard.press("ArrowDown"); pg.keyboard.press("Enter"); print("category set:", cat)

        done = pg.locator('button:has-text("Done"), button:has-text("Save")').first
        if done.count(): done.click(); time.sleep(1.5); print("stream info saved")

        if what == "golive":
            # going live is OBS's job; the switch already launches it with --startstreaming
            r = subprocess.run([sys.executable, os.path.join(ROOT, "stream", "services.py"), "start"],
                               capture_output=True, text=True, timeout=900,
                               creationflags=0x08000000 if os.name == "nt" else 0)
            print("stack:", " | ".join(l for l in r.stdout.splitlines() if "obs" in l.lower())[:120])

main()
