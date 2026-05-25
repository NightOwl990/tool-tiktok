#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

if [ ! -x ".venv/bin/python" ]; then
  python -m venv .venv
fi

.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python collect_reddit.py || echo "Skipping Reddit API collector. Check .env credentials if needed."
.venv/bin/python import_reddit_csv.py
.venv/bin/python import_tiktok_csv.py
.venv/bin/python import_tiktok_analytics_csv.py
.venv/bin/python score_trends.py
.venv/bin/python -m streamlit run dashboard.py
