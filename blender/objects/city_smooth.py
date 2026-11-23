"""
Smooth neon-night city buildings (style: soft rounded futuristic architecture,
kept in the cyberpunk night palette). No hard blocks: rounded-rectangle
floor plates, wrap-around curved balconies with glass railings and neon
edges, a round glass stair tower, a rooftop garden with a glass pavilion.

    build_smooth_tower(parent=None, name="SmoothTower", floors=9, w=20, d=14,
                       accent="#22e4ff", seed=1)
        origin on the ground at the centre of the plan; the main face looks +Z.
    build_smooth_tower_preview(parent, name) -> tower + fill lights

Coordinates are three.js style (Y up).
"""

import math
import os
import random
import sys

import bmesh
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P, _hex  # noqa: E402
from loft_room import mat  # noqa: E402
from glass_room import glass_mat  # noqa: E402

FLOOR_H = 3.4
WIN_COLS, WIN_ROWS = 8, 8
TILE_U, TILE_V = WIN_COLS * 1.7, WIN_ROWS * FLOOR_H  # metres per texture tile


# ---------------------------------------------------------------- textures
def _window_image(seed=1, sparse=0.0):
    """sparse = share of cells that are solid wall panels instead of windows."""
    name = f"SmoothWindows{seed}_{int(sparse * 100)}"
    img = bpy.data.images.get(name)
    if img:
        return img
    S = 32  # pixels per window cell
    W, H = WIN_COLS * S, WIN_ROWS * S
    rng = random.Random(seed)
    img = bpy.data.images.new(name, W, H)
    px = [0.0] * (W * H * 4)
    warm, cool, pink = _hex("#ffdcae"), _hex("#b4ecff"), _hex("#ff9ee0")
    for row in range(WIN_ROWS):
        for col in range(WIN_COLS):
            if rng.random() < sparse:
                # solid cladding panel: mid-dark, a seam line and a faint vent slot
                for y in range(S):
                    for x in range(S):
                        c = (0.055, 0.058, 0.08)
                        if y < 2 or x < 1:
                            c = (0.02, 0.02, 0.03)
                        elif 14 < y < 17 and 6 < x < S - 6:
                            c = (0.035, 0.036, 0.05)
                        i = ((row * S + y) * W + col * S + x) * 4
                        px[i:i + 4] = (*c, 1.0)
                continue
            roll = rng.random()
            if roll < 0.42:
                lit = warm
                k = rng.uniform(0.7, 1.0)
            elif roll < 0.62:
                lit = cool
                k = rng.uniform(0.6, 0.95)
            elif roll < 0.67:
                lit = pink
                k = 0.8
            else:
                lit = (0.03, 0.035, 0.06)  # dark glass
                k = 1.0
            blind = rng.random() < 0.3  # half-drawn blind
            for y in range(S):
                for x in range(S):
                    # frame: slab band at the bottom, thin mullions
                    if y < 7 or x < 2 or x >= S - 2 or y >= S - 2:
                        c = (0.012, 0.012, 0.018)
                    elif x in (S // 2, S // 2 - 1):
                        c = (0.02, 0.02, 0.03)
                    else:
                        g = 0.75 + 0.25 * (y - 7) / (S - 9)  # soft gradient up the pane
                        c = tuple(v * k * g for v in lit)
                        if blind and y > S * 0.62:
                            c = tuple(v * 0.35 for v in c)
                    i = ((row * S + y) * W + col * S + x) * 4
                    px[i:i + 4] = (*c, 1.0)
    img.pixels = px
    img.pack()
    return img


def window_mat(seed=1, sparse=0.0):
    key = f"Smooth_Windows{seed}_{int(sparse * 100)}"
    m = bpy.data.materials.get(key)
    if m:
        return m
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = _window_image(seed, sparse)
    nt.links.new(tex.outputs["Color"], b.inputs["Emission Color"])
    if sparse:
        nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])  # cladding shows its colour
    b.inputs["Emission Strength"].default_value = 1.6
    b.inputs["Base Color"].default_value = (0.02, 0.02, 0.03, 1)
    b.inputs["Roughness"].default_value = 0.12
    b.inputs["Metallic"].default_value = 0.4
    return m


def _mats(accent):
    return {
        "shell": mat("SmoothShell", "#2a2b36", 0.45, metal=0.15),
        "shellLight": mat("SmoothShellLight", "#3a3b4a", 0.4, metal=0.1),
        "slab": mat("SmoothSlab", "#1b1c24", 0.5),
        "rail": glass_mat("SmoothRail", "#9fb4e0", 0.28),
        "railTop": mat("SmoothRailTop", "#8a90a0", 0.3, metal=0.9),
        "frame": mat("SmoothFrame", "#14151b", 0.35, metal=0.6),
        "lobbyGlass": glass_mat("SmoothLobby", "#6a7fb8", 0.22),
        "glass": mat("SmoothGlass", "#0c1630", 0.05, metal=0.6, emit="#1a3a7a", strength=0.6),
        "accent": mat(f"SmoothNeon{accent[1:]}", accent, emit=accent, strength=9.0),
        "warm": mat("SmoothWarm", "#ffcf8a", emit="#ff9e48", strength=1.4),
        "leaf": mat("SmoothLeaf", "#1c4a34", 0.7),
        "leafNeon": mat("SmoothLeafGlow", "#2a6a4a", 0.6, emit="#1e8a5a", strength=0.6),
        "trunk": mat("SmoothTrunk", "#2a1d18", 0.8),
        "soil": mat("SmoothPlanter", "#24252e", 0.6),
    }


