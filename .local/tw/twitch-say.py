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

def page_for(ctx, url_parts, url):
    """Use a Twitch tab that is already open. Owner, 2026-10-10: "what ever keep opening new twich pages is
    piossing me off use the open ones". A new tab is opened only if no matching one exists, and duplicates of
    the same kind are closed so they never pile up."""
    if isinstance(url_parts, str): url_parts = (url_parts,)
    hits = [p for p in ctx.pages if any(u in p.url for u in url_parts)]
    for extra in hits[1:]:
        try: extra.close()
        except Exception: pass
    if hits: return hits[0]
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
            pg = page_for(ctx, ("twitch.tv/popout/%s/chat" % CHANNEL, "twitch.tv/%s" % CHANNEL),
                          "https://www.twitch.tv/popout/%s/chat" % CHANNEL)
            box = pg.locator('[data-a-target="chat-input"]').first
            box.click(); box.type(text, delay=18); time.sleep(0.5)
            pg.keyboard.press("Enter"); time.sleep(1)
            print("said in chat:", text)
            return

        # title and category live on the creator dashboard's stream manager
        # the STREAM MANAGER tab, not any dashboard tab: run 3 (2026-10-13 21:29) matched a settings/about tab that was
        # open, which has no "Edit Stream Info", and the title was refused three times on stream
        sm = "https://dashboard.twitch.tv/u/%s/stream-manager" % CHANNEL
        pg = page_for(ctx, "stream-manager", sm)
        if "stream-manager" not in pg.url:
            pg.goto(sm, wait_until="domcontentloaded"); time.sleep(6)
        # the Edit Stream Info modal may already be open (a previous call that did not reach Done, or a hand on the
        # window): clicking the button again then hits the modal's backdrop and every click retries until it times
        # out (run 3, 21:33-21:34: "stuck behind a modal"). Open it only when its title box is not already there.
        if not pg.locator('#edit-broadcast-title-formgroup').count():
            # by ROLE: the css "button:has-text / [aria-label*=]" pair also matched a hidden node first, and the click
            # waited 30 s for it to become visible (run 3, 21:29-21:36, every title and category call)
            edit = pg.get_by_role("button", name="Edit Stream Info").first
            if edit.count():
                # a pointer click lands on whatever covers the button in the stream-manager layout (run 3, 21:36:
                # visible, box at y=1023, click and force-click both left the modal closed); the element's own click
                # event opens it every time
                try: edit.click(timeout=5000); time.sleep(1.5)
                except Exception: pass
                if not pg.locator('#edit-broadcast-title-formgroup').count():
                    edit.dispatch_event("click"); time.sleep(2)
                if not pg.locator('#edit-broadcast-title-formgroup').count():
                    raise SystemExit("refused: Edit Stream Info did not open its form -- try again")
            else: raise SystemExit("refused: the stream manager page has no Edit Stream Info button yet -- try again in a few seconds")

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
            try: current = box.input_value(timeout=3000) if box.count() else ""
            except Exception: current = ""
            if current.strip().lower() == cat.strip().lower():
                print("category already", current)      # the field stays hidden until it is changed; nothing to type
            elif box.count():
                # the same covered-element problem as the Edit button: focus it directly, never wait on a pointer click
                box.scroll_into_view_if_needed(timeout=4000)
                try: box.click(timeout=4000)
                except Exception: box.evaluate("e => e.focus()")
                try: box.fill("", timeout=4000)
                except Exception: pg.keyboard.press("Control+A"); pg.keyboard.press("Backspace")
                pg.keyboard.type(cat, delay=12); time.sleep(2)
                pg.keyboard.press("ArrowDown"); pg.keyboard.press("Enter"); print("category set:", cat)
            else:
                raise SystemExit("refused: the category box was not found -- nothing saved")

        done = pg.get_by_role("button", name="Done").first
        if not done.count(): done = pg.get_by_role("button", name="Save").first
        if done.count():
            try: done.click(timeout=8000)
            except Exception: done.click(force=True, timeout=8000)
            time.sleep(1.5); print("stream info saved")
        if pg.locator('#edit-broadcast-title-formgroup').count():
            pg.keyboard.press("Escape"); raise SystemExit("refused: the stream info modal did not close after Done -- nothing is confirmed saved; try again")

        if what == "golive":
            # going live is OBS's job; the switch already launches it with --startstreaming
            r = subprocess.run([sys.executable, os.path.join(ROOT, "stream", "services.py"), "start"],
                               capture_output=True, text=True, timeout=900,
                               creationflags=0x08000000 if os.name == "nt" else 0)
            print("stack:", " | ".join(l for l in r.stdout.splitlines() if "obs" in l.lower())[:120])

main()
