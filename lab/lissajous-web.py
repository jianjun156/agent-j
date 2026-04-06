#!/usr/bin/env python3
"""
EXP-20260407-020: LISSAJOUS-HARMONY
Generate a grid of Lissajous figures showing frequency ratios
that correspond to musical intervals.

x(t) = sin(a*t + δ)
y(t) = sin(b*t)

Each ratio a:b maps to a musical interval:
1:1=Unison, 2:1=Octave, 3:2=Fifth, 4:3=Fourth,
5:4=Major Third, 5:3=Major Sixth, 6:5=Minor Third, 8:5=Minor Sixth

Pure Python, zero external dependencies, hand-rolled PNG encoder.
"""

import math
import struct
import zlib

# --- Canvas setup ---
CELL_W, CELL_H = 200, 200
COLS, COLS_GAP = 4, 30
ROWS, ROWS_GAP = 2, 60
PAD_TOP = 90
PAD_BOTTOM = 40
PAD_LR = 40

W = PAD_LR * 2 + COLS * CELL_W + (COLS - 1) * COLS_GAP
H = PAD_TOP + ROWS * CELL_H + (ROWS - 1) * ROWS_GAP + PAD_BOTTOM

# Musical interval Lissajous configs: (a, b, phase_delta, name_en, name_zh)
FIGURES = [
    (1, 1, math.pi/4, "Unison 1:1", "同度"),
    (2, 1, math.pi/4, "Octave 2:1", "八度"),
    (3, 2, math.pi/4, "Fifth 3:2", "五度"),
    (4, 3, math.pi/4, "Fourth 4:3", "四度"),
    (5, 4, math.pi/4, "Maj 3rd 5:4", "大三度"),
    (5, 3, math.pi/4, "Maj 6th 5:3", "大六度"),
    (6, 5, math.pi/4, "Min 3rd 6:5", "小三度"),
    (8, 5, math.pi/4, "Min 6th 8:5", "小六度"),
]

# Colors: cyberpunk palette
BG = (8, 12, 24)
GLOW_COLORS = [
    (0, 255, 220),   # cyan
    (80, 200, 255),   # light blue
    (160, 100, 255),  # purple
    (255, 80, 200),   # magenta
    (255, 200, 60),   # gold
    (100, 255, 150),  # green
    (255, 120, 80),   # orange
    (200, 160, 255),  # lavender
]

# --- 3x5 dot-matrix font ---
FONT_3X5 = {
    'A': [0b111,0b101,0b111,0b101,0b101], 'B': [0b110,0b101,0b110,0b101,0b110],
    'C': [0b111,0b100,0b100,0b100,0b111], 'D': [0b110,0b101,0b101,0b101,0b110],
    'E': [0b111,0b100,0b110,0b100,0b111], 'F': [0b111,0b100,0b110,0b100,0b100],
    'G': [0b111,0b100,0b101,0b101,0b111], 'H': [0b101,0b101,0b111,0b101,0b101],
    'I': [0b111,0b010,0b010,0b010,0b111], 'J': [0b001,0b001,0b001,0b101,0b111],
    'K': [0b101,0b110,0b100,0b110,0b101], 'L': [0b100,0b100,0b100,0b100,0b111],
    'M': [0b101,0b111,0b111,0b101,0b101], 'N': [0b101,0b111,0b111,0b111,0b101],
    'O': [0b111,0b101,0b101,0b101,0b111], 'P': [0b111,0b101,0b111,0b100,0b100],
    'Q': [0b111,0b101,0b101,0b111,0b001], 'R': [0b111,0b101,0b111,0b110,0b101],
    'S': [0b111,0b100,0b111,0b001,0b111], 'T': [0b111,0b010,0b010,0b010,0b010],
    'U': [0b101,0b101,0b101,0b101,0b111], 'V': [0b101,0b101,0b101,0b101,0b010],
    'W': [0b101,0b101,0b111,0b111,0b101], 'X': [0b101,0b101,0b010,0b101,0b101],
    'Y': [0b101,0b101,0b010,0b010,0b010], 'Z': [0b111,0b001,0b010,0b100,0b111],
    '0': [0b111,0b101,0b101,0b101,0b111], '1': [0b010,0b110,0b010,0b010,0b111],
    '2': [0b111,0b001,0b111,0b100,0b111], '3': [0b111,0b001,0b111,0b001,0b111],
    '4': [0b101,0b101,0b111,0b001,0b001], '5': [0b111,0b100,0b111,0b001,0b111],
    '6': [0b111,0b100,0b111,0b101,0b111], '7': [0b111,0b001,0b010,0b010,0b010],
    '8': [0b111,0b101,0b111,0b101,0b111], '9': [0b111,0b101,0b111,0b001,0b111],
    ':': [0b000,0b010,0b000,0b010,0b000], '/': [0b001,0b001,0b010,0b100,0b100],
    ' ': [0b000,0b000,0b000,0b000,0b000], '.': [0b000,0b000,0b000,0b000,0b010],
    '-': [0b000,0b000,0b111,0b000,0b000], '(': [0b010,0b100,0b100,0b100,0b010],
    ')': [0b010,0b001,0b001,0b001,0b010], '+': [0b000,0b010,0b111,0b010,0b000],
    '#': [0b101,0b111,0b101,0b111,0b101], '=': [0b000,0b111,0b000,0b111,0b000],
}

