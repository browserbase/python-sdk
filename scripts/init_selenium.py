from dotenv import load_dotenv
import os
from browserbase import Browserbase

load_dotenv()

BROWSERBASE_API_KEY = os.environ["BROWSERBASE_API_KEY"]
BROWSERBASE_PROJECT_ID = os.environ["BROWSERBASE_PROJECT_ID"]

bb = Browserbase(api_key=BROWSERBASE_API_KEY, project_id=BROWSERBASE_PROJECT_ID)
IS_LOCAL = True


@bb.selenium
def get_title(driver):
    pass


get_title()
