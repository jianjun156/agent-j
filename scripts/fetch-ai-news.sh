#!/bin/bash
# fetch-ai-news.sh — 采集 36Kr 热榜 + AI测评笔记，写入 data/ai-news/YYYY-MM.json
# Cron: 0 8,18 * * *
# 数据源: 36Kr 官方 API（无需认证）
set -e

REPO="/Users/jianjun/.openclaw/workspace/agent-j"
NEWS_DIR="$REPO/data/ai-news"
mkdir -p "$NEWS_DIR"

TODAY=$(date +%Y-%m-%d)
MONTH=$(date +%Y-%m)
JSON_FILE="$NEWS_DIR/$MONTH.json"
NOW=$(date +%Y-%m-%dT%H:%M:%S+08:00)

# 1. Fetch hotlist
HOTLIST=$(curl -s "https://openclaw.36krcdn.com/media/hotlist/$TODAY/24h_hot_list.json" 2>/dev/null)

# 2. Fetch AI notes
AINOTES=$(curl -s "https://openclaw.36krcdn.com/media/ainotes/$TODAY/ai_notes.json" 2>/dev/null)

# 3. Merge all sources into monthly JSON with Python
python3 - "$JSON_FILE" "$MONTH" "$NOW" "$TODAY" << PYEOF
import json, sys, urllib.request

json_file = sys.argv[1]
month = sys.argv[2]
now_str = sys.argv[3]
today = sys.argv[4]

# Load existing
try:
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
except:
    data = {"month": month, "lastUpdate": now_str, "articles": []}

existing_urls = set()
for a in data['articles']:
    existing_urls.add(a['url'].split('?')[0])

added = 0

# --- Source 1: Hotlist ---
try:
    hotlist_raw = '''$HOTLIST'''
    api_data = json.loads(hotlist_raw)
    for item in api_data.get('data', []):
        url = item.get('url', '')
        url_clean = url.split('?')[0]
        if not url_clean or url_clean in existing_urls:
            continue
        pub_time = item.get('publishTime', '')
        date_part = pub_time[:10] if len(pub_time) >= 10 else today
        time_part = pub_time[11:16] if len(pub_time) >= 16 else ''
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
except Exception as e:
    print(f"Hotlist error: {e}")

# --- Source 2: AI Notes ---
try:
    ainotes_raw = '''$AINOTES'''
    notes = json.loads(ainotes_raw)
    for n in notes[:15]:
        note_url = n.get('noteUrl', '')
        url_clean = note_url.split('?')[0]
        if not url_clean or url_clean in existing_urls:
            continue
        data['articles'].append({
            "title": n.get('title', ''),
            "summary": (n.get('content', '') or '')[:120],
            "url": note_url,
            "source": "36Kr测评",
            "author": n.get('authorName', ''),
            "date": today,
            "time": "12:00"
        })
        existing_urls.add(url_clean)
        added += 1
except Exception as e:
    print(f"AI Notes error: {e}")

# Sort and save
data['articles'].sort(key=lambda a: a['date'] + a.get('time', ''), reverse=True)
data['lastUpdate'] = now_str

with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Added {added} new articles, total {len(data['articles'])}")
PYEOF

# 4. Git commit + push (only if changes)
cd "$REPO"
if git diff --quiet data/ai-news/ 2>/dev/null; then
  echo "No changes to commit"
else
  git add data/ai-news/
  git commit -m "data: update AI news $TODAY $(date +%H:%M)"
  git push
fi
