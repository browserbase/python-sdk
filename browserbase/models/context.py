from pydantic import BaseModel
import requests

ENDPOINT = "https://www.browserbase.com/v1/contexts"


class Context(BaseModel):
    id: str
    uploadUrl: str
    publicKey: str
    cipherAlgorithm: str
    initializationVectorSize: str


def create_context(api_key: str, project_id: str) -> Context:
    payload = {"projectId": project_id}
    headers = {
        "X-BB-API-Key": api_key,
        "Content-Type": "application/json",
    }

    response = requests.request("POST", ENDPOINT, json=payload, headers=headers)
    response.raise_for_status()
    return Context(**response.json())
