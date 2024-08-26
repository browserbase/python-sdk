from dotenv import load_dotenv
import os
from browserbase import Browserbase

load_dotenv()

BROWSERBASE_API_KEY = os.environ["BROWSERBASE_API_KEY"]
BROWSERBASE_PROJECT_ID = os.environ["BROWSERBASE_PROJECT_ID"]

bb = Browserbase(api_key=BROWSERBASE_API_KEY, project_id=BROWSERBASE_PROJECT_ID)
IS_LOCAL = True

with bb.init_selenium() as driver:
    driver.get("https://www.browserbase.com")
    get_title = driver.title
    print(get_title)
