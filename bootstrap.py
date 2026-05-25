from db import TrendItem, get_session


def ensure_seed_data():
    session = get_session()
    try:
        has_trends = session.query(TrendItem.id).first() is not None
    finally:
        session.close()

    if has_trends:
        return False

    from import_reddit_csv import main as import_reddit_csv
    from import_tiktok_analytics_csv import main as import_tiktok_analytics_csv
    from import_tiktok_csv import main as import_tiktok_csv
    from score_trends import main as score_trends

    import_reddit_csv()
    import_tiktok_csv()
    import_tiktok_analytics_csv()
    score_trends()
    return True
