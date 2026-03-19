/* ── main.js — Agent J | MIB Site ─────────────── */

'use strict';

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
      const g = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, n.r);
      g.addColorStop(0,   `hsla(${n.hue}, 80%, 60%, ${n.alpha})`);
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
        ? `rgba(200,220,255,${s.alpha})`
        : `hsla(${s.hue}, 80%, 75%, ${s.alpha})`;

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
