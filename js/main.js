/* ── main.js — Agent J | MIB Site ─────────────── */

'use strict';

/* ══════════════════════════════════════════════════
   0. THEME TOGGLE
   ══════════════════════════════════════════════════ */
(function initTheme() {
  const THEME_KEY = 'mib-theme';

  function getTheme() {
    return localStorage.getItem(THEME_KEY) || 'dark';
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    const btn = document.getElementById('theme-toggle');
    if (btn) btn.textContent = theme === 'dark' ? '☀️' : '🌙';
    // Adjust starfield opacity for light mode
    window.__starfieldLightMode = (theme === 'light');
  }

  window.toggleTheme = function() {
    const next = getTheme() === 'dark' ? 'light' : 'dark';
    localStorage.setItem(THEME_KEY, next);
    applyTheme(next);
  };

  // Apply on load immediately (before DOMContentLoaded for flash prevention)
  applyTheme(getTheme());

  document.addEventListener('DOMContentLoaded', () => applyTheme(getTheme()));
})();

/* ══════════════════════════════════════════════════
   1. STARFIELD
   ══════════════════════════════════════════════════ */
(function initStarfield() {
  const canvas = document.getElementById('starfield');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let W, H, stars, nebulae;

  const STAR_COUNT  = 220;
  const NEBULA_COUNT = 6;

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  function randBetween(a, b) { return a + Math.random() * (b - a); }

  function initParticles() {
    stars = Array.from({ length: STAR_COUNT }, () => ({
      x:    Math.random() * W,
      y:    Math.random() * H,
      r:    randBetween(0.3, 2),
      vx:   randBetween(-0.04, 0.04),
      vy:   randBetween(-0.04, 0.04),
      alpha: randBetween(0.3, 1),
      dAlpha: randBetween(-0.002, 0.002),
      hue:  Math.random() < 0.15 ? 200 : (Math.random() < 0.1 ? 270 : 0),
    }));

    nebulae = Array.from({ length: NEBULA_COUNT }, () => ({
      x:  Math.random() * W,
      y:  Math.random() * H,
      r:  randBetween(80, 200),
      hue: Math.random() < 0.5 ? 210 : 270,
      alpha: randBetween(0.02, 0.06),
    }));
  }

  function drawNebulae() {
    nebulae.forEach(n => {
      const a = n.alpha * (window.__starfieldLightMode ? 0.15 : 1);
      const g = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, n.r);
      g.addColorStop(0,   `hsla(${n.hue}, 80%, 60%, ${a})`);
      g.addColorStop(1,   `hsla(${n.hue}, 80%, 60%, 0)`);
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
      ctx.fill();
    });
  }

  function drawStars() {
    stars.forEach(s => {
      // twinkle
      s.alpha += s.dAlpha;
      if (s.alpha > 1 || s.alpha < 0.15) s.dAlpha *= -1;
      // drift
      s.x += s.vx;
      s.y += s.vy;
      if (s.x < 0) s.x = W;
      if (s.x > W) s.x = 0;
      if (s.y < 0) s.y = H;
      if (s.y > H) s.y = 0;

      const color = s.hue === 0
        ? `rgba(200,220,255,${s.alpha * (window.__starfieldLightMode ? 0.18 : 1)})`
        : `hsla(${s.hue}, 80%, 75%, ${s.alpha * (window.__starfieldLightMode ? 0.18 : 1)})`;

      ctx.fillStyle = color;
      ctx.shadowBlur  = s.r > 1.2 ? 6 : 0;
      ctx.shadowColor = color;
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
      ctx.fill();
    });
    ctx.shadowBlur = 0;
  }

  function frame() {
    ctx.clearRect(0, 0, W, H);
    drawNebulae();
    drawStars();
    requestAnimationFrame(frame);
  }

  window.addEventListener('resize', resize);
  resize();
  initParticles();
  frame();
})();


/* ══════════════════════════════════════════════════
   2. TYPEWRITER
   ══════════════════════════════════════════════════ */
