"""Read the last chat lines of a channel's popout chat in the stream browser (read-only).
    python read-chat.py <channel> [n]"""
import json, sys
from playwright.sync_api import sync_playwright
ch = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 15
with sync_playwright() as p:
    ctx = p.chromium.connect_over_cdp("http://127.0.0.1:9333").contexts[0]
    pg = next((q for q in ctx.pages if ("popout/%s/chat" % ch) in q.url), None)
    if pg is None:
        pg = ctx.new_page(); pg.goto("https://www.twitch.tv/popout/%s/chat" % ch); pg.wait_for_timeout(4000)
    rows = pg.eval_on_selector_all('[data-a-target="chat-line-message"], .chat-line__message',
        "els => els.map(e => { const u = e.querySelector('[data-a-target=\"chat-message-username\"], .chat-author__display-name');"
        " const t = e.querySelector('[data-a-target=\"chat-line-message-body\"], .message'); "
        " return [u ? u.innerText : '', t ? t.innerText : e.innerText]; })")
    print(json.dumps(rows[-n:], ensure_ascii=False))
