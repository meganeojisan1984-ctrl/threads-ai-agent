from threads_ai_agent.safety import SafetyAgent


def test_safety_blocks_guaranteed_income_claims():
    result = SafetyAgent().check_text("AI副業なら誰でも必ず月100万円を稼げます")

    assert result.allowed is False
    assert "guaranteed_income" in result.reasons


def test_safety_requires_pr_disclosure_for_affiliate_intent():
    result = SafetyAgent().check_text("ConoHa WINGに申し込みましょう", affiliate_intent=True)

    assert result.allowed is False
    assert "missing_pr_disclosure" in result.reasons


def test_safety_allows_cautious_blog_cta():
    result = SafetyAgent().check_text("AI副業の始め方をブログにまとめました。まずは無料で試せる範囲からどうぞ。")

    assert result.allowed is True
    assert result.reasons == []


def test_reply_classification_blocks_tax_advice():
    decision = SafetyAgent().classify_reply("副業の税金は申告しなくてもバレませんか？")

    assert decision.category == "risky"
    assert decision.auto_reply_allowed is False
