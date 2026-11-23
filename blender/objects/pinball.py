"""
Cyberpunk pinball machine (original design, no licensed art): a black cabinet
on chrome legs, a sloped playfield under glass with glowing pop bumpers,
flippers, slingshots, a chrome wire ramp, lane guides and lit arrow inserts,
a backbox with abstract synthwave backglass art (neon sun over a grid, no
text), neon side trim, a coin door, a start button and a plunger.

    build_pinball(parent=None, name="Pinball") -> root empty

Coordinates are three.js style (Y up). The player stands at +Z; the playfield
rises toward -Z. Origin at the centre of the footprint on the floor. The
backglass plane is named "<name>Backglass" (0..1 UVs) for live art later.
"""

import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from character import P, _hex  # noqa: E402
from gaming_desk import disc, ring, tube  # noqa: E402
from loft_room import block, mat  # noqa: E402
from arcade_cabinet import prism  # noqa: E402
from glass_room import glass_mat  # noqa: E402

W, L = 0.72, 1.4  # cabinet width (x) and length (z)
Y_FRONT, Y_BACK, Y_BOTTOM = 0.92, 1.02, 0.62  # top edge heights + body bottom
SLOPE = (Y_BACK - Y_FRONT) / L


def pf_y(z, lift=0.0):
    """Height of the playfield surface at depth z (front z = +L/2)."""
    return Y_FRONT + (L / 2 - z) * SLOPE - 0.035 + lift


def _backglass_image():
    name = "PinballBackglass"
    img = bpy.data.images.get(name)
    if img:
        return img
    w, h = 256, 200
    img = bpy.data.images.new(name, w, h)
    px = [0.0] * (w * h * 4)
    mag, cyan, yel = _hex("#ff2bd6"), _hex("#22e4ff"), _hex("#ffd21a")
    horizon = 0.42
    for y in range(h):
        v = y / (h - 1)
        for x in range(w):
            u = x / (w - 1)
            r, g, b = 0.03 + 0.08 * v, 0.0 + 0.01 * v, 0.06 + 0.1 * v  # purple night sky
            if v > horizon:  # striped neon sun
                d = math.hypot((u - 0.5) * 1.3, (v - horizon - 0.02))
                if d < 0.3:
                    t = (v - horizon) / 0.3
                    stripe = (int((v - horizon) * 60) % 3) != 0 or t > 0.45
                    if stripe:
                        r, g, b = (mag[0] * (1 - t) + yel[0] * t, mag[1] * (1 - t) + yel[1] * t, mag[2] * (1 - t) + yel[2] * t)
            else:  # perspective grid
                depth = (horizon - v) / horizon
                zl = abs(math.sin(1 / max(depth, 0.03) * 2.0)) < 0.1
                xl = abs(math.sin((u - 0.5) / max(depth, 0.05) * 10)) < 0.07
                r, g, b = (0.01, 0.0, 0.03)
                if zl or xl:
                    k = 0.3 + 0.7 * depth
                    r, g, b = cyan[0] * k, cyan[1] * k, cyan[2] * k
            if abs(u - 0.5) > 0.46 or v > 0.97 or v < 0.03:  # frame
                r, g, b = cyan
            i = (y * w + x) * 4
            px[i:i + 4] = (r, g, b, 1.0)
    img.pixels = px
    img.pack()
    return img


