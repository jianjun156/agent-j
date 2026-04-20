#!/usr/bin/env python3
import math
import struct
import time
import zlib
from pathlib import Path

W, H = 1200, 900
OUT = Path('/Users/jianjun/.openclaw/workspace/agent-j/lab/debruijn-lockpick.png')
N = 8
K = 2

canvas = bytearray(W * H * 3)


def idx(x, y):
    return (y * W + x) * 3


def clamp(v):
    return 0 if v < 0 else 255 if v > 255 else int(v)


def add(x, y, color, power):
    if power <= 0:
        return
    xi = int(round(x))
    yi = int(round(y))
    if not (0 <= xi < W and 0 <= yi < H):
        return
    i = idx(xi, yi)
    canvas[i] = clamp(canvas[i] + color[0] * power)
    canvas[i + 1] = clamp(canvas[i + 1] + color[1] * power)
    canvas[i + 2] = clamp(canvas[i + 2] + color[2] * power)


def blend(x, y, color, alpha):
    if alpha <= 0:
        return
    xi = int(round(x))
    yi = int(round(y))
    if not (0 <= xi < W and 0 <= yi < H):
        return
    i = idx(xi, yi)
    inv = 1.0 - alpha
    canvas[i] = clamp(canvas[i] * inv + color[0] * alpha)
    canvas[i + 1] = clamp(canvas[i + 1] * inv + color[1] * alpha)
    canvas[i + 2] = clamp(canvas[i + 2] * inv + color[2] * alpha)


def soft_dot(x, y, radius, color, strength=1.0):
    r = int(math.ceil(radius))
    for yy in range(int(y) - r, int(y) + r + 1):
        if yy < 0 or yy >= H:
            continue
        for xx in range(int(x) - r, int(x) + r + 1):
            if xx < 0 or xx >= W:
                continue
            d = math.hypot(xx - x, yy - y)
            if d <= radius:
                t = 1.0 - d / max(radius, 1e-6)
                add(xx, yy, color, t * t * strength)


def line(x1, y1, x2, y2, color, alpha=0.25, glow=0.0):
    dist = math.hypot(x2 - x1, y2 - y1)
    steps = max(2, int(dist * 1.6))
    for s in range(steps + 1):
        t = s / steps
        x = x1 + (x2 - x1) * t
        y = y1 + (y2 - y1) * t
        blend(x, y, color, alpha)
        if glow > 0:
            soft_dot(x, y, glow, color, 0.035)


def rect(x, y, w, h, color, alpha=1.0):
    x0 = max(0, int(x))
    y0 = max(0, int(y))
    x1 = min(W, int(x + w))
    y1 = min(H, int(y + h))
    for yy in range(y0, y1):
        for xx in range(x0, x1):
            blend(xx, yy, color, alpha)


def de_bruijn(k, n):
    a = [0] * (k * n)
    seq = []
    def db(t, p):
        if t > n:
            if n % p == 0:
                seq.extend(a[1:p + 1])
        else:
            a[t] = a[t - p]
            db(t + 1, p)
            for j in range(a[t - p] + 1, k):
                a[t] = j
                db(t + 1, t)
    db(1, 1)
    return seq


def background():
    cx, cy = W / 2, H / 2
    for y in range(H):
        for x in range(W):
            dx = (x - cx) / W
            dy = (y - cy) / H
            r = math.sqrt(dx * dx + dy * dy)
            base = 4 + max(0, 15 - int(r * 38))
            blue = 12 + max(0, 26 - int(r * 50))
            scan = 3 if y % 3 == 0 else 0
            i = idx(x, y)
            canvas[i] = base
            canvas[i + 1] = base + scan
            canvas[i + 2] = blue + scan
    soft_dot(cx, cy, 380, (20, 60, 140), 0.08)
    soft_dot(cx, cy, 240, (120, 0, 180), 0.06)
    soft_dot(cx, cy, 120, (0, 255, 220), 0.04)


def draw_digit(x, y, ch, scale, color):
    glyphs = {
        '0': ['111','101','101','101','111'],
        '1': ['010','110','010','010','111'],
        '2': ['111','001','111','100','111'],
        '3': ['111','001','111','001','111'],
        '4': ['101','101','111','001','001'],
        '5': ['111','100','111','001','111'],
        '6': ['111','100','111','101','111'],
        '7': ['111','001','001','001','001'],
        '8': ['111','101','111','101','111'],
        '9': ['111','101','111','001','111'],
    }
    for ry, row in enumerate(glyphs[ch]):
        for rx, bit in enumerate(row):
            if bit == '1':
                rect(x + rx * scale, y + ry * scale, scale - 1, scale - 1, color, 0.95)