# ---------------------------------------------------------------- geometry
def _rounded_ring(w, d, r, seg):
    """Points round a rounded rectangle (x, z), counter-clockwise, plus the arc length at each."""
    r = min(r, w / 2 - 0.01, d / 2 - 0.01)
    pts = []
    for cx, cz, a0 in ((w / 2 - r, d / 2 - r, 0), (-w / 2 + r, d / 2 - r, 90), (-w / 2 + r, -d / 2 + r, 180), (w / 2 - r, -d / 2 + r, 270)):
        for k in range(seg + 1):
            a = math.radians(a0 + 90 * k / seg)
            pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    s, acc = [0.0], 0.0
    for i in range(1, len(pts) + 1):
        acc += math.dist(pts[i - 1], pts[i % len(pts)])
        s.append(acc)
    return pts, s


def rounded_prism(name, c, w, d, r, h, m, parent, seg=10, cap_m=None, uv_scale=None, open_ends=False):
    """Vertical prism with a rounded-rectangle plan, smooth sides, flat caps.
    uv_scale=(tu, tv): side UVs run along the perimeter in metres / tu, height / tv."""
    cx, cy, cz = c
    pts, s = _rounded_ring(w, d, r, seg)
    n = len(pts)
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new()
    bot = [bm.verts.new(P(cx + x, cy, cz + z)) for x, z in pts]
    top = [bm.verts.new(P(cx + x, cy + h, cz + z)) for x, z in pts]
    tu, tv = uv_scale or (1.0, 1.0)
    for i in range(n):
        j = (i + 1) % n
        f = bm.faces.new((bot[i], bot[j], top[j], top[i]))
        f.smooth = True
        f.material_index = 0
        u0, u1 = s[i] / tu, s[i + 1] / tu
        for loop, (u, v) in zip(f.loops, ((u0, cy / tv), (u1, cy / tv), (u1, (cy + h) / tv), (u0, (cy + h) / tv))):
            loop[uv].uv = (u, v)
    if not open_ends:
        # caps on their own verts so the smooth sides keep clean normals
        for y, rev in ((cy, True), (cy + h, False)):
            ring = [bm.verts.new(P(cx + x, y, cz + z)) for x, z in pts]
            f = bm.faces.new(list(reversed(ring)) if rev else ring)
            f.material_index = 1 if cap_m else 0
            for loop in f.loops:
                loop[uv].uv = (0.001, 0.001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    me.materials.append(m)
    if cap_m:
        me.materials.append(cap_m)
    o.parent = parent
    return o


def rounded_band(name, c, w, d, r, h, m, parent, seg=10):
    """Thin open ring (railing glass / neon strip) round a rounded rectangle."""
    return rounded_prism(name, c, w, d, r, h, m, parent, seg, open_ends=True)


def _tree(name, c, s, M, parent, rng):
    x, y, z = c
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12 * s, depth=1.6 * s, vertices=8, location=P(x, y + 0.8 * s, z))
    t = bpy.context.active_object
    t.name = f"{name}Trunk"
    t.data.materials.append(M["trunk"])
    t.parent = parent
    for k in range(4):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=rng.uniform(0.6, 0.9) * s,
                                              location=P(x + rng.uniform(-0.5, 0.5) * s, y + (1.8 + rng.uniform(0, 0.8)) * s, z + rng.uniform(-0.5, 0.5) * s))
        b = bpy.context.active_object
        b.name = f"{name}Crown{k}"
        bpy.ops.object.shade_smooth()
        b.data.materials.append(M["leafNeon" if k == 0 else "leaf"])
        b.parent = parent


