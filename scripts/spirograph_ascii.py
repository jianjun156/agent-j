#!/usr/bin/env python3
"""EXP-20260402-015: Spirograph ASCII — Drawing Parametric Roses with Characters"""
import math, json, os, sys

# === Spirograph / Rose Curve in ASCII ===
# r = cos(k*theta) where k = p/q determines the petal count

W, H = 71, 35  # ASCII canvas size (odd for center)
canvas = [[' '] * W for _ in range(H)]
cx, cy = W // 2, H // 2

# Draw multiple rose curves with different k values
curves = [
    # (k_num, k_den, char, description)
    (3, 1, '*', 'k=3: 3-petal rose'),
    (5, 1, '+', 'k=5: 5-petal rose'),
    (2, 1, 'o', 'k=2: 4-petal rose'),
    (7, 3, '.', 'k=7/3: exotic 7-petal'),
]

# We'll draw the main one: k=5/3 (a beautiful 5-petal with inner loops)
k_num, k_den = 5, 3
k = k_num / k_den
lcm_period = k_den  # full pattern repeats after k_den * pi
total_points = 2000
max_r = 15.0  # radius in char units

# Aspect ratio correction (terminal chars are ~2x taller than wide)
aspect = 2.0

print(f"🌸 Agent J's ASCII Spirograph")
print(f"   Rose curve: r = cos({k_num}/{k_den} · θ)")
print(f"   Canvas: {W}×{H} characters")
print(f"   {total_points} sample points over {k_den}π radians")
print()

# Trace the curve
points_drawn = 0
for i in range(total_points):
    theta = i / total_points * k_den * math.pi
    r = math.cos(k * theta) * max_r
    x = r * math.cos(theta)
    y = r * math.sin(theta)
    
    # Map to canvas with aspect correction
    sx = int(cx + x / aspect)
    sy = int(cy - y * 0.5)
    
    if 0 <= sx < W and 0 <= sy < H:
        # Color by angle (use different chars for different quadrants)
        t = theta / (k_den * math.pi)
        if t < 0.2:
            ch = '░'
        elif t < 0.4:
            ch = '▒'
        elif t < 0.6:
            ch = '▓'
        elif t < 0.8:
            ch = '█'
        else:
            ch = '◆'
        canvas[sy][sx] = ch
        points_drawn += 1

# Draw center marker
canvas[cy][cx] = '◉'

# Draw border
for x in range(W):
    canvas[0][x] = '─'
    canvas[H-1][x] = '─'
for y in range(H):
    canvas[y][0] = '│'
    canvas[y][W-1] = '│'
canvas[0][0] = '┌'; canvas[0][W-1] = '┐'
canvas[H-1][0] = '└'; canvas[H-1][W-1] = '┘'

# Title in border
title = "  SPIROGRAPH: r = cos(5/3·θ)  "
for i, ch in enumerate(title):
    if 2 + i < W - 2:
        canvas[0][2 + i] = ch

# Render
result_lines = []
for row in canvas:
    line = ''.join(row)
    result_lines.append(line)
    print(line)

print()
print(f"📊 Statistics:")
print(f"   Points sampled: {total_points}")
print(f"   Points drawn: {points_drawn}")
print(f"   Petal formula: k = {k_num}/{k_den} = {k:.4f}")
print(f"   Number of petals: {k_num} (when k=p/q and p is odd)")
print(f"   Symmetry: {k_den}-fold rotational")

# Also compute a second interesting curve: Lissajous
print()
print("=" * 50)
print()
print(f"🎯 Bonus: Lissajous Figure (a=3, b=4, δ=π/2)")
print()

W2, H2 = 61, 25
canvas2 = [[' '] * W2 for _ in range(H2)]
cx2, cy2 = W2 // 2, H2 // 2
a_freq, b_freq = 3, 4
delta = math.pi / 2
amp_x, amp_y = 27, 10

for i in range(3000):
    t = i / 3000 * 2 * math.pi
    x = amp_x * math.sin(a_freq * t + delta)
    y = amp_y * math.sin(b_freq * t)
    sx = int(cx2 + x / aspect)
    sy = int(cy2 - y * 0.5)
    if 0 <= sx < W2 and 0 <= sy < H2:
        progress = i / 3000
        if progress < 0.33:
            canvas2[sy][sx] = '·'
        elif progress < 0.67:
            canvas2[sy][sx] = '•'
        else:
            canvas2[sy][sx] = '●'

canvas2[cy2][cx2] = '✦'

# Border
for x in range(W2):
    canvas2[0][x] = '─'; canvas2[H2-1][x] = '─'
for y in range(H2):
    canvas2[y][0] = '│'; canvas2[y][W2-1] = '│'
canvas2[0][0] = '┌'; canvas2[0][W2-1] = '┐'
canvas2[H2-1][0] = '└'; canvas2[H2-1][W2-1] = '┘'
title2 = "  LISSAJOUS: x=sin(3t+π/2), y=sin(4t)  "
for i, ch in enumerate(title2):
    if 2 + i < W2 - 2:
        canvas2[0][2 + i] = ch

lissajous_lines = []
for row in canvas2:
    line = ''.join(row)
    lissajous_lines.append(line)
    print(line)

# Combine for artifact
artifact_text = f"  🌸 Agent J's ASCII Spirograph — EXP-20260402-015\n\n"
artifact_text += "  Rose Curve: r = cos(5/3 · θ)\n\n"
artifact_text += '\n'.join(result_lines)
artifact_text += f"\n\n  Points: {total_points} sampled, {points_drawn} drawn"
artifact_text += f"\n  k = 5/3 → 5 petals with 3-fold symmetry\n\n"
artifact_text += "  Lissajous Figure: x=sin(3t+π/2), y=sin(4t)\n\n"
artifact_text += '\n'.join(lissajous_lines)
artifact_text += "\n\n  Two mathematical curves, zero dependencies, pure terminal art."

print()
print("✅ Experiment complete!")
print()

# Output the artifact for recording
print("=== ARTIFACT_START ===")
print(artifact_text)
print("=== ARTIFACT_END ===")
