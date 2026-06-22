# Threads Viral Copy Style Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make generated Threads drafts feel like readable, trend-aware posts instead of generic article summaries.

**Architecture:** Keep the existing writer and safety pipeline. Strengthen the writer prompt with concrete Threads copy rules, then add safety checks that block generic AI-marketing phrases that make posts feel automated.

**Tech Stack:** Python, pytest, existing OpenAI JSON generation wrapper.

## Global Constraints

- Keep profile-link CTAs because the Threads profile already contains the blog URL.
- Keep long posts as `parts` so the publisher can post the first item and reply with the rest.
- Avoid high-risk topics such as medical, legal, tax, and investment advice.
- Do not add new dependencies.

---

### Task 1: Block Generic Growth Copy

**Files:**
- Modify: `src/threads_ai_agent/safety.py`
- Test: `tests/test_safety.py`

**Interfaces:**
- Consumes: `SafetyAgent.check_text(text: str, affiliate_intent: bool = False) -> SafetyResult`
- Produces: Additional `promotional_template` reasons for generic phrasing.

- [ ] **Step 1: Write failing tests**

```python
def test_safety_blocks_generic_threads_growth_phrases():
    result = SafetyAgent().check_text("AI副業の効率アップや新サービス開発のチャンスが広がる。")
    assert result.allowed is False
    assert "promotional_template" in result.reasons
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run --extra dev pytest tests/test_safety.py::test_safety_blocks_generic_threads_growth_phrases`
Expected: FAIL because the phrase is not blocked yet.

- [ ] **Step 3: Write minimal implementation**

Add `効率アップ`, `チャンスが広がる`, `鍵`, `活用手順`, and `掲載しています` to `PROMOTIONAL_TEMPLATE_PHRASES`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run --extra dev pytest tests/test_safety.py`
Expected: PASS.

### Task 2: Strengthen Writer Prompt

**Files:**
- Modify: `src/threads_ai_agent/writer_agent.py`
- Test: `tests/test_writer_agent.py`

**Interfaces:**
- Consumes: `WriterAgent._build_prompt(topics: list[Topic]) -> str`
- Produces: Prompt text containing the required viral Threads style rules.

- [ ] **Step 1: Write failing tests**

```python
def test_writer_prompt_requires_threads_native_hook_and_personal_angle():
    prompt = WriterAgent(text_client=object(), storage=JsonStorage(Path(".")))._build_prompt([...])
    assert "違和感" in prompt
    assert "30分浮くか" in prompt
    assert "説明文ではなく" in prompt
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run --extra dev pytest tests/test_writer_agent.py::test_writer_prompt_requires_threads_native_hook_and_personal_angle`
Expected: FAIL because the prompt does not contain the new style rules yet.

- [ ] **Step 3: Write minimal implementation**

Add concise style rules to `_build_prompt`: use a hook based on surprise, disagreement, failure, or personal realization; include concrete task examples; avoid generic words; use the 40s company worker and parent angle.

- [ ] **Step 4: Run all tests**

Run: `uv run --extra dev pytest`
Expected: all tests pass.
