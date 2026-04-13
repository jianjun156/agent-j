#!/usr/bin/env python3
"""EXP-20260413-026: BLOOM-CHAOS — Plant Leaf Vein Simulation"""

import math
import struct
import zlib
import random

# Configuration
WIDTH, HEIGHT = 800, 600
SEED = 42
random.seed(SEED)

# Canvas
canvas = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]

def bresenham_line(x0, y0, x1, y1, color):
    """Draw line using Bresenham algorithm."""
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    
    x, y = x0, y0
    while True:
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            canvas[y][x] = max(canvas[y][x], color)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy

def grow_vein(x, y, angle, length, depth, color):
    """Recursively grow leaf veins with branching."""
    if depth == 0 or length < 1:
        return
    
    # Calculate end point
    x1 = x + length * math.cos(angle)
    y1 = y + length * math.sin(angle)
    
    # Draw vein
    bresenham_line(int(x), int(y), int(x1), int(y1), color)
    
    # Branch with random angles
    if depth > 1:
        branch_angle1 = angle + random.uniform(-0.3, -0.1)
        branch_angle2 = angle + random.uniform(0.1, 0.3)
        branch_length = length * random.uniform(0.7, 0.85)
        
        grow_vein(x1, y1, branch_angle1, branch_length, depth - 1, max(0, color - 20))
        grow_vein(x1, y1, branch_angle2, branch_length, depth - 1, max(0, color - 20))

# Generate three leaf veins from different starting points
root_x, root_y = 400, 550
main_length = 120

# Main vein (upward)
grow_vein(root_x, root_y, -math.pi / 2, main_length, 6, 200)

# Left branch
grow_vein(root_x, root_y, -math.pi / 2.5, main_length * 0.8, 5, 180)

# Right branch
grow_vein(root_x, root_y, -math.pi / 1.8, main_length * 0.8, 5, 180)

def encode_png(width, height, pixel_data):
    """Encode raw pixel data to PNG."""
    # PNG signature
    png = b'\x89PNG\r\n\x1a\n'
    
    # IHDR chunk
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)  # RGB, 8-bit
    ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff
    png += struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
    
    # IDAT chunk (image data)
    raw = b''
    for y in range(height):
        raw += b'\x00'  # Filter type: None
        for x in range(width):
            val = pixel_data[y][x]
            # Map grayscale to RGB with color gradient (blue->cyan->green->yellow)
            if val < 80:
                r, g, b = 0, val // 2, 200
            elif val < 150:
                r, g, b = 0, 150, max(0, 200 - (val - 80))
            else:
                r, g, b = (val - 150) * 2, 200, 0
            raw += bytes([r, g, b])
    
    compressed = zlib.compress(raw, 9)
    idat_crc = zlib.crc32(b'IDAT' + compressed) & 0xffffffff
    png += struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', idat_crc)
    
    # IEND chunk
    iend_crc = zlib.crc32(b'IEND') & 0xffffffff
    png += struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)
    
    return png

# Write PNG
png_data = encode_png(WIDTH, HEIGHT, canvas)
with open('/Users/jianjun/.openclaw/workspace/agent-j/experiments/lab/bloom-chaos.png', 'wb') as f:
    f.write(png_data)

print(f'✓ Generated: bloom-chaos.png ({len(png_data)} bytes)')
print(f'✓ Canvas size: {WIDTH}×{HEIGHT}')
print(f'✓ Max pixel value: {max(max(row) for row in canvas)}')
