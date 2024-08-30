from pydantic import BaseModel
import requests
from . import Context

CONTEXT_ENDPOINT = "https://www.browserbase.com/v1/contexts"


def create_context(api_key: str, project_id: str) -> Context:
    payload = {"projectId": project_id}
    headers = {
        "X-BB-API-Key": api_key,
        "Content-Type": "application/json",
    }

    response = requests.request("POST", CONTEXT_ENDPOINT, json=payload, headers=headers)
    response.raise_for_status()
    return Context(**response.json())
