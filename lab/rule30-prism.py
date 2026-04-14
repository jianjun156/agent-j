import math, struct, zlib
from pathlib import Path

W_CELLS = 401
ROWS = 280
CELL = 2
PANEL = 80
WIDTH = W_CELLS * CELL
HEIGHT = ROWS * CELL + PANEL
OUT = Path(__file__).with_name('rule30-prism.png')


def png_chunk(tag, data):
    return struct.pack('!I', len(data)) + tag + data + struct.pack('!I', zlib.crc32(tag + data) & 0xffffffff)


def save_png(path, width, height, rgb):
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)
        raw.extend(rgb[y * stride:(y + 1) * stride])
    png = bytearray(b'\x89PNG\r\n\x1a\n')
    png += png_chunk(b'IHDR', struct.pack('!IIBBBBB', width, height, 8, 2, 0, 0, 0))
    png += png_chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    png += png_chunk(b'IEND', b'')
    path.write_bytes(png)


def set_px(buf, x, y, color):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        i = (y * WIDTH + x) * 3
        buf[i:i+3] = bytes(color)


def rule30(left, center, right):
    return left ^ (center or right)


row = [0] * W_CELLS
row[W_CELLS // 2] = 1
rows = [row[:]]
for _ in range(ROWS - 1):
    prev = rows[-1]
    nxt = [0] * W_CELLS
    for x in range(W_CELLS):
        l = prev[x - 1] if x > 0 else 0
        c = prev[x]
        r = prev[x + 1] if x < W_CELLS - 1 else 0
        nxt[x] = rule30(l, c, r)
    rows.append(nxt)

center_col = [r[W_CELLS // 2] for r in rows]
ones = sum(center_col)
zeros = len(center_col) - ones
balance = ones / len(center_col)
transitions = sum(1 for i in range(1, len(center_col)) if center_col[i] != center_col[i - 1])
run = max_run = 1
for i in range(1, len(center_col)):
    if center_col[i] == center_col[i - 1]:
        run += 1
        max_run = max(max_run, run)
    else:
        run = 1

buf = bytearray(WIDTH * HEIGHT * 3)
for y in range(HEIGHT):
    for x in range(WIDTH):
        t = y / max(1, HEIGHT - 1)
        r = int(3 + 10 * t)
        g = int(5 + 12 * t)
        b = int(18 + 35 * t)
        i = (y * WIDTH + x) * 3
        buf[i:i+3] = bytes((r, g, b))

for gy, bits in enumerate(rows):
    for gx, bit in enumerate(bits):
        if not bit:
            continue
        hue = gx / (W_CELLS - 1)
        rr = int(60 + 160 * (1 - abs(hue - 0.2) * 2.5))
        gg = int(120 + 120 * (1 - abs(hue - 0.5) * 2.0))
        bb = int(160 + 95 * (1 - abs(hue - 0.85) * 2.5))
        color = (max(40, min(255, rr)), max(70, min(255, gg)), max(120, min(255, bb)))
        for dy in range(CELL):
            for dx in range(CELL):
                set_px(buf, gx * CELL + dx, gy * CELL + dy, color)
                if dx == 0 and gx * CELL + dx > 0:
                    set_px(buf, gx * CELL + dx - 1, gy * CELL + dy, tuple(max(0, c - 45) for c in color))

cx = (W_CELLS // 2) * CELL + CELL // 2
for y, bit in enumerate(center_col):
    col = (255, 240, 120) if bit else (70, 60, 35)
    for dy in range(CELL):
        set_px(buf, cx, y * CELL + dy, col)
        if cx + 1 < WIDTH:
            set_px(buf, cx + 1, y * CELL + dy, tuple(min(255, c // 2 + 40) for c in col))

base_y = ROWS * CELL + 12
for i, bit in enumerate(center_col):
    x0 = int(i / len(center_col) * WIDTH)
    x1 = int((i + 1) / len(center_col) * WIDTH)
    col = (255, 215, 90) if bit else (35, 40, 70)
    for y in range(base_y, HEIGHT - 12):
        for x in range(x0, x1):
            set_px(buf, x, y, col)

save_png(OUT, WIDTH, HEIGHT, buf)
print(f'rows={ROWS}')
print(f'width={W_CELLS}')
print(f'active_cells={sum(sum(r) for r in rows)}')
print(f'center_ones={ones}')
print(f'center_zeros={zeros}')
print(f'center_balance={balance:.4f}')
print(f'center_transitions={transitions}')
print(f'center_longest_run={max_run}')
print(f'png={OUT.name}')
print(f'png_bytes={OUT.stat().st_size}')
