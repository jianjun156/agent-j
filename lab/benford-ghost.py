from math import log10
from pathlib import Path
import struct, zlib

W, H = 1200, 800
BG = (4, 4, 15)
OUT = Path(__file__).with_suffix('.png')


def leading_digit_pow2(n: int) -> int:
    frac = (n * log10(2)) % 1.0
    return int(10 ** frac)


def benford(d: int) -> float:
    return log10(1 + 1 / d)


def make_canvas(w, h, bg):
    return [[list(bg) for _ in range(w)] for _ in range(h)]


def blend(px, x, y, color, alpha):
    if 0 <= x < W and 0 <= y < H:
        p = px[y][x]
        for i in range(3):
            p[i] = max(0, min(255, int(p[i] * (1 - alpha) + color[i] * alpha)))


def rect(px, x0, y0, x1, y1, color, alpha=1.0):
    x0, x1 = max(0, int(x0)), min(W, int(x1))
    y0, y1 = max(0, int(y0)), min(H, int(y1))
    for y in range(y0, y1):
        row = px[y]
        for x in range(x0, x1):
            p = row[x]
            for i in range(3):
                p[i] = max(0, min(255, int(p[i] * (1 - alpha) + color[i] * alpha)))


def line(px, x0, y0, x1, y1, color, alpha=1.0):
    x0, y0, x1, y1 = map(int, [x0, y0, x1, y1])
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        blend(px, x0, y0, color, alpha)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


FONT = {
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
    '.': ['0','0','0','0','1'],
    '%': ['1001','0001','0010','0100','1001'],
    ':': ['0','1','0','1','0'],
    '-': ['000','000','111','000','000'],
    ' ': ['0','0','0','0','0'],
    'A': ['010','101','111','101','101'],
    'B': ['110','101','110','101','110'],
    'D': ['110','101','101','101','110'],
    'E': ['111','100','110','100','111'],
    'F': ['111','100','110','100','100'],
    'G': ['111','100','101','101','111'],
    'H': ['101','101','111','101','101'],
    'I': ['111','010','010','010','111'],
    'L': ['100','100','100','100','111'],
    'M': ['101','111','111','101','101'],
    'N': ['101','111','111','111','101'],
    'O': ['111','101','101','101','111'],
    'P': ['111','101','111','100','100'],
    'R': ['110','101','110','101','101'],
    'S': ['111','100','111','001','111'],
    'T': ['111','010','010','010','010'],
    'W': ['101','101','111','111','101'],
    'X': ['101','101','010','101','101'],
}


def text(px, s, x, y, scale, color):
    cx = x
    for ch in s.upper():
        g = FONT.get(ch)
        if not g:
            cx += 4 * scale
            continue
        gw = len(g[0])
        for gy, row in enumerate(g):
            for gx, bit in enumerate(row):
                if bit == '1':
                    rect(px, cx + gx * scale, y + gy * scale,
                         cx + (gx + 1) * scale, y + (gy + 1) * scale, color)
        cx += (gw + 1) * scale


def save_png(px, path: Path):
    raw = bytearray()
    for row in px:
        raw.append(0)
        for r, g, b in row:
            raw.extend((r, g, b))
    comp = zlib.compress(bytes(raw), 9)
    def chunk(tag, data):
        return (
            struct.pack('>I', len(data)) + tag + data +
            struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
        )
    png = bytearray(b'\x89PNG\r\n\x1a\n')
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', comp)
    png += chunk(b'IEND', b'')
    path.write_bytes(png)


