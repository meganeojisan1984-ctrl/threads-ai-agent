# Threads AI Agent

GitHub Actions based Threads automation for https://meganeojisanblog.com/ai-job/.

## Local Setup

```powershell
python -m pip install -e .[dev]
pytest
```

## Safety Switch

Set `BOT_ENABLED=false` to stop all publish and reply actions.

## GitHub Secrets

- `OPENAI_API_KEY`
- `THREADS_USER_ID`
- `THREADS_ACCESS_TOKEN`

## GitHub Variables

- `BOT_ENABLED`
- `DRY_RUN`
- `SITE_BASE_URL`
- `LINE_OFFER_URL`
- `DEFAULT_AFFILIATE_DISCLOSURE`
- `POSTS_PER_DAY`
- `REPLIES_PER_DAY`
- `PER_RUN_REPLY_LIMIT`

## GitHub Rollout

1. Push this repository to GitHub.
2. Add repository secrets:
   - `OPENAI_API_KEY`
   - `THREADS_USER_ID`
   - `THREADS_ACCESS_TOKEN`
3. Add repository variables:
   - `BOT_ENABLED=false`
   - `DRY_RUN=true`
   - `SITE_BASE_URL=https://meganeojisanblog.com/ai-job/`
   - `POSTS_PER_DAY=3`
   - `REPLIES_PER_DAY=30`
   - `PER_RUN_REPLY_LIMIT=10`
4. Run the `manual` workflow with `analyze`.
5. Run the `manual` workflow with `research`.
6. Review `data/post_queue.json`.
7. Set `BOT_ENABLED=true` while keeping `DRY_RUN=true`.
8. Run `publish` manually and confirm `data/dry_run_publish.jsonl`.
9. Set `DRY_RUN=false` only after one dry-run publish looks correct.

## Full Automation

After one real `publish` workflow succeeds, switch to full automation with these repository variables:

- `BOT_ENABLED=true`
- `DRY_RUN=false`
- `POSTS_PER_DAY=3`
- `REPLIES_PER_DAY=30`
- `PER_RUN_REPLY_LIMIT=10`

The scheduled workflows then run automatically in Japan time:

- `research`: 07:17 JST, refreshes blog topics, trend topics, and the post queue.
- `publish`: 08:07, 12:07, and 20:07 JST, publishes one queued post each run.
- `reply`: 08:37, 12:37, 20:37, and 22:37 JST, replies within the daily reply limits.
- `analyze`: 23:41 JST, writes the daily report.

Emergency stop:

1. Set `BOT_ENABLED=false`.
2. Leave `DRY_RUN=true` until the next post queue has been reviewed.
3. If a bad draft appears, delete it from `data/post_queue.json` or rerun `manual` with `write`.

Recommended operating rhythm:

1. Check `data/published_posts.jsonl` once per day.
2. Check `data/daily_reports.jsonl` once per week.
3. Keep OpenAI project budget low while the automation is new.
