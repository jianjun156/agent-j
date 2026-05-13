import math, struct, zlib, statistics
from pathlib import Path

OUT = Path(__file__).with_suffix('.png')
W, H = 1320, 820
BG = (4, 6, 18)
N = 2600
GOLDEN_ANGLE = math.pi * (3 - math.sqrt(5))  # 137.507764°
PANELS = [
    (math.radians(137.0), "137.000°"),
    (GOLDEN_ANGLE, "137.508° GOLDEN"),
    (math.radians(144.0), "144.000° = 2/5 TURN"),
]


def canvas():
    return bytearray(BG * (W * H))


def blend(px, x, y, color, alpha):
    if not (0 <= x < W and 0 <= y < H):
        return
    i = (y * W + x) * 3
    ia = 1 - alpha
    px[i] = min(255, int(px[i] * ia + color[0] * alpha))
    px[i + 1] = min(255, int(px[i + 1] * ia + color[1] * alpha))
    px[i + 2] = min(255, int(px[i + 2] * ia + color[2] * alpha))


def dot(px, x, y, r, color, alpha=1.0):
    rr = int(math.ceil(r))
    for dy in range(-rr, rr + 1):
        for dx in range(-rr, rr + 1):
            d2 = dx * dx + dy * dy
            if d2 <= r * r:
                edge = max(0.25, 1 - d2 / (r * r + 0.001))
                blend(px, int(x) + dx, int(y) + dy, color, alpha * edge)


def line(px, x0, y0, x1, y1, color, alpha=0.45):
    steps = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    for i in range(steps + 1):
        t = i / steps if steps else 0
        x = int(round(x0 + (x1 - x0) * t))
        y = int(round(y0 + (y1 - y0) * t))
        blend(px, x, y, color, alpha)


# tiny 3x5 bitmap font for labels / numbers
FONT = {
    '0': ['111','101','101','101','111'], '1': ['010','110','010','010','111'],
    '2': ['111','001','111','100','111'], '3': ['111','001','111','001','111'],
    '4': ['101','101','111','001','001'], '5': ['111','100','111','001','111'],
    '6': ['111','100','111','101','111'], '7': ['111','001','010','010','010'],
    '8': ['111','101','111','101','111'], '9': ['111','101','111','001','111'],
    '.': ['000','000','000','000','010'], '°': ['010','101','010','000','000'],
    '=': ['000','111','000','111','000'], '/': ['001','001','010','100','100'],
    ' ': ['000','000','000','000','000'], '-': ['000','000','111','000','000'],
    'A': ['010','101','111','101','101'], 'D': ['110','101','101','101','110'],
    'E': ['111','100','110','100','111'], 'G': ['111','100','101','101','111'],
    'L': ['100','100','100','100','111'], 'N': ['101','111','111','111','101'],
    'O': ['111','101','101','101','111'], 'R': ['110','101','110','101','101'],
    'T': ['111','010','010','010','010'], 'U': ['101','101','101','101','111'],
}


def text(px, x, y, s, color=(120, 220, 255), scale=3, alpha=0.85):
    ox = x
    for ch in s.upper():
        glyph = FONT.get(ch, FONT[' '])
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == '1':
                    for sy in range(scale):
                        for sx in range(scale):
                            blend(px, x + gx * scale + sx, y + gy * scale + sy, color, alpha)
        x += 4 * scale
    return x - ox


def phyllotaxis_points(angle, cx, cy, radius):
    pts = []
    c = radius / math.sqrt(N + 8)
    for n in range(N):
        r = c * math.sqrt(n + 0.5)
        a = n * angle
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a), r / radius, n))
    return pts


