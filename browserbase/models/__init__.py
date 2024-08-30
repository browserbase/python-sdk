from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, Union, Literal, List
from enum import Enum
from uuid import uuid4
import json


class DefaultModel(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)


class SessionStatus(Enum):
    RUNNING = "RUNNING"
    ERROR = "ERROR"
    TIMED_OUT = "TIMED_OUT"
    COMPLETED = "COMPLETED"


class Context(DefaultModel):
    id: str
    upload_url: str = Field(alias="uploadUrl")
    public_key: str = Field(alias="publicKey")
    cipher_algorithm: str = Field(alias="cipherAlgorithm")
    initialization_vector_size: str = Field(alias="initializationVectorSize")


# ANI QUESTION: what is a task?
class Task(DefaultModel):
    id: str
    arn: str
    status: str
    external_ip: Optional[str] = None
    internal_ip: Optional[str] = None
    viewport_width: Optional[int] = None
    viewport_height: Optional[int] = None


class Session(DefaultModel):
    id: str
    created_at: str = Field(alias="createdAt")
    updated_at: str  # ANI QUESTION: why is updated_at and not updatedAt?
    project_id: str = Field(alias="projectId")
    started_at: str = Field(alias="startedAt")
    ended_at: Optional[str] = Field(alias="endedAt")
    expires_at: str = Field(alias="expiresAt")
    status: SessionStatus
    proxy_bytes: int = Field(alias="proxyBytes")
    # ANI QUESTION: why are these snake case?
    avg_cpu_usage: Optional[int]
    memory_usage: Optional[int]
    keep_alive: bool
    context_id: Optional[str]
    # ANI QUESTION: what is a task? why is it called tasks but singular?
    task_id: Optional[str] = Field(alias="taskId")
    tasks: Optional[Task] = None


# -----------------------------------------------------------
# Browser Settings
# -----------------------------------------------------------


class Screen(DefaultModel):
    max_height: Optional[int] = Field(alias="maxHeight")
    max_width: Optional[int] = Field(alias="maxWidth")
    min_height: Optional[int] = Field(alias="minHeight")
    min_width: int = Field(alias="minWidth")


class Fingerprint(DefaultModel):
    http_version: Optional[Literal["1", "2"]] = Field(alias="httpVersion")
    # ANI QUESTION: What is browserListQuery?
    browsers: Optional[List[Literal["chrome", "edge", "firefox", "safari"]]] = None
    devices: Optional[List[Literal["desktop", "mobile"]]] = None
    locales: Optional[List[str]] = None
    operating_systems: Optional[
        List[Literal["android", "ios", "linux", "macos", "windows"]]
    ] = Field(alias="operatingSystems")
    screen: Optional[Screen] = None

    @field_validator("operating_systems", "devices")
    def validate_mobile_os(cls, v, values, **kwargs):
        operating_systems = values.get("operating_systems", [])
        devices = values.get("devices", [])

        if "ios" in operating_systems or "android" in operating_systems:
            if "mobile" not in devices:
                raise ValueError(
                    "When 'ios' or 'android' is selected in operating_systems, 'mobile' must be included in devices."
                )

        return v


class BrowserSettingsContext(DefaultModel):
    id: str
    persist: bool = False


class Viewport(DefaultModel):
    width: int
    height: int


class BrowserSettings(DefaultModel):
    fingerprint: Optional[Fingerprint] = None
    context: Optional[BrowserSettingsContext] = None
    viewport: Optional[Viewport] = None
    block_ads: bool = Field(alias="blockAds", default=False)
    solve_captchas: bool = Field(alias="solveCaptchas", default=True)
    record_session: bool = Field(alias="recordSession", default=True)
    log_session: bool = Field(alias="logSession", default=True)


# ------------------------------------------------------------


class Geolocation(DefaultModel):
    city: Optional[str] = Field(
        description="Name of the city. Use spaces for multi-word city names"
    )
    state: Optional[str] = Field(
        description="US state code (2 characters). Must also specify US as the country."
    )
    country: str = Field(description="Country code in ISO 3166-1 alpha-2 format")


class GeolocationProxy(DefaultModel):
    type: Literal["browserbase"] = Field(default="browserbase")
    geolocation: Optional[Geolocation] = None
    domain_pattern: Optional[str] = Field(
        description="Domain pattern for which this proxy should be used. If omitted, defaults to all domains.",
        alias="domainPattern",
    )


class Proxy(DefaultModel):
    type: Literal["external"] = Field(
        description="Type of proxy. Always 'external' for this config."
    )
    server: str = Field(description="Server URL for external proxy.")
    domain_pattern: Optional[str] = Field(
        description="Domain pattern for which this proxy should be used. If omitted, defaults to all domains.",
        alias="domainPattern",
    )
    username: Optional[str] = Field(
        description="Username for external proxy authentication."
    )
    password: Optional[str] = Field(
        description="Password for external proxy authentication."
    )


class CreateSessionOptions(DefaultModel):
    project_id: str = Field(serialization_alias="projectId")
    extension_id: Optional[str] = Field(serialization_alias="extensionId")
    browser_settings: Optional[BrowserSettings] = Field(
        serialization_alias="browserSettings"
    )
    timeout: Optional[int]
    keep_alive: bool = Field(default=False, serialization_alias="keepAlive")
    proxies: Union[bool, List[Proxy], List[GeolocationProxy]] = False


# ------------------------------------------------------------


class Page(DefaultModel):
    id: str
    url: str
    favicon_url: Optional[str] = Field(alias="faviconUrl", default=None)
    title: str
    debugger_url: str = Field(alias="debuggerUrl")
    debugger_fullscreen_url: str = Field(alias="debuggerFullscreenUrl")
    primary: bool = Field(default=False)


class DebugSession(DefaultModel):
    debugger_fullscreen_url: str = Field(alias="debuggerFullscreenUrl")
    debugger_url: str = Field(alias="debuggerUrl")
    pages: List[Page]
    ws_url: str = Field(alias="wsUrl")


# ------------------------------------------------------------


class SessionRecordingItem(BaseModel):
    timestamp: Optional[Union[str, int]] = None
    # ANI QUESTION: why is this a string or int?
    type: Optional[Union[str, int]] = None
    data: Optional[dict] = None
    sessionId: Optional[str] = None


class SessionRecording(BaseModel):
    sessionId: Optional[str] = None
    items: list[SessionRecordingItem]

    def _repr_html_(self):
        divId = f"BB_LIVE_SESSION_{str(uuid4())}"
        html_content = f"""
		<div id="{divId}"></div>
		<script src="https://cdn.jsdelivr.net/npm/rrweb@latest/dist/rrweb.min.js"></script>
		<script src="https://cdn.jsdelivr.net/npm/rrweb-player@latest/dist/index.js"></script>
		<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/rrweb-player@latest/dist/style.css"/>

		<script>
		(function() {{
			var events = {json.dumps([item.model_dump() for item in self.items])};
			
			function initPlayer() {{
				if (typeof rrwebPlayer === 'undefined') {{
					console.log('rrweb player not loaded yet, retrying...');
					setTimeout(initPlayer, 100);
					return;
				}}
				
				new rrwebPlayer({{
					target: document.getElementById('{divId}'),
					props: {{
						events: events,
						width: 800,
						height: 600,
						autoPlay: true
					}}
				}});
			}}
			
			if (document.readyState === 'complete') {{
				initPlayer();
			}} else {{
				window.addEventListener('load', initPlayer);
			}}
		}})();
		</script>
		"""
        return html_content


from . import context_service, session_service
