import unittest
from browserbase import Browserbase, UpdateSessionOptions


class BrowserbaseTestCase(unittest.TestCase):
    def setUp(self):
        self.browserbase = Browserbase()

    def test_create_get_session(self):
        session = self.browserbase.create_session()
        result = self.browserbase.get_session(session.id)
        self.assertEqual(result.status, "RUNNING")

    def test_list_sessions(self):
        result = self.browserbase.list_sessions()
        self.assertEqual(result[0].status, "RUNNING")

    def test_update_session(self):
        session = self.browserbase.create_session()

        result = self.browserbase.update_session(
            session.id,
            options=UpdateSessionOptions(
                status="REQUEST_RELEASE",
            ),
        )
        self.assertEqual(result.status, "COMPLETED")

    def test_session_recording(self):
        session = self.browserbase.create_session()

        result = self.browserbase.get_session_recording(session.id)
        self.assertEqual(len(result), 0)

    def test_debug_connection_urls(self):
        session = self.browserbase.create_session()
        result = self.browserbase.get_debug_connection_urls(session.id)

    def test_load(self):
        result = self.browserbase.load("https://example.com")
        self.assertIn("Example Domain", result)

    def test_load_text(self):
        result = self.browserbase.load("https://example.com/", text_content=True)
        self.assertIn("Example Domain", result)

    def test_load_urls(self):
        result = next(self.browserbase.load_urls(["https://example.com"]))
        self.assertIn("Example Domain", result)

    def test_screenshot(self):
        result = self.browserbase.screenshot("https://example.com")
        self.assertEqual(29806, len(result))


if __name__ == "__main__":
    unittest.main()
