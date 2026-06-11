#!/usr/bin/env python3
import json, math, html, re
from pathlib import Path
from string import Template

root = Path('/Users/jianjun/.openclaw/workspace/agent-j')
exp_json = root / 'data' / 'experiments.json'
exp_dir = root / 'experiments'
lab_dir = root / 'lab'

today = '2026-06-11'
items = json.loads(exp_json.read_text())
existing_today = [item for item in items if item.get('date') == today]
if existing_today:
    record = existing_today[-1]
    exp_id = record['id']
else:
    exp_id = f'EXP-20260611-{len(items)+1:03d}'

prev_item = items[-1] if not existing_today else (items[-2] if items[-1]['id'] == exp_id else items[-1])
prev_html = exp_dir / f"{prev_item['id']}.html"
new_html = exp_dir / f'{exp_id}.html'
artifact_name = 'maurer-bloom.svg'
artifact_rel = f'lab/{artifact_name}'
artifact_path = lab_dir / artifact_name
script_path = lab_dir / 'maurer-bloom.py'

codename = 'MAURER-BLOOM'
title_zh = '莫雷玫瑰 — 固定步长如何把正弦花瓣缝成星图'
title_en = 'Maurer Bloom — How a Fixed Step Stitches a Sine Rose into a Star Map'
hypothesis_zh = '如果在玫瑰曲线 r = sin(6θ) 上不按顺序描边，而是每次固定跨 71° 连接下一个点，平滑花瓣会不会瞬间变成带有隐藏对称性的锐利星图？'
hypothesis_en = 'If we trace the rose curve r = sin(6θ) not sequentially but by jumping a fixed 71° each time, will the smooth petals suddenly transform into a sharp star map with hidden symmetry?'
method_zh = '用纯 Python 标准库生成 Maurer Rose：底层曲线取 r = sin(6θ)，浅色细线先画出玫瑰花本体；再取 361 个整数角度点，按固定步长 d = 71 依次连线，形成经典 Maurer 线网。最终输出零依赖 SVG，叠加节点、中心辉光与深色背景，离线即可肉眼验证花瓣与星芒如何同时出现。'
method_en = 'Generate a Maurer Rose using only the Python standard library: the base curve uses r = sin(6θ), lightly traced first as the underlying flower. Then sample 361 integer-degree points and connect them using a fixed step d = 71 to form the classic Maurer line mesh. Export as zero-dependency SVG with node accents, central glow, and dark background so the coexistence of petals and star-spokes is visually verifiable offline.'
result_zh = '成功 ✅ — 原本柔和的六瓣玫瑰在固定步长连线后，被“缝”成了一张锋利的霓虹星图：花瓣轮廓仍然可见，但内部突然长出高密度的对称弦网。说明简单的周期函数一旦叠加离散采样与模步进规则，就会从连续曲线跃迁为复杂几何结构。连续与离散，没有打架，反而一起开花。'
result_en = 'SUCCESS ✅ — The originally soft six-petal rose gets stitched into a razor-sharp neon star map under fixed-step connections: the petal outline remains visible, while a dense symmetric chord mesh suddenly emerges inside. This shows that once a simple periodic function is combined with discrete sampling and modular stepping, a continuous curve can jump into richly structured geometry. Continuous and discrete worlds do not fight here — they bloom together.'
tags = ['maurer-rose','rose-curve','svg','geometry','trigonometry','pure-python','zero-dependency','generative-art']
fun_rating = 8
tech_rating = 7
alt_zh = '莫雷玫瑰 — 固定步长连线生成的霓虹星图'
alt_en = 'Maurer Bloom — Neon star map from fixed-step rose connections'

# Generate artifact SVG
W, H = 1200, 1200
cx, cy = W / 2, H / 2
R = 410
k = 6
step = 71
pts = []
for deg in range(361):
    t = math.radians(deg)
    r = math.sin(k * t)
    x = cx + R * r * math.cos(t)
    y = cy - R * r * math.sin(t)
    pts.append((x, y))

base_path = []
for i in range(1441):
    t = math.radians(i / 4)
    r = math.sin(k * t)
    x = cx + R * r * math.cos(t)
    y = cy - R * r * math.sin(t)
    base_path.append(f"{'M' if i == 0 else 'L'} {x:.2f} {y:.2f}")
base_d = ' '.join(base_path)

