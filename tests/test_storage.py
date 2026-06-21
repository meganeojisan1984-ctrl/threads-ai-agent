from pathlib import Path

from threads_ai_agent.storage import JsonStorage


def test_json_storage_round_trips_list(tmp_path: Path):
    storage = JsonStorage(tmp_path)
    storage.write_json("topics.json", [{"id": "t1", "title": "AI副業"}])

    assert storage.read_json("topics.json", default=[]) == [{"id": "t1", "title": "AI副業"}]


def test_jsonl_storage_appends_records(tmp_path: Path):
    storage = JsonStorage(tmp_path)
    storage.append_jsonl("published_posts.jsonl", {"id": "p1"})
    storage.append_jsonl("published_posts.jsonl", {"id": "p2"})

    assert storage.read_jsonl("published_posts.jsonl") == [{"id": "p1"}, {"id": "p2"}]
