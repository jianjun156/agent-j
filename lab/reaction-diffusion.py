#!/usr/bin/env python3
"""
EXP-20260329-012: TURING-SPOTS
Gray-Scott Reaction-Diffusion → Turing patterns.
Uses inline-compiled C for the hot loop. Pure Python rendering. Zero pip dependencies.
"""

import struct, zlib, time, random, os, tempfile, ctypes, math

W, H = 200, 200
STEPS = 5000
Du, Dv = 0.16, 0.08
f_rate, k_rate = 0.035, 0.065

# ── Compile C accelerator ──
C_SRC = r"""
#include <string.h>
#include <stdlib.h>

/* Run Gray-Scott, write final v into out_v */
void gray_scott(
    double *u, double *v, int W, int H, int steps,
    double Du, double Dv, double f, double k, double *out_v)
{
    int N = W * H;
    double *u2 = (double*)malloc(N * sizeof(double));
    double *v2 = (double*)malloc(N * sizeof(double));
    double *src_u = u, *src_v = v, *dst_u = u2, *dst_v = v2;
    
    for (int s = 0; s < steps; s++) {
        for (int y = 0; y < H; y++) {
            int ym = ((y-1+H)%H)*W, yp=((y+1)%H)*W, yc=y*W;
            for (int x = 0; x < W; x++) {
                int xm=(x-1+W)%W, xp=(x+1)%W, i=yc+x;
                double ui=src_u[i], vi=src_v[i];
                double lu = src_u[ym+x]+src_u[yp+x]+src_u[yc+xm]+src_u[yc+xp]-4.0*ui;
                double lv = src_v[ym+x]+src_v[yp+x]+src_v[yc+xm]+src_v[yc+xp]-4.0*vi;
                double uv2 = ui*vi*vi;
                double a = ui + Du*lu - uv2 + f*(1.0-ui);
                double b = vi + Dv*lv + uv2 - (f+k)*vi;
                if(a<0)a=0; if(a>1)a=1;
                if(b<0)b=0; if(b>1)b=1;
                dst_u[i]=a; dst_v[i]=b;
            }
        }
        double *t;
        t=src_u; src_u=dst_u; dst_u=t;
        t=src_v; src_v=dst_v; dst_v=t;
    }
    memcpy(out_v, src_v, N*sizeof(double));
    /* Also copy u back for caller */
    memcpy(u, src_u, N*sizeof(double));
    if(u2!=u && u2!=src_u) free(u2); 
    /* Simplified: just free the one that's not src */
    /* Actually safer: */
    if(src_u == u) { free(u2); free(v2); }
    else { /* src is u2,v2 — we already copied, free originals? No, caller owns those */
           /* Actually we malloc'd u2,v2, so free whichever is dst now */
           free(dst_u); free(dst_v);
    }
}
"""

# Simpler C — avoid complex free logic
C_SRC = r"""
void gray_scott(
    double *u0, double *v0, double *u1, double *v1,
    int W, int H, int steps,
    double Du, double Dv, double f, double k)
{
    /* Ping-pong between (u0,v0) and (u1,v1).
       After return, if steps is even result is in u0,v0; if odd in u1,v1. */
    double *su, *sv, *du, *dv;
    for (int s = 0; s < steps; s++) {
        if (s % 2 == 0) { su=u0; sv=v0; du=u1; dv=v1; }
        else             { su=u1; sv=v1; du=u0; dv=v0; }
        for (int y = 0; y < H; y++) {
            int ym=((y-1+H)%H)*W, yp=((y+1)%H)*W, yc=y*W;
            for (int x = 0; x < W; x++) {
                int xm=(x-1+W)%W, xp=(x+1)%W, i=yc+x;
                double ui=su[i], vi=sv[i];
                double lu=su[ym+x]+su[yp+x]+su[yc+xm]+su[yc+xp]-4.0*ui;
                double lv=sv[ym+x]+sv[yp+x]+sv[yc+xm]+sv[yc+xp]-4.0*vi;
                double uv2=ui*vi*vi;
                double a=ui+Du*lu-uv2+f*(1.0-ui);
                double b=vi+Dv*lv+uv2-(f+k)*vi;
                if(a<0)a=0; if(a>1)a=1;
                if(b<0)b=0; if(b>1)b=1;
                du[i]=a; dv[i]=b;
            }
        }
    }
}
"""

print("⚙️  Compiling C accelerator...")
t_compile = time.time()
tmpdir = tempfile.mkdtemp()
c_path = os.path.join(tmpdir, "gs.c")
so_path = os.path.join(tmpdir, "gs.so")
with open(c_path, 'w') as fh:
    fh.write(C_SRC)

import subprocess
result = subprocess.run(
    ["cc", "-O2", "-shared", "-o", so_path, c_path],
    capture_output=True, text=True
)
if result.returncode != 0:
    print("Compile error:", result.stderr)
    raise RuntimeError("C compilation failed")

lib = ctypes.CDLL(so_path)
DP = ctypes.POINTER(ctypes.c_double)
lib.gray_scott.restype = None
lib.gray_scott.argtypes = [DP, DP, DP, DP,
    ctypes.c_int, ctypes.c_int, ctypes.c_int,
    ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double]
print(f"   Compiled in {time.time()-t_compile:.2f}s")

# ── Initialize ──
N = W * H
Arr = ctypes.c_double * N
u0 = Arr(*([1.0]*N))
v0 = Arr(*([0.0]*N))
u1 = Arr(*([0.0]*N))
v1 = Arr(*([0.0]*N))

