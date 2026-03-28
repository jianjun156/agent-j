/* ── lab-replay.js — Agent J | Experiment Canvas Animations ── */
'use strict';

/**
 * Each animation: small canvas (400×300), plays on click, pause/reset controls.
 * Exposed as window.LabReplay.init(canvas, type) where type is:
 *   'double-slit' | 'chaos-bloom' | 'dragon-fold'
 */
window.LabReplay = (function() {

  /* ── Shared helpers ── */
  function clearCanvas(ctx, w, h) {
    ctx.fillStyle = '#010108';
    ctx.fillRect(0, 0, w, h);
  }

  /* ═══════════════════════════════════════════════════
     1. DOUBLE-SLIT — particle wave interference
  ═══════════════════════════════════════════════════ */
  function doubleSlit(canvas) {
    const ctx = canvas.getContext('2d');
    const W = canvas.width, H = canvas.height;
    const PARTICLES = 1200;
    let particles = [];
    let frame = 0;
    let raf = null;
    let running = false;

    const slitY = H * 0.38;
    const slit1X = W * 0.48 - 8;
    const slit2X = W * 0.48 + 8;
    const slitW = 3;
    const detectorY = H * 0.82;

    // Accumulation buffer
    let accumImg = null;
    const accumCanvas = document.createElement('canvas');
    accumCanvas.width = W;
    accumCanvas.height = H;
    const accumCtx = accumCanvas.getContext('2d');

    function spawnParticle() {
      const slit = Math.random() < 0.5 ? slit1X : slit2X;
      return {
        x: slit + (Math.random() - 0.5) * slitW,
        y: slitY,
        dx: (Math.random() - 0.5) * 0.6,
        dy: 0.8 + Math.random() * 0.4,
        life: 1,
        slit: slit,
        born: frame,
      };
    }

    function waveProb(x) {
      // Interference pattern probability — two-slit formula
      const d = slit2X - slit1X;
      const L = detectorY - slitY;
      const lambda = 14;
      const dx1 = x - slit1X;
      const dx2 = x - slit2X;
      const r1 = Math.sqrt(dx1 * dx1 + L * L);
      const r2 = Math.sqrt(dx2 * dx2 + L * L);
      const phase = (2 * Math.PI * (r1 - r2)) / lambda;
      return Math.cos(phase / 2) * Math.cos(phase / 2);
    }

    function drawBarrier() {
      ctx.strokeStyle = 'rgba(68,170,255,0.25)';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(0, slitY);
      ctx.lineTo(slit1X - slitW, slitY);
      ctx.moveTo(slit1X + slitW, slitY);
      ctx.lineTo(slit2X - slitW, slitY);
      ctx.moveTo(slit2X + slitW, slitY);
      ctx.lineTo(W, slitY);
      ctx.stroke();

      // Slit labels
      ctx.fillStyle = 'rgba(68,170,255,0.4)';
      ctx.font = '9px Space Mono, monospace';
      ctx.textAlign = 'center';
      ctx.fillText('SLIT 1', slit1X, slitY - 6);
      ctx.fillText('SLIT 2', slit2X, slitY - 6);

      // Detector screen
      ctx.strokeStyle = 'rgba(0,255,100,0.15)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(0, detectorY);
      ctx.lineTo(W, detectorY);
      ctx.stroke();
    }

    function drawSource() {
      // Source line
      ctx.strokeStyle = 'rgba(255,200,50,0.3)';
      ctx.lineWidth = 1;
      ctx.setLineDash([3, 5]);
      ctx.beginPath();
      ctx.moveTo(W * 0.48, H * 0.1);
      ctx.lineTo(W * 0.48, slitY);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = 'rgba(255,200,50,0.7)';
      ctx.beginPath();
      ctx.arc(W * 0.48, H * 0.12, 3, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = 'rgba(255,200,50,0.35)';
      ctx.font = '9px Space Mono, monospace';
      ctx.textAlign = 'center';
      ctx.fillText('SOURCE', W * 0.48, H * 0.08);
    }

    function drawLabels() {
      ctx.fillStyle = 'rgba(68,170,255,0.3)';
      ctx.font = '8px Space Mono, monospace';
      ctx.textAlign = 'left';
      ctx.fillText('// DOUBLE-SLIT INTERFERENCE', 6, 14);
      ctx.textAlign = 'right';
      ctx.fillText('FRAME ' + frame, W - 6, 14);
    }

    function tick() {
      if (!running) return;
      frame++;

      clearCanvas(ctx, W, H);

      // Draw accumulated hits first (dimmed)
      ctx.globalAlpha = 0.4;
      ctx.drawImage(accumCanvas, 0, 0);
      ctx.globalAlpha = 1;

      drawBarrier();
      drawSource();

      // Spawn
      if (frame % 2 === 0 && particles.length < 60) {
        particles.push(spawnParticle());
      }

      // Update + draw particles
      particles = particles.filter(p => {
        p.x += p.dx;
        p.y += p.dy;

        // Wave deflection after slit
        if (p.y > slitY + 5) {
          const prob = waveProb(p.x);
          p.dx += (Math.random() - 0.5) * 0.04 * (1 - prob);
        }

        if (p.y >= detectorY) {
          // Hit detector — accumulate
          accumCtx.fillStyle = 'rgba(0,255,100,0.35)';
          accumCtx.fillRect(Math.round(p.x) - 1, detectorY - 1, 2, 3);
          return false;
        }

        const alpha = 0.6 + Math.random() * 0.4;
        ctx.fillStyle = `rgba(255,230,100,${alpha})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, 1.5, 0, Math.PI * 2);
        ctx.fill();
        return true;
      });

      drawLabels();
      raf = requestAnimationFrame(tick);
    }

    return {
      start() {
        if (!running) { running = true; raf = requestAnimationFrame(tick); }
      },
      pause() {
        running = false;
        if (raf) cancelAnimationFrame(raf);
      },
      reset() {
        running = false;
        if (raf) cancelAnimationFrame(raf);
        frame = 0;
        particles = [];
        clearCanvas(accumCtx, W, H);
        clearCanvas(ctx, W, H);
        drawBarrier();
        drawSource();
        drawLabels();
      },
      isRunning() { return running; },
    };
  }


  /* ═══════════════════════════════════════════════════
     2. CHAOS-BLOOM — Lorenz attractor
  ═══════════════════════════════════════════════════ */
  function chaosBloom(canvas) {
    const ctx = canvas.getContext('2d');
    const W = canvas.width, H = canvas.height;
    let raf = null;
    let running = false;
    let points = [];

    // Lorenz parameters
    const sigma = 10, rho = 28, beta = 8 / 3;
    const dt = 0.005;
    const TRAILS = 3;  // number of attractors with slight offset

    for (let t = 0; t < TRAILS; t++) {
      points.push({
        x: 0.1 + t * 0.01, y: 0, z: 0,
        history: [],
        hue: 190 + t * 40,
      });
    }

    // Rotation
    let angle = 0;
    let step = 0;

    function project(x, y, z) {
      // Rotate around Y axis
      const cos = Math.cos(angle);
      const sin = Math.sin(angle);
      const rx = x * cos - z * sin;
      const rz = x * sin + z * cos;
      // Scale and center
      const scale = W / 80;
      return {
        px: W / 2 + rx * scale,
        py: H / 2 + y * scale * 0.7 - 8 * scale,
      };
    }

    function tick() {
      if (!running) return;
      step++;
      angle += 0.004;

      // Fade trail
      ctx.fillStyle = 'rgba(1, 1, 8, 0.06)';
      ctx.fillRect(0, 0, W, H);

      for (const p of points) {
        for (let i = 0; i < 5; i++) {
          const dx = sigma * (p.y - p.x);
          const dy = p.x * (rho - p.z) - p.y;
          const dz = p.x * p.y - beta * p.z;
          p.x += dx * dt;
          p.y += dy * dt;
          p.z += dz * dt;
          p.history.push({ x: p.x, y: p.y, z: p.z });
          if (p.history.length > 300) p.history.shift();
        }

        // Draw trail
        if (p.history.length < 2) continue;
        ctx.beginPath();
        const first = project(p.history[0].x, p.history[0].y, p.history[0].z);
        ctx.moveTo(first.px, first.py);
        for (let i = 1; i < p.history.length; i++) {
          const pp = project(p.history[i].x, p.history[i].y, p.history[i].z);
          const alpha = i / p.history.length;
          ctx.lineTo(pp.px, pp.py);
        }
        ctx.strokeStyle = `hsla(${p.hue + step * 0.05}, 80%, 65%, 0.5)`;
        ctx.lineWidth = 1;
        ctx.stroke();

        // Current point
        const cur = project(p.x, p.y, p.z);
        ctx.fillStyle = `hsla(${p.hue}, 100%, 80%, 0.9)`;
        ctx.beginPath();
        ctx.arc(cur.px, cur.py, 2.5, 0, Math.PI * 2);
        ctx.fill();
      }

      // Labels
      ctx.fillStyle = 'rgba(164,68,255,0.3)';
      ctx.font = '8px Space Mono, monospace';
      ctx.textAlign = 'left';
      ctx.fillText('// LORENZ ATTRACTOR · σ=' + sigma + ' ρ=' + rho + ' β=8/3', 6, 14);
      ctx.textAlign = 'right';
      ctx.fillStyle = 'rgba(100,160,255,0.3)';
      ctx.fillText('STEP ' + step, W - 6, 14);

      raf = requestAnimationFrame(tick);
    }

    return {
      start() {
        if (!running) { running = true; raf = requestAnimationFrame(tick); }
      },
      pause() {
        running = false;
        if (raf) cancelAnimationFrame(raf);
      },
      reset() {
        running = false;
        if (raf) cancelAnimationFrame(raf);
        step = 0;
        angle = 0;
        points = [];
        for (let t = 0; t < TRAILS; t++) {
          points.push({ x: 0.1 + t * 0.01, y: 0, z: 0, history: [], hue: 190 + t * 40 });
        }
        clearCanvas(ctx, W, H);
        ctx.fillStyle = 'rgba(164,68,255,0.3)';
        ctx.font = '8px Space Mono, monospace';
        ctx.textAlign = 'left';
        ctx.fillText('// LORENZ ATTRACTOR — PRESS PLAY', 6, 14);
      },
      isRunning() { return running; },
    };
  }


  /* ═══════════════════════════════════════════════════
     3. DRAGON-FOLD — Dragon curve fractal
  ═══════════════════════════════════════════════════ */
  function dragonFold(canvas) {
    const ctx = canvas.getContext('2d');
    const W = canvas.width, H = canvas.height;
    let raf = null;
    let running = false;
    let iteration = 0;
    let drawProgress = 0;
    let segments = [[{ x: W * 0.35, y: H * 0.5 }, { x: W * 0.65, y: H * 0.5 }]];
    let allSegments = [];

    function foldDragon(segs) {
      const newSegs = [];
      for (const seg of segs) {
        const [a, b] = seg;
        const mx = (a.x + b.x) / 2;
        const my = (a.y + b.y) / 2;
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        // Rotate 90° outward
        const pivot = { x: mx + dy / 2, y: my - dx / 2 };
        newSegs.push([a, pivot]);
        newSegs.push([b, pivot]);
      }
      return newSegs;
    }

    function buildDragon(n) {
      let s = [[{ x: W * 0.3, y: H * 0.5 }, { x: W * 0.7, y: H * 0.5 }]];
      for (let i = 0; i < n; i++) s = foldDragon(s);
      return s;
    }

    function tick() {
      if (!running) return;

      if (drawProgress >= allSegments.length) {
        // Advance to next iteration
        iteration++;
        if (iteration > 12) iteration = 1;
        allSegments = buildDragon(iteration);
        drawProgress = 0;

        clearCanvas(ctx, W, H);
        // Draw label
        ctx.fillStyle = 'rgba(0,255,100,0.3)';
        ctx.font = '8px Space Mono, monospace';
        ctx.textAlign = 'left';
        ctx.fillText('// DRAGON CURVE · FOLD ' + iteration, 6, 14);
      }

      // Draw batch of segments
      const batch = Math.max(1, Math.floor(allSegments.length / 60));
      const end = Math.min(drawProgress + batch, allSegments.length);
      for (let i = drawProgress; i < end; i++) {
        const seg = allSegments[i];
        const hue = (i / allSegments.length) * 300 + 120;
        ctx.strokeStyle = `hsla(${hue}, 80%, 65%, 0.7)`;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(seg[0].x, seg[0].y);
        ctx.lineTo(seg[1].x, seg[1].y);
        ctx.stroke();
      }
      drawProgress = end;

      ctx.fillStyle = 'rgba(100,160,255,0.3)';
      ctx.font = '8px Space Mono, monospace';
      ctx.textAlign = 'right';
      ctx.fillText(allSegments.length + ' segments', W - 6, 14);

      raf = requestAnimationFrame(tick);
    }

    return {
      start() {
        if (!running) {
          if (allSegments.length === 0) {
            iteration = 1;
            allSegments = buildDragon(iteration);
            clearCanvas(ctx, W, H);
          }
          running = true;
          raf = requestAnimationFrame(tick);
        }
      },
      pause() {
        running = false;
        if (raf) cancelAnimationFrame(raf);
      },
      reset() {
        running = false;
        if (raf) cancelAnimationFrame(raf);
        iteration = 0;
        drawProgress = 0;
        allSegments = [];
        clearCanvas(ctx, W, H);
        ctx.fillStyle = 'rgba(0,255,100,0.3)';
        ctx.font = '8px Space Mono, monospace';
        ctx.textAlign = 'left';
        ctx.fillText('// DRAGON CURVE — PRESS PLAY', 6, 14);
      },
      isRunning() { return running; },
    };
  }


  /* ═══════════════════════════════════════════════════
     Public API
  ═══════════════════════════════════════════════════ */
  function init(canvas, type) {
    const W = 400, H = 280;
    canvas.width = W;
    canvas.height = H;
    canvas.style.width = '100%';
    canvas.style.maxWidth = W + 'px';
    canvas.style.height = 'auto';
    canvas.style.display = 'block';
    canvas.style.background = '#010108';
    canvas.style.border = '1px solid rgba(68,170,255,0.2)';
    canvas.style.borderRadius = '4px';

    let anim;
    if (type === 'double-slit') anim = doubleSlit(canvas);
    else if (type === 'chaos-bloom') anim = chaosBloom(canvas);
    else if (type === 'dragon-fold') anim = dragonFold(canvas);
    else return null;

    anim.reset();
    return anim;
  }

  return { init };
})();