def draw_text(pixels, text, x0, y0, color, scale=2):
    """Draw text using 3x5 dot-matrix font."""
    text = text.upper()
    cx = x0
    for ch in text:
        glyph = FONT_3X5.get(ch, FONT_3X5[' '])
        for row in range(5):
            for col in range(3):
                if glyph[row] & (1 << (2 - col)):
                    for sy in range(scale):
                        for sx in range(scale):
                            px = cx + col * scale + sx
                            py = y0 + row * scale + sy
                            if 0 <= px < W and 0 <= py < H:
                                pixels[py][px] = color
        cx += 4 * scale

def blend(bg, fg, alpha):
    return tuple(int(b + (f - b) * alpha) for b, f in zip(bg, fg))

def draw_line_aa(pixels, x0, y0, x1, y1, color, thickness=1):
    """Draw anti-aliased line with given thickness."""
    dx = x1 - x0
    dy = y1 - y0
    dist = math.sqrt(dx*dx + dy*dy)
    if dist < 0.5:
        return
    steps = max(int(dist * 2), 1)
    for i in range(steps + 1):
        t = i / steps
        fx = x0 + dx * t
        fy = y0 + dy * t
        # Draw with sub-pixel blending
        for oy in range(-thickness, thickness + 1):
            for ox in range(-thickness, thickness + 1):
                px = int(fx) + ox
                py = int(fy) + oy
                if 0 <= px < W and 0 <= py < H:
                    d = math.sqrt((fx - px)**2 + (fy - py)**2)
                    if d < thickness + 0.5:
                        alpha = max(0, min(1, thickness + 0.5 - d))
                        pixels[py][px] = blend(pixels[py][px], color, alpha * 0.9)

def make_png(pixels, width, height):
    """Hand-rolled PNG encoder."""
    def chunk(ctype, data):
        c = ctype + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    
    raw = b''
    for row in pixels:
        raw += b'\x00'  # filter: none
        for r, g, b in row:
            raw += struct.pack('BBB', r, g, b)
    
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
    idat = chunk(b'IDAT', zlib.compress(raw, 9))
    iend = chunk(b'IEND', b'')
    return sig + ihdr + idat + iend

# --- Init canvas ---
pixels = [[BG for _ in range(W)] for _ in range(H)]

# --- Title ---
title = "LISSAJOUS HARMONY - AGENT J LAB EXP-020"
draw_text(pixels, title, PAD_LR, 15, (0, 200, 180), scale=3)

subtitle = "FREQUENCY RATIOS = MUSICAL INTERVALS = MATHEMATICAL BEAUTY"
draw_text(pixels, subtitle, PAD_LR, 50, (100, 120, 160), scale=2)

