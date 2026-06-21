from __future__ import annotations

import hashlib

from threads_ai_agent.models import PostDraft, Topic
from threads_ai_agent.safety import SafetyAgent
from threads_ai_agent.storage import JsonStorage


class WriterAgent:
    def __init__(
        self,
        text_client,
        storage: JsonStorage,
        safety: SafetyAgent | None = None,
    ) -> None:
        self.text_client = text_client
        self.storage = storage
        self.safety = safety or SafetyAgent()

    def create_post_queue(self, count: int = 3) -> list[PostDraft]:
        raw_topics = self.storage.read_json("topics.json", default=[])
        topics = [Topic.model_validate(item) for item in raw_topics][:count]
        if not topics:
            self.storage.write_json("post_queue.json", [])
            return []

        result = self.text_client.generate_json(self._build_prompt(topics))
        drafts: list[PostDraft] = []
        blocked: list[dict] = []
        for item, topic in zip(result.get("posts", []), topics):
            affiliate_intent = bool(item.get("affiliate_intent", topic.intent == "affiliate"))
            text = item["text"].strip()
            safety = self.safety.check_text(text, affiliate_intent=affiliate_intent)
            draft_id = hashlib.sha1(f"{topic.id}:{text}".encode("utf-8")).hexdigest()[:16]
            if not safety.allowed:
                blocked.append({"topic_id": topic.id, "text": text, "reasons": safety.reasons})
                continue
            drafts.append(
                PostDraft(
                    id=draft_id,
                    topic_id=topic.id,
                    text=text,
                    source_url=item.get("source_url", topic.source_url),
                    affiliate_intent=affiliate_intent,
                )
            )
        self.storage.write_json("post_queue.json", [draft.model_dump(mode="json") for draft in drafts])
        if blocked:
            self.storage.write_json("blocked_drafts.json", blocked)
        return drafts

    def _build_prompt(self, topics: list[Topic]) -> str:
        topic_lines = "\n".join(
            f"- {topic.title}: {topic.source_url} ({topic.intent})" for topic in topics
        )
        return (
            "あなたはAI副業ブログのThreads運用担当です。"
            "各トピックから500文字以内の日本語投稿を作成してください。"
            "誇大表現、断定的な収益保証、煽りを避けてください。"
            "JSON形式で {\"posts\":[{\"text\":\"...\",\"source_url\":\"...\",\"affiliate_intent\":false}]} を返してください。\n"
            f"{topic_lines}"
        )