# ---------------------------------------------------------------- building
def build_smooth_tower(parent=None, name="SmoothTower", floors=9, w=20.0, d=14.0, accent="#22e4ff", seed=1):
    M = _mats(accent)
    rng = random.Random(seed)
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    WM = window_mat(seed)
    R = 3.2  # corner radius of the floor plates
    top_y = floors * FLOOR_H

    # lobby: recessed glowing glass base, deep canopy slab with neon edge
    rounded_prism(f"{name}LobbyGlass", (0, 0, 0), w - 2.0, d - 2.0, R - 1, 4.2, M["lobbyGlass"], root, open_ends=True)
    for k, x in enumerate((-w / 2 + 3, -2.5, 2.5, w / 2 - 3)):
        rounded_prism(f"{name}Column{k}", (x, 0, d / 2 - 1.3), 0.7, 0.7, 0.34, 4.2, M["frame"], root, seg=6)
    rounded_prism(f"{name}Canopy", (0, 4.2, 0.6), w + 1.6, d + 2.6, R + 0.8, 0.45, M["slab"], root, cap_m=M["slab"])
    rounded_band(f"{name}CanopyNeon", (0, 4.25, 0.6), w + 1.65, d + 2.65, R + 0.82, 0.08, M["accent"], root)
    rounded_prism(f"{name}LobbyWarm", (0, 0.2, 0), w - 2.4, d - 2.4, R - 1.2, 3.6, M["warm"], root, open_ends=True)

    # tower core with the window texture, wrapped by curved balcony plates
    core_w, core_d = w - 1.6, d - 1.6
    rounded_prism(f"{name}Core", (0, 4.65, 0), core_w, core_d, R - 0.8, top_y - 4.65, WM, root,
                  cap_m=M["slab"], uv_scale=(TILE_U, TILE_V))
    for f in range(2, floors + 1):
        y = f * FLOOR_H - 0.3
        deep = f % 3 == 0  # every third floor the balcony steps further out
        bw, bd = (w + 1.2, d + 1.2) if deep else (w, d)
        br = R + (0.6 if deep else 0)
        rounded_prism(f"{name}Plate{f}", (0, y, 0), bw, bd, br, 0.32, M["shellLight" if deep else "shell"], root, cap_m=M["slab"])
        rounded_band(f"{name}Rail{f}", (0, y + 0.32, 0), bw - 0.05, bd - 0.05, br - 0.03, 0.95, M["rail"], root)
        rounded_band(f"{name}RailTop{f}", (0, y + 1.25, 0), bw - 0.04, bd - 0.04, br - 0.02, 0.06, M["railTop"], root)
        if deep or f == floors:
            rounded_band(f"{name}PlateNeon{f}", (0, y - 0.02, 0), bw + 0.02, bd + 0.02, br + 0.01, 0.06, M["accent"], root)

    # round glass stair tower on the right-hand corner
    sx, sz = w / 2 - 1.0, -d / 2 + 2.5
    rounded_prism(f"{name}Stair", (sx, 0, sz), 4.6, 4.6, 2.3, top_y + 3.0, M["glass"], root, seg=12, cap_m=M["slab"])
    for k in range(int((top_y + 3.0) / 1.7)):
        rounded_band(f"{name}StairRib{k}", (sx, 0.8 + k * 1.7, sz), 4.65, 4.65, 2.32, 0.12, M["frame"], root, seg=12)
    rounded_band(f"{name}StairNeon", (sx, top_y + 2.7, sz), 4.7, 4.7, 2.35, 0.15, M["accent"], root, seg=12)
    rounded_prism(f"{name}StairCap", (sx, top_y + 3.0, sz), 5.0, 5.0, 2.5, 0.4, M["shell"], root, seg=12, cap_m=M["slab"])

    # vertical neon ribbon up the left corner
    rounded_prism(f"{name}Ribbon", (-w / 2 + 0.4, 5.0, d / 2 - R + 0.4), 0.18, 0.18, 0.08, top_y - 6.0, M["accent"], root, seg=3)

    # rooftop: parapet, planters with trees, glass pavilion with a pitched glass roof
    rounded_prism(f"{name}Roof", (0, top_y, 0), w, d, R, 0.5, M["shell"], root, cap_m=M["slab"])
    rounded_band(f"{name}RoofRail", (0, top_y + 0.5, 0), w - 0.05, d - 0.05, R - 0.03, 1.1, M["rail"], root)
    py = top_y + 0.5
    rounded_prism(f"{name}Pavilion", (-2.5, py, -1.0), 7.0, 5.0, 0.6, 2.8, M["glass"], root, seg=4, cap_m=M["frame"])
    rounded_prism(f"{name}PavilionWarm", (-2.5, py + 0.1, -1.0), 6.4, 4.4, 0.4, 2.2, M["warm"], root, seg=4, open_ends=True)
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=4.2, radius2=0.6, depth=1.4, location=P(-2.5, py + 3.5, -1.0))
    roof = bpy.context.active_object
    roof.name = f"{name}PavilionRoof"
    roof.rotation_euler = (0, 0, math.radians(45))
    roof.scale = (1.0, 0.72, 1.0)
    roof.data.materials.append(M["glass"])
    roof.parent = root
    rounded_band(f"{name}PavilionNeon", (-2.5, py + 2.8, -1.0), 7.05, 5.05, 0.62, 0.1, M["accent"], root, seg=4)
    for k, (x, z) in enumerate(((4.5, 3.0), (6.5, -2.5), (-8.0, 3.5), (2.0, 4.2))):
        rounded_prism(f"{name}Planter{k}", (x, py, z), 2.2, 2.2, 1.0, 0.7, M["soil"], root, seg=6, cap_m=M["leaf"])
        _tree(f"{name}Tree{k}", (x, py + 0.7, z), rng.uniform(0.9, 1.3), M, root, rng)
    return root


def build_smooth_tower_preview(parent=None, name="SmoothTowerPreview"):
    root = build_smooth_tower(parent, name)

    def pl(n, pos, color, energy, size=3.0):
        ld = bpy.data.lights.new(n, "POINT")
        ld.color = color
        ld.energy = energy
        ld.shadow_soft_size = size
        ld.specular_factor = 0.0
        lo = bpy.data.objects.new(n, ld)
        bpy.context.collection.objects.link(lo)
        lo.location = P(*pos)

    pl("Street", (0, 6, 14), (1.0, 0.6, 0.9), 9000)
    pl("Left", (-18, 18, 10), (0.4, 0.6, 1.0), 14000, 6)
    pl("Right", (18, 26, 8), (0.9, 0.4, 1.0), 14000, 6)
    pl("Top", (0, 40, 6), (0.7, 0.6, 1.0), 9000, 6)
    return root


