import pytest

from threads_ai_agent.config import BotConfig, ConfigError


def test_bot_config_defaults_are_safe():
    config = BotConfig.from_env({})

    assert config.enabled is False
    assert config.dry_run is True
    assert config.site_base_url == "https://meganeojisanblog.com/ai-job/"
    assert config.posts_per_day == 3
    assert config.replies_per_day == 30
    assert config.per_run_reply_limit == 10


def test_bot_config_parses_boolean_and_integer_values():
    config = BotConfig.from_env({
        "BOT_ENABLED": "true",
        "DRY_RUN": "false",
        "POSTS_PER_DAY": "2",
        "REPLIES_PER_DAY": "12",
        "PER_RUN_REPLY_LIMIT": "4",
        "OPENAI_API_KEY": "x",
        "THREADS_USER_ID": "u",
        "THREADS_ACCESS_TOKEN": "token",
    })

    assert config.enabled is True
    assert config.dry_run is False
    assert config.posts_per_day == 2
    assert config.replies_per_day == 12
    assert config.per_run_reply_limit == 4


def test_missing_threads_token_fails_when_publish_is_enabled():
    with pytest.raises(ConfigError, match="THREADS_ACCESS_TOKEN"):
        BotConfig.from_env({"BOT_ENABLED": "true", "DRY_RUN": "false"})
