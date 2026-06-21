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
