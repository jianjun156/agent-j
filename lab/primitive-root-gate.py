import math, struct, zlib
from pathlib import Path

OUT = Path(__file__).with_suffix('.png')
MOD = 257
GEN = 97
W, H = 1400, 1400
CX, CY = W // 2, H // 2
R = 520
BG = (4, 6, 18)


def primitive_root_order(g, mod):
    cur = 1
    for k in range(1, mod):
        cur = (cur * g) % mod
        if cur == 1:
            return k
    return None


def palette(t):
    if t < 0.5:
        u = t / 0.5
        return (
            int(50 + (80 - 50) * u),
            int(220 + (120 - 220) * u),
            255,
        )
    u = (t - 0.5) / 0.5
    return (
        int(80 + (255 - 80) * u),
        int(120 + (70 - 120) * u),
        int(255 + (220 - 255) * u),
    )


def make_canvas():
    return bytearray(BG * (W * H))


def blend(px, x, y, color, alpha):
    if not (0 <= x < W and 0 <= y < H):
        return
    i = (y * W + x) * 3
    for c in range(3):
        base = px[i + c]
        px[i + c] = min(255, int(base * (1 - alpha) + color[c] * alpha))


def glow(px, x, y, color, strength=1.0):
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            d2 = dx * dx + dy * dy
            if d2 > 16:
                continue
            a = max(0.0, (1 - d2 / 16.0)) * 0.18 * strength
            if a:
                blend(px, x + dx, y + dy, color, a)


def line(px, x0, y0, x1, y1, color, glow_strength=1.0):
    dx = x1 - x0
    dy = y1 - y0
    steps = int(max(abs(dx), abs(dy))) + 1
    for i in range(steps + 1):
        t = i / steps if steps else 0
        x = int(round(x0 + dx * t))
        y = int(round(y0 + dy * t))
        glow(px, x, y, color, glow_strength)
        blend(px, x, y, (255, 255, 255), 0.75)


def circle(px, x, y, rr, color, alpha=1.0):
    for dy in range(-rr, rr + 1):
        for dx in range(-rr, rr + 1):
            if dx * dx + dy * dy <= rr * rr:
                blend(px, x + dx, y + dy, color, alpha)


def write_png(path, width, height, rgb):
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)
        raw.extend(rgb[y * stride:(y + 1) * stride])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        return (
            len(data).to_bytes(4, 'big') + tag + data +
            (zlib.crc32(tag + data) & 0xffffffff).to_bytes(4, 'big')
        )

    png = bytearray(b'\x89PNG\r\n\x1a\n')
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', comp)
    png += chunk(b'IEND', b'')
    path.write_bytes(png)


order = primitive_root_order(GEN, MOD)
seq = [1]
for _ in range(order):
    seq.append((seq[-1] * GEN) % MOD)

points = {}
for n in range(1, MOD):
    ang = -math.pi / 2 + 2 * math.pi * (n - 1) / (MOD - 1)
    points[n] = (int(CX + R * math.cos(ang)), int(CY + R * math.sin(ang)))

px = make_canvas()

for rr in range(120, 621, 80):
    for k in range(720):
        ang = 2 * math.pi * k / 720
        x = int(CX + rr * math.cos(ang))
        y = int(CY + rr * math.sin(ang))
        blend(px, x, y, (18, 55, 95), 0.08)

for n in range(1, MOD, 16):
    x, y = points[n]
    line(px, CX, CY, x, y, (18, 90, 140), 0.2)

for i in range(len(seq) - 1):
    a, b = seq[i], seq[i + 1]
    x0, y0 = points[a]
    x1, y1 = points[b]
    color = palette(i / (len(seq) - 2))
    line(px, x0, y0, x1, y1, color, 0.9)

for n, (x, y) in points.items():
    circle(px, x, y, 2, (120, 210, 255), 0.55)

xs, ys = points[1]
for rr in range(5, 16, 2):
    for ang_i in range(360):
        ang = 2 * math.pi * ang_i / 360
        blend(px, int(xs + rr * math.cos(ang)), int(ys + rr * math.sin(ang)), (255, 110, 240), 0.35)

write_png(OUT, W, H, px)

lengths = []
lookup = {}
for n in range(1, MOD):
    ang = -math.pi / 2 + 2 * math.pi * (n - 1) / (MOD - 1)
    lookup[n] = (R * math.cos(ang), R * math.sin(ang))
for a, b in zip(seq, seq[1:]):
    x0, y0 = lookup[a]
    x1, y1 = lookup[b]
    lengths.append(math.hypot(x1 - x0, y1 - y0))

print(f"mod={MOD} generator={GEN} order={order} cycle_len={len(set(seq[:-1]))}")
print("first12=" + "→".join(map(str, seq[:12])))
print(f"mean_chord={sum(lengths) / len(lengths):.3f}")
print(f"max_chord={max(lengths):.3f}")
print(f"image={OUT} bytes={OUT.stat().st_size}")
