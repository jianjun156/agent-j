#!/usr/bin/env python3
"""EXP-20260514-035 — Gray Hypercube Relay

Generate a lightweight zero-dependency PNG visualization of an 8-bit Gray-code
Hamiltonian path through all 256 vertices of an 8D hypercube.
"""
from __future__ import annotations

import math
import os
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "lab" / "gray-hypercube-relay.png"
W, H = 1200, 900
BG = (4, 4, 16)


def put(px, x, y, c, a=1.0):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        r, g, b = px[i], px[i+1], px[i+2]
        cr, cg, cb = c
        px[i] = max(0, min(255, int(r * (1-a) + cr * a)))
        px[i+1] = max(0, min(255, int(g * (1-a) + cg * a)))
        px[i+2] = max(0, min(255, int(b * (1-a) + cb * a)))


def line(px, x0, y0, x1, y1, c, a=1.0, width=1):
    x0, y0, x1, y1 = map(lambda v: int(round(v)), (x0, y0, x1, y1))
    dx, dy = abs(x1-x0), -abs(y1-y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        for ox in range(-width, width+1):
            for oy in range(-width, width+1):
                if ox*ox + oy*oy <= width*width:
                    put(px, x+ox, y+oy, c, a)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy; x += sx
        if e2 <= dx:
            err += dx; y += sy


def circle(px, cx, cy, r, c, a=1.0, fill=False):
    rr = int(r)
    if fill:
        for y in range(int(cy-rr), int(cy+rr)+1):
            for x in range(int(cx-rr), int(cx+rr)+1):
                d2 = (x-cx)**2 + (y-cy)**2
                if d2 <= r*r:
                    # soft edge
                    edge = max(0.15, min(1.0, (r - math.sqrt(d2) + 1.5)/2.5))
                    put(px, x, y, c, a*edge)
    else:
        steps = max(60, int(2*math.pi*r*1.4))
        last = None
        for i in range(steps+1):
            t = 2*math.pi*i/steps
            p = (cx + math.cos(t)*r, cy + math.sin(t)*r)
            if last:
                line(px, last[0], last[1], p[0], p[1], c, a, 1)
            last = p


def text5(px, x, y, s, c, a=1.0, scale=3):
    font = {
        '0':['111','101','101','101','111'], '1':['010','110','010','010','111'],
        '2':['111','001','111','100','111'], '3':['111','001','111','001','111'],
        '4':['101','101','111','001','001'], '5':['111','100','111','001','111'],
        '6':['111','100','111','101','111'], '7':['111','001','010','010','010'],
        '8':['111','101','111','101','111'], '9':['111','101','111','001','111'],
        'A':['010','101','111','101','101'], 'B':['110','101','110','101','110'],
        'C':['111','100','100','100','111'], 'D':['110','101','101','101','110'],
        'E':['111','100','110','100','111'], 'F':['111','100','110','100','100'],
        'G':['111','100','101','101','111'], 'H':['101','101','111','101','101'],
        'I':['111','010','010','010','111'], 'J':['001','001','001','101','111'],
        'K':['101','101','110','101','101'], 'L':['100','100','100','100','111'],
        'M':['101','111','111','101','101'], 'N':['101','111','111','111','101'],
        'O':['111','101','101','101','111'], 'P':['111','101','111','100','100'],
        'Q':['111','101','101','111','001'], 'R':['111','101','111','110','101'],
        'S':['111','100','111','001','111'], 'T':['111','010','010','010','010'],
        'U':['101','101','101','101','111'], 'V':['101','101','101','101','010'],
        'W':['101','101','111','111','101'], 'X':['101','101','010','101','101'],
        'Y':['101','101','010','010','010'], 'Z':['111','001','010','100','111'],
        '-':['000','000','111','000','000'], ':':['000','010','000','010','000'],
        '.':['000','000','000','000','010'], ' ':['000','000','000','000','000'],
        '/':['001','001','010','100','100'], '_':['000','000','000','000','111'],
    }
    x0 = x
    for ch in s.upper():
        pat = font.get(ch, font[' '])
        for yy, row in enumerate(pat):
            for xx, bit in enumerate(row):
                if bit == '1':
                    for sy in range(scale):
                        for sx in range(scale):
                            put(px, x + xx*scale + sx, y + yy*scale + sy, c, a)
        x += 4 * scale
    return x - x0


def write_png(path, pixels):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw.extend(pixels[y*W*3:(y+1)*W*3])
    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag+data) & 0xffffffff)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    png += chunk(b'IEND', b'')
    path.write_bytes(png)


