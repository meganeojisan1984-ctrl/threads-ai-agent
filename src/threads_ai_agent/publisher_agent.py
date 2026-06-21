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
        parts = _publish_parts(draft)
        safety = self._check_parts(parts, affiliate_intent=draft.affiliate_intent)
        if not safety.allowed:
            self.storage.append_jsonl(
                "blocked_publish.jsonl",
                {"draft_id": draft.id, "reasons": safety.reasons},
            )
            self.storage.write_json("post_queue.json", [item.model_dump(mode="json") for item in queue[1:]])
            return None
        if self.config.dry_run:
            self.storage.append_jsonl(
                "dry_run_publish.jsonl",
                {
                    "draft_id": draft.id,
                    "post_type": draft.post_type,
                    "parts": parts,
                    "text": "\n\n".join(parts),
                },
            )
            return None
        container_id = self.threads_client.create_text_container(parts[0])
        media_id = self.threads_client.publish_container(container_id)
        thread_media_ids = [media_id]
        for part in parts[1:]:
            thread_media_ids.append(self.threads_client.reply_to_media(media_id, part))
        published = PublishedPost(
            draft_id=draft.id,
            threads_media_id=media_id,
            text="\n\n".join(parts),
            source_url=draft.source_url,
        )
        log_entry = published.model_dump(mode="json")
        log_entry["post_type"] = draft.post_type
        log_entry["parts"] = parts
        log_entry["thread_media_ids"] = thread_media_ids
        self.storage.append_jsonl("published_posts.jsonl", log_entry)
        self.storage.write_json("post_queue.json", [item.model_dump(mode="json") for item in queue[1:]])
        return published

    def _check_parts(self, parts: list[str], *, affiliate_intent: bool):
        reasons: list[str] = []
        for part in parts:
            result = self.safety.check_text(part, affiliate_intent=affiliate_intent)
            reasons.extend(result.reasons)
        combined = self.safety.check_text("\n\n".join(parts), affiliate_intent=affiliate_intent)
        reasons.extend(combined.reasons)
        unique_reasons = list(dict.fromkeys(reasons))
        return type(combined)(allowed=not unique_reasons, reasons=unique_reasons)


def _with_source_url(text: str, source_url: str) -> str:
    if not source_url or source_url in text:
        return text
    return f"{text.rstrip()}\n\n{source_url}"


def _publish_parts(draft: PostDraft) -> list[str]:
    parts = draft.parts or [draft.text]
    cleaned = [part.strip() for part in parts if part.strip()]
    if not cleaned:
        cleaned = [draft.text.strip()]
    if draft.cta_style == "direct_url":
        cleaned[-1] = _with_source_url(cleaned[-1], draft.source_url)
    return cleaned
