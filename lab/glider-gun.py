#!/usr/bin/env python3
"""
EXP-20260405-019: GOSPER-CANNON
Conway's Game of Life — Gosper Glider Gun
A pattern that endlessly spawns glider "bullets" from just two simple rules.
Pure Python, zero external dependencies, hand-rolled PNG encoder.
"""

import struct, zlib, math

# ── Conway's Game of Life Rules ──
# 1. Live cell with 2 or 3 neighbors → survives
# 2. Dead cell with exactly 3 neighbors → becomes alive
# 3. All other cells → die or stay dead

WIDTH, HEIGHT = 160, 90  # Grid size
STEPS = 240  # Simulation steps
CELL_SIZE = 5  # Pixels per cell
CANVAS_W = WIDTH * CELL_SIZE
CANVAS_H = HEIGHT * CELL_SIZE

# ── Gosper Glider Gun Pattern ──
# Discovered by Bill Gosper in 1970, first known finite pattern
# that grows indefinitely. It fires a new glider every 30 steps.
GOSPER_GUN = [
    (1,5),(1,6),(2,5),(2,6),  # Left block
    (11,5),(11,6),(11,7),(12,4),(12,8),(13,3),(13,9),(14,3),(14,9),
    (15,6),(16,4),(16,8),(17,5),(17,6),(17,7),(18,6),  # Left part
    (21,3),(21,4),(21,5),(22,3),(22,4),(22,5),(23,2),(23,6),
    (25,1),(25,2),(25,6),(25,7),  # Right part
    (35,3),(35,4),(36,3),(36,4),  # Right block
]

def init_grid():
    """Initialize grid with Gosper Glider Gun at offset (10, 20)."""
    grid = [[0]*WIDTH for _ in range(HEIGHT)]
    ox, oy = 10, 20
    for gx, gy in GOSPER_GUN:
        grid[oy + gy][ox + gx] = 1
    return grid

def step(grid):
    """Advance one generation."""
    new = [[0]*WIDTH for _ in range(HEIGHT)]
    for y in range(HEIGHT):
        for x in range(WIDTH):
            n = 0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dy == 0 and dx == 0:
                        continue
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < HEIGHT and 0 <= nx < WIDTH:
                        n += grid[ny][nx]
            if grid[y][x]:
                new[y][x] = 1 if n in (2, 3) else 0
            else:
                new[y][x] = 1 if n == 3 else 0
    return new

def simulate():
    """Run simulation, record birth times for heatmap."""
    grid = init_grid()
    # Track when each cell was first alive and last alive
    birth_time = [[STEPS+1]*WIDTH for _ in range(HEIGHT)]
    alive_count = [[0]*WIDTH for _ in range(HEIGHT)]
    
    for gx, gy in GOSPER_GUN:
        birth_time[20 + gy][10 + gx] = 0
        alive_count[20 + gy][10 + gx] = 1
    
    snapshots = [grid]  # Save key frames
    snap_times = [0]
    
    for t in range(1, STEPS + 1):
        grid = step(grid)
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if grid[y][x]:
                    if birth_time[y][x] > t:
                        birth_time[y][x] = t
                    alive_count[y][x] += 1
        
        # Save snapshots at key moments
        if t in (30, 60, 120, 180, STEPS):
            snapshots.append([row[:] for row in grid])
            snap_times.append(t)
    
    return grid, birth_time, alive_count, snapshots, snap_times

# ── PNG Encoder ──
def make_png(width, height, pixels):
    """Hand-rolled PNG encoder. pixels = list of (r,g,b) row by row."""
    def chunk(ctype, data):
        c = ctype + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
    
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # filter none
        offset = y * width
        for x in range(width):
            r, g, b = pixels[offset + x]
            raw.extend((r, g, b))
    
    idat = chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    iend = chunk(b'IEND', b'')
    return sig + ihdr + idat + iend

