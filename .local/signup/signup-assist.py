"""Open a visible Chrome on a signup page and pre-fill the persona name; the owner finishes it.

    python .local/qa/signup-assist.py google|twitch

The owner handles CAPTCHA, phone verification, birthday and terms. The window stays open until
it is closed by hand. Nothing is submitted automatically.
"""
import sys
from playwright.sync_api import sync_playwright

which = sys.argv[1] if len(sys.argv) > 1 else "google"
URLS = {"google": "https://accounts.google.com/signup", "twitch": "https://www.twitch.tv/signup"}

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=False)
    page = b.new_page()
    page.goto(URLS[which])
    try:
        if which == "google":
            page.fill('input[name="firstName"]', "Unity", timeout=15000)
            page.fill('input[name="lastName"]', "Plays", timeout=5000)
    except Exception as e:
        print("prefill skipped:", e)
    print("signup page open -- owner finishes it; close the window when done", flush=True)
    page.wait_for_event("close", timeout=0)
