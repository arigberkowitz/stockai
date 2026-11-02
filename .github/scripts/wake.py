"""Open the StockIQ app in a real (headless) browser so Streamlit Community Cloud
keeps it awake. If the app is already asleep, click the wake-up button and wait
for it to boot. Exits non-zero if the app never loads, so failures show up in
the Actions tab."""
import os, sys
from playwright.sync_api import sync_playwright

URL = os.environ.get("APP_URL", "https://stockai-2adqr977bvhhsgg9qm63vc.streamlit.app/")
WAKE_TEXT = "Yes, get this app back up"

def app_loaded(page):
    # The Streamlit app itself runs inside an iframe on *.streamlit.app
    for frame in page.frames:
        if "/~/+/" not in frame.url:
            continue
        try:
            if frame.locator("text=StockIQ").count() > 0:
                return True
        except Exception:
            pass
    return False

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(URL, wait_until="domcontentloaded", timeout=90_000)
    page.wait_for_timeout(10_000)
    btn = page.get_by_role("button", name=WAKE_TEXT)
    if btn.count() > 0:
        print("App was asleep, clicking wake button")
        btn.first.click()
    else:
        print("App was awake")
    for _ in range(36):  # up to ~3 minutes for a cold boot
        if app_loaded(page):
            print("App loaded OK")
            browser.close()
            sys.exit(0)
        page.wait_for_timeout(5_000)
    print("App did not finish loading")
    browser.close()
    sys.exit(1)
