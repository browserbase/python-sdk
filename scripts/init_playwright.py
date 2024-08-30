# %%
from dotenv import load_dotenv
import os
from browserbase import Browserbase
import time
import asyncio

load_dotenv()

BROWSERBASE_API_KEY = os.environ["BROWSERBASE_API_KEY"]
BROWSERBASE_PROJECT_ID = os.environ["BROWSERBASE_PROJECT_ID"]

bb = Browserbase(api_key=BROWSERBASE_API_KEY, project_id=BROWSERBASE_PROJECT_ID)


@bb.async_playwright
async def run_browser(browser):
    page = await browser.new_page()
    await page.goto("http://example.com")
    # other actions...
    await asyncio.sleep(10)
    await page.goto("http://browserbase.com")
    await asyncio.sleep(10)


# await run_browser()
# %%
