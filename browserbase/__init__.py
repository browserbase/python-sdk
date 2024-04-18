import os
from typing import Optional, Sequence, Union
from playwright.sync_api import sync_playwright


class Browserbase:
    def __init__(self, api_key: Optional[str] = None):
        """Create new Browserbase SDK client instance"""
        self.api_key = api_key or os.environ["BROWSERBASE_API_KEY"]

    def load(self, url: Union[str, Sequence[str]], **args):
        if isinstance(url, str):
            return self.load_url(url, **args)
        elif isinstance(url, Sequence):
            return self.load_urls(url, **args)
        else:
            raise TypeError("Input must be a URL string or a Sequence of URLs")

    def load_url(self, url: str, text_content: bool = False):
        """Load a page in a headless browser and return the contents"""
        if not url:
            raise ValueError("Page URL was not provided")

        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(
                "wss://api.browserbase.com?apiKey=" + self.api_key
            )
            default_context = browser.contexts[0]
            page = default_context.pages[0]
            page.goto(url)
            html = page.content()
            if text_content:
                readable = page.evaluate("""async () => {
                  const readability = await import('https://cdn.skypack.dev/@mozilla/readability');
                  return (new readability.Readability(document)).parse();
                }""")

                html = f"{readable['title']}\n{readable['textContent']}"
            browser.close()

            return html

    def load_urls(self, urls: Sequence[str], text_content: bool = False):
        """Load multiple pages in a headless browser and return the contents"""
        if not urls:
            raise ValueError("Page URL was not provided")

        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(
                "wss://api.browserbase.com?apiKey=" + self.api_key
            )

            default_context = browser.contexts[0]
            page = default_context.pages[0]

            for url in urls:
                page.goto(url)
                html = page.content()
                if text_content:
                    readable = page.evaluate("""async () => {
                      const readability = await import('https://cdn.skypack.dev/@mozilla/readability');
                      return (new readability.Readability(document)).parse();
                    }""")

                    html = f"{readable['title']}\n{readable['textContent']}"
                yield html

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
