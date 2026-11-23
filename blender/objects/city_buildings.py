"""
Cyberpunk city building kit (low-poly, made to be repeated many times by the
website with instancing). Every facade uses one shared window texture mapped
in world metres, so windows stay the same size on every building.

    build_stepped_tower(parent, name, h=140)    3 setback tiers, corner fins, antenna,
                                                magenta corner neon + cyan tier rims
    build_ring_tower(parent, name, h=160)       octagonal tower with glowing cyan ring
                                                balconies, crown and a dish
    build_billboard_tower(parent, name, h=110)  wide slab with a giant lit billboard,
                                                side ribs and rooftop AC units
    build_twin_towers(parent, name, h=150)      two slabs joined by a neon sky-bridge
    build_lowrise_block(parent, name, h=18)     low block for the district below: water
                                                tank, AC units, stair hut, rooftop sign
    build_building_kit_preview(parent, name)    all five in a row

Coordinates are three.js style (Y up, origin at the centre of the base).
"""

import math
import os
import random
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P, _hex  # noqa: E402
from gaming_desk import tube  # noqa: E402
from loft_room import block, mat  # noqa: E402

COLS, ROWS = 16, 32  # windows per texture tile
TILE_W, TILE_H = COLS * 1.6, ROWS * 3.0  # metres one texture tile covers


def _window_image():
    name = "CityWindows"
    img = bpy.data.images.get(name)
    if img:
        return img
    W = H = 512
    cw, ch = W // COLS, H // ROWS
    rng = random.Random(4)
    facade = (0.018, 0.018, 0.03, 1.0)
    px = [0.0] * (W * H * 4)
    for i in range(W * H):
        px[i * 4:i * 4 + 4] = facade
    palette = [((1.0, 0.72, 0.42), 0.58), ((0.82, 0.86, 1.0), 0.25), ((0.2, 0.9, 1.0), 0.09), ((1.0, 0.25, 0.8), 0.08)]
    for cy in range(ROWS):
        for cx in range(COLS):
            if rng.random() < 0.36:
                r = rng.random()
                acc = 0
                col = palette[0][0]
                for c, p in palette:
                    acc += p
                    if r <= acc:
                        col = c
                        break
                k = 0.45 + 0.55 * rng.random()
                c = (col[0] * k, col[1] * k, col[2] * k, 1.0)
            else:
                c = (0.006, 0.008, 0.018, 1.0)
            x0, x1 = cx * cw + int(cw * 0.2), cx * cw + int(cw * 0.8)
            y0, y1 = cy * ch + int(ch * 0.3), cy * ch + int(ch * 0.75)
            for y in range(y0, y1):
                row = y * W
                for x in range(x0, x1):
                    px[(row + x) * 4:(row + x) * 4 + 4] = c
    img = bpy.data.images.new(name, W, H)
    img.pixels = px
    img.pack()
    return img


def facade_mat():
    m = bpy.data.materials.get("City_Facade")
    if m:
        return m
    m = bpy.data.materials.new("City_Facade")
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = _window_image()
    t.interpolation = "Closest"
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(t.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 1.6
    b.inputs["Roughness"].default_value = 0.6
    return m


def _world_uv(o):
    """Map the window texture in world metres: walls get the window grid, roofs a plain facade pixel."""
    me = o.data
    if not me.uv_layers:
        me.uv_layers.new()
    uv = me.uv_layers.active.data
    mw = o.matrix_world
    for poly in me.polygons:
        n = (mw.to_3x3() @ poly.normal).normalized()
        for li in poly.loop_indices:
            co = mw @ me.vertices[me.loops[li].vertex_index].co
            if abs(n.z) > 0.7:
                uv[li].uv = (0.003, 0.003)
            else:
                h = co.x if abs(n.y) > abs(n.x) else co.y
                uv[li].uv = (h / TILE_W, co.z / TILE_H)


def part(name, c, size, parent, m=None):
    """A facade box (three.js centre + size) with world-mapped windows."""
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.active_object
    o.name = name
    o.location = P(*c)
    o.scale = (size[0], size[2], size[1])
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(m or facade_mat())
    bpy.context.view_layer.update()
    _world_uv(o)
    o.parent = parent
    return o


def _root(name, parent):
    r = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(r)
    if parent:
        r.parent = parent
    return r


def _neon(color, strength=8.0):
    return mat(f"CityNeon_{color}", color, emit=color, strength=strength)


DARK = None


def _dark():
    return mat("CityDark", "#0c0c12", 0.5, metal=0.5)


def _red_light(name, c, parent):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.7, segments=10, ring_count=6)
    o = bpy.context.active_object
    o.name = name
    o.location = P(*c)
    o.data.materials.append(mat("CityAviation", "#ff2020", emit="#ff2020", strength=10.0))
    o.parent = parent
    return o