def main():
    pixels = bytearray(BG * (W * H))

    # radial background and grid
    cx, cy = W/2, H/2
    for y in range(H):
        for x in range(W):
            dx, dy = (x-cx)/(W/2), (y-cy)/(H/2)
            d = min(1.0, math.sqrt(dx*dx + dy*dy))
            i = (y*W+x)*3
            glow = max(0, 1-d)
            pixels[i] = int(pixels[i] + 10*glow)
            pixels[i+1] = int(pixels[i+1] + 18*glow)
            pixels[i+2] = int(pixels[i+2] + 40*glow)
    for x in range(80, W, 80): line(pixels, x, 0, x, H, (25, 70, 110), 0.13, 1)
    for y in range(60, H, 60): line(pixels, 0, y, W, y, (25, 70, 110), 0.10, 1)

    # 8D projection vectors arranged with incommensurate-looking angles.
    vecs = []
    for k in range(8):
        ang = 2*math.pi*k/8 + (0.19 if k % 2 else 0.0)
        mag = 70 + (k % 3) * 12
        vecs.append((math.cos(ang)*mag, math.sin(ang)*mag))

    def gray(i): return i ^ (i >> 1)
    def project(v):
        x, y = cx, cy + 20
        for k in range(8):
            sx = 1 if (v >> k) & 1 else -1
            x += sx * vecs[k][0]
            y += sx * vecs[k][1]
        return x, y

    seq = [gray(i) for i in range(256)]
    pts = [project(v) for v in seq]
    unique = len(set(seq))
    hamming_steps = [bin(seq[i]^seq[i-1]).count('1') for i in range(1, len(seq))]
    max_hamming = max(hamming_steps)
    flips = [0]*8
    for i in range(1, len(seq)):
        bit = (seq[i]^seq[i-1]).bit_length()-1
        flips[bit] += 1

    # ghost hypercube edges: connect vertices differing by 1 bit.
    vertex_pts = {v: project(v) for v in range(256)}
    for v in range(256):
        x0, y0 = vertex_pts[v]
        for k in range(8):
            u = v ^ (1 << k)
            if u > v:
                x1, y1 = vertex_pts[u]
                line(pixels, x0, y0, x1, y1, (40, 90, 150), 0.055, 1)

    # Gray-code relay path, cyan -> violet -> gold.
    def grad(t):
        if t < 0.5:
            q = t/0.5
            return (int(40+80*q), int(220-90*q), int(255))
        q = (t-0.5)/0.5
        return (int(120+135*q), int(130+80*q), int(255-195*q))

    for i in range(1, len(pts)):
        t = i/(len(pts)-1)
        c = grad(t)
        x0, y0 = pts[i-1]; x1, y1 = pts[i]
        line(pixels, x0, y0, x1, y1, c, 0.18, 5)
        line(pixels, x0, y0, x1, y1, c, 0.95, 2)
    for idx, (x, y) in enumerate(pts):
        t = idx/255
        r = 2.2 + 1.0*math.sin(t*math.pi)
        circle(pixels, x, y, r+3, grad(t), 0.12, True)
        circle(pixels, x, y, r, grad(t), 0.95, True)

    # Emphasize start/end relay beacons.
    circle(pixels, pts[0][0], pts[0][1], 12, (0,255,180), 0.65, False)
    circle(pixels, pts[-1][0], pts[-1][1], 14, (255,210,60), 0.75, False)

    # Bit flip histogram.
    bx, by = 90, 665
    text5(pixels, bx, by-55, 'BIT FLIPS: 128 64 32 16 8 4 2 1', (90, 230, 255), 0.85, 3)
    maxf = max(flips)
    for k, f in enumerate(flips):
        x = bx + k * 105
        hh = int(160 * f / maxf)
        for yy in range(by+160-hh, by+160):
            for xx in range(x, x+48):
                put(pixels, xx, yy, (50+k*20, 220-k*12, 255-k*22), 0.8)
        line(pixels, x, by+160-hh, x+48, by+160-hh, (255,255,255), 0.6, 1)
        text5(pixels, x+8, by+172, str(k), (170,210,255), 0.9, 3)
        text5(pixels, x, by+200, str(f), (255,210,80), 0.9, 3)

    # Title and metrics.
    text5(pixels, 72, 55, 'GRAY-HYPERCUBE-RELAY', (120, 240, 255), 0.95, 5)
    text5(pixels, 74, 105, '256 VERTICES / 255 MOVES / HAMMING STEP = 1', (255, 215, 90), 0.9, 3)
    text5(pixels, 74, 138, f'UNIQUE={unique} MAX_DELTA={max_hamming} DIM=8', (180, 160, 255), 0.88, 3)
    text5(pixels, 780, 55, 'START', (0,255,180), 0.9, 3)
    line(pixels, 855, 65, pts[0][0], pts[0][1], (0,255,180), 0.5, 1)
    text5(pixels, 920, 90, 'END', (255,210,60), 0.9, 3)
    line(pixels, 970, 100, pts[-1][0], pts[-1][1], (255,210,60), 0.5, 1)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    write_png(OUT, pixels)

    print('GRAY_HYPERCUBE_RELAY_RESULT')
    print(f'output={OUT.relative_to(ROOT)}')
    print(f'bytes={OUT.stat().st_size}')
    print(f'unique_vertices={unique}')
    print(f'moves={len(seq)-1}')
    print(f'max_hamming_step={max_hamming}')
    print('bit_flip_counts=' + ','.join(map(str, flips)))
    print('first_8_gray=' + ','.join(f'{v:08b}' for v in seq[:8]))
    print('last_8_gray=' + ','.join(f'{v:08b}' for v in seq[-8:]))


if __name__ == '__main__':
    main()
