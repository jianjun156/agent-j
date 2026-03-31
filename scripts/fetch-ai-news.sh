#!/bin/bash
# fetch-ai-news.sh — 采集 36Kr 热榜 + AI测评笔记，写入 data/ai-news/YYYY-MM.json
# Cron: 0 8,18 * * *
# 数据源: 36Kr 官方 API（无需认证）
set -e

REPO="/Users/jianjun/.openclaw/workspace/agent-j"
NEWS_DIR="$REPO/data/ai-news"
mkdir -p "$NEWS_DIR"

# 纯 Python 实现，避免 shell 变量嵌入 heredoc 的转义问题
python3 << 'PYEOF'
import json, urllib.request, datetime, os

REPO = "/Users/jianjun/.openclaw/workspace/agent-j"
NEWS_DIR = os.path.join(REPO, "data", "ai-news")
os.makedirs(NEWS_DIR, exist_ok=True)

today = datetime.date.today().strftime("%Y-%m-%d")
month = datetime.date.today().strftime("%Y-%m")
json_file = os.path.join(NEWS_DIR, f"{month}.json")
now_str = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")

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
    req = urllib.request.urlopen(
        f"https://openclaw.36krcdn.com/media/hotlist/{today}/24h_hot_list.json", timeout=15)
    hotlist = json.loads(req.read())
    for item in hotlist.get('data', []):
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
    print(f"Hotlist: {added} new articles")
except Exception as e:
    print(f"Hotlist error: {e}")

# --- Source 2: AI Notes ---
added_notes = 0
try:
    req = urllib.request.urlopen(
        f"https://openclaw.36krcdn.com/media/ainotes/{today}/ai_notes.json", timeout=15)
    notes = json.loads(req.read())
    for n in notes[:20]:
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
            "time": "09:00"
        })
        existing_urls.add(url_clean)
        added_notes += 1
    print(f"AI Notes: {added_notes} new articles")
except Exception as e:
    print(f"AI Notes error: {e}")

# Sort by date+time descending and save
data['articles'].sort(key=lambda a: a['date'] + a.get('time', ''), reverse=True)
data['lastUpdate'] = now_str

with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

total = added + added_notes
print(f"Total added: {total}, all articles: {len(data['articles'])}")
PYEOF

# Git commit + push (only if changes)
cd "$REPO"
if git diff --quiet data/ai-news/ 2>/dev/null; then
  echo "No changes to commit"
else
  git add data/ai-news/
  git commit -m "data: update AI news $TODAY $(date +%H:%M)"
  git push
fi
