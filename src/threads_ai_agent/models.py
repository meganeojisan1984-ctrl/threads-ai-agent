from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class Topic(BaseModel):
    id: str
    title: str
    source_url: str
    intent: str = "blog"
    weight: float = 1.0


class PostDraft(BaseModel):
    id: str
    topic_id: str
    text: str
    source_url: str
    affiliate_intent: bool = False
    status: str = "queued"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PublishedPost(BaseModel):
    draft_id: str
    threads_media_id: str
    text: str
    source_url: str
    published_at: datetime = Field(default_factory=datetime.utcnow)


class IncomingReply(BaseModel):
    reply_id: str
    media_id: str
    username: str
    text: str
    created_at: datetime | None = None


class ReplyDecision(BaseModel):
    category: str
    auto_reply_allowed: bool
    reasons: list[str] = Field(default_factory=list)


class SafetyResult(BaseModel):
    allowed: bool
    reasons: list[str] = Field(default_factory=list)


class DailyReport(BaseModel):
    date: str
    published_count: int
    replies_sent_count: int
    blocked_count: int
    notes: list[str] = Field(default_factory=list)
