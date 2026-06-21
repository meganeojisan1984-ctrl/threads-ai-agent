from __future__ import annotations

import requests


class ThreadsApiError(RuntimeError):
    pass


class ThreadsClient:
    def __init__(
        self,
        user_id: str,
        access_token: str,
        api_base: str = "https://graph.threads.net/v1.0",
    ) -> None:
        self.user_id = user_id
        self.access_token = access_token
        self.api_base = api_base.rstrip("/")

    def create_text_container(self, text: str) -> str:
        response = requests.post(
            f"{self.api_base}/{self.user_id}/threads",
            data={"media_type": "TEXT", "text": text, "access_token": self.access_token},
            timeout=30,
        )
        return self._id_from_response(response)

    def publish_container(self, container_id: str) -> str:
        response = requests.post(
            f"{self.api_base}/{self.user_id}/threads_publish",
            data={"creation_id": container_id, "access_token": self.access_token},
            timeout=30,
        )
        return self._id_from_response(response)

    def _id_from_response(self, response: requests.Response) -> str:
        if response.status_code >= 400:
            raise ThreadsApiError(f"Threads API error {response.status_code}: {response.text[:300]}")
        payload = response.json()
        if "id" not in payload:
            raise ThreadsApiError(f"Threads API response missing id: {payload}")
        return str(payload["id"])
