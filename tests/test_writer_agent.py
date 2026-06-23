from pathlib import Path

from threads_ai_agent.storage import JsonStorage
from threads_ai_agent.writer_agent import WriterAgent


def test_writer_prompt_requires_longer_save_worthy_thread_parts():
    storage = JsonStorage("data")
    agent = WriterAgent(FakeTextClient(), storage)
    prompt = agent._build_prompt([
        type("TopicLike", (), {
            "title": "Google AI latest release",
            "source_url": "https://example.com",
            "intent": "trend",
        })()
    ])

    assert "220〜320文字" in prompt
    assert "最低3文" in prompt
    assert "1投稿だけ読んでも意味が通る" in prompt
    assert "主張・理由・具体例" in prompt
    assert "スレッド全体で900〜1,300文字" in prompt
    assert "2行だけの返信は禁止" in prompt


def test_writer_prompt_requires_viral_threads_style_rules():
    storage = JsonStorage("data")
    agent = WriterAgent(FakeTextClient(), storage)
    prompt = agent._build_prompt([
        type("TopicLike", (), {
            "title": "Google AI latest release",
            "source_url": "https://example.com",
            "intent": "trend",
        })()
    ])

    assert "違和感" in prompt
    assert "失敗談" in prompt
    assert "今日30分浮くか" in prompt
    assert "説明文ではなく" in prompt
    assert "効率アップ" in prompt


def test_writer_prompt_blocks_overhyped_threads_phrases():
    storage = JsonStorage("data")
    agent = WriterAgent(FakeTextClient(), storage)
    prompt = agent._build_prompt([
        type("TopicLike", (), {
            "title": "Google AI latest release",
            "source_url": "https://example.com",
            "intent": "trend",
        })()
    ])

    assert "確認いただければ幸いです" in prompt
    assert "おすすめしたい" in prompt
    assert "爆速" in prompt
    assert "落とし穴があった" in prompt
    assert "差がつく" in prompt


def test_writer_prompt_requires_problem_to_affiliate_flow():
    storage = JsonStorage("data")
    agent = WriterAgent(FakeTextClient(), storage)
    prompt = agent._build_prompt([
        type("TopicLike", (), {
            "title": "Google AI latest release",
            "source_url": "https://example.com",
            "intent": "trend",
        })()
    ])

    assert "読者の悩み" in prompt
    assert "失敗原因" in prompt
    assert "具体行動" in prompt
    assert "ブログ収益につなげる流れ" in prompt
    assert "AIニュースを毎日追ってるのに" in prompt


class FakeTextClient:
    def generate_json(self, prompt: str):
        return {
            "posts": [
                {
                    "text": "AI副業は、まず小さく試すのが大事です。失敗談と手順をブログにまとめました。",
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
                        "AI副業で最初に迷うのは、何から始めるかです。",
                        "おすすめは、ツールを増やす前に小さな作業を1つ自動化することです。",
                        "詳しい手順はプロフィールのブログにまとめています。",
                    ],
                    "source_url": "https://meganeojisanblog.com/ai-job/ai-fukugyou-osusume-guide/",
                    "cta_style": "profile",
                    "affiliate_intent": False,
                }
            ]
        }


def test_writer_agent_creates_safe_queue(tmp_path: Path):
    storage = JsonStorage(tmp_path)
    storage.write_json("topics.json", [{
        "id": "t1",
        "title": "AI副業おすすめ完全ガイド",
        "source_url": "https://meganeojisanblog.com/ai-job/ai-fukugyou-osusume-guide/",
        "intent": "blog",
        "weight": 1.0,
    }])
    agent = WriterAgent(FakeTextClient(), storage)

    drafts = agent.create_post_queue(count=1)

    assert len(drafts) == 1
    assert drafts[0].status == "queued"
    assert storage.read_json("post_queue.json", default=[])[0]["text"].startswith("AI副業")


def test_writer_agent_creates_thread_parts_with_profile_cta(tmp_path: Path):
    storage = JsonStorage(tmp_path)
    storage.write_json("topics.json", [{
        "id": "t1",
        "title": "AI副業おすすめ完全ガイド",
        "source_url": "https://meganeojisanblog.com/ai-job/ai-fukugyou-osusume-guide/",
        "intent": "blog",
        "weight": 1.0,
    }])
    agent = WriterAgent(FakeThreadTextClient(), storage)

    drafts = agent.create_post_queue(count=1)

    assert drafts[0].post_type == "thread"
    assert len(drafts[0].parts) == 3
    assert drafts[0].cta_style == "profile"
    assert "プロフィール" in drafts[0].parts[-1]
    assert storage.read_json("post_queue.json", default=[])[0]["parts"] == drafts[0].parts


def test_writer_prompt_asks_for_threads_native_copy():
    storage = JsonStorage("data")
    agent = WriterAgent(FakeTextClient(), storage)
    prompt = agent._build_prompt([
        type("TopicLike", (), {
            "title": "急上昇AIニュース",
            "source_url": "https://example.com",
            "intent": "trend",
        })()
    ])

    assert "説明文・記事紹介文ではなく" in prompt
    assert "1つ目のpartは必ずフック" in prompt
    assert "ニュースの丸写しではなく" in prompt
    assert "プロフィールにはブログURLがすでに掲載" in prompt
    assert "禁止表現" in prompt