# ---------------------------------------------------------------- ad boards
def _ad_image(kind, seed=0):
    """Original pixel-art adverts: screen (wide), banner (tall glyphs), ticker (thin strip), roof (letters)."""
    name = f"SmoothAd_{kind}{seed}"
    img = bpy.data.images.get(name)
    if img:
        return img
    rng = random.Random(seed * 31 + len(kind))
    W, H = {"screen": (192, 108), "banner": (48, 192), "ticker": (256, 24), "roof": (160, 40), "product": (240, 100)}[kind]
    img = bpy.data.images.new(name, W, H)
    px = [[(0.0, 0.0, 0.0)] * W for _ in range(H)]

    def rect(x0, y0, x1, y1, c):
        for y in range(max(0, y0), min(H, y1)):
            for x in range(max(0, x0), min(W, x1)):
                px[y][x] = c

    pink, cyan, yel, white = (1.0, 0.25, 0.8), (0.2, 0.9, 1.0), (1.0, 0.82, 0.2), (0.95, 0.95, 1.0)
    if kind == "screen":
        for y in range(H):
            for x in range(W):
                v = y / H
                px[y][x] = (0.12 + 0.2 * v, 0.03, 0.3 + 0.25 * (1 - v)) if y % 3 else (0.08, 0.02, 0.2)
        for y in range(H):  # face profile
            for x in range(W):
                dx, dy = (x - 52) / 30, (y - 62) / 34
                if dx * dx + dy * dy < 1 and not (x > 70 and 40 < y < 55):
                    px[y][x] = (0.9, 0.25, 0.75) if (x + y) % 7 else (1.0, 0.5, 0.9)
        rect(40, 8, 62, 30, (0.9, 0.25, 0.75))
        rect(60, 64, 66, 70, cyan)
        rect(100, 70, 180, 84, cyan)
        rect(100, 52, 160, 60, yel)
        rect(100, 40, 172, 46, white)
        rect(100, 30, 140, 36, white)
        rect(100, 12, 136, 22, pink)
    elif kind == "banner":
        for y in range(H):
            for x in range(W):
                px[y][x] = (0.45, 0.02, 0.12) if (x // 2 + y // 2) % 2 else (0.38, 0.02, 0.1)
        rect(0, 0, W, 3, yel)
        rect(0, H - 3, W, H, yel)
        for g in range(4):  # four original block glyphs
            gy = H - 14 - g * 44
            col = white if g % 2 == 0 else yel
            for _ in range(5):
                if rng.random() < 0.5:
                    y0 = gy - rng.randint(0, 30)
                    rect(8, y0, 40, y0 + 4, col)
                else:
                    x0 = rng.randint(8, 34)
                    rect(x0, gy - 32, x0 + 4, gy, col)
    elif kind == "ticker":
        x = 0
        while x < W:
            c = rng.choice((pink, cyan, yel, white))
            for _ in range(rng.randint(3, 6)):  # one word of glyph blocks
                rect(x, 6, x + 4, 18, c)
                if rng.random() < 0.5:
                    rect(x + 4, 6 if rng.random() < 0.5 else 15, x + 7, 9 if rng.random() < 0.5 else 18, c)
                x += 9
            x += 14
            rect(x - 9, 11, x - 6, 14, (0.6, 0.6, 0.7))
    elif kind == "product":
        for y in range(H):
            for x in range(W):
                v = y / H
                px[y][x] = (0.02 + 0.08 * v, 0.12 + 0.25 * v, 0.2 + 0.2 * v)  # teal night gradient
        for y in range(H):  # radial glow behind the can
            for x in range(W):
                dd = ((x - 60) / 50) ** 2 + ((y - 50) / 45) ** 2
                if dd < 1:
                    r0, g0, b0 = px[y][x]
                    k = (1 - dd) * 0.8
                    px[y][x] = (r0 + k, g0 + k * 0.6, b0 + k * 0.1)
        rect(44, 14, 76, 86, (0.9, 0.15, 0.2))  # can body
        rect(46, 86, 74, 90, (0.75, 0.75, 0.8))  # lid
        rect(44, 44, 76, 56, (0.98, 0.95, 0.9))  # label band
        rect(50, 47, 70, 53, (0.9, 0.15, 0.2))
        rect(110, 62, 220, 76, yel)  # headline
        rect(110, 44, 200, 52, white)
        rect(110, 32, 180, 38, white)
        rect(110, 14, 150, 24, cyan)
    elif kind == "roof":
        for y in range(H):
            for x in range(W):
                px[y][x] = (0.02, 0.03, 0.08)
        x = 10
        for k in range(6):  # big chunky letters
            c = cyan if k % 2 == 0 else pink
            rect(x, 8, x + 6, 32, c)
            rect(x, 26, x + 18, 32, c)
            if k % 3 != 1:
                rect(x, 8, x + 18, 14, c)
            if k % 2:
                rect(x + 12, 8, x + 18, 32, c)
            x += 25
    flat = []
    for row in px:
        for c in row:
            flat.extend((*c, 1.0))
    img.pixels = flat
    img.pack()
    return img


def ad_mat(kind, seed=0, strength=2.2):
    key = f"Smooth_Ad_{kind}{seed}"
    m = bpy.data.materials.get(key)
    if m:
        return m
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = _ad_image(kind, seed)
    tex.interpolation = "Closest"  # crisp LED pixels
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(tex.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = strength
    b.inputs["Roughness"].default_value = 0.3
    return m


def _screen_plane(name, c, w, h, m, parent, back=False):
    bpy.ops.mesh.primitive_plane_add(size=1)
    o = bpy.context.active_object
    o.name = name
    o.scale = (w, h, 1)
    o.rotation_euler = (math.pi / 2, 0, math.pi if back else 0)
    o.location = P(*c)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    o.data.materials.append(m)
    o.parent = parent
    return o


def ad_board(name, c, w, h, kind, M, parent, seed=0, arm=0.8, double=False):
    """Framed LED advert facing +Z, centred at c, held off the wall behind it by arms."""
    x, y, z = c
    rounded_prism(f"{name}Frame", (x, y - h / 2 - 0.2, z - 0.25), w + 0.4, 0.4, 0.15, h + 0.4, M["frame"], parent, seg=2, cap_m=M["frame"])
    _screen_plane(f"{name}Screen", (x, y, z - 0.04), w, h, ad_mat(kind, seed), parent)
    if double:
        _screen_plane(f"{name}ScreenBack", (x, y, z - 0.46), w, h, ad_mat(kind, seed + 1), parent, back=True)
    rounded_band(f"{name}Edge", (x, y - h / 2 - 0.22, z - 0.25), w + 0.44, 0.44, 0.16, 0.08, M["accent"], parent, seg=2)
    rounded_band(f"{name}EdgeTop", (x, y + h / 2 + 0.14, z - 0.25), w + 0.44, 0.44, 0.16, 0.08, M["accent"], parent, seg=2)
    if arm > 0:
        for k, dx in enumerate((-w / 3, w / 3)):
            rounded_prism(f"{name}Arm{k}", (x + dx, y - 0.15, z - 0.45 - arm / 2), 0.2, arm, 0.05, 0.3, M["frame"], parent, seg=2)
            rounded_prism(f"{name}ArmB{k}", (x + dx, y + h / 3, z - 0.45 - arm / 2), 0.2, arm, 0.05, 0.3, M["frame"], parent, seg=2)


# ---------------------------------------------------------------- variant 2
def build_smooth_slim(parent=None, name="SmoothSlim", accent="#ff4fd8", seed=2):
    """Slim stadium-plan tower on a wide rounded podium. The shaft steps back
    twice with terraces, a glowing vertical spine runs up the front and a
    halo ring crowns the top."""
    M = _mats(accent)
    rng = random.Random(seed)
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    WM = window_mat(seed, sparse=0.7)

    # podium: two storeys, wide and low, glass shopfront + canopy + sign
    PW, PD, PH = 24.0, 16.0, 7.0
    rounded_prism(f"{name}PodGlass", (0, 0, 0.5), PW - 1.5, PD - 1.5, 3.5, 3.8, M["lobbyGlass"], root, open_ends=True)
    rounded_prism(f"{name}PodWarm", (0, 0.2, 0.5), PW - 2.0, PD - 2.0, 3.2, 3.4, M["warm"], root, open_ends=True)
    rounded_prism(f"{name}PodUpper", (0, 3.8, 0), PW, PD, 4.0, PH - 3.8, M["shell"], root, cap_m=M["slab"])
    rounded_band(f"{name}PodNeon", (0, 3.75, 0), PW + 0.05, PD + 0.05, 4.02, 0.12, M["accent"], root)
    rounded_prism(f"{name}PodTicker", (0, 4.6, 0), PW + 0.06, PD + 0.06, 4.03, 1.5, ad_mat("ticker", seed, 2.6), root, open_ends=True, uv_scale=(PW * 0.75, 1.5))
    rounded_band(f"{name}PodRail", (0, PH, 0), PW - 0.05, PD - 0.05, 3.97, 1.0, M["rail"], root)
    for k, (x, z) in enumerate(((-8.5, 5.0), (8.5, 4.5), (-9.0, -4.5))):
        rounded_prism(f"{name}PodPlanter{k}", (x, PH, z), 2.0, 2.0, 1.0, 0.6, M["soil"], root, seg=6, cap_m=M["leaf"])
        _tree(f"{name}PodTree{k}", (x, PH + 0.6, z), rng.uniform(0.8, 1.1), M, root, rng)

    # shaft: stadium plan (fully round ends), three tiers stepping back
    tiers = [(15.0, 10.0, 5), (13.0, 8.6, 5), (11.0, 7.2, 4)]  # w, d, floors
    y = PH
    for t, (w, d, n) in enumerate(tiers):
        h = n * FLOOR_H
        r = d / 2 - 0.05
        rounded_prism(f"{name}Shaft{t}", (0, y, 0), w, d, r, h, WM, root, seg=14, cap_m=M["slab"], uv_scale=(TILE_U, TILE_V))
        for f in range(1, n + 1):
            fy = y + f * FLOOR_H - 0.25
            rounded_prism(f"{name}Fin{t}_{f}", (0, fy, 0), w + 0.5, d + 0.5, r + 0.25, 0.22, M["shell"], root, seg=14, cap_m=M["slab"])
        # terrace on top of each tier, glass rail, neon lip
        rounded_prism(f"{name}Terrace{t}", (0, y + h, 0), w + 0.8, d + 0.8, r + 0.4, 0.35, M["shellLight"], root, seg=14, cap_m=M["slab"])
        rounded_band(f"{name}TerraceNeon{t}", (0, y + h - 0.02, 0), w + 0.85, d + 0.85, r + 0.42, 0.08, M["accent"], root, seg=14)
        rounded_band(f"{name}TerraceRail{t}", (0, y + h + 0.35, 0), w + 0.75, d + 0.75, r + 0.37, 1.0, M["rail"], root, seg=14)
        y += h + 0.35

    # glowing spine up the front of the shaft
    rounded_prism(f"{name}Spine", (3.2, PH + 0.5, tiers[0][1] / 2 - 0.2), 0.9, 0.6, 0.15, 5 * FLOOR_H - 1.0, M["frame"], root, seg=3)
    rounded_prism(f"{name}SpineGlow", (3.2, PH + 0.8, tiers[0][1] / 2 + 0.12), 0.35, 0.1, 0.04, 5 * FLOOR_H - 1.6, M["accent"], root, seg=2)

    # adverts: big LED screen on the middle tier, a tall glyph banner blade off
    # the left end of the bottom tier, a smaller screen on the top tier
    t1y = PH + 5 * FLOOR_H + 0.35
    ad_board(f"{name}BigScreen", (0, t1y + 8.0, tiers[1][1] / 2 + 1.3), 10.5, 6.2, "screen", M, root, seed)
    ad_board(f"{name}Banner", (-tiers[0][0] / 2 - 1.2, PH + 9.0, 1.2), 2.6, 10.5, "banner", M, root, seed, arm=0, double=True)
    rounded_prism(f"{name}BannerArm0", (-tiers[0][0] / 2 + 0.2, PH + 13.6, 1.0), 3.0, 0.25, 0.08, 0.25, M["frame"], root, seg=2)
    rounded_prism(f"{name}BannerArm1", (-tiers[0][0] / 2 + 0.2, PH + 4.2, 1.0), 3.0, 0.25, 0.08, 0.25, M["frame"], root, seg=2)
    t2y = t1y + 5 * FLOOR_H + 0.35
    ad_board(f"{name}TopScreen", (0, t2y + 6.6, tiers[2][1] / 2 + 1.0), 6.0, 3.4, "screen", M, root, seed + 5)

    # crown: halo ring on slim posts, small penthouse, antenna with beacon
    top = y
    rounded_prism(f"{name}Penthouse", (0, top, -0.6), 7.0, 4.6, 2.2, 2.6, M["lobbyGlass"], root, seg=10, cap_m=M["shell"])
    rounded_prism(f"{name}PenthouseWarm", (0, top + 0.1, -0.6), 6.4, 4.0, 1.9, 2.2, M["warm"], root, seg=10, open_ends=True)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        rounded_prism(f"{name}HaloPost{k}", (4.6 * math.cos(a), top, 2.9 * math.sin(a)), 0.2, 0.2, 0.09, 4.0, M["frame"], root, seg=3)
    rounded_band(f"{name}Halo", (0, top + 4.0, 0), 11.6, 7.6, 3.75, 0.25, M["accent"], root, seg=14)
    ad_board(f"{name}RoofSign", (0, top + 2.0, 3.0), 8.0, 2.0, "roof", M, root, seed, arm=0)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=6.0, vertices=8, location=P(0, top + 5.6, -0.6))
    ant = bpy.context.active_object
    ant.name = f"{name}Antenna"
    ant.data.materials.append(M["frame"])
    ant.parent = root
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, segments=12, ring_count=8, location=P(0, top + 8.7, -0.6))
    bc = bpy.context.active_object
    bc.name = f"{name}Beacon"
    bc.data.materials.append(mat("SmoothBeacon", "#ff2020", emit="#ff2020", strength=14.0))
    bc.parent = root
    return root


