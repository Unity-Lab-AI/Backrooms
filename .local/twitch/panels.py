"""Add the channel's About panels from docs/TWITCH_PANELS.md (separate Twitch window, CDP 9333).
Edit Panels must already be switched on. python .local/twitch/panels.py"""
import re
from playwright.sync_api import sync_playwright

ROOT = "C:/Users/gfour/Desktop/Backrooms/"
md = open(ROOT + "docs/TWITCH_PANELS.md", encoding="utf-8").read()
text = {int(n): (t, body.strip()) for n, t, body in
        re.findall(r"## Panel (\d) — Title: `([^`]*)`\s*```\n(.*?)```", md, re.S)}
S = "https://g-fourteen.github.io/Rimrooms-AsyncIndustries/"
ICONS = [("site", S, "Rimrooms mod site and wiki"), ("install", S + "install.html", "Install guide"),
         ("modlist", S + "mods-list.html", "Mod list"), ("source", "https://github.com/Unity-Lab-AI/Backrooms", "Source code on GitHub"),
         ("bugs", "https://github.com/Unity-Lab-AI/Backrooms/issues", "Report a bug"), ("workshop", "", "Steam Workshop collection, coming soon")]
PANELS = [dict(title=text[1][0], desc=text[1][1])]
PANELS += [dict(image=ROOT + "docs/twitch-panels/panel-%s.png" % k, url=u, alt=a) for k, u, a in ICONS]
PANELS += [dict(title=text[n][0], desc=text[n][1]) for n in (2, 3, 4, 5)]

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9333")
    pg = [x for c in b.contexts for x in c.pages if "twitch" in x.url][-1]
    import sys
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    for i, pn in enumerate(PANELS):
        if i < start: continue
        pg.locator("path[d^='M11 13v6']").last.click(timeout=10000); pg.wait_for_timeout(800)
        pg.get_by_text("Add a Text or Image Panel").last.click(timeout=10000); pg.wait_for_timeout(1200)
        if pn.get("title"): pg.locator("#panel-title").last.fill(pn["title"])
        if pn.get("image"):
            pg.get_by_role("button", name="Add Image", exact=True).last.click(); pg.wait_for_timeout(1200)
            pg.locator("input[type=file]").last.set_input_files(pn["image"]); pg.wait_for_timeout(2500)
            pg.get_by_role("button", name="Done", exact=True).last.click(timeout=10000); pg.wait_for_timeout(2500)
        if pn.get("url"): pg.locator("#panel-link-url").last.fill(pn["url"])
        if pn.get("alt"): pg.locator("#panel-image-description").last.fill(pn["alt"])
        if pn.get("desc"): pg.locator("#description").last.fill(pn["desc"])
        pg.get_by_role("button", name="Submit", exact=True).last.click(timeout=10000)
        pg.wait_for_timeout(2500)
        print("panel", i + 1, pn.get("title") or pn.get("alt"))
    pg.screenshot(path=ROOT + ".local/twitch/panels-done.png", full_page=True)
