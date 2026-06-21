from pathlib import Path

from threads_ai_agent.storage import JsonStorage
from threads_ai_agent.writer_agent import WriterAgent


class FakeTextClient:
    def generate_json(self, prompt: str):
        return {
            "posts": [
                {
                    "text": "AI副業は、まず小さく試すのが大事です。失敗談と手順をブログにまとめました。",
                    "source_url": "https://meganeojisanblog.com/ai-job/ai-fukugyou-osusume-guide/",
                    "affiliate_intent": False,
                }
            ]
        }


def test_writer_agent_creates_safe_queue(tmp_path: Path):
    storage = JsonStorage(tmp_path)
    storage.write_json("topics.json", [{
        "id": "t1",
        "title": "AI副業おすすめ完全ガイド",
        "source_url": "https://meganeojisanblog.com/ai-job/ai-fukugyou-osusume-guide/",
        "intent": "blog",
        "weight": 1.0,
    }])
    agent = WriterAgent(FakeTextClient(), storage)

    drafts = agent.create_post_queue(count=1)

    assert len(drafts) == 1
    assert drafts[0].status == "queued"
    assert storage.read_json("post_queue.json", default=[])[0]["text"].startswith("AI副業")