# ------------------------------------------------------------------ the five designs

def build_stepped_tower(parent=None, name="SteppedTower", h=140):
    root = _root(name, parent)
    MAG, CYAN = _neon("#ff2bd6"), _neon("#22e4ff")
    tiers = [(30, 0.5), (22, 0.3), (14, 0.2)]
    y = 0.0
    for k, (w, frac) in enumerate(tiers):
        hk = h * frac
        part(f"{name}Tier{k}", (0, y + hk / 2, 0), (w, hk, w), root)
        block(f"{name}Rim{k}", (0, y + hk + 0.3, 0), (w + 0.6, 0.5, w + 0.6), CYAN, root)
        if k == 0:  # magenta neon up the four corners of the base
            for sx in (-1, 1):
                for sz in (-1, 1):
                    block(f"{name}CornerNeon{sx}{sz}", (sx * (w / 2 + 0.15), y + hk / 2, sz * (w / 2 + 0.15)), (0.4, hk * 0.96, 0.4), MAG, root)
        y += hk
    # crown: four corner fins + antenna with a red light
    for sx in (-1, 1):
        for sz in (-1, 1):
            block(f"{name}Fin{sx}{sz}", (sx * 6.5, y + 6, sz * 6.5), (1.0, 12, 1.0), _dark(), root)
    tube(f"{name}Antenna", [(0, y, 0), (0, y + 26, 0)], 0.35, _dark(), root)
    _red_light(f"{name}AntennaLight", (0, y + 26.5, 0), root)
    return root


def build_ring_tower(parent=None, name="RingTower", h=160):
    root = _root(name, parent)
    CYAN = _neon("#22e4ff")
    R = 12.0
    bpy.ops.mesh.primitive_cylinder_add(radius=R, depth=h, vertices=8)
    o = bpy.context.active_object
    o.name = f"{name}Shaft"
    o.location = P(0, h / 2, 0)
    o.rotation_euler = (0, 0, math.pi / 8)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    o.data.materials.append(facade_mat())
    bpy.context.view_layer.update()
    _world_uv(o)
    o.parent = root
    # glowing ring balconies every ~22 m
    for k, y in enumerate(range(22, int(h) - 8, 22)):
        bpy.ops.mesh.primitive_torus_add(major_radius=R + 0.8, minor_radius=0.35, major_segments=32, minor_segments=6)
        t = bpy.context.active_object
        t.name = f"{name}Ring{k}"
        t.location = P(0, y, 0)
        t.data.materials.append(CYAN)
        t.parent = root
    # crown: narrower drum + dish
    bpy.ops.mesh.primitive_cylinder_add(radius=R * 0.6, depth=14, vertices=8)
    cr = bpy.context.active_object
    cr.name = f"{name}Crown"
    cr.location = P(0, h + 7, 0)
    cr.data.materials.append(_dark())
    cr.parent = root
    bpy.ops.mesh.primitive_uv_sphere_add(radius=5, segments=16, ring_count=8)
    dish = bpy.context.active_object
    dish.name = f"{name}Dish"
    dish.scale = (1, 1, 0.35)
    dish.location = P(3, h + 16, 0)
    dish.rotation_euler = (0.5, 0.3, 0)
    dish.data.materials.append(mat("CityDish", "#8a8f99", 0.3, metal=0.9))
    dish.parent = root
    _red_light(f"{name}Light", (0, h + 14.5, 0), root)
    return root


