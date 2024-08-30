import requests
from typing import List, Union, Optional, Literal
from . import (
    Session,
    BrowserSettings,
    Proxy,
    GeolocationProxy,
    CreateSessionOptions,
    DebugSession,
    SessionRecording,
    SessionRecordingItem,
)

SESSION_ENDPOINT = "https://www.browserbase.com/v1/sessions"


def get_session(api_key: str, session_id: str) -> Session:
    url = f"{SESSION_ENDPOINT}/{session_id}"
    headers = {"X-BB-API-Key": api_key}
    response = requests.request("GET", url, headers=headers)
    response.raise_for_status()
    print(response.json())
    return Session(**response.json())


def list_sessions(api_key: str) -> List[Session]:
    url = f"{SESSION_ENDPOINT}"
    headers = {"X-BB-API-Key": api_key}
    response = requests.request("GET", url, headers=headers)
    response.raise_for_status()
    return [Session(**session, test="test") for session in response.json()]


def create_session(
    project_id: str,
    api_key: str,
    options: Optional[BrowserSettings] = None,
    extension_id: Optional[str] = None,
    timeout: Optional[int] = None,
    keep_alive: bool = False,
    proxies: Union[bool, List[Proxy], List[GeolocationProxy]] = False,
) -> Session:
    url = f"{SESSION_ENDPOINT}"
    headers = {"X-BB-API-Key": api_key, "Content-Type": "application/json"}
    settings = CreateSessionOptions(
        project_id=project_id,
        extension_id=extension_id,
        browser_settings=options,
        timeout=timeout,
        keep_alive=keep_alive,
        proxies=proxies,
    )
    payload = settings.model_dump(by_alias=True, exclude_none=True)
    response = requests.request("POST", url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    return Session(**data)


def update_session(
    project_id: str,
    api_key: str,
    session_id: str,
    status: Literal["REQUEST_RELEASE"] = "REQUEST_RELEASE",
) -> Session:
    url = f"{SESSION_ENDPOINT}/{session_id}"
    headers = {"X-BB-API-Key": api_key, "Content-Type": "application/json"}
    payload = {"status": status, "projectId": project_id}
    response = requests.request("POST", url, json=payload, headers=headers)
    response.raise_for_status()
    return Session(**response.json())


def debug_session(api_key: str, session_id: str) -> DebugSession:
    url = f"{SESSION_ENDPOINT}/{session_id}/debug"
    headers = {"X-BB-API-Key": api_key}
    response = requests.request("GET", url, headers=headers)
    response.raise_for_status()
    return DebugSession(**response.json())


def get_session_recording(api_key: str, session_id: str) -> SessionRecording:
    url = f"{SESSION_ENDPOINT}/{session_id}/recording"
    headers = {"X-BB-API-Key": api_key, "Content-Type": "application/json"}
    response = requests.request("GET", url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return SessionRecording(
        sessionId=session_id,
        items=[SessionRecordingItem(**item) for item in data],
    )
