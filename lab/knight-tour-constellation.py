#!/usr/bin/env python3
import math
import struct
import time
import zlib
from pathlib import Path

W, H = 1200, 900
OUT = Path('/Users/jianjun/.openclaw/workspace/agent-j/lab/knight-tour-constellation.png')
BOARD = 8
MOVES = [
    (1, 2), (2, 1), (2, -1), (1, -2),
    (-1, -2), (-2, -1), (-2, 1), (-1, 2),
]

canvas = bytearray(W * H * 3)


def idx(x, y):
    return (y * W + x) * 3


def clamp(v):
    return 0 if v < 0 else 255 if v > 255 else int(v)


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


def rect(x, y, w, h, color, alpha=1.0):
    x0 = max(0, int(x))
    y0 = max(0, int(y))
    x1 = min(W, int(x + w))
    y1 = min(H, int(y + h))
    for yy in range(y0, y1):
        for xx in range(x0, x1):
            blend(xx, yy, color, alpha)


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
    steps = max(2, int(dist * 1.4))
    for s in range(steps + 1):
        t = s / steps
        x = x1 + (x2 - x1) * t
        y = y1 + (y2 - y1) * t
        blend(x, y, color, alpha)
        if glow > 0:
            soft_dot(x, y, glow, color, 0.03)


def chunk(tag, data):
    return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF)


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


def background():
    cx, cy = W / 2, H / 2
    for y in range(H):
        for x in range(W):
            dx = (x - cx) / W
            dy = (y - cy) / H
            r = math.sqrt(dx * dx + dy * dy)
            base = 4 + max(0, 18 - int(r * 40))
            blue = 13 + max(0, 34 - int(r * 56))
            scan = 2 if y % 3 == 0 else 0
            i = idx(x, y)
            canvas[i] = base
            canvas[i + 1] = base + scan
            canvas[i + 2] = blue + scan
    for sx, sy, rr, col, strength in [
        (210, 130, 2, (255, 255, 255), 1.0),
        (300, 220, 3, (80, 220, 255), 0.8),
        (980, 170, 2, (255, 120, 220), 0.9),
        (1040, 720, 2, (120, 255, 210), 0.7),
        (120, 760, 3, (255, 255, 180), 0.6),
    ]:
        soft_dot(sx, sy, rr, col, strength)
    soft_dot(cx, cy, 340, (26, 70, 140), 0.09)
    soft_dot(cx, cy, 230, (160, 40, 220), 0.05)


def onward_count(x, y, visited):
    c = 0
    for dx, dy in MOVES:
        nx, ny = x + dx, y + dy
        if 0 <= nx < BOARD and 0 <= ny < BOARD and (nx, ny) not in visited:
            c += 1
    return c


def center_bias(x, y):
    cx = cy = (BOARD - 1) / 2
    return abs(x - cx) + abs(y - cy)


def knight_tour(start=(0, 0)):
    path = [start]
    visited = {start}
    for _ in range(BOARD * BOARD - 1):
        x, y = path[-1]
        cand = []
        for dx, dy in MOVES:
            nx, ny = x + dx, y + dy
            if 0 <= nx < BOARD and 0 <= ny < BOARD and (nx, ny) not in visited:
                cand.append((onward_count(nx, ny, visited), center_bias(nx, ny), ny, nx, (nx, ny)))
        if not cand:
            return path
        cand.sort()
        nxt = cand[0][-1]
        path.append(nxt)
        visited.add(nxt)
    return path


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


