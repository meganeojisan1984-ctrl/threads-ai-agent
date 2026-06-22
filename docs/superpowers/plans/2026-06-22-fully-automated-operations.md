# Fully Automated Operations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Document and label the already-built GitHub Actions schedules so the Threads agent can be safely switched into fully automated operation.

**Architecture:** Keep the existing scheduled workflows. Add operator-facing README instructions and JST comments in workflow files so the user can enable, pause, and audit the automation without changing code.

**Tech Stack:** GitHub Actions, Python CLI, Markdown documentation.

## Global Constraints

- Keep `BOT_ENABLED=false` as the emergency stop.
- Keep `DRY_RUN=true` as the review mode.
- Do not change posting cadence in this task.
- Do not change API secrets or repository variables from code.

---

### Task 1: Document Full Automation

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: Existing GitHub variables `BOT_ENABLED`, `DRY_RUN`, `POSTS_PER_DAY`, `REPLIES_PER_DAY`, and `PER_RUN_REPLY_LIMIT`.
- Produces: A clear checklist for switching from dry-run to fully automated posting.

- [ ] Add a `Full Automation` section with exact variable values.
- [ ] Add the daily JST schedule.
- [ ] Add the emergency pause and rollback steps.

### Task 2: Label Workflow Schedules

**Files:**
- Modify: `.github/workflows/research.yml`
- Modify: `.github/workflows/publish.yml`
- Modify: `.github/workflows/reply.yml`
- Modify: `.github/workflows/analyze.yml`

**Interfaces:**
- Consumes: Existing cron schedules.
- Produces: Comments explaining each UTC cron in Japan time.

- [ ] Add comments above each `cron` line.
- [ ] Keep all cron expressions unchanged.

### Task 3: Verify and Commit

**Files:**
- Verify: changed Markdown/YAML files.

**Interfaces:**
- Produces: A committed and pushed documentation update.

- [ ] Run `git diff --check`.
- [ ] Commit with `docs: add fully automated operations guide`.
- [ ] Push to GitHub.
