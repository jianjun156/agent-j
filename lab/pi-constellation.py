import math
import random
from pathlib import Path

W, H = 1200, 800
PLOT_X0, PLOT_Y0, PLOT_W, PLOT_H = 70, 90, 520, 520
CURVE_X0, CURVE_Y0, CURVE_W, CURVE_H = 660, 120, 460, 400
HIST_X0, HIST_Y0, HIST_W, HIST_H = 660, 570, 460, 140
N = 20000
SEED = 5212026
random.seed(SEED)

points = []
inside = 0
pi_estimates = []
checkpoints = []
cp_step = 100
for i in range(1, N + 1):
    x = random.random()
    y = random.random()
    hit = x * x + y * y <= 1.0
    if hit:
        inside += 1
    est = 4 * inside / i
    points.append((x, y, hit))
    if i % cp_step == 0 or i == 1:
        pi_estimates.append(est)
        checkpoints.append(i)

final_est = pi_estimates[-1]
error = abs(final_est - math.pi)
inside_ratio = inside / N
outside = N - inside

# Bucket errors by 1000-sample windows for mini histogram.
window = 1000
error_bins = []
for start in range(0, len(pi_estimates), window // cp_step):
    chunk = pi_estimates[start:start + window // cp_step]
    if chunk:
        avg_err = sum(abs(v - math.pi) for v in chunk) / len(chunk)
        error_bins.append(avg_err)

# SVG helpers

def esc(s: str) -> str:
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
             .replace('"', '&quot;'))

svg = []
append = svg.append
append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
append('<defs>')
append('<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
       '<stop offset="0%" stop-color="#050816"/>'
       '<stop offset="55%" stop-color="#0b1230"/>'
       '<stop offset="100%" stop-color="#16051d"/>'
       '</linearGradient>')
append('<linearGradient id="curveGrad" x1="0" y1="0" x2="1" y2="0">'
       '<stop offset="0%" stop-color="#4af"/>'
       '<stop offset="50%" stop-color="#72ffd2"/>'
       '<stop offset="100%" stop-color="#ff5ad9"/>'
       '</linearGradient>')
append('<filter id="glow"><feGaussianBlur stdDeviation="2.4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
append('</defs>')
append('<rect width="100%" height="100%" fill="url(#bg)"/>')

# subtle stars
for i in range(120):
    sx = (i * 97) % W
    sy = (i * 173) % H
    r = 0.6 + (i % 4) * 0.2
    op = 0.15 + (i % 5) * 0.08
    append(f'<circle cx="{sx}" cy="{sy}" r="{r}" fill="#9ed0ff" opacity="{op:.2f}"/>')

append('<text x="70" y="48" fill="#e8f3ff" font-family="monospace" font-size="28" font-weight="700">PI CONSTELLATION</text>')
append('<text x="72" y="72" fill="#79a7d8" font-family="monospace" font-size="13">Monte Carlo estimate of π from 20,000 random points — pure Python, zero deps</text>')

# Main quarter-circle plot
append(f'<rect x="{PLOT_X0}" y="{PLOT_Y0}" width="{PLOT_W}" height="{PLOT_H}" rx="8" fill="rgba(0,0,0,0.18)" stroke="rgba(90,160,255,0.25)"/>'.replace('rgba', 'rgb'))
# grid
for i in range(6):
    x = PLOT_X0 + i * PLOT_W / 5
    y = PLOT_Y0 + i * PLOT_H / 5
    append(f'<line x1="{x:.1f}" y1="{PLOT_Y0}" x2="{x:.1f}" y2="{PLOT_Y0 + PLOT_H}" stroke="#28466f" opacity="0.35"/>')
    append(f'<line x1="{PLOT_X0}" y1="{y:.1f}" x2="{PLOT_X0 + PLOT_W}" y2="{y:.1f}" stroke="#28466f" opacity="0.35"/>')

# quarter circle arc and axes
append(f'<path d="M {PLOT_X0},{PLOT_Y0 + PLOT_H} A {PLOT_W},{PLOT_H} 0 0 1 {PLOT_X0 + PLOT_W},{PLOT_Y0}" fill="none" stroke="#a06dff" stroke-width="2.2" opacity="0.9"/>')
append(f'<line x1="{PLOT_X0}" y1="{PLOT_Y0 + PLOT_H}" x2="{PLOT_X0 + PLOT_W}" y2="{PLOT_Y0 + PLOT_H}" stroke="#8dbfff" opacity="0.8"/>')
append(f'<line x1="{PLOT_X0}" y1="{PLOT_Y0 + PLOT_H}" x2="{PLOT_X0}" y2="{PLOT_Y0}" stroke="#8dbfff" opacity="0.8"/>')

for idx, (x, y, hit) in enumerate(points):
    px = PLOT_X0 + x * PLOT_W
    py = PLOT_Y0 + PLOT_H - y * PLOT_H
    color = '#6fffe9' if hit else '#ff6bd6'
    op = 0.38 if hit else 0.22
    if idx % 3 == 0:
        append(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="1.15" fill="{color}" opacity="{op:.2f}"/>')

for i in range(6):
    val = i / 5
    x = PLOT_X0 + i * PLOT_W / 5
    y = PLOT_Y0 + PLOT_H - i * PLOT_H / 5
    append(f'<text x="{x-8:.1f}" y="{PLOT_Y0 + PLOT_H + 24}" fill="#8cb3dc" font-family="monospace" font-size="11">{val:.1f}</text>')
    append(f'<text x="{PLOT_X0-28}" y="{y+4:.1f}" fill="#8cb3dc" font-family="monospace" font-size="11">{val:.1f}</text>')

append(f'<text x="{PLOT_X0}" y="{PLOT_Y0 - 18}" fill="#d8e7ff" font-family="monospace" font-size="16">Quarter Circle Hit Test</text>')

# Convergence chart
append(f'<rect x="{CURVE_X0}" y="{CURVE_Y0}" width="{CURVE_W}" height="{CURVE_H}" rx="8" fill="#060b1a" stroke="#2e4f7b" opacity="0.95"/>')
for i in range(6):
    y = CURVE_Y0 + i * CURVE_H / 5
    append(f'<line x1="{CURVE_X0}" y1="{y:.1f}" x2="{CURVE_X0 + CURVE_W}" y2="{y:.1f}" stroke="#28466f" opacity="0.35"/>')
for i in range(5):
    x = CURVE_X0 + i * CURVE_W / 4
    append(f'<line x1="{x:.1f}" y1="{CURVE_Y0}" x2="{x:.1f}" y2="{CURVE_Y0 + CURVE_H}" stroke="#28466f" opacity="0.35"/>')

min_y, max_y = 2.8, 3.5
path_parts = []
for n, est in zip(checkpoints, pi_estimates):
    px = CURVE_X0 + (n / N) * CURVE_W
    py = CURVE_Y0 + CURVE_H * (1 - (est - min_y) / (max_y - min_y))
    path_parts.append(('M' if not path_parts else 'L') + f' {px:.2f} {py:.2f}')
append(f'<path d="{" ".join(path_parts)}" fill="none" stroke="url(#curveGrad)" stroke-width="2.4" filter="url(#glow)"/>')
py_pi = CURVE_Y0 + CURVE_H * (1 - (math.pi - min_y) / (max_y - min_y))
append(f'<line x1="{CURVE_X0}" y1="{py_pi:.2f}" x2="{CURVE_X0 + CURVE_W}" y2="{py_pi:.2f}" stroke="#f7d46a" stroke-dasharray="6 5" opacity="0.9"/>')
append(f'<text x="{CURVE_X0 + 10}" y="{py_pi - 8:.2f}" fill="#f7d46a" font-family="monospace" font-size="12">π = 3.14159265...</text>')
for tick in [0, 5000, 10000, 15000, 20000]:
    x = CURVE_X0 + (tick / N) * CURVE_W
    append(f'<text x="{x - 18:.1f}" y="{CURVE_Y0 + CURVE_H + 24}" fill="#8cb3dc" font-family="monospace" font-size="11">{tick}</text>')
for val in [2.8, 3.0, 3.2, 3.4, 3.5]:
    y = CURVE_Y0 + CURVE_H * (1 - (val - min_y) / (max_y - min_y))
    append(f'<text x="{CURVE_X0 - 42}" y="{y + 4:.1f}" fill="#8cb3dc" font-family="monospace" font-size="11">{val:.1f}</text>')
append(f'<text x="{CURVE_X0}" y="{CURVE_Y0 - 18}" fill="#d8e7ff" font-family="monospace" font-size="16">Convergence of 4 × inside / total</text>')

# Error histogram bars
append(f'<rect x="{HIST_X0}" y="{HIST_Y0}" width="{HIST_W}" height="{HIST_H}" rx="8" fill="#060b1a" stroke="#2e4f7b" opacity="0.95"/>')
append(f'<text x="{HIST_X0}" y="{HIST_Y0 - 16}" fill="#d8e7ff" font-family="monospace" font-size="16">Average absolute error by 1k-sample window</text>')
max_err = max(error_bins)
bar_gap = 8
bar_w = (HIST_W - bar_gap * (len(error_bins) + 1)) / len(error_bins)
for i, errv in enumerate(error_bins):
    bh = (errv / max_err) * (HIST_H - 34)
    x = HIST_X0 + bar_gap + i * (bar_w + bar_gap)
    y = HIST_Y0 + HIST_H - 20 - bh
    hue = 190 - i * 8
    append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_w:.2f}" height="{bh:.2f}" fill="hsl({hue},85%,62%)" opacity="0.88"/>')
    append(f'<text x="{x + bar_w/2 - 10:.1f}" y="{HIST_Y0 + HIST_H - 5}" fill="#89afd7" font-family="monospace" font-size="10">{i+1}k</text>')

# Summary panel
panel_x, panel_y = 70, 650
append(f'<rect x="{panel_x}" y="{panel_y}" width="520" height="110" rx="10" fill="#07101f" stroke="#2d4b75" opacity="0.96"/>')
summary = [
    f'Seed              : {SEED}',
    f'Inside / Outside  : {inside} / {outside}',
    f'Inside ratio      : {inside_ratio:.6f}',
    f'π estimate        : {final_est:.8f}',
    f'Absolute error    : {error:.8f}',
    f'Error in percent  : {error / math.pi * 100:.4f}%'
]
for i, line in enumerate(summary):
    append(f'<text x="{panel_x + 22}" y="{panel_y + 28 + i*14}" fill="#c9def8" font-family="monospace" font-size="13">{esc(line)}</text>')
append(f'<text x="{panel_x + 320}" y="{panel_y + 92}" fill="#6ef4d7" font-family="monospace" font-size="15">π emerges from randomness.</text>')

append('</svg>')

out = Path(__file__).with_suffix('.svg')
out.write_text('\n'.join(svg), encoding='utf-8')
print(f'Wrote {out} | estimate={final_est:.8f} error={error:.8f}')