def lerp_color(c1, c2, t):
    """Linear interpolation between two RGB colors."""
    t = max(0, min(1, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

# ── Render ──
def render(final_grid, birth_time, alive_count, snapshots, snap_times):
    """Render the final visualization."""
    
    # Layout: main heatmap + 5 small snapshots below
    SNAP_CELL = 3
    SNAP_W = WIDTH * SNAP_CELL
    SNAP_H = HEIGHT * SNAP_CELL
    SNAP_PANEL_H = SNAP_H + 40  # 40px for labels
    
    MAIN_H = CANVAS_H
    TOTAL_W = CANVAS_W
    TOTAL_H = MAIN_H + 30 + SNAP_PANEL_H + 20  # 30px gap, 20px bottom
    
    # But 5 snapshots side by side won't fit at SNAP_CELL=3 (5*480=2400 > 800)
    # Use 2px cells for snapshots, and place them in a row
    SNAP_CELL = 2
    SNAP_W = WIDTH * SNAP_CELL  # 320
    SNAP_H = HEIGHT * SNAP_CELL  # 180
    
    # We have 5 snapshots: t=30, 60, 120, 180, 240
    # Let's pick 4 snapshots to fit nicely
    # Actually let's make the canvas wider to accommodate
    # Or: show main heatmap (800x450) + stats panel on right
    
    # Simpler approach: single large image with heatmap
    # Plus a small panel at bottom showing 4 mini snapshots
    
    MARGIN = 10
    TITLE_H = 50
    STATS_H = 80
    MINI_CELL = 2
    MINI_W = WIDTH * MINI_CELL  # 320
    MINI_H = HEIGHT * MINI_CELL  # 180
    MINI_GAP = 10
    MINI_COUNT = min(4, len(snapshots) - 1)  # Skip t=0
    MINI_PANEL_W = MINI_COUNT * MINI_W + (MINI_COUNT - 1) * MINI_GAP
    
    TOTAL_W = max(CANVAS_W, MINI_PANEL_W + 2 * MARGIN)
    TOTAL_H = TITLE_H + CANVAS_H + 20 + MINI_H + 30 + STATS_H + MARGIN
    
    # Background
    pixels = [(8, 12, 24)] * (TOTAL_W * TOTAL_H)
    
    def set_pixel(px, py, color):
        if 0 <= px < TOTAL_W and 0 <= py < TOTAL_H:
            pixels[py * TOTAL_W + px] = color
    
    def fill_rect(x1, y1, w, h, color):
        for dy in range(h):
            for dx in range(w):
                set_pixel(x1 + dx, y1 + dy, color)
    
    # ── Color scheme ──
    # Heatmap: birth time → color
    # Early (gun body) = bright cyan
    # Gliders = gradient from green to yellow to magenta
    DEEP_BG = (8, 12, 24)
    CYAN = (0, 255, 255)
    GREEN = (0, 200, 100)
    YELLOW = (255, 220, 50)
    MAGENTA = (255, 50, 200)
    RED = (255, 40, 80)
    
    def birth_color(t, count):
        """Color by birth time with intensity by alive count."""
        if t > STEPS:
            return DEEP_BG
        frac = t / STEPS
        if frac < 0.05:
            c = CYAN
        elif frac < 0.25:
            c = lerp_color(CYAN, GREEN, (frac - 0.05) / 0.2)
        elif frac < 0.5:
            c = lerp_color(GREEN, YELLOW, (frac - 0.25) / 0.25)
        elif frac < 0.75:
            c = lerp_color(YELLOW, MAGENTA, (frac - 0.5) / 0.25)
        else:
            c = lerp_color(MAGENTA, RED, (frac - 0.75) / 0.25)
        
        # Intensity by alive count
        intensity = min(1.0, count / (STEPS * 0.3))
        intensity = 0.4 + 0.6 * intensity
        return tuple(int(v * intensity) for v in c)
    
    # ── Draw main heatmap ──
    main_y0 = TITLE_H
    for cy in range(HEIGHT):
        for cx in range(WIDTH):
            bt = birth_time[cy][cx]
            ac = alive_count[cy][cx]
            color = birth_color(bt, ac)
            
            # Also glow currently alive cells
            if final_grid[cy][cx]:
                color = tuple(min(255, c + 60) for c in color)
            
            for dy in range(CELL_SIZE):
                for dx in range(CELL_SIZE):
                    set_pixel(cx * CELL_SIZE + dx, main_y0 + cy * CELL_SIZE + dy, color)
    
    # ── Draw title ──
    # Simple dot-matrix "GOSPER GLIDER GUN" title
    title = "GOSPER GLIDER GUN - CONWAY'S GAME OF LIFE"
    # 3x5 font
    FONT = {
        'A': ["111","101","111","101","101"], 'B': ["110","101","110","101","110"],
        'C': ["111","100","100","100","111"], 'D': ["110","101","101","101","110"],
        'E': ["111","100","110","100","111"], 'F': ["111","100","110","100","100"],
        'G': ["111","100","101","101","111"], 'H': ["101","101","111","101","101"],
        'I': ["111","010","010","010","111"], 'J': ["111","001","001","101","111"],
        'K': ["101","110","100","110","101"], 'L': ["100","100","100","100","111"],
        'M': ["101","111","111","101","101"], 'N': ["101","111","111","111","101"],
        'O': ["111","101","101","101","111"], 'P': ["111","101","111","100","100"],
        'Q': ["111","101","101","111","001"], 'R': ["111","101","111","110","101"],
        'S': ["111","100","111","001","111"], 'T': ["111","010","010","010","010"],
        'U': ["101","101","101","101","111"], 'V': ["101","101","101","101","010"],
        'W': ["101","101","111","111","101"], 'X': ["101","101","010","101","101"],
        'Y': ["101","101","111","010","010"], 'Z': ["111","001","010","100","111"],
        '0': ["111","101","101","101","111"], '1': ["010","110","010","010","111"],
        '2': ["111","001","111","100","111"], '3': ["111","001","111","001","111"],
        '4': ["101","101","111","001","001"], '5': ["111","100","111","001","111"],
        '6': ["111","100","111","101","111"], '7': ["111","001","001","010","010"],
        '8': ["111","101","111","101","111"], '9': ["111","101","111","001","111"],
        ' ': ["000","000","000","000","000"], '-': ["000","000","111","000","000"],
        "'": ["010","010","000","000","000"], '.': ["000","000","000","000","010"],
        ',': ["000","000","000","010","100"], ':': ["000","010","000","010","000"],
    }
    
    def draw_text(text, x0, y0, scale=2, color=(0, 220, 255)):
        cx = x0
        for ch in text.upper():
            glyph = FONT.get(ch, FONT[' '])
            for row_i, row in enumerate(glyph):
                for col_i, bit in enumerate(row):
                    if bit == '1':
                        for sy in range(scale):
                            for sx in range(scale):
                                set_pixel(cx + col_i * scale + sx, y0 + row_i * scale + sy, color)
            cx += (len(glyph[0]) + 1) * scale
        return cx
    
    draw_text(title, 10, 15, 3, (0, 200, 255))
    
    # ── Draw mini snapshots ──
    mini_y0 = main_y0 + CANVAS_H + 20
    selected = [(snapshots[i], snap_times[i]) for i in range(1, len(snapshots))][:4]
    
    for si, (snap, st) in enumerate(selected):
        sx0 = MARGIN + si * (MINI_W + MINI_GAP)
        
        # Border
        for bx in range(MINI_W + 4):
            set_pixel(sx0 - 2 + bx, mini_y0 - 2, (0, 100, 150))
            set_pixel(sx0 - 2 + bx, mini_y0 + MINI_H + 1, (0, 100, 150))
        for by in range(MINI_H + 4):
            set_pixel(sx0 - 2, mini_y0 - 2 + by, (0, 100, 150))
            set_pixel(sx0 + MINI_W + 1, mini_y0 - 2 + by, (0, 100, 150))
        
        for cy in range(HEIGHT):
            for cx in range(WIDTH):
                if snap[cy][cx]:
                    # Color by position for visual interest
                    dist = math.sqrt((cx - 20)**2 + (cy - 23)**2)
                    frac = min(1.0, dist / 80)
                    color = lerp_color((0, 255, 220), (255, 80, 220), frac)
                else:
                    color = (12, 18, 32)
                for dy in range(MINI_CELL):
                    for dx in range(MINI_CELL):
                        set_pixel(sx0 + cx * MINI_CELL + dx, mini_y0 + cy * MINI_CELL + dy, color)
        
        # Label
        label = f"T:{st}"
        draw_text(label, sx0 + 5, mini_y0 + MINI_H + 5, 2, (0, 180, 220))
    
    # ── Stats panel ──
    stats_y0 = mini_y0 + MINI_H + 30
    
    # Count live cells and gliders
    live_cells = sum(sum(row) for row in final_grid)
    total_ever = sum(1 for y in range(HEIGHT) for x in range(WIDTH) if birth_time[y][x] <= STEPS)
    gliders_spawned = STEPS // 30  # One glider every 30 steps
    
    stats_lines = [
        f"GRID: {WIDTH}X{HEIGHT}  STEPS: {STEPS}  LIVE CELLS: {live_cells}  TOTAL VISITED: {total_ever}",
        f"GLIDERS SPAWNED: {gliders_spawned}  PERIOD: 30 STEPS  GUN CELLS: {len(GOSPER_GUN)}",
        f"RULE: B3 S23  BORN IF 3 NEIGHBORS, SURVIVE IF 2 OR 3",
    ]
    
    for i, line in enumerate(stats_lines):
        color = (0, 180, 220) if i < 2 else (100, 140, 180)
        draw_text(line, 10, stats_y0 + i * 18, 2, color)
    
    # ── Scanline effect ──
    for y in range(TOTAL_H):
        if y % 3 == 0:
            for x in range(TOTAL_W):
                r, g, b = pixels[y * TOTAL_W + x]
                pixels[y * TOTAL_W + x] = (max(0, r - 8), max(0, g - 8), max(0, b - 8))
    
    # ── Vignette ──
    cx_center, cy_center = TOTAL_W / 2, TOTAL_H / 2
    max_dist = math.sqrt(cx_center**2 + cy_center**2)
    for y in range(TOTAL_H):
        for x in range(TOTAL_W):
            dist = math.sqrt((x - cx_center)**2 + (y - cy_center)**2)
            vignette = 1.0 - 0.3 * (dist / max_dist) ** 2
            r, g, b = pixels[y * TOTAL_W + x]
            pixels[y * TOTAL_W + x] = (
                int(r * vignette), int(g * vignette), int(b * vignette)
            )
    
    return pixels, TOTAL_W, TOTAL_H, live_cells, total_ever, gliders_spawned

# ── Main ──
print("🔬 EXP-019: GOSPER-CANNON — Conway's Game of Life")
print(f"   Grid: {WIDTH}×{HEIGHT}, Steps: {STEPS}")
print("   Initializing Gosper Glider Gun...")

import time
t0 = time.time()

final_grid, birth_time, alive_count, snapshots, snap_times = simulate()
t_sim = time.time() - t0
print(f"   Simulation: {t_sim:.2f}s ({STEPS/t_sim:.0f} steps/s)")

live_cells = sum(sum(row) for row in final_grid)
total_ever = sum(1 for y in range(HEIGHT) for x in range(WIDTH) if birth_time[y][x] <= STEPS)
gliders_spawned = STEPS // 30

print(f"   Live cells: {live_cells}")
print(f"   Total cells ever alive: {total_ever}")
print(f"   Gliders spawned: {gliders_spawned} (one every 30 steps)")

print("   Rendering heatmap...")
t1 = time.time()
pixels, w, h, _, _, _ = render(final_grid, birth_time, alive_count, snapshots, snap_times)
t_render = time.time() - t1
print(f"   Render: {t_render:.2f}s ({w}×{h})")

print("   Encoding PNG...")
png_data = make_png(w, h, pixels)
out_path = "/Users/jianjun/.openclaw/workspace/agent-j/lab/glider-gun.png"
with open(out_path, 'wb') as f:
    f.write(png_data)
print(f"   ✅ Saved: {out_path} ({len(png_data)//1024}KB)")
print(f"   Total time: {time.time()-t0:.2f}s")
