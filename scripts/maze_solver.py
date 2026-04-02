#!/usr/bin/env python3
"""
EXP-017: MAZE-MIND — DFS Maze Generation + A* Solving + PNG Visualization
Agent J's Daily Lab Experiment — 2026-04-03
Pure Python, zero external dependencies (only stdlib)
"""

import random
import struct
import zlib
import heapq
import time

random.seed(20260403)

# ── Maze Parameters ──
COLS, ROWS = 41, 31  # Maze cells
CELL_SIZE = 14
MARGIN = 40

IMG_W = COLS * CELL_SIZE + 2 * MARGIN
IMG_H = ROWS * CELL_SIZE + 2 * MARGIN + 80

print(f"🏗️  Generating {COLS}×{ROWS} maze ({COLS*ROWS} cells)...")
t0 = time.time()

# ── DFS Maze Generation (Iterative to avoid recursion limit) ──
grid = [[0]*(2*COLS+1) for _ in range(2*ROWS+1)]
visited = [[False]*COLS for _ in range(ROWS)]

stack = [(0, 0)]
visited[0][0] = True
grid[1][1] = 1

while stack:
    cx, cy = stack[-1]
    dirs = [(0,-1),(0,1),(-1,0),(1,0)]
    random.shuffle(dirs)
    found = False
    for dx, dy in dirs:
        nx, ny = cx+dx, cy+dy
        if 0 <= nx < COLS and 0 <= ny < ROWS and not visited[ny][nx]:
            visited[ny][nx] = True
            grid[2*ny+1][2*nx+1] = 1
            grid[2*cy+1+dy][2*cx+1+dx] = 1
            stack.append((nx, ny))
            found = True
            break
    if not found:
        stack.pop()

START = (0, 0)
END = (COLS-1, ROWS-1)
print(f"✅ Maze generated in {time.time()-t0:.3f}s")

# ── A* Pathfinding ──
print("🔍 Solving with A*...")
t1 = time.time()

def heuristic(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def astar(grid, start, end):
    sx, sy = 2*start[0]+1, 2*start[1]+1
    ex, ey = 2*end[0]+1, 2*end[1]+1
    open_set = [(heuristic((sx,sy),(ex,ey)), 0, sx, sy)]
    came_from = {}
    g_score = {(sx,sy): 0}
    explored = set()
    while open_set:
        f, g, x, y = heapq.heappop(open_set)
        if (x,y) in explored:
            continue
        explored.add((x,y))
        if (x,y) == (ex,ey):
            path = [(x,y)]
            while (x,y) in came_from:
                x,y = came_from[(x,y)]
                path.append((x,y))
            path.reverse()
            return path, explored
        for dx, dy in [(0,-1),(0,1),(-1,0),(1,0)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid) and grid[ny][nx] == 1:
                ng = g + 1
                if ng < g_score.get((nx,ny), float('inf')):
                    g_score[(nx,ny)] = ng
                    came_from[(nx,ny)] = (x,y)
                    heapq.heappush(open_set, (ng + heuristic((nx,ny),(ex,ey)), ng, nx, ny))
    return [], explored

solution_path, explored_cells = astar(grid, START, END)
t_solve = time.time() - t1
print(f"✅ Solved in {t_solve:.3f}s — path length: {len(solution_path)}, explored: {len(explored_cells)}")

# ── Dead End Analysis ──
dead_ends = 0
for cy in range(ROWS):
    for cx in range(COLS):
        gx, gy = 2*cx+1, 2*cy+1
        neighbors = sum(1 for dx,dy in [(0,-1),(0,1),(-1,0),(1,0)]
                       if grid[gy+dy][gx+dx] == 1)
        if neighbors == 1:
            dead_ends += 1
print(f"📊 Dead ends: {dead_ends}")

# ── PNG Rendering ──
print("🎨 Rendering cyberpunk maze PNG...")

pixels = [[(10, 12, 20)] * IMG_W for _ in range(IMG_H)]

WALL_COLOR = (20, 30, 50)
PASSAGE_COLOR = (15, 20, 35)
EXPLORED_COLOR_BASE = (20, 50, 40)
PATH_COLOR_START = (0, 220, 255)
PATH_COLOR_END = (255, 50, 200)
START_COLOR = (0, 255, 100)
END_COLOR = (255, 80, 80)

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i]) * t) for i in range(3))

def set_pixel(px, py, color):
    if 0 <= px < IMG_W and 0 <= py < IMG_H:
        pixels[py][px] = color

