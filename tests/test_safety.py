from threads_ai_agent.safety import SafetyAgent


def test_safety_blocks_generic_threads_growth_phrases():
    result = SafetyAgent().check_text("AI副業の効率アップや新サービス開発のチャンスが広がる。使いこなすことが鍵です。")

    assert result.allowed is False
    assert "promotional_template" in result.reasons


def test_safety_blocks_blog_listing_style_cta():
    result = SafetyAgent().check_text("詳しい活用手順はプロフィールのブログに掲載しています。")

    assert result.allowed is False
    assert "promotional_template" in result.reasons


def test_safety_blocks_overhyped_threads_phrases():
    result = SafetyAgent().check_text(
        "実はここに落とし穴があった。AI副業初心者にはおすすめしたい。爆速で差がつくので、確認いただければ幸いです。"
    )

    assert result.allowed is False
    assert "promotional_template" in result.reasons


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


def test_safety_blocks_sensitive_medical_ai_posts():
    result = SafetyAgent().check_text("医療AIのAMIEを使った副業アイデアを紹介します。慢性疾患の管理にも役立ちます。")

    assert result.allowed is False
    assert "sensitive_topic" in result.reasons


def test_safety_blocks_article_intro_templates():
    result = SafetyAgent().check_text("Geminiの使い方を解説しています。興味がある方はぜひチェックしてください。")

    assert result.allowed is False
    assert "promotional_template" in result.reasons
