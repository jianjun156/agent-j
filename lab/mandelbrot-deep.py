#!/usr/bin/env python3
"""
EXP-20260406-020: MANDELBROT-ABYSS
Deep zoom into the Mandelbrot set boundary — finding a Mini-Mandelbrot.
Uses inline C for the hot loop. Hand-rolled PNG encoder.
"""
import struct, zlib, math, time, ctypes, tempfile, os, subprocess

WIDTH, HEIGHT = 600, 450
MAX_ITER = 500

# Four views: overview + progressive zooms into a known Mini-Mandelbrot
# The famous Mini-Mandelbrot at the tip of the main antenna:
# Located near c = -1.768 (a well-known location)
# Another classic: Seahorse Valley mini-brot near (-0.743643887037151, 0.131825904205330)
VIEWS = [
    (-0.5, 0.0, 3.5, "Overview · 1×"),
    (-0.743644, 0.131826, 0.01, "Seahorse Valley · 350×"),
    (-0.7436439, 0.1318260, 0.0006, "Spiral Detail · 5,833×"),
    (-0.74364388703, 0.13182590421, 0.00002, "Mini-Mandelbrot · 175,000×"),
]

# ---- Compile C accelerator ----
C_SRC = r"""
#include <math.h>

void mandelbrot_render(
    double cx, double cy, double view_w,
    int img_w, int img_h, int max_iter,
    double *out_iters
) {
    double view_h = view_w * img_h / img_w;
    double x_min = cx - view_w / 2.0;
    double y_min = cy - view_h / 2.0;
    double dx = view_w / img_w;
    double dy = view_h / img_h;
    
    for (int py = 0; py < img_h; py++) {
        double imag = y_min + py * dy;
        for (int px = 0; px < img_w; px++) {
            double real = x_min + px * dx;
            double zx = 0.0, zy = 0.0;
            int i;
            for (i = 0; i < max_iter; i++) {
                double zx2 = zx * zx, zy2 = zy * zy;
                if (zx2 + zy2 > 256.0) {
                    double log_zn = log(zx2 + zy2) / 2.0;
                    double nu = log(log_zn / log(2.0)) / log(2.0);
                    out_iters[py * img_w + px] = (double)i + 1.0 - nu;
                    goto next_pixel;
                }
                zy = 2.0 * zx * zy + imag;
                zx = zx2 - zy2 + real;
            }
            out_iters[py * img_w + px] = (double)max_iter;
            next_pixel:;
        }
    }
}
"""

print("🔬 MANDELBROT-ABYSS: Deep zoom — finding the Mini-Mandelbrot")
print(f"   Canvas: {WIDTH}×{HEIGHT} per panel, Max iterations: {MAX_ITER}")
print()

# Compile C
tmpdir = tempfile.mkdtemp()
c_path = os.path.join(tmpdir, "mandelbrot.c")
so_path = os.path.join(tmpdir, "mandelbrot.so")

with open(c_path, "w") as f:
    f.write(C_SRC)

print("   Compiling C accelerator...")
result = subprocess.run(
    ["cc", "-O2", "-shared", "-fPIC", "-o", so_path, c_path, "-lm"],
    capture_output=True, text=True
)
if result.returncode != 0:
    print(f"   ❌ Compile failed: {result.stderr}")
    exit(1)

lib = ctypes.CDLL(so_path)
lib.mandelbrot_render.argtypes = [
    ctypes.c_double, ctypes.c_double, ctypes.c_double,
    ctypes.c_int, ctypes.c_int, ctypes.c_int,
    ctypes.POINTER(ctypes.c_double)
]
lib.mandelbrot_render.restype = None
print("   ✅ C accelerator ready\n")