def _billboard_image():
    name = "CityBillboard"
    img = bpy.data.images.get(name)
    if img:
        return img
    W, H = 256, 160
    img = bpy.data.images.new(name, W, H)
    px = [0.0] * (W * H * 4)
    mag, cyan, yel = _hex("#ff2bd6"), _hex("#22e4ff"), _hex("#ffd21a")
    for y in range(H):
        for x in range(W):
            u, v = x / (W - 1), y / (H - 1)
            r, g, b = 0.12 + 0.35 * v, 0.02, 0.25 + 0.2 * (1 - v)  # magenta-purple gradient
            d = math.hypot((u - 0.68) * 1.6, v - 0.5)
            if abs(d - 0.28) < 0.03:
                r, g, b = cyan  # neon ring
            if 0.12 < u < 0.42 and abs(v - 0.62) < 0.05:
                r, g, b = yel  # "headline" bar
            if 0.12 < u < 0.36 and abs(v - 0.42) < 0.025:
                r, g, b = mag
            if 0.12 < u < 0.3 and abs(v - 0.3) < 0.025:
                r, g, b = (0.9, 0.9, 1.0)
            px[(y * W + x) * 4:(y * W + x) * 4 + 4] = (r, g, b, 1.0)
    img.pixels = px
    img.pack()
    return img


def build_billboard_tower(parent=None, name="BillboardTower", h=110):
    root = _root(name, parent)
    W, D = 34.0, 14.0
    part(f"{name}Slab", (0, h / 2, 0), (W, h, D), root)
    # side ribs
    for s in (-1, 1):
        for k in range(3):
            block(f"{name}Rib{s}_{k}", (s * (W / 2 + 0.6), h / 2, -D / 2 + 2 + k * 5), (1.2, h, 0.8), _dark(), root)
    # giant billboard on the front face
    bw, bh = W - 6, 22.0
    by = h * 0.62
    block(f"{name}BoardFrame", (0, by, D / 2 + 0.6), (bw + 1.2, bh + 1.2, 1.0), _dark(), root)
    m = bpy.data.materials.get("City_Billboard")
    if not m:
        m = bpy.data.materials.new("City_Billboard")
        try:
            m.use_nodes = True
        except Exception:
            pass
        nt = m.node_tree
        bs = nt.nodes["Principled BSDF"]
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = _billboard_image()
        nt.links.new(t.outputs["Color"], bs.inputs["Base Color"])
        nt.links.new(t.outputs["Color"], bs.inputs["Emission Color"])
        bs.inputs["Emission Strength"].default_value = 2.5
    bpy.ops.mesh.primitive_plane_add(size=1)
    bd = bpy.context.active_object
    bd.name = f"{name}Board"
    bd.scale = (bw, bh, 1)
    bd.location = P(0, by, D / 2 + 1.15)
    bd.rotation_euler = (math.pi / 2, 0, 0)
    bd.data.materials.append(m)
    bd.parent = root
    # rooftop AC units
    for k in range(4):
        block(f"{name}AC{k}", (-W / 2 + 5 + k * 7, h + 1.2, -2), (4, 2.4, 4), mat("CityAC", "#2a2c31", 0.5, metal=0.6), root)
    _red_light(f"{name}Light", (W / 2 - 2, h + 1, D / 2 - 2), root)
    return root


def build_twin_towers(parent=None, name="TwinTowers", h=150):
    root = _root(name, parent)
    MAG, CYAN = _neon("#ff2bd6"), _neon("#9a5bff")
    for s, hh in ((-1, h), (1, h * 0.86)):
        part(f"{name}Tower{s}", (s * 15, hh / 2, 0), (16, hh, 16), root)
        block(f"{name}TopRim{s}", (s * 15, hh + 0.3, 0), (16.6, 0.5, 16.6), CYAN, root)
        tube(f"{name}Mast{s}", [(s * 15, hh, 0), (s * 15, hh + 12, 0)], 0.3, _dark(), root)
        _red_light(f"{name}Light{s}", (s * 15, hh + 12.5, 0), root)
    # sky-bridge with a neon underside
    yb = h * 0.62
    part(f"{name}Bridge", (0, yb, 0), (14, 6, 9), root)
    block(f"{name}BridgeNeon", (0, yb - 3.2, 0), (14, 0.4, 7), MAG, root)
    return root


