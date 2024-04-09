from playwright.sync_api import sync_playwright

class Browserbase:
    # Create new Browserbase instance
    def __init__(self, api_key: str):
      if not api_key:
        raise ValueError("Browserbase API key was not provided")

      self.api_key = api_key

    # Load a page in a headless browser and return the html contents
    def load(self, url: str):
        if not url:
          raise ValueError("Page URL was not provided")

        with sync_playwright() as p:
          browser = p.chromium.connect_over_cdp("wss://api.browserbase.com?apiKey=" + self.api_key)
          page = browser.new_page()
          page.goto(url)
          html = page.content()
          browser.close()

          return html
