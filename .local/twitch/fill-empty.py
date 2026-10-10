"""Fill one blank panel form (by index) with an image + link. python fill-empty.py INDEX key url alt"""
import sys
from playwright.sync_api import sync_playwright
i, key, url, alt = int(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
F = "C:/Users/gfour/Desktop/Backrooms/docs/twitch-panels/panel-%s.png" % key
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9333")
    pg = [x for c in b.contexts for x in c.pages if "twitch" in x.url][-1]
    box = pg.locator("#panel-link-url").nth(i).locator("xpath=ancestor::*[8]")
    box.scroll_into_view_if_needed()
    box.get_by_role("button", name="Add Image", exact=True).click(); pg.wait_for_timeout(1500)
    pg.locator("input[type=file]").last.set_input_files(F); pg.wait_for_timeout(3000)
    pg.get_by_role("button", name="Done", exact=True).last.click(); pg.wait_for_timeout(5000)
    box.locator("#panel-link-url").fill(url); box.locator("#panel-image-description").fill(alt); pg.wait_for_timeout(500)
    btns = box.locator("button")
    for k in range(btns.count()):
        if btns.nth(k).inner_text().strip() == "Submit":
            print("submit enabled", btns.nth(k).is_enabled()); btns.nth(k).click(); break
    pg.wait_for_timeout(5000)
    print("now:", [btns.nth(k).inner_text().strip() for k in range(btns.count())], box.locator("img").count(), "img")
