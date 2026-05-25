import hashlib
import math
import re
from collections import defaultdict

from creator_rewards import infer_content_pillar
from db import PostedVideo
from utils import keyword_tokens


def clamp(value, min_value=0, max_value=100):
    return max(min_value, min(max_value, value))


def normalize_rate(value):
    value = float(value or 0)
    if value > 1:
        value = value / 100
    return clamp(value, 0, 1)


def make_video_key(video_id="", video_url="", keyword="", posted_at=None):
    raw = video_id or video_url or f"{keyword}|{posted_at or ''}"
    return hashlib.sha1(str(raw).strip().lower().encode("utf-8")).hexdigest()[:20]


def calculate_video_performance_score(video):
    views = float(video.views or 0)
    duration = float(video.duration_seconds or 0)
    avg_watch = float(video.avg_watch_time_seconds or 0)
    qualified_views = float(video.qualified_views or 0)
    rpm = float(video.rpm or 0)
    revenue = float(video.revenue or 0)

    completion = normalize_rate(video.completion_rate)
    retention = normalize_rate(video.retention_rate)
    watch_ratio = clamp(avg_watch / max(duration, 1), 0, 1) if avg_watch else 0
    qualified_rate = clamp(qualified_views / max(views, 1), 0, 1) if qualified_views else 0

    engagement_units = (
        float(video.likes or 0) +
        float(video.comments or 0) * 4 +
        float(video.shares or 0) * 6 +
        float(video.saves or 0) * 5 +
        float(video.follows or 0) * 8
    )
    engagement_rate = engagement_units / max(views, 1)

    views_score = clamp(math.log1p(views) * 6)
    watch_score = max(watch_ratio, retention, completion * 0.9) * 100
    qualified_score = qualified_rate * 100 if qualified_views else min(views_score, 65)
    engagement_score = clamp(engagement_rate * 850)
    rpm_score = clamp(rpm * 18) if rpm else 45
    revenue_score = clamp(math.log1p(revenue) * 18) if revenue else 35

    score = (
        watch_score * 0.30 +
        qualified_score * 0.18 +
        engagement_score * 0.18 +
        rpm_score * 0.20 +
        revenue_score * 0.07 +
        views_score * 0.07
    )
    return round(clamp(score), 2)


def outcome_label(score):
    if score >= 78:
        return "winner"
    if score >= 64:
        return "promising"
    if score >= 48:
        return "neutral"
    return "loser"


def topic_cluster_for(item_or_text, pillar=None):
    if isinstance(item_or_text, str):
        text = item_or_text
        cluster_pillar = pillar or "General"
    else:
        item = item_or_text
        text = " ".join(
            str(value or "")
            for value in [
                getattr(item, "keyword", ""),
                getattr(item, "title", ""),
                getattr(item, "description", ""),
                getattr(item, "category", ""),
                getattr(item, "subreddit", ""),
            ]
        )
        cluster_pillar = pillar or getattr(item, "content_pillar", "") or infer_content_pillar(item)

    tokens = sorted(keyword_tokens(text))
    short_tokens = {
        token
        for token in re.findall(r"\b[a-zA-Z0-9]{2}\b", text.lower())
        if token in {"ai", "vr", "ar", "us", "uk"}
    }
    tokens = sorted(set(tokens) | short_tokens)
    if not tokens:
        cleaned = re.sub(r"[^a-zA-Z0-9]+", " ", text.lower()).strip()
        tokens = cleaned.split()[:3]
    return f"{cluster_pillar}: {' '.join(tokens[:4])}".strip()


def pillar_performance_summary(session):
    videos = session.query(PostedVideo).all()
    grouped = defaultdict(list)

    for video in videos:
        pillar = video.content_pillar or "Unknown"
        if video.performance_score:
            grouped[pillar].append(video)

    summary = {}
    for pillar, pillar_videos in grouped.items():
        scores = [float(video.performance_score or 0) for video in pillar_videos]
        rpms = [float(video.rpm or 0) for video in pillar_videos if video.rpm]
        completion_rates = [
            normalize_rate(video.completion_rate)
            for video in pillar_videos
            if video.completion_rate
        ]
        avg_score = sum(scores) / len(scores)
        avg_rpm = sum(rpms) / len(rpms) if rpms else 0
        avg_completion = (
            sum(completion_rates) / len(completion_rates)
            if completion_rates
            else 0
        )
        confidence = min(len(scores) / 5, 1)
        adjustment = clamp((avg_score - 55) * 0.35 * confidence, -12, 12)

        summary[pillar] = {
            "count": len(scores),
            "avg_score": round(avg_score, 2),
            "avg_rpm": round(avg_rpm, 2),
            "avg_completion_rate": round(avg_completion * 100, 2),
            "adjustment": round(adjustment, 2),
        }

    return summary


def analytics_adjustment_for_item(item, pillar_summary):
    pillar = getattr(item, "content_pillar", "") or infer_content_pillar(item)
    summary = pillar_summary.get(pillar)
    if not summary:
        return 0, "No posted-video data for this pillar yet."

    adjustment = float(summary["adjustment"])
    direction = "boost" if adjustment > 0 else "penalty" if adjustment < 0 else "neutral"
    hint = (
        f"{pillar} has {summary['count']} posted videos, avg performance "
        f"{summary['avg_score']}, avg RPM {summary['avg_rpm']}. Analytics {direction}: {adjustment:+.1f}."
    )
    return adjustment, hint