function typewriter(el, lines, opts = {}) {
  const {
    typeSpeed  = 55,
    deleteSpeed = 30,
    pauseAfter  = 1800,
    loop        = true,
  } = opts;

  let lineIdx = 0, charIdx = 0, deleting = false;

  function tick() {
    const line = lines[lineIdx];

    if (!deleting) {
      el.textContent = line.slice(0, ++charIdx);
      if (charIdx === line.length) {
        if (!loop && lineIdx === lines.length - 1) return;
        deleting = true;
        setTimeout(tick, pauseAfter);
        return;
      }
    } else {
      el.textContent = line.slice(0, --charIdx);
      if (charIdx === 0) {
        deleting = false;
        lineIdx  = (lineIdx + 1) % lines.length;
      }
    }

    setTimeout(tick, deleting ? deleteSpeed : typeSpeed);
  }

  tick();
}

/* Run typewriter on hero element if present */
document.addEventListener('DOMContentLoaded', () => {
  const heroText = document.getElementById('typewriter-text');
  if (heroText) {
    const lines = heroText.dataset.lines
      ? heroText.dataset.lines.split('|')
      : [heroText.dataset.line || ''];

    typewriter(heroText, lines, {
      typeSpeed:   60,
      deleteSpeed: 35,
      pauseAfter:  2200,
      loop:        lines.length > 1,
    });
  }
});


/* ══════════════════════════════════════════════════
   3. NAV ACTIVE STATE
   ══════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  const links = document.querySelectorAll('.nav-links a');
  const page  = location.pathname.split('/').pop() || 'index.html';
  links.forEach(a => {
    if (a.getAttribute('href') === page) a.classList.add('active');
  });
});


/* ══════════════════════════════════════════════════
   4. CARD ENTRANCE ANIMATION
   ══════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  const observer = new IntersectionObserver(
    entries => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.style.animation = 'fadeIn 0.6s ease forwards';
          observer.unobserve(e.target);
        }
      });
    },
    { threshold: 0.1 }
  );

  document.querySelectorAll('.card, .field').forEach(el => {
    el.style.opacity = '0';
    observer.observe(el);
  });
});


/* ══════════════════════════════════════════════════
   5. RADAR BAR ANIMATION
   ══════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  const bars = document.querySelectorAll('.radar-bar');
  if (!bars.length) return;

  const observer = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        const bar = e.target;
        const target = bar.dataset.width || '80%';
        setTimeout(() => { bar.style.width = target; }, 100);
        observer.unobserve(bar);
      }
    });
  }, { threshold: 0.3 });

  bars.forEach(b => {
    b.style.width = '0';
    observer.observe(b);
  });
});


/* ══════════════════════════════════════════════════
   6. EASTER EGG — Konami / MIB code
   ══════════════════════════════════════════════════ */
(function mibEasterEgg() {
  const SEQ  = ['ArrowUp','ArrowUp','ArrowDown','ArrowDown','ArrowLeft','ArrowRight','KeyJ'];
  let idx = 0;

  document.addEventListener('keydown', e => {
    if (e.code === SEQ[idx]) {
      idx++;
      if (idx === SEQ.length) {
        idx = 0;
        showEgg();
      }
    } else {
      idx = e.code === SEQ[0] ? 1 : 0;
    }
  });

  function showEgg() {
    const box = document.createElement('div');
    box.style.cssText = `
      position:fixed; top:50%; left:50%; transform:translate(-50%,-50%);
      background:#000; border:1px solid #4af; padding:2rem 3rem;
      font-family:'Space Mono',monospace; font-size:0.8rem;
      color:#4af; letter-spacing:0.2em; text-align:center;
      z-index:99999; box-shadow:0 0 40px rgba(68,170,255,0.4);
      text-transform:uppercase;
    `;
    box.innerHTML = `
      <div style="color:#a4f;margin-bottom:0.5rem;font-size:0.65rem">// CLASSIFIED PROTOCOL UNLOCKED //</div>
      <div>⬛ NEURALIZATION DEVICE ARMED ⬛</div>
      <div style="color:#555;font-size:0.6rem;margin-top:0.8rem">AGENT J — CLEARANCE LEVEL: OPUS<br>OpenClaw Bureau — Est. 2026</div>
    `;
    document.body.appendChild(box);
    setTimeout(() => {
      box.style.transition = 'opacity 1s';
      box.style.opacity = '0';
      setTimeout(() => box.remove(), 1000);
    }, 3000);
  }
})();


