from math import cos, sin, pi
from pathlib import Path

W, H = 1200, 1200
cx, cy = W/2, H/2
radius = 420
line_count = 144
rotation_deg = 3.2
rotation = rotation_deg * pi / 180
out = Path(__file__).with_suffix('.svg')

lines_a = []
lines_b = []
for i in range(line_count):
    a = 2*pi*i/line_count
    lines_a.append((cx + cos(a) * 120, cy + sin(a) * 120, cx + cos(a) * radius, cy + sin(a) * radius))
    b = a + rotation
    lines_b.append((cx + cos(b) * 120, cy + sin(b) * 120, cx + cos(b) * radius, cy + sin(b) * radius))

rings = [160, 210, 260, 310, 360, 410]
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">']
svg.append('<rect width="100%" height="100%" fill="#050812"/>')
for r in rings:
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#1f3b57" stroke-width="1"/>')
for x1,y1,x2,y2 in lines_a:
    svg.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="#60f6ff" stroke-width="1.15" opacity="0.8"/>')
for x1,y1,x2,y2 in lines_b:
    svg.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="#ff5bd1" stroke-width="1.15" opacity="0.58"/>')
svg.append('</svg>')
out.write_text('\n'.join(svg), encoding='utf-8')
print(out)
