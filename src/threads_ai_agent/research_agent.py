from __future__ import annotations

import re

from threads_ai_agent.models import Topic
from threads_ai_agent.storage import JsonStorage


AFFILIATE_HINTS = ["スクール", "ConoHa", "ツール", "案件", "比較", "DMM", "サーバー"]


def _slugify(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()[:60] or "topic"


class ResearchAgent:
    def __init__(self, wordpress_client, storage: JsonStorage) -> None:
        self.wordpress_client = wordpress_client
        self.storage = storage

    def refresh_topics(self, limit: int = 20) -> list[Topic]:
        posts = self.wordpress_client.fetch_recent_posts(limit=limit)
        topics: list[Topic] = []
        for post in posts:
            title = post["title"]["rendered"]
            intent = "affiliate" if any(hint in title for hint in AFFILIATE_HINTS) else "blog"
            topics.append(
                Topic(
                    id=f"wp-{post['id']}-{_slugify(title)}",
                    title=title,
                    source_url=post["link"],
                    intent=intent,
                    weight=1.5 if intent == "affiliate" else 1.0,
                )
            )
        self.storage.write_json("topics.json", [topic.model_dump(mode="json") for topic in topics])
        return topics
