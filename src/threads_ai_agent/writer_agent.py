from __future__ import annotations

import hashlib
import html
import re

from threads_ai_agent.models import PostDraft, Topic
from threads_ai_agent.safety import SafetyAgent
from threads_ai_agent.storage import JsonStorage


MOJIBAKE_MARKERS = ("縺", "繧", "蜑", "讌", "譛", "螟", "逕", "遞", "謚")


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
        generated_posts = result.get("posts", []) if isinstance(result, dict) else []
        drafts: list[PostDraft] = []
        blocked: list[dict] = []

        for index, topic in enumerate(topics):
            item = generated_posts[index] if index < len(generated_posts) else {}
            draft = self._draft_from_generated(item, topic)
            if draft is not None:
                safety = self.safety.check_text(
                    "\n\n".join(draft.parts), affiliate_intent=draft.affiliate_intent
                )
                if safety.allowed:
                    drafts.append(draft)
                    continue
                blocked.append({"topic_id": topic.id, "text": "\n\n".join(draft.parts), "reasons": safety.reasons})

            fallback = self._fallback_draft(topic)
            fallback_safety = self.safety.check_text(
                "\n\n".join(fallback.parts), affiliate_intent=fallback.affiliate_intent
            )
            if fallback_safety.allowed:
                drafts.append(fallback)
            else:
                blocked.append(
                    {
                        "topic_id": topic.id,
                        "text": "\n\n".join(fallback.parts),
                        "reasons": fallback_safety.reasons,
                    }
                )

        self.storage.write_json("post_queue.json", [draft.model_dump(mode="json") for draft in drafts])
        if blocked:
            self.storage.write_json("blocked_drafts.json", blocked)
        return drafts

    def _draft_from_generated(self, item: dict, topic: Topic) -> PostDraft | None:
        if not isinstance(item, dict):
            return None
        affiliate_intent = bool(item.get("affiliate_intent", topic.intent == "affiliate"))
        parts = [part.strip() for part in item.get("parts", []) if isinstance(part, str) and part.strip()]
        if not parts and isinstance(item.get("text"), str) and item["text"].strip():
            parts = [item["text"].strip()]
        if not parts:
            return None
        combined_text = "\n\n".join(parts)
        draft_id = hashlib.sha1(f"{topic.id}:{combined_text}".encode("utf-8")).hexdigest()[:16]
        post_type = item.get("post_type", "thread" if len(parts) > 1 else "single")
        return PostDraft(
            id=draft_id,
            topic_id=topic.id,
            text=parts[0],
            source_url=item.get("source_url", topic.source_url),
            affiliate_intent=affiliate_intent,
            post_type=post_type,
            parts=parts,
            cta_style=item.get("cta_style", "profile"),
        )

    def _fallback_draft(self, topic: Topic) -> PostDraft:
        title = _safe_topic_title(topic.title)
        affiliate_intent = topic.intent == "affiliate"
        disclosure = "PRを含みます。" if affiliate_intent else ""
        parts = [
            (
                f"{disclosure}{title}について、AI副業で見るべきポイントは「何がすごいか」より"
                "「今日の作業に変えられるか」です。ニュースや記事を読んで終わると、時間だけが溶けます。"
                "まずは自分の副業に使える作業へ分解するのが大事です。"
            ),
            (
                "僕なら、記事ネタを10個出す、見出しを3案作る、比較表を作る、Threads用に短く分ける、"
                "の順番で試します。派手な機能を全部追うより、毎日30分で繰り返せる型を作るほうが、"
                "ブログ収益化に近づきます。"
            ),
            (
                "AI副業の始め方や、ブログ収益につなげる流れはプロフィールのブログに整理しています。"
                "まずは無料で試せる範囲から、今日の作業に落とし込んでみてください。"
            ),
        ]
        combined_text = "\n\n".join(parts)
        draft_id = hashlib.sha1(f"fallback:{topic.id}:{combined_text}".encode("utf-8")).hexdigest()[:16]
        return PostDraft(
            id=draft_id,
            topic_id=topic.id,
            text=parts[0],
            source_url=topic.source_url,
            affiliate_intent=affiliate_intent,
            post_type="thread",
            parts=parts,
            cta_style="profile",
        )

    def _build_prompt(self, topics: list[Topic]) -> str:
        topic_lines = "\n".join(
            f"- {_safe_topic_title(topic.title)}: {topic.source_url} ({topic.intent})" for topic in topics
        )
        return (
            "あなたはAI副業ブログのThreads運用担当です。プロフィールにはブログURLがすでに掲載されています。"
            "40代会社員、2児の父が実際にAI副業を試している目線で書いてください。"
            "文字化けは禁止です。必ず自然な日本語で出力してください。"
            "\n\n"
            "目的は、読者が投稿を保存・返信し、プロフィールのブログを見に行きたくなることです。"
            "単なるニュース紹介や記事説明ではなく、読者の悩み、失敗原因、具体行動、プロフィール誘導の流れにしてください。"
            "\n\n"
            "投稿ルール:\n"
            "- 各partは220〜320文字を目安にしてください。最後のpartは160〜240文字でも構いません。\n"
            "- 2行だけの返信は禁止です。各partは最低3文にしてください。\n"
            "- 1投稿だけ読んでも意味が通るように、各partに主張・理由・具体例のうち最低2つを入れてください。\n"
            "- スレッド全体で900〜1,300文字を目安にしてください。\n"
            "- 1つ目のpartは、違和感、失敗談、反対意見、個人的な気づきのどれかで始めてください。\n"
            "- 抽象的な期待ではなく、ネタ出し、見出し作成、比較表作成、SNS投稿化など具体的な作業に落としてください。\n"
            "- URLは本文に直接貼らず、通常はプロフィールのブログに誘導してください。\n"
            "- affiliate_intent が true の投稿には、自然に『PRを含みます』を入れてください。\n"
            "- 誇大表現、収益保証、医療・法律・税務の断定、弱い紹介文を避けてください。\n"
            "- 禁止表現: 解説しています、紹介しています、ぜひチェック、興味がある方、効率アップ、チャンスが広がる、掲載しています、確認いただければ幸いです。\n"
            "\n"
            "JSON形式で {\"posts\":[{\"post_type\":\"single|thread\",\"parts\":[\"...\"],\"source_url\":\"...\",\"cta_style\":\"profile\",\"affiliate_intent\":false}]} を返してください。\n"
            f"{topic_lines}"
        )


def _safe_topic_title(title: str) -> str:
    cleaned = html.unescape(re.sub(r"<[^>]+>", "", title)).strip()
    if not cleaned or _looks_mojibake(cleaned):
        return "AI副業の最新テーマ"
    return cleaned[:80]


def _looks_mojibake(value: str) -> bool:
    marker_count = sum(value.count(marker) for marker in MOJIBAKE_MARKERS)
    return marker_count >= 2
