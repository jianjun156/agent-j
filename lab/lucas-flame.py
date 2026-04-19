#!/usr/bin/env python3
import math
import struct
import zlib
from pathlib import Path

ROWS = 512
WIDTH = 1200
HEIGHT = 1104
CENTER_X = WIDTH // 2
TOP = 40
OUT = Path(__file__).with_suffix('.png')


def chunk(tag: bytes, data: bytes) -> bytes:
    return (
        struct.pack('>I', len(data))
        + tag
        + data
        + struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def save_png(path: Path, width: int, height: int, rgb: bytearray) -> None:
    rows = []
    stride = width * 3
    for y in range(height):
        start = y * stride
        rows.append(b'\x00' + bytes(rgb[start:start + stride]))
    raw = b''.join(rows)
    png = [b'\x89PNG\r\n\x1a\n']
    png.append(chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)))
    png.append(chunk(b'IDAT', zlib.compress(raw, 9)))
    png.append(chunk(b'IEND', b''))
    path.write_bytes(b''.join(png))


def idx(x: int, y: int) -> int:
    return (y * WIDTH + x) * 3


def add_pixel(buf: bytearray, x: int, y: int, color, alpha: float = 1.0) -> None:
    if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
        return
    i = idx(x, y)
    for c in range(3):
        value = buf[i + c] + int(color[c] * alpha)
        buf[i + c] = 255 if value > 255 else value


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# Background: deep-space vertical gradient + faint scanlines + vignette
img = bytearray(WIDTH * HEIGHT * 3)
for y in range(HEIGHT):
    t = y / (HEIGHT - 1)
    base = lerp((4, 6, 18), (12, 18, 42), t)
    scan = -4 if y % 4 == 0 else 0
    for x in range(WIDTH):
        vx = (x - WIDTH / 2) / (WIDTH / 2)
        vy = (y - HEIGHT / 2) / (HEIGHT / 2)
        vignette = max(0.0, 1.0 - 0.52 * (vx * vx + vy * vy))
        i = idx(x, y)
        img[i] = max(0, min(255, int((base[0] + scan) * vignette)))
        img[i + 1] = max(0, min(255, int((base[1] + scan) * vignette)))
        img[i + 2] = max(0, min(255, int((base[2] + scan) * vignette)))

odd_count = 0
row_odd_counts = []
for n in range(ROWS):
    row_odd = 0
    t = n / (ROWS - 1)
    color = lerp((66, 220, 255), (255, 90, 220), t ** 0.8)
    glow = lerp((20, 90, 160), (120, 40, 150), t ** 0.8)
    y = TOP + n * 2
    for k in range(n + 1):
        if (k & (n - k)) == 0:  # Lucas theorem parity shortcut
            row_odd += 1
            odd_count += 1
            x = CENTER_X - n + 2 * k
            for dy in range(-1, 3):
                for dx in range(-1, 3):
                    dist = abs(dx - 0.5) + abs(dy - 0.5)
                    if 0 <= dist <= 3:
                        add_pixel(img, x + dx, y + dy, glow, 0.18 if dist > 1 else 0.32)
            for dy in range(2):
                for dx in range(2):
                    add_pixel(img, x + dx, y + dy, color, 1.0)
    row_odd_counts.append(row_odd)

# faint frame
frame = (30, 80, 120)
for x in range(22, WIDTH - 22):
    add_pixel(img, x, 22, frame, 0.9)
    add_pixel(img, x, HEIGHT - 23, frame, 0.9)
for y in range(22, HEIGHT - 22):
    add_pixel(img, 22, y, frame, 0.9)
    add_pixel(img, WIDTH - 23, y, frame, 0.9)

save_png(OUT, WIDTH, HEIGHT, img)

total_entries = ROWS * (ROWS + 1) // 2
ratio = odd_count / total_entries * 100
m = int(math.log2(ROWS))
expected = 3 ** m if 2 ** m == ROWS else None
max_row_index = max(range(ROWS), key=lambda i: row_odd_counts[i])
max_row_odd = row_odd_counts[max_row_index]

print(f'output={OUT}')
print(f'rows={ROWS}')
print(f'total_entries={total_entries}')
print(f'odd_entries={odd_count}')
print(f'odd_ratio={ratio:.4f}%')
print(f'max_odd_row=row {max_row_index} -> {max_row_odd} odd coefficients')
if expected is not None:
    print(f'expected_odd_entries=3^{m}={expected}')
    print(f'match={odd_count == expected}')