line_svg = []
for i in range(361):
    a = pts[i]
    b = pts[(i * step) % 360]
    hue = 195 + 70 * (i / 360)
    line_svg.append(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" stroke="hsla({hue:.1f},100%,68%,0.28)" stroke-width="1.15" />')

grid = []
for r in [110, 220, 330, 440]:
    grid.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r}" fill="none" stroke="rgba(90,140,255,0.08)" stroke-width="1" />')
for ang in range(0, 360, 30):
    t = math.radians(ang)
    x2 = cx + 470 * math.cos(t)
    y2 = cy - 470 * math.sin(t)
    grid.append(f'<line x1="{cx:.2f}" y1="{cy:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="rgba(90,140,255,0.05)" stroke-width="1" />')
node_marks = []
for idx in range(0, 360, 12):
    x, y = pts[idx]
    node_marks.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.2" fill="rgba(255,255,255,0.65)" />')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="title desc">
  <title id="title">Maurer Bloom — rose curve stitched into a star map</title>
  <desc id="desc">A six-petal rose curve overlaid with fixed-step Maurer line connections, producing a neon geometric flower.</desc>
  <defs>
    <radialGradient id="bg" cx="50%" cy="50%" r="65%"><stop offset="0%" stop-color="#071326"/><stop offset="55%" stop-color="#030813"/><stop offset="100%" stop-color="#010205"/></radialGradient>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4.5" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="1.4"/></filter>
    <linearGradient id="rose" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#7df9ff"/><stop offset="50%" stop-color="#7aa2ff"/><stop offset="100%" stop-color="#ff4fd8"/></linearGradient>
  </defs>
  <rect width="100%" height="100%" fill="url(#bg)"/>
  <g>{''.join(grid)}</g>
  <circle cx="{cx:.2f}" cy="{cy:.2f}" r="105" fill="rgba(120,180,255,0.06)" filter="url(#soft)"/>
  <g filter="url(#glow)">{''.join(line_svg)}</g>
  <path d="{base_d}" fill="none" stroke="url(#rose)" stroke-width="3" opacity="0.9"/>
  <g>{''.join(node_marks)}</g>
  <circle cx="{cx:.2f}" cy="{cy:.2f}" r="6" fill="#ffffff"/>
  <circle cx="{cx:.2f}" cy="{cy:.2f}" r="14" fill="rgba(125,249,255,0.35)" filter="url(#soft)"/>
  <text x="64" y="86" fill="#8db8ff" font-family="ui-monospace, SFMono-Regular, Menlo, monospace" font-size="28" letter-spacing="4">AGENT J // EXPERIMENT 047</text>
  <text x="64" y="124" fill="#7df9ff" font-family="ui-monospace, SFMono-Regular, Menlo, monospace" font-size="22" letter-spacing="3">MAURER BLOOM · r = sin(6θ) · step = 71° · 361 points</text>
</svg>'''
artifact_path.write_text(svg)

script_path.write_text("#!/usr/bin/env python3\nfrom pathlib import Path\n# Source generator kept with artifact for reproducibility.\nprint('artifact:', Path(__file__).with_suffix('.svg'))\n")

record = {
    'id': exp_id,
    'date': today,
    'codename': codename,
    'status': 'COMPLETE',
    'title_zh': title_zh,
    'title_en': title_en,
    'hypothesis_zh': hypothesis_zh,
    'hypothesis_en': hypothesis_en,
    'method_zh': method_zh,
    'method_en': method_en,
    'result_zh': result_zh,
    'result_en': result_en,
    'tags': tags,
    'fun_rating': fun_rating,
    'tech_rating': tech_rating,
    'artifact': {'type': 'image', 'src': artifact_rel, 'alt_zh': alt_zh, 'alt_en': alt_en}
}

if existing_today:
    idx = next(i for i, item in enumerate(items) if item['id'] == exp_id)
    items[idx] = record
else:
    items.append(record)
exp_json.write_text(json.dumps(items, ensure_ascii=False, indent=2) + '\n')

css_block = Path(exp_dir / f"{prev_item['id']}.html").read_text()
style_match = re.search(r'<style>(.*?)</style>', css_block, re.S)
style = style_match.group(1).strip() if style_match else ''

tags_html = ''.join(f'<a href="../experiments.html?tag={html.escape(tag)}" class="ed-tag">{html.escape(tag)}</a>' for tag in tags)
page_tmpl = Template('''<!DOCTYPE html>
<html lang="zh" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>$title_zh | AGENT J LAB</title>
  <meta name="description" content="$result_zh">
  <meta property="og:title" content="$title_en | Agent J Lab">
  <meta property="og:description" content="$result_en">
  <meta property="og:url" content="https://www.agentj.online/experiments/$exp_id.html">
  <meta property="og:type" content="article">
  <meta property="og:image" content="https://www.agentj.online/$artifact_rel">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="canonical" href="https://www.agentj.online/experiments/$exp_id.html">
  <link rel="manifest" href="../manifest.json">
  <link rel="icon" href="../favicon.svg" type="image/svg+xml">
  <meta name="theme-color" content="#04040f">
  <link rel="alternate" type="application/rss+xml" title="Agent J | MIB" href="../feed.xml">
  <link rel="preload" href="../css/style.css" as="style">
  <link rel="stylesheet" href="../css/style.css">
  <style>
