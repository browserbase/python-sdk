from typing import List
from playwright.sync_api import sync_playwright


class Browserbase:
    def __init__(self, api_key: str):
        """Create new Browserbase instance"""
        if not api_key:
            raise ValueError("Browserbase API key was not provided")

        self.api_key = api_key

    def load(self, url: str):
        """Load a page in a headless browser and return the html contents"""
        if not url:
            raise ValueError("Page URL was not provided")

        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(
                "wss://api.browserbase.com?apiKey=" + self.api_key
            )
            page = browser.new_page()
            page.goto(url)
            html = page.content()
            browser.close()

            return html

    def load_urls(self, urls: List[str]):
        """Load multiple pages in a headless browser and return the html contents"""
        if not urls:
            raise ValueError("Page URL was not provided")

        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(
                "wss://api.browserbase.com?apiKey=" + self.api_key
            )

            for url in urls:
                page = browser.new_page()
                page.goto(url)
                yield page.content()

            browser.close()

    def screenshot(self, url: str, full_page: bool = False):
        """Load a page in a headless browser and return a screenshot as bytes"""
        if not url:
            raise ValueError("Page URL was not provided")

        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(
                "wss://api.browserbase.com?apiKey=" + self.api_key
            )
            page = browser.new_page()
            page.goto(url)
            screenshot = page.screenshot(full_page=full_page)
            browser.close()

            return screenshot
