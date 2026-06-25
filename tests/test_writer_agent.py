from pathlib import Path

from threads_ai_agent.storage import JsonStorage
from threads_ai_agent.writer_agent import WriterAgent


def _topic(title: str = "Google AIの最新アップデート") -> object:
    return type(
        "TopicLike",
        (),
        {
            "id": "t1",
            "title": title,
            "source_url": "https://example.com",
            "intent": "trend",
        },
    )()


def test_writer_prompt_uses_readable_japanese_and_long_thread_rules():
    agent = WriterAgent(FakeTextClient(), JsonStorage("data"))

    prompt = agent._build_prompt([_topic()])

    assert "AI副業ブログのThreads運用担当" in prompt
    assert "220〜320文字" in prompt
    assert "2行だけの返信は禁止" in prompt
    assert "スレッド全体で900〜1,300文字" in prompt
    assert "プロフィールのブログ" in prompt
    assert "文字化けは禁止" in prompt


def test_writer_agent_creates_safe_queue(tmp_path: Path):
    storage = JsonStorage(tmp_path)
    storage.write_json(
        "topics.json",
        [
            {
                "id": "t1",
                "title": "AI副業おすすめ完全ガイド",
                "source_url": "https://meganeojisanblog.com/ai-job/ai-fukugyou-osusume-guide/",
                "intent": "blog",
                "weight": 1.0,
            }
        ],
    )

    drafts = WriterAgent(FakeTextClient(), storage).create_post_queue(count=1)

    assert len(drafts) == 1
    assert drafts[0].status == "queued"
    assert storage.read_json("post_queue.json", default=[])[0]["text"].startswith("AI副業")


def test_writer_agent_creates_thread_parts_with_profile_cta(tmp_path: Path):
    storage = JsonStorage(tmp_path)
    storage.write_json(
        "topics.json",
        [
            {
                "id": "t1",
                "title": "AI副業おすすめ完全ガイド",
                "source_url": "https://meganeojisanblog.com/ai-job/ai-fukugyou-osusume-guide/",
                "intent": "blog",
                "weight": 1.0,
            }
        ],
    )

    drafts = WriterAgent(FakeThreadTextClient(), storage).create_post_queue(count=1)

    assert drafts[0].post_type == "thread"
    assert len(drafts[0].parts) == 3
    assert drafts[0].cta_style == "profile"
    assert "プロフィールのブログ" in drafts[0].parts[-1]
    assert storage.read_json("post_queue.json", default=[])[0]["parts"] == drafts[0].parts


def test_writer_agent_falls_back_when_generated_posts_are_blocked(tmp_path: Path):
    storage = JsonStorage(tmp_path)
    storage.write_json(
        "topics.json",
        [
            {
                "id": "t1",
                "title": "AI副業ロードマップ",
                "source_url": "https://meganeojisanblog.com/ai-job/ai-sidejob-roadmap/",
                "intent": "blog",
                "weight": 1.0,
            }
        ],
    )

    drafts = WriterAgent(BlockedTextClient(), storage).create_post_queue(count=1)

    assert len(drafts) == 1
    assert drafts[0].topic_id == "t1"
    assert drafts[0].post_type == "thread"
    assert len(drafts[0].parts) == 3
    assert "プロフィールのブログ" in drafts[0].parts[-1]
    assert storage.read_json("post_queue.json", default=[])[0]["topic_id"] == "t1"
    assert storage.read_json("blocked_drafts.json", default=[])[0]["topic_id"] == "t1"


def test_writer_agent_sanitizes_mojibake_topic_titles_in_fallback(tmp_path: Path):
    storage = JsonStorage(tmp_path)
    storage.write_json(
        "topics.json",
        [
            {
                "id": "t1",
                "title": "AI蜑ｯ讌ｭ縺翫☆縺吶ａ",
                "source_url": "https://meganeojisanblog.com/ai-job/ai-sidejob-roadmap/",
                "intent": "blog",
                "weight": 1.0,
            }
        ],
    )

    drafts = WriterAgent(BlockedTextClient(), storage).create_post_queue(count=1)

    assert "縺" not in "\n".join(drafts[0].parts)
    assert "AI副業" in drafts[0].parts[0]


class FakeTextClient:
    def generate_json(self, prompt: str):
        return {
            "posts": [
                {
                    "text": "AI副業は、まず小さく試すことが大事です。失敗例と手順をブログにまとめました。",
                    "source_url": "https://meganeojisanblog.com/ai-job/ai-fukugyou-osusume-guide/",
                    "affiliate_intent": False,
                }
            ]
        }


class FakeThreadTextClient:
    def generate_json(self, prompt: str):
        return {
            "posts": [
                {
                    "post_type": "thread",
                    "parts": [
                        "AI副業で最初に迷うのは、何から始めるかです。ツールを増やすより、毎日30分で続けられる作業を一つ決めるほうが成果につながります。",
                        "僕なら、記事ネタを出す、見出しを作る、比較表を作る、Threads投稿へ分解する、の順番で進めます。ここまでなら初心者でも今日から試せます。",
                        "詳しい手順はプロフィールのブログにまとめています。忙しい会社員でも迷わないように、ロードマップ形式で整理しました。",
                    ],
                    "source_url": "https://meganeojisanblog.com/ai-job/ai-fukugyou-osusume-guide/",
                    "cta_style": "profile",
                    "affiliate_intent": False,
                }
            ]
        }


class BlockedTextClient:
    def generate_json(self, prompt: str):
        return {
            "posts": [
                {
                    "text": "AI副業なら誰でも必ず稼げるので、今すぐ始めれば月100万円を稼げます。",
                    "source_url": "https://meganeojisanblog.com/ai-job/ai-sidejob-roadmap/",
                    "affiliate_intent": False,
                }
            ]
        }
