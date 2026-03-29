#!/bin/bash
# fetch-ai-news.sh — 采集 36Kr AI 频道资讯，写入 data/ai-news/YYYY-MM.json
# Cron: 0 8,18 * * *
set -e

REPO="/Users/jianjun/.openclaw/workspace/agent-j"
NEWS_DIR="$REPO/data/ai-news"
mkdir -p "$NEWS_DIR"

MONTH=$(date +%Y-%m)
JSON_FILE="$NEWS_DIR/$MONTH.json"
NOW=$(date -u +%Y-%m-%dT%H:%M:%S+08:00)

# 1. Open 36Kr AI in Chrome
osascript -e 'tell application "Google Chrome" to open location "https://36kr.com/information/AI/"' 2>/dev/null

# 2. Wait for page load
sleep 7

# 3. Extract articles via Chrome JS — find the 36kr tab first
RAW=$(osascript << 'APPLESCRIPT'
tell application "Google Chrome"
  -- Find the 36kr tab
  set found to false
  repeat with w in windows
    repeat with i from 1 to (count tabs of w)
      if URL of tab i of w contains "36kr.com/information" then
        set active tab index of w to i
        set index of w to 1
        set found to true
        exit repeat
      end if
    end repeat
    if found then exit repeat
  end repeat
  
  if not found then return "[]"
  
  delay 2
  set t to active tab of front window
  set r to execute t javascript "
    var cards = document.querySelectorAll('.flow-item, .article-item, [class*=flow-item]');
    var out = [];
    cards.forEach(function(card, idx) {
      if (idx >= 20) return;
      var titleEl = card.querySelector('a[class*=title], [class*=title] a, .flow-item-title a');
      if (!titleEl) titleEl = card.querySelector('a');
      var descEl = card.querySelector('[class*=desc], [class*=summary], .flow-item-desc');
      var timeEl = card.querySelector('[class*=time], [class*=date], time');
      var title = titleEl ? titleEl.innerText.trim() : '';
      var href = titleEl ? titleEl.href : '';
      var desc = descEl ? descEl.innerText.trim().substring(0, 120) : '';
      var time = timeEl ? timeEl.innerText.trim() : '';
      if (title && href) out.push(JSON.stringify({t:title, h:href, d:desc, tm:time}));
    });
    '[' + out.join(',') + ']';
  "
  return r
end tell
APPLESCRIPT
)

# 4. Merge into JSON with Python
python3 - "$RAW" "$JSON_FILE" "$MONTH" "$NOW" << 'PYEOF'
import json, sys, re
from datetime import datetime, timedelta

raw_str = sys.argv[1]
json_file = sys.argv[2]
month = sys.argv[3]
now_str = sys.argv[4]

# Parse raw
try:
    items = json.loads(raw_str)
except:
    print("Failed to parse Chrome output"); sys.exit(1)

if not items:
    print("No articles found"); sys.exit(0)

now = datetime.now()
today_str = now.strftime('%Y-%m-%d')

def parse_relative_time(t):
    """Convert relative time like '45分钟前', '3小时前', '昨天' to date+time"""
    if '分钟前' in t:
        mins = int(re.search(r'(\d+)', t).group(1))
        dt = now - timedelta(minutes=mins)
    elif '小时前' in t:
        hrs = int(re.search(r'(\d+)', t).group(1))
        dt = now - timedelta(hours=hrs)
    elif '昨天' in t:
        dt = now - timedelta(days=1)
    elif '天前' in t:
        days = int(re.search(r'(\d+)', t).group(1))
        dt = now - timedelta(days=days)
    elif re.match(r'\d{4}-\d{2}-\d{2}', t):
        dt = datetime.strptime(t[:10], '%Y-%m-%d')
    else:
        dt = now
    return dt.strftime('%Y-%m-%d'), dt.strftime('%H:%M')

# Load existing
try:
    with open(json_file, 'r') as f:
        data = json.load(f)
except:
    data = {"month": month, "lastUpdate": now_str, "articles": []}

existing_urls = {a['url'] for a in data['articles']}

added = 0
for item in items:
    url = item.get('h', '')
    if not url or url in existing_urls:
        continue
    date, time = parse_relative_time(item.get('tm', ''))
    # Only add if in current month
    if not date.startswith(month):
        continue
    data['articles'].append({
        "title": item['t'],
        "summary": item.get('d', ''),
        "url": url,
        "source": "36Kr",
        "date": date,
        "time": time
    })
    existing_urls.add(url)
    added += 1

# Sort by date+time descending
data['articles'].sort(key=lambda a: a['date'] + a.get('time',''), reverse=True)
data['lastUpdate'] = now_str

with open(json_file, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Added {added} new articles, total {len(data['articles'])}")
PYEOF

# 5. Git commit + push (only if changes)
cd "$REPO"
if git diff --quiet data/ai-news/ 2>/dev/null; then
  echo "No changes to commit"
else
  git add data/ai-news/
  git commit -m "data: update AI news $(date +%Y-%m-%d\ %H:%M)"
  git push
fi