def main():
    t0 = time.time()
    path = knight_tour((0, 0))
    assert len(path) == 64
    closed = any(path[-1][0] + dx == path[0][0] and path[-1][1] + dy == path[0][1] for dx, dy in MOVES)

    background()

    board_x, board_y = 120, 110
    cell = 76
    board_w = BOARD * cell
    board_h = BOARD * cell

    # board squares
    for y in range(BOARD):
        for x in range(BOARD):
            light = (14, 26, 50) if (x + y) % 2 == 0 else (8, 14, 32)
            glow = 0.92 if (x + y) % 2 == 0 else 0.96
            rect(board_x + x * cell, board_y + y * cell, cell - 2, cell - 2, light, glow)

    # frame & grid
    rect(board_x - 2, board_y - 2, board_w + 4, 2, (60, 140, 220), 0.9)
    rect(board_x - 2, board_y + board_h, board_w + 4, 2, (60, 140, 220), 0.9)
    rect(board_x - 2, board_y, 2, board_h, (60, 140, 220), 0.9)
    rect(board_x + board_w, board_y, 2, board_h, (60, 140, 220), 0.9)
    for i in range(1, BOARD):
        rect(board_x + i * cell, board_y, 1, board_h, (30, 70, 110), 0.55)
        rect(board_x, board_y + i * cell, board_w, 1, (30, 70, 110), 0.55)

    coords = []
    for x, y in path:
        px = board_x + x * cell + cell / 2
        py = board_y + y * cell + cell / 2
        coords.append((px, py))

    # path lines
    for i in range(len(coords) - 1):
        t = i / (len(coords) - 2)
        color = (
            int(70 + 185 * t),
            int(235 - 80 * t),
            int(255 - 35 * t + 20 * math.sin(t * math.pi * 2)),
        )
        line(coords[i][0], coords[i][1], coords[i + 1][0], coords[i + 1][1], color, 0.28, 2.2)

    # nodes and move numbers
    for i, (px, py) in enumerate(coords, start=1):
        t = (i - 1) / 63
        outer = (80, 220, 255) if i < 64 else (255, 90, 220)
        inner = (255, 255, 255) if i in (1, 64) else (150 + int(80 * t), 200, 255)
        soft_dot(px, py, 9 if i in (1, 64) else 6, outer, 0.55 if i in (1, 64) else 0.22)
        soft_dot(px, py, 2.5, inner, 0.9)
        draw_number(px - (6 if i < 10 else 10 if i < 100 else 14), py - 8, i, 2, (255, 255, 255))

    # side stats panel
    panel_x, panel_y = 830, 160
    rect(panel_x, panel_y, 280, 290, (8, 18, 38), 0.88)
    rect(panel_x, panel_y, 280, 1, (80, 160, 255), 0.95)
    rect(panel_x, panel_y + 289, 280, 1, (80, 160, 255), 0.95)
    rect(panel_x, panel_y, 1, 290, (80, 160, 255), 0.95)
    rect(panel_x + 279, panel_y, 1, 290, (80, 160, 255), 0.95)

    # mini move-length bars (all equal in a knight move class, but looks nice and proves jump geometry)
    lengths = []
    for (x1, y1), (x2, y2) in zip(path, path[1:]):
        lengths.append(math.hypot(x2 - x1, y2 - y1))
    avg_len = sum(lengths) / len(lengths)
    unique_len = sorted({round(v, 5) for v in lengths})

    for i, val in enumerate(lengths[:16]):
        bx = panel_x + 18
        by = panel_y + 28 + i * 15
        bw = int((val / max(lengths)) * 160)
        rect(bx, by, bw, 8, (70, 220, 255), 0.9)
        if i % 2 == 0:
            rect(bx, by, max(1, bw // 3), 8, (255, 90, 220), 0.85)

    # visit order heat strip
    strip_x, strip_y = 830, 500
    rect(strip_x, strip_y, 280, 120, (8, 18, 38), 0.88)
    for i in range(64):
        t = i / 63
        color = (int(40 + 215 * t), int(220 - 90 * t), int(255 - 10 * t))
        rect(strip_x + 10 + i * 4, strip_y + 18, 3, 82, color, 0.95)
    rect(strip_x, strip_y, 280, 1, (80, 160, 255), 0.95)
    rect(strip_x, strip_y + 119, 280, 1, (80, 160, 255), 0.95)

    save_png(OUT)

    print(f'generated={OUT.name}')
    print(f'squares_visited={len(path)}')
    print(f'start={path[0]} end={path[-1]}')
    print(f'closed_tour={closed}')
    print('first_12=' + ','.join(f'{x}{y}' for x, y in path[:12]))
    print(f'avg_jump={avg_len:.6f}')
    print('unique_jump_lengths=' + ','.join(str(v) for v in unique_len))
    print(f'elapsed={time.time() - t0:.4f}s')
    print(f'bytes={OUT.stat().st_size}')


if __name__ == '__main__':
    main()
