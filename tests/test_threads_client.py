import responses

from threads_ai_agent.threads_client import ThreadsClient


@responses.activate
def test_threads_client_creates_and_publishes_text_container():
    client = ThreadsClient("user-1", "token", api_base="https://example.test/v1.0")
    responses.post("https://example.test/v1.0/user-1/threads", json={"id": "container-1"})
    responses.post("https://example.test/v1.0/user-1/threads_publish", json={"id": "media-1"})

    container_id = client.create_text_container("hello")
    media_id = client.publish_container(container_id)

    assert container_id == "container-1"
    assert media_id == "media-1"


@responses.activate
def test_threads_client_retries_media_not_found_when_publishing_reply_container():
    client = ThreadsClient(
        "user-1",
        "token",
        api_base="https://example.test/v1.0",
        publish_retry_delay_seconds=0,
    )
    responses.post("https://example.test/v1.0/user-1/threads", json={"id": "reply-container-1"})
    responses.post(
        "https://example.test/v1.0/user-1/threads_publish",
        json={
            "error": {
                "message": "The requested resource does not exist",
                "type": "OAuthException",
                "code": 24,
                "error_subcode": 4279009,
                "error_user_title": "Media Not Found",
            }
        },
        status=400,
    )
    responses.post("https://example.test/v1.0/user-1/threads_publish", json={"id": "reply-media-1"})

    media_id = client.reply_to_media("root-media-1", "reply text")

    assert media_id == "reply-media-1"
    assert len(responses.calls) == 3
