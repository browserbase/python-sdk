import os
import httpx
import time
from typing import Optional, Sequence, Union, Literal
from enum import Enum
from pydantic import BaseModel
from playwright.sync_api import sync_playwright


BrowserType = Literal["chrome", "firefox", "edge", "safari"]
DeviceType = Literal["desktop", "mobile"]
OperatingSystem = Literal["windows", "macos", "linux", "ios", "android"]
SessionStatus = Literal[
    "NEW", "CREATED", "ERROR", "RUNNING", "REQUEST_RELEASE", "RELEASING", "COMPLETED"
]


class Screen(BaseModel):
    maxHeight: Optional[int] = None
    maxWidth: Optional[int] = None
    minHeight: Optional[int] = None
    minWidth: Optional[int] = None


class Fingerprint(BaseModel):
    browserListQuery: Optional[str] = None
    httpVersion: Optional[int] = None
    browsers: Optional[list[BrowserType]] = None
    devices: Optional[list[DeviceType]] = None
    locales: Optional[list[str]] = None
    operatingSystems: Optional[list[OperatingSystem]] = None
    screen: Optional[Screen] = None


class Viewport(BaseModel):
    width: Optional[int] = None
    height: Optional[int] = None


class BrowserSettings(BaseModel):
    fingerprint: Optional[Fingerprint] = None
    viewport: Optional[Viewport] = None


class CreateSessionOptions(BaseModel):
    projectId: Optional[str] = None
    extensionId: Optional[str] = None
    browserSettings: Optional[BrowserSettings] = None


class Session(BaseModel):
    id: str
    createdAt: str
    startedAt: str
    endedAt: Optional[str]
    projectId: str
    status: Optional[SessionStatus] = None
    taskId: Optional[str] = None
    proxyBytes: Optional[int] = None
    expiresAt: Optional[str] = None
    avg_cpu_usage: Optional[float] = None
    memory_usage: Optional[int] = None
    details: Optional[str] = None
    logs: Optional[str] = None


class SessionRecording(BaseModel):
    type: Optional[str] = None
    time: Optional[str] = None
    data: Optional[dict] = None


class DebugConnectionURLs(BaseModel):
    debuggerFullscreenUrl: Optional[str] = None
    debuggerUrl: Optional[str] = None
    wsUrl: Optional[str] = None


class Request(BaseModel):
    timestamp: Optional[str]
    params: Optional[dict]
    rawBody: Optional[str] = None


class Response(BaseModel):
    timestamp: Optional[str]
    result: Optional[dict]
    rawBody: Optional[str] = None


class SessionLog(BaseModel):
    sessionId: Optional[str] = None
    id: str
    timestamp: Optional[str]
    method: Optional[str]
    request: Optional[Request]
    response: Optional[Response]
    pageId: Optional[str] = None


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

    def get_connect_url(
        self, session_id: Optional[str] = None, proxy: Optional[bool] = None
    ):
        base_url = f"{self.connect_url}?apiKey={self.api_key}"
        if session_id:
            base_url += f"&sessionId={session_id}"
        if proxy:
            base_url += "&enableProxy=true"
        return base_url

    def list_sessions(self) -> list[Session]:
        response = httpx.get(
            f"{self.api_url}/v1/sessions",
            headers={
                "x-bb-api-key": self.api_key,
                "Content-Type": "application/json",
            },
        )

        response.raise_for_status()
        data = response.json()
        return [Session(**item) for item in data]

    def create_session(self, options: Optional[CreateSessionOptions] = None) -> Session:
        payload = {"projectId": self.project_id}
        if options:
            payload.update(options.model_dump(by_alias=True, exclude_none=True))

        if not payload['projectId']:
            raise ValueError("a projectId is missing: use the options.projectId or BROWSERBASE_PROJECT_ID environment variable to set one.")

        response = httpx.post(
            f"{self.api_url}/v1/sessions",
            headers={
                "x-bb-api-key": self.api_key,
                "Content-Type": "application/json",
            },
            json=payload,
        )

        response.raise_for_status()
        return Session(**response.json())

    def complete_session(self, session_id: str) -> Session:
        if not session_id or session_id == '':
            raise ValueError('sessionId is required')

        if not self.project_id:
            raise ValueError(
                'a projectId is missing: use the options.projectId or BROWSERBASE_PROJECT_ID environment variable to set one.'
            )

        response = httpx.post(
            f"{self.api_url}/v1/sessions/{session_id}",
            headers={
                "x-bb-api-key": self.api_key,
                "Content-Type": "application/json",
            },
            json={
                "projectId": self.project_id,
                "status": "REQUEST_RELEASE",
            },
        )

        response.raise_for_status()
        return Session(**response.json())

    def get_session(self, session_id: str) -> Session:
        response = httpx.get(
            f"{self.api_url}/v1/sessions/{session_id}",
            headers={
                "x-bb-api-key": self.api_key,
                "Content-Type": "application/json",
            },
        )

        response.raise_for_status()
        return Session(**response.json())

    def get_session_recording(self, session_id: str) -> list[SessionRecording]:
        response = httpx.get(
            f"{self.api_url}/v1/sessions/{session_id}/recording",
            headers={
                "x-bb-api-key": self.api_key,
                "Content-Type": "application/json",
            },
        )

        response.raise_for_status()
        data = response.json()
        return [SessionRecording(**item) for item in data]

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

    def get_debug_connection_urls(self, session_id: str) -> DebugConnectionURLs:
        response = httpx.get(
            f"{self.api_url}/v1/sessions/{session_id}/debug",
            headers={
                "x-bb-api-key": self.api_key,
                "Content-Type": "application/json",
            },
        )

        response.raise_for_status()
        return DebugConnectionURLs(**response.json())

    def get_session_logs(self, session_id: str) -> list[SessionLog]:
        response = httpx.get(
            f"{self.api_url}/v1/sessions/{session_id}/logs",
            headers={
                "x-bb-api-key": self.api_key,
                "Content-Type": "application/json",
            },
        )

        response.raise_for_status()
        data = response.json()
        return [SessionLog(**item) for item in data]

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
                readable = page.evaluate("""async () => {
                  const readability = await import('https://cdn.skypack.dev/@mozilla/readability');
                  return (new readability.Readability(document)).parse();
                }""")

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
                    readable = page.evaluate("""async () => {
                      const readability = await import('https://cdn.skypack.dev/@mozilla/readability');
                      return (new readability.Readability(document)).parse();
                    }""")

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
