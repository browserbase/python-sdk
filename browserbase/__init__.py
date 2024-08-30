import os
import httpx
import time
from typing import Optional, Sequence, Union, Literal, Generator
from enum import Enum
from pydantic import BaseModel
from playwright.sync_api import sync_playwright, Browser, Playwright
from contextlib import contextmanager
from functools import wraps
from .helpers.utils import is_running_in_jupyter
import json
from uuid import uuid4
from .models import *


class Browserbase:
    def __init__(
        self,
        api_key: Optional[str] = None,
        project_id: Optional[str] = None,
        api_url: Optional[str] = None,
        connect_url: Optional[str] = None,
    ):
        """Create new Browserbase SDK client instance"""
        self.api_key = api_key or os.environ["BROWSERBASE_API_KEY"]
        self.project_id = project_id or os.environ["BROWSERBASE_PROJECT_ID"]
        self.connect_url = connect_url or "wss://connect.browserbase.com"
        self.api_url = api_url or "https://www.browserbase.com"
        self.sessions = {}

    def get_connect_url(
        self, session_id: Optional[str] = None, proxy: Optional[bool] = None
    ):
        base_url = f"{self.connect_url}?apiKey={self.api_key}"
        if session_id:
            base_url += f"&sessionId={session_id}"
        if proxy:
            base_url += "&enableProxy=true"
        return base_url

    def get_session(self, session_id: str) -> Session:
        return session_service.get_session(self.api_key, session_id)

    def list_sessions(self) -> list[Session]:
        return session_service.list_sessions(self.api_key)

    def create_session(
        self,
        options: Optional[BrowserSettings] = None,
        extension_id: Optional[str] = None,
        timeout: Optional[int] = None,
        keep_alive: bool = False,
        proxies: Union[bool, List[Proxy], List[GeolocationProxy]] = False,
    ) -> Session:
        return session_service.create_session(
            self.project_id,
            self.api_key,
            options,
            extension_id,
            timeout,
            keep_alive,
            proxies,
        )

    def update_session(self, session_id: str) -> Session:
        return session_service.update_session(
            self.project_id, self.api_key, session_id, "REQUEST_RELEASE"
        )

    def complete_session(self, session_id: str) -> Session:
        return self.update_session(session_id)

    def debug_session(self, session_id: str) -> DebugSession:
        return session_service.debug_session(self.api_key, session_id)

    def get_session_downloads(
        self, session_id: str, retry_interval: int = 2000, retry_count: int = 2
    ) -> Optional[bytes]:
        def fetch_download():
            nonlocal retry_count

            response = httpx.get(
                f"{self.api_url}/v1/sessions/{session_id}/downloads",
                headers={
                    "x-bb-api-key": self.api_key,
                },
            )
            content = response.read()
            if len(content) > 0:
                return content
            else:
                retry_count -= 1
                if retry_count <= 0:
                    return None
                time.sleep(retry_interval / 1000)
                return fetch_download()

        return fetch_download()

    def load(self, url: Union[str, Sequence[str]], **args):
        if isinstance(url, str):
            return self.load_url(url, **args)
        elif isinstance(url, Sequence):
            return self.load_urls(url, **args)
        else:
            raise TypeError("Input must be a URL string or a Sequence of URLs")

    def load_url(
        self,
        url: str,
        text_content: bool = False,
        session_id: Optional[str] = None,
        proxy: Optional[bool] = None,
    ):
        """Load a page in a headless browser and return the contents"""
        if not url:
            raise ValueError("Page URL was not provided")

        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(
                self.get_connect_url(session_id, proxy)
            )
            default_context = browser.contexts[0]
            page = default_context.pages[0]
            page.goto(url)
            html = page.content()
            if text_content:
                readable = page.evaluate(
                    """async () => {
				  const readability = await import('https://cdn.skypack.dev/@mozilla/readability');
				  return (new readability.Readability(document)).parse();
				}"""
                )

                html = f"{readable['title']}\n{readable['textContent']}"
            browser.close()

            return html

    def load_urls(
        self,
        urls: Sequence[str],
        text_content: bool = False,
        session_id: Optional[str] = None,
        proxy: Optional[bool] = None,
    ):
        """Load multiple pages in a headless browser and return the contents"""
        if not urls:
            raise ValueError("Page URL was not provided")

        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(
                self.get_connect_url(session_id, proxy)
            )

            default_context = browser.contexts[0]
            page = default_context.pages[0]

            for url in urls:
                page.goto(url)
                html = page.content()
                if text_content:
                    readable = page.evaluate(
                        """async () => {
					  const readability = await import('https://cdn.skypack.dev/@mozilla/readability');
					  return (new readability.Readability(document)).parse();
					}"""
                    )

                    html = f"{readable['title']}\n{readable['textContent']}"
                yield html

            browser.close()

    def screenshot(
        self,
        url: str,
        full_page: bool = False,
        session_id: Optional[str] = None,
        proxy: Optional[bool] = None,
    ):
        """Load a page in a headless browser and return a screenshot as bytes"""
        if not url:
            raise ValueError("Page URL was not provided")

        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(
                self.get_connect_url(session_id, proxy)
            )

            page = browser.new_page()
            page.goto(url)
            screenshot = page.screenshot(full_page=full_page)
            browser.close()

            return screenshot

    def selenium(
        self, func, session_id: Optional[str] = None, proxy: Optional[bool] = None
    ):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Add imports here to avoid unnecesary dependencies
            from selenium import webdriver
            from selenium.webdriver.remote.remote_connection import RemoteConnection
            from selenium.webdriver.common.desired_capabilities import (
                DesiredCapabilities,
            )

            class CustomRemoteConnection(RemoteConnection):
                _session_id = None

                def __init__(self, remote_server_addr: str, session_id: str):
                    super().__init__(remote_server_addr)
                    self._session_id = session_id

                def get_remote_connection_headers(self, parsed_url, keep_alive=False):
                    headers = super().get_remote_connection_headers(
                        parsed_url, keep_alive
                    )
                    headers.update({"x-bb-api-key": os.environ["BROWSERBASE_API_KEY"]})
                    headers.update({"session-id": self._session_id})
                    return headers

            nonlocal session_id, proxy
            if not session_id:
                session = self.create_session()
                session_id = session.id

            enable_proxy = "?enableProxy=true" if proxy else ""
            custom_conn = CustomRemoteConnection(
                "http://connect.browserbase.com/webdriver" + enable_proxy, session_id
            )
            options = webdriver.ChromeOptions()
            driver = webdriver.Remote(custom_conn, options=options)
            result = func(driver, *args, **kwargs)
            driver.quit()
            self.complete_session(session_id)
            self.sessions[func.__name__] = session_id
            while True:
                session = self.get_session(session_id)
                if session.status == "COMPLETED":
                    break
                time.sleep(1)
            if result is None and is_running_in_jupyter():
                return self.get_session_recording(session_id)
            return result

        return wrapper

    @contextmanager
    def init_playwright(
        self,
        session_id: Optional[str] = None,
        proxy: Optional[bool] = None,
    ) -> Generator[Browser, None, None]:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(
                self.get_connect_url(session_id, proxy)
            )
            yield browser

    def record_rrweb(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            browser = args[0]  # Assuming the first argument is the browser object
            page = browser.new_page()

            # Inject rrweb script
            page.add_script_tag(
                url="https://cdn.jsdelivr.net/npm/rrweb@latest/dist/rrweb.min.js"
            )

            # Start recording
            page.evaluate(
                """
				window.events = [];
				rrweb.record({
					emit: event => window.events.push(event)
				});
			"""
            )

            # Run the original function
            result = func(*args, **kwargs)

            # Stop recording and save events
            events = page.evaluate("window.events")
            with open("rrweb.json", "w") as f:
                json.dump(events, f)

            return result

        return wrapper
