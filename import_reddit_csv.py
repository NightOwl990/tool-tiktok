from pathlib import Path
import pandas as pd
from db import get_session, TrendItem
from utils import safe_parse_datetime, age_hours, normalize_keyword

CSV_PATH = Path("data/reddit_trends.csv")

def as_int(value, default=0):
    try:
        if pd.isna(value):
            return default
        return int(float(value))
    except Exception:
        return default

def main():
    if not CSV_PATH.exists():
        print(f"Missing {CSV_PATH}. Create it first.")
        print("Columns: subreddit,title,url,score,comments,created_at")
        return

    df = pd.read_csv(CSV_PATH)
    session = get_session()

    inserted = 0
    updated = 0

    for _, row in df.iterrows():
        subreddit = str(row.get("subreddit", "") or "").strip()
        title = str(row.get("title", "") or "").strip()
        source_url = str(row.get("url", "") or "").strip()

        if not title:
            continue

        keyword = normalize_keyword(title)
        created_dt = safe_parse_datetime(row.get("created_at", None))
        ah = age_hours(created_dt)

        score_raw = as_int(row.get("score", 0))
        comments = as_int(row.get("comments", 0))

        velocity = (score_raw + comments * 2) / max(ah, 1)

        existing = session.query(TrendItem).filter_by(
            platform="reddit",
            source_url=source_url or title
        ).first()

        data = {
            "platform": "reddit",
            "keyword": keyword,
            "title": title,
            "description": "",
            "source_url": source_url or title,
            "subreddit": subreddit,
            "category": "manual_csv",
            "score_raw": score_raw,
            "comments": comments,
            "upvote_ratio": 1.0,
            "created_at_source": created_dt,
            "age_hours": ah,
            "velocity": velocity,
        }

        if existing:
            for k, v in data.items():
                setattr(existing, k, v)
            updated += 1
        else:
            session.add(TrendItem(**data))
            inserted += 1

    session.commit()
    session.close()
    print(f"Reddit CSV import done. Inserted={inserted}, Updated={updated}")

if __name__ == "__main__":
    main()