def build_smooth_slim_preview(parent=None, name="SmoothSlimPreview"):
    root = build_smooth_slim(parent, name)
    for n, pos, col, e, sz in (("Street", (0, 6, 16), (1.0, 0.6, 0.9), 9000, 3), ("Left", (-20, 24, 12), (0.4, 0.6, 1.0), 16000, 6),
                               ("Right", (20, 34, 10), (0.9, 0.4, 1.0), 16000, 6), ("Top", (0, 60, 8), (0.7, 0.6, 1.0), 9000, 6)):
        ld = bpy.data.lights.new(n, "POINT")
        ld.color = col
        ld.energy = e
        ld.shadow_soft_size = sz
        ld.specular_factor = 0.0
        lo = bpy.data.objects.new(n, ld)
        bpy.context.collection.objects.link(lo)
        lo.location = P(*pos)
    return root


# ---------------------------------------------------------------- variant 3
def build_smooth_terrace(parent=None, name="SmoothTerrace", accent="#ffb82e", seed=3):
    """Wide stepped block: rounded levels that step back toward the rear so
    every level has a planted terrace facing the street. Mostly solid
    cladding, a wide product billboard on a rooftop scaffold, two red banner
    blades on the right end, a ticker round the base."""
    M = _mats(accent)
    rng = random.Random(seed)
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    WM = window_mat(seed, sparse=0.65)

    # base: shopfront + ticker band
    BW, BD = 26.0, 18.0
    rounded_prism(f"{name}BaseGlass", (0, 0, 0.6), BW - 1.6, BD - 1.6, 3.2, 3.8, M["lobbyGlass"], root, open_ends=True)
    rounded_prism(f"{name}BaseWarm", (0, 0.2, 0.6), BW - 2.0, BD - 2.0, 3.0, 3.4, M["warm"], root, open_ends=True)
    rounded_prism(f"{name}BaseUpper", (0, 3.8, 0), BW, BD, 3.6, 3.2, M["shell"], root, cap_m=M["slab"])
    rounded_band(f"{name}BaseNeon", (0, 3.75, 0), BW + 0.05, BD + 0.05, 3.62, 0.12, M["accent"], root)
    rounded_prism(f"{name}BaseTicker", (0, 4.6, 0), BW + 0.06, BD + 0.06, 3.63, 1.4, ad_mat("ticker", seed, 2.6), root,
                  open_ends=True, uv_scale=(BW * 0.75, 1.4))

    # stepped levels, each two storeys, pulled back toward the rear
    y = 7.0
    w, d, zc = BW - 1.0, BD - 1.0, 0.0
    levels = 4
    for k in range(levels):
        h = 2 * FLOOR_H
        r = 3.2 - k * 0.3
        rounded_prism(f"{name}Level{k}", (0, y, zc), w, d, r, h, WM, root, cap_m=M["slab"], uv_scale=(TILE_U, TILE_V))
        rounded_prism(f"{name}LevelFin{k}", (0, y + FLOOR_H - 0.2, zc), w + 0.4, d + 0.4, r + 0.2, 0.22, M["shell"], root, cap_m=M["slab"])
        y += h
        # roof of this level becomes the terrace of the next
        rounded_prism(f"{name}Terrace{k}", (0, y, zc), w + 0.6, d + 0.6, r + 0.3, 0.35, M["shellLight"], root, cap_m=M["slab"])
        rounded_band(f"{name}TerraceNeon{k}", (0, y - 0.02, zc), w + 0.65, d + 0.65, r + 0.32, 0.08, M["accent"], root)
        rounded_band(f"{name}TerraceRail{k}", (0, y + 0.35, zc), w + 0.55, d + 0.55, r + 0.28, 0.95, M["rail"], root)
        rounded_band(f"{name}TerraceRailTop{k}", (0, y + 1.3, zc), w + 0.56, d + 0.56, r + 0.28, 0.06, M["railTop"], root)
        if k < levels - 1:
            # planters along the front edge of the terrace
            nw, nd = w - 3.0, d - 2.6
            front = zc + d / 2 - 0.9
            for j, x in enumerate((-w / 2 + 2.0, w / 2 - 2.0)):
                rounded_prism(f"{name}Planter{k}_{j}", (x, y + 0.35, front), 1.8, 1.2, 0.5, 0.6, M["soil"], root, seg=4, cap_m=M["leaf"])
                _tree(f"{name}Tree{k}_{j}", (x, y + 0.95, front), rng.uniform(0.7, 1.0), M, root, rng)
            w, d, zc = nw, nd, zc - 1.3
        y += 0.35

    # rooftop: wide product billboard on a scaffold, AC units, beacon
    top = y
    ad_board(f"{name}Billboard", (0, top + 4.3, zc + 1.0), 12.0, 5.0, "product", M, root, seed, arm=0)
    for k, x in enumerate((-4.5, 0.0, 4.5)):
        rounded_prism(f"{name}BillLeg{k}", (x, top, zc + 0.6), 0.3, 0.3, 0.1, 6.8, M["frame"], root, seg=2)
    rounded_prism(f"{name}BillBrace", (0, top + 1.2, zc + 0.6), 10.0, 0.25, 0.1, 0.25, M["frame"], root, seg=2)
    for k, x in enumerate((-3.0, 3.0)):
        rounded_prism(f"{name}AC{k}", (x, top, zc - 2.5), 2.0, 1.4, 0.4, 1.1, M["shellLight"], root, seg=4, cap_m=M["frame"])
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, segments=12, ring_count=8, location=P(w / 2 - 1.0, top + 2.2, zc))
    bc = bpy.context.active_object
    bc.name = f"{name}Beacon"
    bc.data.materials.append(mat("SmoothBeacon", "#ff2020", emit="#ff2020", strength=14.0))
    bc.parent = root
    rounded_prism(f"{name}BeaconMast", (w / 2 - 1.0, top, zc), 0.12, 0.12, 0.05, 1.9, M["frame"], root, seg=2)

    # two red glyph banners as blades off the right end
    for k, (yy, s) in enumerate(((7.0 + 6.5, seed + 2), (7.0 + 6.5 + 2 * FLOOR_H + 1.0, seed + 4))):
        bx = BW / 2 - 1.0 - k * 1.6
        ad_board(f"{name}Banner{k}", (bx + 1.8, yy, 2.0 - k * 1.3), 2.2, 8.0, "banner", M, root, s, arm=0, double=True)
        for j, dy in enumerate((3.2, -3.2)):
            rounded_prism(f"{name}BannerArm{k}{j}", (bx + 0.4, yy + dy, 1.8 - k * 1.3), 2.2, 0.2, 0.06, 0.2, M["frame"], root, seg=2)
    return root


