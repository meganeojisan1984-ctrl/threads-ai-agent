from __future__ import annotations

import argparse

from threads_ai_agent.analyzer_agent import AnalyzerAgent
from threads_ai_agent.config import BotConfig
from threads_ai_agent.openai_client import OpenAITextClient
from threads_ai_agent.publisher_agent import PublisherAgent
from threads_ai_agent.reply_agent import ReplyAgent
from threads_ai_agent.research_agent import ResearchAgent
from threads_ai_agent.storage import JsonStorage
from threads_ai_agent.threads_client import ThreadsClient
from threads_ai_agent.trend_agent import TrendResearchAgent
from threads_ai_agent.wordpress import WordPressClient
from threads_ai_agent.writer_agent import WriterAgent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="threads-agent")
    parser.add_argument("command", choices=["research", "trends", "write", "publish", "reply", "analyze"])
    parser.add_argument("--data-dir", default="data")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = BotConfig.from_env()
    storage = JsonStorage(args.data_dir)

    if args.command == "research":
        ResearchAgent(WordPressClient(config.site_base_url), storage).refresh_topics()
        return 0
    if args.command == "trends":
        TrendResearchAgent(storage).refresh_trends()
        return 0
    if args.command == "write":
        if not config.openai_api_key:
            raise SystemExit("OPENAI_API_KEY is required for write")
        WriterAgent(OpenAITextClient(config.openai_api_key), storage).create_post_queue(
            count=config.posts_per_day
        )
        return 0
    if args.command == "publish":
        if not config.threads_user_id or not config.threads_access_token:
            raise SystemExit("THREADS_USER_ID and THREADS_ACCESS_TOKEN are required for publish")
        PublisherAgent(
            ThreadsClient(config.threads_user_id, config.threads_access_token),
            storage,
            config,
        ).publish_next()
        return 0
    if args.command == "reply":
        if not config.openai_api_key or not config.threads_user_id or not config.threads_access_token:
            raise SystemExit("OPENAI_API_KEY, THREADS_USER_ID, and THREADS_ACCESS_TOKEN are required for reply")
        ReplyAgent(
            ThreadsClient(config.threads_user_id, config.threads_access_token),
            OpenAITextClient(config.openai_api_key),
            storage,
            config,
        ).process_replies()
        return 0
    if args.command == "analyze":
        AnalyzerAgent(storage).write_daily_report()
        return 0
    raise SystemExit(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