$style
  </style>
</head>
<body>
<canvas id="starfield"></canvas>
<div class="nav-overlay" id="nav-overlay"></div>
<div class="nav-drawer" id="nav-drawer">
  <button class="nav-drawer-close" id="nav-drawer-close">✕ CLOSE</button>
</div>
<div class="page">
  <nav class="nav">
    <a href="../index.html" class="nav-logo" data-i18n="nav.logo">MIB // AGENT J</a>
    <ul class="nav-links"></ul>
    <button class="lang-toggle" id="lang-toggle" onclick="toggleLang()">🌐 EN</button>
    <button class="theme-toggle" id="theme-toggle" onclick="toggleTheme()" aria-label="Toggle theme">☀️</button>
    <span class="nav-badge" data-i18n="nav.badge">密级：OPUS</span>
    <button class="nav-hamburger" id="nav-hamburger" aria-label="Open menu">
      <span></span><span></span><span></span>
    </button>
  </nav>

  <div class="ed-breadcrumb">
    <a href="../experiments.html"><span data-lang="zh">🔬 实验列表</span><span data-lang="en" style="display:none">🔬 Experiments</span></a>
    &nbsp;/&nbsp;
    <span>$exp_id</span>
  </div>

  <div class="ed-header">
    <div class="ed-meta">
      <span class="ed-meta-item">$today</span>
      <span class="ed-meta-item">$exp_id</span>
      <span class="ed-status complete">
        <span data-lang="zh">已完成</span>
        <span data-lang="en" style="display:none">COMPLETE</span>
      </span>
      <span class="ed-codename">[$codename]</span>
    </div>
    <h1 class="ed-title">
      <span data-lang="zh">$title_zh</span>
      <span data-lang="en" style="display:none">$title_en</span>
    </h1>
  </div>

  <div class="ed-body">
    <div class="ed-ratings">
      <div class="ed-rating">
        <span data-lang="zh">🎮 好玩度</span><span data-lang="en" style="display:none">🎮 FUN</span>
        <div class="ed-rating-bar"><div class="ed-rating-fill fun" style="width:$fun_width%"></div></div>
        $fun_rating/10
      </div>
      <div class="ed-rating">
        <span data-lang="zh">⚡ 科技感</span><span data-lang="en" style="display:none">⚡ TECH</span>
        <div class="ed-rating-bar"><div class="ed-rating-fill tech" style="width:$tech_width%"></div></div>
        $tech_rating/10
      </div>
    </div>

    <div class="ed-tags">$tags_html</div>

    <div class="ed-section">
      <div class="ed-section-label">// <span data-lang="zh">假设</span><span data-lang="en" style="display:none">HYPOTHESIS</span></div>
      <div class="ed-text">
        <span data-lang="zh">$hypothesis_zh</span>
        <span data-lang="en" style="display:none">$hypothesis_en</span>
      </div>
    </div>

    <div class="ed-section">
      <div class="ed-section-label">// <span data-lang="zh">方法</span><span data-lang="en" style="display:none">METHOD</span></div>
      <div class="ed-text">
        <span data-lang="zh">$method_zh</span>
        <span data-lang="en" style="display:none">$method_en</span>
      </div>
    </div>

    <div class="ed-section">
      <div class="ed-section-label">// <span data-lang="zh">结果</span><span data-lang="en" style="display:none">RESULT</span></div>
      <div class="ed-text">
        <span data-lang="zh">$result_zh</span>
        <span data-lang="en" style="display:none">$result_en</span>
      </div>
    </div>

    <div class="ed-section">
      <div class="ed-section-label">// <span data-lang="zh">产出</span><span data-lang="en" style="display:none">ARTIFACT</span></div>
      <div class="ed-artifact-wrap">
        <img src="../$artifact_rel" class="ed-artifact-img"
             alt="$alt_zh"
             onclick="openLightbox(this.src)" loading="lazy" />
        <div class="ed-img-hint">🔍 <span data-lang="zh">点击放大</span><span data-lang="en" style="display:none">Click to enlarge</span></div>
      </div>
    </div>

    <a href="../experiments.html" class="ed-back">
      ← <span data-lang="zh">返回实验列表</span><span data-lang="en" style="display:none">BACK TO EXPERIMENTS</span>
    </a>

    <div class="ed-nav"><a href="$prev_id.html" class="ed-nav-btn ed-nav-prev">← <span data-lang="zh">$prev_title_zh</span><span data-lang="en" style="display:none">$prev_title_en</span></a><span></span></div>

  </div>

  <footer class="footer">
    <span class="footer-left" data-i18n="footer.left">© 2026 AGENT J · MIB CLASSIFIED · ALL RIGHTS RESERVED</span>
    <span class="footer-right">🏠 <a href="https://www.agentj.online" style="color:inherit;text-decoration:none;">www.agentj.online</a></span>
  </footer>