def draw_number(x, y, value, scale, color):
    s = str(value)
    for i, ch in enumerate(s):
        draw_digit(x + i * scale * 4, y, ch, scale, color)


def chunk(tag, data):
    return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)


def save_png(path):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw.extend(canvas[y * stride:(y + 1) * stride])
    png = bytearray(b'\x89PNG\r\n\x1a\n')
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    png += chunk(b'IEND', b'')
    path.write_bytes(png)


def main():
    t0 = time.time()
    seq = de_bruijn(K, N)
    bits = ''.join(str(b) for b in seq)
    cycle = bits + bits[:N - 1]
    windows = {cycle[i:i+N] for i in range(len(bits))}
    assert len(bits) == 2 ** N
    assert len(windows) == 2 ** N

    background()

    left, top = 90, 150
    cell_w, cell_h = 4, 120
    for i, bit in enumerate(bits):
        x = left + i * cell_w
        if bit == '1':
            color = (80, 245, 255) if i % 2 == 0 else (255, 90, 214)
            rect(x, top, cell_w - 1, cell_h, color, 0.92)
            soft_dot(x + cell_w / 2, top + cell_h / 2, 3, color, 0.3)
        else:
            rect(x, top, cell_w - 1, cell_h, (10, 20, 40), 0.85)
    rect(left - 1, top - 1, len(bits) * cell_w + 2, 1, (50, 120, 170), 0.8)
    rect(left - 1, top + cell_h, len(bits) * cell_w + 2, 1, (50, 120, 170), 0.8)

    cx, cy, r = 600, 570, 245
    positions = []
    for i, bit in enumerate(bits):
        ang = -math.pi / 2 + 2 * math.pi * i / len(bits)
        rr = r + (18 if bit == '1' else -18)
        x = cx + rr * math.cos(ang)
        y = cy + rr * math.sin(ang)
        positions.append((x, y))
    for i in range(len(bits)):
        x1, y1 = positions[i]
        x2, y2 = positions[(i + 1) % len(bits)]
        color = (80, 245, 255) if bits[i] == '1' else (90, 70, 180)
        line(x1, y1, x2, y2, color, 0.35 if bits[i]=='1' else 0.12, 1.6 if bits[i]=='1' else 0.0)
    for i in range(0, len(bits), 32):
        ang = -math.pi / 2 + 2 * math.pi * i / len(bits)
        x1 = cx + (r - 35) * math.cos(ang)
        y1 = cy + (r - 35) * math.sin(ang)
        x2 = cx + (r + 38) * math.cos(ang)
        y2 = cy + (r + 38) * math.sin(ang)
        line(x1, y1, x2, y2, (255, 110, 220), 0.35, 0.0)
    soft_dot(cx, cy, 95, (40, 180, 255), 0.06)
    soft_dot(cx, cy, 30, (255, 100, 210), 0.05)

    base_x, base_y = 900, 485
    bar_w = 24
    counts = [0] * (N + 1)
    ones_first = [0] * (N + 1)
    for w in windows:
        h = w.count('1')
        counts[h] += 1
        if w[0] == '1':
            ones_first[h] += 1
    max_count = max(counts)
    for i, c in enumerate(counts):
        h = int(180 * c / max_count)
        rect(base_x + i * (bar_w + 8), base_y - h, bar_w, h, (60, 160, 255), 0.85)
        inner = int(h * ones_first[i] / max(c, 1))
        rect(base_x + i * (bar_w + 8) + 4, base_y - inner, bar_w - 8, inner, (255, 90, 214), 0.92)
        draw_number(base_x + i * (bar_w + 8) + 4, base_y + 18, i, 3, (160, 220, 255))

    save_png(OUT)

    sample = [cycle[i:i+N] for i in range(12)]
    print(f'generated={OUT.name}')
    print(f'bits={len(bits)} order={N} alphabet={K}')
    print(f'unique_windows={len(windows)} expected={2**N}')
    print(f'ones={bits.count("1")} zeros={bits.count("0")}')
    print('sample_windows=' + ','.join(sample))
    print('sequence_prefix=' + bits[:64])
    print(f'elapsed={time.time()-t0:.4f}s')
    print(f'bytes={OUT.stat().st_size}')


if __name__ == '__main__':
    main()
