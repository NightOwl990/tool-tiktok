import pandas as pd
import streamlit as st

from bootstrap import ensure_seed_data
from analytics import pillar_performance_summary
from db import PostedVideo, TrendItem, get_session
from idea_generator import generate_idea


STATUSES = ["new", "shortlist", "scripted", "posted", "used", "ignore"]
RISK_LEVELS = ["Low", "Medium", "High"]

LANGUAGE_OPTIONS = {
    "vi": "Tiếng Việt",
    "en": "English",
}

TEXT = {
    "en": {
        "app_title": "US Creator Rewards Trend Tool",
        "app_caption": "Trend ranking, risk checks, posted-video analytics, and 60-90s production briefs.",
        "filters": "Filters",
        "platform": "Platform",
        "status": "Status",
        "pillar": "Content pillar",
        "risk_level": "Risk level",
        "min_score": "Min Creator Rewards score",
        "max_risk": "Max risk score",
        "search_box": "Search keyword/title",
        "no_data": "No trend data yet. Run an importer first.",
        "total_trends": "Total trends",
        "filtered": "Filtered",
        "tiktok_total": "TikTok total",
        "tiktok_visible": "TikTok visible",
        "posted_videos": "Posted videos",
        "creator_ready": "Creator-ready",
        "shortlist_metric": "Shortlist",
        "tab_trends": "Trend Ranking",
        "tab_analytics": "Posted Analytics",
        "ranked_trends": "Ranked Trends",
        "empty_filter": "No trends match the current filters. Lower the score filter or allow Medium risk.",
        "hidden_tiktok": "TikTok trends exist in the database, but they are hidden by the current filters. Check Platform, Status, Score, or Risk filters.",
        "select_trend": "Select trend",
        "production_brief": "Production Brief",
        "score": "Score",
        "risk": "Risk",
        "retention": "Retention",
        "search": "Search",
        "title": "Title",
        "shortlist": "Shortlist",
        "scripted": "Scripted",
        "posted": "Posted",
        "used": "Used",
        "ignore": "Ignore",
        "tab_brief": "Brief",
        "tab_script": "Script",
        "tab_production": "Production",
        "tab_scoring": "Scoring",
        "hook": "Hook",
        "hook_variants": "A/B hook variants",
        "title_options": "Title options",
        "format": "Format",
        "script_angle": "Script angle",
        "caption": "Caption",
        "hashtags": "Hashtags",
        "beat_sheet": "Beat sheet",
        "structure": "60-90s structure",
        "voiceover_draft": "Voiceover draft",
        "voiceover": "Voiceover",
        "onscreen_text": "On-screen text",
        "text_overlays": "Text overlays",
        "broll_plan": "B-roll plan",
        "safety_originality": "Safety and originality",
        "production_notes": "Production notes",
        "run_score_note": "Run score_trends.py to generate notes.",
        "us_relevance": "US relevance",
        "originality": "Originality",
        "engagement": "Engagement",
        "cross_platform": "Cross-platform",
        "analytics_adjustment": "Analytics adjustment",
        "topic_cluster": "Topic cluster",
        "performance_hint": "Performance hint",
        "pillar_summary": "Pillar performance summary",
        "posted_video_table": "Posted video performance",
        "no_analytics": "No posted-video analytics yet. Fill data/tiktok_analytics.csv, run import_tiktok_analytics_csv.py, then run score_trends.py.",
    },
    "vi": {
        "app_title": "Công cụ tìm trend TikTok US",
        "app_caption": "Xếp hạng trend, kiểm tra rủi ro, học từ video đã đăng và tạo brief video 60-90 giây.",
        "filters": "Bộ lọc",
        "platform": "Nền tảng",
        "status": "Trạng thái",
        "pillar": "Nhóm nội dung",
        "risk_level": "Mức rủi ro",
        "min_score": "Điểm Creator Rewards tối thiểu",
        "max_risk": "Điểm rủi ro tối đa",
        "search_box": "Tìm keyword/title",
        "no_data": "Chưa có dữ liệu trend. Hãy chạy importer trước.",
        "total_trends": "Tổng trend",
        "filtered": "Đang lọc",
        "tiktok_total": "Tổng TikTok",
        "tiktok_visible": "TikTok đang hiện",
        "posted_videos": "Video đã đăng",
        "creator_ready": "Sẵn sàng làm video",
        "shortlist_metric": "Đã shortlist",
        "tab_trends": "Xếp hạng trend",
        "tab_analytics": "Analytics đã đăng",
        "ranked_trends": "Bảng xếp hạng trend",
        "empty_filter": "Không có trend nào khớp bộ lọc. Hãy giảm điểm tối thiểu hoặc cho phép rủi ro Medium.",
        "hidden_tiktok": "Có trend TikTok trong database, nhưng đang bị ẩn bởi bộ lọc hiện tại. Kiểm tra Platform, Trạng thái, Điểm hoặc Rủi ro.",
        "select_trend": "Chọn trend",
        "production_brief": "Brief sản xuất",
        "score": "Điểm",
        "risk": "Rủi ro",
        "retention": "Giữ chân",
        "search": "Search",
        "title": "Tiêu đề",
        "shortlist": "Shortlist",
        "scripted": "Đã viết script",
        "posted": "Đã đăng",
        "used": "Đã dùng",
        "ignore": "Bỏ qua",
        "tab_brief": "Brief",
        "tab_script": "Script",
        "tab_production": "Sản xuất",
        "tab_scoring": "Chấm điểm",
        "hook": "Hook",
        "hook_variants": "Hook A/B",
        "title_options": "Gợi ý tiêu đề",
        "format": "Format",
        "script_angle": "Góc triển khai",
        "caption": "Caption",
        "hashtags": "Hashtag",
        "beat_sheet": "Khung video",
        "structure": "Cấu trúc 60-90 giây",
        "voiceover_draft": "Bản nháp voiceover",
        "voiceover": "Voiceover",
        "onscreen_text": "Chữ trên màn hình",
        "text_overlays": "Text overlay",
        "broll_plan": "Kế hoạch B-roll",
        "safety_originality": "An toàn và độ original",
        "production_notes": "Ghi chú sản xuất",
        "run_score_note": "Chạy score_trends.py để tạo ghi chú.",
        "us_relevance": "Độ hợp thị trường US",
        "originality": "Độ original",
        "engagement": "Tương tác",
        "cross_platform": "Đa nền tảng",
        "analytics_adjustment": "Điểm chỉnh từ analytics",
        "topic_cluster": "Cụm chủ đề",
        "performance_hint": "Gợi ý từ dữ liệu đã đăng",
        "pillar_summary": "Hiệu suất theo nhóm nội dung",
        "posted_video_table": "Hiệu suất video đã đăng",
        "no_analytics": "Chưa có analytics video đã đăng. Điền data/tiktok_analytics.csv, chạy import_tiktok_analytics_csv.py, rồi chạy score_trends.py.",
    },
}

