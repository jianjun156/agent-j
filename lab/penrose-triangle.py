#!/usr/bin/env python3
"""
EXP-20260401-015: PENROSE-PARADOX
Impossible Penrose Triangle — an object that can't exist in 3D, rendered in 2D.
Perfect for April Fool's Day: your brain insists it's real, but geometry says no.
Pure Python, zero external dependencies, hand-rolled PNG encoder.
"""
import struct, zlib, math, hashlib

WIDTH, HEIGHT = 800, 800
BG = (10, 12, 28)  # deep navy background

def make_png(w, h, pixels):
    """Hand-rolled PNG encoder, zero dependencies."""
    def chunk(ctype, data):
        c = ctype + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xFFFFFFFF)
    
    raw = b''
    for y in range(h):
        raw += b'\x00'  # filter: none
        for x in range(w):
            r, g, b = pixels[y * w + x]
            raw += struct.pack('BBB', min(255, max(0, r)), min(255, max(0, g)), min(255, max(0, b)))
    
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    return sig + chunk(b'IHDR', ihdr) + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b'')

def lerp_color(c1, c2, t):
    t = max(0, min(1, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def point_in_triangle(px, py, x1, y1, x2, y2, x3, y3):
    """Barycentric coordinate test for point-in-triangle."""
    d = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
    if abs(d) < 1e-10:
        return False
    a = ((y2 - y3) * (px - x3) + (x3 - x2) * (py - y3)) / d
    b = ((y3 - y1) * (px - x3) + (x1 - x3) * (py - y3)) / d
    c = 1 - a - b
    return a >= 0 and b >= 0 and c >= 0

def dist_to_segment(px, py, ax, ay, bx, by):
    """Distance from point to line segment."""
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.sqrt((px - ax)**2 + (py - ay)**2)
    t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    cx, cy = ax + t * dx, ay + t * dy
    return math.sqrt((px - cx)**2 + (py - cy)**2)

def draw_penrose():
    """Draw a Penrose impossible triangle with 3D shading."""
    pixels = [BG] * (WIDTH * HEIGHT)
    cx, cy = WIDTH // 2, HEIGHT // 2 + 20
    
    # The Penrose triangle: 3 bars that connect in an impossible way
    # Each bar has an outer edge and inner edge, creating depth illusion
    
    size = 280  # distance from center to vertex
    bar_w = 70  # width of each bar
    
    # Three vertices of the outer triangle (pointing up)
    angle_offset = -math.pi / 2  # top vertex
    outer_verts = []
    for i in range(3):
        a = angle_offset + i * 2 * math.pi / 3
        outer_verts.append((cx + size * math.cos(a), cy + size * math.sin(a)))
    
    # Three vertices of the inner triangle (smaller, rotated slightly)
    inner_size = size - bar_w * 1.73  # adjusted for equilateral proportions
    inner_verts = []
    for i in range(3):
        a = angle_offset + i * 2 * math.pi / 3
        inner_verts.append((cx + inner_size * math.cos(a), cy + inner_size * math.sin(a)))
    
    # The impossible triangle is constructed from three parallelogram-like bars
    # Each bar connects two outer vertices and has an inner edge
    # The "impossibility" comes from how the inner corners connect
    
    # Define the three faces of each bar (light, medium, dark shading)
    # Bar colors - three distinct face colors for 3D effect
    face_colors = [
        # Face 1 (lightest - top-facing)
        (80, 200, 255),   # bright cyan
        # Face 2 (medium - side)  
        (40, 130, 200),   # medium blue
        # Face 3 (darkest - shadow)
        (20, 70, 140),    # dark blue
    ]
    
    # Alternative: use neon color scheme for April Fool's vibe
    neon_faces = [
        [(0, 255, 200), (0, 180, 140), (0, 100, 80)],    # neon cyan/teal
        [(255, 100, 200), (180, 60, 140), (100, 30, 80)], # neon pink
        [(120, 200, 255), (80, 140, 200), (40, 80, 140)], # neon blue
    ]
    
    # Build the impossible triangle geometry
    # Each "beam" of the triangle has 3 visible faces
    # The trick: at each corner, one beam appears to pass OVER the other
    
    # Outer triangle vertices
    Ax, Ay = outer_verts[0]  # top
    Bx, By = outer_verts[1]  # bottom-right
    Cx, Cy = outer_verts[2]  # bottom-left
    
    # Inner triangle vertices  
    ax, ay = inner_verts[0]  # top-inner
    bx, by = inner_verts[1]  # bottom-right-inner
    cx_i, cy_i = inner_verts[2]  # bottom-left-inner
    
    # For the Penrose triangle, we need to offset the inner vertices
    # to create the 3D beam effect
    # Each beam has a "top face" and "side face"
    
    # Compute perpendicular offsets for 3D depth
    depth = bar_w * 0.5
    
    # Let me build this more carefully with explicit polygon regions
    # The Penrose triangle consists of three beams, each drawn as a set of parallelograms
    
    # Redefine with cleaner geometry
    # Outer equilateral triangle
    R = 280  # outer radius
    r = 140  # inner radius (hole)
    
    # Outer corners
    pts_out = []
    for i in range(3):
        a = -math.pi/2 + i * 2*math.pi/3
        pts_out.append((cx + R * math.cos(a), cy + R * math.sin(a)))
    
    # Inner corners (rotated 60° from outer to create the impossible effect)
    pts_in = []
    for i in range(3):
        a = -math.pi/2 + (i + 0.5) * 2*math.pi/3  # offset by 60°
        pts_in.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    
    # Now define the three beams
    # Beam 0: from pts_out[0] (top) to pts_out[1] (bottom-right)
    # Beam 1: from pts_out[1] (bottom-right) to pts_out[2] (bottom-left)
    # Beam 2: from pts_out[2] (bottom-left) to pts_out[0] (top)
    
    # Each beam is a trapezoid with a "3D" side
    # The impossible connection: inner vertex of beam N connects to beam N+1 in a way
    # that creates the paradox
    
    # Let me use a simpler approach: draw the Penrose triangle as filled polygons
    # with explicit "overlap" regions to create the illusion
    
    # Simplified Penrose construction:
    # Three thick bars forming a triangle, with each corner having one bar
    # passing "over" the other in a cyclic impossible way
    
    T = 65  # bar thickness
    L = 300  # half-length of triangle side
    
    # Define the triangle in terms of three bars
    # Each bar is defined by its center line (between two outer vertices)
    # and thickness T
    
    # Outer vertices of equilateral triangle
    ov = []
    for i in range(3):
        a = -math.pi/2 + i * 2*math.pi/3
        ov.append((cx + L * math.cos(a), cy + L * math.sin(a)))
    
    # For each edge, compute the outward and inward parallel lines
    edges = [(0,1), (1,2), (2,0)]
    
    # Direction perpendicular to each edge (pointing outward)
    perps = []
    for i, (a, b) in enumerate(edges):
        dx = ov[b][0] - ov[a][0]
        dy = ov[b][1] - ov[a][1]
        length = math.sqrt(dx*dx + dy*dy)
        # Normal pointing outward (right-hand rule for CW winding)
        nx, ny = dy/length, -dx/length
        perps.append((nx, ny))
    
    # For the 3D effect, we'll add a depth direction
    # Light comes from upper-left, so top faces are bright, right faces medium, bottom dark
    
    # Actually, let me take a different approach that's more reliable:
    # Draw the Penrose triangle pixel by pixel using a distance-field approach
    
    # For each pixel, determine if it's inside the thick triangle outline
    # and which "face" it belongs to based on distance to edges
    
    # Thick triangle = outer triangle minus inner triangle, 
    # but with impossible corners
    
    # Let me use a well-known construction:
    # The Penrose triangle can be drawn as three L-shaped bars
    # Each bar covers one corner and two half-edges
    
    # I'll define three quadrilateral regions (the three visible faces)
    
    # Key points for the Penrose triangle construction
    s = 260  # size
    t = 75   # thickness
    
    # The three outer vertices
    v = []
    for i in range(3):
        a = -math.pi/2 + i * 2*math.pi/3
        v.append((cx + s * math.cos(a), cy + s * math.sin(a)))
    
    # For each vertex, compute two points offset inward along each adjacent edge
    # and offset by thickness perpendicular to create the 3D bar
    
    # Edge directions
    def normalize(dx, dy):
        l = math.sqrt(dx*dx + dy*dy)
        return dx/l, dy/l if l > 0 else (0, 0)
    
    # Let me just hardcode a clean Penrose triangle using explicit coordinates
    # This is the most reliable way
    
    # Scale factor
    sc = 3.2
    
    # Classic Penrose triangle coordinates (normalized, then scaled)
    # Three bars, each with a light face and dark face
    
    # I'll use a parameterized approach:
    # Outer triangle with vertices at equal spacing
    # Inner triangle (smaller, same orientation)
    # But with cyclic "overlap" at corners
    
    # Outer vertices
    top = (cx, cy - 260)
    br = (cx + 225, cy + 130)
    bl = (cx - 225, cy + 130)
    
    # Inner vertices (for the triangular hole)
    # These are offset inward by the bar thickness
    itop = (cx, cy - 115)
    ibr = (cx + 100, cy + 57)
    ibl = (cx - 100, cy + 57)
    
    # The three bars of the Penrose triangle
    # Bar A: top to bottom-right (right edge)
    # Bar B: bottom-right to bottom-left (bottom edge)
    # Bar C: bottom-left to top (left edge)
    
    # For the impossible effect, at each corner one bar's inner edge
    # connects to a different position than geometrically possible
    
    # Let me define each bar as a filled polygon
    # Bar A (right side): top → bottom-right, colors: neon cyan
    # Top face of bar A
    barA_top = [top, br, ibr, itop]
    
    # Bar B (bottom): bottom-right → bottom-left, colors: neon pink
    barB_top = [br, bl, ibl, ibr]
    
    # Bar C (left side): bottom-left → top, colors: neon blue
    barC_top = [bl, top, itop, ibl]
    
    # But this just makes a regular thick triangle, not impossible!
    # The impossibility comes from the 3D depth effect at each corner.
    
    # Let me add 3D depth by splitting each bar into a "top face" and "side face"
    # The depth offset creates the illusion
    d = 35  # depth offset
    
    # Depth direction for each bar face (simulating 3D extrusion)
    # Bar A (right edge): depth goes left-down → creates a left face
    # Bar B (bottom edge): depth goes up → creates a top face  
    # Bar C (left edge): depth goes right-down → creates a right face
    
    # Top outer vertices with depth offset
    top_d = (top[0] - d, top[1] + d * 0.5)
    br_d = (br[0] - d, br[1] + d * 0.5)
    bl_d = (bl[0] - d, bl[1] + d * 0.5)
    itop_d = (itop[0] - d, itop[1] + d * 0.5)
    ibr_d = (ibr[0] - d, ibr[1] + d * 0.5)
    ibl_d = (ibl[0] - d, ibl[1] + d * 0.5)
    
    # OK this is getting complex. Let me use a much simpler and more reliable approach:
    # Pre-compute a classic Penrose triangle using explicit vertex coordinates.
    
    # Classic Penrose triangle with 3D shading
    # Using the well-known construction with 3 parallelogram beams
    
    # Outer triangle pointing up
    s = 250
    h = s * math.sqrt(3) / 2  # height of equilateral triangle
    
    OA = (cx, cy - h * 2/3)           # top vertex
    OB = (cx + s/2, cy + h * 1/3)     # bottom right
    OC = (cx - s/2, cy + h * 1/3)     # bottom left
    
    # Bar width
    w = 65
    
    # For each edge, compute inner parallel edge
    # Edge AB direction
    def vec_sub(a, b): return (a[0]-b[0], a[1]-b[1])
    def vec_add(a, b): return (a[0]+b[0], a[1]+b[1])
    def vec_scale(v, s): return (v[0]*s, v[1]*s)
    def vec_len(v): return math.sqrt(v[0]**2 + v[1]**2)
    def vec_norm(v): 
        l = vec_len(v)
        return (v[0]/l, v[1]/l) if l > 0 else (0,0)
    def vec_perp(v): return (-v[1], v[0])  # 90° CCW rotation
    
    # The three edges
    edge_AB = vec_norm(vec_sub(OB, OA))
    edge_BC = vec_norm(vec_sub(OC, OB))
    edge_CA = vec_norm(vec_sub(OA, OC))
    
    # Inward perpendiculars (pointing into the triangle)
    perp_AB = vec_perp(edge_AB)  # Should point left (into triangle)
    perp_BC = vec_perp(edge_BC)  # Should point up-right (into triangle)
    perp_CA = vec_perp(edge_CA)  # Should point right-down... 
    
    # Check: for edge AB (going right-down), perp should point left-down (inward)
    # Actually need to check direction. For CCW winding, left perpendicular points inward.
    # Our triangle is CW (top, bottom-right, bottom-left), so right perpendicular is inward.
    # vec_perp gives CCW rotation, so we need negative for inward
    
    # Let me just compute the inward normal by checking which side the opposite vertex is on
    def inward_perp(edge_dir, p_on_edge, p_opposite):
        n = vec_perp(edge_dir)  # CCW perpendicular
        # Check if opposite point is on the positive side
        test = (p_opposite[0] - p_on_edge[0]) * n[0] + (p_opposite[1] - p_on_edge[1]) * n[1]
        if test < 0:
            n = (-n[0], -n[1])
        return n
    
    nAB = inward_perp(edge_AB, OA, OC)  # inward normal for edge AB
    nBC = inward_perp(edge_BC, OB, OA)  # inward normal for edge BC
    nCA = inward_perp(edge_CA, OC, OB)  # inward normal for edge CA
    
    # Inner vertices: offset each outer vertex inward along the two adjacent edges' normals
    # For vertex A: move along nAB and nCA
    # The inner vertex is at the intersection of the two offset edges
    
    # Offset edge AB inward by w: new line passes through OA + w*nAB, direction edge_AB
    # Offset edge CA inward by w: new line passes through OC + w*nCA, direction edge_CA
    
    def line_intersect(p1, d1, p2, d2):
        """Intersection of line (p1 + t*d1) and (p2 + s*d2)"""
        det = d1[0]*d2[1] - d1[1]*d2[0]
        if abs(det) < 1e-10:
            return p1  # parallel, shouldn't happen
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        t = (dx*d2[1] - dy*d2[0]) / det
        return (p1[0] + t*d1[0], p1[1] + t*d1[1])
    
    # Inner vertex near A: intersection of (AB offset inward) and (CA offset inward)
    IA = line_intersect(
        vec_add(OA, vec_scale(nAB, w)), edge_AB,
        vec_add(OC, vec_scale(nCA, w)), edge_CA
    )
    
    # Inner vertex near B: intersection of (AB offset inward) and (BC offset inward)
    IB = line_intersect(
        vec_add(OA, vec_scale(nAB, w)), edge_AB,
        vec_add(OB, vec_scale(nBC, w)), edge_BC
    )
    
    # Inner vertex near C: intersection of (BC offset inward) and (CA offset inward)
    IC = line_intersect(
        vec_add(OB, vec_scale(nBC, w)), edge_BC,
        vec_add(OC, vec_scale(nCA, w)), edge_CA
    )
    
    # Now we have outer triangle (OA, OB, OC) and inner triangle (IA, IB, IC)
    # The regular thick triangle = outer - inner
    # For the IMPOSSIBLE triangle, we modify the corners
    
    # At each corner, one bar passes "over" the other
    # Corner A: the left bar (CA) passes over the right bar (AB)
    # Corner B: the right bar (AB) passes over the bottom bar (BC)
    # Corner C: the bottom bar (BC) passes over the left bar (CA)
    # This creates the cyclic impossibility!
    
    # For the 3D effect, each bar has 2 visible faces:
    # - A bright face (top/front)
    # - A darker face (side)
    # The depth illusion is created by a consistent shading direction
    
    # Depth offset vector (light from upper-left)
    depth = 32
    dv = (-depth * 0.6, depth * 0.35)
    
    # For each bar, define the "top face" and "side face" as polygons
    # Bar AB (right side): from vertex A to vertex B
    # Top face: the strip between outer edge AB and inner edge AB
    # Side face: the depth face along the inner edge
    
    # Let me define midpoints on each edge for the corner overlap construction
    # On outer edge AB: midpoint between A and B on the outer side
    # We need points where the bars "break" at corners
    
    # For the Penrose trick at corner A:
    # The outer point is OA
    # The "entering" bar is CA (from left)
    # The "exiting" bar is AB (to right)
    # CA should appear to go OVER AB
    # This means: near corner A, the CA bar's polygon covers the AB bar's polygon
    
    # The construction: 
    # 1. Draw all three bars as the thick triangle regions
    # 2. At each corner, add a small "cap" polygon that covers one bar's end
    
    # Actually, the cleanest way to render a Penrose triangle:
    # Just define all polygons explicitly and draw them in the right order
    
    # Three quadrilateral faces for the main bars:
    # Face 1 (right bar, top face): OA, OB, IB, IA - light cyan
    # Face 2 (bottom bar, top face): OB, OC, IC, IB - light pink
    # Face 3 (left bar, top face): OC, OA, IA, IC - light blue
    
    # But for the 3D impossible effect, we need to split each into sub-faces
    # and add depth faces
    
    # Let me try a cleaner approach: render the Penrose triangle using
    # distance-based shading for a smooth 3D look
    
    # Actually, the simplest reliable Penrose: use explicit polygons
    # with clear overlap at corners
    
    # Define 6 key points: 3 outer, 3 inner
    # Then define the three bars, each as a trapezoid
    # Draw in order with corner overlaps
    
    # For the impossibility: at each corner, extend one bar's polygon
    # to cover the other bar's end
    
    # Corner A overlap: extend inner edge of bar CA past IA to cover bar AB's start
    # Corner B overlap: extend inner edge of bar AB past IB to cover bar BC's start  
    # Corner C overlap: extend inner edge of bar BC past IC to cover bar CA's start
    
    # Points for extended corners
    ext = 30  # extension length
    
    # At corner A: bar CA extends past IA along edge CA direction
    # The extended point goes toward the inner edge of bar AB
    IA_ext = vec_add(IA, vec_scale(edge_CA, ext))
    
    # At corner B: bar AB extends past IB
    IB_ext = vec_add(IB, vec_scale(edge_AB, ext))
    
    # At corner C: bar BC extends past IC
    IC_ext = vec_add(IC, vec_scale(edge_BC, ext))
    
    print(f"Outer: A={OA}, B={OB}, C={OC}")
    print(f"Inner: A={IA}, B={IB}, C={IC}")
    
    # OK let me just use a totally different, proven approach.
    # I'll render the Penrose triangle as three colored L-shaped bars
    # drawn in a specific Z-order to create the impossible overlap.
    
    # === FINAL APPROACH: Explicit polygon-based Penrose triangle ===
    
    # Parameters
    R = 250      # outer radius
    r = 130      # inner radius (triangular hole)
    
    # Outer equilateral triangle vertices
    A = (cx, cy - R)
    B = (cx + R * math.cos(math.radians(-30)), cy + R * math.sin(math.radians(-30)))  
    C = (cx + R * math.cos(math.radians(210)), cy + R * math.sin(math.radians(210)))
    
    # Recompute cleanly
    A = (cx, cy - R)
    B = (cx + R * math.sin(math.radians(60)), cy + R * math.cos(math.radians(60)) * (-1) + R)
    
    # Just use trig directly
    A = (cx + R * math.cos(math.radians(90)), cy - R * math.sin(math.radians(90)))  # top
    B = (cx + R * math.cos(math.radians(-30)), cy - R * math.sin(math.radians(-30)))  # bottom-right
    C = (cx + R * math.cos(math.radians(210)), cy - R * math.sin(math.radians(210)))  # bottom-left
    
    print(f"A={A}, B={B}, C={C}")
    
    # Inner triangle vertices (same orientation, smaller)
    IA = (cx + r * math.cos(math.radians(90)), cy - r * math.sin(math.radians(90)))
    IB = (cx + r * math.cos(math.radians(-30)), cy - r * math.sin(math.radians(-30)))
    IC = (cx + r * math.cos(math.radians(210)), cy - r * math.sin(math.radians(210)))
    
    print(f"IA={IA}, IB={IB}, IC={IC}")
    
    # Helper: fill a convex polygon
    def fill_polygon(poly, color, pixels, w, h):
        """Fill a convex polygon with a solid color using scanline."""
        # Get bounding box
        min_y = max(0, int(min(p[1] for p in poly)))
        max_y = min(h-1, int(max(p[1] for p in poly)))
        min_x = max(0, int(min(p[0] for p in poly)))
        max_x = min(w-1, int(max(p[0] for p in poly)))
        
        n = len(poly)
        for y in range(min_y, max_y + 1):
            # Find intersections with polygon edges
            xs = []
            for i in range(n):
                j = (i + 1) % n
                y1, y2 = poly[i][1], poly[j][1]
                if y1 == y2:
                    continue
                if min(y1, y2) <= y < max(y1, y2):
                    t = (y - y1) / (y2 - y1)
                    x = poly[i][0] + t * (poly[j][0] - poly[i][0])
                    xs.append(x)
            
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                x_start = max(min_x, int(xs[k]))
                x_end = min(max_x, int(xs[k + 1]))
                for x in range(x_start, x_end + 1):
                    pixels[y * w + x] = color
    
    def fill_polygon_gradient(poly, color1, color2, grad_start, grad_end, pixels, w, h):
        """Fill polygon with gradient based on distance from grad_start to grad_end."""
        min_y = max(0, int(min(p[1] for p in poly)))
        max_y = min(h-1, int(max(p[1] for p in poly)))
        
        gx = grad_end[0] - grad_start[0]
        gy = grad_end[1] - grad_start[1]
        gl = gx*gx + gy*gy
        
        n = len(poly)
        for y in range(min_y, max_y + 1):
            xs = []
            for i in range(n):
                j = (i + 1) % n
                y1, y2 = poly[i][1], poly[j][1]
                if y1 == y2:
                    continue
                if min(y1, y2) <= y < max(y1, y2):
                    t = (y - y1) / (y2 - y1)
                    x = poly[i][0] + t * (poly[j][0] - poly[i][0])
                    xs.append(x)
            
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                x_start = max(0, int(xs[k]))
                x_end = min(w-1, int(xs[k + 1]))
                for x in range(x_start, x_end + 1):
                    # Compute gradient parameter
                    if gl > 0:
                        t = ((x - grad_start[0]) * gx + (y - grad_start[1]) * gy) / gl
                        t = max(0, min(1, t))
                    else:
                        t = 0.5
                    color = lerp_color(color1, color2, t)
                    pixels[y * w + x] = color
    
    # Now define the three bars of the Penrose triangle
    # Each bar is an L-shaped region covering one corner and two half-edges
    
    # For the impossible connection, we draw three quadrilaterals in order
    # with specific overlaps at corners
    
    # Bar 1 (right side: A→B): quad [A, B, IB, IA]  
    # Bar 2 (bottom: B→C): quad [B, C, IC, IB]
    # Bar 3 (left side: C→A): quad [C, A, IA, IC]
    
    # For Penrose impossibility:
    # At corner A: bar 3 (left) overlaps bar 1 (right) — bar 3 drawn AFTER bar 1
    # At corner B: bar 1 (right) overlaps bar 2 (bottom) — bar 1 drawn AFTER bar 2
    # At corner C: bar 2 (bottom) overlaps bar 3 (left) — bar 2 drawn AFTER bar 3
    # 
    # This is cyclically impossible! 3 > 1 > 2 > 3
    # Solution: split one bar and draw in two parts
    
    # Split bar 1 into two halves:
    # - Bar 1a (upper half: A to midpoint of AB)
    # - Bar 1b (lower half: midpoint of AB to B)
    
    M_AB = ((A[0]+B[0])/2, (A[1]+B[1])/2)
    M_IAB = ((IA[0]+IB[0])/2, (IA[1]+IB[1])/2)
    
    # Drawing order for Penrose impossibility:
    # 1. Bar 1a (upper right) — goes under bar 3 at corner A
    # 2. Bar 3 (left side) — over bar 1a at corner A, under bar 2 at corner C
    # 3. Bar 2 (bottom) — over bar 3 at corner C, under bar 1b at corner B
    # 4. Bar 1b (lower right) — over bar 2 at corner B
    
    # Color scheme: three different neon colors for three bars
    # Bar 1: Neon cyan
    c1_light = (0, 230, 210)
    c1_mid = (0, 170, 160)
    c1_dark = (0, 100, 95)
    
    # Bar 2: Neon magenta/pink
    c2_light = (255, 80, 180)
    c2_mid = (190, 50, 130)
    c2_dark = (120, 30, 80)
    
    # Bar 3: Neon blue/purple
    c3_light = (100, 140, 255)
    c3_mid = (60, 90, 200)
    c3_dark = (30, 50, 140)
    
    # For 3D effect: each bar has a bright front face and darker side face
    # Side faces are created by offsetting the inner edge
    
    # Depth offset for 3D (light from upper-left)
    dd = 25
    dx_d, dy_d = -dd * 0.5, dd * 0.5
    
    # Create depth-shifted inner vertices
    IA_d = (IA[0] + dx_d, IA[1] + dy_d)
    IB_d = (IB[0] + dx_d, IB[1] + dy_d)
    IC_d = (IC[0] + dx_d, IC[1] + dy_d)
    M_IAB_d = (M_IAB[0] + dx_d, M_IAB[1] + dy_d)
    
    # Draw order:
    # 1. Side faces first (darker, behind)
    # 2. Then front faces (brighter, in front)
    
    # Bar 1a side face (depth face along inner edge, upper half)
    side_1a = [IA, M_IAB, M_IAB_d, IA_d]
    # Bar 1a front face
    front_1a = [A, M_AB, M_IAB, IA]
    
    # Bar 3 side face
    side_3 = [IC, IA, IA_d, IC_d]
    # Bar 3 front face
    front_3 = [C, A, IA, IC]
    
    # Bar 2 side face
    side_2 = [IB, IC, IC_d, IB_d]
    # Bar 2 front face
    front_2 = [B, C, IC, IB]
    
    # Bar 1b side face
    side_1b = [M_IAB, IB, IB_d, M_IAB_d]
    # Bar 1b front face
    front_1b = [M_AB, B, IB, M_IAB]
    
    # Draw in Penrose order:
    # Layer 1: Bar 1a (will be partially covered by bar 3)
    fill_polygon(side_1a, c1_dark, pixels, WIDTH, HEIGHT)
    fill_polygon(front_1a, c1_light, pixels, WIDTH, HEIGHT)
    
    # Layer 2: Bar 3 (covers bar 1a at corner A, will be covered by bar 2 at corner C)
    fill_polygon(side_3, c3_dark, pixels, WIDTH, HEIGHT)
    fill_polygon(front_3, c3_light, pixels, WIDTH, HEIGHT)
    
    # Layer 3: Bar 2 (covers bar 3 at corner C, will be covered by bar 1b at corner B)
    fill_polygon(side_2, c2_dark, pixels, WIDTH, HEIGHT)
    fill_polygon(front_2, c2_light, pixels, WIDTH, HEIGHT)
    
    # Layer 4: Bar 1b (covers bar 2 at corner B)
    fill_polygon(side_1b, c1_dark, pixels, WIDTH, HEIGHT)
    fill_polygon(front_1b, c1_light, pixels, WIDTH, HEIGHT)
    
    # Add edge lines for definition
    def draw_line(x1, y1, x2, y2, color, thickness, pixels, w, h):
        """Draw an anti-aliased thick line."""
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx*dx + dy*dy)
        if length == 0:
            return
        steps = int(length * 2)
        for i in range(steps + 1):
            t = i / max(1, steps)
            px = x1 + t * dx
            py = y1 + t * dy
            for oy in range(-thickness, thickness + 1):
                for ox in range(-thickness, thickness + 1):
                    if ox*ox + oy*oy <= thickness * thickness:
                        ix, iy = int(px + ox), int(py + oy)
                        if 0 <= ix < w and 0 <= iy < h:
                            pixels[iy * w + ix] = color
    
    edge_color = (15, 20, 40)
    lw = 2
    
    # Outer triangle edges
    draw_line(A[0], A[1], B[0], B[1], edge_color, lw, pixels, WIDTH, HEIGHT)
    draw_line(B[0], B[1], C[0], C[1], edge_color, lw, pixels, WIDTH, HEIGHT)
    draw_line(C[0], C[1], A[0], A[1], edge_color, lw, pixels, WIDTH, HEIGHT)
    
    # Inner triangle edges
    draw_line(IA[0], IA[1], IB[0], IB[1], edge_color, lw, pixels, WIDTH, HEIGHT)
    draw_line(IB[0], IB[1], IC[0], IC[1], edge_color, lw, pixels, WIDTH, HEIGHT)
    draw_line(IC[0], IC[1], IA[0], IA[1], edge_color, lw, pixels, WIDTH, HEIGHT)
    
    # Depth edges
    draw_line(IA[0], IA[1], IA_d[0], IA_d[1], edge_color, lw, pixels, WIDTH, HEIGHT)
    draw_line(IB[0], IB[1], IB_d[0], IB_d[1], edge_color, lw, pixels, WIDTH, HEIGHT)
    draw_line(IC[0], IC[1], IC_d[0], IC_d[1], edge_color, lw, pixels, WIDTH, HEIGHT)
    draw_line(IA_d[0], IA_d[1], IB_d[0], IB_d[1], edge_color, lw, pixels, WIDTH, HEIGHT)
    draw_line(IB_d[0], IB_d[1], IC_d[0], IC_d[1], edge_color, lw, pixels, WIDTH, HEIGHT)
    draw_line(IC_d[0], IC_d[1], IA_d[0], IA_d[1], edge_color, lw, pixels, WIDTH, HEIGHT)
    
    # Split line at midpoint
    draw_line(M_AB[0], M_AB[1], M_IAB[0], M_IAB[1], edge_color, 1, pixels, WIDTH, HEIGHT)
    draw_line(M_IAB[0], M_IAB[1], M_IAB_d[0], M_IAB_d[1], edge_color, 1, pixels, WIDTH, HEIGHT)
    
    # Add glow effect around the triangle
    # We'll add a subtle outer glow by scanning for edge pixels
    
    # Add a title at the top
    # Using a simple 5x7 bitmap font
    font_5x7 = {
        'A': ["01110","10001","10001","11111","10001","10001","10001"],
        'B': ["11110","10001","10001","11110","10001","10001","11110"],
        'C': ["01110","10001","10000","10000","10000","10001","01110"],
        'D': ["11100","10010","10001","10001","10001","10010","11100"],
        'E': ["11111","10000","10000","11110","10000","10000","11111"],
        'F': ["11111","10000","10000","11110","10000","10000","10000"],
        'G': ["01110","10001","10000","10111","10001","10001","01110"],
        'H': ["10001","10001","10001","11111","10001","10001","10001"],
        'I': ["01110","00100","00100","00100","00100","00100","01110"],
        'J': ["00111","00010","00010","00010","00010","10010","01100"],
        'K': ["10001","10010","10100","11000","10100","10010","10001"],
        'L': ["10000","10000","10000","10000","10000","10000","11111"],
        'M': ["10001","11011","10101","10101","10001","10001","10001"],
        'N': ["10001","10001","11001","10101","10011","10001","10001"],
        'O': ["01110","10001","10001","10001","10001","10001","01110"],
        'P': ["11110","10001","10001","11110","10000","10000","10000"],
        'Q': ["01110","10001","10001","10001","10101","10010","01101"],
        'R': ["11110","10001","10001","11110","10100","10010","10001"],
        'S': ["01111","10000","10000","01110","00001","00001","11110"],
        'T': ["11111","00100","00100","00100","00100","00100","00100"],
        'U': ["10001","10001","10001","10001","10001","10001","01110"],
        'V': ["10001","10001","10001","10001","01010","01010","00100"],
        'W': ["10001","10001","10001","10101","10101","10101","01010"],
        'X': ["10001","10001","01010","00100","01010","10001","10001"],
        'Y': ["10001","10001","01010","00100","00100","00100","00100"],
        'Z': ["11111","00001","00010","00100","01000","10000","11111"],
        '0': ["01110","10001","10011","10101","11001","10001","01110"],
        '1': ["00100","01100","00100","00100","00100","00100","01110"],
        '2': ["01110","10001","00001","00010","00100","01000","11111"],
        '3': ["11110","00001","00001","00110","00001","00001","11110"],
        '4': ["00010","00110","01010","10010","11111","00010","00010"],
        '5': ["11111","10000","11110","00001","00001","10001","01110"],
        '6': ["00110","01000","10000","11110","10001","10001","01110"],
        '7': ["11111","00001","00010","00100","01000","01000","01000"],
        '8': ["01110","10001","10001","01110","10001","10001","01110"],
        '9': ["01110","10001","10001","01111","00001","00010","01100"],
        ' ': ["00000","00000","00000","00000","00000","00000","00000"],
        '-': ["00000","00000","00000","11111","00000","00000","00000"],
        '.': ["00000","00000","00000","00000","00000","00000","00100"],
        ':': ["00000","00100","00100","00000","00100","00100","00000"],
        '!': ["00100","00100","00100","00100","00100","00000","00100"],
        '?': ["01110","10001","00001","00110","00100","00000","00100"],
        '/': ["00001","00010","00010","00100","01000","01000","10000"],
        '\'': ["00100","00100","00000","00000","00000","00000","00000"],
        '#': ["01010","01010","11111","01010","11111","01010","01010"],
    }
    
    def draw_text(text, start_x, start_y, scale, color, pixels, w, h):
        """Draw text using 5x7 bitmap font."""
        cursor_x = start_x
        for ch in text.upper():
            glyph = font_5x7.get(ch)
            if glyph is None:
                cursor_x += 6 * scale
                continue
            for row_i, row in enumerate(glyph):
                for col_i, bit in enumerate(row):
                    if bit == '1':
                        for dy in range(scale):
                            for dx in range(scale):
                                px = cursor_x + col_i * scale + dx
                                py = start_y + row_i * scale + dy
                                if 0 <= px < w and 0 <= py < h:
                                    pixels[py * w + px] = color
            cursor_x += 6 * scale
    
    # Title
    title = "PENROSE PARADOX"
    title_w = len(title) * 6 * 3
    draw_text(title, (WIDTH - title_w) // 2, 50, 3, (0, 230, 210), pixels, WIDTH, HEIGHT)
    
    # Subtitle
    sub = "EXP-015  APRIL FOOLS 2026"
    sub_w = len(sub) * 6 * 2
    draw_text(sub, (WIDTH - sub_w) // 2, 85, 2, (100, 140, 200), pixels, WIDTH, HEIGHT)
    
    # Footer text
    foot = "THIS OBJECT CANNOT EXIST IN 3D"
    foot_w = len(foot) * 6 * 2
    draw_text(foot, (WIDTH - foot_w) // 2, HEIGHT - 100, 2, (255, 80, 180), pixels, WIDTH, HEIGHT)
    
    foot2 = "...OR CAN IT?"
    foot2_w = len(foot2) * 6 * 2
    draw_text(foot2, (WIDTH - foot2_w) // 2, HEIGHT - 70, 2, (0, 230, 210), pixels, WIDTH, HEIGHT)
    
    # Agent J signature
    sig = "AGENT J LAB"
    sig_w = len(sig) * 6 * 2
    draw_text(sig, (WIDTH - sig_w) // 2, HEIGHT - 35, 2, (60, 70, 100), pixels, WIDTH, HEIGHT)
    
    # Add some decorative dots/stars in the background
    import random
    random.seed(42)
    for _ in range(200):
        sx = random.randint(0, WIDTH-1)
        sy = random.randint(0, HEIGHT-1)
        # Don't place on the triangle area
        dist_center = math.sqrt((sx - cx)**2 + (sy - cy)**2)
        if dist_center > 300 or dist_center < 100:
            brightness = random.randint(30, 80)
            pixels[sy * WIDTH + sx] = (brightness, brightness, brightness + 20)
    
    # Add neon glow/scan lines
    for y in range(HEIGHT):
        if y % 4 == 0:
            for x in range(WIDTH):
                r, g, b = pixels[y * WIDTH + x]
                pixels[y * WIDTH + x] = (max(0, r - 8), max(0, g - 8), max(0, b - 8))
    
    # Add radial vignette
    for y in range(HEIGHT):
        for x in range(WIDTH):
            dist = math.sqrt((x - cx)**2 + (y - cy)**2)
            vignette = max(0, 1 - (dist / 500) ** 2)
            vignette = 0.3 + 0.7 * vignette
            r, g, b = pixels[y * WIDTH + x]
            pixels[y * WIDTH + x] = (int(r * vignette), int(g * vignette), int(b * vignette))
    
    return pixels

print("🔬 Generating Penrose Triangle...")
pixels = draw_penrose()
print("📸 Encoding PNG...")
png_data = make_png(WIDTH, HEIGHT, pixels)
output_path = "/Users/jianjun/.openclaw/workspace/agent-j/lab/penrose-paradox.png"
with open(output_path, 'wb') as f:
    f.write(png_data)
print(f"✅ Saved to {output_path} ({len(png_data) // 1024}KB)")
