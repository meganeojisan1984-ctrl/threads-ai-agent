from pathlib import Path

from threads_ai_agent.config import BotConfig
from threads_ai_agent.publisher_agent import PublisherAgent
from threads_ai_agent.storage import JsonStorage


class FakeThreadsClient:
    def create_text_container(self, text: str) -> str:
        return "container-1"

    def publish_container(self, container_id: str) -> str:
        return "media-1"


def _write_queue(storage: JsonStorage) -> None:
    storage.write_json("post_queue.json", [{
        "id": "d1",
        "topic_id": "t1",
        "text": "AI副業の始め方をブログにまとめました。",
        "source_url": "https://meganeojisanblog.com/ai-job/ai-fukugyou-osusume-guide/",
        "affiliate_intent": False,
        "status": "queued",
        "created_at": "2026-06-21T00:00:00",
    }])


def test_publisher_dry_run_does_not_publish(tmp_path: Path):
    storage = JsonStorage(tmp_path)
    _write_queue(storage)
    config = BotConfig.from_env({"BOT_ENABLED": "true", "DRY_RUN": "true"})

    result = PublisherAgent(FakeThreadsClient(), storage, config).publish_next()

    assert result is None
    assert storage.read_jsonl("published_posts.jsonl") == []
    assert storage.read_jsonl("dry_run_publish.jsonl")[0]["draft_id"] == "d1"


def test_publisher_publishes_next_safe_post(tmp_path: Path):
    storage = JsonStorage(tmp_path)
    _write_queue(storage)
    config = BotConfig.from_env({
        "BOT_ENABLED": "true",
        "DRY_RUN": "false",
        "OPENAI_API_KEY": "x",
        "THREADS_USER_ID": "u",
        "THREADS_ACCESS_TOKEN": "token",
    })

    result = PublisherAgent(FakeThreadsClient(), storage, config).publish_next()

    assert result is not None
    assert result.threads_media_id == "media-1"
    assert storage.read_jsonl("published_posts.jsonl")[0]["threads_media_id"] == "media-1"
