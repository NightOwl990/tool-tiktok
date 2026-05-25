# TikTok US Creator Rewards Trend Tool

Tool này dùng để tìm và chấm điểm trend cho nội dung TikTok thị trường US, ưu tiên video 60-90 giây phù hợp Creator Rewards:

- Lấy trend từ Reddit qua API chính thức.
- Nhập trend TikTok bằng CSV từ TikTok Creative Center hoặc nhập tay.
- Nhập Reddit trend thủ công bằng CSV khi chưa cấu hình Reddit API.
- Chấm điểm theo US relevance, search value, retention, originality, engagement, freshness, cross-platform và monetization risk.
- Import analytics video đã đăng để tool tự học nhóm nội dung/hook nào đang thắng.
- Hiển thị dashboard Streamlit để lọc trend, shortlist, tạo production brief, script tiếng Anh, caption, hashtag và B-roll plan.

## 1. Cài đặt

```bash
cd tiktok_reddit_trend_tool
python -m venv .venv
source .venv/bin/activate

# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env
```

## 2. Cấu hình Reddit API

Vào Reddit Developer Apps:

- Tạo app loại `script`.
- Lấy `client_id` và `client_secret`.
- Điền vào `.env`.

```env
REDDIT_CLIENT_ID=xxx
REDDIT_CLIENT_SECRET=xxx
REDDIT_USER_AGENT=tiktok-reddit-trend-tool by your_name
```

Nếu chưa có Reddit API, bạn vẫn có thể dùng `data/reddit_trends.csv` và chạy `python import_reddit_csv.py`.

## 3. CSV TikTok

File: `data/tiktok_trends.csv`

```csv
keyword,source_url,region,category,views,likes,comments,shares,created_at
ai girlfriend,https://www.tiktok.com/tag/aigirlfriend,US,AI,1000000,50000,3000,2000,2026-05-25T10:00:00
```

Ưu tiên `region=US` nếu bạn đang làm thị trường US.

## 4. CSV Reddit thủ công

File: `data/reddit_trends.csv`

```csv
subreddit,title,url,score,comments,created_at
AITAH,"Am I wrong for not inviting my sister to my wedding?","https://reddit.com/r/AITAH/example",12000,3400,2026-05-25T10:00:00
```

## 5. Workflow hằng ngày

Windows, chạy nhanh một lệnh:

```powershell
.\run.bat
```

Lệnh này sẽ tự dùng `.venv`, cài requirements nếu cần, import CSV, import analytics, chấm điểm và mở dashboard.

Nếu muốn chạy kèm Reddit API collector:

```powershell
.\run_all.bat
```

Chạy thủ công từng bước:

```bash
python collect_reddit.py       # optional nếu đã cấu hình Reddit API
python import_reddit_csv.py    # optional nếu dùng CSV Reddit
python import_tiktok_csv.py
python import_tiktok_analytics_csv.py  # optional nếu có analytics video đã đăng
python score_trends.py
streamlit run dashboard.py
```

macOS/Linux:

```bash
./run_all.sh  # macOS/Linux
```

## 6. Ý nghĩa điểm mới

- `creator_rewards_score`: điểm xếp hạng chính cho TikTok US.
- `us_relevance_score`: độ hợp với thị trường US.
- `search_value_score`: khả năng có search intent và giá trị evergreen.
- `retention_score`: khả năng giữ người xem 60-90 giây.
- `originality_score`: khả năng biến thành nội dung gốc, không low-effort/reused.
- `risk_score`: rủi ro monetization/policy. Điểm càng cao càng rủi ro.
- `cross_platform_score`: độ trùng trend giữa Reddit và TikTok, đã giảm false positive so với bản MVP.
- `analytics_adjustment_score`: điểm cộng/trừ học từ hiệu suất video đã đăng theo từng nhóm nội dung.
- `topic_cluster`: cụm chủ đề để tránh làm trùng quá nhiều video cùng một angle.

## 7. Import analytics TikTok Studio

Sau khi đăng video, điền file `data/tiktok_analytics.csv`.

```csv
video_id,video_url,trend_item_id,keyword,content_pillar,title,hook_used,caption_used,posted_at,duration_seconds,views,qualified_views,avg_watch_time_seconds,completion_rate,retention_rate,likes,comments,shares,saves,follows,rpm,revenue,snapshot_age_hours,notes
```

Các cột quan trọng nhất:

- `trend_item_id`: ID trend trong dashboard. Có thì tool link chính xác nhất.
- `keyword`: keyword/topic video đã đăng.
- `content_pillar`: ví dụ `AI tools`, `Workplace`, `Money`, `Relationship drama`, `Horror story`.
- `hook_used`: hook đã dùng để sau này so sánh hook thắng/thua.
- `duration_seconds`: độ dài video.
- `views`, `qualified_views`, `avg_watch_time_seconds`, `completion_rate`, `retention_rate`.
- `rpm`, `revenue`: nếu TikTok Studio có hiển thị.

Sau đó chạy:

```bash
python import_tiktok_analytics_csv.py
python score_trends.py
```

Dashboard tab `Analytics đã đăng` sẽ hiển thị:

- performance score từng video;
- winner/promising/neutral/loser;
- RPM trung bình theo nhóm nội dung;
- điểm boost/penalty áp ngược vào trend mới cùng nhóm.

## 8. Dashboard workflow

Trong dashboard:

0. Chọn `Tiếng Việt` hoặc `English` ở sidebar nếu muốn đổi ngôn ngữ giao diện.
1. Lọc theo `Creator Rewards score`, `risk`, `pillar`, `platform`, `status`.
2. Chọn trend có score cao, risk thấp hoặc trung bình.
3. Xem production brief gồm hook A/B, title options, beat sheet, voiceover, on-screen text, B-roll plan, caption và hashtag.
4. Dùng nút trạng thái: `shortlist`, `scripted`, `posted`, `used`, `ignore`.

## 9. Lưu ý quan trọng

- Không đọc nguyên văn bài Reddit/TikTok thành video. Hãy rewrite, thêm bình luận, cấu trúc, ví dụ và visual riêng.
- Hạn chế topic graphic, sexual, illegal, medical/legal/financial advice hoặc copyrighted clips.
- Với money/career content, trình bày như giáo dục hoặc case study, không hứa kết quả.
- Tool này không scrape private API của TikTok.
