#!/usr/bin/env python3
"""
EXP-20260408-021: VORONOI-CRYSTAL
用 150 个随机种子点生成 Voronoi 图，每个区域着色为独特的宝石色调，
边界处绘制发光边缘。叠加种子点标记和距离场等高线。
纯 Python + struct + zlib，零外部依赖。
"""

import random
import struct
import zlib
import math
import time

random.seed(42)

W, H = 800, 600
N_SEEDS = 150

# Generate random seed points
seeds = [(random.randint(20, W-20), random.randint(20, H-20)) for _ in range(N_SEEDS)]

# Cyberpunk gem palette - generate unique hue for each seed
def hsl_to_rgb(h, s, l):
    """Convert HSL to RGB (all 0-1 range)"""
    if s == 0:
        r = g = b = l
    else:
        def hue2rgb(p, q, t):
            if t < 0: t += 1
            if t > 1: t -= 1
            if t < 1/6: return p + (q - p) * 6 * t
            if t < 1/2: return q
            if t < 2/3: return p + (q - p) * (2/3 - t) * 6
            return p
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue2rgb(p, q, h + 1/3)
        g = hue2rgb(p, q, h)
        b = hue2rgb(p, q, h - 1/3)
    return (int(r * 255), int(g * 255), int(b * 255))

# Generate colors for each cell - spread across hue wheel with varying saturation/lightness
cell_colors = []
for i in range(N_SEEDS):
    hue = (i * 0.618033988749895) % 1.0  # golden ratio for even distribution
    sat = 0.5 + 0.3 * math.sin(i * 0.7)  # 0.2 to 0.8
    lit = 0.25 + 0.15 * math.cos(i * 1.3)  # 0.1 to 0.4 (dark, gem-like)
    cell_colors.append(hsl_to_rgb(hue, sat, lit))

print(f"Generating Voronoi diagram: {W}x{H}, {N_SEEDS} seeds...")
t0 = time.time()

# Compute Voronoi using brute force (nearest seed for each pixel)
# Store: cell_id, min_dist, second_min_dist for each pixel
pixels = bytearray(W * H * 3)
edge_map = bytearray(W * H)  # 0 or 255 for edge detection

cell_id_map = [[0]*W for _ in range(H)]
dist1_map = [[0.0]*W for _ in range(H)]
dist2_map = [[0.0]*W for _ in range(H)]

# Optimization: use squared distances
for y in range(H):
    if y % 50 == 0:
        print(f"  Row {y}/{H}...")
    for x in range(W):
        min_d2 = float('inf')
        min2_d2 = float('inf')
        min_id = 0
        for i, (sx, sy) in enumerate(seeds):
            d2 = (x - sx) ** 2 + (y - sy) ** 2
            if d2 < min_d2:
                min2_d2 = min_d2
                min_d2 = d2
                min_id = i
            elif d2 < min2_d2:
                min2_d2 = d2
        cell_id_map[y][x] = min_id
        dist1_map[y][x] = math.sqrt(min_d2)
        dist2_map[y][x] = math.sqrt(min2_d2)

t1 = time.time()
print(f"  Voronoi computed in {t1-t0:.1f}s")

# Render pixels
for y in range(H):
    for x in range(W):
        cid = cell_id_map[y][x]
        d1 = dist1_map[y][x]
        d2 = dist2_map[y][x]
        
        # Edge detection: difference between closest and second closest
        edge_strength = d2 - d1
        
        # Base color from cell
        r0, g0, b0 = cell_colors[cid]
        
        # Inner glow: slightly brighter near seed, darker near edges
        # Normalize distance within cell (approximate)
        max_cell_dist = d2  # approximate cell radius
        if max_cell_dist > 0:
            norm_dist = d1 / max_cell_dist
        else:
            norm_dist = 0
        
        # Gem-like shading: bright center, darker edges
        brightness = 1.0 + 0.4 * (1.0 - norm_dist)  # 1.0 to 1.4 from edge to center
        
        # Add subtle distance-based texture (concentric rings inside each cell)
        ring_freq = 0.15
        ring = 0.5 + 0.5 * math.sin(d1 * ring_freq)
        brightness *= (0.9 + 0.1 * ring)
        
        r = min(255, int(r0 * brightness))
        g = min(255, int(g0 * brightness))
        b = min(255, int(b0 * brightness))
        
        # Edge glow: bright cyan/white at cell boundaries
        if edge_strength < 3.0:
            # Strong edge - bright glow
            edge_t = edge_strength / 3.0
            glow_r, glow_g, glow_b = 100, 255, 255  # cyan glow
            t_blend = 1.0 - edge_t
            r = min(255, int(r * (1 - t_blend * 0.7) + glow_r * t_blend * 0.7))
            g = min(255, int(g * (1 - t_blend * 0.7) + glow_g * t_blend * 0.7))
            b = min(255, int(b * (1 - t_blend * 0.7) + glow_b * t_blend * 0.7))
        elif edge_strength < 6.0:
            # Softer glow
            edge_t = (edge_strength - 3.0) / 3.0
            t_blend = (1.0 - edge_t) * 0.3
            r = min(255, int(r * (1 - t_blend) + 70 * t_blend))
            g = min(255, int(g * (1 - t_blend) + 200 * t_blend))
            b = min(255, int(b * (1 - t_blend) + 200 * t_blend))
        
        # Vignette
        vx = (x - W/2) / (W/2)
        vy = (y - H/2) / (H/2)
        vignette = 1.0 - 0.4 * (vx*vx + vy*vy)
        vignette = max(0.3, min(1.0, vignette))
        r = int(r * vignette)
        g = int(g * vignette)
        b = int(b * vignette)
        
        idx = (y * W + x) * 3
        pixels[idx] = r
        pixels[idx+1] = g
        pixels[idx+2] = b

