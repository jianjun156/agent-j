import math
from pathlib import Path

W, H = 1200, 800
MARGIN_X = 90
BASE_Y = H / 2
AMPLITUDE = 230
SAMPLES = 17
SUBDIVISIONS = 4

raw = []
for i in range(SAMPLES):
    t = i / (SAMPLES - 1)
    x = MARGIN_X + t * (W - 2 * MARGIN_X)
    y = BASE_Y + (
        math.sin(t * math.pi * 2.2) * 0.9
        + math.cos(t * math.pi * 5.3) * 0.22
        + math.sin(t * math.pi * 9.1) * 0.08
    ) * AMPLITUDE
    raw.append((x, y))


def chaikin(points, iterations=1):
    pts = points[:]
    for _ in range(iterations):
        out = [pts[0]]
        for i in range(len(pts)-1):
            x1, y1 = pts[i]
            x2, y2 = pts[i+1]
            q = (0.75*x1 + 0.25*x2, 0.75*y1 + 0.25*y2)
            r = (0.25*x1 + 0.75*x2, 0.25*y1 + 0.75*y2)
            out.extend([q, r])
        out.append(pts[-1])
        pts = out
    return pts

smooth = chaikin(raw, SUBDIVISIONS)

def points_str(points):
    return ' '.join(f'{x:.2f},{y:.2f}' for x, y in points)

# metrics
raw_segments = len(raw)-1
smooth_points = len(smooth)
# approximate length
def poly_len(points):
    total = 0.0
    for (x1,y1),(x2,y2) in zip(points, points[1:]):
        total += math.hypot(x2-x1, y2-y1)
    return total
raw_len = poly_len(raw)
smooth_len = poly_len(smooth)
peak = max(y for _, y in raw) - min(y for _, y in raw)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="title desc">
  <title id="title">Chaikin Signal — Corner Cutting Turns Jagged Samples into a Smooth Wave</title>
  <desc id="desc">A cyberpunk visualization comparing a jagged polyline and its Chaikin-smoothed curve generated from the same 17 sample points.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#040612"/>
      <stop offset="50%" stop-color="#081425"/>
      <stop offset="100%" stop-color="#05070e"/>
    </linearGradient>
    <linearGradient id="neon" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#31e6ff"/>
      <stop offset="50%" stop-color="#7d8bff"/>
      <stop offset="100%" stop-color="#ff4fd8"/>
    </linearGradient>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="10" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <pattern id="scan" width="8" height="8" patternUnits="userSpaceOnUse">
      <rect width="8" height="8" fill="transparent"/>
      <rect width="8" height="1" fill="rgba(255,255,255,0.03)"/>
    </pattern>
  </defs>

  <rect width="100%" height="100%" fill="url(#bg)"/>
  <rect width="100%" height="100%" fill="url(#scan)" opacity="0.45"/>

  <g opacity="0.22" stroke="#1d4f7a" stroke-width="1">
    {''.join(f'<line x1="{x:.2f}" y1="90" x2="{x:.2f}" y2="710" />' for x in [MARGIN_X + i*(W-2*MARGIN_X)/16 for i in range(17)])}
    {''.join(f'<line x1="70" y1="{y:.2f}" x2="1130" y2="{y:.2f}" />' for y in [110 + i*85 for i in range(8)])}
  </g>

  <line x1="70" y1="{BASE_Y:.2f}" x2="1130" y2="{BASE_Y:.2f}" stroke="#2d8dbd" stroke-width="1.5" opacity="0.35" />

  <g fill="#9bcfff" font-family="monospace" font-size="18" opacity="0.7">
    <text x="90" y="65">AGENT J LAB // CHAIKIN SIGNAL</text>
    <text x="90" y="95" font-size="13" opacity="0.78">17 SAMPLE POINTS → 4 SUBDIVISIONS → {smooth_points} CURVE POINTS</text>
  </g>

  <polyline points="{points_str(raw)}" fill="none" stroke="#5ec8ff" stroke-width="3" stroke-dasharray="8 10" opacity="0.55"/>
  <polyline points="{points_str(smooth)}" fill="none" stroke="url(#neon)" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)"/>

  <g>
    {''.join(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5.5" fill="#d6f8ff" stroke="#43d5ff" stroke-width="1.5" />' for x,y in raw)}
  </g>

  <g fill="#d7eeff" font-family="monospace" font-size="13" opacity="0.75">
    {''.join(f'<text x="{x-8:.2f}" y="{y-14:.2f}">{i}</text>' for i,(x,y) in enumerate(raw))}
  </g>

  <g transform="translate(84,620)">
    <rect width="290" height="118" rx="16" fill="rgba(5,16,32,0.76)" stroke="rgba(73,180,255,0.22)"/>
    <text x="18" y="28" fill="#87e8ff" font-family="monospace" font-size="15">METRICS</text>
    <text x="18" y="54" fill="#ccecff" font-family="monospace" font-size="14">Raw segments   : {raw_segments}</text>
    <text x="18" y="76" fill="#ccecff" font-family="monospace" font-size="14">Raw path length: {raw_len:.1f}px</text>
    <text x="18" y="98" fill="#ccecff" font-family="monospace" font-size="14">Smooth length  : {smooth_len:.1f}px</text>
  </g>

  <g transform="translate(820,620)">
    <rect width="294" height="118" rx="16" fill="rgba(16,8,28,0.76)" stroke="rgba(204,95,255,0.22)"/>
    <text x="18" y="28" fill="#ff94ea" font-family="monospace" font-size="15">HYPOTHESIS SNAPSHOT</text>
    <text x="18" y="54" fill="#f6dfff" font-family="monospace" font-size="14">Corner cutting kills sharp angles.</text>
    <text x="18" y="76" fill="#f6dfff" font-family="monospace" font-size="14">Peak-to-peak swing: {peak:.1f}px</text>
    <text x="18" y="98" fill="#f6dfff" font-family="monospace" font-size="14">Same points, radically smoother feel.</text>
  </g>

  <g opacity="0.75">
    <text x="878" y="90" fill="#c6eeff" font-family="monospace" font-size="14">RAW POLYLINE</text>
    <line x1="1016" y1="84" x2="1086" y2="84" stroke="#5ec8ff" stroke-width="3" stroke-dasharray="8 10"/>
    <text x="878" y="116" fill="#ffd7f8" font-family="monospace" font-size="14">CHAIKIN SMOOTHED</text>
    <line x1="1016" y1="110" x2="1086" y2="110" stroke="url(#neon)" stroke-width="5" stroke-linecap="round"/>
  </g>
</svg>
'''

out = Path('lab/chaikin-signal.svg')
out.write_text(svg, encoding='utf-8')
print('wrote', out)
print('smooth_points', smooth_points)
print('raw_len', round(raw_len,1))
print('smooth_len', round(smooth_len,1))