def metrics(angle):
    # occupancy uniformity on 36 angular bins: lower variance means fewer spoke clumps.
    bins = [0] * 36
    for n in range(N):
        a = (n * angle) % (2 * math.pi)
        bins[int(a / (2 * math.pi) * 36) % 36] += 1
    mean = sum(bins) / len(bins)
    cv = statistics.pstdev(bins) / mean

    # nearest-neighbor spread sampled every 13th point: golden angle keeps distances steadier.
    pts = [(math.sqrt(n + 0.5) * math.cos(n * angle), math.sqrt(n + 0.5) * math.sin(n * angle)) for n in range(N)]
    dists = []
    for i in range(0, N, 13):
        x, y = pts[i]
        best = 1e9
        for j in range(max(0, i - 200), min(N, i + 201)):
            if i == j:
                continue
            x2, y2 = pts[j]
            d = (x - x2) ** 2 + (y - y2) ** 2
            if d < best:
                best = d
        dists.append(math.sqrt(best))
    nn_cv = statistics.pstdev(dists) / (sum(dists) / len(dists))
    return cv, nn_cv, min(bins), max(bins)


def render():
    px = canvas()
    # subtle starfield / scanlines
    for y in range(0, H, 4):
        for x in range(W):
            blend(px, x, y, (8, 16, 38), 0.25)
    for k in range(360):
        x = (k * 97) % W
        y = (k * 193) % H
        blend(px, x, y, (70, 120, 180), 0.35)

    centers = [(220, 410), (660, 410), (1100, 410)]
    radius = 305
    all_metrics = []
    for idx, ((angle, label), (cx, cy)) in enumerate(zip(PANELS, centers)):
        # panel frame and rings
        for rr in (80, 160, 240, 305):
            for k in range(720):
                a = 2 * math.pi * k / 720
                blend(px, int(cx + rr * math.cos(a)), int(cy + rr * math.sin(a)), (20, 60, 110), 0.22)
        for k in range(12):
            a = 2 * math.pi * k / 12
            line(px, cx, cy, cx + radius * math.cos(a), cy + radius * math.sin(a), (12, 45, 85), 0.20)

        pts = phyllotaxis_points(angle, cx, cy, radius)
        for x, y, t, n in pts:
            # cyan -> violet -> gold as the seed index grows
            if t < 0.55:
                u = t / 0.55
                col = (int(45 + 45 * u), int(210 - 55 * u), 255)
            else:
                u = (t - 0.55) / 0.45
                col = (int(90 + 165 * u), int(155 - 55 * u), int(255 - 120 * u))
            if idx == 1:
                dot(px, x, y, 2.05, col, 0.82)
            else:
                dot(px, x, y, 1.75, col, 0.62)
        # bright center and label
        dot(px, cx, cy, 6, (255, 255, 255), 0.8)
        text(px, cx - 150, 55, label, (125, 230, 255) if idx == 1 else (110, 150, 210), 4, 0.9)
        cv, nn_cv, bmin, bmax = metrics(angle)
        all_metrics.append((label, cv, nn_cv, bmin, bmax))
        text(px, cx - 118, 720, f"CV {cv:.3f}", (120, 230, 255), 3, 0.72)
        text(px, cx - 118, 752, f"NN {nn_cv:.3f}", (190, 120, 255), 3, 0.72)

    text(px, 24, 24, "PHYLLOTAXIS ORACLE", (95, 255, 190), 5, 0.95)
    text(px, 24, 780, "2600 SEEDS / ZERO DEPS / GOLDEN ANGLE MINIMIZES VISIBLE SPOKES", (120, 180, 255), 3, 0.7)
    write_png(OUT, W, H, px)
    return all_metrics


def write_png(path, width, height, rgb):
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)
        raw.extend(rgb[y * stride:(y + 1) * stride])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        return len(data).to_bytes(4, 'big') + tag + data + (zlib.crc32(tag + data) & 0xffffffff).to_bytes(4, 'big')

    png = bytearray(b'\x89PNG\r\n\x1a\n')
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', comp)
    png += chunk(b'IEND', b'')
    path.write_bytes(png)


if __name__ == '__main__':
    ms = render()
    for label, cv, nn_cv, bmin, bmax in ms:
        print(f"{label}: angular_cv={cv:.4f} nn_cv={nn_cv:.4f} bin_range={bmin}-{bmax}")
    best = min(ms, key=lambda row: row[1] + row[2])
    print(f"winner={best[0]} score={best[1] + best[2]:.4f}")
    print(f"golden_angle_deg={math.degrees(GOLDEN_ANGLE):.9f}")
    print(f"seeds={N} image={OUT} bytes={OUT.stat().st_size}")
