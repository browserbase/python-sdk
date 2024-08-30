from dotenv import load_dotenv
import os
from browserbase import Browserbase

load_dotenv()

BROWSERBASE_API_KEY = os.environ["BROWSERBASE_API_KEY"]
BROWSERBASE_PROJECT_ID = os.environ["BROWSERBASE_PROJECT_ID"]

bb = Browserbase(BROWSERBASE_API_KEY, BROWSERBASE_PROJECT_ID)

# session = bb.get_session("2a2960b2-34eb-4a87-83a5-09c9c5d0b87f")
# print(session)

sess = bb.create_session()
print(sess)

bb.debug_session(sess.id)
bb.complete_session(sess.id)
