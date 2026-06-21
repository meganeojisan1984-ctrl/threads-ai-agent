# Threaded Trend Posting Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add profile-link-aware copy, long-form thread publishing, and safe trend-topic ingestion to the Threads automation.

**Architecture:** Extend the existing Python package without changing the GitHub Actions interface. `PostDraft` gains ordered `parts`, `post_type`, and `cta_style`; `WriterAgent` asks for thread-aware JSON; `PublisherAgent` publishes root posts and replies; `TrendResearchAgent` converts configured RSS feeds into owned-viewpoint topics.

**Tech Stack:** Python 3.11+, pytest, requests, pydantic, official Threads Graph API.

## Global Constraints

- Default CTA should reference the existing profile blog link.
- Direct URLs are optional and should be used only when a draft explicitly requests a deep link.
- Long-form drafts must be posted as a root post plus replies to the root post.
- Dry-run logs must show the full ordered thread before real posting.
- Trend research must not scrape Threads or copy other creators' posts.
- Trend sources are limited to configured public RSS/XML feeds for this version.
- Safety checks must run on every part and on the combined thread.
- Keep `DRY_RUN=true` until generated thread copy is reviewed.

---

## File Structure

- Modify `src/threads_ai_agent/models.py`: add thread-aware fields to `PostDraft`.
- Modify `src/threads_ai_agent/writer_agent.py`: update prompt and parsing for `parts`, `post_type`, and profile CTA.
- Modify `src/threads_ai_agent/publisher_agent.py`: publish ordered thread parts and log dry-run/full publish details.
- Modify `src/threads_ai_agent/threads_client.py`: reuse `reply_to_media` for thread replies.
- Create `src/threads_ai_agent/trend_agent.py`: fetch RSS feed items and convert them into `Topic` records.
- Create `config/trend_sources.json`: configured public trend feeds.
- Modify `src/threads_ai_agent/cli.py`: add optional `trends` command.
- Add tests in `tests/test_writer_agent.py`, `tests/test_publisher_agent.py`, and `tests/test_trend_agent.py`.

---

### Task 1: Thread-Aware Draft Model and Writer

**Files:**
- Modify: `E:/threads-ai-agent/src/threads_ai_agent/models.py`
- Modify: `E:/threads-ai-agent/src/threads_ai_agent/writer_agent.py`
- Modify: `E:/threads-ai-agent/tests/test_writer_agent.py`

**Interfaces:**
- Produces: `PostDraft.post_type: str`
- Produces: `PostDraft.parts: list[str]`
- Produces: `PostDraft.cta_style: str`

- [ ] **Step 1: Add writer tests**

Add tests asserting a generated thread draft preserves `parts`, uses `post_type="thread"`, and includes a profile-link CTA in the last part.

- [ ] **Step 2: Run writer tests and confirm failure**

Run: `python -m pytest tests/test_writer_agent.py -v`

- [ ] **Step 3: Add model fields**

Add default fields to `PostDraft`:

```python
post_type: str = "single"
parts: list[str] = Field(default_factory=list)
cta_style: str = "profile"
```

- [ ] **Step 4: Update writer parsing**

When OpenAI returns `parts`, use them. If not, fall back to `[text]`. Set `text` to `parts[0]`.

- [ ] **Step 5: Update writer prompt**

Ask for JSON with:

```json
{"posts":[{"post_type":"single|thread","parts":["..."],"source_url":"...","cta_style":"profile|direct_url","affiliate_intent":false}]}
```

The prompt must tell the model that the profile already contains the blog link.

- [ ] **Step 6: Verify and commit**

Run: `python -m pytest tests/test_writer_agent.py -v`

Commit: `feat: add thread-aware writer drafts`

---

### Task 2: Thread Publishing and Dry-Run Logs

**Files:**
- Modify: `E:/threads-ai-agent/src/threads_ai_agent/publisher_agent.py`
- Modify: `E:/threads-ai-agent/tests/test_publisher_agent.py`

**Interfaces:**
- Consumes: `PostDraft.parts`
- Produces dry-run log entries with `parts`
- Produces publish log entries with `thread_media_ids`

- [ ] **Step 1: Add publisher tests**

Add tests for:

- dry-run thread logs all parts.
- real publish posts root once and replies for later parts.
- any unsafe part blocks the whole thread.

- [ ] **Step 2: Run publisher tests and confirm failure**

Run: `python -m pytest tests/test_publisher_agent.py -v`

- [ ] **Step 3: Implement publish part composition**

For `cta_style="profile"`, do not append raw URL. For `cta_style="direct_url"`, append `source_url` only to the final part if absent.

- [ ] **Step 4: Implement thread publish flow**

Publish part 1 with `create_text_container` and `publish_container`. Publish parts 2+ with `reply_to_media(root_media_id, part)`.

- [ ] **Step 5: Verify and commit**

Run: `python -m pytest tests/test_publisher_agent.py tests/test_threads_client.py -v`

Commit: `feat: publish long drafts as threads`

---

### Task 3: Safe Trend Source Ingestion

**Files:**
- Create: `E:/threads-ai-agent/src/threads_ai_agent/trend_agent.py`
- Create: `E:/threads-ai-agent/config/trend_sources.json`
- Create: `E:/threads-ai-agent/tests/test_trend_agent.py`
- Modify: `E:/threads-ai-agent/src/threads_ai_agent/cli.py`

**Interfaces:**
- Produces: `TrendResearchAgent.refresh_trends(limit: int = 10) -> list[Topic]`
- CLI command: `threads-agent trends`

- [ ] **Step 1: Add trend tests**

Test that RSS items become `Topic` records with `intent="trend"` and source URLs preserved.

- [ ] **Step 2: Run trend tests and confirm failure**

Run: `python -m pytest tests/test_trend_agent.py -v`

- [ ] **Step 3: Implement RSS ingestion**

Use `xml.etree.ElementTree` and `requests` to read configured RSS feeds. Parse `item/title` and `item/link`.

- [ ] **Step 4: Merge trends into topics**

Write trend topics to `trend_topics.json` and prepend them to `topics.json` without deleting owned blog topics.

- [ ] **Step 5: Add CLI command**

Add `trends` to the CLI choices and call `TrendResearchAgent`.

- [ ] **Step 6: Verify and commit**

Run: `python -m pytest tests/test_trend_agent.py tests/test_cli.py -v`

Commit: `feat: add safe trend topic ingestion`

---

### Task 4: Final Verification and GitHub Push

**Files:**
- All modified files.

- [ ] **Step 1: Run full tests**

Run: `python -m pytest -v`

- [ ] **Step 2: Run local dry-run shape check**

Run:

```powershell
python -m threads_ai_agent.cli analyze --data-dir data
```

- [ ] **Step 3: Push**

Run:

```powershell
git pull --rebase origin main
git push
```

## Self-Review

- Spec coverage: Thread publishing, profile-link CTA, dry-run review, and safe trend RSS ingestion are covered.
- Placeholder scan: No placeholder implementation steps remain.
- Type consistency: `PostDraft.parts`, `post_type`, and `cta_style` are introduced before publisher usage.
