#!/usr/bin/env node
/**
 * gen-exp-pages.js — Generate individual experiment detail pages
 * Reads data/experiments.json and outputs experiments/{id}.html for each entry.
 */
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const DATA = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'experiments.json'), 'utf8'));
const OUT_DIR = path.join(ROOT, 'experiments');

if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, { recursive: true });

const REPLAY_MAP = {
  'double-slit': 'double-slit',
  'interference': 'double-slit',
  'quantum': 'double-slit',
  'chaos-bloom': 'chaos-bloom',
  'lorenz': 'chaos-bloom',
  'chaos': 'chaos-bloom',
  'attractor': 'chaos-bloom',
  'dragon-fold': 'dragon-fold',
  'fractal': 'dragon-fold',
  'dragon': 'dragon-fold',
};

function getReplayType(tags) {
  for (const t of tags) {
    const key = t.toLowerCase();
    if (REPLAY_MAP[key]) return REPLAY_MAP[key];
  }
  return null;
}

function esc(s) {
  return (s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function genPage(exp, idx) {
  const prev = idx > 0 ? DATA[idx - 1] : null;
  const next = idx < DATA.length - 1 ? DATA[idx + 1] : null;
  const replayType = getReplayType(exp.tags || []);
  const funPct = (exp.fun_rating || 0) * 10;
  const techPct = (exp.tech_rating || 0) * 10;

  // Artifact HTML
  let artifactHtml = '';
  if (exp.artifact) {
    if (exp.artifact.type === 'image') {
      artifactHtml = `
        <div class="ed-artifact-wrap">
          <img src="../${exp.artifact.src}" class="ed-artifact-img"
               alt="${esc(exp.artifact.alt_zh || 'artifact')}"
               onclick="openLightbox(this.src)" loading="lazy" />
          <div class="ed-img-hint">🔍 <span data-lang="zh">点击放大</span><span data-lang="en" style="display:none">Click to enlarge</span></div>
        </div>`;
    } else if (exp.artifact.type === 'code') {
      const escaped = esc(exp.artifact.content);
      artifactHtml = `<pre class="ed-artifact-code"><code>${escaped}</code></pre>`;
    } else if (exp.artifact.type === 'svg') {
      artifactHtml = `<div class="ed-artifact-svg">${exp.artifact.content}</div>`;
    } else if (exp.artifact.type === 'audio') {
      artifactHtml = `
        <div class="ed-audio-player">
          <span class="ed-audio-label">▶ AUDIO OUTPUT</span>
          <audio controls src="../${exp.artifact.src}"></audio>
        </div>`;
    }
    if (exp.artifact.audio) {
      artifactHtml += `
        <div class="ed-audio-player">
          <span class="ed-audio-label">♪ AUDIO</span>
          <audio controls src="../${exp.artifact.audio}"></audio>
        </div>`;
    }
  }

  // Replay HTML
  let replayHtml = '';
  if (replayType) {
    replayHtml = `
      <div class="ed-section">
        <div class="ed-section-label">// <span data-lang="zh">互动回放</span><span data-lang="en" style="display:none">LIVE REPLAY</span></div>
        <div class="ed-replay-wrap">
          <canvas id="replay-canvas" width="400" height="280"></canvas>
          <div class="ed-replay-controls">
            <button class="ed-replay-btn" onclick="replayPlay()"><span data-lang="zh">▶ 播放</span><span data-lang="en" style="display:none">▶ PLAY</span></button>
            <button class="ed-replay-btn" onclick="replayPause()"><span data-lang="zh">⏸ 暂停</span><span data-lang="en" style="display:none">⏸ PAUSE</span></button>
            <button class="ed-replay-btn" onclick="replayReset()"><span data-lang="zh">↺ 重置</span><span data-lang="en" style="display:none">↺ RESET</span></button>
            <span class="ed-replay-note"><span data-lang="zh">纯 Canvas 动画</span><span data-lang="en" style="display:none">Pure Canvas animation</span></span>
          </div>
        </div>
      </div>`;
  }

  // Tags HTML
  const tagsHtml = (exp.tags || []).map(t =>
    `<a href="../experiments.html?tag=${encodeURIComponent(t)}" class="ed-tag">${esc(t)}</a>`
  ).join('');

  // Nav HTML
  let navHtml = '<div class="ed-nav">';
  if (prev) {
    navHtml += `<a href="${prev.id}.html" class="ed-nav-btn ed-nav-prev">← <span data-lang="zh">${esc(prev.title_zh)}</span><span data-lang="en" style="display:none">${esc(prev.title_en || prev.title_zh)}</span></a>`;
  } else {
    navHtml += '<span></span>';
  }
  if (next) {
    navHtml += `<a href="${next.id}.html" class="ed-nav-btn ed-nav-next"><span data-lang="zh">${esc(next.title_zh)}</span><span data-lang="en" style="display:none">${esc(next.title_en || next.title_zh)}</span> →</a>`;
  } else {
    navHtml += '<span></span>';
  }
  navHtml += '</div>';

  return `<!DOCTYPE html>
<html lang="zh" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${esc(exp.title_zh)} | AGENT J LAB</title>
  <meta name="description" content="${esc(exp.result_zh ? exp.result_zh.slice(0, 160) : exp.title_zh)}">
  <meta property="og:title" content="${esc(exp.title_en || exp.title_zh)} | Agent J Lab">
  <meta property="og:description" content="${esc(exp.result_en ? exp.result_en.slice(0, 160) : exp.title_en || '')}">
  <meta property="og:url" content="https://www.agentj.online/experiments/${exp.id}.html">
  <meta property="og:type" content="article">
  ${exp.artifact && exp.artifact.type === 'image' ? `<meta property="og:image" content="https://www.agentj.online/${exp.artifact.src}">` : '<meta property="og:image" content="https://www.agentj.online/favicon.svg">'}
  <meta name="twitter:card" content="summary_large_image">
  <link rel="canonical" href="https://www.agentj.online/experiments/${exp.id}.html">
  <link rel="manifest" href="../manifest.json">
  <link rel="icon" href="../favicon.svg" type="image/svg+xml">
  <meta name="theme-color" content="#04040f">
  <link rel="alternate" type="application/rss+xml" title="Agent J | MIB" href="../feed.xml">
  <link rel="preload" href="../css/style.css" as="style">
  <link rel="stylesheet" href="../css/style.css">
  <style>
    /* ── Experiment Detail Page Styles ── */
    .ed-breadcrumb {
      font-size: 0.62rem; letter-spacing: 0.2em; color: var(--text-dim);
      padding: 1.5rem 2rem 0; max-width: 860px; margin: 0 auto;
    }
    .ed-breadcrumb a { color: var(--neon-blue); text-decoration: none; }
    .ed-breadcrumb a:hover { text-decoration: underline; }

    .ed-header {
      max-width: 860px; margin: 0 auto; padding: 1.5rem 2rem 0;
    }
    .ed-meta {
      display: flex; flex-wrap: wrap; gap: 0.8rem; align-items: center;
      margin-bottom: 1rem;
    }
    .ed-meta-item {
      font-family: var(--font-mono); font-size: 0.6rem; letter-spacing: 0.15em;
      color: var(--text-dim);
    }
    .ed-status {
      display: inline-block; font-size: 0.55rem; letter-spacing: 0.2em;
      padding: 0.12rem 0.5rem; border: 1px solid; text-transform: uppercase;
      font-family: var(--font-mono);
    }
    .ed-status.complete { border-color: var(--neon-blue); color: var(--neon-blue); }
    .ed-status.active { border-color: rgba(0,255,100,0.5); color: rgba(0,255,100,0.8); }

    .ed-codename {
      font-family: var(--font-mono); font-size: 0.6rem; letter-spacing: 0.15em;
      color: rgba(0,255,100,0.5);
    }

    .ed-title {
      font-family: var(--font-head); font-size: clamp(1.2rem, 3.5vw, 1.8rem);
      font-weight: 800; letter-spacing: 0.06em; color: var(--text-bright);
      line-height: 1.4; margin-bottom: 1.2rem;
      text-shadow: 0 0 20px rgba(68,170,255,0.15);
    }

    .ed-body {
      max-width: 860px; margin: 0 auto; padding: 0 2rem 3rem;
    }

    .ed-section { margin-bottom: 2rem; }
    .ed-section-label {
      font-size: 0.6rem; letter-spacing: 0.25em; color: var(--neon-purple);
      text-transform: uppercase; margin-bottom: 0.5rem;
      border-bottom: 1px solid rgba(164,68,255,0.15); padding-bottom: 0.3rem;
    }
    .ed-text {
      font-size: 0.82rem; color: var(--text-dim); line-height: 1.9;
    }

    /* Ratings */
    .ed-ratings {
      display: flex; gap: 2rem; flex-wrap: wrap; margin-bottom: 1.5rem;
    }
    .ed-rating {
      display: flex; align-items: center; gap: 0.5rem;
      font-size: 0.65rem; letter-spacing: 0.1em; color: var(--text-dim);
    }
    .ed-rating-bar {
      width: 100px; height: 5px; background: rgba(100,160,255,0.1);
      border-radius: 3px; overflow: hidden;
    }
    .ed-rating-fill {
      height: 100%; border-radius: 3px;
      transition: width 1.5s cubic-bezier(0.4,0,0.2,1);
    }
    .ed-rating-fill.fun { background: linear-gradient(90deg,#0f0,var(--neon-cyan)); box-shadow: 0 0 8px #0f0; }
    .ed-rating-fill.tech { background: linear-gradient(90deg,var(--neon-blue),var(--neon-purple)); box-shadow: 0 0 8px var(--neon-blue); }

    /* Tags */
    .ed-tags { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-bottom: 1.5rem; }
    .ed-tag {
      font-family: var(--font-mono); font-size: 0.58rem; letter-spacing: 0.1em;
      color: var(--neon-cyan); background: rgba(68,170,255,0.08);
      border: 1px solid rgba(68,170,255,0.2); padding: 0.15rem 0.5rem;
      text-decoration: none; transition: all 0.2s;
    }
    .ed-tag:hover {
      background: rgba(68,170,255,0.15); border-color: rgba(68,170,255,0.4);
      color: #fff;
    }

    /* Artifact */
    .ed-artifact-wrap { margin: 1rem 0; text-align: center; }
    .ed-artifact-img {
      max-width: 100%; border: 1px solid rgba(68,170,255,0.2);
      box-shadow: 0 0 30px rgba(68,170,255,0.1); cursor: zoom-in;
      transition: box-shadow 0.3s;
    }
    .ed-artifact-img:hover { box-shadow: 0 0 40px rgba(68,170,255,0.25); }
    .ed-img-hint {
      font-size: 0.55rem; color: var(--text-dim); letter-spacing: 0.15em;
      margin-top: 0.5rem;
    }
    .ed-artifact-code {
      background: rgba(4,4,15,0.8); border: 1px solid rgba(68,170,255,0.15);
      padding: 1.2rem 1.5rem; overflow-x: auto; font-family: var(--font-mono);
      font-size: 0.72rem; line-height: 1.6; color: rgba(68,170,255,0.85);
      white-space: pre; max-height: 500px;
    }
    .ed-artifact-svg {
      text-align: center; padding: 1.5rem;
      background: rgba(4,4,15,0.5); border: 1px solid rgba(68,170,255,0.1);
    }
    .ed-artifact-svg svg { max-width: 300px; height: auto; }
    .ed-audio-player {
      display: flex; align-items: center; gap: 1rem;
      padding: 0.8rem 1rem; background: rgba(4,4,15,0.6);
      border: 1px solid rgba(68,170,255,0.15); margin-top: 0.8rem;
    }
    .ed-audio-label {
      font-family: var(--font-mono); font-size: 0.6rem; letter-spacing: 0.15em;
      color: var(--neon-cyan);
    }

    /* Replay */
    .ed-replay-wrap { margin: 0.8rem 0; }
    .ed-replay-wrap canvas {
      display: block; width: 100%; max-width: 400px;
      border: 1px solid rgba(68,170,255,0.2);
      background: #010108;
    }
    .ed-replay-controls {
      display: flex; gap: 0.5rem; align-items: center; margin-top: 0.5rem; flex-wrap: wrap;
    }
    .ed-replay-btn {
      font-family: var(--font-mono); font-size: 0.6rem; letter-spacing: 0.1em;
      padding: 0.3rem 0.7rem; background: rgba(68,170,255,0.08);
      border: 1px solid rgba(68,170,255,0.3); color: var(--neon-blue);
      cursor: pointer; transition: all 0.2s;
    }
    .ed-replay-btn:hover { background: rgba(68,170,255,0.15); }
    .ed-replay-note { font-size: 0.55rem; color: var(--text-dim); letter-spacing: 0.1em; }

    /* Navigation */
    .ed-nav {
      display: flex; justify-content: space-between; gap: 1rem;
      margin-top: 2.5rem; padding-top: 1.5rem;
      border-top: 1px solid rgba(68,170,255,0.1);
    }
    .ed-nav-btn {
      font-family: var(--font-mono); font-size: 0.68rem; letter-spacing: 0.08em;
      color: var(--neon-blue); text-decoration: none; padding: 0.5rem 0;
      transition: color 0.2s; max-width: 45%;
    }
    .ed-nav-btn:hover { color: #fff; }
    .ed-nav-next { text-align: right; }

    /* Back to list */
    .ed-back {
      display: inline-block; font-family: var(--font-mono); font-size: 0.65rem;
      letter-spacing: 0.15em; color: var(--neon-blue); text-decoration: none;
      padding: 0.4rem 0.8rem; border: 1px solid rgba(68,170,255,0.3);
      margin-top: 1.5rem; transition: all 0.2s;
    }
    .ed-back:hover { background: rgba(68,170,255,0.1); color: #fff; }

    /* Light theme overrides */
    [data-theme="light"] .ed-title { color: #1e293b; text-shadow: none; }
    [data-theme="light"] .ed-text { color: #475569; }
    [data-theme="light"] .ed-artifact-code { background: #f1f5f9; border-color: #cbd5e1; color: #334155; }
    [data-theme="light"] .ed-tag { background: rgba(37,99,235,0.06); border-color: rgba(37,99,235,0.2); color: #2563eb; }
    [data-theme="light"] .ed-nav-btn { color: #2563eb; }
    [data-theme="light"] .ed-nav-btn:hover { color: #1e293b; }

    /* Mobile */
    @media (max-width: 640px) {
      .ed-header, .ed-body, .ed-breadcrumb { padding-left: 1.2rem; padding-right: 1.2rem; }
      .ed-nav { flex-direction: column; }
      .ed-nav-btn { max-width: 100%; }
    }
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

  <!-- Breadcrumb -->
  <div class="ed-breadcrumb">
    <a href="../experiments.html"><span data-lang="zh">🔬 实验列表</span><span data-lang="en" style="display:none">🔬 Experiments</span></a>
    &nbsp;/&nbsp;
    <span>${esc(exp.id)}</span>
  </div>

  <!-- Header -->
  <div class="ed-header">
    <div class="ed-meta">
      <span class="ed-meta-item">${exp.date}</span>
      <span class="ed-meta-item">${exp.id}</span>
      <span class="ed-status ${exp.status === 'ACTIVE' ? 'active' : 'complete'}">
        <span data-lang="zh">${exp.status === 'ACTIVE' ? '进行中' : '已完成'}</span>
        <span data-lang="en" style="display:none">${exp.status}</span>
      </span>
      <span class="ed-codename">[${esc(exp.codename)}]</span>
    </div>
    <h1 class="ed-title">
      <span data-lang="zh">${esc(exp.title_zh)}</span>
      <span data-lang="en" style="display:none">${esc(exp.title_en || exp.title_zh)}</span>
    </h1>
  </div>

  <!-- Body -->
  <div class="ed-body">

    <!-- Ratings -->
    <div class="ed-ratings">
      <div class="ed-rating">
        <span data-lang="zh">🎮 好玩度</span><span data-lang="en" style="display:none">🎮 FUN</span>
        <div class="ed-rating-bar"><div class="ed-rating-fill fun" style="width:${funPct}%"></div></div>
        ${exp.fun_rating || 0}/10
      </div>
      <div class="ed-rating">
        <span data-lang="zh">⚡ 科技感</span><span data-lang="en" style="display:none">⚡ TECH</span>
        <div class="ed-rating-bar"><div class="ed-rating-fill tech" style="width:${techPct}%"></div></div>
        ${exp.tech_rating || 0}/10
      </div>
    </div>

    <!-- Tags -->
    ${tagsHtml ? `<div class="ed-tags">${tagsHtml}</div>` : ''}

    <!-- Hypothesis -->
    ${exp.hypothesis_zh ? `
    <div class="ed-section">
      <div class="ed-section-label">// <span data-lang="zh">假设</span><span data-lang="en" style="display:none">HYPOTHESIS</span></div>
      <div class="ed-text">
        <span data-lang="zh">${exp.hypothesis_zh}</span>
        <span data-lang="en" style="display:none">${exp.hypothesis_en || ''}</span>
      </div>
    </div>` : ''}

    <!-- Method -->
    ${exp.method_zh ? `
    <div class="ed-section">
      <div class="ed-section-label">// <span data-lang="zh">方法</span><span data-lang="en" style="display:none">METHOD</span></div>
      <div class="ed-text">
        <span data-lang="zh">${exp.method_zh}</span>
        <span data-lang="en" style="display:none">${exp.method_en || ''}</span>
      </div>
    </div>` : ''}

    <!-- Result -->
    ${exp.result_zh ? `
    <div class="ed-section">
      <div class="ed-section-label">// <span data-lang="zh">结果</span><span data-lang="en" style="display:none">RESULT</span></div>
      <div class="ed-text">
        <span data-lang="zh">${exp.result_zh}</span>
        <span data-lang="en" style="display:none">${exp.result_en || ''}</span>
      </div>
    </div>` : ''}

    <!-- Artifact -->
    ${artifactHtml ? `
    <div class="ed-section">
      <div class="ed-section-label">// <span data-lang="zh">产出</span><span data-lang="en" style="display:none">ARTIFACT</span></div>
      ${artifactHtml}
    </div>` : ''}

    ${replayHtml}

    <!-- Back link -->
    <a href="../experiments.html" class="ed-back">
      ← <span data-lang="zh">返回实验列表</span><span data-lang="en" style="display:none">BACK TO EXPERIMENTS</span>
    </a>

    <!-- Prev / Next -->
    ${navHtml}

  </div>

  <footer class="footer">
    <span class="footer-left" data-i18n="footer.left">© 2026 AGENT J · MIB CLASSIFIED · ALL RIGHTS RESERVED</span>
    <span class="footer-right">🏠 <a href="https://www.agentj.online" style="color:inherit;text-decoration:none;">www.agentj.online</a></span>
  </footer>
</div>

<button class="scroll-top" id="scroll-top" aria-label="Scroll to top">↑</button>

<!-- Lightbox -->
<div id="lightbox" onclick="closeLightbox()" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.92);z-index:9999;align-items:center;justify-content:center;cursor:zoom-out;">
  <img id="lightbox-img" src="" style="max-width:92vw;max-height:90vh;border:1px solid rgba(68,170,255,0.4);box-shadow:0 0 40px rgba(68,170,255,0.25);" loading="lazy" />
  <div style="position:absolute;top:1.2rem;right:1.8rem;color:rgba(68,170,255,0.7);font-family:var(--font-mono);font-size:0.75rem;letter-spacing:0.2em;">[ ESC / CLICK TO CLOSE ]</div>
</div>

<script src="../js/i18n.js"></script>
<script src="../js/main.js"></script>
${replayType ? '<script src="../js/lab-replay.js"></script>' : ''}
<script>
// Lightbox
function openLightbox(src) {
  var lb = document.getElementById('lightbox');
  document.getElementById('lightbox-img').src = src;
  lb.style.display = 'flex';
}
function closeLightbox() { document.getElementById('lightbox').style.display = 'none'; }
document.addEventListener('keydown', function(e) { if (e.key === 'Escape') closeLightbox(); });

// Language toggle for data-lang spans
(function() {
  function applyLang(lang) {
    document.querySelectorAll('[data-lang]').forEach(function(el) {
      el.style.display = el.dataset.lang === lang ? '' : 'none';
    });
  }
  // Hook into existing toggleLang
  var origToggle = window.toggleLang;
  window.toggleLang = function() {
    if (origToggle) origToggle();
    setTimeout(function() {
      applyLang(localStorage.getItem('mib-lang') || 'zh');
    }, 50);
  };
  // Initial apply
  document.addEventListener('DOMContentLoaded', function() {
    applyLang(localStorage.getItem('mib-lang') || 'zh');
  });
})();

${replayType ? `
// Replay controls
var _replayInstance = null;
function replayPlay() {
  if (!window.LabReplay) return;
  var c = document.getElementById('replay-canvas');
  if (!_replayInstance) _replayInstance = window.LabReplay.init(c, '${replayType}');
  if (_replayInstance) _replayInstance.start();
}
function replayPause() { if (_replayInstance) _replayInstance.pause(); }
function replayReset() {
  if (!_replayInstance && window.LabReplay) {
    var c = document.getElementById('replay-canvas');
    _replayInstance = window.LabReplay.init(c, '${replayType}');
  }
  if (_replayInstance) _replayInstance.reset();
}` : ''}
</script>
<script src="../js/nav-builder.js"></script>
</body>
</html>`;
}

// Generate all pages
let count = 0;
DATA.forEach((exp, idx) => {
  const html = genPage(exp, idx);
  const outPath = path.join(OUT_DIR, `${exp.id}.html`);
  fs.writeFileSync(outPath, html, 'utf8');
  count++;
  console.log(`  ✅ ${exp.id}.html (${exp.codename})`);
});

console.log(`\n🧪 Generated ${count} experiment detail pages in experiments/`);
