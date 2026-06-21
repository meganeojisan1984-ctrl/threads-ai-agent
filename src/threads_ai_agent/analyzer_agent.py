from __future__ import annotations

from datetime import date as date_type

from threads_ai_agent.models import DailyReport
from threads_ai_agent.storage import JsonStorage


class AnalyzerAgent:
    def __init__(self, storage: JsonStorage) -> None:
        self.storage = storage

    def write_daily_report(self, date: str | None = None) -> DailyReport:
        report = DailyReport(
            date=date or date_type.today().isoformat(),
            published_count=len(self.storage.read_jsonl("published_posts.jsonl")),
            replies_sent_count=len(self.storage.read_jsonl("replies_sent.jsonl")),
            blocked_count=(
                len(self.storage.read_jsonl("blocked_replies.jsonl"))
                + len(self.storage.read_jsonl("blocked_publish.jsonl"))
            ),
            notes=["GitHub Actions MVP report. Add Threads insights after app review access is confirmed."],
        )
        self.storage.append_jsonl("daily_reports.jsonl", report.model_dump(mode="json"))
        return report
