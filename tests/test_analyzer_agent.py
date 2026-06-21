from pathlib import Path

from threads_ai_agent.analyzer_agent import AnalyzerAgent
from threads_ai_agent.storage import JsonStorage


def test_analyzer_writes_daily_report(tmp_path: Path):
    storage = JsonStorage(tmp_path)
    storage.append_jsonl("published_posts.jsonl", {"threads_media_id": "m1"})
    storage.append_jsonl("replies_sent.jsonl", {"reply_id": "r1"})
    storage.append_jsonl("blocked_replies.jsonl", {"reply_id": "r2"})

    report = AnalyzerAgent(storage).write_daily_report(date="2026-06-21")

    assert report.published_count == 1
    assert report.replies_sent_count == 1
    assert report.blocked_count == 1
    assert storage.read_jsonl("daily_reports.jsonl")[0]["date"] == "2026-06-21"
