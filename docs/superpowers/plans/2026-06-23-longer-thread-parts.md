# Longer Thread Parts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make each Threads reply part substantial enough to communicate a clear point and create save-worthy value.

**Architecture:** Keep the current `parts` publishing model. Change only the writer prompt so generated parts become longer, self-contained, and structured around claim, reason, and concrete example.

**Tech Stack:** Python, pytest, existing OpenAI JSON generation wrapper.

## Global Constraints

- Keep the thread model: one root post plus replies.
- Keep the profile-link CTA.
- Do not change posting schedule or Threads API behavior.
- Do not add dependencies.

---

### Task 1: Lock Prompt Requirements

**Files:**
- Modify: `tests/test_writer_agent.py`

**Interfaces:**
- Consumes: `WriterAgent._build_prompt(topics) -> str`
- Produces: Tests that require longer part guidance and save-worthy structure.

- [ ] Add assertions for `220〜320文字`, `最低3文`, `1投稿だけ読んでも意味が通る`, `主張・理由・具体例`, and `スレッド全体で900〜1,300文字`.

### Task 2: Update Writer Prompt

**Files:**
- Modify: `src/threads_ai_agent/writer_agent.py`

**Interfaces:**
- Consumes: Same prompt builder.
- Produces: Longer, standalone thread parts.

- [ ] Replace the old `各partは120文字以内` rule.
- [ ] Add minimum sentence count and save-worthy value requirements.
- [ ] Keep existing hook, affiliate flow, and banned phrase rules.

### Task 3: Verify

**Files:**
- Verify: `tests/test_writer_agent.py`

**Interfaces:**
- Produces: Passing full test suite.

- [ ] Run targeted prompt test.
- [ ] Run full `uv run --extra dev pytest`.
- [ ] Commit and push.
