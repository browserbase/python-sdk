from dotenv import load_dotenv
import os
from browserbase import Browserbase
import time

load_dotenv()

BROWSERBASE_API_KEY = os.environ["BROWSERBASE_API_KEY"]
BROWSERBASE_PROJECT_ID = os.environ["BROWSERBASE_PROJECT_ID"]

bb = Browserbase(api_key=BROWSERBASE_API_KEY, project_id=BROWSERBASE_PROJECT_ID)

with bb.init_playwright() as browser:
    page = browser.new_page()
    page.goto("http://example.com")
    # other actions...
    time.sleep(5)
    page.goto("http://browserbase.com")
    time.sleep(10)
