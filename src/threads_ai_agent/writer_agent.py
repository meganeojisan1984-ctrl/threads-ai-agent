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
            parts = [part.strip() for part in item.get("parts", []) if part.strip()]
            if not parts:
                parts = [item["text"].strip()]
            text = parts[0]
            combined_text = "\n\n".join(parts)
            safety = self.safety.check_text(combined_text, affiliate_intent=affiliate_intent)
            draft_id = hashlib.sha1(f"{topic.id}:{combined_text}".encode("utf-8")).hexdigest()[:16]
            if not safety.allowed:
                blocked.append({"topic_id": topic.id, "text": combined_text, "reasons": safety.reasons})
                continue
            post_type = item.get("post_type", "thread" if len(parts) > 1 else "single")
            drafts.append(
                PostDraft(
                    id=draft_id,
                    topic_id=topic.id,
                    text=text,
                    source_url=item.get("source_url", topic.source_url),
                    affiliate_intent=affiliate_intent,
                    post_type=post_type,
                    parts=parts,
                    cta_style=item.get("cta_style", "profile"),
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
            "プロフィールにはブログURLがすでに掲載されています。"
            "40代会社員、2児の父が実際にAI副業を試している目線で書いてください。"
            "各トピックから、Threads向けの単発投稿またはスレッド投稿を作成してください。"
            "説明文・記事紹介文ではなく、読者が保存や返信をしたくなる投稿にしてください。"
            "1つ目のpartは必ずフックにしてください。例: 失敗談、意外な気づき、質問、チェックリストの入口。"
            "2つ目以降のpartでは具体例、手順、注意点を短く分けてください。"
            "トレンド系トピックはニュースの丸写しではなく、AI副業初心者にどう関係するかへリライトしてください。"
            "Threadsで読まれる文章にするため、1つ目のpartは違和感、失敗談、反対意見、個人的な気づきのどれかで始めてください。"
            "説明文ではなく、読者が自分ごと化できる短い主張にしてください。例: すごい機能より今日30分浮くかを見る。"
            "抽象的な期待ではなく、ネタ出し、見出し作成、比較表づくり、SNS投稿化など具体的な作業に落としてください。"
            "40代会社員・2児の父として、時間が限られる人の視点を自然に入れてください。"
            "最後のpartには「詳しい手順はプロフィールのブログにまとめています」のような自然な導線を入れてください。"
            "URLを本文に直接貼るのは、cta_styleがdirect_urlの場合だけにしてください。通常はprofileにしてください。"
            "誇大表現、断定的な収益保証、煽りを避けてください。"
            "禁止表現: 解説しています、紹介しています、ぜひチェック、最新技術を生かすことで、興味がある方、効率アップ、チャンスが広がる、鍵、活用手順、掲載しています。"
            "各partは120文字以内を目安にしてください。"
            "JSON形式で {\"posts\":[{\"post_type\":\"single|thread\",\"parts\":[\"...\"],\"source_url\":\"...\",\"cta_style\":\"profile\",\"affiliate_intent\":false}]} を返してください。\n"
            f"{topic_lines}"
        )
