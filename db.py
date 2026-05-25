from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

from config import DATABASE_URL

Path("data").mkdir(exist_ok=True)

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


class TrendItem(Base):
    __tablename__ = "trend_items"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, index=True)  # reddit / tiktok
    keyword = Column(String, index=True)
    title = Column(Text, default="")
    description = Column(Text, default="")
    source_url = Column(Text, default="")
    region = Column(String, default="")
    category = Column(String, default="")
    subreddit = Column(String, default="")

    score_raw = Column(Float, default=0)
    comments = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    views = Column(Integer, default=0)
    upvote_ratio = Column(Float, default=0)

    age_hours = Column(Float, default=0)
    velocity = Column(Float, default=0)
    engagement_score = Column(Float, default=0)
    freshness_score = Column(Float, default=0)
    cross_platform_score = Column(Float, default=0)
    trend_score = Column(Float, default=0)

    # Creator Rewards / US market optimization scores.
    creator_rewards_score = Column(Float, default=0)
    us_relevance_score = Column(Float, default=0)
    search_value_score = Column(Float, default=0)
    retention_score = Column(Float, default=0)
    originality_score = Column(Float, default=0)
    risk_score = Column(Float, default=0)
    content_pillar = Column(String, default="")
    risk_level = Column(String, default="")
    production_notes = Column(Text, default="")
    topic_cluster = Column(String, default="")
    analytics_adjustment_score = Column(Float, default=0)
    performance_hint = Column(Text, default="")

    created_at_source = Column(DateTime, nullable=True)
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String, default="new")  # new / shortlist / scripted / posted / used / ignore

    __table_args__ = (
        UniqueConstraint("platform", "source_url", name="uq_platform_source"),
    )


class PostedVideo(Base):
    __tablename__ = "posted_videos"

    id = Column(Integer, primary_key=True, index=True)
    trend_item_id = Column(Integer, index=True, nullable=True)
    video_key = Column(String, unique=True, index=True)
    video_id = Column(String, default="", index=True)
    video_url = Column(Text, default="")
    keyword = Column(String, default="", index=True)
    content_pillar = Column(String, default="", index=True)
    title = Column(Text, default="")
    hook_used = Column(Text, default="")
    caption_used = Column(Text, default="")
    posted_at = Column(DateTime, nullable=True)

    duration_seconds = Column(Float, default=0)
    views = Column(Integer, default=0)
    qualified_views = Column(Integer, default=0)
    avg_watch_time_seconds = Column(Float, default=0)
    completion_rate = Column(Float, default=0)
    retention_rate = Column(Float, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    follows = Column(Integer, default=0)
    rpm = Column(Float, default=0)
    revenue = Column(Float, default=0)
    snapshot_age_hours = Column(Float, default=0)

    performance_score = Column(Float, default=0)
    outcome_label = Column(String, default="")
    source_file = Column(String, default="")
    notes = Column(Text, default="")
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


SQLITE_COLUMN_MIGRATIONS = {
    "creator_rewards_score": "FLOAT DEFAULT 0",
    "us_relevance_score": "FLOAT DEFAULT 0",
    "search_value_score": "FLOAT DEFAULT 0",
    "retention_score": "FLOAT DEFAULT 0",
    "originality_score": "FLOAT DEFAULT 0",
    "risk_score": "FLOAT DEFAULT 0",
    "content_pillar": "VARCHAR DEFAULT ''",
    "risk_level": "VARCHAR DEFAULT ''",
    "production_notes": "TEXT DEFAULT ''",
    "topic_cluster": "VARCHAR DEFAULT ''",
    "analytics_adjustment_score": "FLOAT DEFAULT 0",
    "performance_hint": "TEXT DEFAULT ''",
}


def _migrate_sqlite_schema():
    if engine.dialect.name != "sqlite":
        return

    with engine.begin() as conn:
        table_exists = conn.exec_driver_sql(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='trend_items'"
        ).first()
        if not table_exists:
            return

        existing_columns = {
            row[1] for row in conn.exec_driver_sql("PRAGMA table_info(trend_items)")
        }

        for column_name, column_ddl in SQLITE_COLUMN_MIGRATIONS.items():
            if column_name not in existing_columns:
                conn.exec_driver_sql(
                    f"ALTER TABLE trend_items ADD COLUMN {column_name} {column_ddl}"
                )


def init_db():
    Base.metadata.create_all(bind=engine)
    _migrate_sqlite_schema()


def get_session():
    init_db()
    return SessionLocal()
