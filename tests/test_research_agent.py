from pathlib import Path

from threads_ai_agent.research_agent import ResearchAgent
from threads_ai_agent.storage import JsonStorage


class FakeWordPressClient:
    def fetch_recent_posts(self, limit: int = 20):
        return [
            {
                "id": 1,
                "link": "https://meganeojisanblog.com/ai-job/ai-fukugyou-osusume-guide/",
                "title": {"rendered": "AI副業おすすめ完全ガイド｜初心者の始め方"},
            },
            {
                "id": 2,
                "link": "https://meganeojisanblog.com/ai-job/ai-school-recommendation-sidehustle/",
                "title": {"rendered": "AIスクールおすすめ4社徹底比較"},
            },
        ]


def test_research_agent_writes_topics(tmp_path: Path):
    storage = JsonStorage(tmp_path)
    agent = ResearchAgent(FakeWordPressClient(), storage)

    topics = agent.refresh_topics(limit=2)

    assert [topic.intent for topic in topics] == ["blog", "affiliate"]
    assert storage.read_json("topics.json", default=[]) == [
        topic.model_dump(mode="json") for topic in topics
    ]
