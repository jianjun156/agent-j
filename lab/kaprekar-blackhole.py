import math
import struct
import zlib
from collections import Counter
from pathlib import Path

OUT = Path(__file__).with_name('kaprekar-blackhole.png')
W, H = 1000, 860
GRID = 8
GX0, GY0 = 70, 120
GW = 100 * GRID
GH = 100 * GRID

FONT = {
    '0': ['111', '101', '101', '101', '111'],
    '1': ['010', '110', '010', '010', '111'],
    '2': ['111', '001', '111', '100', '111'],
    '3': ['111', '001', '111', '001', '111'],
    '4': ['101', '101', '111', '001', '001'],
    '5': ['111', '100', '111', '001', '111'],
    '6': ['111', '100', '111', '101', '111'],
    '7': ['111', '001', '001', '001', '001'],
    '8': ['111', '101', '111', '101', '111'],
    '9': ['111', '101', '111', '001', '111'],
    'A': ['010', '101', '111', '101', '101'],
    'B': ['110', '101', '110', '101', '110'],
    'C': ['011', '100', '100', '100', '011'],
    'D': ['110', '101', '101', '101', '110'],
    'E': ['111', '100', '110', '100', '111'],
    'F': ['111', '100', '110', '100', '100'],
    'G': ['011', '100', '101', '101', '011'],
    'H': ['101', '101', '111', '101', '101'],
    'I': ['111', '010', '010', '010', '111'],
    'J': ['001', '001', '001', '101', '010'],
    'K': ['101', '101', '110', '101', '101'],
    'L': ['100', '100', '100', '100', '111'],
    'M': ['101', '111', '111', '101', '101'],
    'N': ['101', '111', '111', '111', '101'],
    'O': ['111', '101', '101', '101', '111'],
    'P': ['111', '101', '111', '100', '100'],
    'Q': ['111', '101', '101', '111', '001'],
    'R': ['110', '101', '110', '101', '101'],
    'S': ['011', '100', '111', '001', '110'],
    'T': ['111', '010', '010', '010', '010'],
    'U': ['101', '101', '101', '101', '111'],
    'V': ['101', '101', '101', '101', '010'],
    'W': ['101', '101', '111', '111', '101'],
    'X': ['101', '101', '010', '101', '101'],
    'Y': ['101', '101', '010', '010', '010'],
    'Z': ['111', '001', '010', '100', '111'],
    '-': ['000', '000', '111', '000', '000'],
    '>': ['100', '010', '001', '010', '100'],
    ':': ['000', '010', '000', '010', '000'],
    '.': ['000', '000', '000', '000', '010'],
    ' ': ['000', '000', '000', '000', '000'],
}

PALETTE = {
    0: (255, 240, 120),
    1: (90, 250, 220),
    2: (80, 210, 255),
    3: (90, 160, 255),
    4: (130, 110, 255),
    5: (190, 90, 255),
    6: (255, 90, 190),
    7: (255, 80, 120),
    'zero': (110, 40, 40),
}


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
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i:i + 3] = bytes(max(0, min(255, c)) for c in color)


def blend_px(buf, x, y, color, alpha):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        old = buf[i:i + 3]
        buf[i:i + 3] = bytes(int(old[k] * (1 - alpha) + color[k] * alpha) for k in range(3))


def rect(buf, x0, y0, x1, y1, color):
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    for y in range(max(0, y0), min(H, y1)):
        i = (y * W + max(0, x0)) * 3
        row = bytes(color) * max(0, min(W, x1) - max(0, x0))
        buf[i:i + len(row)] = row