def build_smooth_terrace_preview(parent=None, name="SmoothTerracePreview"):
    root = build_smooth_terrace(parent, name)
    for n, pos, col, e, sz in (("Street", (0, 6, 18), (1.0, 0.7, 0.8), 9000, 3), ("Left", (-22, 20, 14), (0.4, 0.6, 1.0), 16000, 6),
                               ("Right", (22, 26, 12), (0.9, 0.4, 1.0), 16000, 6), ("Top", (0, 50, 10), (0.7, 0.6, 1.0), 9000, 6)):
        ld = bpy.data.lights.new(n, "POINT")
        ld.color = col
        ld.energy = e
        ld.shadow_soft_size = sz
        ld.specular_factor = 0.0
        lo = bpy.data.objects.new(n, ld)
        bpy.context.collection.objects.link(lo)
        lo.location = P(*pos)
    return root


# ---------------------------------------------------------------- variant 4
def _eye_image(seed=0):
    """Original advert art for the curved corner screen: a giant cyber eye with text bars."""
    name = f"SmoothAd_eye{seed}"
    img = bpy.data.images.get(name)
    if img:
        return img
    W, H = 256, 128
    img = bpy.data.images.new(name, W, H)
    flat = []
    for y in range(H):
        for x in range(W):
            u, v = x / W, y / H
            c = (0.05 + 0.1 * v, 0.02, 0.12 + 0.15 * v) if y % 3 else (0.03, 0.01, 0.08)
            # almond eye shape centred at u=0.38
            ex, ey = (u - 0.38) / 0.3, (v - 0.5) / 0.32
            if abs(ey) < (1 - ex * ex) * 1.0 and abs(ex) < 1:
                c = (0.92, 0.9, 1.0)
                d = math.hypot((u - 0.38) * 2.0, v - 0.5)
                if d < 0.26:
                    c = (0.1, 0.95, 0.75)  # green iris
                    if abs(d - 0.18) < 0.02:
                        c = (0.6, 1.0, 0.9)
                if d < 0.1:
                    c = (0.02, 0.02, 0.05)  # pupil
                if d < 0.035 and u < 0.37:
                    c = (1.0, 1.0, 1.0)  # highlight
            if 0.72 < u < 0.95 and 0.62 < v < 0.72:
                c = (0.1, 0.95, 0.75)
            if 0.72 < u < 0.9 and 0.45 < v < 0.52:
                c = (1.0, 0.3, 0.8)
            if 0.72 < u < 0.86 and 0.32 < v < 0.38:
                c = (0.95, 0.95, 1.0)
            flat.extend((*c, 1.0))
    img.pixels = flat
    img.pack()
    return img


