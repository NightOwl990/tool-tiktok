import praw
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError

from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT, DEFAULT_SUBREDDITS
from db import get_session, TrendItem
from utils import age_hours, normalize_keyword

def reddit_client():
    if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
        raise RuntimeError("Missing Reddit credentials. Please fill .env first.")
    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )

def collect_subreddit(reddit, subreddit_name, limit=50):
    results = []
    sub = reddit.subreddit(subreddit_name)

    listings = [
        ("hot", sub.hot(limit=limit)),
        ("rising", sub.rising(limit=limit)),
        ("top_day", sub.top(time_filter="day", limit=limit)),
    ]

    for listing_name, posts in listings:
        for post in posts:
            if getattr(post, "stickied", False) or getattr(post, "over_18", False):
                continue

            created = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
            ah = age_hours(created)
            velocity = float(post.score) / max(ah, 1)
            comment_velocity = float(post.num_comments) / max(ah, 1)
            keyword = normalize_keyword(post.title)
            flair = getattr(post, "link_flair_text", "") or ""

            results.append({
                "platform": "reddit",
                "keyword": keyword,
                "title": post.title,
                "description": getattr(post, "selftext", "")[:1000],
                "source_url": f"https://reddit.com{post.permalink}",
                "subreddit": subreddit_name,
                "category": f"{listing_name}:{flair}" if flair else listing_name,
                "score_raw": int(post.score),
                "comments": int(post.num_comments),
                "upvote_ratio": float(getattr(post, "upvote_ratio", 0) or 0),
                "created_at_source": created,
                "age_hours": ah,
                "velocity": velocity + comment_velocity * 2,
            })
    return results

def save_items(items):
    session = get_session()
    inserted = 0
    updated = 0

    for item in items:
        existing = session.query(TrendItem).filter_by(
            platform=item["platform"],
            source_url=item["source_url"]
        ).first()

        if existing:
            existing.score_raw = item["score_raw"]
            existing.comments = item["comments"]
            existing.upvote_ratio = item["upvote_ratio"]
            existing.age_hours = item["age_hours"]
            existing.velocity = item["velocity"]
            updated += 1
        else:
            session.add(TrendItem(**item))
            inserted += 1

    session.commit()
    session.close()
    return inserted, updated

def main():
    reddit = reddit_client()
    all_items = []

    for sub in DEFAULT_SUBREDDITS:
        try:
            print(f"Collecting r/{sub}...")
            all_items.extend(collect_subreddit(reddit, sub, limit=50))
        except Exception as e:
            print(f"Failed r/{sub}: {e}")

    inserted, updated = save_items(all_items)
    print(f"Done. Inserted={inserted}, Updated={updated}, Total fetched={len(all_items)}")

if __name__ == "__main__":
    main()
