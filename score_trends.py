import math
from collections import defaultdict

from analytics import (
    analytics_adjustment_for_item,
    pillar_performance_summary,
    topic_cluster_for,
)
from creator_rewards import calculate_creator_rewards_metrics
from db import TrendItem, get_session
from utils import keyword_similarity


def clamp(v, min_v=0, max_v=100):
    return max(min_v, min(max_v, v))


def log_score(value, multiplier=20):
    return clamp(math.log1p(max(value, 0)) * multiplier)


def freshness_score(age_hours):
    # Strong recency still matters, but US Creator Rewards also needs evergreen value.
    if age_hours <= 3:
        return 100
    if age_hours <= 12:
        return 85
    if age_hours <= 24:
        return 70
    if age_hours <= 72:
        return 45
    if age_hours <= 168:
        return 25
    return 10


def match_text(item):
    return " ".join(
        str(value or "")
        for value in [item.keyword, item.title, item.description, item.category, item.subreddit]
    )


def best_cross_platform_score(item, other_platform_items):
    own_text = match_text(item)
    best = 0

    for other in other_platform_items:
        score = keyword_similarity(own_text, match_text(other))
        if score > best:
            best = score
        if best >= 100:
            break

    return best


def main():
    session = get_session()
    items = session.query(TrendItem).all()
    pillar_summary = pillar_performance_summary(session)

    by_platform = defaultdict(list)
    for item in items:
        by_platform[item.platform].append(item)

    for item in items:
        velocity_score = log_score(item.velocity, multiplier=22)

        if item.platform == "reddit":
            engagement_score = log_score(
                item.comments * 2 + item.score_raw * item.upvote_ratio,
                multiplier=12,
            )
            opposite_items = by_platform["tiktok"]
        else:
            engagement_score = log_score(
                item.likes * 0.05 + item.comments * 0.5 + item.shares * 0.8,
                multiplier=14,
            )
            opposite_items = by_platform["reddit"]

        fresh = freshness_score(item.age_hours or 999)
        cross = best_cross_platform_score(item, opposite_items)

        metrics = calculate_creator_rewards_metrics(
            item=item,
            velocity_score=velocity_score,
            engagement_score=engagement_score,
            freshness_score=fresh,
            cross_platform_score=cross,
        )
        analytics_adjustment, performance_hint = analytics_adjustment_for_item(
            item,
            pillar_summary,
        )
        final_score = clamp(metrics["creator_rewards_score"] + analytics_adjustment)

        item.engagement_score = engagement_score
        item.freshness_score = fresh
        item.cross_platform_score = cross
        item.creator_rewards_score = round(final_score, 2)
        item.us_relevance_score = metrics["us_relevance_score"]
        item.search_value_score = metrics["search_value_score"]
        item.retention_score = metrics["retention_score"]
        item.originality_score = metrics["originality_score"]
        item.risk_score = metrics["risk_score"]
        item.risk_level = metrics["risk_level"]
        item.content_pillar = metrics["content_pillar"]
        item.topic_cluster = topic_cluster_for(item, metrics["content_pillar"])
        item.analytics_adjustment_score = analytics_adjustment
        item.performance_hint = performance_hint
        item.production_notes = metrics["production_notes"]

        # Keep the old public column as the main ranking score for existing views.
        item.trend_score = item.creator_rewards_score

    session.commit()
    session.close()
    print(f"Scored {len(items)} trend items for US Creator Rewards.")


if __name__ == "__main__":
    main()
