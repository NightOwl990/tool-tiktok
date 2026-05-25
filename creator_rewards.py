from utils import keyword_tokens


US_SUBREDDIT_WEIGHTS = {
    "aitah": 24,
    "amitheasshole": 24,
    "relationship_advice": 22,
    "trueoffmychest": 20,
    "confession": 18,
    "askreddit": 16,
    "antiwork": 24,
    "jobs": 22,
    "careerguidance": 22,
    "workreform": 18,
    "personalfinance": 20,
    "povertyfinance": 18,
    "frugal": 14,
    "sidehustle": 16,
    "outoftheloop": 18,
    "popculturechat": 16,
    "chatgpt": 20,
    "artificialinteligence": 18,
    "technology": 18,
    "nosleep": 15,
    "letsnotmeet": 15,
    "shortscarystories": 12,
}

US_CONTEXT_TERMS = (
    "rent", "mortgage", "landlord", "roommate", "neighbor", "hoa", "college",
    "student loan", "salary", "boss", "workplace", "job", "laid off", "fired",
    "wedding", "divorce", "wife", "husband", "girlfriend", "boyfriend",
    "dating", "insurance", "tax", "credit score", "401k", "target", "walmart",
    "costco", "amazon", "doordash", "uber", "starbucks", "iphone", "chatgpt",
)

SEARCH_VALUE_TERMS = (
    "how to", "why", "what happened", "explained", "meaning", "cost", "salary",
    "best", "review", "template", "checklist", "mistake", "warning", "is it worth",
    "side hustle", "ai tool", "chatgpt", "credit score", "rent", "tax", "resume",
)

RETENTION_TERMS = (
    "wrong", "secret", "hid", "refused", "caught", "scam", "betrayed", "fired",
    "begged", "quit", "wedding", "divorce", "roommate", "neighbor", "boss",
    "creepy", "heard", "confession", "update", "twist", "aita", "aitah",
    "revenge", "drama", "argument", "exposed", "lied", "missing",
)

LOW_ORIGINALITY_TERMS = (
    "reddit story", "redditstories", "askreddit", "aita story", "viral video",
    "compilation", "reaction clip", "tiktok compilation", "part 2", "full clip",
)

HIGH_RISK_TERMS = (
    "suicide", "self harm", "self-harm", "rape", "sexual assault", "minor",
    "underage", "child abuse", "murder", "kill", "weapon", "gun", "blood",
    "explicit", "nude", "nsfw", "drug", "cocaine",
)

POLICY_RISK_TERMS = (
    "medical advice", "legal advice", "financial advice", "guaranteed income",
    "get rich quick", "pirated", "leaked", "copyright", "full movie", "episode",
    "streaming clip",
)


def clamp(value, min_value=0, max_value=100):
    return max(min_value, min(max_value, value))


def item_text(item):
    return " ".join(
        str(value or "")
        for value in [
            getattr(item, "keyword", ""),
            getattr(item, "title", ""),
            getattr(item, "description", ""),
            getattr(item, "category", ""),
            getattr(item, "subreddit", ""),
        ]
    ).lower()


def phrase_matches(text, phrases):
    return [phrase for phrase in phrases if phrase in text]


def infer_content_pillar(item):
    text = item_text(item)
    subreddit = (getattr(item, "subreddit", "") or "").lower()

    if any(term in text for term in ["chatgpt", "ai ", "ai tool", "tool", "app", "tech"]):
        return "AI tools"
    if subreddit in {"antiwork", "jobs", "careerguidance", "workreform"}:
        return "Workplace"
    if any(term in text for term in ["boss", "salary", "job", "career", "fired", "workplace"]):
        return "Workplace"
    if subreddit in {"personalfinance", "povertyfinance", "frugal", "sidehustle"}:
        return "Money"
    if any(term in text for term in ["money", "rent", "debt", "credit", "tax", "side hustle"]):
        return "Money"
    if subreddit in {"aitah", "amitheasshole", "relationship_advice"}:
        return "Relationship drama"
    if any(term in text for term in ["girlfriend", "boyfriend", "wife", "husband", "dating", "wedding"]):
        return "Relationship drama"
    if subreddit in {"nosleep", "letsnotmeet", "shortscarystories"}:
        return "Horror story"
    if any(term in text for term in ["scary", "horror", "creepy", "basement"]):
        return "Horror story"
    if any(term in text for term in ["celebrity", "movie", "show", "pop culture"]):
        return "Pop culture"
    return "Story explainer"


def score_us_relevance(item):
    text = item_text(item)
    score = 38
    platform = (getattr(item, "platform", "") or "").lower()
    region = (getattr(item, "region", "") or "").strip().upper()
    subreddit = (getattr(item, "subreddit", "") or "").lower()

    if platform == "tiktok":
        if region in {"US", "USA", "UNITED STATES"}:
            score += 36
        elif not region:
            score += 12
        else:
            score -= 12

    if platform == "reddit":
        score += US_SUBREDDIT_WEIGHTS.get(subreddit, 10)

    score += min(len(phrase_matches(text, US_CONTEXT_TERMS)) * 7, 26)

    if keyword_tokens(text):
        score += 6

    return round(clamp(score), 2)


def score_search_value(item):
    text = item_text(item)
    title = (getattr(item, "title", "") or "").strip()
    pillar = infer_content_pillar(item)
    tokens = keyword_tokens(text)

    score = 28
    score += min(len(phrase_matches(text, SEARCH_VALUE_TERMS)) * 9, 36)

    if "?" in title:
        score += 10
    if title.lower().startswith(("how ", "why ", "what ", "am i ", "is it ")):
        score += 8

    if pillar in {"AI tools", "Money", "Workplace"}:
        score += 16
    elif pillar in {"Relationship drama", "Story explainer"}:
        score += 8

    token_count = len(tokens)
    if 3 <= token_count <= 10:
        score += 8
    elif token_count <= 1:
        score -= 16

    return round(clamp(score), 2)