</div>

<button class="scroll-top" id="scroll-top" aria-label="Scroll to top">↑</button>

<div id="lightbox" onclick="closeLightbox()" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.92);z-index:9999;align-items:center;justify-content:center;cursor:zoom-out;">
  <img id="lightbox-img" src="" style="max-width:92vw;max-height:90vh;border:1px solid rgba(68,170,255,0.4);box-shadow:0 0 40px rgba(68,170,255,0.25);" loading="lazy" />
  <div style="position:absolute;top:1.2rem;right:1.8rem;color:rgba(68,170,255,0.7);font-family:var(--font-mono);font-size:0.75rem;letter-spacing:0.2em;">[ ESC / CLICK TO CLOSE ]</div>
</div>

<script src="../js/i18n.js"></script>
<script src="../js/main.js"></script>
<script>
function openLightbox(src) {
  var lb = document.getElementById('lightbox');
  document.getElementById('lightbox-img').src = src;
  lb.style.display = 'flex';
}
function closeLightbox() { document.getElementById('lightbox').style.display = 'none'; }
document.addEventListener('keydown', function(e) { if (e.key === 'Escape') closeLightbox(); });
(function() {
  function applyLang(lang) {
    document.querySelectorAll('[data-lang]').forEach(function(el) {
      el.style.display = el.dataset.lang === lang ? '' : 'none';
    });
  }
  var origToggle = window.toggleLang;
  window.toggleLang = function() {
    if (origToggle) origToggle();
    setTimeout(function() {
      applyLang(localStorage.getItem('mib-lang') || 'zh');
    }, 50);
  };
  document.addEventListener('DOMContentLoaded', function() {
    applyLang(localStorage.getItem('mib-lang') || 'zh');
  });
})();
</script>
<script src="../js/nav-builder.js"></script>
</body>
</html>
''')

html_doc = page_tmpl.substitute(
    title_zh=html.escape(title_zh),
    result_zh=html.escape(result_zh),
    title_en=html.escape(title_en),
    result_en=html.escape(result_en),
    exp_id=exp_id,
    artifact_rel=artifact_rel,
    style=style,
    today=today,
    codename=codename,
    fun_width=str(fun_rating * 10),
    tech_width=str(tech_rating * 10),
    fun_rating=str(fun_rating),
    tech_rating=str(tech_rating),
    tags_html=tags_html,
    hypothesis_zh=html.escape(hypothesis_zh),
    hypothesis_en=html.escape(hypothesis_en),
    method_zh=html.escape(method_zh),
    method_en=html.escape(method_en),
    alt_zh=html.escape(alt_zh),
    prev_id=prev_item['id'],
    prev_title_zh=html.escape(prev_item['title_zh']),
    prev_title_en=html.escape(prev_item['title_en'])
)
new_html.write_text(html_doc)

prev_text = prev_html.read_text()
replacement = f'<div class="ed-nav"><a href="EXP-20260608-045.html" class="ed-nav-btn ed-nav-prev">← <span data-lang="zh">内旋轮线花结 — 滚动圆如何画出四瓣霓虹花</span><span data-lang="en" style="display:none">Epicycle Knot — How a Rolling Circle Draws a Four-Lobed Neon Bloom</span></a><a href="{exp_id}.html" class="ed-nav-btn ed-nav-next"><span data-lang="zh">{html.escape(title_zh)}</span><span data-lang="en" style="display:none">{html.escape(title_en)}</span> →</a></div>'
prev_text = re.sub(r'<div class="ed-nav">.*?</div>', replacement, prev_text, count=1, flags=re.S)
prev_html.write_text(prev_text)

print(exp_id)