STATUS_LABELS = {
    "en": {
        "new": "New",
        "shortlist": "Shortlist",
        "scripted": "Scripted",
        "posted": "Posted",
        "used": "Used",
        "ignore": "Ignore",
    },
    "vi": {
        "new": "Mới",
        "shortlist": "Shortlist",
        "scripted": "Đã viết script",
        "posted": "Đã đăng",
        "used": "Đã dùng",
        "ignore": "Bỏ qua",
    },
}

RISK_LABELS = {
    "en": {"Low": "Low", "Medium": "Medium", "High": "High"},
    "vi": {"Low": "Thấp", "Medium": "Trung bình", "High": "Cao"},
}

PILLAR_LABELS = {
    "en": {},
    "vi": {
        "AI tools": "Công cụ AI",
        "Workplace": "Công việc",
        "Money": "Tiền bạc",
        "Relationship drama": "Drama quan hệ",
        "Horror story": "Chuyện kinh dị",
        "Pop culture": "Pop culture",
        "Story explainer": "Kể chuyện/giải thích",
    },
}

COLUMN_LABELS = {
    "en": {
        "score": "Score",
        "risk_level": "Risk level",
        "risk": "Risk",
        "pillar": "Pillar",
        "platform": "Platform",
        "keyword": "Keyword",
        "title": "Title",
        "us": "US",
        "search": "Search",
        "retention": "Retention",
        "originality": "Originality",
        "analytics_adj": "Analytics adj",
        "cluster": "Cluster",
        "engagement": "Engagement",
        "freshness": "Freshness",
        "cross": "Cross",
        "comments": "Comments",
        "views": "Views",
        "status": "Status",
        "url": "URL",
    },
    "vi": {
        "score": "Điểm",
        "risk_level": "Mức rủi ro",
        "risk": "Rủi ro",
        "pillar": "Nhóm nội dung",
        "platform": "Nền tảng",
        "keyword": "Keyword",
        "title": "Tiêu đề",
        "us": "US",
        "search": "Search",
        "retention": "Giữ chân",
        "originality": "Original",
        "analytics_adj": "Analytics chỉnh",
        "cluster": "Cụm",
        "engagement": "Tương tác",
        "freshness": "Độ mới",
        "cross": "Đa nền tảng",
        "comments": "Bình luận",
        "views": "Views",
        "status": "Trạng thái",
        "url": "URL",
    },
}


