from pathlib import Path

import pandas as pd

from analytics import calculate_video_performance_score, make_video_key, outcome_label
from creator_rewards import infer_content_pillar
from db import PostedVideo, TrendItem, get_session
from utils import keyword_similarity, safe_parse_datetime

CSV_PATH = Path("data/tiktok_analytics.csv")


def as_int(value, default=0):
    try:
        if pd.isna(value):
            return default
        return int(float(value))
    except Exception:
        return default


def as_float(value, default=0):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def clean(value):
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def find_trend(session, row):
    trend_item_id = as_int(row.get("trend_item_id", 0))
    if trend_item_id:
        trend = session.query(TrendItem).filter_by(id=trend_item_id).first()
        if trend:
            return trend

    keyword = clean(row.get("keyword", ""))
    title = clean(row.get("title", ""))
    search_text = " ".join([keyword, title]).strip()
    if not search_text:
        return None

    best_trend = None
    best_score = 0
    for trend in session.query(TrendItem).all():
        trend_text = " ".join([trend.keyword or "", trend.title or ""])
        score = keyword_similarity(search_text, trend_text)
        if score > best_score:
            best_score = score
            best_trend = trend

    return best_trend if best_score >= 55 else None


def main():
    if not CSV_PATH.exists():
        print(f"Missing {CSV_PATH}. Create it first.")
        print(
            "Columns: video_id,video_url,trend_item_id,keyword,content_pillar,title,"
            "hook_used,caption_used,posted_at,duration_seconds,views,qualified_views,"
            "avg_watch_time_seconds,completion_rate,retention_rate,likes,comments,"
            "shares,saves,follows,rpm,revenue,snapshot_age_hours,notes"
        )
        return

    df = pd.read_csv(CSV_PATH)
    session = get_session()

    inserted = 0
    updated = 0
    linked = 0

    for _, row in df.iterrows():
        video_id = clean(row.get("video_id", ""))
        video_url = clean(row.get("video_url", ""))
        keyword = clean(row.get("keyword", ""))
        title = clean(row.get("title", ""))
        posted_at = safe_parse_datetime(row.get("posted_at", None))

        if not any([video_id, video_url, keyword, title]):
            continue

        trend = find_trend(session, row)
        content_pillar = clean(row.get("content_pillar", ""))
        if not content_pillar and trend:
            content_pillar = trend.content_pillar or infer_content_pillar(trend)

        video_key = make_video_key(
            video_id=video_id,
            video_url=video_url,
            keyword=keyword or title,
            posted_at=posted_at,
        )
        video = session.query(PostedVideo).filter_by(video_key=video_key).first()
        if not video:
            video = PostedVideo(video_key=video_key)
            session.add(video)
            inserted += 1
        else:
            updated += 1

        video.trend_item_id = trend.id if trend else None
        video.video_id = video_id
        video.video_url = video_url
        video.keyword = keyword or (trend.keyword if trend else title)
        video.content_pillar = content_pillar or "Unknown"
        video.title = title
        video.hook_used = clean(row.get("hook_used", ""))
        video.caption_used = clean(row.get("caption_used", ""))
        video.posted_at = posted_at
        video.duration_seconds = as_float(row.get("duration_seconds", 0))
        video.views = as_int(row.get("views", 0))
        video.qualified_views = as_int(row.get("qualified_views", 0))
        video.avg_watch_time_seconds = as_float(row.get("avg_watch_time_seconds", 0))
        video.completion_rate = as_float(row.get("completion_rate", 0))
        video.retention_rate = as_float(row.get("retention_rate", 0))
        video.likes = as_int(row.get("likes", 0))
        video.comments = as_int(row.get("comments", 0))
        video.shares = as_int(row.get("shares", 0))
        video.saves = as_int(row.get("saves", 0))
        video.follows = as_int(row.get("follows", 0))
        video.rpm = as_float(row.get("rpm", 0))
        video.revenue = as_float(row.get("revenue", 0))
        video.snapshot_age_hours = as_float(row.get("snapshot_age_hours", 0))
        video.notes = clean(row.get("notes", ""))
        video.source_file = str(CSV_PATH)
        video.performance_score = calculate_video_performance_score(video)
        video.outcome_label = outcome_label(video.performance_score)

        if trend:
            trend.status = "posted"
            linked += 1

    session.commit()
    session.close()
    print(f"TikTok analytics import done. Inserted={inserted}, Updated={updated}, Linked={linked}")


if __name__ == "__main__":
    main()
