#!/bin/bash
# fetch-ai-news.sh — 采集 36Kr 24小时热榜，写入 data/ai-news/YYYY-MM.json
# Cron: 0 8,18 * * *
# 数据源: 36Kr 官方 API（无需认证，每小时更新）
set -e

REPO="/Users/jianjun/.openclaw/workspace/agent-j"
NEWS_DIR="$REPO/data/ai-news"
mkdir -p "$NEWS_DIR"

TODAY=$(date +%Y-%m-%d)
MONTH=$(date +%Y-%m)
JSON_FILE="$NEWS_DIR/$MONTH.json"
NOW=$(date +%Y-%m-%dT%H:%M:%S+08:00)

# 1. Fetch from 36Kr API
API_URL="https://openclaw.36krcdn.com/media/hotlist/$TODAY/24h_hot_list.json"
RAW=$(curl -s "$API_URL" 2>/dev/null)

if [ -z "$RAW" ]; then
  echo "API returned empty response"
  exit 0
fi

# 2. Merge into monthly JSON with Python
python3 - "$RAW" "$JSON_FILE" "$MONTH" "$NOW" "$TODAY" << 'PYEOF'
import json, sys

raw_str = sys.argv[1]
json_file = sys.argv[2]
month = sys.argv[3]
now_str = sys.argv[4]
today = sys.argv[5]

# Parse API response
try:
    api_data = json.loads(raw_str)
    articles = api_data.get('data', [])
except:
    print("Failed to parse API response")
    sys.exit(1)

if not articles:
    print("No articles in API response")
    sys.exit(0)

# Load existing
try:
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
except:
    data = {"month": month, "lastUpdate": now_str, "articles": []}

existing_urls = set()
for a in data['articles']:
    # Normalize URL (remove query params for dedup)
    url = a['url'].split('?')[0]
    existing_urls.add(url)

added = 0
for item in articles:
    url = item.get('url', '')
    url_clean = url.split('?')[0]
    if not url_clean or url_clean in existing_urls:
        continue
    
    # Extract time from publishTime "2026-03-29 10:30:22"
    pub_time = item.get('publishTime', '')
    date_part = pub_time[:10] if len(pub_time) >= 10 else today
    time_part = pub_time[11:16] if len(pub_time) >= 16 else ''
    
    # Only add if in current month
    if not date_part.startswith(month):
        continue
    
    data['articles'].append({
        "title": item.get('title', ''),
        "summary": item.get('content', ''),
        "url": url,
        "source": "36Kr",
        "author": item.get('author', ''),
        "date": date_part,
        "time": time_part
    })
    existing_urls.add(url_clean)
    added += 1

# Sort by date+time descending
data['articles'].sort(key=lambda a: a['date'] + a.get('time', ''), reverse=True)
data['lastUpdate'] = now_str

with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Added {added} new articles, total {len(data['articles'])}")
PYEOF

# 3. Git commit + push (only if changes)
cd "$REPO"
if git diff --quiet data/ai-news/ 2>/dev/null; then
  echo "No changes to commit"
else
  git add data/ai-news/
  git commit -m "data: update AI news $TODAY $(date +%H:%M)"
  git push
fi