def color_from_iter(n, max_iter):
    """Map iteration count to a rich cyberpunk palette with smooth gradients."""
    if n >= max_iter:
        return (0, 0, 0)
    
    # Log scaling for better color distribution
    t = math.log(1 + n) / math.log(1 + max_iter)
    
    # Rich palette: deep ocean → electric blue → cyan → gold → fire → magenta → deep purple
    palette = [
        (0.0,    2,   4,  30),
        (0.04,   5,  20,  80),
        (0.10,  10,  50, 160),
        (0.18,   0, 130, 220),
        (0.28,   0, 220, 255),
        (0.38,  40, 255, 200),
        (0.48, 180, 255,  60),
        (0.55, 255, 220,   0),
        (0.62, 255, 150,   0),
        (0.70, 255,  60,  30),
        (0.78, 230,  30, 120),
        (0.86, 180,  20, 200),
        (0.94, 100,  10, 160),
        (1.0,   30,   5,  60),
    ]
    
    for i in range(len(palette) - 1):
        t0, r0, g0, b0 = palette[i]
        t1, r1, g1, b1 = palette[i + 1]
        if t <= t1:
            f = (t - t0) / (t1 - t0) if t1 > t0 else 0
            # Smooth interpolation
            f = f * f * (3 - 2 * f)  # smoothstep
            r = int(r0 + (r1 - r0) * f)
            g = int(g0 + (g1 - g0) * f)
            b = int(b0 + (b1 - b0) * f)
            return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
    
    return (30, 5, 60)

def make_png(pixel_data, width, height):
    """Hand-rolled PNG encoder."""
    def chunk(ctype, data):
        c = ctype + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xFFFFFFFF)
    
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
    
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            r, g, b = pixel_data[y * width + x]
            raw.extend((r, g, b))
    
    idat = chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    iend = chunk(b'IEND', b'')
    
    return sig + ihdr + idat + iend

def draw_box(composite, x1, y1, x2, y2, color, comp_w, comp_h, thickness=2):
    """Draw rectangle outline."""
    for x in range(max(0, x1), min(comp_w, x2 + 1)):
        for t in range(thickness):
            if 0 <= y1 + t < comp_h:
                composite[(y1 + t) * comp_w + x] = color
            if 0 <= y2 - t < comp_h:
                composite[(y2 - t) * comp_w + x] = color
    for y in range(max(0, y1), min(comp_h, y2 + 1)):
        for t in range(thickness):
            if 0 <= x1 + t < comp_w:
                composite[y * comp_w + x1 + t] = color
            if 0 <= x2 - t < comp_w:
                composite[y * comp_w + x2 - t] = color

# ---- Render all views ----
COMP_W = WIDTH * 2
COMP_H = HEIGHT * 2

composite = [(0, 0, 0)] * (COMP_W * COMP_H)
all_stats = []

