#!/usr/bin/env python3
import math
import struct
import time
import zlib
from pathlib import Path

W = 1200
H = 1200
CX = W / 2
CY = H / 2
R = 430
MODULUS = 361
MULTIPLIER = 5
OUT = Path(__file__).with_suffix('.png')

PALETTE = [
    (56, 235, 255),
    (78, 140, 255),
    (255, 90, 214),
    (255, 162, 92),
    (255, 232, 120),
]

canvas = bytearray(W * H * 3)


def idx(x: int, y: int) -> int:
    return (y * W + x) * 3


def clamp(v: float) -> int:
    return 0 if v < 0 else 255 if v > 255 else int(v)


def blend(x: float, y: float, color, alpha: float):
    xi = int(round(x))
    yi = int(round(y))
    if xi < 0 or yi < 0 or xi >= W or yi >= H or alpha <= 0:
        return
    i = idx(xi, yi)
    inv = 1.0 - alpha
    canvas[i] = clamp(canvas[i] * inv + color[0] * alpha)
    canvas[i + 1] = clamp(canvas[i + 1] * inv + color[1] * alpha)
    canvas[i + 2] = clamp(canvas[i + 2] * inv + color[2] * alpha)


def add(x: float, y: float, color, power: float):
    xi = int(round(x))
    yi = int(round(y))
    if xi < 0 or yi < 0 or xi >= W or yi >= H or power <= 0:
        return
    i = idx(xi, yi)
    canvas[i] = clamp(canvas[i] + color[0] * power)
    canvas[i + 1] = clamp(canvas[i + 1] + color[1] * power)
    canvas[i + 2] = clamp(canvas[i + 2] + color[2] * power)


def soft_dot(x: float, y: float, radius: float, color, strength: float = 1.0):
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
                add(xx, yy, color, (t * t) * strength)


def line(x1: float, y1: float, x2: float, y2: float, color, alpha: float, glow: float):
    dist = math.hypot(x2 - x1, y2 - y1)
    steps = max(2, int(dist * 1.6))
    for s in range(steps + 1):
        t = s / steps
        x = x1 + (x2 - x1) * t
        y = y1 + (y2 - y1) * t
        blend(x, y, color, alpha)
        if glow > 0:
            soft_dot(x, y, glow, color, strength=0.055)


def lerp(c1, c2, t: float):
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


def background():
    for y in range(H):
        for x in range(W):
            dx = (x - CX) / W
            dy = (y - CY) / H
            r = math.sqrt(dx * dx + dy * dy)
            base = 4 + max(0, 18 - int(r * 42))
            blue = 14 + max(0, 26 - int(r * 64))
            scan = 3 if y % 3 == 0 else 0
            i = idx(x, y)
            canvas[i] = base
            canvas[i + 1] = base + scan
            canvas[i + 2] = blue + scan
    for radius, color, strength in [
        (450, (24, 80, 140), 0.12),
        (330, (100, 0, 150), 0.08),
        (210, (0, 255, 220), 0.045),
    ]:
        soft_dot(CX, CY, radius, color, strength)


def png_chunk(tag: bytes, data: bytes) -> bytes:
    return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)


def save_png(path: Path):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        start = y * stride
        raw.extend(canvas[start:start + stride])
    compressed = zlib.compress(bytes(raw), 9)
    png = bytearray(b'\x89PNG\r\n\x1a\n')
    png += png_chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
    png += png_chunk(b'IDAT', compressed)
    png += png_chunk(b'IEND', b'')
    path.write_bytes(png)


def point_pos(n: int):
    angle = -math.pi / 2 + 2 * math.pi * n / MODULUS
    return CX + R * math.cos(angle), CY + R * math.sin(angle)


def build_cycles():
    visited = set()
    cycles = []
    for start in range(MODULUS):
        if start in visited:
            continue
        cur = start
        cyc = []
        while cur not in visited:
            visited.add(cur)
            cyc.append(cur)
            cur = (cur * MULTIPLIER) % MODULUS
        cycles.append(cyc)
    cycles.sort(key=len, reverse=True)
    return cycles


def main():
    t0 = time.time()
    background()

    cycles = build_cycles()
    positions = [point_pos(i) for i in range(MODULUS)]

    # Outer ring
    for i in range(MODULUS):
        x1, y1 = positions[i]
        x2, y2 = positions[(i + 1) % MODULUS]
        line(x1, y1, x2, y2, (40, 90, 140), 0.09, 0.0)

    # Orbit chords
    for ci, cyc in enumerate(cycles):
        base = PALETTE[ci % len(PALETTE)]
        accent = lerp(base, (255, 255, 255), 0.28)
        alpha = 0.28 if len(cyc) >= 100 else 0.42 if len(cyc) >= 9 else 0.85
        glow = 2.3 if len(cyc) >= 100 else 2.6 if len(cyc) >= 9 else 4.0
        for j, node in enumerate(cyc):
            nxt = cyc[(j + 1) % len(cyc)]
            color = lerp(base, accent, j / max(1, len(cyc) - 1))
            x1, y1 = positions[node]
            x2, y2 = positions[nxt]
            if node == nxt:
                soft_dot(x1, y1, 8, color, 0.8)
            else:
                line(x1, y1, x2, y2, color, alpha, glow)

    # Nodes
    for ci, cyc in enumerate(cycles):
        color = PALETTE[ci % len(PALETTE)]
        radius = 2.2 if len(cyc) >= 100 else 2.8 if len(cyc) >= 9 else 5.5
        for node in cyc:
            x, y = positions[node]
            soft_dot(x, y, radius, color, 0.95)

    # Center glow and framing ring
    soft_dot(CX, CY, 84, (40, 180, 255), 0.06)
    soft_dot(CX, CY, 24, (255, 100, 200), 0.04)
    for a in range(360):
        ang = math.radians(a)
        x = CX + (R + 18) * math.cos(ang)
        y = CY + (R + 18) * math.sin(ang)
        blend(x, y, (20, 90, 140), 0.14)

    save_png(OUT)
    elapsed = time.time() - t0
    lengths = [len(c) for c in cycles]
    phi = sum(1 for i in range(MODULUS) if math.gcd(i, MODULUS) == 1)
    mult19 = sum(1 for i in range(1, MODULUS) if i % 19 == 0)
    print(f"generated={OUT.name}")
    print(f"modulus={MODULUS} multiplier={MULTIPLIER}")
    print(f"cycle_lengths={lengths}")
    print(f"unit_count={phi} multiple_of_19_nonzero={mult19}")
    print(f"elapsed={elapsed:.4f}s")
    print(f"bytes={OUT.stat().st_size}")


if __name__ == '__main__':
    main()