st.set_page_config(page_title="US Creator Rewards Trend Tool", layout="wide")

with st.sidebar:
    selected_language = st.selectbox(
        "Language / Ngôn ngữ",
        list(LANGUAGE_OPTIONS.keys()),
        format_func=lambda value: LANGUAGE_OPTIONS[value],
        index=0,
    )

language = selected_language


def t(key):
    return TEXT[language][key]


def status_label(status):
    return STATUS_LABELS[language].get(status, status)


def risk_label(risk):
    return RISK_LABELS[language].get(risk, risk)


def pillar_label(pillar):
    return PILLAR_LABELS[language].get(pillar, pillar)


def item_score(item):
    return float(item.creator_rewards_score or item.trend_score or 0)


def load_trend_dataframe(session):
    items = session.query(TrendItem).order_by(TrendItem.creator_rewards_score.desc()).all()
    rows = []

    for item in items:
        idea = generate_idea(item)
        rows.append({
            "id": item.id,
            "score": round(item_score(item), 2),
            "platform": item.platform,
            "keyword": item.keyword,
            "title": item.title,
            "pillar": item.content_pillar or idea["content_pillar"],
            "risk_level": item.risk_level or "Low",
            "risk": round(item.risk_score or 0, 2),
            "us": round(item.us_relevance_score or 0, 2),
            "search": round(item.search_value_score or 0, 2),
            "retention": round(item.retention_score or 0, 2),
            "originality": round(item.originality_score or 0, 2),
            "analytics_adj": round(item.analytics_adjustment_score or 0, 2),
            "cluster": item.topic_cluster or "",
            "performance_hint": item.performance_hint or "",
            "engagement": round(item.engagement_score or 0, 2),
            "freshness": round(item.freshness_score or 0, 2),
            "cross": round(item.cross_platform_score or 0, 2),
            "velocity": round(item.velocity or 0, 2),
            "views": item.views,
            "likes": item.likes,
            "comments": item.comments,
            "shares": item.shares,
            "subreddit": item.subreddit,
            "category": item.category,
            "region": item.region,
            "status": item.status or "new",
            "format": idea["format"],
            "hook": idea["hook"],
            "caption": idea["caption"],
            "url": item.source_url,
            "notes": item.production_notes or "",
        })

    return pd.DataFrame(rows)


def load_posted_videos_dataframe(session):
    videos = session.query(PostedVideo).order_by(PostedVideo.performance_score.desc()).all()
    rows = []

    for video in videos:
        rows.append({
            "id": video.id,
            "trend_item_id": video.trend_item_id,
            "performance_score": round(video.performance_score or 0, 2),
            "outcome": video.outcome_label,
            "pillar": video.content_pillar,
            "keyword": video.keyword,
            "hook": video.hook_used,
            "posted_at": video.posted_at,
            "duration": video.duration_seconds,
            "views": video.views,
            "qualified_views": video.qualified_views,
            "avg_watch_time": video.avg_watch_time_seconds,
            "completion_rate": video.completion_rate,
            "retention_rate": video.retention_rate,
            "likes": video.likes,
            "comments": video.comments,
            "shares": video.shares,
            "saves": video.saves,
            "follows": video.follows,
            "rpm": video.rpm,
            "revenue": video.revenue,
            "url": video.video_url,
            "notes": video.notes,
        })

    return pd.DataFrame(rows)


def set_status(item_id, status):
    update_session = get_session()
    try:
        item = update_session.query(TrendItem).filter_by(id=int(item_id)).first()
        if item:
            item.status = status
            update_session.commit()
    finally:
        update_session.close()
    st.rerun()


st.title(t("app_title"))
st.caption(t("app_caption"))

ensure_seed_data()

session = get_session()
df = load_trend_dataframe(session)
posted_df = load_posted_videos_dataframe(session)
pillar_summary = pillar_performance_summary(session)

if df.empty:
    st.warning(t("no_data"))
    session.close()
    st.stop()

with st.sidebar:
    st.header(t("filters"))
    platform = st.multiselect(
        t("platform"),
        sorted(df["platform"].dropna().unique()),
        default=list(sorted(df["platform"].dropna().unique())),
    )
    status = st.multiselect(
        t("status"),
        STATUSES,
        default=[s for s in STATUSES if s in set(df["status"]) and s != "ignore"] or ["new"],
        format_func=status_label,
    )
    pillar = st.multiselect(
        t("pillar"),
        sorted(df["pillar"].dropna().unique()),
        default=list(sorted(df["pillar"].dropna().unique())),
        format_func=pillar_label,
    )
    risk_level = st.multiselect(
        t("risk_level"),
        RISK_LEVELS,
        default=["Low", "Medium"],
        format_func=risk_label,
    )
    min_score = st.slider(t("min_score"), 0, 100, 45)
    max_risk = st.slider(t("max_risk"), 0, 100, 65)
    search = st.text_input(t("search_box"))