def _image_emissive(name, img, strength):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = img
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(t.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = strength
    return m


def build_pinball(parent=None, name="Pinball"):
    BODY = mat("PinBody", "#0d0e12", 0.35, metal=0.4)
    CHROME = mat("PinChrome", "#a3a9b0", 0.12, metal=1.0)
    FIELD = mat("PinField", "#120a1c", 0.4)
    RAIL = mat("PinRail", "#2a2d33", 0.3, metal=0.9)
    MAG = mat("PinMagenta", "#ff2bd6", emit="#ff2bd6", strength=8.0)
    CYAN = mat("PinCyan", "#22e4ff", emit="#22e4ff", strength=8.0)
    YEL = mat("PinYellow", "#ffd21a", emit="#ffd21a", strength=7.0)
    FLIP = mat("PinFlipper", "#f2f2f2", 0.3)
    SLOT = mat("PinCoinSlot", "#ff7a14", emit="#ff7a14", strength=5.0)
    GLASS = glass_mat("PinGlass", "#9fd8ff", 0.12)

    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    if parent:
        root.parent = parent
    z0, z1 = -L / 2, L / 2

    # ---------- cabinet body (sloped top) on chrome legs
    prism(f"{name}Body", [(z0, Y_BOTTOM), (z1, Y_BOTTOM), (z1, Y_FRONT), (z0, Y_BACK)], -W / 2, W / 2, BODY, root)
    for k, (sx, sz) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        x, z = sx * (W / 2 - 0.05), sz * (L / 2 - 0.06)
        block(f"{name}Leg{k}", (x, Y_BOTTOM / 2, z), (0.05, Y_BOTTOM, 0.05), CHROME, root)
        block(f"{name}LegPlate{k}", (x, Y_BOTTOM - 0.06, z), (0.09, 0.12, 0.09), CHROME, root)
        disc(f"{name}Foot{k}", (x, 0.01, z), 0.035, 0.02, CHROME, root)
    # neon trim along both top edges (follows the slope)
    for s in (-1, 1):
        tube(f"{name}SideNeon{s}", [(s * (W / 2 + 0.004), Y_FRONT - 0.01, z1), (s * (W / 2 + 0.004), Y_BACK - 0.01, z0)], 0.006, MAG, root)
        tube(f"{name}SideRail{s}", [(s * (W / 2 - 0.02), Y_FRONT + 0.01, z1), (s * (W / 2 - 0.02), Y_BACK + 0.01, z0)], 0.014, CHROME, root)
    block(f"{name}Lockdown", (0, Y_FRONT + 0.012, z1 - 0.03), (W, 0.025, 0.06), CHROME, root, r=0.006)

    # ---------- playfield: dark plane + lit pieces, then glass on top
    ang = math.atan(SLOPE)
    pf = block(f"{name}Playfield", (0, pf_y(0), 0), (W - 0.06, 0.01, L - 0.12), FIELD, root)
    pf.rotation_euler = (ang, 0, 0)  # rises toward -Z

    def piece(nm, x, z, size, m, lift=0.0, rot=0.0):
        o = block(nm, (x, pf_y(z, size[1] / 2 + lift), z), size, m, root, r=0.004)
        o.rotation_euler = (ang, 0, math.radians(rot))
        return o

    # pop bumpers: black base + glowing cap ring
    for k, (bx, bz, m) in enumerate(((-0.12, -0.35, MAG), (0.12, -0.35, CYAN), (0.0, -0.18, YEL))):
        disc(f"{name}BumperBase{k}", (bx, pf_y(bz, 0.03), bz), 0.055, 0.06, BODY, root)
        disc(f"{name}BumperCap{k}", (bx, pf_y(bz, 0.065), bz), 0.05, 0.012, m, root)
        ring(f"{name}BumperSkirt{k}", (bx, pf_y(bz, 0.008), bz), 0.06, 0.006, m, root)
    # flippers + slingshots near the front
    piece(f"{name}FlipperL", -0.1, 0.5, (0.17, 0.03, 0.035), FLIP, rot=-22)
    piece(f"{name}FlipperR", 0.1, 0.5, (0.17, 0.03, 0.035), FLIP, rot=22)
    for s in (-1, 1):
        piece(f"{name}Sling{s}", s * 0.2, 0.33, (0.04, 0.04, 0.22), CYAN, rot=s * 18)
        piece(f"{name}OutLane{s}", s * 0.29, 0.18, (0.012, 0.03, 0.4), RAIL)
    # lit arrow inserts pointing up the playfield
    for k, (ax, az, m) in enumerate(((-0.2, 0.05, MAG), (0.0, 0.12, YEL), (0.2, 0.05, CYAN), (-0.05, -0.02, CYAN), (0.05, -0.02, MAG))):
        a = piece(f"{name}Arrow{k}", ax, az, (0.05, 0.004, 0.05), m, rot=45)
    # top lanes
    for k, lx in enumerate((-0.15, -0.05, 0.05, 0.15)):
        piece(f"{name}TopLane{k}", lx, -0.55, (0.01, 0.03, 0.12), RAIL)
    # chrome wire ramp looping from the right toward the top
    ramp = [(0.24, pf_y(0.25, 0.01), 0.25), (0.26, pf_y(0.0, 0.08), 0.0), (0.22, pf_y(-0.3, 0.14), -0.3),
            (0.05, pf_y(-0.5, 0.16), -0.5), (-0.15, pf_y(-0.45, 0.12), -0.45), (-0.24, pf_y(-0.25, 0.04), -0.25)]
    for s in (-1, 1):
        tube(f"{name}RampWire{s}", [(x + s * 0.025, y, z) for x, y, z in ramp], 0.004, CHROME, root)
    # the ball
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.014, segments=16, ring_count=8)
    ball = bpy.context.active_object
    ball.name = f"{name}Ball"
    ball.location = P(0.03, pf_y(0.2, 0.014), 0.2)
    bpy.ops.object.shade_smooth()
    ball.data.materials.append(CHROME)
    ball.parent = root
    gl = block(f"{name}Glass", (0, pf_y(0, 0.042), 0), (W - 0.05, 0.006, L - 0.08), GLASS, root)
    gl.rotation_euler = (ang, 0, 0)

    # ---------- backbox with synthwave backglass
    bh, bd = 0.72, 0.2
    bz = z0 + bd / 2 + 0.02
    block(f"{name}Backbox", (0, Y_BACK + bh / 2, bz), (W, bh, bd), BODY, root, r=0.01)
    bpy.ops.mesh.primitive_plane_add(size=1)
    bg = bpy.context.active_object
    bg.name = f"{name}Backglass"
    bg.scale = (W - 0.08, bh - 0.12, 1)
    bg.location = P(0, Y_BACK + bh / 2 + 0.02, bz + bd / 2 + 0.003)
    bg.rotation_euler = (math.pi / 2, 0, 0)
    bg.data.materials.append(_image_emissive("Pinball_Backglass", _backglass_image(), 1.8))
    bg.parent = root
    for s in (-1, 1):
        block(f"{name}BackNeon{s}", (s * (W / 2 + 0.004), Y_BACK + bh / 2, bz + bd / 2), (0.01, bh - 0.04, 0.01), CYAN, root)
    block(f"{name}BackTopNeon", (0, Y_BACK + bh + 0.004, bz + bd / 2), (W - 0.04, 0.01, 0.01), MAG, root)

    # ---------- front: coin door, start button, plunger
    zf = z1 + 0.002
    block(f"{name}CoinDoor", (0, 0.77, zf), (0.3, 0.2, 0.012), RAIL, root, r=0.004)
    for k, cx in enumerate((-0.06, 0.06)):
        block(f"{name}CoinSlot{k}", (cx, 0.8, zf + 0.008), (0.008, 0.05, 0.004), SLOT, root)
    disc(f"{name}StartButton", (-0.26, 0.86, zf + 0.01), 0.018, 0.02, YEL, root, axis="z")
    tube(f"{name}Plunger", [(0.26, 0.86, zf), (0.26, 0.86, zf + 0.09)], 0.008, CHROME, root)
    disc(f"{name}PlungerKnob", (0.26, 0.86, zf + 0.1), 0.022, 0.03, BODY, root, axis="z")

    # preview-only glow (lights aren't exported)
    for k, (lx, ly, lz, col, en) in enumerate(((0, 1.3, 0.2, (1.0, 0.3, 0.9), 10), (0, 1.5, z0 + 0.6, (0.2, 0.9, 1.0), 8))):
        ld = bpy.data.lights.new(f"{name}GlowLight{k}", "POINT")
        ld.color = col
        ld.energy = en
        ld.shadow_soft_size = 0.3
        lo = bpy.data.objects.new(f"{name}GlowLight{k}", ld)
        bpy.context.collection.objects.link(lo)
        lo.location = P(lx, ly, lz)
        lo.parent = root
    return root
