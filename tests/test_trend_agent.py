from pathlib import Path

import responses

from threads_ai_agent.storage import JsonStorage
from threads_ai_agent.trend_agent import TrendResearchAgent, parse_rss_items


RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item>
      <title>New AI video feature launches</title>
      <link>https://example.com/ai-video</link>
    </item>
  </channel>
</rss>
"""

RSS_WITH_SENSITIVE_ITEM = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item>
      <title>Medical AI AMIE helps chronic disease management</title>
      <link>https://example.com/medical-ai</link>
    </item>
    <item>
      <title>AI automation tool launches for creators</title>
      <link>https://example.com/ai-automation</link>
    </item>
  </channel>
</rss>
"""


def test_parse_rss_items_extracts_title_and_link():
    assert parse_rss_items(RSS) == [
        {"title": "New AI video feature launches", "link": "https://example.com/ai-video"}
    ]


@responses.activate
def test_trend_agent_writes_trend_topics(tmp_path: Path):
    config_path = tmp_path / "trend_sources.json"
    config_path.write_text(
        '{"feeds":[{"name":"Example","url":"https://example.com/rss.xml"}]}',
        encoding="utf-8",
    )
    responses.get("https://example.com/rss.xml", body=RSS, status=200)
    storage = JsonStorage(tmp_path / "data")
    storage.write_json("topics.json", [{
        "id": "wp-1",
        "title": "AI副業おすすめ完全ガイド",
        "source_url": "https://meganeojisanblog.com/ai-job/ai-fukugyou-osusume-guide/",
        "intent": "blog",
        "weight": 1.0,
    }])

    topics = TrendResearchAgent(storage, config_path).refresh_trends(limit=1)

    assert len(topics) == 1
    assert topics[0].intent == "trend"
    assert topics[0].source_url == "https://example.com/ai-video"
    assert storage.read_json("trend_topics.json", default=[])[0]["intent"] == "trend"
    assert storage.read_json("topics.json", default=[])[0]["id"].startswith("trend-")
    assert storage.read_json("topics.json", default=[])[1]["id"] == "wp-1"


@responses.activate
def test_trend_agent_skips_sensitive_topics(tmp_path: Path):
    config_path = tmp_path / "trend_sources.json"
    config_path.write_text(
        '{"feeds":[{"name":"Example","url":"https://example.com/rss.xml"}]}',
        encoding="utf-8",
    )
    responses.get("https://example.com/rss.xml", body=RSS_WITH_SENSITIVE_ITEM, status=200)
    storage = JsonStorage(tmp_path / "data")

    topics = TrendResearchAgent(storage, config_path).refresh_trends(limit=1)

    assert len(topics) == 1
    assert topics[0].source_url == "https://example.com/ai-automation"
    assert "Medical AI" not in topics[0].title
