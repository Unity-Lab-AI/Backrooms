"""Moderate the stream's chat from the separate logged-in Twitch browser (CDP 9333). Owner, 2026-10-09 (chat):
"viewer bots posting links is what she mean kick/ban those Unity".   twitch-mod.py ban USER [reason]"""
import sys, time
from playwright.sync_api import sync_playwright
cmd, user = sys.argv[1], sys.argv[2]; reason = " ".join(sys.argv[3:]) or "spam bot"
with sync_playwright() as p:
    br = p.chromium.connect_over_cdp("http://127.0.0.1:9333")
    ctx = br.contexts[0]
    page = next((pg for pg in ctx.pages if "twitch.tv/popout/unityplaysrimworld/chat" in pg.url), None)
    if page is None:
        page = ctx.new_page(); page.goto("https://www.twitch.tv/popout/unityplaysrimworld/chat", wait_until="domcontentloaded"); time.sleep(6)
    box = page.locator('[data-a-target="chat-input"]').first
    box.click(); box.type("/%s %s %s" % (cmd, user, reason) if cmd == "ban" else "/%s %s" % (cmd, user), delay=20)
    time.sleep(0.8); page.keyboard.press("Enter"); time.sleep(1.5)
    # a slash command may open a confirm card; accept it if present
    for sel in ('button:has-text("Ban")', 'button:has-text("Confirm")'):
        b = page.locator(sel)
        if b.count(): b.first.click(); break
    time.sleep(1); print("sent /%s %s" % (cmd, user), "url", page.url)
