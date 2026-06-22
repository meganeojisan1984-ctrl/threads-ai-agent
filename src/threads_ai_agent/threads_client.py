from __future__ import annotations

import time

import requests


class ThreadsApiError(RuntimeError):
    pass


class ThreadsClient:
    def __init__(
        self,
        user_id: str,
        access_token: str,
        api_base: str = "https://graph.threads.net/v1.0",
        publish_retry_attempts: int = 3,
        publish_retry_delay_seconds: float = 5,
    ) -> None:
        self.user_id = user_id
        self.access_token = access_token
        self.api_base = api_base.rstrip("/")
        self.publish_retry_attempts = publish_retry_attempts
        self.publish_retry_delay_seconds = publish_retry_delay_seconds

    def create_text_container(self, text: str) -> str:
        response = requests.post(
            f"{self.api_base}/{self.user_id}/threads",
            data={"media_type": "TEXT", "text": text, "access_token": self.access_token},
            timeout=30,
        )
        return self._id_from_response(response)

    def publish_container(self, container_id: str) -> str:
        response = None
        for attempt in range(self.publish_retry_attempts):
            response = requests.post(
                f"{self.api_base}/{self.user_id}/threads_publish",
                data={"creation_id": container_id, "access_token": self.access_token},
                timeout=30,
            )
            if not _should_retry_publish(response):
                return self._id_from_response(response)
            if attempt < self.publish_retry_attempts - 1:
                time.sleep(self.publish_retry_delay_seconds)
        assert response is not None
        return self._id_from_response(response)

    def fetch_replies(self, media_id: str) -> list[dict]:
        response = requests.get(
            f"{self.api_base}/{media_id}/replies",
            params={"access_token": self.access_token},
            timeout=30,
        )
        if response.status_code >= 400:
            raise ThreadsApiError(f"Threads API error {response.status_code}: {response.text[:300]}")
        return response.json().get("data", [])

    def reply_to_media(self, media_id: str, text: str) -> str:
        container_response = requests.post(
            f"{self.api_base}/{self.user_id}/threads",
            data={
                "media_type": "TEXT",
                "text": text,
                "reply_to_id": media_id,
                "access_token": self.access_token,
            },
            timeout=30,
        )
        container_id = self._id_from_response(container_response)
        return self.publish_container(container_id)

    def _id_from_response(self, response: requests.Response) -> str:
        if response.status_code >= 400:
            raise ThreadsApiError(f"Threads API error {response.status_code}: {response.text[:300]}")
        payload = response.json()
        if "id" not in payload:
            raise ThreadsApiError(f"Threads API response missing id: {payload}")
        return str(payload["id"])


def _should_retry_publish(response: requests.Response) -> bool:
    if response.status_code != 400:
        return False
    try:
        error = response.json().get("error", {})
    except ValueError:
        return False
    return (
        error.get("code") == 24
        and error.get("error_subcode") == 4279009
        and error.get("error_user_title") == "Media Not Found"
    )