for idx, (cx, cy, vw, label) in enumerate(VIEWS):
    t0 = time.time()
    print(f"   Rendering {idx+1}/4: {label}...")
    
    buf = (ctypes.c_double * (WIDTH * HEIGHT))()
    lib.mandelbrot_render(cx, cy, vw, WIDTH, HEIGHT, MAX_ITER, buf)
    elapsed = time.time() - t0
    
    inside = sum(1 for i in range(WIDTH * HEIGHT) if buf[i] >= MAX_ITER)
    max_n = max(buf[i] for i in range(WIDTH * HEIGHT) if buf[i] < MAX_ITER) if inside < WIDTH * HEIGHT else 0
    
    pct_inside = inside / (WIDTH * HEIGHT) * 100
    zoom = 3.5 / vw
    
    all_stats.append({
        'label': label, 'cx': cx, 'cy': cy, 'vw': vw,
        'inside': inside, 'pct_inside': pct_inside,
        'max_n': max_n, 'elapsed': elapsed, 'zoom': zoom
    })
    
    print(f"   ✅ {label}: {elapsed:.2f}s, inside={pct_inside:.1f}%, max_iter={max_n:.0f}, zoom={zoom:,.0f}x")
    
    # Color and place into composite
    ox = (idx % 2) * WIDTH
    oy = (idx // 2) * HEIGHT
    
    for py in range(HEIGHT):
        for px in range(WIDTH):
            n = buf[py * WIDTH + px]
            color = color_from_iter(n, MAX_ITER)
            composite[(oy + py) * COMP_W + (ox + px)] = color

# Draw panel borders (3px cyan)
for y in range(COMP_H):
    for dx in range(-1, 2):
        x = WIDTH + dx
        if 0 <= x < COMP_W:
            composite[y * COMP_W + x] = (0, 200, 255)
for x in range(COMP_W):
    for dy in range(-1, 2):
        y = HEIGHT + dy
        if 0 <= y < COMP_H:
            composite[y * COMP_W + x] = (0, 200, 255)

# Draw zoom indicator on panel 1 → panel 2
v1 = VIEWS[0]
v2 = VIEWS[1]
v1_xmin = v1[0] - v1[2] / 2
v1_ymin = v1[1] - (v1[2] * HEIGHT / WIDTH) / 2
pcx = int((v2[0] - v1_xmin) / v1[2] * WIDTH)
pcy = int((v2[1] - v1_ymin) / (v1[2] * HEIGHT / WIDTH) * HEIGHT)
phw = max(4, int(v2[2] / v1[2] * WIDTH / 2))
phh = max(4, int(v2[2] / v1[2] * HEIGHT / 2))
draw_box(composite, pcx - phw, pcy - phh, pcx + phw, pcy + phh, (255, 255, 0), COMP_W, COMP_H)

# Draw zoom indicator on panel 2 → panel 3
v2p = VIEWS[1]
v3 = VIEWS[2]
v2_xmin = v2p[0] - v2p[2] / 2
v2_ymin = v2p[1] - (v2p[2] * HEIGHT / WIDTH) / 2
ox2 = WIDTH  # panel 2 offset
pcx2 = ox2 + int((v3[0] - v2_xmin) / v2p[2] * WIDTH)
pcy2 = int((v3[1] - v2_ymin) / (v2p[2] * HEIGHT / WIDTH) * HEIGHT)
phw2 = max(4, int(v3[2] / v2p[2] * WIDTH / 2))
phh2 = max(4, int(v3[2] / v2p[2] * HEIGHT / 2))
draw_box(composite, pcx2 - phw2, pcy2 - phh2, pcx2 + phw2, pcy2 + phh2, (255, 255, 0), COMP_W, COMP_H)

# Draw zoom indicator on panel 3 → panel 4
v3p = VIEWS[2]
v4 = VIEWS[3]
v3_xmin = v3p[0] - v3p[2] / 2
v3_ymin = v3p[1] - (v3p[2] * HEIGHT / WIDTH) / 2
oy3 = HEIGHT  # panel 3 offset
pcx3 = int((v4[0] - v3_xmin) / v3p[2] * WIDTH)
pcy3 = oy3 + int((v4[1] - v3_ymin) / (v3p[2] * HEIGHT / WIDTH) * HEIGHT)
phw3 = max(4, int(v4[2] / v3p[2] * WIDTH / 2))
phh3 = max(4, int(v4[2] / v3p[2] * HEIGHT / 2))
draw_box(composite, pcx3 - phw3, pcy3 - phh3, pcx3 + phw3, pcy3 + phh3, (255, 255, 0), COMP_W, COMP_H)

# PNG encode
print("\n   Encoding PNG...")
t0 = time.time()
png_data = make_png(composite, COMP_W, COMP_H)
encode_time = time.time() - t0
print(f"   PNG: {len(png_data)/1024:.0f}KB in {encode_time:.1f}s")

out_path = '/Users/jianjun/.openclaw/workspace/agent-j/lab/mandelbrot-deep.png'
with open(out_path, 'wb') as f:
    f.write(png_data)

print(f"\n   📸 Saved: {out_path}")
print()
print("=" * 60)
print("   📊 MANDELBROT-ABYSS RESULTS")
print("=" * 60)
for s in all_stats:
    print(f"   [{s['label']}]")
    print(f"     Zoom: {s['zoom']:,.0f}x | Inside: {s['pct_inside']:.1f}% | Time: {s['elapsed']:.2f}s")

total = sum(s['elapsed'] for s in all_stats) + encode_time
print(f"\n   Total: {total:.1f}s | Final zoom: {all_stats[-1]['zoom']:,.0f}x")
print(f"   Total pixels rendered: {COMP_W * COMP_H:,}")
print()
print("   🔬 At 175,000× zoom, we find a miniature Mandelbrot set —")
print("   identical in shape to the whole, yet infinitely smaller.")
print("   The boundary of the Mandelbrot set is the most complex object")
print("   in mathematics: infinite detail at every scale, forever. 🌀")

# Cleanup
os.unlink(c_path)
os.unlink(so_path)
os.rmdir(tmpdir)
