import os
import httpx
import time
from typing import Optional, Sequence, Union, List
from enum import Enum
from pydantic import BaseModel, Field
from playwright.sync_api import sync_playwright


class BrowserType(str, Enum):
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    SAFARI = "safari"


class DeviceType(str, Enum):
    DESKTOP = "desktop"
    MOBILE = "mobile"


class OperatingSystem(str, Enum):
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    IOS = "ios"
    ANDROID = "android"


class SessionStatus(str, Enum):
    NEW = "NEW"
    CREATED = "CREATED"
    ERROR = "ERROR"
    RUNNING = "RUNNING"
    REQUEST_RELEASE = "REQUEST_RELEASE"
    RELEASING = "RELEASING"
    COMPLETED = "COMPLETED"


class Screen(BaseModel):
    max_height: Optional[int] = Field(None, alias="maxHeight")
    max_width: Optional[int] = Field(None, alias="maxWidth")
    min_height: Optional[int] = Field(None, alias="minHeight")
    min_width: Optional[int] = Field(None, alias="minWidth")


class Fingerprint(BaseModel):
    browser_list_query: Optional[str] = Field(None, alias="browserListQuery")
    http_version: Optional[int] = Field(None, alias="httpVersion")
    browsers: Optional[List[BrowserType]] = None
    devices: Optional[List[DeviceType]] = None
    locales: Optional[List[str]] = None
    operating_systems: Optional[List[OperatingSystem]] = Field(
        None, alias="operatingSystems"
    )
    screen: Optional[Screen] = None


class CreateSessionOptions(BaseModel):
    project_id: Optional[str] = Field(None, alias="projectId")
    extension_id: Optional[str] = Field(None, alias="extensionId")
    fingerprint: Optional[Fingerprint] = None


class Session(BaseModel):
    id: str
    created_at: str = Field(..., alias="createdAt")
    started_at: str = Field(..., alias="startedAt")
    ended_at: Optional[str] = Field(..., alias="endedAt")
    project_id: str = Field(..., alias="projectId")
    status: Optional[SessionStatus] = None
    task_id: Optional[str] = Field(None, alias="taskId")
    proxy_bytes: Optional[int] = Field(None, alias="proxyBytes")
    expires_at: Optional[str] = Field(None, alias="expiresAt")
    avg_cpu_usage: Optional[float] = Field(None, alias="avg_cpu_usage")
    memory_usage: Optional[int] = None
    details: Optional[str] = None
    logs: Optional[str] = None


class UpdateSessionOptions(BaseModel):
    project_id: Optional[str] = Field(None, alias="projectId")
    status: Optional[SessionStatus] = None


class SessionRecording(BaseModel):
    type: Optional[str] = None
    time: Optional[str] = None
    data: Optional[dict] = None


class DebugConnectionURLs(BaseModel):
    debugger_fullscreen_url: Optional[str] = Field(None, alias="debuggerFullscreenUrl")
    debugger_url: Optional[str] = Field(None, alias="debuggerUrl")
    ws_url: Optional[str] = Field(None, alias="wsUrl")


class Request(BaseModel):
    timestamp: Optional[str]
    params: Optional[dict]
    raw_body: Optional[str] = Field(alias="rawBody")


class Response(BaseModel):
    timestamp: Optional[str]
    result: Optional[dict]
    raw_body: Optional[str] = Field(alias="rawBody")


class SessionLog(BaseModel):
    session_id: Optional[str] = Field(alias="sessionId")
    id: str
    timestamp: Optional[str]
    method: Optional[str]
    request: Optional[Request]
    response: Optional[Response]
    page_id: Optional[str] = Field(alias="pageId")


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

    def list_sessions(self) -> List[Session]:
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

    def get_session(self, session_id: str) -> List[Session]:
        response = httpx.get(
            f"{self.api_url}/v1/sessions/{session_id}",
            headers={
                "x-bb-api-key": self.api_key,
                "Content-Type": "application/json",
            },
        )

        response.raise_for_status()
        return Session(**response.json())

    def update_session(
        self, session_id: str, options: Optional[UpdateSessionOptions] = None
    ) -> Session:
        payload = {"projectId": self.project_id}
        if options:
            payload.update(options.model_dump(by_alias=True, exclude_none=True))

        response = httpx.post(
            f"{self.api_url}/v1/sessions/{session_id}",
            headers={
                "x-bb-api-key": self.api_key,
                "Content-Type": "application/json",
            },
            json=payload,
        )

        response.raise_for_status()
        return Session(**response.json())

    def get_session_recording(self, session_id: str) -> List[SessionRecording]:
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

    def get_session_logs(self, session_id: str) -> List[SessionLog]:
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

    def get_connect_url(self, session_id=None, proxy=False):
        base_url = f"{self.connect_url}?apiKey={self.api_key}"
        if session_id:
            base_url += f"&sessionId={session_id}"
        if proxy:
            base_url += "&enableProxy=true"
        return base_url

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
        session_id: Optional[str] = None,
        proxy: Optional[bool] = None,
        text_content: bool = False,
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
        session_id: Optional[str] = None,
        proxy: Optional[bool] = None,
        text_content: bool = False,
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
        session_id: Optional[str] = None,
        proxy: Optional[bool] = None,
        full_page: bool = False,
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