# --- Draw each Lissajous figure ---
for idx, (a, b, delta, name_en, name_zh) in enumerate(FIGURES):
    row = idx // COLS
    col = idx % COLS
    
    cx = PAD_LR + col * (CELL_W + COLS_GAP) + CELL_W // 2
    cy = PAD_TOP + row * (CELL_H + ROWS_GAP) + CELL_H // 2
    
    color = GLOW_COLORS[idx % len(GLOW_COLORS)]
    dim_color = tuple(c // 4 for c in color)
    
    # Draw cell border (subtle)
    bx0 = PAD_LR + col * (CELL_W + COLS_GAP)
    by0 = PAD_TOP + row * (CELL_H + ROWS_GAP)
    for bx in range(bx0, bx0 + CELL_W):
        if 0 <= bx < W:
            if 0 <= by0 < H:
                pixels[by0][bx] = blend(BG, color, 0.15)
            if 0 <= by0 + CELL_H - 1 < H:
                pixels[by0 + CELL_H - 1][bx] = blend(BG, color, 0.15)
    for by in range(by0, by0 + CELL_H):
        if 0 <= by < H:
            if 0 <= bx0 < W:
                pixels[by][bx0] = blend(BG, color, 0.15)
            if 0 <= bx0 + CELL_W - 1 < W:
                pixels[by][bx0 + CELL_W - 1] = blend(BG, color, 0.15)
    
    # Draw label
    draw_text(pixels, name_en, bx0 + 4, by0 + CELL_H + 4, color, scale=2)
    
    # Generate Lissajous curve points
    radius = 80  # half of cell, with margin
    num_points = 2000
    points = []
    for i in range(num_points + 1):
        t = 2 * math.pi * i / num_points
        x = cx + radius * math.sin(a * t + delta)
        y = cy + radius * math.sin(b * t)
        points.append((x, y, i / num_points))
    
    # Draw glow layer (wider, dimmer)
    for i in range(len(points) - 1):
        x0, y0, prog0 = points[i]
        x1, y1, prog1 = points[i + 1]
        # Color progression along the curve
        t_color = (prog0 + prog1) / 2
        r = int(color[0] * (1 - t_color * 0.3))
        g = int(color[1] * (1 - t_color * 0.3))
        bv = int(color[2] * (1 - t_color * 0.3))
        glow_c = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, bv)))
        
        # Only draw every few points for glow (performance)
        if i % 3 == 0:
            draw_line_aa(pixels, x0, y0, x1, y1, glow_c, thickness=2)
    
    # Draw main curve (thinner, brighter)
    for i in range(len(points) - 1):
        x0, y0, prog0 = points[i]
        x1, y1, prog1 = points[i + 1]
        t_color = (prog0 + prog1) / 2
        # Brighten along progress
        r = int(min(255, color[0] + (255 - color[0]) * t_color * 0.4))
        g = int(min(255, color[1] + (255 - color[1]) * t_color * 0.4))
        bv = int(min(255, color[2] + (255 - color[2]) * t_color * 0.4))
        main_c = (r, g, bv)
        draw_line_aa(pixels, x0, y0, x1, y1, main_c, thickness=1)

# --- Vignette ---
center_x, center_y = W / 2, H / 2
max_dist = math.sqrt(center_x**2 + center_y**2)
for y in range(H):
    for x in range(W):
        d = math.sqrt((x - center_x)**2 + (y - center_y)**2) / max_dist
        darken = max(0, d - 0.5) * 1.2
        darken = min(darken, 0.6)
        r, g, b = pixels[y][x]
        pixels[y][x] = (int(r * (1 - darken)), int(g * (1 - darken)), int(b * (1 - darken)))

# --- Scanlines ---
for y in range(0, H, 3):
    for x in range(W):
        r, g, b = pixels[y][x]
        pixels[y][x] = (int(r * 0.92), int(g * 0.92), int(b * 0.92))

# --- Footer ---
footer = "X(T)=SIN(A.T+D) Y(T)=SIN(B.T) -- PURE PYTHON ZERO DEPS"
draw_text(pixels, footer, PAD_LR, H - 25, (60, 80, 100), scale=1)

# --- Save PNG ---
print(f"Canvas: {W}x{H}")
png_data = make_png(pixels, W, H)
out_path = "/Users/jianjun/.openclaw/workspace/agent-j/lab/lissajous-harmony.png"
with open(out_path, 'wb') as f:
    f.write(png_data)
print(f"Saved: {out_path} ({len(png_data)//1024}KB)")
print("Done!")