def _eye_mat(seed=0):
    key = f"Smooth_Ad_eye{seed}"
    m = bpy.data.materials.get(key)
    if m:
        return m
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = _eye_image(seed)
    tex.interpolation = "Closest"
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(tex.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 2.2
    return m


def arc_surface(name, centre, radius, a0, a1, y0, h, m, parent, seg=24):
    """Curved vertical surface (plan arc from angle a0 to a1, degrees, x = cos, z = sin)
    facing outward; UVs run 0..1 across and up."""
    cx, cz = centre
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new()
    lo, hi = [], []
    for k in range(seg + 1):
        a = math.radians(a0 + (a1 - a0) * k / seg)
        x, z = cx + radius * math.cos(a), cz + radius * math.sin(a)
        lo.append(bm.verts.new(P(x, y0, z)))
        hi.append(bm.verts.new(P(x, y0 + h, z)))
    for k in range(seg):
        f = bm.faces.new((lo[k + 1], lo[k], hi[k], hi[k + 1]))
        f.smooth = True
        # u runs from a1 side to a0 side so the image reads left-to-right from outside
        u0, u1 = 1 - k / seg, 1 - (k + 1) / seg
        for loop, (u, v) in zip(f.loops, ((u1, 0), (u0, 0), (u0, 1), (u1, 1))):
            loop[uv].uv = (u, v)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    me.materials.append(m)
    o.parent = parent
    return o


def build_smooth_corner(parent=None, name="SmoothCorner", accent="#2bff9a", seed=4):
    """Soft square tower (big corner radii) with neon ring bands every three floors and a rooftop
    helipad with a lit landing ring."""
    M = _mats(accent)
    rng = random.Random(seed)
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    WM = window_mat(seed, sparse=0.72)
    W = D = 18.0
    R = 6.5
    floors = 11

    # lobby: warm glass, deep canopy, columns
    rounded_prism(f"{name}LobbyGlass", (0, 0, 0), W - 1.6, D - 1.6, R - 0.8, 4.2, M["lobbyGlass"], root, open_ends=True)
    rounded_prism(f"{name}LobbyWarm", (0, 0.2, 0), W - 2.0, D - 2.0, R - 1.0, 3.6, M["warm"], root, open_ends=True)
    rounded_prism(f"{name}Canopy", (0, 4.2, 0.4), W + 1.6, D + 1.6, R + 0.8, 0.45, M["slab"], root, cap_m=M["slab"])
    rounded_band(f"{name}CanopyNeon", (0, 4.25, 0.4), W + 1.65, D + 1.65, R + 0.82, 0.08, M["accent"], root)

    # shaft with neon ring bands
    top = 4.65 + floors * FLOOR_H
    rounded_prism(f"{name}Shaft", (0, 4.65, 0), W, D, R, top - 4.65, WM, root, cap_m=M["slab"], uv_scale=(TILE_U, TILE_V))
    for f in range(1, floors + 1):
        y = 4.65 + f * FLOOR_H - 0.2
        ring = f % 3 == 0
        rounded_prism(f"{name}Fin{f}", (0, y, 0), W + (0.8 if ring else 0.35), D + (0.8 if ring else 0.35), R + (0.4 if ring else 0.18),
                      0.24, M["shellLight" if ring else "shell"], root, cap_m=M["slab"])
        if ring:
            rounded_band(f"{name}Ring{f}", (0, y - 0.02, 0), W + 0.85, D + 0.85, R + 0.42, 0.08, M["accent"], root)

    # red glyph banner on the left side
    ad_board(f"{name}Banner", (-W / 2 - 1.3, 4.65 + 3.0 + 5.0, 2.5), 2.2, 9.0, "banner", M, root, seed + 1, arm=0, double=True)
    for j, dy in enumerate((3.8, -3.8)):
        rounded_prism(f"{name}BannerArm{j}", (-W / 2 + 0.1, 4.65 + 8.0 + dy, 2.3), 2.6, 0.2, 0.06, 0.2, M["frame"], root, seg=2)

    # roof: parapet, helipad with lit landing ring and an H, beacons
    rounded_prism(f"{name}Roof", (0, top, 0), W + 0.4, D + 0.4, R + 0.2, 0.6, M["shell"], root, cap_m=M["slab"])
    rounded_band(f"{name}RoofNeon", (0, top + 0.55, 0), W + 0.45, D + 0.45, R + 0.22, 0.08, M["accent"], root)
    pad = top + 0.6
    rounded_prism(f"{name}Pad", (0, pad, 0), 12.0, 12.0, 5.99, 0.3, M["slab"], root, seg=12, cap_m=M["shellLight"])
    rounded_band(f"{name}PadRing", (0, pad + 0.3, 0), 10.0, 10.0, 4.99, 0.06, M["accent"], root, seg=12)
    hw = mat("SmoothPadMark", "#e8f0ff", emit="#e8f0ff", strength=2.0)
    for k, (x, ww, dd) in enumerate(((-1.4, 0.5, 4.0), (1.4, 0.5, 4.0), (0.0, 2.8, 0.5))):
        rounded_prism(f"{name}PadH{k}", (x, pad + 0.3, 0), ww, dd, 0.05, 0.03, hw, root, seg=2, cap_m=hw)
    beacon = mat("SmoothBeacon", "#ff2020", emit="#ff2020", strength=14.0)
    for k, (x, z) in enumerate(((W / 2 - 1.5, D / 2 - 1.5), (-W / 2 + 1.5, -D / 2 + 1.5))):
        rounded_prism(f"{name}Mast{k}", (x, pad, z), 0.15, 0.15, 0.07, 2.5, M["frame"], root, seg=2)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.28, segments=12, ring_count=8, location=P(x, pad + 2.7, z))
        b = bpy.context.active_object
        b.name = f"{name}Beacon{k}"
        b.data.materials.append(beacon)
        b.parent = root
    rng.random()
    return root


def build_smooth_corner_preview(parent=None, name="SmoothCornerPreview"):
    root = build_smooth_corner(parent, name)
    for n, pos, col, e, sz in (("Street", (0, 6, 18), (1.0, 0.7, 0.8), 9000, 3), ("Left", (-22, 22, 14), (0.4, 0.6, 1.0), 16000, 6),
                               ("Right", (22, 28, 12), (0.9, 0.4, 1.0), 16000, 6), ("Top", (0, 55, 10), (0.7, 0.6, 1.0), 9000, 6)):
        ld = bpy.data.lights.new(n, "POINT")
        ld.color = col
        ld.energy = e
        ld.shadow_soft_size = sz
        ld.specular_factor = 0.0
        lo = bpy.data.objects.new(n, ld)
        bpy.context.collection.objects.link(lo)
        lo.location = P(*pos)
    return root
