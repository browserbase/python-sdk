from dotenv import load_dotenv
import os
from playwright.sync_api import sync_playwright, Playwright
import time
from browserbase import Browserbase

load_dotenv()

BROWSERBASE_API_KEY = os.environ["BROWSERBASE_API_KEY"]
BROWSERBASE_PROJECT_ID = os.environ["BROWSERBASE_PROJECT_ID"]

bb = Browserbase(api_key=BROWSERBASE_API_KEY, project_id=BROWSERBASE_PROJECT_ID)
IS_LOCAL = True

def run(playwright: Playwright):
    browser = bb.init_playwright(playwright, is_local=IS_LOCAL)
    page = browser.new_page()
    page.goto("http://example.com")
    # other actions...
    if IS_LOCAL:
        time.sleep(5)
    browser.close()

with sync_playwright() as playwright:
    run(playwright)