# Draw seed points as small bright dots
for i, (sx, sy) in enumerate(seeds):
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            px, py = sx + dx, sy + dy
            if 0 <= px < W and 0 <= py < H:
                dist_sq = dx*dx + dy*dy
                if dist_sq <= 4:  # circle radius 2
                    idx = (py * W + px) * 3
                    pixels[idx] = 255
                    pixels[idx+1] = 255
                    pixels[idx+2] = 255

# Add title text area at top
# Simple: darken top strip
for y in range(35):
    for x in range(W):
        idx = (y * W + x) * 3
        alpha = 0.4 if y < 30 else 0.4 * (35 - y) / 5
        pixels[idx] = int(pixels[idx] * (1 - alpha))
        pixels[idx+1] = int(pixels[idx+1] * (1 - alpha))
        pixels[idx+2] = int(pixels[idx+2] * (1 - alpha))

# Add stats text area at bottom
for y in range(H-45, H):
    for x in range(W):
        idx = (y * W + x) * 3
        alpha = 0.5 if y > H-40 else 0.5 * (y - (H-45)) / 5
        pixels[idx] = int(pixels[idx] * (1 - alpha))
        pixels[idx+1] = int(pixels[idx+1] * (1 - alpha))
        pixels[idx+2] = int(pixels[idx+2] * (1 - alpha))

# Scanline overlay
for y in range(H):
    if y % 3 == 0:
        for x in range(W):
            idx = (y * W + x) * 3
            pixels[idx] = int(pixels[idx] * 0.92)
            pixels[idx+1] = int(pixels[idx+1] * 0.92)
            pixels[idx+2] = int(pixels[idx+2] * 0.92)

t2 = time.time()
print(f"  Rendered in {t2-t1:.1f}s")

# --- Stats ---
# Count cells that have pixels (some seeds might be very close)
cell_pixel_counts = {}
for y in range(H):
    for x in range(W):
        cid = cell_id_map[y][x]
        cell_pixel_counts[cid] = cell_pixel_counts.get(cid, 0) + 1

active_cells = len(cell_pixel_counts)
sizes = sorted(cell_pixel_counts.values())
smallest = sizes[0]
largest = sizes[-1]
median_size = sizes[len(sizes)//2]
avg_size = sum(sizes) / len(sizes)

# Count edge pixels (where edge_strength < 3)
edge_count = 0
for y in range(H):
    for x in range(W):
        if dist2_map[y][x] - dist1_map[y][x] < 3.0:
            edge_count += 1

print(f"\n--- Voronoi Stats ---")
print(f"Seeds: {N_SEEDS}, Active cells: {active_cells}")
print(f"Cell sizes: min={smallest}px, max={largest}px, median={median_size}px, avg={avg_size:.0f}px")
print(f"Edge pixels (boundary): {edge_count} ({edge_count*100/(W*H):.1f}%)")
print(f"Size ratio (max/min): {largest/smallest:.1f}x")

# --- Hand-rolled PNG encoder ---
def write_png(filename, width, height, rgb_data):
    def chunk(chunk_type, data):
        c = chunk_type + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # filter: None
        offset = y * width * 3
        raw.extend(rgb_data[offset:offset + width * 3])
    
    compressed = zlib.compress(bytes(raw), 9)
    
    with open(filename, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n')
        f.write(chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)))
        f.write(chunk(b'IDAT', compressed))
        f.write(chunk(b'IEND', b''))

out_path = "/Users/jianjun/.openclaw/workspace/agent-j/lab/voronoi-crystal.png"
write_png(out_path, W, H, bytes(pixels))

import os
fsize = os.path.getsize(out_path)
print(f"\nOutput: {out_path}")
print(f"File size: {fsize//1024}KB")
print(f"Total time: {time.time()-t0:.1f}s")
print("Done! ✅")
