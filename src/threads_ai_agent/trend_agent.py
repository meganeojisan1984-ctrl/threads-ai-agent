from __future__ import annotations

import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

from threads_ai_agent.models import Topic
from threads_ai_agent.storage import JsonStorage


class TrendResearchAgent:
    def __init__(
        self,
        storage: JsonStorage,
        config_path: Path | str = "config/trend_sources.json",
    ) -> None:
        self.storage = storage
        self.config_path = Path(config_path)

    def refresh_trends(self, limit: int = 10) -> list[Topic]:
        feeds = self._load_feeds()
        topics: list[Topic] = []
        for feed in feeds:
            for item in self._fetch_feed_items(feed["url"]):
                topics.append(_topic_from_feed_item(item["title"], item["link"]))
                if len(topics) >= limit:
                    break
            if len(topics) >= limit:
                break

        existing = self.storage.read_json("topics.json", default=[])
        existing_by_id = {item["id"]: item for item in existing}
        merged = [topic.model_dump(mode="json") for topic in topics]
        for item in existing:
            if item["id"] not in {topic.id for topic in topics}:
                merged.append(existing_by_id[item["id"]])
        self.storage.write_json("trend_topics.json", [topic.model_dump(mode="json") for topic in topics])
        self.storage.write_json("topics.json", merged)
        return topics

    def _load_feeds(self) -> list[dict[str, str]]:
        if not self.config_path.exists():
            return []
        payload = json.loads(self.config_path.read_text(encoding="utf-8"))
        return payload.get("feeds", [])

    def _fetch_feed_items(self, url: str) -> list[dict[str, str]]:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        return parse_rss_items(response.text)


def parse_rss_items(xml_text: str) -> list[dict[str, str]]:
    root = ET.fromstring(xml_text)
    items: list[dict[str, str]] = []
    for item in root.findall(".//item"):
        title = item.findtext("title", default="").strip()
        link = item.findtext("link", default="").strip()
        if title and link:
            items.append({"title": title, "link": link})
    return items


def _topic_from_feed_item(title: str, link: str) -> Topic:
    digest = hashlib.sha1(f"{title}:{link}".encode("utf-8")).hexdigest()[:12]
    return Topic(
        id=f"trend-{digest}",
        title=f"急上昇AIニュースをAI副業目線で解説: {title}",
        source_url=link,
        intent="trend",
        weight=1.3,
    )
