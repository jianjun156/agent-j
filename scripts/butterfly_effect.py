#!/usr/bin/env python3
"""EXP-20260402-015: Butterfly Effect — Lorenz Attractor (optimized)"""
import struct, zlib, math, time

start = time.time()

sigma, rho, beta = 10.0, 28.0, 8.0/3.0
dt, steps = 0.005, 10000

def lorenz(x0, y0, z0):
    traj = []; x, y, z = x0, y0, z0
    for _ in range(steps):
        traj.append((x, y, z))
        dx1 = sigma*(y-x); dy1 = x*(rho-z)-y; dz1 = x*y-beta*z
        x2, y2, z2 = x+.5*dt*dx1, y+.5*dt*dy1, z+.5*dt*dz1
        dx2 = sigma*(y2-x2); dy2 = x2*(rho-z2)-y2; dz2 = x2*y2-beta*z2
        x3, y3, z3 = x+.5*dt*dx2, y+.5*dt*dy2, z+.5*dt*dz2
        dx3 = sigma*(y3-x3); dy3 = x3*(rho-z3)-y3; dz3 = x3*y3-beta*z3
        x4, y4, z4 = x+dt*dx3, y+dt*dy3, z+dt*dz3
        dx4 = sigma*(y4-x4); dy4 = x4*(rho-z4)-y4; dz4 = x4*y4-beta*z4
        x += dt*(dx1+2*dx2+2*dx3+dx4)/6
        y += dt*(dy1+2*dy2+2*dy3+dy4)/6
        z += dt*(dz1+2*dz2+2*dz3+dz4)/6
    return traj

print("Computing trajectories...", flush=True)
ta = lorenz(1.0, 1.0, 1.0)
tb = lorenz(1.001, 1.0, 1.0)

divs = []
for i in range(steps):
    a, b = ta[i], tb[i]
    divs.append(math.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2+(a[2]-b[2])**2))

ds = next((i for i, d in enumerate(divs) if d > 1.0), None)

# Smaller canvas for speed
W, H = 800, 530
# Use flat array for speed
pixels = bytearray(W * H * 3)
bg = (8, 12, 24)
for i in range(W * H):
    pixels[i*3] = bg[0]; pixels[i*3+1] = bg[1]; pixels[i*3+2] = bg[2]

main_h = int(H * 0.72)

def proj(x, y, z):
    return x*0.9553+y*0.2955, z  # cos(0.3), sin(0.3)

print("Projecting...", flush=True)
pa = [proj(*p) for p in ta]
pb = [proj(*p) for p in tb]
all_px = [p[0] for p in pa] + [p[0] for p in pb]
all_py = [p[1] for p in pa] + [p[1] for p in pb]
mnx, mxx = min(all_px), max(all_px)
mny, mxy = min(all_py), max(all_py)
mg = 30

def m2c(px, py):
    return mg+int((px-mnx)/(mxx-mnx)*(W-2*mg)), mg+int((mxy-py)/(mxy-mny)*(main_h-2*mg))

def setpx(x, y, r, g, b, a=1.0):
    if 0 <= x < W and 0 <= y < H:
        idx = (y*W+x)*3
        pixels[idx] = min(255, int(pixels[idx]*(1-a)+r*a))
        pixels[idx+1] = min(255, int(pixels[idx+1]*(1-a)+g*a))
        pixels[idx+2] = min(255, int(pixels[idx+2]*(1-a)+b*a))

print("Drawing A...", flush=True)
for i in range(steps):
    cx, cy = m2c(*pa[i]); t = i/steps
    setpx(cx, cy, int(20+30*t), int(180-80*t), int(220+35*t), 0.3+0.3*t)

print("Drawing B...", flush=True)
for i in range(steps):
    cx, cy = m2c(*pb[i]); t = i/steps
    setpx(cx, cy, int(220+35*t), int(40+60*t), int(160+60*t), 0.3+0.3*t)

# Divergence plot
print("Divergence plot...", flush=True)
dt2, db = main_h+15, H-10
dl, dr = mg, W-mg
for y in range(max(0,dt2-3), min(db+3,H)):
    for x in range(max(0,dl-3), min(dr+3,W)):
        idx = (y*W+x)*3
        pixels[idx]=12; pixels[idx+1]=18; pixels[idx+2]=32

md = max(divs)
for i in range(0, len(divs), 2):  # skip every other for speed
    x = dl + int(i/len(divs)*(dr-dl))
    v = min(divs[i], md*0.95)
    y = db - int(v/md*(db-dt2)*0.9)
    ratio = min(1.0, divs[i]/20.0)
    setpx(x, y, int(50+205*ratio), int(255-155*ratio), int(80-60*ratio), 0.9)

if ds:
    tx = dl + int(ds/len(divs)*(dr-dl))
    for y in range(dt2, db):
        setpx(tx, y, 255, 200, 50, 0.7)

# Simple vignette (fast: only darken edges)
print("Vignette...", flush=True)
cx_v, cy_v = W//2, H//2
for y in range(H):
    dy2 = (y - cy_v) ** 2
    for x in range(W):
        dx2 = (x - cx_v) ** 2
        dist2 = dx2 + dy2
        md2 = cx_v*cx_v + cy_v*cy_v
        f = max(0.6, 1.0 - 0.4 * dist2 / md2)
        idx = (y*W+x)*3
        pixels[idx] = int(pixels[idx]*f)
        pixels[idx+1] = int(pixels[idx+1]*f)
        pixels[idx+2] = int(pixels[idx+2]*f)

# PNG encode
print("PNG...", flush=True)
raw = bytearray()
for y in range(H):
    raw.append(0)  # filter none
    raw.extend(pixels[y*W*3:(y+1)*W*3])

def chunk(ct, d):
    c = ct + d; crc = zlib.crc32(c) & 0xFFFFFFFF
    return struct.pack('>I', len(d)) + c + struct.pack('>I', crc)

ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
comp = zlib.compress(bytes(raw), 6)
out = 'lab/butterfly-effect.png'
with open(out, 'wb') as f:
    f.write(b'\x89PNG\r\n\x1a\n')
    f.write(chunk(b'IHDR', ihdr))
    f.write(chunk(b'IDAT', comp))
    f.write(chunk(b'IEND', b''))

import os
el = time.time() - start
sz = os.path.getsize(out)
print(f'=== BUTTERFLY EFFECT ===')
print(f'σ={sigma} ρ={rho} β={beta:.4f}')
print(f'RK4 dt={dt} steps={steps}')
print(f'Δx₀ = 0.001')
if ds:
    print(f'Diverge: step {ds} (t={ds*dt:.2f}s)')
print(f'Max div: {max(divs):.2f}')
print(f'Final div: {divs[-1]:.2f}')
print(f'Time: {el:.1f}s | Size: {sz//1024}KB')
print(f'Output: {out}')
