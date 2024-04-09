import unittest
import os
from browserbase import Browserbase


class BrowserbaseTestCase(unittest.TestCase):
    def setUp(self):
        self.browserbase = Browserbase(os.environ["BROWSERBASE_KEY"])

    def test_load(self):
        result = self.browserbase.load("https://example.com")
        self.assertIn("Example Domain", result)


if __name__ == "__main__":
    unittest.main()