def build_lowrise_block(parent=None, name="LowRise", h=18, seed=3):
    rng = random.Random(seed)
    root = _root(name, parent)
    W, D = 26.0, 20.0
    part(f"{name}Block", (0, h / 2, 0), (W, h, D), root)
    block(f"{name}Parapet", (0, h + 0.5, 0), (W + 0.4, 1.0, D + 0.4), _dark(), root)
    roof = mat("CityRoof", "#15151b", 0.8)
    block(f"{name}Roof", (0, h + 0.05, 0), (W - 0.6, 0.1, D - 0.6), roof, root)
    # water tank on legs
    for sx in (-1, 1):
        for sz in (-1, 1):
            tube(f"{name}TankLeg{sx}{sz}", [(6 + sx * 1.6, h, -4 + sz * 1.6), (6 + sx * 1.6, h + 3.5, -4 + sz * 1.6)], 0.15, _dark(), root)
    bpy.ops.mesh.primitive_cylinder_add(radius=2.4, depth=4, vertices=16)
    tk = bpy.context.active_object
    tk.name = f"{name}Tank"
    tk.location = P(6, h + 5.5, -4)
    tk.data.materials.append(mat("CityTank", "#3a2a22", 0.8))
    tk.parent = root
    # AC units + stair hut
    for k in range(rng.randint(3, 5)):
        block(f"{name}AC{k}", (-9 + k * 3.6, h + 1.0, 5 + rng.uniform(-1, 1)), (2.6, 2.0, 2.6), mat("CityAC", "#2a2c31", 0.5, metal=0.6), root)
    block(f"{name}StairHut", (-8, h + 2.0, -5), (5, 4, 4), roof, root)
    # small rooftop neon sign frame
    col = rng.choice(["#ff2bd6", "#22e4ff", "#ffd21a"])
    block(f"{name}SignFrame", (2, h + 4, D / 2 - 1), (9, 3, 0.4), _dark(), root)
    block(f"{name}Sign", (2, h + 4, D / 2 - 0.75), (8, 2.2, 0.1), _neon(col, 5.0), root)
    for sx in (-1, 1):
        tube(f"{name}SignPost{sx}", [(2 + sx * 4, h, D / 2 - 1), (2 + sx * 4, h + 2.6, D / 2 - 1)], 0.15, _dark(), root)
    return root


def build_building_kit_preview(parent=None, name="BuildingKitPreview"):
    root = _root(name, parent)
    items = [
        (build_lowrise_block, -150, {"h": 18}),
        (build_stepped_tower, -85, {"h": 140}),
        (build_ring_tower, -20, {"h": 160}),
        (build_billboard_tower, 45, {"h": 110}),
        (build_twin_towers, 120, {"h": 150}),
    ]
    for fn, x, kw in items:
        b = fn(root, f"{name}{fn.__name__}", **kw)
        b.location = P(x, 0, 0)
    # preview lighting: a purple-ish wash so the silhouettes read
    for k, (lx, ly, lz, col, en) in enumerate(((0, 120, 160, (0.6, 0.4, 1.0), 6.0e5), (-160, 60, 80, (1.0, 0.3, 0.8), 2.5e5))):
        ld = bpy.data.lights.new(f"{name}Wash{k}", "POINT")
        ld.color = col
        ld.energy = en
        ld.shadow_soft_size = 20
        lo = bpy.data.objects.new(f"{name}Wash{k}", ld)
        bpy.context.collection.objects.link(lo)
        lo.location = P(lx, ly, lz)
        lo.parent = root
    return root
