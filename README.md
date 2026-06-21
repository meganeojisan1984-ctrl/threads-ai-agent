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