filtered = df[
    (df["platform"].isin(platform)) &
    (df["status"].isin(status)) &
    (df["pillar"].isin(pillar)) &
    (df["risk_level"].isin(risk_level)) &
    (df["score"] >= min_score) &
    (df["risk"] <= max_risk)
].copy()

if search:
    query = search.lower()
    filtered = filtered[
        filtered["keyword"].str.lower().str.contains(query, na=False) |
        filtered["title"].str.lower().str.contains(query, na=False)
    ]

filtered = filtered.sort_values(["score", "retention", "search"], ascending=False)

metric_1, metric_2, metric_3, metric_4, metric_5, metric_6 = st.columns(6)
metric_1.metric(t("total_trends"), len(df))
metric_2.metric(t("filtered"), len(filtered))
metric_3.metric(t("tiktok_total"), len(df[df["platform"] == "tiktok"]))
metric_4.metric(t("tiktok_visible"), len(filtered[filtered["platform"] == "tiktok"]))
metric_5.metric(t("posted_videos"), len(posted_df))
metric_6.metric(t("creator_ready"), len(df[(df["score"] >= 70) & (df["risk_level"] == "Low")]))

trend_tab, analytics_tab = st.tabs([t("tab_trends"), t("tab_analytics")])

with trend_tab:
    st.subheader(t("ranked_trends"))

    if len(df[df["platform"] == "tiktok"]) > 0 and len(filtered[filtered["platform"] == "tiktok"]) == 0:
        st.info(t("hidden_tiktok"))

    if filtered.empty:
        st.warning(t("empty_filter"))
    else:
        table_columns = [
            "score", "risk_level", "risk", "pillar", "platform", "keyword", "title",
            "us", "search", "retention", "originality", "analytics_adj", "cluster",
            "engagement", "freshness", "cross", "comments", "views", "status", "url",
        ]
        table_df = filtered[table_columns].copy()
        table_df["risk_level"] = table_df["risk_level"].map(risk_label)
        table_df["pillar"] = table_df["pillar"].map(pillar_label)
        table_df["status"] = table_df["status"].map(status_label)

        st.dataframe(
            table_df,
            width="stretch",
            height=420,
            column_config={
                column: st.column_config.TextColumn(label)
                for column, label in COLUMN_LABELS[language].items()
                if column in table_df.columns and column not in {"url", "score", "risk", "analytics_adj"}
            } | {
                "score": st.column_config.NumberColumn(COLUMN_LABELS[language]["score"], format="%.2f"),
                "risk": st.column_config.NumberColumn(COLUMN_LABELS[language]["risk"], format="%.2f"),
                "analytics_adj": st.column_config.NumberColumn(COLUMN_LABELS[language]["analytics_adj"], format="%+.2f"),
                "url": st.column_config.LinkColumn(COLUMN_LABELS[language]["url"]),
            },
        )

        id_to_label = {
            row["id"]: f"#{row['id']} | {row['score']:.1f} | {pillar_label(row['pillar'])} | {row['keyword']}"
            for _, row in filtered.iterrows()
        }

        selected_id = st.selectbox(
            t("select_trend"),
            list(id_to_label.keys()),
            format_func=lambda value: id_to_label.get(value, str(value)),
        )

        selected = session.query(TrendItem).filter_by(id=int(selected_id)).first()
        idea = generate_idea(selected)

        st.subheader(t("production_brief"))

        top_cols = st.columns([2, 1, 1, 1, 1])
        top_cols[0].markdown(f"### {selected.keyword}")
        top_cols[1].metric(t("score"), f"{item_score(selected):.1f}")
        top_cols[2].metric(t("risk"), risk_label(selected.risk_level or "Low"))
        top_cols[3].metric(t("retention"), f"{selected.retention_score or 0:.1f}")
        top_cols[4].metric(t("analytics_adjustment"), f"{selected.analytics_adjustment_score or 0:+.1f}")

        st.write(f"**{t('platform')}:** {selected.platform}")
        st.write(f"**{t('title')}:** {selected.title}")
        st.write(f"**{t('topic_cluster')}:** {selected.topic_cluster or ''}")
        st.write(f"**URL:** {selected.source_url}")

        action_cols = st.columns(5)
        if action_cols[0].button(t("shortlist"), width="stretch"):
            set_status(selected.id, "shortlist")
        if action_cols[1].button(t("scripted"), width="stretch"):
            set_status(selected.id, "scripted")
        if action_cols[2].button(t("posted"), width="stretch"):
            set_status(selected.id, "posted")
        if action_cols[3].button(t("used"), width="stretch"):
            set_status(selected.id, "used")
        if action_cols[4].button(t("ignore"), width="stretch"):
            set_status(selected.id, "ignore")

        brief_tab, script_tab, production_tab, scoring_tab = st.tabs(
            [t("tab_brief"), t("tab_script"), t("tab_production"), t("tab_scoring")]
        )

        with brief_tab:
            st.markdown(f"#### {t('hook')}")
            st.success(idea["hook"])

            st.markdown(f"#### {t('hook_variants')}")
            hook_variant_rows = [
                {"type": name, "hook": hook}
                for name, hook in idea["hook_variants"].items()
            ]
            st.dataframe(pd.DataFrame(hook_variant_rows), width="stretch", hide_index=True)

            st.markdown(f"#### {t('title_options')}")
            for option in idea["title_options"]:
                st.write(f"- {option}")

            st.markdown(f"#### {t('format')}")
            st.write(idea["format"])

            st.markdown(f"#### {t('script_angle')}")
            st.info(idea["script_angle"])

            st.markdown(f"#### {t('caption')}")
            st.write(idea["caption"])

            st.markdown(f"#### {t('hashtags')}")
            st.code(idea["hashtags"])

        with script_tab:
            st.markdown(f"#### {t('beat_sheet')}")
            st.text_area(t("structure"), idea["beat_sheet"], height=190)

            st.markdown(f"#### {t('voiceover_draft')}")
            st.text_area(t("voiceover"), idea["voiceover_script"], height=360)

        with production_tab:
            st.markdown(f"#### {t('onscreen_text')}")
            st.text_area(t("text_overlays"), idea["onscreen_text"], height=160)

            st.markdown(f"#### {t('broll_plan')}")
            st.write(idea["broll_plan"])

            st.markdown(f"#### {t('safety_originality')}")
            st.warning(idea["safety_notes"])

            st.markdown(f"#### {t('production_notes')}")
            st.write(selected.production_notes or t("run_score_note"))

        with scoring_tab:
            score_cols = st.columns(4)
            score_cols[0].metric(t("us_relevance"), f"{selected.us_relevance_score or 0:.1f}")
            score_cols[1].metric(t("originality"), f"{selected.originality_score or 0:.1f}")
            score_cols[2].metric(t("engagement"), f"{selected.engagement_score or 0:.1f}")
            score_cols[3].metric(t("cross_platform"), f"{selected.cross_platform_score or 0:.1f}")

            st.markdown(f"#### {t('performance_hint')}")
            st.info(selected.performance_hint or t("no_analytics"))

            detail = pd.DataFrame([{
                "creator_rewards_score": selected.creator_rewards_score,
                "analytics_adjustment_score": selected.analytics_adjustment_score,
                "topic_cluster": selected.topic_cluster,
                "us_relevance_score": selected.us_relevance_score,
                "search_value_score": selected.search_value_score,
                "retention_score": selected.retention_score,
                "originality_score": selected.originality_score,
                "risk_score": selected.risk_score,
                "engagement_score": selected.engagement_score,
                "freshness_score": selected.freshness_score,
                "cross_platform_score": selected.cross_platform_score,
                "velocity": selected.velocity,
            }])
            st.dataframe(detail, width="stretch", hide_index=True)

with analytics_tab:
    st.subheader(t("pillar_summary"))
    if pillar_summary:
        summary_rows = []
        for pillar_name, values in pillar_summary.items():
            summary_rows.append({
                "pillar": pillar_label(pillar_name),
                "count": values["count"],
                "avg_score": values["avg_score"],
                "avg_rpm": values["avg_rpm"],
                "avg_completion_rate": values["avg_completion_rate"],
                "adjustment": values["adjustment"],
            })
        st.dataframe(pd.DataFrame(summary_rows), width="stretch", hide_index=True)
    else:
        st.info(t("no_analytics"))

    st.subheader(t("posted_video_table"))
    if posted_df.empty:
        st.info(t("no_analytics"))
    else:
        table = posted_df.copy()
        table["pillar"] = table["pillar"].map(pillar_label)
        st.dataframe(
            table,
            width="stretch",
            height=420,
            column_config={"url": st.column_config.LinkColumn("URL")},
        )

session.close()
