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
