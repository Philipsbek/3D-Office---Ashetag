"""
Street kit for the outside city, in the smooth neon-night style:

    build_road_segment(parent=None, name="Road", length=40.0, crosswalk=False)
        one side of the canal road: canal edge with a glass railing and a neon
        base strip, two asphalt lanes (dashed centre line, solid edge lines),
        a rounded curb with a cyan neon strip, a tiled sidewalk, drain grates.
        Runs along X from -length/2 to +length/2; across Z the canal edge is
        at z = 0 and the sidewalk ends at z = 14.3.
    build_street_lamp(parent=None, name="Lamp", accent="#22e4ff", twin=False)
        7.2 m slim tapered pole on a round base, glowing accent ring, curved
        arm(s) and a flat lamp head with a warm-white light panel underneath.
        Origin at the foot of the pole; the arm reaches toward -Z (the road).
    build_street_kit_preview(parent, name) -> road + crosswalk + lamps + a car

Coordinates are three.js style (Y up).
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
from gaming_desk import disc, tube  # noqa: E402
from glass_room import glass_mat  # noqa: E402
from loft_room import block, mat  # noqa: E402

CANAL_EDGE, ROAD0, ROAD1, CURB1, WALK1 = 0.0, 1.2, 10.0, 10.35, 14.3
TEX_M = 4.0


# ---------------------------------------------------------------- textures
def _image(name, size, fn):
    img = bpy.data.images.get(name)
    if img:
        return img
    img = bpy.data.images.new(name, size, size)
    px = []
    for y in range(size):
        for x in range(size):
            px.extend((*fn(x, y), 1.0))
    img.pixels = px
    img.pack()
    return img


def _tex_mat(key, img, rough, interp="Linear", base_mult=1.0):
    m = bpy.data.materials.get(key)
    if m:
        return m
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = interp
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    return m


def asphalt_mat():
    rng = random.Random(5)
    noise = [[rng.random() for _ in range(128)] for _ in range(128)]

    def fn(x, y):
        n = noise[y][x]
        v = 0.07 + 0.04 * n
        if n > 0.97:
            v = 0.2  # bright aggregate
        return (v, v, v * 1.15)

    return _tex_mat("Road_Asphalt", _image("RoadAsphalt", 128, fn), 0.32)


def paving_mat():
    rng = random.Random(9)
    shade = {(i, j): rng.uniform(0.85, 1.15) for i in range(4) for j in range(8)}

    def fn(x, y):
        # 64 px = 4 m: 1 m x 0.5 m slabs in a running bond
        row = y // 8
        off = 8 if row % 2 else 0
        col = ((x + off) % 64) // 16
        if y % 8 == 0 or (x + off) % 16 == 0:
            return (0.025, 0.025, 0.035)
        s = shade[(col, row % 8)]
        return (0.11 * s, 0.11 * s, 0.13 * s)

    return _tex_mat("Road_Paving", _image("RoadPaving", 64, fn), 0.45, "Closest")


def _world_uv(o):
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
                u, v = co.x, co.y
            elif abs(n.y) > abs(n.x):
                u, v = co.x, co.z
            else:
                u, v = co.y, co.z
            uv[li].uv = (u / TEX_M, v / TEX_M)


def _mats(accent="#22e4ff"):
    return {
        "asphalt": asphalt_mat(),
        "paving": paving_mat(),
        "paint": mat("RoadPaint", "#d8dce6", 0.6, emit="#c8d0e0", strength=0.35),
        "paintY": mat("RoadPaintYellow", "#e0b030", 0.6, emit="#d0a020", strength=0.35),
        "curb": mat("RoadCurb", "#2b2d36", 0.5),
        "edge": mat("RoadCanalEdge", "#1e2028", 0.55),
        "metal": mat("RoadMetal", "#5b6070", 0.3, metal=0.9),
        "dark": mat("RoadDark", "#121318", 0.4, metal=0.5),
        "grate": mat("RoadGrate", "#0a0a0d", 0.6, metal=0.6),
        "glass": glass_mat("RoadRail", "#9fb4e0", 0.25),
        "neon": mat(f"RoadNeon{accent[1:]}", accent, emit=accent, strength=7.0),
        "lampLight": mat("LampPanel", "#fff2dc", emit="#ffe8c8", strength=12.0),
    }


def _slab(name, x0, x1, y0, y1, z0, z1, m, parent, r=0.0, world_uv=False):
    o = block(name, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0), m, parent, r)
    if world_uv:
        bpy.context.view_layer.update()
        _world_uv(o)
    return o


# ---------------------------------------------------------------- road
def build_road_segment(parent=None, name="Road", length=40.0, crosswalk=False, accent="#22e4ff"):
    M = _mats(accent)
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    L0, L1 = -length / 2, length / 2

    # canal edge: low stone ledge, neon base strip, glass railing with metal posts
    _slab(f"{name}Edge", L0, L1, -0.2, 0.2, CANAL_EDGE, ROAD0, M["edge"], root, r=0.04)
    _slab(f"{name}RailGlass", L0, L1, 0.2, 1.15, 0.28, 0.3, M["glass"], root)
    tube(f"{name}RailTop", [(L0, 1.18, 0.29), (L1, 1.18, 0.29)], 0.035, M["metal"], root)
    n_posts = int(length / 2.5)
    for k in range(n_posts + 1):
        x = L0 + k * length / n_posts
        _slab(f"{name}Post{k}", x - 0.03, x + 0.03, 0.2, 1.18, 0.25, 0.33, M["metal"], root)

    # asphalt, two lanes, markings (thin painted strips a hair above the road)
    _slab(f"{name}Asphalt", L0, L1, -0.1, 0.0, ROAD0, ROAD1, M["asphalt"], root, world_uv=True)
    mid = (ROAD0 + ROAD1) / 2
    for k, z in enumerate((ROAD0 + 0.35, ROAD1 - 0.35)):
        _slab(f"{name}EdgeLine{k}", L0, L1, 0.0, 0.012, z - 0.07, z + 0.07, M["paint"], root)
    x = L0 + 1.0
    k = 0
    while x + 3.0 <= L1:
        _slab(f"{name}Dash{k}", x, x + 3.0, 0.0, 0.012, mid - 0.08, mid + 0.08, M["paintY"], root)
        x += 6.0
        k += 1
    if crosswalk:
        for j in range(8):
            z0 = ROAD0 + 0.6 + j * 1.05
            _slab(f"{name}Zebra{j}", -2.0, 2.0, 0.0, 0.013, z0, z0 + 0.6, M["paint"], root)
        for k, x in enumerate((-2.6, 2.6)):
            _slab(f"{name}StopLine{k}", x - 0.15, x + 0.15, 0.0, 0.013, ROAD0 + 0.5, ROAD1 - 0.5, M["paint"], root)

    # rounded curb with a neon strip on its face, drains along the gutter
    _slab(f"{name}Curb", L0, L1, -0.1, 0.18, ROAD1, CURB1, M["curb"], root, r=0.06)
    for k, x in enumerate(range(int(L0) + 6, int(L1) - 2, 12)):
        _slab(f"{name}Drain{k}", x - 0.4, x + 0.4, 0.0, 0.01, ROAD1 - 0.45, ROAD1 - 0.05, M["grate"], root)
        for j in range(4):
            _slab(f"{name}DrainBar{k}_{j}", x - 0.32 + j * 0.2, x - 0.28 + j * 0.2, 0.01, 0.015, ROAD1 - 0.42, ROAD1 - 0.08, M["dark"], root)

    # tiled sidewalk
    _slab(f"{name}Sidewalk", L0, L1, -0.1, 0.16, CURB1, WALK1, M["paving"], root, world_uv=True)
    if crosswalk:
        # tactile paving at the crossing
        _slab(f"{name}Tactile", -2.0, 2.0, 0.16, 0.175, CURB1 + 0.1, CURB1 + 0.7, M["paintY"], root)
    return root


# ---------------------------------------------------------------- lamp
def build_street_lamp(parent=None, name="Lamp", accent="#22e4ff", twin=False):
    M = _mats(accent)
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    H = 7.2
    disc(f"{name}Base", (0, 0.15, 0), 0.32, 0.3, M["dark"], root, verts=24)
    disc(f"{name}BaseRing", (0, 0.31, 0), 0.26, 0.04, M["metal"], root, verts=24)
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=0.13, radius2=0.07, depth=H - 0.3, location=P(0, 0.3 + (H - 0.3) / 2, 0))
    pole = bpy.context.active_object
    pole.name = f"{name}Pole"
    bpy.ops.object.shade_smooth()
    pole.data.materials.append(M["dark"])
    pole.parent = root
    # collar ring (its neon glow was removed at the user's request, 2026-11-22)
    disc(f"{name}Ring", (0, 2.9, 0), 0.135, 0.12, M["metal"], root, verts=24)
    disc(f"{name}RingTop", (0, 3.06, 0), 0.125, 0.03, M["metal"], root, verts=24)

    sides = (-1, 1) if twin else (-1,)
    for s in sides:
        # curved arm: up, then out over the road (toward s * Z), drooping slightly
        pts = []
        for k in range(9):
            t = k / 8
            a = t * math.pi / 2
            pts.append((0, H - 0.6 + 0.6 * math.sin(a), s * 2.2 * (1 - math.cos(a)) * 0.55 + s * 2.2 * t * 0.45))
        tube(f"{name}Arm{s}", pts, 0.05, M["dark"], root)
        hz = s * 2.25
        block(f"{name}Head{s}", (0, H + 0.02, hz), (0.38, 0.12, 1.25), M["dark"], root, r=0.05)
        block(f"{name}Panel{s}", (0, H - 0.045, hz), (0.28, 0.02, 1.1), M["lampLight"], root)
    return root


# ---------------------------------------------------------------- preview
def build_street_kit_preview(parent=None, name="StreetKitPreview"):
    import city_cars

    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    # canal water strip so the edge reads
    water = mat("PreviewCanal", "#3a1a6a", 0.1, emit="#7a3aff", strength=0.6)
    _slab(f"{name}Canal", -40, 40, -0.6, -0.3, -8, 0, water, root)
    build_road_segment(root, f"{name}RoadA", 40.0).location = P(-20, 0, 0)
    build_road_segment(root, f"{name}RoadB", 40.0, crosswalk=True).location = P(20, 0, 0)
    for k, x in enumerate((-30, -12, 6, 24)):
        lamp = build_street_lamp(root, f"{name}Lamp{k}", "#22e4ff" if k % 2 == 0 else "#ff4fd8")
        lamp.location = P(x, 0.16, WALK1 - 3.2)
        # preview-only pool of light under the head (lights are not exported)
        ld = bpy.data.lights.new(f"{name}LampLight{k}", "SPOT")
        ld.color = (1.0, 0.9, 0.78)
        ld.energy = 16000
        ld.spot_size = math.radians(120)
        ld.spot_blend = 0.6
        ld.shadow_soft_size = 0.5
        ld.specular_factor = 0.0
        lo = bpy.data.objects.new(f"{name}LampLight{k}", ld)
        bpy.context.collection.objects.link(lo)
        lo.location = P(x, 7.0, WALK1 - 3.2 - 2.25)
        lo.rotation_euler = (0, 0, 0)  # points straight down
    twin = build_street_lamp(root, f"{name}TwinLamp", "#ffb82e", twin=True)
    twin.location = P(42, 0.16, WALK1 - 3.2)
    for k, (x, z, paint) in enumerate(((-16, 3.4, "#c23a1c"), (9, 7.8, "#c9ccd4"))):
        car = city_cars.build_street_car(root, f"{name}Car{k}", paint)
        car.location = P(x, 0, z)
        if k:
            car.rotation_euler = (0, 0, math.pi)
    fill = bpy.data.lights.new(f"{name}Fill", "POINT")
    fill.color = (0.6, 0.5, 1.0)
    fill.energy = 60000
    fill.shadow_soft_size = 8
    fo = bpy.data.objects.new(f"{name}Fill", fill)
    bpy.context.collection.objects.link(fo)
    fo.location = P(0, 30, 30)
    return root


# ---------------------------------------------------------------- city grid streets
HALF_ROAD = 4.4  # asphalt half width (two lanes)
WALK = 4.0  # sidewalk width each side
CURB = 0.35
STREET_W = 2 * (HALF_ROAD + CURB + WALK)  # 17.5 m kerb-to-kerb incl. sidewalks


def build_street_segment(parent=None, name="Street", length=40.0, accent="#22e4ff"):
    """Two-lane city street with a sidewalk on both sides. Runs along X, centred
    on the origin; the road centre line is z = 0."""
    M = _mats(accent)
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    L0, L1 = -length / 2, length / 2
    _slab(f"{name}Asphalt", L0, L1, -0.1, 0.0, -HALF_ROAD, HALF_ROAD, M["asphalt"], root, world_uv=True)
    for k, z in enumerate((-HALF_ROAD + 0.35, HALF_ROAD - 0.35)):
        _slab(f"{name}EdgeLine{k}", L0, L1, 0.0, 0.012, z - 0.07, z + 0.07, M["paint"], root)
    x = L0 + 1.0
    k = 0
    while x + 3.0 <= L1:
        _slab(f"{name}Dash{k}", x, x + 3.0, 0.0, 0.012, -0.08, 0.08, M["paintY"], root)
        x += 6.0
        k += 1
    for s in (-1, 1):
        z0, z1 = sorted((s * HALF_ROAD, s * (HALF_ROAD + CURB)))
        _slab(f"{name}Curb{s}", L0, L1, -0.1, 0.18, z0, z1, M["curb"], root, r=0.06)
        # (curb neon strip removed at the user's request, 2026-11-22)
        w0, w1 = sorted((s * (HALF_ROAD + CURB), s * (HALF_ROAD + CURB + WALK)))
        _slab(f"{name}Sidewalk{s}", L0, L1, -0.1, 0.16, w0, w1, M["paving"], root, world_uv=True)
        for j, xx in enumerate(range(int(L0) + 6, int(L1) - 2, 12)):
            gz = s * (HALF_ROAD - 0.25)
            _slab(f"{name}Drain{s}_{j}", xx - 0.4, xx + 0.4, 0.0, 0.01, gz - 0.2, gz + 0.2, M["grate"], root)
    return root


def build_intersection(parent=None, name="Crossroads", accent="#22e4ff"):
    """Four-way crossing tile, STREET_W square, centred on the origin: open asphalt
    in a plus shape, zebra crossings and stop lines on all four arms, rounded
    corner sidewalks with neon curb edges, a lamp on two opposite corners."""
    from city_smooth import rounded_band, rounded_prism

    M = _mats(accent)
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    H = STREET_W / 2
    _slab(f"{name}Asphalt", -H, H, -0.1, 0.0, -H, H, M["asphalt"], root, world_uv=True)
    # zebra crossings across each arm, just outside the junction box
    for arm in range(4):
        for j in range(7):
            t = -HALF_ROAD + 0.5 + j * 1.15
            if arm in (0, 1):  # crossings over the X-running arms (stripes run along X)
                x = (H - 1.6) * (1 if arm == 0 else -1)
                _slab(f"{name}Zebra{arm}_{j}", x - 1.3, x + 1.3, 0.0, 0.013, t, t + 0.6, M["paint"], root)
            else:  # crossings over the Z-running arms
                z = (H - 1.6) * (1 if arm == 2 else -1)
                _slab(f"{name}Zebra{arm}_{j}", t, t + 0.6, 0.0, 0.013, z - 1.3, z + 1.3, M["paint"], root)
        # stop line on the inner side of each crossing
        if arm in (0, 1):
            x = (H - 3.3) * (1 if arm == 0 else -1)
            _slab(f"{name}Stop{arm}", x - 0.15, x + 0.15, 0.0, 0.013, -HALF_ROAD + 0.4, HALF_ROAD - 0.4, M["paint"], root)
        else:
            z = (H - 3.3) * (1 if arm == 2 else -1)
            _slab(f"{name}Stop{arm}", -HALF_ROAD + 0.4, HALF_ROAD - 0.4, 0.0, 0.013, z - 0.15, z + 0.15, M["paint"], root)
    # rounded corner sidewalk blocks (their neon curb edge was removed, 2026-11-22)
    c = HALF_ROAD + (CURB + WALK) / 2
    size = CURB + WALK
    for k, (sx, sz) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
        cx, cz = sx * c, sz * c
        rounded_prism(f"{name}Corner{k}", (cx, -0.1, cz), size, size, 1.4, 0.28, M["paving"], root, seg=6, cap_m=M["paving"])
        if k in (0, 2):
            lamp = build_street_lamp(root, f"{name}Lamp{k}", accent)
            lamp.location = P(cx + sx * 0.8, 0.18, cz + sz * 0.8)
            lamp.rotation_euler = (0, 0, math.atan2(-sx, -sz) + math.pi)
    return root


def build_street_grid_preview(parent=None, name="StreetGridPreview"):
    """Preview only: a crossroads with a street arm on each side, lamps and cars."""
    import city_cars

    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    build_intersection(root, f"{name}X")
    H = STREET_W / 2
    for k, (dx, dz, rot) in enumerate(((H + 15, 0, 0), (-H - 15, 0, 0), (0, H + 15, 90), (0, -H - 15, 90))):
        st = build_street_segment(root, f"{name}Arm{k}", 30.0, "#ff4fd8" if k % 2 else "#22e4ff")
        st.location = P(dx, 0, dz)
        st.rotation_euler = (0, 0, math.radians(rot))
    for k, (x, z, rz) in enumerate(((H + 8, HALF_ROAD + CURB + WALK - 1.0, 180), (-H - 22, -(HALF_ROAD + CURB + WALK - 1.0), 0))):
        lamp = build_street_lamp(root, f"{name}ArmLamp{k}", "#ff4fd8")
        lamp.location = P(x, 0.16, z)
        lamp.rotation_euler = (0, 0, math.radians(rz))
    for k, (x, z, rz, paint) in enumerate(((H + 12, -2.2, 0, "#c23a1c"), (-H - 9, 2.2, 180, "#c9ccd4"), (2.2, H + 10, -90, "#23408f"))):
        car = city_cars.build_street_car(root, f"{name}Car{k}", paint)
        car.location = P(x, 0, z)
        car.rotation_euler = (0, 0, math.radians(rz))
    fill = bpy.data.lights.new(f"{name}Fill", "POINT")
    fill.color = (0.6, 0.5, 1.0)
    fill.energy = 90000
    fill.shadow_soft_size = 10
    fo = bpy.data.objects.new(f"{name}Fill", fill)
    bpy.context.collection.objects.link(fo)
    fo.location = P(0, 35, 10)
    return root


# ---------------------------------------------------------------- traffic lights
SIGNAL_COLORS = {"red": "#ff2a2a", "amber": "#ffb020", "green": "#2bff7a", "walk": "#e8f6ff", "stop": "#ff3a3a"}


def _signal_mat(kind, on):
    """Lens materials keep fixed names (Loft_SignalRed ...) so the site can drive
    them per instance; the preview shows lit or dark versions."""
    col = SIGNAL_COLORS[kind]
    name = f"Signal{kind.capitalize()}" + ("" if on else "Off")
    if on:
        return mat(name, col, 0.3, emit=col, strength=14.0)
    return mat(name, "#1a1b20", 0.25)


def build_traffic_light(parent=None, name="TrafficLight", accent="#22e4ff", state="green"):
    """Slim mast-arm signal: tapered pole with a neon ring, a curved-brace arm
    reaching 5 m over the road (toward local -Z), two rounded signal heads with
    red / amber / green lenses and visors facing local -X, a neon-edged
    backplate, and a pedestrian walk box on the pole.
    state: 'green' | 'amber' | 'red' (which lens is lit in the preview)."""
    from city_smooth import rounded_band, rounded_prism

    M = _mats(accent)
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    H, ARM = 6.0, 5.0
    disc(f"{name}Base", (0, 0.12, 0), 0.3, 0.24, M["dark"], root, verts=24)
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=0.15, radius2=0.1, depth=H, location=P(0, 0.24 + H / 2, 0))
    pole = bpy.context.active_object
    pole.name = f"{name}Pole"
    bpy.ops.object.shade_smooth()
    pole.data.materials.append(M["dark"])
    pole.parent = root
    disc(f"{name}Ring", (0, 3.6, 0), 0.155, 0.1, M["metal"], root, verts=24)  # neon removed 2026-11-22
    disc(f"{name}Cap", (0, H + 0.28, 0), 0.13, 0.08, M["metal"], root, verts=24)
    # arm with a curved brace underneath
    tube(f"{name}Arm", [(0, H - 0.2, 0), (0, H - 0.2, -ARM)], 0.06, M["dark"], root)
    brace = [(0, H - 1.4 + 1.2 * math.sin(t / 8 * math.pi / 2), -ARM * 0.55 * (1 - math.cos(t / 8 * math.pi / 2))) for t in range(9)]
    tube(f"{name}Brace", brace, 0.035, M["dark"], root)

    # state "all": every lens uses its lit material (the site export: the page drives them per instance)
    lit = {k: state in (k, "all") for k in ("red", "amber", "green")}
    for k, hz in enumerate((-2.6, -4.6)):
        hy = H - 1.05
        # backplate with neon edge, then the rounded housing in front of it
        rounded_prism(f"{name}Back{k}", (0.04, hy - 0.85, hz), 0.05, 0.78, 0.12, 1.7, M["dark"], root, seg=4, cap_m=M["dark"])
        rounded_prism(f"{name}Head{k}", (-0.17, hy - 0.62, hz), 0.34, 0.44, 0.1, 1.24, M["curb"], root, seg=4, cap_m=M["dark"])
        tube(f"{name}Hanger{k}", [(-0.05, hy + 0.62, hz), (-0.05, H - 0.2, hz)], 0.03, M["metal"], root)
        for j, (kind, dy) in enumerate((("red", 0.38), ("amber", 0.0), ("green", -0.38))):
            disc(f"{name}Lens{k}{kind}", (-0.35, hy + dy, hz), 0.13, 0.03, _signal_mat(kind, lit[kind]), root, axis="x", verts=24)
            block(f"{name}Visor{k}{j}", (-0.45, hy + dy + 0.15, hz), (0.22, 0.025, 0.3), M["dark"], root)

    # pedestrian box on the pole, facing the crossing (local -X): hand above, walker below
    walk_on = state in ("red", "all")  # walkers cross while the cars wait
    rounded_prism(f"{name}PedBox", (-0.25, 2.5, 0), 0.3, 0.42, 0.06, 0.8, M["dark"], root, seg=4, cap_m=M["dark"])
    block(f"{name}PedStop", (-0.41, 3.1, 0), (0.02, 0.26, 0.3), _signal_mat("stop", not walk_on or state == "all"), root)
    block(f"{name}PedWalk", (-0.41, 2.75, 0), (0.02, 0.26, 0.3), _signal_mat("walk", walk_on), root)
    return root


def build_traffic_preview(parent=None, name="TrafficPreview"):
    """Preview only: the crossroads with street arms, a signal on every corner
    (east-west green, north-south red), and cars waiting / driving."""
    root = build_street_grid_preview(parent, name)
    c = HALF_ROAD + CURB + 0.55
    # (corner sx, sz, rotation, state): east-west approaches green, north-south red
    for k, (sx, sz, rot, st) in enumerate(((1, 1, 0, "green"), (-1, -1, 180, "green"), (-1, 1, -90, "red"), (1, -1, 90, "red"))):
        tl = build_traffic_light(root, f"{name}Signal{k}", "#22e4ff", st)
        tl.location = P(sx * c, 0.16, sz * c)
        tl.rotation_euler = (0, 0, math.radians(rot))
    return root
