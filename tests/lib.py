import unittest
import os
from browserbase import Browserbase


class BrowserbaseTestCase(unittest.TestCase):
    def setUp(self):
        self.browserbase = Browserbase(os.environ["BROWSERBASE_KEY"])

    def test_load(self):
        result = self.browserbase.load("https://example.com")
        self.assertIn("Example Domain", result)

    def test_load_urls(self):
        result = self.browserbase.load_urls(["https://example.com"])
        self.assertIn("Example Domain", result[0])

    def test_screenshot(self):
        result = self.browserbase.screenshot("https://example.com")
        print(result)
        self.assertIn("Example Domain", result)


if __name__ == "__main__":
    unittest.main()