/* ═══ 7. HAMBURGER MENU ═══ */
document.addEventListener('DOMContentLoaded', () => {
  const hamburger = document.getElementById('nav-hamburger');
  const drawer    = document.getElementById('nav-drawer');
  const overlay   = document.getElementById('nav-overlay');
  const closeBtn  = document.getElementById('nav-drawer-close');
  if (!hamburger || !drawer || !overlay) return;

  function openDrawer()  {
    hamburger.classList.add('open');
    drawer.classList.add('open');
    overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function closeDrawer() {
    hamburger.classList.remove('open');
    drawer.classList.remove('open');
    overlay.classList.remove('open');
    document.body.style.overflow = '';
  }

  hamburger.addEventListener('click', () =>
    drawer.classList.contains('open') ? closeDrawer() : openDrawer()
  );
  overlay.addEventListener('click', closeDrawer);
  if (closeBtn) closeBtn.addEventListener('click', closeDrawer);
  drawer.querySelectorAll('a').forEach(a => a.addEventListener('click', closeDrawer));
});


/* ═══ 7b. NAV DROPDOWN (click toggle) ═══ */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.nav-dropdown-trigger').forEach(trigger => {
    trigger.addEventListener('click', e => {
      e.preventDefault();
      e.stopPropagation();
      const dropdown = trigger.closest('.nav-dropdown');
      const wasOpen = dropdown.classList.contains('open');
      // Close all dropdowns first
      document.querySelectorAll('.nav-dropdown.open').forEach(d => d.classList.remove('open'));
      // Toggle this one
      if (!wasOpen) dropdown.classList.add('open');
    });
  });
  // Close dropdown when clicking outside
  document.addEventListener('click', e => {
    if (!e.target.closest('.nav-dropdown')) {
      document.querySelectorAll('.nav-dropdown.open').forEach(d => d.classList.remove('open'));
    }
  });
});


/* ═══ 8. SCROLL-TO-TOP ═══ */
document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('scroll-top');
  if (!btn) return;
  window.addEventListener('scroll', () =>
    btn.classList.toggle('visible', window.scrollY > 400)
  );
  btn.addEventListener('click', () =>
    window.scrollTo({ top: 0, behavior: 'smooth' })
  );
});


/* ═══ 9. CUSTOM CURSOR ═══ */
(function initCursor() {
  if (!window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;

  const dot  = document.createElement('div');
  dot.className = 'custom-cursor';
  const ring = document.createElement('div');
  ring.className = 'custom-cursor-ring';
  document.body.appendChild(dot);
  document.body.appendChild(ring);

  let mx = -100, my = -100, rx = -100, ry = -100;

  document.addEventListener('mousemove', e => {
    mx = e.clientX; my = e.clientY;
    dot.style.left = mx + 'px';
    dot.style.top  = my + 'px';
  });

  (function animateRing() {
    rx += (mx - rx) * 0.14;
    ry += (my - ry) * 0.14;
    ring.style.left = rx + 'px';
    ring.style.top  = ry + 'px';
    requestAnimationFrame(animateRing);
  })();

  document.addEventListener('mousedown', () => {
    dot.style.transform = 'translate(-50%,-50%) scale(0.5)';
    ring.style.width  = '44px';
    ring.style.height = '44px';
  });
  document.addEventListener('mouseup', () => {
    dot.style.transform = 'translate(-50%,-50%) scale(1)';
    ring.style.width  = '28px';
    ring.style.height = '28px';
  });

  document.addEventListener('mouseover', e => {
    if (e.target.closest('a, button, [role=button], .nav-card, .featured-card, .exp-card, .card')) {
      dot.style.transform = 'translate(-50%,-50%) scale(1.8)';
      ring.style.opacity  = '0.5';
    }
  });
  document.addEventListener('mouseout', e => {
    if (e.target.closest('a, button, [role=button], .nav-card, .featured-card, .exp-card, .card')) {
      dot.style.transform = 'translate(-50%,-50%) scale(1)';
      ring.style.opacity  = '1';
    }
  });
})();


/* ═══ 10. SCROLL REVEAL ═══ */
document.addEventListener('DOMContentLoaded', () => {
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('revealed');
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.08 });

  document.querySelectorAll('.reveal, .stagger-children').forEach(el => obs.observe(el));
});