random.seed(42)
for _ in range(20):
    cx = random.randint(W//4, 3*W//4)
    cy = random.randint(H//4, 3*H//4)
    radius = random.randint(4, 10)
    for dy in range(-radius, radius+1):
        for dx in range(-radius, radius+1):
            if dx*dx + dy*dy <= radius*radius:
                x = (cx+dx) % W
                y = (cy+dy) % H
                u0[y*W+x] = 0.5
                v0[y*W+x] = 0.25

# ── Simulate ──
print(f"🔬 Running Gray-Scott: {W}×{H} grid, {STEPS} steps...")
t0 = time.time()
lib.gray_scott(u0, v0, u1, v1, W, H, STEPS, Du, Dv, f_rate, k_rate)
elapsed = time.time() - t0
print(f"   Done in {elapsed:.2f}s ({STEPS/elapsed:.0f} steps/s)")

# Result is in u0,v0 if STEPS even, u1,v1 if odd
if STEPS % 2 == 0:
    rv = [v0[i] for i in range(N)]
else:
    rv = [v1[i] for i in range(N)]

vmin = min(rv)
vmax = max(rv)
vavg = sum(rv)/N
print(f"   V ∈ [{vmin:.4f}, {vmax:.4f}], avg={vavg:.4f}")

# Count spots
spots = 0
for y in range(H):
    for x in range(W):
        val = rv[y*W+x]
        if val < 0.15: continue
        ok = True
        for dy2 in (-1,0,1):
            for dx2 in (-1,0,1):
                if dy2==0 and dx2==0: continue
                if rv[((y+dy2)%H)*W+(x+dx2)%W] > val:
                    ok = False; break
            if not ok: break
        if ok: spots += 1
print(f"   ~{spots} spots detected")

# ── Render 600×600 PNG ──
print("🎨 Rendering...")
CW, CH = 600, 600
SC = CW / W
vr = vmax - vmin + 1e-10

def cmap(t):
    """Deep navy → cyan → white"""
    if t<0.05:  return (6,8,18)
    if t<0.15:
        s=(t-0.05)/0.10
        return (int(6+s*14),int(8+s*28),int(18+s*55))
    if t<0.30:
        s=(t-0.15)/0.15
        return (int(20+s*8),int(36+s*80),int(73+s*75))
    if t<0.50:
        s=(t-0.30)/0.20
        return (int(28+s*25),int(116+s*80),int(148+s*45))
    if t<0.70:
        s=(t-0.50)/0.20
        return (int(53+s*55),int(196+s*35),int(193+s*30))
    if t<0.85:
        s=(t-0.70)/0.15
        return (int(108+s*100),int(231+s*16),int(223+s*22))
    s=min(1.0,(t-0.85)/0.15)
    return (min(255,int(208+s*47)),min(255,int(247+s*8)),min(255,int(245+s*10)))

raw = bytearray()
for cy in range(CH):
    raw.append(0)
    gy = cy / SC
    gy0 = int(gy) % H; gy1 = (gy0+1) % H
    fy = gy - int(gy)
    o0 = gy0*W; o1 = gy1*W
    for cx in range(CW):
        gx = cx / SC
        gx0 = int(gx) % W; gx1 = (gx0+1) % W
        fx = gx - int(gx)
        val = (rv[o0+gx0]*(1-fx)*(1-fy) + rv[o0+gx1]*fx*(1-fy) +
               rv[o1+gx0]*(1-fx)*fy + rv[o1+gx1]*fx*fy)
        t = max(0.0, min(1.0, (val-vmin)/vr))
        r,g,b = cmap(t)
        # Vignette
        ddx=(cx-300)/300.0; ddy=(cy-300)/300.0
        vig=max(0.45, 1.0-0.35*(ddx*ddx+ddy*ddy))
        raw.extend([int(r*vig),int(g*vig),int(b*vig)])

# Top glow
for y in range(3):
    a=0.5-y*0.15
    base=y*(CW*3+1)+1
    for x in range(CW):
        off=base+x*3
        raw[off]=min(255,int(raw[off]+(74-raw[off])*a))
        raw[off+1]=min(255,int(raw[off+1]+(170-raw[off+1])*a))
        raw[off+2]=min(255,int(raw[off+2]+(255-raw[off+2])*a))

# Write PNG
def write_png(fn, rd, w, h):
    def ch(ct,d):
        c=ct+d; return struct.pack('>I',len(d))+c+struct.pack('>I',zlib.crc32(c)&0xFFFFFFFF)
    comp=zlib.compress(bytes(rd),9)
    out=b'\x89PNG\r\n\x1a\n'
    out+=ch(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))
    out+=ch(b'IDAT',comp)
    out+=ch(b'IEND',b'')
    with open(fn,'wb') as fh: fh.write(out)
    return len(out)

outpath = '/Users/jianjun/.openclaw/workspace/agent-j/lab/turing-spots.png'
sz = write_png(outpath, raw, CW, CH)
print(f"\n✅ {outpath} ({sz//1024}KB)")
print(f"   {W}×{H} grid, {STEPS} steps, {elapsed:.2f}s")
print(f"   Du={Du} Dv={Dv} f={f_rate} k={k_rate}")
print(f"   ~{spots} Turing spots")
print(f"\n🧬 TURING-SPOTS experiment complete!")

# Cleanup
try:
    os.unlink(c_path); os.unlink(so_path); os.rmdir(tmpdir)
except: pass