def score_retention_potential(item):
    text = item_text(item)
    title = (getattr(item, "title", "") or "").strip()
    pillar = infer_content_pillar(item)
    platform = (getattr(item, "platform", "") or "").lower()

    score = 34
    score += min(len(phrase_matches(text, RETENTION_TERMS)) * 8, 40)

    if 45 <= len(title) <= 140:
        score += 12
    elif len(title) < 20:
        score -= 12

    if platform == "reddit":
        comments = float(getattr(item, "comments", 0) or 0)
        score_raw = float(getattr(item, "score_raw", 0) or 0)
        comment_ratio = comments / max(score_raw, 1)
        score += min(comment_ratio * 70, 18)
        if comments >= 1000:
            score += 10
    else:
        views = float(getattr(item, "views", 0) or 0)
        weighted_engagement = (
            float(getattr(item, "likes", 0) or 0) +
            float(getattr(item, "comments", 0) or 0) * 3 +
            float(getattr(item, "shares", 0) or 0) * 4
        )
        engagement_rate = weighted_engagement / max(views, 1)
        score += min(engagement_rate * 230, 22)

    if pillar in {"Relationship drama", "Workplace", "Horror story"}:
        score += 10

    if len(keyword_tokens(text)) <= 1:
        score -= 12

    return round(clamp(score), 2)


def score_originality(item):
    text = item_text(item)
    title = (getattr(item, "title", "") or "").strip()
    platform = (getattr(item, "platform", "") or "").lower()
    source_url = (getattr(item, "source_url", "") or "").lower()
    pillar = infer_content_pillar(item)

    score = 82

    if platform == "reddit":
        score -= 6
        if len(title) >= 45:
            score += 10
    elif platform == "tiktok":
        if "/tag/" in source_url:
            score -= 14
        if len(keyword_tokens(title)) <= 2:
            score -= 8
        if getattr(item, "description", ""):
            score += 7

    score -= min(len(phrase_matches(text, LOW_ORIGINALITY_TERMS)) * 9, 28)

    if pillar in {"AI tools", "Money", "Workplace"}:
        score += 5
    if "compilation" in text or "repost" in text:
        score -= 20

    return round(clamp(score), 2)


def score_monetization_risk(item):
    text = item_text(item)
    subreddit = (getattr(item, "subreddit", "") or "").lower()
    pillar = infer_content_pillar(item)

    risk = 10
    risk += min(len(phrase_matches(text, HIGH_RISK_TERMS)) * 13, 55)
    risk += min(len(phrase_matches(text, POLICY_RISK_TERMS)) * 11, 32)

    if pillar == "Money":
        risk += 6
    if pillar == "Pop culture":
        risk += 10
    if subreddit in {"nosleep", "letsnotmeet", "shortscarystories"}:
        risk = max(0, risk - 10)

    if "nsfw" in text or "over 18" in text:
        risk += 30

    return round(clamp(risk), 2)


def risk_level(risk_score):
    if risk_score >= 65:
        return "High"
    if risk_score >= 35:
        return "Medium"
    return "Low"


def production_notes_for(item, metrics):
    notes = []
    pillar = metrics["content_pillar"]

    if metrics["risk_score"] >= 65:
        notes.append("Skip or rewrite heavily; monetization risk is high.")
    elif metrics["risk_score"] >= 35:
        notes.append("Keep claims conservative and avoid graphic or policy-sensitive details.")

    if metrics["originality_score"] < 70:
        notes.append("Add original commentary, structure, examples, and custom visuals.")
    else:
        notes.append("Rewrite from your own POV; do not read source text verbatim.")

    if metrics["retention_score"] >= 75:
        notes.append("Use a delayed reveal and one new beat every 6-8 seconds.")
    else:
        notes.append("Strengthen the conflict, stakes, or practical payoff before production.")

    if metrics["search_value_score"] >= 70:
        notes.append("Use a searchable on-screen title and repeat the core keyword early.")

    if pillar == "Money":
        notes.append("Frame as education or personal experience, not financial advice.")
    elif pillar == "AI tools":
        notes.append("Show the output/result first, then explain the workflow.")
    elif pillar == "Relationship drama":
        notes.append("End with a clear viewer question to drive comments.")

    return " ".join(notes)


def calculate_creator_rewards_metrics(
    item,
    velocity_score,
    engagement_score,
    freshness_score,
    cross_platform_score,
):
    us_relevance = score_us_relevance(item)
    search_value = score_search_value(item)
    retention = score_retention_potential(item)
    originality = score_originality(item)
    risk = score_monetization_risk(item)

    score = (
        us_relevance * 0.16 +
        search_value * 0.18 +
        retention * 0.25 +
        originality * 0.19 +
        engagement_score * 0.10 +
        freshness_score * 0.05 +
        cross_platform_score * 0.05 +
        velocity_score * 0.02 -
        risk * 0.18
    )

    metrics = {
        "creator_rewards_score": round(clamp(score), 2),
        "us_relevance_score": us_relevance,
        "search_value_score": search_value,
        "retention_score": retention,
        "originality_score": originality,
        "risk_score": risk,
        "risk_level": risk_level(risk),
        "content_pillar": infer_content_pillar(item),
    }
    metrics["production_notes"] = production_notes_for(item, metrics)
    return metrics
