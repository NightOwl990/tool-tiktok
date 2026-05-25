import re
from datetime import datetime, timezone

from dateutil.parser import parse as parse_dt

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "to", "of", "in", "on", "for", "with",
    "is", "are", "was", "were", "i", "you", "he", "she", "they", "we", "it",
    "this", "that", "what", "why", "how", "when", "where", "my", "your",
    "me", "from", "about", "just", "not", "have", "has", "had", "can", "could",
    "would", "should", "did", "does", "do", "been", "being", "after", "before",
    "into", "over", "under", "than", "then", "them", "their", "his", "her",
}

WEAK_MATCH_TOKENS = {
    "reddit", "tiktok", "story", "stories", "viral", "trend", "trends", "video",
    "part", "update", "updates", "best", "new", "old", "day", "days", "people",
}


def now_utc():
    return datetime.now(timezone.utc)


def safe_parse_datetime(value):
    if not value:
        return None
    try:
        dt = parse_dt(str(value))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def age_hours(dt):
    if not dt:
        return 999
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return max((now_utc() - dt).total_seconds() / 3600, 0.1)


def text_tokens(text, keep_weak=False):
    text = (text or "").lower()
    words = re.findall(r"[a-zA-Z0-9_]{3,}", text)
    tokens = [word for word in words if word not in STOPWORDS]
    if not keep_weak:
        tokens = [word for word in tokens if word not in WEAK_MATCH_TOKENS]
    return tokens


def extract_keywords(text, max_keywords=5):
    freq = {}
    for word in text_tokens(text, keep_weak=True):
        if word in WEAK_MATCH_TOKENS and len(freq) >= 2:
            continue
        freq[word] = freq.get(word, 0) + 1

    ranked = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in ranked[:max_keywords]]


def normalize_keyword(text):
    kws = extract_keywords(text, max_keywords=4)
    return " ".join(kws) if kws else (text or "")[:80]


def keyword_tokens(text):
    return set(text_tokens(text, keep_weak=False))


def keyword_similarity(left, right):
    left_tokens = keyword_tokens(left)
    right_tokens = keyword_tokens(right)

    if not left_tokens or not right_tokens:
        return 0

    overlap = left_tokens & right_tokens
    if not overlap:
        return 0

    union = left_tokens | right_tokens
    jaccard = len(overlap) / max(len(union), 1)
    containment = len(overlap) / max(min(len(left_tokens), len(right_tokens)), 1)

    score = max(jaccard * 100, containment * 75)

    strong_overlap = [token for token in overlap if len(token) >= 5]
    if len(overlap) >= 2:
        score += 15
    elif strong_overlap:
        score = min(max(score, 45), 55)
    else:
        score = min(score, 25)

    left_phrase_tokens = text_tokens(left, keep_weak=True)
    right_phrase_tokens = text_tokens(right, keep_weak=True)
    left_text = " ".join(left_phrase_tokens)
    right_text = " ".join(right_phrase_tokens)
    if (
        min(len(left_phrase_tokens), len(right_phrase_tokens)) >= 2
        and left_text
        and right_text
        and (left_text in right_text or right_text in left_text)
    ):
        score = max(score, 80)

    return round(max(0, min(100, score)), 2)
