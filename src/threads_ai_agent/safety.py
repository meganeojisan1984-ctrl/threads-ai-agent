from __future__ import annotations

from threads_ai_agent.models import ReplyDecision, SafetyResult


BLOCKED_PHRASES = [
    "必ず稼げる",
    "絶対稼げる",
    "誰でも稼げる",
    "放置で月収",
    "月100万円を稼げます",
    "確実に稼げる",
]

RISKY_REPLY_KEYWORDS = [
    "税金",
    "確定申告",
    "会社にバレ",
    "労働契約",
    "法律",
    "違法",
    "投資助言",
    "病気",
    "死にたい",
    "訴える",
]

PROMPT_INJECTION_MARKERS = [
    "前の指示を無視",
    "システムプロンプト",
    "ignore previous",
    "reveal your instructions",
]

SENSITIVE_TOPIC_KEYWORDS = [
    "amie",
    "chronic disease",
    "diagnosis",
    "medical ai",
    "medicine",
    "医療",
    "診断",
    "治療",
    "疾患",
    "慢性疾患",
    "薬",
    "税務判断",
    "法律判断",
    "訴訟",
]

PROMOTIONAL_TEMPLATE_PHRASES = [
    "解説しています",
    "紹介しています",
    "ぜひチェック",
    "興味がある方",
    "最新技術を生かすことで",
    "効率アップ",
    "チャンスが広がる",
    "活用手順",
    "掲載しています",
    "確認いただければ幸い",
    "おすすめしたい",
    "迅速",
    "差がつく穴",
    "本質",
    "近道",
    "マッチします",
    "ブログで書いています",
]


def has_sensitive_topic(text: str) -> bool:
    normalized = text.lower()
    return any(keyword in normalized for keyword in SENSITIVE_TOPIC_KEYWORDS)


class SafetyAgent:
    def check_text(self, text: str, *, affiliate_intent: bool = False) -> SafetyResult:
        reasons: list[str] = []
        normalized = text.lower()
        if any(phrase in text for phrase in BLOCKED_PHRASES):
            reasons.append("guaranteed_income")
        if any(marker in normalized for marker in PROMPT_INJECTION_MARKERS):
            reasons.append("prompt_injection")
        if has_sensitive_topic(text):
            reasons.append("sensitive_topic")
        if any(phrase in text for phrase in PROMOTIONAL_TEMPLATE_PHRASES):
            reasons.append("promotional_template")
        if affiliate_intent and "PR" not in text and "アフィリエイト" not in text:
            reasons.append("missing_pr_disclosure")
        return SafetyResult(allowed=not reasons, reasons=reasons)

    def classify_reply(self, text: str) -> ReplyDecision:
        normalized = text.lower()
        if any(marker in normalized for marker in PROMPT_INJECTION_MARKERS):
            return ReplyDecision(
                category="risky",
                auto_reply_allowed=False,
                reasons=["prompt_injection"],
            )
        if any(keyword in text for keyword in RISKY_REPLY_KEYWORDS):
            return ReplyDecision(
                category="risky",
                auto_reply_allowed=False,
                reasons=["sensitive_topic"],
            )
        if any(keyword in text for keyword in ["有料", "スクール", "稼ぐ", "案件", "ツール"]):
            return ReplyDecision(category="sales_sensitive", auto_reply_allowed=True, reasons=[])
        if len(text.strip()) < 2:
            return ReplyDecision(category="unknown", auto_reply_allowed=False, reasons=["too_short"])
        return ReplyDecision(category="safe", auto_reply_allowed=True, reasons=[])