def line(buf, x0, y0, x1, y1, color):
    x0, y0, x1, y1 = map(int, (x0, y0, x1, y1))
    dx = abs(x1 - x0)
    sx = 1 if x0 < x1 else -1
    dy = -abs(y1 - y0)
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        set_px(buf, x0, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def glow_dot(buf, cx, cy, r, color):
    x0, x1 = int(cx - r * 2), int(cx + r * 2) + 1
    y0, y1 = int(cy - r * 2), int(cy + r * 2) + 1
    for y in range(y0, y1):
        for x in range(x0, x1):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if d <= r * 2:
                a = max(0.0, 1 - d / (r * 2))
                blend_px(buf, x, y, color, 0.18 * a)
    for y in range(int(cy - r), int(cy + r) + 1):
        for x in range(int(cx - r), int(cx + r) + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                set_px(buf, x, y, color)


def draw_char(buf, x, y, ch, color, scale=2):
    patt = FONT.get(ch.upper(), FONT[' '])
    for ry, row in enumerate(patt):
        for rx, bit in enumerate(row):
            if bit == '1':
                rect(buf, x + rx * scale, y + ry * scale, x + (rx + 1) * scale, y + (ry + 1) * scale, color)


def draw_text(buf, x, y, text, color, scale=2, gap=1):
    cx = x
    for ch in text:
        draw_char(buf, cx, y, ch, color, scale)
        cx += (3 + gap) * scale


def step(n):
    s = f"{n:04d}"
    a = int(''.join(sorted(s, reverse=True)))
    b = int(''.join(sorted(s)))
    return a - b


def repdigit(n):
    return len(set(f"{n:04d}")) == 1


def chain(n):
    seq = [n]
    while seq[-1] not in (6174, 0):
        seq.append(step(seq[-1]))
        if len(seq) > 20:
            raise RuntimeError('unexpected loop')
    return seq


def main():
    buf = bytearray(W * H * 3)
    for y in range(H):
        for x in range(W):
            dx = (x - W / 2) / (W / 2)
            dy = (y - H / 2) / (H / 2)
            rad = (dx * dx + dy * dy) ** 0.5
            t = y / (H - 1)
            r = int(4 + 12 * t)
            g = int(6 + 18 * t)
            b = int(18 + 36 * t)
            vign = max(0.45, 1 - rad * 0.55)
            i = (y * W + x) * 3
            buf[i:i + 3] = bytes((int(r * vign), int(g * vign), int(b * vign)))

    rect(buf, GX0 - 16, GY0 - 16, GX0 + GW + 16, GY0 + GH + 16, (10, 16, 34))
    for k in range(0, 101, 10):
        c = (25, 40, 68) if k < 100 else (50, 80, 120)
        line(buf, GX0 + k * GRID, GY0, GX0 + k * GRID, GY0 + GH, c)
        line(buf, GX0, GY0 + k * GRID, GX0 + GW, GY0 + k * GRID, c)

    hist = Counter()
    max_steps = 0
    valid_count = 0
    for n in range(10000):
        x = n % 100
        y = n // 100
        if repdigit(n):
            steps = -1
            color = PALETTE['zero']
        else:
            seq = chain(n)
            steps = len(seq) - 1
            hist[steps] += 1
            valid_count += 1
            max_steps = max(max_steps, steps)
            color = PALETTE[steps]
        px = GX0 + x * GRID
        py = GY0 + y * GRID
        rect(buf, px + 1, py + 1, px + GRID - 1, py + GRID - 1, color)
        if steps >= 0:
            for oy in (-1, 0, 1):
                for ox in (-1, 0, 1):
                    if ox or oy:
                        blend_px(buf, px + GRID // 2 + ox, py + GRID // 2 + oy, color, 0.18)

    hx = GX0 + (6174 % 100) * GRID + GRID // 2
    hy = GY0 + (6174 // 100) * GRID + GRID // 2
    for rr in (6, 11, 16):
        for a in range(0, 360, 3):
            x = int(hx + math.cos(math.radians(a)) * rr)
            y = int(hy + math.sin(math.radians(a)) * rr)
            blend_px(buf, x, y, (255, 240, 120), 0.5 if rr == 6 else 0.22)
    glow_dot(buf, hx, hy, 4, (255, 250, 180))

    panel_x0 = 870
    max_hist = max(hist.values())
    for s in range(8):
        x0 = panel_x0 + s * 14
        h = int(hist[s] / max_hist * 250)
        rect(buf, x0, 530 - h, x0 + 10, 530, PALETTE[s])
        draw_text(buf, x0, 540, str(s), (180, 190, 220), scale=2)

    ly = 150
    for key in [0, 1, 2, 3, 4, 5, 6, 7]:
        rect(buf, 875, ly, 891, ly + 12, PALETTE[key])
        draw_text(buf, 900, ly + 1, f"{key} STEP" + ('S' if key != 1 else ''), (210, 220, 245), scale=2)
        ly += 24
    rect(buf, 875, ly + 4, 891, ly + 16, PALETTE['zero'])
    draw_text(buf, 900, ly + 5, 'REPDIGIT -> 0', (210, 220, 245), scale=2)

    cyan = (110, 230, 255)
    white = (230, 240, 255)
    dim = (150, 165, 190)
    gold = (255, 235, 140)
    pink = (255, 120, 180)

    draw_text(buf, 70, 34, 'KAPREKAR BLACK HOLE', white, scale=4)
    draw_text(buf, 72, 72, 'ALL 4-DIGIT NUMBERS FALL TOWARD 6174', cyan, scale=2)
    draw_text(buf, 70, 94, 'GRID: ROW=FIRST TWO DIGITS  COL=LAST TWO DIGITS', dim, scale=2)
    draw_text(buf, 875, 122, 'STEPS TO SINGULARITY', white, scale=2)

    for v in [0, 25, 50, 75, 99]:
        draw_text(buf, GX0 + v * GRID - 6, GY0 + GH + 12, f"{v:02d}", dim, scale=2)
        draw_text(buf, GX0 - 34, GY0 + v * GRID - 3, f"{v:02d}", dim, scale=2)

    avg_steps = sum(k * v for k, v in hist.items()) / valid_count
    draw_text(buf, 70, 760, f'VALID: {valid_count}', cyan, scale=2)
    draw_text(buf, 220, 760, 'REPDIGITS: 10', dim, scale=2)
    draw_text(buf, 380, 760, f'AVG STEPS: {avg_steps:.2f}', dim, scale=2)
    draw_text(buf, 610, 760, f'MAX: {max_steps}', pink, scale=2)
    draw_text(buf, 70, 790, f'7-STEP NUMBERS: {hist[7]}', pink, scale=2)
    draw_text(buf, 280, 790, 'ONLY 6174 NEEDS 0 STEPS', gold, scale=2)
    draw_text(buf, 560, 790, 'ALL NON-REPDIGITS REACH 6174', white, scale=2)

    rect(buf, 60, 806, 940, 852, (8, 14, 28))
    draw_text(buf, 70, 812, '0014 -> 4086 -> 8172 -> 7443 -> 3996 -> 6264 -> 4176 -> 6174', (210, 220, 245), scale=2)
    draw_text(buf, 70, 830, '3524 -> 3087 -> 8352 -> 6174', cyan, scale=2)
    draw_text(buf, 520, 830, '9831 -> 8442 -> 5994 -> 5355 -> 1998 -> 8082 -> 8532 -> 6174', pink, scale=2)

    for y in range(0, H, 3):
        for x in range(W):
            blend_px(buf, x, y, (0, 0, 0), 0.08)

    save_png(OUT, W, H, buf)

    print(f'png={OUT.name}')
    print(f'png_bytes={OUT.stat().st_size}')
    print(f'valid_count={valid_count}')
    print('repdigits=10')
    print(f'avg_steps={avg_steps:.4f}')
    print(f'max_steps={max_steps}')
    print(f'steps_7={hist[7]}')
    print(f'one_step={hist[1]}')
    print('sample_long=0014->4086->8172->7443->3996->6264->4176->6174')
    print('all_non_repdigits_reach=6174')


if __name__ == '__main__':
    main()
