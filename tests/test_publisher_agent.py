from pathlib import Path

from threads_ai_agent.config import BotConfig
from threads_ai_agent.publisher_agent import PublisherAgent
from threads_ai_agent.storage import JsonStorage


class FakeThreadsClient:
    def __init__(self):
        self.created_texts = []
        self.replies = []

    def create_text_container(self, text: str) -> str:
        self.created_texts.append(text)
        return "container-1"

    def publish_container(self, container_id: str) -> str:
        return "media-1"

    def reply_to_media(self, media_id: str, text: str) -> str:
        self.replies.append((media_id, text))
        return f"reply-{len(self.replies)}"


def _write_queue(storage: JsonStorage) -> None:
    storage.write_json("post_queue.json", [{
        "id": "d1",
        "topic_id": "t1",
        "text": "AI副業の始め方をブログにまとめました。",
        "source_url": "https://meganeojisanblog.com/ai-job/ai-fukugyou-osusume-guide/",
        "affiliate_intent": False,
        "post_type": "single",
        "parts": ["AI副業の始め方をブログにまとめました。"],
        "cta_style": "direct_url",
        "status": "queued",
        "created_at": "2026-06-21T00:00:00",
    }])


def _write_thread_queue(storage: JsonStorage) -> None:
    storage.write_json("post_queue.json", [{
        "id": "d2",
        "topic_id": "t1",
        "text": "AI副業で最初に迷うのは、何から始めるかです。",
        "source_url": "https://meganeojisanblog.com/ai-job/ai-fukugyou-osusume-guide/",
        "affiliate_intent": False,
        "post_type": "thread",
        "parts": [
            "AI副業で最初に迷うのは、何から始めるかです。",
            "最初はツールを増やすより、小さな作業を1つ自動化するのがおすすめです。",
            "詳しい手順はプロフィールのブログにまとめています。",
        ],
        "cta_style": "profile",
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
    assert storage.read_jsonl("dry_run_publish.jsonl")[0]["text"].endswith(
        "https://meganeojisanblog.com/ai-job/ai-fukugyou-osusume-guide/"
    )


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
    assert result.text.endswith("https://meganeojisanblog.com/ai-job/ai-fukugyou-osusume-guide/")
    assert storage.read_jsonl("published_posts.jsonl")[0]["threads_media_id"] == "media-1"


def test_publisher_dry_run_logs_all_thread_parts(tmp_path: Path):
    storage = JsonStorage(tmp_path)
    _write_thread_queue(storage)
    config = BotConfig.from_env({"BOT_ENABLED": "true", "DRY_RUN": "true"})

    result = PublisherAgent(FakeThreadsClient(), storage, config).publish_next()

    log = storage.read_jsonl("dry_run_publish.jsonl")[0]
    assert result is None
    assert log["post_type"] == "thread"
    assert len(log["parts"]) == 3
    assert "プロフィール" in log["parts"][-1]


def test_publisher_posts_thread_replies_to_root(tmp_path: Path):
    storage = JsonStorage(tmp_path)
    _write_thread_queue(storage)
    client = FakeThreadsClient()
    config = BotConfig.from_env({
        "BOT_ENABLED": "true",
        "DRY_RUN": "false",
        "OPENAI_API_KEY": "x",
        "THREADS_USER_ID": "u",
        "THREADS_ACCESS_TOKEN": "token",
    })

    result = PublisherAgent(client, storage, config).publish_next()

    log = storage.read_jsonl("published_posts.jsonl")[0]
    assert result is not None
    assert client.created_texts == ["AI副業で最初に迷うのは、何から始めるかです。"]
    assert len(client.replies) == 2
    assert client.replies[0][0] == "media-1"
    assert log["thread_media_ids"] == ["media-1", "reply-1", "reply-2"]
