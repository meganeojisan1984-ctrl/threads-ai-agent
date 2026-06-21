from __future__ import annotations

import html

import requests


class WordPressClient:
    def __init__(self, site_base_url: str) -> None:
        self.site_base_url = site_base_url.rstrip("/") + "/"

    def fetch_recent_posts(self, limit: int = 20) -> list[dict]:
        endpoint = self.site_base_url + "wp-json/wp/v2/posts"
        response = requests.get(
            endpoint,
            params={"per_page": min(limit, 100), "_fields": "id,link,title,date,modified"},
            timeout=20,
        )
        response.raise_for_status()
        posts = response.json()
        for post in posts:
            post["title"]["rendered"] = html.unescape(post["title"]["rendered"])
        return posts
