from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping


class ConfigError(RuntimeError):
    """Raised when configuration is unsafe for the requested mode."""


def _bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _int(value: str | None, default: int) -> int:
    if value is None or value == "":
        return default
    parsed = int(value)
    if parsed < 0:
        raise ConfigError("Numeric configuration values must be zero or greater")
    return parsed


@dataclass(frozen=True)
class BotConfig:
    enabled: bool
    dry_run: bool
    site_base_url: str
    line_offer_url: str
    affiliate_disclosure: str
    posts_per_day: int
    replies_per_day: int
    per_run_reply_limit: int
    openai_api_key: str | None
    threads_user_id: str | None
    threads_access_token: str | None

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "BotConfig":
        source = os.environ if env is None else env
        config = cls(
            enabled=_bool(source.get("BOT_ENABLED"), False),
            dry_run=_bool(source.get("DRY_RUN"), True),
            site_base_url=source.get("SITE_BASE_URL", "https://meganeojisanblog.com/ai-job/"),
            line_offer_url=source.get("LINE_OFFER_URL", ""),
            affiliate_disclosure=source.get("DEFAULT_AFFILIATE_DISCLOSURE", "PRを含みます。"),
            posts_per_day=_int(source.get("POSTS_PER_DAY"), 3),
            replies_per_day=_int(source.get("REPLIES_PER_DAY"), 30),
            per_run_reply_limit=_int(source.get("PER_RUN_REPLY_LIMIT"), 10),
            openai_api_key=source.get("OPENAI_API_KEY"),
            threads_user_id=source.get("THREADS_USER_ID"),
            threads_access_token=source.get("THREADS_ACCESS_TOKEN"),
        )
        config.validate()
        return config

    def validate(self) -> None:
        if self.posts_per_day > 3:
            raise ConfigError("POSTS_PER_DAY must be 3 or less for the initial rollout")
        if self.replies_per_day > 30:
            raise ConfigError("REPLIES_PER_DAY must be 30 or less for the initial rollout")
        if self.per_run_reply_limit > 10:
            raise ConfigError("PER_RUN_REPLY_LIMIT must be 10 or less")
        if self.enabled and not self.dry_run:
            missing = [
                name
                for name, value in {
                    "OPENAI_API_KEY": self.openai_api_key,
                    "THREADS_USER_ID": self.threads_user_id,
                    "THREADS_ACCESS_TOKEN": self.threads_access_token,
                }.items()
                if not value
            ]
            if missing:
                raise ConfigError(f"Missing required secret(s): {', '.join(missing)}")