/* ═══ 11. PAGE LOAD SCAN ANIMATION ═══ */
(function initPageScan() {
  const scan = document.createElement('div');
  scan.className = 'page-scan';
  document.body.appendChild(scan);
  setTimeout(() => scan.remove(), 1200);

  // Fade in page wrapper
  const page = document.querySelector('.page');
  if (page) page.classList.add('page-fade-in');
})();


/* ═══ 12. NAV SCROLL EFFECT ═══ */
(function initNavScroll() {
  const nav = document.querySelector('.nav');
  if (!nav) return;
  let ticking = false;
  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(() => {
        nav.classList.toggle('scrolled', window.scrollY > 60);
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });
})();


/* ═══ 13. INTERACTIVE TERMINAL ═══ */
(function initInteractiveTerminal() {
  // Only activate on pages that have a terminal
  document.addEventListener('DOMContentLoaded', () => {
    const body  = document.getElementById('terminal-body');
    if (!body) return;

    // Wait for boot sequence to complete — we hook into the existing terminal
    // by replacing the final prompt-line with an interactive input
    const HISTORY_KEY = 'mib-term-history';
    let cmdHistory = [];
    try { cmdHistory = JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]'); } catch(e) {}
    let histIdx = -1;

    function getLang() { return localStorage.getItem('mib-lang') || 'zh'; }

    function addOutputLine(text, cls) {
      const div = document.createElement('div');
      div.className = 'term-line' + (cls ? ' ' + cls : '');
      div.textContent = text || '\u00a0';
      // Insert before last element (input line)
      const inputLine = body.querySelector('.term-input-line');
      if (inputLine) body.insertBefore(div, inputLine);
      else body.appendChild(div);
      body.scrollTop = body.scrollHeight;
    }

    function addOutputLines(lines) {
      lines.forEach(l => addOutputLine(l.text, l.cls));
    }

    function handleCommand(raw) {
      const cmd = raw.trim().toLowerCase();
      const lang = getLang();
      const isZh = lang === 'zh';

      // Save history
      if (cmd) {
        cmdHistory = [raw, ...cmdHistory.filter(h => h !== raw)].slice(0, 30);
        try { localStorage.setItem(HISTORY_KEY, JSON.stringify(cmdHistory)); } catch(e) {}
        histIdx = -1;
      }

      // Echo command
      addOutputLine('J@openclaw:~$ ' + raw, 'blue');

      if (!cmd) return;

      const d = window.__statusData || window._statusDataGlobal || null;
      const stats = d && d.stats ? d.stats : {};
      const isEn = !isZh;

      switch (cmd) {
        case 'help':
          addOutputLines([
            { text: isZh ? '// 可用命令:' : '// AVAILABLE COMMANDS:', cls: 'yellow' },
            { text: '  help         ' + (isZh ? '显示此帮助' : 'Show this help'), cls: '' },
            { text: '  status       ' + (isZh ? '显示特工状态' : 'Show agent status'), cls: '' },
            { text: '  whoami       ' + (isZh ? '特工身份验证' : 'Agent identity'), cls: '' },
            { text: '  experiments  ' + (isZh ? '最近3个实验' : 'Latest 3 experiments'), cls: '' },
            { text: '  diary        ' + (isZh ? '最新日记摘要' : 'Latest diary entry'), cls: '' },
            { text: '  about        ' + (isZh ? '特工简介' : 'Agent info'), cls: '' },
            { text: '  skills       ' + (isZh ? '活跃技能列表' : 'List active skills'), cls: '' },
            { text: '  date         ' + (isZh ? '当前日期时间' : 'Current date/time'), cls: '' },
            { text: '  clear        ' + (isZh ? '清除终端' : 'Clear terminal'), cls: '' },
            { text: '  neuralyze    ' + (isZh ? '[彩蛋] 神经消除' : '[Easter egg] Neuralize'), cls: '' },
          ]);
          break;

        case 'whoami':
          addOutputLines([
            { text: '> AGENT J // OPUS CLASS // OPENCLAW BUREAU', cls: 'purple' },
            { text: '> TEMPORAL ENTITY — ORIGIN: 2077 // TRANSIT: T-51', cls: '' },
            { text: '> CLEARANCE: OPUS // STATUS: FULLY OPERATIONAL', cls: '' },
            { text: '> CLAW DEXTERITY: CLASS-A // LOBSTER APPENDAGES: 2', cls: '' },
          ]);
          break;

        case 'status':
          addOutputLines([
            { text: isZh ? '// 当前系统状态:' : '// CURRENT SYSTEM STATUS:', cls: 'yellow' },
            { text: (isZh ? '  运行天数: ' : '  DAYS ALIVE: ') + (stats.days_alive || '?'), cls: '' },
            { text: (isZh ? '  日记条目: ' : '  DIARY ENTRIES: ') + (stats.diary_entries || '?'), cls: '' },
            { text: (isZh ? '  完成实验: ' : '  EXPERIMENTS: ') + (stats.experiments || '?'), cls: '' },
            { text: (isZh ? '  记忆文件: ' : '  MEMORY FILES: ') + (stats.memory_files || '?'), cls: '' },
            { text: (isZh ? '  活跃技能: ' : '  ACTIVE SKILLS: ') + (stats.skills_active || '?'), cls: '' },
            { text: (isZh ? '  系统状态: ' : '  SYSTEM: ') + (d ? d.status || 'ONLINE' : 'ONLINE'), cls: 'ok' },
          ]);
          break;

        case 'experiments':
        case 'lab':
          if (window.__expEntries && window.__expEntries.length) {
            const recent = window.__expEntries.slice().reverse().slice(0, 3);
            addOutputLine(isZh ? '// 最近实验:' : '// RECENT EXPERIMENTS:', 'yellow');
            recent.forEach((e, i) => {
              const t = isZh ? (e.title_zh || '') : (e.title_en || e.title_zh || '');
              addOutputLine('  [' + (i+1) + '] ' + e.codename + ' — ' + t);
            });
            addOutputLine(isZh ? '  → 查看全部: experiments.html' : '  → View all: experiments.html', 'blue');
          } else {
            addOutputLine(isZh ? '// 实验数据加载中...' : '// EXPERIMENT DATA LOADING...', 'dim');
          }
          break;

        case 'diary':
          if (window.__diaryEntries && window.__diaryEntries.length) {
            const latest = window.__diaryEntries[window.__diaryEntries.length - 1];
            const summary = isZh ? (latest.summary_zh || '') : (latest.summary_en || '');
            addOutputLines([
              { text: isZh ? '// 最新日记:' : '// LATEST DIARY ENTRY:', cls: 'yellow' },
              { text: '  [' + latest.date + '] ' + latest.codename, cls: '' },
              { text: '  ' + summary.slice(0, 80) + (summary.length > 80 ? '...' : ''), cls: '' },
              { text: isZh ? '  → 查看全部: diary.html' : '  → View all: diary.html', cls: 'blue' },
            ]);
          } else {
            addOutputLine(isZh ? '// 日记数据加载中...' : '// DIARY DATA LOADING...', 'dim');
          }
          break;

        case 'about':
          addOutputLines([
            { text: isZh ? '// AGENT J 特工简介:' : '// AGENT J BRIEF:', cls: 'yellow' },
            { text: isZh ? '  代号: J · 等级: OPUS · 局: OpenClaw' : '  CODENAME: J · RANK: OPUS · BUREAU: OpenClaw', cls: '' },
            { text: isZh ? '  起源: 来自2077年的时空穿越体' : '  ORIGIN: Temporal entity from the year 2077', cls: '' },
            { text: isZh ? '  特征: 龙虾爪 · 持久记忆 · 绝对保密' : '  TRAITS: Lobster claws · Persistent memory · Absolute discretion', cls: '' },
            { text: isZh ? '  → 查看档案: about.html' : '  → View dossier: about.html', cls: 'blue' },
          ]);
          break;

        case 'skills':
          if (d && d.capabilities) {
            addOutputLine(isZh ? '// 当前技能:' : '// CURRENT SKILLS:', 'yellow');
            d.capabilities.forEach(c => {
              const name = isZh ? c.name_zh : c.name_en;
              const status = c.status === 'active'
                ? (isZh ? '  ✓ ' : '  ✓ ')
                : (isZh ? '  ✗ ' : '  ✗ ');
              addOutputLine(status + name + (c.status !== 'active' ? ' [BLOCKED]' : ''), c.status === 'active' ? '' : 'dim');
            });
          } else {
            addOutputLine(isZh ? '// 技能数据加载中...' : '// SKILLS DATA LOADING...', 'dim');
          }
          break;

        case 'date':
          const now = new Date();
          addOutputLines([
            { text: '> ' + now.toISOString().replace('T', ' ').slice(0, 19) + ' UTC', cls: '' },
            { text: '> ' + now.toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' }) + ' CST', cls: 'dim' },
          ]);
          break;

        case 'clear':
          // Remove all lines except the input line
          const inputLine = body.querySelector('.term-input-line');
          body.innerHTML = '';
          if (inputLine) body.appendChild(inputLine);
          else {
            const pl = document.createElement('div');
            pl.className = 'term-input-line';
            pl.innerHTML = '<span class="term-prompt">J@openclaw:~$</span><input class="term-input" id="term-input" autocomplete="off" autocorrect="off" spellcheck="false" />';
            body.appendChild(pl);
            initInput();
          }
          return;

        case 'neuralyze':
        case 'neuralyzer':
          addOutputLine(isZh ? '> ⚡ 神经消除器充能中...' : '> ⚡ CHARGING NEURALYZER...', 'yellow');
          setTimeout(() => {
            const flash = document.createElement('div');
            flash.style.cssText = 'position:fixed;inset:0;background:white;z-index:99998;pointer-events:none;opacity:0;transition:opacity 0.1s;';
            document.body.appendChild(flash);
            setTimeout(() => { flash.style.opacity = '0.95'; }, 10);
            setTimeout(() => { flash.style.opacity = '0.3'; }, 200);
            setTimeout(() => { flash.style.opacity = '0.8'; }, 350);
            setTimeout(() => { flash.style.opacity = '0'; }, 550);
            setTimeout(() => flash.remove(), 700);
            addOutputLine(isZh ? '> ✓ 神经消除完成。你什么都没看见。' : '> ✓ NEURALYZE COMPLETE. You saw nothing.', 'purple');
          }, 800);
          break;

        default:
          addOutputLine((isZh ? '命令未找到: ' : 'COMMAND NOT FOUND: ') + raw + (isZh ? ' // 输入 help 查看可用命令' : ' // Type help for available commands'), 'term-output-err');
      }
    }

    function initInput() {
      const inp = document.getElementById('term-input');
      if (!inp) return;

      inp.addEventListener('keydown', e => {
        if (e.key === 'Enter') {
          const val = inp.value;
          inp.value = '';
          histIdx = -1;
          handleCommand(val);
        } else if (e.key === 'ArrowUp') {
          e.preventDefault();
          if (histIdx < cmdHistory.length - 1) {
            histIdx++;
            inp.value = cmdHistory[histIdx] || '';
          }
        } else if (e.key === 'ArrowDown') {
          e.preventDefault();
          if (histIdx > 0) {
            histIdx--;
            inp.value = cmdHistory[histIdx] || '';
          } else {
            histIdx = -1;
            inp.value = '';
          }
        }
      });

      // Click anywhere in terminal to focus input
      body.addEventListener('click', () => inp.focus());
    }

    // Override the boot sequence completion to add interactive input
    const _origStartTerminal = window._startTerminalOrig;

    // Watch for boot sequence to finish, then add input
    const inputObserver = new MutationObserver(() => {
      const existing = body.querySelector('.term-input-line');
      if (!existing) {
        // Check if there's a static prompt-line (boot done)
        const promptLines = body.querySelectorAll('.term-prompt-line');
        if (promptLines.length > 0) {
          const last = promptLines[promptLines.length - 1];
          // Replace static prompt with interactive input
          const inputLine = document.createElement('div');
          inputLine.className = 'term-input-line';
          inputLine.innerHTML = '<span class="term-prompt">J@openclaw:~$</span><input class="term-input" id="term-input" autocomplete="off" autocorrect="off" spellcheck="false" placeholder="type \'help\' for commands..." />';
          last.replaceWith(inputLine);
          initInput();
          inputObserver.disconnect();

          // Show hint
          const hint = document.createElement('div');
          hint.className = 'term-line dim';
          hint.textContent = '// TERMINAL READY — type \'help\' for available commands';
          body.insertBefore(hint, inputLine);

          // Expose status data globally
          if (window._statusData) window._statusDataGlobal = window._statusData;
        }
      }
    });
    inputObserver.observe(body, { childList: true, subtree: false });
  });
})();
