from pathlib import Path

from threads_ai_agent.config import BotConfig
from threads_ai_agent.reply_agent import ReplyAgent
from threads_ai_agent.storage import JsonStorage


class FakeTextClient:
    def generate_json(self, prompt: str):
        return {"reply": "ありがとうございます。まずは無料で試せる手順から始めるのがおすすめです。"}


class FakeThreadsClient:
    def fetch_replies(self, media_id: str):
        return [{"id": "r1", "text": "詳しく知りたいです", "username": "reader"}]

    def reply_to_media(self, media_id: str, text: str) -> str:
        return "reply-media-1"


def _config() -> BotConfig:
    return BotConfig.from_env({
        "BOT_ENABLED": "true",
        "DRY_RUN": "false",
        "OPENAI_API_KEY": "x",
        "THREADS_USER_ID": "u",
        "THREADS_ACCESS_TOKEN": "token",
    })


def _write_published_post(storage: JsonStorage) -> None:
    storage.append_jsonl("published_posts.jsonl", {
        "draft_id": "d1",
        "threads_media_id": "media-1",
        "text": "AI副業の始め方をまとめました",
        "source_url": "https://meganeojisanblog.com/ai-job/ai-fukugyou-osusume-guide/",
        "published_at": "2026-06-21T00:00:00",
    })


def test_reply_agent_sends_safe_reply(tmp_path: Path):
    storage = JsonStorage(tmp_path)
    _write_published_post(storage)

    sent = ReplyAgent(FakeThreadsClient(), FakeTextClient(), storage, _config()).process_replies()

    assert sent == 1
    assert storage.read_jsonl("replies_sent.jsonl")[0]["reply_id"] == "r1"


def test_reply_agent_blocks_sensitive_reply(tmp_path: Path):
    class SensitiveThreadsClient(FakeThreadsClient):
        def fetch_replies(self, media_id: str):
            return [{"id": "r2", "text": "税金は申告しなくてもいい？", "username": "reader"}]

    storage = JsonStorage(tmp_path)
    _write_published_post(storage)

    sent = ReplyAgent(SensitiveThreadsClient(), FakeTextClient(), storage, _config()).process_replies()

    assert sent == 0
    assert storage.read_jsonl("blocked_replies.jsonl")[0]["reply_id"] == "r2"
