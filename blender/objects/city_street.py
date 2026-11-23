"""
Blocky neon street building for the outside city (style ref: a chunky,
fog-wrapped cyberpunk street block). One wide building in three joined
sections, all dark cobbled stone with neon:

  left   : 2-storey BAR with a cyan box sign, lantern panel sign, purple-lit
           shopfront, overhanging roof, rooftop AC + antennas with red beacons
  middle : 3-storey GARAGE with a roller door framed in cyan neon, a big cyan
           GARAGE sign, blue-lit windows with cyan light bars, a balcony
  right  : 4-storey red block with a stepped red awning, red-lit windows with
           pink tube lights, corner pink neon tubes, a vertical bulb sign and
           a rooftop billboard on scaffolding

Plus a sidewalk with a curb, pipes, AC units and wall lamps.

    build_street_building(parent=None, name="StreetBuilding") -> root empty
        origin on the ground at the middle of the front wall, facing +Z,
        about 24 m wide and 22 m tall to the billboard top.
    build_street_building_preview(parent, name) -> building + coloured fill lights

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
from loft_room import block, mat  # noqa: E402

TEX_M = 4.0  # metres covered by one stone-texture tile


# ---------------------------------------------------------------- materials
def _stone_image(name, base, seed):
    img = bpy.data.images.get(name)
    if img:
        return img
    W = 64
    rng = random.Random(seed)
    img = bpy.data.images.new(name, W, W)
    br, bg, bb = _hex(base)
    px = [0.0] * (W * W * 4)
    # chunky 8x8 "blocks" with their own shade, mortar lines, per-pixel grit
    shade = {(i, j): rng.uniform(0.55, 1.45) for i in range(8) for j in range(8)}
    for y in range(W):
        for x in range(W):
            i, j = x // 8, y // 8
            s = shade[(i, j)] * rng.uniform(0.85, 1.15)
            if x % 8 == 0 or y % 8 == 0:
                s *= 0.55  # mortar
            k = (y * W + x) * 4
            px[k:k + 4] = (br * s, bg * s, bb * s, 1.0)
    img.pixels = px
    img.pack()
    return img


def stone_mat(name="Stone", base="#24252c", seed=1):
    key = "Street_" + name
    m = bpy.data.materials.get(key)
    if m:
        return m
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.78
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = _stone_image(key + "Tex", base, seed)
    tex.interpolation = "Closest"  # crisp blocky texels
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    m.diffuse_color = (*_hex(base), 1)
    return m


def _world_uv(o):
    """Box-map the stone texture in world metres so blocks line up across parts."""
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


def wall(name, x0, x1, y0, y1, z0, z1, m, parent):
    o = block(name, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0), m, parent)
    bpy.context.view_layer.update()
    _world_uv(o)
    return o


def _M():
    return {
        "stoneA": stone_mat("StoneA", "#3a3b47", 1),
        "stoneB": stone_mat("StoneB", "#33353f", 2),
        "stoneC": stone_mat("StoneC", "#3b3340", 3),
        "pave": stone_mat("Pave", "#1c1d22", 4),
        "trim": mat("StreetTrim", "#121318", 0.6),
        "metal": mat("StreetMetal", "#3a3d45", 0.4, metal=0.7),
        "light": mat("StreetLightGrey", "#b9bcc4", 0.55),
        "door": mat("StreetDoor", "#4a4d55", 0.5, metal=0.5),
        "glass": mat("StreetGlass", "#0a0c14", 0.08, metal=0.3),
        "pipe": mat("StreetPipe", "#8a3a1e", 0.5, metal=0.6),
        "red": mat("StreetRed", "#7a0f1c", 0.55),
        "redDark": mat("StreetRedDark", "#4a0812", 0.6),
        "cyan": mat("StreetCyan", "#2af0ff", emit="#2af0ff", strength=9.0),
        "cyanDim": mat("StreetCyanDim", "#1aa8c4", emit="#1aa8c4", strength=3.5),
        "pink": mat("StreetPink", "#ff5cf0", emit="#ff5cf0", strength=10.0),
        "purpleIn": mat("StreetPurpleIn", "#a04cff", emit="#a04cff", strength=1.1),
        "blueIn": mat("StreetBlueIn", "#2d6bff", emit="#2d6bff", strength=1.3),
        "redIn": mat("StreetRedIn", "#ff1838", emit="#ff1838", strength=1.6),
        "white": mat("StreetWhite", "#ffffff", emit="#e8f0ff", strength=7.0),
        "amber": mat("StreetAmber", "#ffb23a", emit="#ffa020", strength=9.0),
        "beacon": mat("StreetBeacon", "#ff2020", emit="#ff2020", strength=14.0),
    }


# ---------------------------------------------------------------- details
def neon_text(name, body, c, size, m, parent, max_w, depth=0.06):
    """Solid, extruded block-letter text facing +Z, centred at c."""
    bpy.ops.object.text_add()
    t = bpy.context.active_object
    t.data.body = body
    t.data.align_x = "CENTER"
    t.data.align_y = "CENTER"
    t.data.size = size
    t.data.space_character = 1.1
    bpy.context.view_layer.update()
    if t.dimensions.x > max_w:
        t.data.size = size * max_w / t.dimensions.x
    t.data.extrude = depth
    t.data.bevel_depth = 0.012
    t.rotation_euler = (math.pi / 2, 0, 0)
    t.location = P(*c)
    t.data.materials.append(m)
    bpy.ops.object.convert(target="MESH")
    t = bpy.context.active_object
    t.name = name
    t.parent = parent
    return t


def box_sign(name, c, w, h, text, M, parent, glow="cyan", face="trim"):
    """Backlit box sign: dark box, neon frame, neon letters."""
    x, y, z = c
    block(f"{name}Box", (x, y, z + 0.15), (w, h, 0.3), M[face], parent)
    for k, (dx, dy, sw, sh) in enumerate(((0, h / 2, w, 0.08), (0, -h / 2, w, 0.08), (-w / 2, 0, 0.08, h), (w / 2, 0, 0.08, h))):
        block(f"{name}Frame{k}", (x + dx, y + dy, z + 0.32), (sw, sh, 0.06), M[glow], parent)
    neon_text(f"{name}Text", text, (x, y, z + 0.33), h * 0.7, M[glow], parent, w * 0.86)


def ac_unit(name, c, M, parent):
    x, y, z = c
    block(f"{name}Body", (x, y, z), (0.8, 0.6, 0.35), M["light"], parent, r=0.02)
    disc(f"{name}Fan", (x - 0.12, y, z + 0.18), 0.2, 0.02, M["trim"], parent, axis="z")
    for k in range(3):
        block(f"{name}Grill{k}", (x + 0.26, y - 0.15 + k * 0.15, z + 0.18), (0.18, 0.03, 0.02), M["metal"], parent)


def wall_lamp(name, c, M, parent, size=(0.45, 0.6)):
    """Chunky white lamp box with a dark grid (the bright 'pixel' lamps in the ref)."""
    x, y, z = c
    w, h = size
    block(f"{name}Glow", (x, y, z + 0.12), (w, h, 0.24), M["white"], parent)
    block(f"{name}Bar", (x, y, z + 0.25), (0.05, h, 0.02), M["trim"], parent)
    block(f"{name}BarH", (x, y, z + 0.25), (w, 0.05, 0.02), M["trim"], parent)


def antenna(name, c, h, M, parent):
    x, y, z = c
    block(f"{name}Base", (x, y + 0.15, z), (0.4, 0.3, 0.4), M["trim"], parent)
    block(f"{name}Mast", (x, y + h / 2, z), (0.14, h, 0.14), M["metal"], parent)
    block(f"{name}Beacon", (x, y + h + 0.1, z), (0.22, 0.22, 0.22), M["beacon"], parent)


def pipe_run(name, pts, M, parent, r=0.06):
    tube(name, pts, r, M["pipe"], parent)


def _billboard_image():
    name = "StreetBillboard"
    img = bpy.data.images.get(name)
    if img:
        return img
    W, H = 96, 48
    img = bpy.data.images.new(name, W, H)
    px = [0.0] * (W * H * 4)
    rng = random.Random(7)
    for y in range(H):
        for x in range(W):
            u, v = x / W, y / H
            r, g, b = 0.18 + 0.25 * v, 0.04, 0.35 + 0.2 * v  # purple
            if (x // 6 + y // 6) % 2 == 0:
                r, g, b = r * 0.8, g, b * 0.8
            if 0.08 < u < 0.4 and 0.15 < v < 0.85:  # pink panel with a figure
                r, g, b = 0.9, 0.2, 0.7
                if abs(u - 0.24) < 0.04 and 0.2 < v < 0.65 or math.hypot((u - 0.24) * 2, v - 0.72) < 0.07:
                    r, g, b = 0.05, 0.02, 0.1
            if 0.5 < u < 0.92 and 0.55 < v < 0.7:
                r, g, b = 0.2, 0.9, 1.0  # cyan headline bar
            if 0.5 < u < 0.8 and 0.35 < v < 0.43:
                r, g, b = 1.0, 0.8, 0.2
            if 0.5 < u < 0.7 and 0.2 < v < 0.27:
                r, g, b = 0.9, 0.9, 1.0
            px[(y * W + x) * 4:(y * W + x) * 4 + 4] = (r, g, b, 1.0)
    img.pixels = px
    img.pack()
    return img


def billboard(name, c, w, h, M, parent):
    x, y, z = c
    m = bpy.data.materials.get("Street_Billboard")
    if not m:
        m = bpy.data.materials.new("Street_Billboard")
        m.use_nodes = True
        nt = m.node_tree
        b = nt.nodes["Principled BSDF"]
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = _billboard_image()
        tex.interpolation = "Closest"
        nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
        nt.links.new(tex.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = 2.2
    bpy.ops.mesh.primitive_plane_add(size=1)
    o = bpy.context.active_object
    o.name = f"{name}Screen"
    o.scale = (w, h, 1)
    o.rotation_euler = (math.pi / 2, 0, 0)
    o.location = P(x, y + h / 2, z + 0.12)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    o.data.materials.append(m)
    o.parent = parent
    block(f"{name}Back", (x, y + h / 2, z), (w + 0.3, h + 0.3, 0.2), M["trim"], parent)
    # scaffold legs + cross braces behind it
    for k, dx in enumerate((-w / 2 + 0.4, 0, w / 2 - 0.4)):
        block(f"{name}Leg{k}", (x + dx, y + h / 2 - 0.6, z - 0.6), (0.18, h + 1.2, 0.18), M["metal"], parent)
    for k, dy in enumerate((0.4, h - 0.4)):
        block(f"{name}Rail{k}", (x, y + dy, z - 0.6), (w, 0.12, 0.12), M["metal"], parent)
    block(f"{name}Lip", (x, y - 0.05, z + 0.3), (w + 0.4, 0.12, 0.5), M["trim"], parent)
    block(f"{name}LipGlow", (x, y - 0.12, z + 0.5), (w, 0.04, 0.06), M["pink"], parent)


def balcony(name, x0, x1, y, z, M, parent, depth=1.0):
    block(f"{name}Slab", ((x0 + x1) / 2, y, z + depth / 2), (x1 - x0, 0.2, depth), M["trim"], parent)
    block(f"{name}Rail", ((x0 + x1) / 2, y + 1.0, z + depth), (x1 - x0, 0.08, 0.08), M["metal"], parent)
    n = int((x1 - x0) / 0.3)
    for k in range(n + 1):
        block(f"{name}Bar{k}", (x0 + k * (x1 - x0) / n, y + 0.5, z + depth), (0.05, 1.0, 0.05), M["metal"], parent)


def _texture_bumps(prefix, x0, x1, y0, y1, z, M, parent, rng, n, m):
    """Odd stones sticking out of the wall, for the chunky block texture."""
    for k in range(n):
        s = rng.choice((0.5, 0.5, 1.0))
        x = rng.uniform(x0 + s, x1 - s)
        y = rng.uniform(y0 + s, y1 - s)
        wall(f"{prefix}Bump{k}", x - s / 2, x + s / 2, y - s / 2, y + s / 2, z, z + 0.03, m, parent)


# ---------------------------------------------------------------- building
def build_street_building(parent=None, name="StreetBuilding"):
    M = _M()
    rng = random.Random(11)
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent

    # ---- sidewalk + curb
    wall(f"{name}Sidewalk", -13, 13, 0, 0.18, 0, 3.2, M["pave"], root)
    wall(f"{name}Curb", -13, 13, 0, 0.22, 3.2, 3.45, M["trim"], root)

    # ================= LEFT: BAR (x -12..-4, 2 storeys)
    L0, L1 = -12.0, -4.0
    wall(f"{name}BarMass", L0, L1, 0, 8.0, -6, 0, M["stoneA"], root)
    wall(f"{name}BarPlinth", L0, L1, 0, 0.6, 0, 0.15, M["trim"], root)
    # shopfront: recessed purple-lit glass + mullions
    wall(f"{name}BarFrontRecess", L0 + 0.6, L1 - 0.6, 0.6, 3.2, -0.01, 0.12, M["trim"], root)
    block(f"{name}BarInterior", ((L0 + L1) / 2, 1.9, 0.14), (L1 - L0 - 1.6, 2.3, 0.04), M["purpleIn"], root)
    for k in range(4):
        block(f"{name}BarMull{k}", (L0 + 1.5 + k * 1.7, 1.9, 0.2), (0.1, 2.4, 0.08), M["trim"], root)
    block(f"{name}BarStrip", ((L0 + L1) / 2, 3.45, 0.25), (L1 - L0 - 1.2, 0.14, 0.1), M["cyan"], root)
    block(f"{name}BarStrip2", ((L0 + L1) / 2, 3.75, 0.25), (L1 - L0 - 1.2, 0.08, 0.08), M["cyanDim"], root)
    # canopy above shopfront with a white tube light under it
    block(f"{name}BarCanopy", ((L0 + L1) / 2, 4.15, 0.6), (L1 - L0 - 0.4, 0.25, 1.2), M["trim"], root)
    block(f"{name}BarCanopyLight", ((L0 + L1) / 2 + 0.5, 4.0, 0.9), (3.0, 0.06, 0.1), M["pink"], root)
    # signs: lantern panel + BAR box sign
    block(f"{name}LanternBack", (L0 + 2.3, 5.2, 0.15), (2.6, 1.3, 0.3), M["redDark"], root)
    for k in range(3):
        cx = L0 + 1.45 + k * 0.85
        block(f"{name}Lantern{k}", (cx, 5.2, 0.33), (0.62, 1.05, 0.06), M["amber"], root)
        block(f"{name}LanternMark{k}", (cx, 5.25, 0.37), (0.28, 0.45, 0.02), M["red"], root)
    box_sign(f"{name}BarSign", (L0 + 5.4, 5.2, 0.0), 2.7, 1.3, "BAR", M, root)
    # upper floor window + roof overhang
    block(f"{name}UpWin", (L0 + 4.0, 6.9, 0.03), (3.0, 0.9, 0.08), M["glass"], root)
    block(f"{name}UpWinGlow", (L0 + 4.0, 6.75, 0.08), (2.8, 0.25, 0.04), M["blueIn"], root)
    wall(f"{name}BarRoof", L0 - 0.3, L1, 8.0, 8.5, -6, 0.9, M["trim"], root)
    block(f"{name}BarRoofGlow", ((L0 + L1) / 2, 7.95, 0.92), (L1 - L0 - 1.0, 0.05, 0.04), M["cyanDim"], root)
    # rooftop: parapet, AC, water tank, antennas
    wall(f"{name}BarParapet", L0, L1, 8.5, 9.1, 0.3, 0.6, M["stoneA"], root)
    ac_unit(f"{name}RoofAC0", (L0 + 2.0, 8.8, -1.5), M, root)
    ac_unit(f"{name}RoofAC1", (L0 + 3.2, 8.8, -1.5), M, root)
    block(f"{name}RoofHut", (L0 + 6.0, 9.4, -3.0), (2.0, 1.8, 2.0), M["stoneA"], root)
    antenna(f"{name}Ant0", (L0 + 1.0, 8.5, -0.8), 3.2, M, root)
    antenna(f"{name}Ant1", (L0 + 4.6, 8.5, -2.5), 2.2, M, root)
    wall_lamp(f"{name}RoofLamp", (L0 + 0.3, 9.4, 0.6), M, root, (0.5, 0.5))
    _texture_bumps(f"{name}BarTex", L0, L1, 4.4, 8.0, 0.0, M, root, rng, 10, M["stoneA"])

    # ================= MIDDLE: GARAGE (x -4..4, 3 storeys)
    G0, G1 = -4.0, 4.0
    wall(f"{name}GarMass", G0, G1, 0, 13.0, -7, 0.3, M["stoneB"], root)
    # roller door with a cyan neon frame
    wall(f"{name}GarDoorRecess", -2.6, 2.6, 0.18, 3.6, 0.2, 0.32, M["trim"], root)
    for k in range(11):
        block(f"{name}GarSlat{k}", (0, 0.4 + k * 0.29, 0.31), (5.0, 0.22, 0.04), M["door"], root)
    for k, (cx, cy, sw, sh) in enumerate(((0, 3.75, 5.6, 0.12), (-2.75, 1.9, 0.12, 3.6), (2.75, 1.9, 0.12, 3.6))):
        block(f"{name}GarFrame{k}", (cx, cy, 0.4), (sw, sh, 0.08), M["cyan"], root)
    box_sign(f"{name}GarSign", (0, 5.0, 0.3), 6.2, 1.5, "GARAGE", M, root)
    block(f"{name}GarSignIcon", (3.55, 5.0, 0.6), (0.8, 1.5, 0.1), M["redIn"], root)
    # floor 2: wide blue-lit window under two cyan light bars
    for k in range(2):
        block(f"{name}GarBar{k}", (0, 7.1 + k * 0.45, 0.4), (5.6, 0.18, 0.12), M["cyan"], root)
    block(f"{name}GarWin2", (0, 8.6, 0.33), (5.8, 1.8, 0.04), M["trim"], root)
    block(f"{name}GarWin2Glow", (0, 8.6, 0.36), (5.4, 1.4, 0.02), M["blueIn"], root)
    for k in range(3):
        block(f"{name}GarWin2Mull{k}", (-1.4 + k * 1.4, 8.6, 0.38), (0.1, 1.6, 0.06), M["trim"], root)
    # floor 3: blue panel + balcony at the left
    block(f"{name}GarWin3", (1.0, 11.2, 0.33), (4.0, 1.5, 0.04), M["blueIn"], root)
    for k in range(2):
        block(f"{name}GarWin3Mull{k}", (k * 2.0, 11.2, 0.37), (0.1, 1.5, 0.06), M["trim"], root)
    balcony(f"{name}GarBalc", -3.9, -1.6, 10.0, 0.3, M, root)
    block(f"{name}GarBalcDoor", (-2.75, 11.0, 0.33), (1.4, 2.0, 0.04), M["purpleIn"], root)
    wall_lamp(f"{name}GarLamp0", (-3.6, 6.2, 0.3), M, root)
    wall_lamp(f"{name}GarLamp1", (-3.4, 9.0, 0.3), M, root, (0.6, 0.9))
    ac_unit(f"{name}GarAC0", (2.4, 9.9, 0.5), M, root)
    ac_unit(f"{name}GarAC1", (-3.0, 4.6, 0.5), M, root)
    wall(f"{name}GarRoof", G0, G1, 13.0, 13.5, -7, 0.8, M["trim"], root)
    antenna(f"{name}Ant2", (G0 + 0.8, 13.5, -1.0), 2.8, M, root)
    _texture_bumps(f"{name}GarTex", G0, G1, 6.0, 13.0, 0.3, M, root, rng, 12, M["stoneB"])

    # ================= RIGHT: red block (x 4..12, 4 storeys) + billboard
    R0, R1 = 4.0, 12.0
    wall(f"{name}RedMass", R0, R1, 0, 17.0, -7, 0.1, M["stoneC"], root)
    # ground: red-lit shop
    wall(f"{name}RedShopRecess", R0 + 1.0, R1 - 1.0, 0.18, 3.8, 0.0, 0.12, M["trim"], root)
    block(f"{name}RedShopGlow", ((R0 + R1) / 2, 2.0, 0.14), (5.6, 3.2, 0.04), M["redIn"], root)
    block(f"{name}RedShopDoor", ((R0 + R1) / 2 - 1.0, 1.6, 0.18), (1.3, 2.8, 0.06), M["trim"], root)
    for k, x in enumerate((R0 + 0.6, R1 - 0.6)):
        block(f"{name}RedTube{k}", (x, 2.0, 0.25), (0.14, 3.0, 0.14), M["pink"], root)
    # stepped red awning
    for k in range(4):
        block(f"{name}Awning{k}", ((R0 + R1) / 2 + 0.2, 4.4 + k * 0.28, 1.0 - k * 0.35),
              (R1 - R0 + 1.2 - k * 0.2, 0.28, 2.0 - k * 0.5), M["red" if k % 2 == 0 else "redDark"], root)
    # floor 2-3: two red windows with pink tube light above each
    for k, cx in enumerate((R0 + 2.2, R0 + 5.6)):
        block(f"{name}RedWin{k}", (cx, 7.6, 0.12), (2.6, 2.2, 0.04), M["redIn"], root)
        block(f"{name}RedWinFrame{k}", (cx, 6.45, 0.18), (2.8, 0.15, 0.15), M["trim"], root)
        block(f"{name}RedWinTube{k}", (cx, 8.85, 0.25), (2.4, 0.09, 0.09), M["pink"], root)
    # red strips + sign band
    block(f"{name}RedStrip0", ((R0 + R1) / 2 + 0.6, 10.3, 0.2), (R1 - R0 - 1.0, 0.35, 0.2), M["redIn"], root)
    block(f"{name}RedStrip1", ((R0 + R1) / 2 + 0.3, 11.1, 0.2), (R1 - R0 - 2.0, 0.25, 0.2), M["red"], root)
    # floor 4: recessed balcony with white light + corner pink tubes
    balcony(f"{name}RedBalc", R0 + 1.0, R0 + 4.5, 12.4, 0.1, M, root, depth=0.8)
    block(f"{name}RedBalcGlow", (R0 + 2.75, 13.6, 0.16), (3.0, 1.8, 0.04), M["purpleIn"], root)
    block(f"{name}RedCornerTube", (R1 - 0.2, 14.0, 0.3), (0.2, 4.6, 0.2), M["pink"], root)
    block(f"{name}RedTopLight", (R0 + 6.0, 15.5, 0.2), (0.2, 1.2, 0.15), M["white"], root)
    wall(f"{name}RedRoof", R0 - 0.2, R1 + 0.3, 17.0, 17.5, -7, 0.9, M["trim"], root)
    # vertical bulb sign on the corner between garage and red block
    block(f"{name}VSign", (R0 + 0.3, 10.0, 0.9), (1.1, 4.4, 0.4), M["redDark"], root)
    block(f"{name}VSignFace", (R0 + 0.3, 10.0, 1.11), (0.95, 4.2, 0.03), M["red"], root)
    for i in range(16):
        for j in range(2):
            block(f"{name}Bulb{i}_{j}", (R0 + 0.05 + j * 0.5, 8.1 + i * 0.25, 1.15), (0.09, 0.09, 0.05), M["amber"], root)
    for i in range(3):
        block(f"{name}VSignGlyph{i}", (R0 + 0.3, 8.9 + i * 1.1, 1.16), (0.42, 0.62, 0.04), M["white"], root)
    block(f"{name}VSignArm", (R0 + 0.3, 12.4, 0.5), (0.1, 0.1, 0.8), M["metal"], root)
    # rooftop billboard + antennas
    billboard(f"{name}Billboard", (R0 + 4.0, 18.2, -1.0), 7.0, 3.6, M, root)
    antenna(f"{name}Ant3", (R1 - 0.6, 17.5, -0.4), 3.0, M, root)
    antenna(f"{name}Ant4", (R0 + 0.6, 17.5, -2.0), 2.0, M, root)
    _texture_bumps(f"{name}RedTex", R0, R1, 12.0, 17.0, 0.1, M, root, rng, 10, M["stoneC"])

    # ---- pipes + conduits down the walls
    pipe_run(f"{name}Pipe0", [(L1 - 0.3, 0.2, 0.15), (L1 - 0.3, 7.8, 0.15)], M, root)
    pipe_run(f"{name}Pipe1", [(G1 - 0.3, 0.2, 0.45), (G1 - 0.3, 12.8, 0.45)], M, root, 0.05)
    pipe_run(f"{name}Pipe2", [(-1.0, 6.5, 0.4), (-1.0, 9.6, 0.4), (2.0, 9.6, 0.4)], M, root, 0.04)
    pipe_run(f"{name}Pipe3", [(R1 - 1.2, 0.2, 0.25), (R1 - 1.2, 12.0, 0.25)], M, root, 0.05)
    for k, (x, y, z) in enumerate(((G1 - 0.3, 4.2, 0.55), (G1 - 0.3, 9.0, 0.55), (L1 - 0.3, 4.6, 0.25))):
        block(f"{name}Junction{k}", (x, y, z), (0.35, 0.45, 0.2), M["light"], root)
    return root


def build_street_building_preview(parent=None, name="StreetBuildingPreview"):
    root = build_street_building(parent, name)

    def pl(n, pos, color, energy, size=1.0):
        ld = bpy.data.lights.new(n, "POINT")
        ld.color = color
        ld.energy = energy
        ld.shadow_soft_size = size
        ld.specular_factor = 0.0  # no light blobs in the wet ground
        lo = bpy.data.objects.new(n, ld)
        bpy.context.collection.objects.link(lo)
        lo.location = P(*pos)

    pl("FillBar", (-8, 4.5, 2.0), (0.7, 0.4, 1.0), 2800)
    pl("FillBarUp", (-8, 7.5, 3.0), (0.6, 0.5, 1.0), 1800)
    pl("FillMidUp", (0, 11.5, 3.0), (0.6, 0.6, 1.0), 1800)
    pl("FillRedUp", (8, 13.5, 3.0), (1.0, 0.4, 0.8), 2000)
    pl("FillGarage", (0, 4.5, 2.5), (0.2, 0.9, 1.0), 4400)
    pl("FillGarage2", (0, 8.5, 2.0), (0.3, 0.5, 1.0), 1800)
    pl("FillRed", (8, 3.5, 2.5), (1.0, 0.15, 0.3), 4400)
    pl("FillRed2", (8, 8.0, 2.0), (1.0, 0.25, 0.5), 2400)
    pl("FillTop", (8, 20, 2.0), (0.8, 0.3, 1.0), 3000)
    return root