def main():
    N = 5000
    counts = [0] * 10
    for n in range(1, N + 1):
        counts[leading_digit_pow2(n)] += 1

    observed = [counts[d] / N for d in range(1, 10)]
    expected = [benford(d) for d in range(1, 10)]
    max_diff = max(abs(o - e) for o, e in zip(observed, expected))
    chi2 = sum((counts[d] - N * expected[d - 1]) ** 2 / (N * expected[d - 1]) for d in range(1, 10))

    px = make_canvas(W, H, BG)
    for y in range(H):
        for x in range(W):
            dx = (x - W / 2) / (W / 2)
            dy = (y - H / 2) / (H / 2)
            vignette = max(0.0, 1.0 - (dx * dx + dy * dy) * 0.45)
            row = px[y][x]
            row[0] = int(row[0] * vignette)
            row[1] = int(row[1] * vignette)
            row[2] = int(row[2] * vignette + 12 * vignette)
            if y % 3 == 0:
                row[1] = max(0, row[1] - 2)
                row[2] = max(0, row[2] - 2)

    chart_x0, chart_y0 = 120, 180
    chart_w, chart_h = 960, 430
    rect(px, chart_x0, chart_y0, chart_x0 + chart_w, chart_y0 + chart_h, (10, 20, 38), 0.85)

    for i in range(11):
        y = chart_y0 + int(chart_h * i / 10)
        line(px, chart_x0, y, chart_x0 + chart_w, y, (35, 70, 120), 0.5)
    for i in range(10):
        x = chart_x0 + int(chart_w * i / 9)
        line(px, x, chart_y0, x, chart_y0 + chart_h, (24, 48, 84), 0.35)

    max_p = 0.35
    cluster_w = chart_w / 9
    obs_w = 42
    exp_w = 16

    for idx, d in enumerate(range(1, 10)):
        cx = chart_x0 + cluster_w * idx + cluster_w / 2
        obs_h = observed[idx] / max_p * chart_h
        exp_h = expected[idx] / max_p * chart_h
        ox0 = int(cx - obs_w / 2)
        ex0 = int(cx + obs_w / 2 - exp_w)
        for glow in range(8, 0, -1):
            rect(px, ox0 - glow, chart_y0 + chart_h - obs_h - glow,
                 ox0 + obs_w + glow, chart_y0 + chart_h + glow,
                 (0, 180, 255), 0.025)
        rect(px, ox0, chart_y0 + chart_h - obs_h, ox0 + obs_w, chart_y0 + chart_h, (46, 212, 255), 0.95)
        rect(px, ox0, chart_y0 + chart_h - obs_h, ox0 + obs_w, chart_y0 + chart_h - obs_h + 8, (220, 250, 255), 0.65)
        rect(px, ex0, chart_y0 + chart_h - exp_h, ex0 + exp_w, chart_y0 + chart_h, (191, 90, 255), 0.95)
        text(px, str(d), int(cx - 6), chart_y0 + chart_h + 26, 4, (180, 220, 255))
        text(px, f'{observed[idx]*100:.1f}%', int(cx - 28), int(chart_y0 + chart_h - obs_h - 34), 2, (180, 245, 255))

    text(px, 'BENFORD GHOST', 120, 70, 7, (240, 248, 255))
    text(px, 'POWERS OF TWO KEEP FALLING FOR 1', 122, 120, 3, (118, 212, 255))
    text(px, 'OBSERVED', 842, 92, 3, (80, 220, 255))
    rect(px, 808, 94, 834, 108, (46, 212, 255), 0.95)
    text(px, 'BENFORD', 842, 124, 3, (210, 128, 255))
    rect(px, 808, 126, 824, 140, (191, 90, 255), 0.95)

    text(px, 'LEADING DIGIT', 500, 660, 3, (170, 210, 255))
    text(px, '0.0%', 54, 600, 3, (110, 170, 230))
    text(px, '17.5%', 42, 390, 3, (110, 170, 230))
    text(px, '35.0%', 42, 176, 3, (110, 170, 230))

    text(px, f'N: {N}', 120, 716, 3, (170, 230, 255))
    text(px, f'MAX DIFF: {max_diff*100:.2f}%', 330, 716, 3, (170, 230, 255))
    text(px, f'CHI2: {chi2:.3f}', 700, 716, 3, (170, 230, 255))

    save_png(px, OUT)
    print('Counts:', counts[1:])
    print('Observed:', [round(x, 4) for x in observed])
    print('Expected:', [round(x, 4) for x in expected])
    print('Max diff:', round(max_diff, 6))
    print('Chi2:', round(chi2, 6))
    print('Saved:', OUT)


if __name__ == '__main__':
    main()
