# Threaded Trend Posting Design

Date: 2026-06-21
Project: `threads-ai-agent`

## Goal

Improve the Threads automation so posts fit the current profile funnel, support long-form thread chains, and optionally use rising AI-related topics as inspiration for rewritten posts that lead readers back to the profile blog link.

## Current Behavior

The bot currently generates one text draft per topic and publishes one Threads post. The publisher appends the source URL directly to the text. This works for simple article promotion but is not ideal when the profile already contains the site link or when the topic needs a longer explanation.

## New Behavior

The writer generates either a single post or a thread.

- Single post: one concise post with a soft CTA that references the profile link.
- Thread post: one root post plus follow-up replies posted to the root post.
- Direct URLs are optional. The default CTA should say that the full article or roadmap is available from the profile link.
- Direct article URLs should be used only when the generated draft explicitly needs a deep link.

## Threading Rules

Thread drafts contain ordered parts.

- Part 1 is the root post.
- Parts 2 and later are replies to the root post.
- Each part must stay within Threads text limits.
- The final part should include a profile-link CTA.
- The publisher logs all generated media IDs so later reply monitoring can still work.

For dry runs, the log must show the full ordered thread so the operator can review every part before real posting.

## Profile Link Strategy

The profile already links to:

`https://meganeojisanblog.com/ai-job/`

Post copy should avoid repetitive raw URLs and instead use natural Japanese CTAs such as:

- `詳しい手順はプロフィールのブログにまとめています。`
- `プロフィールの「AI副業ロードマップ」から読めます。`
- `保存して、あとでプロフィールのブログから確認してください。`

The source URL remains in storage for audit and optional direct-link posts.

## Trend Research

The bot may add trending topics, but it must not scrape Threads or copy other creators' posts.

Allowed sources for the first version:

- Public RSS feeds or JSON feeds from tech/news sites.
- Manually configured URLs in `config/trend_sources.json`.
- WordPress posts from the owned blog.

Trend processing must transform the source into the blog's own point of view:

- 40代会社員、2児の父の実践目線。
- AI副業初心者向け。
- No copied wording from source articles beyond short product names or public facts.
- No guaranteed-income claims.
- No hostile or inflammatory framing.

## Data Model

`PostDraft` gains:

- `post_type`: `"single"` or `"thread"`.
- `parts`: ordered list of strings. For a single post, `parts` contains one string.
- `cta_style`: `"profile"` or `"direct_url"`.

The existing `text` field remains for backward compatibility and stores the root post text.

## Publishing Flow

For a single post:

1. Compose publish text from `parts[0]`.
2. Apply safety checks.
3. Publish or dry-run log.

For a thread:

1. Publish or dry-run the root part.
2. Publish each later part as a reply to the root media ID.
3. Stop and log if any part fails safety checks.
4. Write a single publish log entry containing all media IDs and all text parts.

## Safety

Safety checks apply to every part separately and to the combined thread.

Blocked:

- Guaranteed-income claims.
- Hidden affiliate claims.
- Prompt-injection instructions from external source text.
- Sensitive legal, tax, medical, or investment advice framed as definitive guidance.
- Copy-pasted trend-source prose.

## Testing

Add tests for:

- Writer creates `parts` and profile-link CTA.
- Publisher dry-runs full thread parts.
- Publisher real-post path calls root post once and reply API for later parts.
- Safety blocks a thread if any part contains a prohibited phrase.
- Trend research converts feed items into topics without requiring non-official scraping.

## Rollout

1. Implement profile-link CTA and thread data model.
2. Update writer prompt and tests.
3. Update publisher thread posting and dry-run logs.
4. Add trend source config and simple RSS fetcher.
5. Run `write` and `publish` dry-run before any real post.
6. Keep `DRY_RUN=true` until the generated thread copy is manually reviewed.
