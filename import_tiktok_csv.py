from pathlib import Path
import pandas as pd

from db import get_session, TrendItem
from utils import safe_parse_datetime, age_hours, normalize_keyword

CSV_PATH = Path("data/tiktok_trends.csv")

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
        print("Columns: keyword,source_url,region,category,views,likes,comments,shares,created_at")
        return

    df = pd.read_csv(CSV_PATH)
    session = get_session()

    inserted = 0
    updated = 0

    for _, row in df.iterrows():
        keyword = str(row.get("keyword", "") or "").strip()
        title = keyword
        source_url = str(row.get("source_url", "") or "").strip()

        if not keyword:
            keyword = normalize_keyword(title or source_url)

        created_dt = safe_parse_datetime(row.get("created_at", None))
        ah = age_hours(created_dt)

        views = as_int(row.get("views", 0))
        likes = as_int(row.get("likes", 0))
        comments = as_int(row.get("comments", 0))
        shares = as_int(row.get("shares", 0))

        velocity = (views * 0.001 + likes * 0.02 + comments * 0.08 + shares * 0.1) / max(ah, 1)

        existing = session.query(TrendItem).filter_by(
            platform="tiktok",
            source_url=source_url or keyword
        ).first()

        data = {
            "platform": "tiktok",
            "keyword": keyword,
            "title": title,
            "description": str(row.get("description", "") or ""),
            "source_url": source_url or keyword,
            "region": str(row.get("region", "") or ""),
            "category": str(row.get("category", "") or ""),
            "views": views,
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "created_at_source": created_dt,
            "age_hours": ah,
            "velocity": velocity,
            "score_raw": views,
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
    print(f"TikTok import done. Inserted={inserted}, Updated={updated}")

if __name__ == "__main__":
    main()
