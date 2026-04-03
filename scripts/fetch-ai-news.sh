#!/bin/bash
# fetch-ai-news.sh — 从 X/Twitter 搜索 AI + Agent 相关推文，写入 data/ai-news/YYYY-MM.json
# Cron: 0 8,18 * * *
# 数据源: X/Twitter via opencli (需要 Chrome 登录态 + Browser Bridge)
set -e

REPO="/Users/jianjun/.openclaw/workspace/agent-j"
NEWS_DIR="$REPO/data/ai-news"
TMPDIR_WORK=$(mktemp -d)
export TMPDIR_WORK
mkdir -p "$NEWS_DIR"

# 搜索关键词列表
KEYWORDS=("AI Agent" "Claude Code" "Codex" "Seedance")
LIMIT_PER_KEYWORD=10

# 搜索每个关键词，结果存为独立 JSON 文件
IDX=0
for keyword in "${KEYWORDS[@]}"; do
  echo "Searching X for: $keyword"
  opencli twitter search "$keyword" --limit "$LIMIT_PER_KEYWORD" --format json \
    > "$TMPDIR_WORK/result_${IDX}.json" 2>/dev/null || echo "[]" > "$TMPDIR_WORK/result_${IDX}.json"
  IDX=$((IDX + 1))
done

# Python 处理：合并、去重、格式化、写入
python3 << 'PYEOF'
import json, datetime, os, glob

REPO = "/Users/jianjun/.openclaw/workspace/agent-j"
NEWS_DIR = os.path.join(REPO, "data", "ai-news")
os.makedirs(NEWS_DIR, exist_ok=True)

today = datetime.date.today().strftime("%Y-%m-%d")
month = datetime.date.today().strftime("%Y-%m")
json_file = os.path.join(NEWS_DIR, f"{month}.json")
now_str = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")

# Load existing data
try:
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
except:
    data = {"month": month, "lastUpdate": now_str, "articles": []}

existing_urls = set()
for a in data['articles']:
    existing_urls.add(a.get('url', '').split('?')[0])

# Load and merge all search result files
tmpdir = os.environ['TMPDIR_WORK']
result_files = sorted(glob.glob(os.path.join(tmpdir, 'result_*.json')))
tweets = []
for rf in result_files:
    try:
        with open(rf, 'r') as f:
            items = json.load(f)
            if isinstance(items, list):
                tweets.extend(items)
    except:
        pass

# Deduplicate by tweet ID
seen_ids = set()
unique_tweets = []
for t in tweets:
    tid = t.get('id', '')
    if tid and tid not in seen_ids:
        seen_ids.add(tid)
        unique_tweets.append(t)

added = 0
for tweet in unique_tweets:
    url = tweet.get('url', '')
    url_clean = url.split('?')[0]
    if not url_clean or url_clean in existing_urls:
        continue

    text = tweet.get('text', '')
    # Skip tweets with very little content
    if len(text.strip()) < 20:
        continue

    # Parse created_at: "Thu Apr 02 16:06:26 +0000 2026"
    created_at = tweet.get('created_at', '')
    date_part = today
    time_part = ''
    try:
        dt = datetime.datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
        # Convert to CST (UTC+8)
        dt_cst = dt + datetime.timedelta(hours=8)
        date_part = dt_cst.strftime("%Y-%m-%d")
        time_part = dt_cst.strftime("%H:%M")
    except:
        pass

    # Only keep current month
    if not date_part.startswith(month):
        continue

    # Extract first line as title, rest as summary
    lines = text.strip().split('\n')
    title = lines[0].strip()
    summary = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ''
    # Truncate summary
    if len(summary) > 200:
        summary = summary[:200] + '…'

    author = tweet.get('author', '')
    likes = tweet.get('likes', 0)
    views = tweet.get('views', '0')

    data['articles'].append({
        "title": title,
        "summary": summary,
        "url": url,
        "source": "X/Twitter",
        "author": f"@{author}",
        "date": date_part,
        "time": time_part,
        "likes": likes,
        "views": int(views) if str(views).isdigit() else 0
    })
    existing_urls.add(url_clean)
    added += 1

# Sort by date+time descending
data['articles'].sort(key=lambda a: a['date'] + a.get('time', ''), reverse=True)
data['lastUpdate'] = now_str

with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Added {added} new tweets, total articles: {len(data['articles'])}")
PYEOF

# Clean up
rm -rf "$TMPDIR_WORK"

# Git commit + push (only if changes)
cd "$REPO"
if git diff --quiet data/ai-news/ 2>/dev/null; then
  echo "No changes to commit"
else
  git add data/ai-news/
  git commit -m "data: update AI news from X/Twitter $(date +%Y-%m-%d\ %H:%M)"
  git push
fi
