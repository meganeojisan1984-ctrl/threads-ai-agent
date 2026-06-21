from __future__ import annotations

from threads_ai_agent.config import BotConfig
from threads_ai_agent.models import PostDraft, PublishedPost
from threads_ai_agent.safety import SafetyAgent
from threads_ai_agent.storage import JsonStorage


class PublisherAgent:
    def __init__(
        self,
        threads_client,
        storage: JsonStorage,
        config: BotConfig,
        safety: SafetyAgent | None = None,
    ) -> None:
        self.threads_client = threads_client
        self.storage = storage
        self.config = config
        self.safety = safety or SafetyAgent()

    def publish_next(self) -> PublishedPost | None:
        if not self.config.enabled:
            return None
        queue = [
            PostDraft.model_validate(item)
            for item in self.storage.read_json("post_queue.json", default=[])
        ]
        if not queue:
            return None
        draft = queue[0]
        publish_text = _with_source_url(draft.text, draft.source_url)
        safety = self.safety.check_text(publish_text, affiliate_intent=draft.affiliate_intent)
        if not safety.allowed:
            self.storage.append_jsonl(
                "blocked_publish.jsonl",
                {"draft_id": draft.id, "reasons": safety.reasons},
            )
            self.storage.write_json("post_queue.json", [item.model_dump(mode="json") for item in queue[1:]])
            return None
        if self.config.dry_run:
            self.storage.append_jsonl("dry_run_publish.jsonl", {"draft_id": draft.id, "text": publish_text})
            return None
        container_id = self.threads_client.create_text_container(publish_text)
        media_id = self.threads_client.publish_container(container_id)
        published = PublishedPost(
            draft_id=draft.id,
            threads_media_id=media_id,
            text=publish_text,
            source_url=draft.source_url,
        )
        self.storage.append_jsonl("published_posts.jsonl", published.model_dump(mode="json"))
        self.storage.write_json("post_queue.json", [item.model_dump(mode="json") for item in queue[1:]])
        return published


def _with_source_url(text: str, source_url: str) -> str:
    if not source_url or source_url in text:
        return text
    return f"{text.rstrip()}\n\n{source_url}"
