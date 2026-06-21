from __future__ import annotations

from datetime import UTC, datetime

from threads_ai_agent.config import BotConfig
from threads_ai_agent.safety import SafetyAgent
from threads_ai_agent.storage import JsonStorage


class ReplyAgent:
    def __init__(
        self,
        threads_client,
        text_client,
        storage: JsonStorage,
        config: BotConfig,
        safety: SafetyAgent | None = None,
    ) -> None:
        self.threads_client = threads_client
        self.text_client = text_client
        self.storage = storage
        self.config = config
        self.safety = safety or SafetyAgent()

    def process_replies(self) -> int:
        if not self.config.enabled:
            return 0
        seen_ids = {item["reply_id"] for item in self.storage.read_jsonl("replies_seen.jsonl")}
        sent = 0
        for post in self.storage.read_jsonl("published_posts.jsonl"):
            if sent >= self.config.per_run_reply_limit or self._daily_reply_limit_reached():
                break
            media_id = post["threads_media_id"]
            for reply in self.threads_client.fetch_replies(media_id):
                if sent >= self.config.per_run_reply_limit or self._daily_reply_limit_reached():
                    break
                reply_id = str(reply["id"])
                if reply_id in seen_ids:
                    continue
                incoming_text = reply.get("text", "")
                self.storage.append_jsonl(
                    "replies_seen.jsonl",
                    {"reply_id": reply_id, "media_id": media_id, "text": incoming_text},
                )
                seen_ids.add(reply_id)
                decision = self.safety.classify_reply(incoming_text)
                if not decision.auto_reply_allowed:
                    self.storage.append_jsonl(
                        "blocked_replies.jsonl",
                        {
                            "reply_id": reply_id,
                            "category": decision.category,
                            "reasons": decision.reasons,
                        },
                    )
                    continue
                reply_text = self._generate_reply(post_text=post["text"], incoming_text=incoming_text)
                safety = self.safety.check_text(reply_text)
                if not safety.allowed:
                    self.storage.append_jsonl(
                        "blocked_replies.jsonl",
                        {
                            "reply_id": reply_id,
                            "category": "generated_blocked",
                            "reasons": safety.reasons,
                        },
                    )
                    continue
                if self.config.dry_run:
                    self.storage.append_jsonl("dry_run_replies.jsonl", {"reply_id": reply_id, "text": reply_text})
                    continue
                published_reply_id = self.threads_client.reply_to_media(media_id, reply_text)
                self.storage.append_jsonl(
                    "replies_sent.jsonl",
                    {
                        "reply_id": reply_id,
                        "published_reply_id": published_reply_id,
                        "text": reply_text,
                        "sent_at": datetime.now(UTC).isoformat(),
                    },
                )
                sent += 1
        return sent

    def _daily_reply_limit_reached(self) -> bool:
        today = datetime.now(UTC).date().isoformat()
        sent_today = [
            item for item in self.storage.read_jsonl("replies_sent.jsonl")
            if str(item.get("sent_at", "")).startswith(today)
        ]
        return len(sent_today) >= self.config.replies_per_day

    def _generate_reply(self, *, post_text: str, incoming_text: str) -> str:
        result = self.text_client.generate_json(
            "次のThreads返信に、短く丁寧な日本語で返答してください。"
            "収益保証や強い売り込みは禁止です。"
            f"\n投稿: {post_text}\n返信: {incoming_text}\n"
            "{\"reply\":\"...\"} のJSONだけを返してください。"
        )
        return result["reply"].strip()