def fill_rect(x1, y1, w, h, color):
    for dy in range(h):
        for dx in range(w):
            set_pixel(x1+dx, y1+dy, color)

explored_set = set(explored_cells)
cs = CELL_SIZE // 2

for gy in range(2*ROWS+1):
    for gx in range(2*COLS+1):
        px = MARGIN + gx * cs
        py = MARGIN + gy * cs
        if grid[gy][gx] == 0:
            fill_rect(px, py, cs, cs, WALL_COLOR)
        else:
            if (gx, gy) in explored_set:
                fill_rect(px, py, cs, cs, EXPLORED_COLOR_BASE)
            else:
                fill_rect(px, py, cs, cs, PASSAGE_COLOR)

# Draw solution path with gradient
if solution_path:
    path_len = len(solution_path)
    for i, (gx, gy) in enumerate(solution_path):
        t = i / max(path_len - 1, 1)
        color = lerp_color(PATH_COLOR_START, PATH_COLOR_END, t)
        px = MARGIN + gx * cs
        py = MARGIN + gy * cs
        fill_rect(px, py, cs, cs, color)
        glow = tuple(max(0, c // 3) for c in color)
        for dx in range(-1, cs+1):
            for dy in range(-1, cs+1):
                if dx < 0 or dy < 0 or dx >= cs or dy >= cs:
                    npx, npy = px+dx, py+dy
                    if 0 <= npx < IMG_W and 0 <= npy < IMG_H:
                        old = pixels[npy][npx]
                        pixels[npy][npx] = tuple(min(255, old[j] + glow[j]) for j in range(3))

# Start and end markers
sx, sy = 2*START[0]+1, 2*START[1]+1
ex, ey = 2*END[0]+1, 2*END[1]+1
for gx, gy, color in [(sx, sy, START_COLOR), (ex, ey, END_COLOR)]:
    px = MARGIN + gx * cs
    py = MARGIN + gy * cs
    fill_rect(px, py, cs, cs, color)
    for r in range(1, 4):
        gc = tuple(max(0, c // (r+1)) for c in color)
        for dx in range(-r, cs+r):
            for dy in range(-r, cs+r):
                if dx < 0 or dy < 0 or dx >= cs or dy >= cs:
                    npx, npy = px+dx, py+dy
                    if 0 <= npx < IMG_W and 0 <= npy < IMG_H:
                        old = pixels[npy][npx]
                        pixels[npy][npx] = tuple(min(255, old[j] + gc[j]) for j in range(3))

# ── Stats text at bottom ──
stats_y = MARGIN + (2*ROWS+1) * cs + 15

def draw_dot_char(x, y, char, color, scale=1):
    font = {
        '0':[0b111,0b101,0b101,0b101,0b111],'1':[0b010,0b110,0b010,0b010,0b111],
        '2':[0b111,0b001,0b111,0b100,0b111],'3':[0b111,0b001,0b111,0b001,0b111],
        '4':[0b101,0b101,0b111,0b001,0b001],'5':[0b111,0b100,0b111,0b001,0b111],
        '6':[0b111,0b100,0b111,0b101,0b111],'7':[0b111,0b001,0b010,0b010,0b010],
        '8':[0b111,0b101,0b111,0b101,0b111],'9':[0b111,0b101,0b111,0b001,0b111],
        'A':[0b111,0b101,0b111,0b101,0b101],'B':[0b110,0b101,0b110,0b101,0b110],
        'C':[0b111,0b100,0b100,0b100,0b111],'D':[0b110,0b101,0b101,0b101,0b110],
        'E':[0b111,0b100,0b111,0b100,0b111],'F':[0b111,0b100,0b111,0b100,0b100],
        'G':[0b111,0b100,0b101,0b101,0b111],'H':[0b101,0b101,0b111,0b101,0b101],
        'I':[0b111,0b010,0b010,0b010,0b111],'J':[0b001,0b001,0b001,0b101,0b111],
        'K':[0b101,0b101,0b110,0b101,0b101],'L':[0b100,0b100,0b100,0b100,0b111],
        'M':[0b101,0b111,0b111,0b101,0b101],'N':[0b101,0b111,0b111,0b111,0b101],
        'O':[0b111,0b101,0b101,0b101,0b111],'P':[0b111,0b101,0b111,0b100,0b100],
        'R':[0b111,0b101,0b111,0b110,0b101],'S':[0b111,0b100,0b111,0b001,0b111],
        'T':[0b111,0b010,0b010,0b010,0b010],'U':[0b101,0b101,0b101,0b101,0b111],
        'V':[0b101,0b101,0b101,0b101,0b010],'W':[0b101,0b101,0b111,0b111,0b101],
        'X':[0b101,0b101,0b010,0b101,0b101],'Y':[0b101,0b101,0b111,0b010,0b010],
        'Z':[0b111,0b001,0b010,0b100,0b111],
        ' ':[0,0,0,0,0],':':[0,0b010,0,0b010,0],'.':[0,0,0,0,0b010],
        '-':[0,0,0b111,0,0],'*':[0,0b101,0b010,0b101,0],'%':[0b101,0b001,0b010,0b100,0b101],
    }
    ch = char.upper() if char.upper() in font else ' '
    rows = font.get(ch, font[' '])
    for ri, rb in enumerate(rows):
        for ci in range(3):
            if rb & (1 << (2-ci)):
                for sy2 in range(scale):
                    for sx2 in range(scale):
                        set_pixel(x + ci*scale + sx2, y + ri*scale + sy2, color)

def draw_text(x, y, text, color, scale=2):
    for i, ch in enumerate(text):
        draw_dot_char(x + i * (4*scale), y, ch, color, scale)

draw_text(MARGIN, stats_y, "MAZE-MIND  41X31  A* SOLVER", (0, 200, 230), 2)

efficiency = len(solution_path) / max(len(explored_cells), 1) * 100
stats_text = f"PATH:{len(solution_path)}  EXPLORED:{len(explored_cells)}  DEAD ENDS:{dead_ends}  EFF:{efficiency:.0f}%"
draw_text(MARGIN, stats_y + 20, stats_text, (150, 160, 180), 1)

legend_y = stats_y + 35
fill_rect(MARGIN, legend_y, 8, 8, START_COLOR)
draw_text(MARGIN + 12, legend_y, "START", START_COLOR, 1)
fill_rect(MARGIN + 60, legend_y, 8, 8, END_COLOR)
draw_text(MARGIN + 72, legend_y, "END", END_COLOR, 1)
fill_rect(MARGIN + 110, legend_y, 8, 8, PATH_COLOR_START)
draw_text(MARGIN + 122, legend_y, "PATH", (0, 220, 255), 1)
fill_rect(MARGIN + 165, legend_y, 8, 8, EXPLORED_COLOR_BASE)
draw_text(MARGIN + 177, legend_y, "EXPLORED", (100, 120, 100), 1)

# ── Scanline + Vignette ──
for y in range(IMG_H):
    if y % 3 == 0:
        for x in range(IMG_W):
            r, g, b = pixels[y][x]
            pixels[y][x] = (max(0, r-5), max(0, g-5), max(0, b-5))

cx_v, cy_v = IMG_W // 2, IMG_H // 2
max_dist = (cx_v**2 + cy_v**2) ** 0.5
for y in range(IMG_H):
    for x in range(IMG_W):
        dist = ((x - cx_v)**2 + (y - cy_v)**2) ** 0.5
        factor = max(0, 1 - (dist / max_dist) ** 1.5 * 0.5)
        r, g, b = pixels[y][x]
        pixels[y][x] = (int(r * factor), int(g * factor), int(b * factor))

# ── Write PNG ──
def write_png(filename, width, height, pixels):
    def chunk(ctype, data):
        c = ctype + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xFFFFFFFF)
    raw = b''
    for row in pixels:
        raw += b'\x00'
        for r, g, b in row:
            raw += bytes([r, g, b])
    compressed = zlib.compress(raw, 9)
    with open(filename, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n')
        f.write(chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)))
        f.write(chunk(b'IDAT', compressed))
        f.write(chunk(b'IEND', b''))

out_path = '/Users/jianjun/.openclaw/workspace/agent-j/lab/maze-mind.png'
write_png(out_path, IMG_W, IMG_H, pixels)

import os
fsize = os.path.getsize(out_path)
print(f"\n🏆 EXPERIMENT COMPLETE!")
print(f"   Image: {out_path}")
print(f"   Size: {fsize//1024}KB")
print(f"   Maze: {COLS}×{ROWS} = {COLS*ROWS} cells")
print(f"   Path length: {len(solution_path)} steps")
print(f"   A* explored: {len(explored_cells)} cells")
print(f"   Dead ends: {dead_ends}")
print(f"   Efficiency: {efficiency:.1f}%")
print(f"   Total time: {time.time()-t0:.2f}s")
